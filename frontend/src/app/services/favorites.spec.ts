import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { API_URL } from '../api';
import { makeJob } from '../testing/fixtures';
import { FavoritesService } from './favorites';

describe('FavoritesService', () => {
  let service: FavoritesService;
  let http: HttpTestingController;
  const settle = () => new Promise((resolve) => setTimeout(resolve));
  const url = (id: string) => `${API_URL}/favorites/${encodeURIComponent(id)}`;

  function create() {
    TestBed.configureTestingModule({ providers: [provideHttpClient(), provideHttpClientTesting()] });
    http = TestBed.inject(HttpTestingController);
    service = TestBed.inject(FavoritesService);
  }

  beforeEach(() => localStorage.clear());
  afterEach(() => http.verify());

  it('loads the favorites from the server', async () => {
    create();
    await settle();

    http.expectOne(`${API_URL}/favorites`).flush([makeJob({ id: 'a' })]);
    await settle();

    expect(service.isFavorite('a')).toBe(true);
  });

  it('stars a job right away and saves it on the server', async () => {
    create();
    await settle();
    http.expectOne(`${API_URL}/favorites`).flush([]);
    const job = makeJob({ id: 'a' });

    const done = service.toggle(job);
    expect(service.isFavorite('a')).toBe(true);
    const put = http.expectOne(url('a'));
    expect(put.request.method).toBe('PUT');
    expect(put.request.body).toEqual(job);
    put.flush(job);
    await done;

    expect(service.revision()).toBe(1);
  });

  it('puts the star back if the server refuses to remove it', async () => {
    create();
    await settle();
    http.expectOne(`${API_URL}/favorites`).flush([makeJob({ id: 'a' })]);
    await settle();

    const done = service.toggle(makeJob({ id: 'a' }));
    expect(service.isFavorite('a')).toBe(false);
    http.expectOne(url('a')).flush('down', { status: 500, statusText: 'Server Error' });
    await done;

    expect(service.isFavorite('a')).toBe(true);
    expect(service.revision()).toBe(0);
  });

  it('moves favorites saved in the browser to the server once', async () => {
    localStorage.setItem('job-radar.favorites', JSON.stringify([makeJob({ id: 'new' }), makeJob({ id: 'old' })]));
    create();
    await settle();

    // Oldest first, so the newest keeps the newest star time.
    http.expectOne(url('old')).flush({});
    await settle();
    http.expectOne(url('new')).flush({});
    await settle();
    http.expectOne(`${API_URL}/favorites`).flush([]);

    expect(localStorage.getItem('job-radar.favorites')).toBeNull();
  });
});

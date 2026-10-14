import { TestBed } from '@angular/core/testing';
import { makeJob } from '../testing/fixtures';
import { FavoritesService } from './favorites';

describe('FavoritesService', () => {
  let service: FavoritesService;

  function createService() {
    TestBed.resetTestingModule();
    TestBed.configureTestingModule({});
    return TestBed.inject(FavoritesService);
  }

  beforeEach(() => {
    localStorage.clear();
    service = createService();
  });

  it('stars a job, and a second toggle removes it', () => {
    const job = makeJob({ id: 'a' });

    service.toggle(job);
    expect(service.isFavorite('a')).toBe(true);

    service.toggle(job);
    expect(service.isFavorite('a')).toBe(false);
  });

  it('lists the newest star first', () => {
    service.toggle(makeJob({ id: 'a' }));
    service.toggle(makeJob({ id: 'b' }));

    expect(service.favorites().map((job) => job.id)).toEqual(['b', 'a']);
  });

  it('keeps favorites after a page reload', () => {
    service.toggle(makeJob({ id: 'a' }));
    TestBed.tick();

    expect(createService().favorites().map((job) => job.id)).toEqual(['a']);
  });
});

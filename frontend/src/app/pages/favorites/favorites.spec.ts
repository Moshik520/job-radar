import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { FavoritesService } from '../../services/favorites';
import { makeJob } from '../../testing/fixtures';
import { Favorites } from './favorites';

describe('Favorites page', () => {
  let fixture: ComponentFixture<Favorites>;

  const page = () => fixture.nativeElement as HTMLElement;
  const titles = () => [...page().querySelectorAll('[data-testid="job-card-link"]')].map((a) => a.textContent?.trim());

  beforeEach(async () => {
    localStorage.clear();
    await TestBed.configureTestingModule({
      imports: [Favorites],
      providers: [provideRouter([]), provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();
    fixture = TestBed.createComponent(Favorites);
  });

  it('explains how to add favorites when there are none', async () => {
    await fixture.whenStable();

    expect(page().querySelector('[data-testid="no-favorites"]')).not.toBeNull();
  });

  it('lists starred jobs, and un-starring removes one from the page', async () => {
    const favorites = TestBed.inject(FavoritesService);
    favorites.toggle(makeJob({ id: 'a', title: 'QA Engineer' }));
    favorites.toggle(makeJob({ id: 'b', title: 'Backend Engineer' }));
    await fixture.whenStable();
    expect(titles()).toEqual(['Backend Engineer', 'QA Engineer']);

    (page().querySelector('[data-testid="favorite-button"]') as HTMLButtonElement).click();
    await fixture.whenStable();

    expect(titles()).toEqual(['QA Engineer']);
  });
});

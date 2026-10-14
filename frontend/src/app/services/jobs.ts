import { HttpClient, httpResource } from '@angular/common/http';
import { inject, Service, signal } from '@angular/core';
import { firstValueFrom } from 'rxjs';
import { API_URL } from '../api';
import { Category, CategoryCount, JobsPage } from '../models/job';
import { FavoritesService } from './favorites';

export const PAGE_SIZE = 20;
const SHOW_FAVORITES_KEY = 'job-radar.show-favorites';

@Service()
export class JobsService {
  private readonly http = inject(HttpClient);
  private readonly favorites = inject(FavoritesService);

  // Filter state lives here so it survives navigating to a job and back.
  readonly search = signal('');
  readonly categories = signal<Category[]>([]);
  readonly page = signal(1);
  readonly showFavorites = signal(loadShowFavorites());

  readonly jobsPage = httpResource<JobsPage>(() => ({
    url: `${API_URL}/jobs`,
    params: {
      search: this.search(),
      category: this.categories(), // sent as ?category=qa&category=backend
      ...this.favoritesParams(),
      page: this.page(),
      page_size: PAGE_SIZE,
    },
  }));

  // Counts follow the search but not the selected categories, so every option keeps its number.
  readonly categoryCounts = httpResource<CategoryCount[]>(() => ({
    url: `${API_URL}/jobs/categories`,
    params: { search: this.search(), ...this.favoritesParams() },
  }));

  setSearch(search: string) {
    this.search.set(search);
    this.page.set(1);
  }

  setCategories(categories: Category[]) {
    this.categories.set(categories);
    this.page.set(1);
  }

  setShowFavorites(show: boolean) {
    this.showFavorites.set(show);
    this.page.set(1);
    try {
      localStorage.setItem(SHOW_FAVORITES_KEY, String(show));
    } catch {
      // Not remembered in this browser; the default is used next time.
    }
  }

  /** Remove a job for good (future scans skip it), then refresh the list and the counts. */
  async removeJob(id: string) {
    await firstValueFrom(this.http.delete(`${API_URL}/jobs/${encodeURIComponent(id)}`));
    this.refresh();
  }

  async restoreJob(id: string) {
    await firstValueFrom(this.http.post(`${API_URL}/jobs/${encodeURIComponent(id)}/restore`, null));
    this.refresh();
  }

  private favoritesParams(): Record<string, string | number | boolean> {
    if (this.showFavorites()) {
      return {};
    }
    // `v` changes whenever a star is added or removed, so the list asks the server again and the job
    // moves out of (or back into) the list. The API ignores it.
    return { hide_favorites: true, v: this.favorites.revision() };
  }

  private refresh() {
    this.jobsPage.reload();
    this.categoryCounts.reload();
  }
}

function loadShowFavorites(): boolean {
  try {
    return localStorage.getItem(SHOW_FAVORITES_KEY) !== 'false';
  } catch {
    return true;
  }
}

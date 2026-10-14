import { HttpClient } from '@angular/common/http';
import { computed, inject, Service, signal } from '@angular/core';
import { firstValueFrom } from 'rxjs';
import { API_URL } from '../api';
import { Job } from '../models/job';

// Favorites used to be kept in the browser; they are moved to the server the first time the app loads.
const OLD_STORAGE_KEY = 'job-radar.favorites';

/** Starred jobs, newest star first. Stored on the server so the job list can leave them out. */
@Service()
export class FavoritesService {
  private readonly http = inject(HttpClient);

  readonly favorites = signal<Job[]>([]);
  readonly ids = computed(() => new Set(this.favorites().map((job) => job.id)));
  /** Goes up each time the server confirms a change, so lists that hide favorites know to refresh. */
  readonly revision = signal(0);

  constructor() {
    void this.load();
  }

  isFavorite(id: string): boolean {
    return this.ids().has(id);
  }

  async toggle(job: Job) {
    const wasFavorite = this.isFavorite(job.id);
    // Update the star right away, and undo it if the server says no.
    this.favorites.update((list) => (wasFavorite ? list.filter((f) => f.id !== job.id) : [job, ...list]));
    try {
      const url = this.url(job.id);
      await firstValueFrom(wasFavorite ? this.http.delete(url) : this.http.put(url, job));
      this.revision.update((n) => n + 1);
    } catch {
      this.favorites.update((list) => (wasFavorite ? [job, ...list] : list.filter((f) => f.id !== job.id)));
    }
  }

  private url(id: string) {
    return `${API_URL}/favorites/${encodeURIComponent(id)}`;
  }

  private async load() {
    await this.moveBrowserFavoritesToServer();
    try {
      this.favorites.set(await firstValueFrom(this.http.get<Job[]>(`${API_URL}/favorites`)));
    } catch {
      // The list stays empty; starring still works once the server is back.
    }
  }

  private async moveBrowserFavoritesToServer() {
    let stored: Job[] = [];
    try {
      stored = JSON.parse(localStorage.getItem(OLD_STORAGE_KEY) ?? '[]');
    } catch {
      return;
    }
    if (!stored.length) {
      return;
    }
    try {
      // Oldest first, so the server keeps the same "newest star first" order.
      for (const job of [...stored].reverse()) {
        await firstValueFrom(this.http.put(this.url(job.id), job));
      }
      localStorage.removeItem(OLD_STORAGE_KEY);
    } catch {
      // Keep them in the browser and try again next time.
    }
  }
}

import { computed, effect, Service, signal } from '@angular/core';
import { Job } from '../models/job';

const STORAGE_KEY = 'job-radar.favorites';

/** Starred jobs, newest star first. A copy of each job is kept so it stays visible after the posting closes. */
@Service()
export class FavoritesService {
  readonly favorites = signal<Job[]>(this.load());
  readonly ids = computed(() => new Set(this.favorites().map((job) => job.id)));

  constructor() {
    effect(() => localStorage.setItem(STORAGE_KEY, JSON.stringify(this.favorites())));
  }

  isFavorite(id: string): boolean {
    return this.ids().has(id);
  }

  toggle(job: Job) {
    if (this.isFavorite(job.id)) {
      this.favorites.update((list) => list.filter((favorite) => favorite.id !== job.id));
    } else {
      this.favorites.update((list) => [job, ...list]);
    }
  }

  private load(): Job[] {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY) ?? '[]');
    } catch {
      return [];
    }
  }
}

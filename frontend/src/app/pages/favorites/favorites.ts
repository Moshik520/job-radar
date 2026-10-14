import { Component, inject, signal } from '@angular/core';
import { JobCard } from '../../components/job-card/job-card';
import { FavoritesService } from '../../services/favorites';

@Component({
  imports: [JobCard],
  selector: 'app-favorites',
  styleUrl: './favorites.scss',
  templateUrl: './favorites.html',
})
export class Favorites {
  protected readonly favorites = inject(FavoritesService).favorites;
  protected readonly expandedIds = signal<ReadonlySet<string>>(new Set());

  toggleJob(id: string) {
    this.expandedIds.update((ids) => {
      const next = new Set(ids);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  }
}

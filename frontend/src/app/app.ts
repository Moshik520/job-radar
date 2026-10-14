import { Component, computed, inject, signal } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { FavoritesService } from './services/favorites';

@Component({
  imports: [RouterOutlet, RouterLink, RouterLinkActive],
  selector: 'app-root',
  styleUrl: './app.scss',
  templateUrl: './app.html',
})
export class App {
  protected readonly title = signal('Job Radar');
  private readonly favorites = inject(FavoritesService);
  protected readonly favoritesCount = computed(() => this.favorites.favorites().length);
}



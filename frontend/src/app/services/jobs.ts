import { httpResource } from '@angular/common/http';
import { Service, signal } from '@angular/core';
import { API_URL } from '../api';
import { Category, CategoryCount, JobsPage } from '../models/job';

export const PAGE_SIZE = 20;

@Service()
export class JobsService {
  // Filter state lives here so it survives navigating to a job and back.
  readonly search = signal('');
  readonly categories = signal<Category[]>([]);
  readonly page = signal(1);

  readonly jobsPage = httpResource<JobsPage>(() => ({
    url: `${API_URL}/jobs`,
    params: {
      search: this.search(),
      category: this.categories(), // sent as ?category=qa&category=backend
      page: this.page(),
      page_size: PAGE_SIZE,
    },
  }));

  // Counts follow the search but not the selected categories, so every option keeps its number.
  readonly categoryCounts = httpResource<CategoryCount[]>(() => ({
    url: `${API_URL}/jobs/categories`,
    params: { search: this.search() },
  }));

  setSearch(search: string) {
    this.search.set(search);
    this.page.set(1);
  }

  setCategories(categories: Category[]) {
    this.categories.set(categories);
    this.page.set(1);
  }
}

import { httpResource } from '@angular/common/http';
import { Service, signal } from '@angular/core';
import { API_URL } from '../api';
import { JobsPage } from '../models/job';

export const PAGE_SIZE = 20;

@Service()
export class JobsService {
  // Filter state lives here so it survives navigating to a job and back.
  readonly search = signal('');
  readonly israelOnly = signal(false);
  readonly page = signal(1);

  readonly jobsPage = httpResource<JobsPage>(() => ({
    url: `${API_URL}/jobs`,
    params: {
      search: this.search(),
      israel_only: this.israelOnly(),
      page: this.page(),
      page_size: PAGE_SIZE,
    },
  }));

  setSearch(search: string) {
    this.search.set(search);
    this.page.set(1);
  }

  setIsraelOnly(israelOnly: boolean) {
    this.israelOnly.set(israelOnly);
    this.page.set(1);
  }
}

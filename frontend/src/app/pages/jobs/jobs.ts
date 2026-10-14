import { Component, computed, inject, linkedSignal } from '@angular/core';
import { JobCard } from '../../components/job-card/job-card';
import { JobsPage } from '../../models/job';
import { JobsService, PAGE_SIZE } from '../../services/jobs';

const SEARCH_DEBOUNCE_MS = 300;

@Component({
  imports: [JobCard],
  selector: 'app-jobs',
  styleUrl: './jobs.scss',
  templateUrl: './jobs.html',
})
export class Jobs {
  private readonly jobsService = inject(JobsService);
  private searchTimer?: ReturnType<typeof setTimeout>;

  protected readonly search = this.jobsService.search;
  protected readonly israelOnly = this.jobsService.israelOnly;
  protected readonly page = this.jobsService.page;
  protected readonly isLoading = this.jobsService.jobsPage.isLoading;
  protected readonly error = this.jobsService.jobsPage.error;

  // Keep showing the previous page while the next one loads, instead of flashing an empty list.
  protected readonly jobsPage = linkedSignal<JobsPage | undefined, JobsPage | undefined>({
    source: () => this.jobsService.jobsPage.value(),
    computation: (current, previous) => current ?? previous?.value,
  });
  protected readonly jobs = computed(() => this.jobsPage()?.items ?? []);
  protected readonly total = computed(() => this.jobsPage()?.total ?? 0);
  protected readonly totalPages = computed(() => Math.max(1, Math.ceil(this.total() / PAGE_SIZE)));
  protected readonly firstShown = computed(() =>
    this.total() === 0 ? 0 : (this.page() - 1) * PAGE_SIZE + 1,
  );
  protected readonly lastShown = computed(() => Math.min(this.page() * PAGE_SIZE, this.total()));

  onSearchInput(value: string) {
    clearTimeout(this.searchTimer);
    this.searchTimer = setTimeout(() => this.jobsService.setSearch(value.trim()), SEARCH_DEBOUNCE_MS);
  }

  onIsraelOnlyChange(checked: boolean) {
    this.jobsService.setIsraelOnly(checked);
  }

  goToPage(page: number) {
    this.page.set(page);
    window.scrollTo({ top: 0 });
  }

  retry() {
    this.jobsService.jobsPage.reload();
  }
}

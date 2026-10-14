import { Component, computed, inject, linkedSignal, signal } from '@angular/core';
import { CategoryFilter } from '../../components/category-filter/category-filter';
import { JobCard } from '../../components/job-card/job-card';
import { Category, Job, JobsPage } from '../../models/job';
import { JobsService, PAGE_SIZE } from '../../services/jobs';

const SEARCH_DEBOUNCE_MS = 300;
const UNDO_SECONDS = 8;

@Component({
  imports: [JobCard, CategoryFilter],
  selector: 'app-jobs',
  styleUrl: './jobs.scss',
  templateUrl: './jobs.html',
})
export class Jobs {
  private readonly jobsService = inject(JobsService);
  private searchTimer?: ReturnType<typeof setTimeout>;
  private undoTimer?: ReturnType<typeof setTimeout>;

  protected readonly search = this.jobsService.search;
  protected readonly page = this.jobsService.page;
  protected readonly categories = this.jobsService.categories;
  protected readonly showFavorites = this.jobsService.showFavorites;
  protected readonly expandedIds = signal<ReadonlySet<string>>(new Set());
  protected readonly lastRemoved = signal<Job | null>(null);
  protected readonly removeError = signal(false);
  protected readonly categoryCounts = computed(() =>
    this.jobsService.categoryCounts.hasValue() ? this.jobsService.categoryCounts.value() : [],
  );
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
  protected readonly lastShown = computed(() => this.firstShown() + Math.max(this.jobs().length - 1, 0));

  onSearchInput(value: string) {
    clearTimeout(this.searchTimer);
    this.searchTimer = setTimeout(() => this.jobsService.setSearch(value.trim()), SEARCH_DEBOUNCE_MS);
  }

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

  async removeJob(job: Job) {
    this.removeError.set(false);
    try {
      await this.jobsService.removeJob(job.id);
    } catch {
      this.removeError.set(true);
      return;
    }
    this.lastRemoved.set(job);
    clearTimeout(this.undoTimer);
    this.undoTimer = setTimeout(() => this.lastRemoved.set(null), UNDO_SECONDS * 1000);
  }

  async undoRemove() {
    const job = this.lastRemoved();
    if (!job) {
      return;
    }
    this.lastRemoved.set(null);
    await this.jobsService.restoreJob(job.id);
  }

  collapseAll() {
    this.expandedIds.set(new Set());
  }

  onShowFavoritesChange(show: boolean) {
    this.jobsService.setShowFavorites(show);
  }

  onCategoriesChange(categories: Category[]) {
    this.jobsService.setCategories(categories);
  }

  goToPage(page: number) {
    this.page.set(page);
    window.scrollTo({ top: 0 });
  }

  retry() {
    this.jobsService.jobsPage.reload();
  }
}

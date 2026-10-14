import { Component, computed, inject, signal } from '@angular/core';
import { JobCard } from '../../components/job-card/job-card';
import { JobsService } from '../../services/jobs';

@Component({
  imports: [JobCard],
  selector: 'app-jobs',
  styleUrl: './jobs.scss',
  templateUrl: './jobs.html',
})
export class Jobs {
  private readonly jobsService = inject(JobsService);
  protected readonly isLoading = this.jobsService.jobs.isLoading;
  protected readonly error = this.jobsService.jobs.error;
  protected readonly jobs = computed(() => this.jobsService.jobs.value() ?? []);
  protected readonly searchTerm = signal('');
  protected readonly filteredJobs = computed(() =>
    this.jobs().filter((job) => job.title.toLowerCase().includes(this.searchTerm().toLowerCase())),
  );

  retry() {
    this.jobsService.jobs.reload();
  }
}

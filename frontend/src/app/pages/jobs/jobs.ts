import { Component, computed, signal } from '@angular/core';
import { MOCK_JOBS } from '../../models/mock-jobs';

@Component({
  imports: [],
  selector: 'app-jobs',
  styleUrl: './jobs.scss',
  templateUrl: './jobs.html',
})
export class Jobs {
  protected readonly jobs = signal(MOCK_JOBS);
  protected readonly searchTerm = signal('');
  protected readonly filteredJobs = computed(() =>
    this.jobs().filter((job) => job.title.toLowerCase().includes(this.searchTerm().toLowerCase())),
  );
}

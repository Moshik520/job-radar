import { Component, computed, inject, input } from '@angular/core';
import { RouterLink } from '@angular/router';
import { ApplicationsService } from '../../services/applications';
import { JobsService } from '../../services/jobs';

@Component({
  imports: [RouterLink],
  selector: 'app-job-details',
  styleUrl: './job-details.scss',
  templateUrl: './job-details.html',
})
export class JobDetails {
  private readonly applicationsService = inject(ApplicationsService);
  private readonly jobsService = inject(JobsService);

  readonly id = input.required<string>();
  protected readonly isLoading = this.jobsService.jobs.isLoading;
  protected readonly job = computed(() =>
    this.jobsService.jobs.value()?.find((job) => job.id === this.id()),
  );
  protected readonly isSaved = computed(() =>
    this.applicationsService.applications().some((application) => application.jobId === this.id()),
  );

  toggleSave() {
    if (this.isSaved()) {
      this.applicationsService.remove(this.id());
    } else {
      this.applicationsService.save(this.id());
    }
  }
}

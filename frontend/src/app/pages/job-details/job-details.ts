import { httpResource } from '@angular/common/http';
import { Component, computed, inject, input } from '@angular/core';
import { RouterLink } from '@angular/router';
import { API_URL } from '../../api';
import { Job } from '../../models/job';
import { ApplicationsService } from '../../services/applications';

@Component({
  imports: [RouterLink],
  selector: 'app-job-details',
  styleUrl: './job-details.scss',
  templateUrl: './job-details.html',
})
export class JobDetails {
  private readonly applicationsService = inject(ApplicationsService);

  readonly id = input.required<string>();
  private readonly jobResource = httpResource<Job>(
    () => `${API_URL}/jobs/${encodeURIComponent(this.id())}`,
  );
  protected readonly isLoading = this.jobResource.isLoading;
  protected readonly job = computed(() =>
    this.jobResource.hasValue() ? this.jobResource.value() : undefined,
  );
  protected readonly isSaved = computed(() =>
    this.applicationsService.applications().some((application) => application.jobId === this.id()),
  );

  toggleSave(job: Job) {
    if (this.isSaved()) {
      this.applicationsService.remove(job.id);
    } else {
      this.applicationsService.save(job);
    }
  }
}

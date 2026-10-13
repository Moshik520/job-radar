import { Component, computed, inject, input } from '@angular/core';
import { RouterLink } from '@angular/router';
import { MOCK_JOBS } from '../../models/mock-jobs';
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
  protected readonly job = computed(() => MOCK_JOBS.find((job) => job.id === this.id()));
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

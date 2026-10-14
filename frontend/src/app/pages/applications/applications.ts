import { Component, inject } from '@angular/core';
import { JobCard } from '../../components/job-card/job-card';
import { JOB_STATUSES, JobStatus } from '../../models/job';
import { ApplicationsService } from '../../services/applications';

@Component({
  imports: [JobCard],
  selector: 'app-applications',
  styleUrl: './applications.scss',
  templateUrl: './applications.html',
})
export class Applications {
  private readonly applicationsService = inject(ApplicationsService);

  protected readonly statuses = JOB_STATUSES;
  protected readonly applications = this.applicationsService.applications;

  changeStatus(jobId: string, status: JobStatus) {
    this.applicationsService.updateStatus(jobId, status);
  }
}

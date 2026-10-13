import { Component, computed, inject } from '@angular/core';
import { JobCard } from '../../components/job-card/job-card';
import { JOB_STATUSES, JobStatus } from '../../models/job';
import { MOCK_JOBS } from '../../models/mock-jobs';
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
  protected readonly savedJobs = computed(() =>
    this.applicationsService.applications().map((application) => ({
      application,
      job: MOCK_JOBS.find((job) => job.id === application.jobId),
    })),
  );

  changeStatus(jobId: string, status: JobStatus) {
    this.applicationsService.updateStatus(jobId, status);
  }
}

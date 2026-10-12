import { Component, computed, input } from '@angular/core';
import { RouterLink } from '@angular/router';
import { MOCK_JOBS } from '../../models/mock-jobs';

@Component({
  imports: [RouterLink],
  selector: 'app-job-details',
  styleUrl: './job-details.scss',
  templateUrl: './job-details.html',
})
export class JobDetails {
  readonly id = input.required<string>();
  protected readonly job = computed(() => MOCK_JOBS.find((job) => job.id === this.id()));
}

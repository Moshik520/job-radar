import { Component, input } from '@angular/core';
import { CATEGORY_LABELS, Job } from '../../models/job';
import { RouterLink } from '@angular/router';

@Component({
  imports: [RouterLink],
  selector: 'app-job-card',
  styleUrl: './job-card.scss',
  templateUrl: './job-card.html',
})
export class JobCard {
  readonly job = input.required<Job>();
  protected readonly categoryLabels = CATEGORY_LABELS;
}


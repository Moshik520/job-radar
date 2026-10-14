import { httpResource } from '@angular/common/http';
import { Component, input, output } from '@angular/core';
import { RouterLink } from '@angular/router';
import { API_URL } from '../../api';
import { CATEGORY_LABELS, Job, JobDetails } from '../../models/job';

@Component({
  imports: [RouterLink],
  selector: 'app-job-card',
  styleUrl: './job-card.scss',
  templateUrl: './job-card.html',
})
export class JobCard {
  readonly job = input.required<Job>();
  readonly expandable = input(false);
  readonly expanded = input(false);
  readonly toggled = output<void>();

  protected readonly categoryLabels = CATEGORY_LABELS;

  // Fetched only while the card is open; an undefined URL means "no request".
  protected readonly details = httpResource<JobDetails>(() =>
    this.expanded() ? `${API_URL}/jobs/${encodeURIComponent(this.job().id)}/details` : undefined,
  );

  onCardClick(event: MouseEvent) {
    const target = event.target as HTMLElement;
    // Links keep working normally, and clicks inside the open description (e.g. selecting text) don't close it.
    if (!this.expandable() || target.closest('a') || target.closest('.details')) {
      return;
    }
    this.toggled.emit();
  }
}

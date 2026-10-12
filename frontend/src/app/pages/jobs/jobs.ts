import { Component, signal } from '@angular/core';
import { MOCK_JOBS } from '../../models/mock-jobs';
@Component({
  imports: [],
  selector: 'app-jobs',
  styleUrl: './jobs.scss',
  templateUrl: './jobs.html',
})
export class Jobs {
  protected readonly jobs = signal(MOCK_JOBS);


}

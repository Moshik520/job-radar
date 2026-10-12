import { Routes } from '@angular/router';
import { JobDetails } from './pages/job-details/job-details';
import { Jobs } from './pages/jobs/jobs';

export const routes: Routes = [
  { path: '', redirectTo: 'jobs', pathMatch: 'full' },
  { path: 'jobs', component: Jobs },
  { path: 'jobs/:id', component: JobDetails },
];

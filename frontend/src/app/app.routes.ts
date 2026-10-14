import { Routes } from '@angular/router';
import { JobDetails } from './pages/job-details/job-details';
import { Jobs } from './pages/jobs/jobs';
import { Applications } from './pages/applications/applications';
import { Favorites } from './pages/favorites/favorites';

export const routes: Routes = [
  { path: '', redirectTo: 'jobs', pathMatch: 'full' },
  { path: 'jobs', component: Jobs },
  { path: 'jobs/:id', component: JobDetails },
  { path: 'favorites', component: Favorites },
  { path: 'applications', component: Applications },
];

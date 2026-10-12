import { Routes } from '@angular/router';
import { Jobs } from './pages/jobs/jobs';
export const routes: Routes = [
    {
    path: 'jobs',
    component: Jobs,
    },
    { path: '', redirectTo: 'jobs', pathMatch: 'full' },
];

import { effect, Service, signal } from '@angular/core';
import { Application } from '../models/application';
import { JobStatus } from '../models/job';
// Temporary browser storage until the backend exists.
const STORAGE_KEY = 'job-radar.applications';

@Service()
export class ApplicationsService {
  readonly applications = signal<Application[]>(this.load());

  constructor() {
    effect(() => localStorage.setItem(STORAGE_KEY, JSON.stringify(this.applications())));
  }

  save(jobId: string) {
    if (this.applications().some((application) => application.jobId === jobId)) {
      return;
    }
    const newApplication: Application = {
      jobId,
      status: 'saved',
      savedAt: new Date().toISOString(),
    };
    this.applications.update((list) => [...list, newApplication]);
  }

  remove(jobId: string) {
    this.applications.update((list) => list.filter((application) => application.jobId !== jobId));
  }

  updateStatus(jobId: string, status: JobStatus) {
    this.applications.update((list) =>
      list.map((application) =>
        application.jobId === jobId ? { ...application, status } : application,
      ),
    );
  }

  private load(): Application[] {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY) ?? '[]');
    } catch {
      return [];
    }
  }
}

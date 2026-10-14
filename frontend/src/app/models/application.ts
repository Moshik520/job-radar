import { Job, JobStatus } from './job';

export interface Application {
  jobId: string;
  status: JobStatus;
  savedAt: string;
  // A copy of the job when it was saved, so the list still works after the posting closes.
  job: Job;
}

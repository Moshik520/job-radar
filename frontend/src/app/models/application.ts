import { JobStatus } from './job';

export interface Application {
  jobId: string;
  status: JobStatus;
  savedAt: string;
}

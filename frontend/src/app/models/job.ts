export type JobSource = 'greenhouse' | 'lever' | 'ashby' | 'workday' | 'comeet';
export type JobStatus = 'saved' | 'applied' | 'interview' | 'offer' | 'rejected';

export const JOB_STATUSES: JobStatus[] = ['saved', 'applied', 'interview', 'offer', 'rejected'];

export interface Job {
  id: string;
  title: string;
  company: string;
  location: string;
  url: string;
  source: JobSource;
  publishedAt: string;
  isIsrael: boolean;
}

export type JobSource =
  | 'greenhouse'
  | 'ashby'
  | 'lever'
  | 'workable'
  | 'recruitee'
  | 'personio'
  | 'rippling'
  | 'workday'
  | 'comeet';
export type JobStatus = 'saved' | 'applied' | 'interview' | 'offer' | 'rejected';

export const JOB_SOURCES: JobSource[] = [
  'greenhouse',
  'ashby',
  'lever',
  'workable',
  'recruitee',
  'personio',
  'rippling',
  'workday',
  'comeet',
];
export const JOB_STATUSES: JobStatus[] = ['saved', 'applied', 'interview', 'offer', 'rejected'];

export interface Job {
  id: string;
  title: string;
  company: string;
  location: string;
  url: string;
  source: JobSource;
  publishedAt: string | null;
  updatedAt: string | null;
  isIsrael: boolean;
}

export interface JobsPage {
  items: Job[];
  total: number;
  page: number;
  pageSize: number;
}

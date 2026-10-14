import { Job, JobsPage } from '../models/job';

/** A job as the API returns it; override any field per test. */
export function makeJob(overrides: Partial<Job> = {}): Job {
  return {
    id: 'greenhouse:acme:1',
    title: 'QA Automation Engineer',
    company: 'Acme',
    location: 'Tel Aviv, Israel',
    url: 'https://example.com/jobs/1',
    source: 'greenhouse',
    publishedAt: '2026-10-10T09:00:00Z',
    updatedAt: '2026-10-10T09:00:00Z',
    isIsrael: true,
    category: 'qa',
    ...overrides,
  };
}

export function makePage(items: Job[], total = items.length, page = 1): JobsPage {
  return { items, total, page, pageSize: 20 };
}

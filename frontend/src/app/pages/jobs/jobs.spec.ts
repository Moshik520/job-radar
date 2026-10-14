import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting, TestRequest } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { API_URL } from '../../api';
import { makeJob, makePage } from '../../testing/fixtures';
import { Jobs } from './jobs';

describe('Jobs page', () => {
  let fixture: ComponentFixture<Jobs>;
  let http: HttpTestingController;

  const page = () => fixture.nativeElement as HTMLElement;
  const find = (testId: string) => page().querySelector(`[data-testid="${testId}"]`) as HTMLElement | null;
  const all = (testId: string) => [...page().querySelectorAll(`[data-testid="${testId}"]`)] as HTMLElement[];

  function jobsRequest(): TestRequest {
    return http.match((request) => request.url === `${API_URL}/jobs`).at(-1)!;
  }

  async function answerJobs(body: object) {
    TestBed.tick();
    jobsRequest().flush(body);
    http.match((request) => request.url === `${API_URL}/jobs/categories`).forEach((r) => r.flush([]));
    await fixture.whenStable();
  }

  const settle = () => new Promise((resolve) => setTimeout(resolve));

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Jobs],
      providers: [provideRouter([{ path: '**', children: [] }]), provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();

    fixture = TestBed.createComponent(Jobs);
    http = TestBed.inject(HttpTestingController);
  });

  it('shows a loading message until the jobs arrive', () => {
    TestBed.tick();

    expect(find('jobs-loading')).not.toBeNull();
  });

  it('shows the jobs and how many there are', async () => {
    await answerJobs(
      makePage([makeJob({ id: 'a', title: 'QA Engineer' }), makeJob({ id: 'b', title: 'Backend Engineer' })], 42),
    );

    expect(all('job-card-link').map((link) => link.textContent?.trim())).toEqual(['QA Engineer', 'Backend Engineer']);
    expect(find('results-count')?.textContent).toContain('Showing 1–2 of 42 jobs');
  });

  it('says so when no job matches', async () => {
    await answerJobs(makePage([], 0));

    expect(find('no-results')).not.toBeNull();
    expect(find('pagination')).toBeNull();
  });

  it('shows an error with a retry button when the server fails, and retries', async () => {
    TestBed.tick();
    jobsRequest().flush('down', { status: 500, statusText: 'Server Error' });
    http.match((request) => request.url === `${API_URL}/jobs/categories`).forEach((r) => r.flush([]));
    await fixture.whenStable();

    expect(find('jobs-error')).not.toBeNull();

    find('retry-button')!.click();
    await answerJobs(makePage([makeJob()]));

    expect(find('jobs-error')).toBeNull();
    expect(all('job-card')).toHaveLength(1);
  });

  it('pages through the results', async () => {
    await answerJobs(makePage([makeJob()], 45));
    expect(find('page-indicator')?.textContent).toContain('Page 1 of 3');
    expect((find('prev-page') as HTMLButtonElement).disabled).toBe(true);

    find('next-page')!.click();
    TestBed.tick();

    expect(jobsRequest().request.params.get('page')).toBe('2');
  });

  it('opens a card on click, closes it on a second click', async () => {
    await answerJobs(makePage([makeJob({ id: 'a' })]));
    const card = find('job-card')!;

    card.click();
    TestBed.tick();
    expect(card.getAttribute('aria-expanded')).toBe('true');

    card.querySelector<HTMLElement>('.summary')!.click();
    TestBed.tick();
    expect(card.getAttribute('aria-expanded')).toBe('false');
  });

  it('"Collapse all" closes every open card', async () => {
    await answerJobs(makePage([makeJob({ id: 'a' }), makeJob({ id: 'b' })]));
    const collapseAll = find('collapse-all') as HTMLButtonElement;
    expect(collapseAll.disabled).toBe(true);

    all('job-card').forEach((card) => card.click());
    TestBed.tick();
    expect(all('job-card').every((card) => card.getAttribute('aria-expanded') === 'true')).toBe(true);
    expect(collapseAll.disabled).toBe(false);

    collapseAll.click();
    TestBed.tick();

    expect(all('job-card').every((card) => card.getAttribute('aria-expanded') === 'false')).toBe(true);
    expect(collapseAll.disabled).toBe(true);
  });

  it('✕ removes a job, and Undo brings it back', async () => {
    const job = makeJob({ id: 'greenhouse:acme:1', title: 'QA Engineer' });
    await answerJobs(makePage([job]));

    find('remove-job-button')!.click();
    TestBed.tick();
    const remove = http.expectOne((r) => r.method === 'DELETE');
    expect(remove.request.url).toBe(`${API_URL}/jobs/${encodeURIComponent(job.id)}`);
    remove.flush(null, { status: 204, statusText: 'No Content' });
    await settle(); // the component awaits the DELETE before refreshing the list
    await answerJobs(makePage([]));

    expect(find('removed-toast')?.textContent).toContain('QA Engineer');

    find('undo-remove')!.click();
    TestBed.tick();
    const restore = http.expectOne((r) => r.method === 'POST');
    expect(restore.request.url).toBe(`${API_URL}/jobs/${encodeURIComponent(job.id)}/restore`);
    restore.flush(job);
    await settle();
    await answerJobs(makePage([job]));

    expect(find('removed-toast')).toBeNull();
    expect(all('job-card')).toHaveLength(1);
  });

  it('"Show favorites" off asks the server to leave starred jobs out, and is remembered', async () => {
    localStorage.clear();
    await answerJobs(makePage([makeJob()]));
    const checkbox = find('show-favorites') as HTMLInputElement;
    expect(checkbox.checked).toBe(true);
    expect(jobsRequest()).toBeUndefined();

    checkbox.checked = false;
    checkbox.dispatchEvent(new Event('change'));
    TestBed.tick();

    expect(jobsRequest().request.params.get('hide_favorites')).toBe('true');
    expect(localStorage.getItem('job-radar.show-favorites')).toBe('false');
  });
});


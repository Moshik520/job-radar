import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { API_URL } from '../../api';
import { makeJob } from '../../testing/fixtures';
import { JobCard } from './job-card';

describe('JobCard', () => {
  let fixture: ComponentFixture<JobCard>;
  let http: HttpTestingController;
  const job = makeJob({ id: 'workday:wd1/acme/Careers:/job/Haifa/QA_R1' });
  const detailsUrl = `${API_URL}/jobs/${encodeURIComponent(job.id)}/details`;

  const page = () => fixture.nativeElement as HTMLElement;
  const find = (testId: string) => page().querySelector(`[data-testid="${testId}"]`);

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [JobCard],
      providers: [provideRouter([{ path: '**', children: [] }]), provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();

    fixture = TestBed.createComponent(JobCard);
    http = TestBed.inject(HttpTestingController);
    fixture.componentRef.setInput('job', job);
    await fixture.whenStable();
  });

  afterEach(() => http.verify());

  it('shows the title, company, location and category', () => {
    expect(find('job-card-link')?.textContent?.trim()).toBe('QA Automation Engineer');
    expect(page().textContent).toContain('Acme · Tel Aviv, Israel');
    expect(find('job-category')?.textContent?.trim()).toBe('QA & Testing');
  });

  it('shows when the job was posted, with the exact date in a tooltip', () => {
    const posted = find('job-posted') as HTMLElement;

    expect(posted.textContent?.trim()).not.toBe('');
    expect(posted.getAttribute('datetime')).toBe('2026-10-10T09:00:00Z');
    expect(posted.title).not.toBe('');
  });

  it('links the title to the job page', () => {
    const href = find('job-card-link')!.getAttribute('href')!;
    expect(decodeURIComponent(href)).toBe(`/jobs/${job.id}`);
  });

  it('does not load details while closed', () => {
    http.expectNone(detailsUrl);
    expect(find('job-details-panel')).toBeNull();
  });

  it('asks to open when clicked, if it is expandable', () => {
    fixture.componentRef.setInput('expandable', true);
    const toggled = vi.fn();
    fixture.componentInstance.toggled.subscribe(toggled);

    (find('job-card') as HTMLElement).click();

    expect(toggled).toHaveBeenCalledTimes(1);
  });

  it('ignores clicks when it is not expandable (e.g. on My Applications)', () => {
    const toggled = vi.fn();
    fixture.componentInstance.toggled.subscribe(toggled);

    (find('job-card') as HTMLElement).click();

    expect(toggled).not.toHaveBeenCalled();
  });

  it('does not toggle when the title link is clicked', () => {
    fixture.componentRef.setInput('expandable', true);
    const toggled = vi.fn();
    fixture.componentInstance.toggled.subscribe(toggled);

    (find('job-card-link') as HTMLElement).dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));

    expect(toggled).not.toHaveBeenCalled();
  });

  it('loads and shows the job details when opened', async () => {
    fixture.componentRef.setInput('expandable', true);
    fixture.componentRef.setInput('expanded', true);
    TestBed.tick();
    expect(find('job-details-loading')).not.toBeNull();

    http.expectOne(detailsUrl).flush({
      content: '<p>Write <strong>Playwright</strong> tests</p>',
      departments: ['R&D'],
      fields: [{ name: 'Workplace', value: 'Hybrid' }],
    });
    await fixture.whenStable();

    expect(find('job-description')?.innerHTML).toContain('<strong>Playwright</strong>');
    expect(page().textContent).toContain('R&D');
    expect(page().textContent).toContain('Hybrid');
    expect(find('job-apply-link')?.getAttribute('href')).toBe(job.url);
  });

  it('removes scripts from the description HTML', async () => {
    fixture.componentRef.setInput('expanded', true);
    TestBed.tick();

    http.expectOne(detailsUrl).flush({
      content: '<p>Hello</p><script>alert(1)</script><img src="x" onerror="alert(2)">',
      departments: [],
      fields: [],
    });
    await fixture.whenStable();

    const description = find('job-description') as HTMLElement;
    expect(description.querySelector('script')).toBeNull();
    expect(description.innerHTML).not.toContain('onerror');
  });

  it('offers the company site when the details cannot be loaded', async () => {
    fixture.componentRef.setInput('expanded', true);
    TestBed.tick();

    http.expectOne(detailsUrl).flush({ detail: 'gone' }, { status: 404, statusText: 'Not Found' });
    await fixture.whenStable();

    const error = find('job-details-error') as HTMLElement;
    expect(error).not.toBeNull();
    expect(error.querySelector('a')?.getAttribute('href')).toBe(job.url);
  });
});

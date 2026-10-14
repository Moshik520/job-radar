import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { API_URL } from '../../api';
import { ApplicationsService } from '../../services/applications';
import { makeJob } from '../../testing/fixtures';
import { JobDetails } from './job-details';

describe('Job details page', () => {
  let fixture: ComponentFixture<JobDetails>;
  let http: HttpTestingController;
  const job = makeJob();

  const page = () => fixture.nativeElement as HTMLElement;
  const find = (testId: string) => page().querySelector(`[data-testid="${testId}"]`) as HTMLElement | null;

  beforeEach(async () => {
    localStorage.clear();
    await TestBed.configureTestingModule({
      imports: [JobDetails],
      providers: [provideRouter([]), provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();

    fixture = TestBed.createComponent(JobDetails);
    http = TestBed.inject(HttpTestingController);
    fixture.componentRef.setInput('id', job.id);
    TestBed.tick(); // starts the request; whenStable() would wait for it to finish
  });

  afterEach(() => http.verify());

  it('loads the job from the API and shows it', async () => {
    expect(find('job-loading')).not.toBeNull();

    http.expectOne(`${API_URL}/jobs/${encodeURIComponent(job.id)}`).flush(job);
    await fixture.whenStable();

    expect(find('job-title')?.textContent).toBe('QA Automation Engineer');
    expect(find('apply-button')?.getAttribute('href')).toBe(job.url);
  });

  it('says the job was not found when the API answers 404', async () => {
    http.expectOne(`${API_URL}/jobs/${encodeURIComponent(job.id)}`).flush(
      { detail: 'Job not found' },
      { status: 404, statusText: 'Not Found' },
    );
    await fixture.whenStable();

    expect(find('job-not-found')).not.toBeNull();
  });

  it('saves the job, and a second click removes it', async () => {
    http.expectOne(`${API_URL}/jobs/${encodeURIComponent(job.id)}`).flush(job);
    await fixture.whenStable();
    const applications = TestBed.inject(ApplicationsService);
    const save = find('save-button')!;

    save.click();
    await fixture.whenStable();
    expect(save.textContent).toContain('Saved ✓');
    expect(applications.applications().map((a) => a.jobId)).toEqual([job.id]);

    save.click();
    await fixture.whenStable();
    expect(save.textContent).toContain('Save');
    expect(applications.applications()).toEqual([]);
  });
});

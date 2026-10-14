import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { ApplicationsService } from '../../services/applications';
import { makeJob } from '../../testing/fixtures';
import { Applications } from './applications';

describe('My Applications page', () => {
  let fixture: ComponentFixture<Applications>;
  let applications: ApplicationsService;

  const page = () => fixture.nativeElement as HTMLElement;
  const all = (testId: string) => [...page().querySelectorAll(`[data-testid="${testId}"]`)] as HTMLElement[];

  beforeEach(async () => {
    localStorage.clear();
    await TestBed.configureTestingModule({
      imports: [Applications],
      providers: [provideRouter([]), provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();

    applications = TestBed.inject(ApplicationsService);
    fixture = TestBed.createComponent(Applications);
  });

  it('explains that nothing was saved yet', async () => {
    await fixture.whenStable();

    expect(page().querySelector('[data-testid="no-applications"]')).not.toBeNull();
  });

  it('lists saved jobs with their status', async () => {
    applications.save(makeJob({ id: 'a', title: 'QA Engineer' }));
    applications.save(makeJob({ id: 'b', title: 'Backend Engineer' }));
    applications.updateStatus('b', 'interview');
    await fixture.whenStable();

    expect(all('job-card-link').map((link) => link.textContent?.trim())).toEqual(['QA Engineer', 'Backend Engineer']);
    expect(all('status-select').map((select) => (select as HTMLSelectElement).value)).toEqual(['saved', 'interview']);
  });

  it('changes a status from the dropdown', async () => {
    applications.save(makeJob({ id: 'a' }));
    await fixture.whenStable();

    const select = all('status-select')[0] as HTMLSelectElement;
    select.value = 'applied';
    select.dispatchEvent(new Event('change'));

    expect(applications.applications()[0].status).toBe('applied');
  });
});

import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { App } from './app';

describe('App', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [App],
      providers: [provideRouter([])],
    }).compileComponents();
  });

  it('shows the Job Radar logo', async () => {
    const fixture = TestBed.createComponent(App);
    await fixture.whenStable();

    const logo = (fixture.nativeElement as HTMLElement).querySelector('.logo');
    expect(logo?.textContent?.trim()).toBe('Job Radar');
  });

  it('links to the jobs list and to my applications', async () => {
    const fixture = TestBed.createComponent(App);
    await fixture.whenStable();
    const page = fixture.nativeElement as HTMLElement;

    expect(page.querySelector('[data-testid="nav-jobs"]')?.getAttribute('href')).toBe('/jobs');
    expect(page.querySelector('[data-testid="nav-applications"]')?.getAttribute('href')).toBe('/applications');
  });
});

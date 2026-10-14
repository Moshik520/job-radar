import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { ApplicationRef } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { API_URL } from '../api';
import { makeJob, makePage } from '../testing/fixtures';
import { JobsService, PAGE_SIZE } from './jobs';

describe('JobsService', () => {
  let service: JobsService;
  let http: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    service = TestBed.inject(JobsService);
    http = TestBed.inject(HttpTestingController);
  });

  function lastJobsRequest() {
    TestBed.tick();
    return http.match((request) => request.url === `${API_URL}/jobs`).at(-1)!;
  }

  it('asks for the first page of all jobs', () => {
    const request = lastJobsRequest();

    expect(request.request.params.get('page')).toBe('1');
    expect(request.request.params.get('page_size')).toBe(String(PAGE_SIZE));
    expect(request.request.params.get('search')).toBe('');
    expect(request.request.params.getAll('category') ?? []).toEqual([]);
  });

  it('sends every selected category as its own parameter', () => {
    service.setCategories(['qa', 'fullstack']);

    expect(lastJobsRequest().request.params.getAll('category')).toEqual(['qa', 'fullstack']);
  });

  it('goes back to page 1 when the search changes', () => {
    service.page.set(3);
    service.setSearch('automation');

    const request = lastJobsRequest();
    expect(request.request.params.get('page')).toBe('1');
    expect(request.request.params.get('search')).toBe('automation');
  });

  it('goes back to page 1 when the categories change', () => {
    service.page.set(3);
    service.setCategories(['qa']);

    expect(lastJobsRequest().request.params.get('page')).toBe('1');
  });

  it('exposes the page the API returned', async () => {
    lastJobsRequest().flush(makePage([makeJob()]));
    http.match((r) => r.url === `${API_URL}/jobs/categories`).forEach((r) => r.flush([]));
    await TestBed.inject(ApplicationRef).whenStable();

    expect(service.jobsPage.value()?.items[0].title).toBe('QA Automation Engineer');
  });

  it('counts per category follow the search but not the selected categories', () => {
    service.setSearch('senior');
    service.setCategories(['qa']);
    TestBed.tick();

    const request = http.match((r) => r.url === `${API_URL}/jobs/categories`).at(-1)!;
    expect(request.request.params.get('search')).toBe('senior');
    expect(request.request.params.has('category')).toBe(false);
  });
});

import { TestBed } from '@angular/core/testing';
import { makeJob } from '../testing/fixtures';
import { ApplicationsService } from './applications';

const STORAGE_KEY = 'job-radar.applications';

describe('ApplicationsService', () => {
  let service: ApplicationsService;

  function createService() {
    TestBed.resetTestingModule();
    TestBed.configureTestingModule({});
    return TestBed.inject(ApplicationsService);
  }

  beforeEach(() => {
    localStorage.clear();
    service = createService();
  });

  it('starts empty', () => {
    expect(service.applications()).toEqual([]);
  });

  it('saves a job with status "saved" and a copy of the job', () => {
    const job = makeJob();

    service.save(job);

    expect(service.applications()).toHaveLength(1);
    expect(service.applications()[0]).toMatchObject({ jobId: job.id, status: 'saved', job });
  });

  it('does not save the same job twice', () => {
    const job = makeJob();

    service.save(job);
    service.save(job);

    expect(service.applications()).toHaveLength(1);
  });

  it('removes only the given job', () => {
    service.save(makeJob({ id: 'a' }));
    service.save(makeJob({ id: 'b' }));

    service.remove('a');

    expect(service.applications().map((application) => application.jobId)).toEqual(['b']);
  });

  it('updates the status of one job', () => {
    service.save(makeJob({ id: 'a' }));
    service.save(makeJob({ id: 'b' }));

    service.updateStatus('b', 'interview');

    expect(service.applications().map((application) => application.status)).toEqual(['saved', 'interview']);
  });

  it('keeps saved jobs after a page reload', () => {
    service.save(makeJob({ id: 'a' }));
    TestBed.tick(); // runs the effect that writes localStorage

    const afterReload = createService();

    expect(afterReload.applications().map((application) => application.jobId)).toEqual(['a']);
  });

  it('ignores stored entries saved before job copies existed', () => {
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify([
        { jobId: 'old', status: 'saved', savedAt: '2026-10-01' },
        { jobId: 'new', status: 'applied', savedAt: '2026-10-02', job: makeJob({ id: 'new' }) },
      ]),
    );

    const loaded = createService();

    expect(loaded.applications().map((application) => application.jobId)).toEqual(['new']);
  });

  it('starts empty when the stored data is broken', () => {
    localStorage.setItem(STORAGE_KEY, '{not json');

    expect(createService().applications()).toEqual([]);
  });
});

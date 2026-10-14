import { Service } from '@angular/core';
import { httpResource } from '@angular/common/http';
import { Job } from '../models/job';
import { API_URL } from '../api';

@Service()
export class JobsService {
  readonly jobs = httpResource<Job[]>(() => `${API_URL}/jobs`);
}

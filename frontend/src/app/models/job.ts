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
export type Category =
  | 'qa'
  | 'fullstack'
  | 'frontend'
  | 'backend'
  | 'mobile'
  | 'software'
  | 'ai_ml'
  | 'data'
  | 'devops'
  | 'security'
  | 'hardware'
  | 'it_support'
  | 'solutions'
  | 'product'
  | 'design'
  | 'ai_training'
  | 'sales'
  | 'marketing'
  | 'customer_success'
  | 'operations'
  | 'finance'
  | 'legal'
  | 'hr'
  | 'admin'
  | 'mechanical'
  | 'trades'
  | 'healthcare'
  | 'fitness'
  | 'education'
  | 'general_application'
  | 'other';

export const CATEGORY_LABELS: Record<Category, string> = {
  qa: 'QA & Testing',
  fullstack: 'Full Stack',
  frontend: 'Frontend',
  backend: 'Backend',
  mobile: 'Mobile',
  software: 'Software Engineering',
  ai_ml: 'AI & Machine Learning',
  data: 'Data & Analytics',
  devops: 'DevOps / SRE / Cloud',
  security: 'Security',
  hardware: 'Hardware & Embedded',
  it_support: 'IT & Tech Support',
  solutions: 'Solutions & Forward-Deployed',
  product: 'Product Management',
  design: 'Design (UX/UI)',
  ai_training: 'AI Training & Annotation',
  sales: 'Sales & Business Development',
  marketing: 'Marketing & Growth',
  customer_success: 'Customer Success & Support',
  operations: 'Operations & Management',
  finance: 'Finance & Accounting',
  legal: 'Legal & Compliance',
  hr: 'HR & Recruiting',
  admin: 'Admin & Office',
  mechanical: 'Mechanical / Electrical / Manufacturing',
  trades: 'Skilled Trades & Technicians',
  healthcare: 'Healthcare & Medical',
  fitness: 'Fitness & Wellness',
  education: 'Education & Training',
  general_application: 'General Application',
  other: 'Other',
};

export const CATEGORY_GROUPS: { label: string; categories: Category[] }[] = [
  {
    label: 'Tech',
    categories: [
      'qa',
      'fullstack',
      'frontend',
      'backend',
      'mobile',
      'software',
      'ai_ml',
      'data',
      'devops',
      'security',
      'hardware',
      'it_support',
      'solutions',
      'product',
      'design',
      'ai_training',
    ],
  },
  {
    label: 'Other roles',
    categories: [
      'sales',
      'marketing',
      'customer_success',
      'operations',
      'finance',
      'legal',
      'hr',
      'admin',
      'mechanical',
      'trades',
      'healthcare',
      'fitness',
      'education',
      'general_application',
      'other',
    ],
  },
];

export interface CategoryCount {
  category: Category;
  count: number;
}

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
  category?: Category;
}

export interface JobsPage {
  items: Job[];
  total: number;
  page: number;
  pageSize: number;
}

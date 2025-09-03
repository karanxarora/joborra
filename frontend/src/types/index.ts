// API Types
export interface User {
  id: number;
  email: string;
  username: string;
  full_name: string;
  contact_number?: string;
  role: 'student' | 'employer';
  is_verified?: boolean;
  // OAuth fields
  oauth_provider?: string | null;
  oauth_sub?: string | null;
  university?: string;
  degree?: string;
  graduation_year?: number;
  visa_status?: string;
  city_suburb?: string;
  date_of_birth?: string; // ISO datetime string
  // Study details (moved from visa verification)
  course_name?: string;
  institution_name?: string;
  course_start_date?: string; // ISO datetime string
  course_end_date?: string;   // ISO datetime string

  company_name?: string;
  company_website?: string;
  company_size?: string;
  industry?: string;
  company_description?: string;
  company_logo_url?: string;
  resume_url?: string;
  created_at: string;
  updated_at: string;
}

export interface Job {
  id: number;
  title: string;
  company: {
    id: number;
    name: string;
    website?: string;
    size?: string;
    industry?: string;
  };
  location: string;
  state?: string;
  city?: string;
  description: string;
  employment_type: string;
  job_type?: string;
  experience_level: string;
  salary_min?: number;
  salary_max?: number;
  salary?: string;
  salary_currency?: string;
  is_active?: boolean;
  visa_sponsorship: boolean;
  visa_sponsorship_confidence: number;
  visa_types?: string[];
  international_student_friendly: boolean;
  source_website: string;
  source_url: string;
  job_document_url?: string;
  posted_date?: string;
  scraped_at: string;
  created_at: string;
  updated_at: string;
  remote_option: boolean;
  required_skills?: string[];
  preferred_skills?: string[];
  education_requirements?: string;
  expires_at?: string;
  posted_by_user_id?: number;
  is_joborra_job: boolean;
  is_duplicate: boolean;
  company_id?: number;
}

export interface JobStats {
  total_jobs: number;
  visa_friendly_jobs: number;
  visa_friendly_percentage: number;
  student_friendly_jobs: number;
  student_friendly_percentage: number;
  jobs_by_state: Record<string, number>;
  jobs_by_source: Record<string, number>;
  average_salary: number;
  recent_jobs_count: number;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface SessionInfo {
  session_id: string;
  user_id: number;
  user_email: string;
  created_at: string;
  last_activity: string;
  ip_address: string;
  user_agent: string;
  device_info: {
    browser: string;
    os: string;
    device: string;
  };
}

// Form Types
export interface LoginForm {
  email: string;
  password: string;
}

export interface RegisterForm {
  email: string;
  password: string;
  full_name: string;
  contact_number?: string;
  role?: 'student' | 'employer';
  university?: string;
  degree?: string;
  graduation_year?: number;
  visa_status?: string;
  city_suburb?: string;
  date_of_birth?: string; // ISO datetime string
  // Study details for students
  course_name?: string;
  institution_name?: string;
  course_start_date?: string; // ISO datetime string
  course_end_date?: string;   // ISO datetime string

  company_name?: string;
  company_website?: string;
  company_size?: string;
  industry?: string;
  company_description?: string;
  company_abn?: string;
  employer_role_title?: string;
}

export interface JobFilters {
  search: string;
  location: string;
  visa_sponsorship: boolean | null;
  student_friendly: boolean;
  experience_level: string;
  source: string;
  salary_min?: number;
  salary_max?: number;
  // New filters
  category?: 'casual' | 'career' | string;
  work_type?: 'Full-time' | 'Part-time' | 'Contract' | 'Internship' | string;
  remote_friendly?: boolean;
  visa_types?: string[]; // e.g., ["Subclass 482", "Subclass 186"]
  industry?: string;
}

// API Response Types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

// Favorites
export interface JobFavorite {
  id: number;
  job_id: number;
  created_at: string;
  notes?: string | null;
}

export interface JobFavoriteWithJob extends JobFavorite {
  job: Job;
}

// Employer Posting
export interface EmployerJobCreate {
  title: string;
  description: string;
  location?: string;
  city?: string;
  state?: string;
  salary_min?: number;
  salary_max?: number;
  salary_currency?: string;
  salary?: string;
  employment_type?: string;
  job_type?: string;
  role_category?: string;
  experience_level?: string;
  remote_option?: boolean;
  visa_sponsorship?: boolean;
  visa_types?: string[];
  international_student_friendly?: boolean;
  education_requirements?: string;
  expires_at?: string;
}

export interface EmployerJobUpdate extends Partial<EmployerJobCreate> {
  is_active?: boolean;
}

export interface JobDraft {
  id: number;
  title: string;
  description?: string;
  location?: string;
  city?: string;
  state?: string;
  salary_min?: number;
  salary_max?: number;
  salary_currency: string;
  salary?: string;
  employment_type?: string;
  job_type?: string;
  role_category?: string;
  experience_level?: string;
  remote_option: boolean;
  visa_sponsorship: boolean;
  visa_types?: string[];
  international_student_friendly: boolean;
  required_skills?: string[];
  preferred_skills?: string[];
  education_requirements?: string;
  expires_at?: string;
  draft_name?: string;
  step: number;
  created_by_user_id: number;
  created_at: string;
  updated_at?: string;
}

export interface JobDraftCreate {
  title: string;
  description?: string;
  location?: string;
  city?: string;
  state?: string;
  salary_min?: number;
  salary_max?: number;
  salary_currency?: string;
  salary?: string;
  employment_type?: string;
  job_type?: string;
  role_category?: string;
  experience_level?: string;
  remote_option?: boolean;
  visa_sponsorship?: boolean;
  visa_types?: string[];
  international_student_friendly?: boolean;
  required_skills?: string[];
  preferred_skills?: string[];
  education_requirements?: string;
  expires_at?: string;
  draft_name?: string;
  step?: number;
}

// UI State Types
export interface LoadingState {
  [key: string]: boolean;
}

export interface ErrorState {
  [key: string]: string | null;
}

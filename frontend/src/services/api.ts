import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { 
  User, 
  Job, 
  JobStats, 
  AuthResponse, 
  SessionInfo, 
  LoginForm, 
  RegisterForm, 
  JobFilters,
  PaginatedResponse,
  EmployerJobCreate,
  EmployerJobUpdate 
} from '../types';

class ApiService {
  private api: AxiosInstance;
  private baseURL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  constructor() {
    this.api = axios.create({
      baseURL: this.baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.api.interceptors.request.use((config) => {
      const token = localStorage.getItem('token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Response interceptor to handle auth errors
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          this.clearAuth();
          window.location.href = '/auth';
        }
        return Promise.reject(error);
      }
    );
  }

  // Helpers
  getFileUrl(path: string): string {
    // Ensure we point to backend origin even if baseURL includes /api
    try {
      const url = new URL(this.baseURL);
      const origin = `${url.protocol}//${url.host}`;
      return `${origin}${path}`;
    } catch {
      return `${this.baseURL.replace(/\/api$/, '')}${path}`;
    }
  }

  // Auth methods
  async login(credentials: LoginForm): Promise<AuthResponse> {
    const response: AxiosResponse<AuthResponse> = await this.api.post('/auth/login', credentials);
    this.setAuth(response.data);
    return response.data;
  }

  async register(userData: RegisterForm): Promise<AuthResponse> {
    // Backend expects username; derive from email if UI omits it
    const email = userData.email || '';
    const derived = email.includes('@') ? email.split('@')[0] : email;
    const payload: any = { username: derived, ...userData };
    const response: AxiosResponse<AuthResponse> = await this.api.post('/auth/register', payload);
    this.setAuth(response.data);
    return response.data;
  }

  async logout(): Promise<void> {
    const token = localStorage.getItem('token');
    if (!token) {
      // Already logged out on client
      this.clearAuth();
      return;
    }
    try {
      await this.api.post('/auth/session/logout');
    } catch (err: any) {
      // Treat auth/network errors as successful logout
      const status = err?.response?.status;
      if (status === 401 || status === 403 || err?.message === 'Network Error') {
        // fall through to clearAuth
      } else {
        // For other errors, still clear auth but rethrow for visibility
        this.clearAuth();
        throw err;
      }
    } finally {
      this.clearAuth();
    }
  }

  async logoutAll(): Promise<void> {
    try {
      await this.api.post('/auth/session/logout-all');
    } finally {
      this.clearAuth();
    }
  }

  // Session methods
  async getCurrentSession(): Promise<SessionInfo> {
    const response: AxiosResponse<SessionInfo> = await this.api.get('/auth/session/current');
    return response.data;
  }

  async getAllSessions(): Promise<SessionInfo[]> {
    const response: AxiosResponse<SessionInfo[]> = await this.api.get('/auth/session/all');
    return response.data;
  }

  // Job methods
  async getJobs(filters?: Partial<JobFilters>, page = 1, limit = 20): Promise<PaginatedResponse<Job>> {
    // Backend expects: /api/jobs/search?search=...&location=...&page=&per_page=
    // Map our filters to backend params
    const params = new URLSearchParams();
    if (filters) {
      const f: any = filters;
      if (f.search) params.append('search', String(f.search));
      if (f.location) params.append('location', String(f.location));
      if (typeof f.visa_sponsorship === 'boolean') params.append('visa_sponsorship', String(f.visa_sponsorship));
      if (typeof f.student_friendly === 'boolean') params.append('student_friendly', String(f.student_friendly));
      if (f.category) params.append('category', String(f.category)); // casual/career
      if (f.work_type) params.append('employment_type', String(f.work_type));
      if (typeof f.remote_friendly === 'boolean') params.append('remote', String(f.remote_friendly));
      if (Array.isArray(f.visa_types) && f.visa_types.length) params.append('visa_types', f.visa_types.join(','));
      if (f.industry) params.append('industry', String(f.industry));
      if (typeof f.salary_min === 'number') params.append('salary_min', String(f.salary_min));
      if (typeof f.salary_max === 'number') params.append('salary_max', String(f.salary_max));
    }
    params.append('page', String(page));
    params.append('per_page', String(limit));

    const response = await this.api.get(`/jobs/search?${params.toString()}`);
    const data = response.data as any;
    // Normalize to PaginatedResponse shape expected by UI (items, total_pages, etc.)
    return {
      items: data.jobs ?? [],
      total: data.total ?? 0,
      page: data.page ?? page,
      per_page: data.per_page ?? limit,
      total_pages: data.total_pages ?? Math.ceil((data.total ?? 0) / (data.per_page ?? limit))
    } as PaginatedResponse<Job>;
  }

  async getJobById(id: number): Promise<Job> {
    const response: AxiosResponse<Job> = await this.api.get(`/jobs/${id}`);
    return response.data;
  }

  async getJobStats(): Promise<JobStats> {
    const response: AxiosResponse<any> = await this.api.get('/jobs/stats');
    const d = response.data || {};
    const total = d.total_jobs ?? 0;
    const visa = d.visa_friendly_jobs ?? 0;
    const student = d.student_friendly_jobs ?? 0;
    return {
      total_jobs: total,
      visa_friendly_jobs: visa,
      visa_friendly_percentage: total ? (visa / total) * 100 : 0,
      student_friendly_jobs: student,
      student_friendly_percentage: total ? (student / total) * 100 : 0,
      jobs_by_state: d.jobs_by_state ?? {},
      jobs_by_source: d.jobs_by_source ?? {},
      average_salary: d.average_salary ?? 0,
      recent_jobs_count: d.recent_jobs_count ?? 0,
    } as JobStats;
  }

  async searchJobs(query: string, filters?: Partial<JobFilters>): Promise<Job[]> {
    const params = new URLSearchParams();
    params.append('search', query);
    if (filters) {
      if ((filters as any).location) params.append('location', String((filters as any).location));
    }
    const response: AxiosResponse<any> = await this.api.get(`/jobs/search?${params.toString()}`);
    // Backend returns an object with jobs array
    return response.data?.jobs ?? [];
  }

  async getJobRecommendations(): Promise<Job[]> {
    const response: AxiosResponse<Job[]> = await this.api.get('/jobs/recommended');
    return response.data;
  }

  // Locations autocomplete
  async getLocationSuggestions(query: string, limit = 8): Promise<string[]> {
    if (!query || !query.trim()) return [];
    const params = new URLSearchParams();
    params.append('q', query.trim());
    params.append('limit', String(limit));
    const response: AxiosResponse<{ items: string[] }> = await this.api.get(`/locations/suggest?${params.toString()}`);
    return response.data?.items ?? [];
  }

  // User methods
  async getCurrentUser(): Promise<User> {
    const response: AxiosResponse<User> = await this.api.get('/auth/me');
    return response.data;
  }

  async updateProfile(userData: Partial<User>): Promise<User> {
    // Decide endpoint based on current user role
    const current = this.getCurrentUserFromStorage();
    const role = (current as any)?.role?.toString().toLowerCase();
    const path = role === 'employer'
      ? '/auth/profile/employer'
      : '/auth/profile/student';
    const response: AxiosResponse<User> = await this.api.put(path, userData);
    return response.data;
  }

  // Visa verification methods
  async getVisaStatus(): Promise<any> {
    const response = await this.api.get('/auth/visa/status');
    return response.data;
  }

  async submitVisaVerification(data: any): Promise<any> {
    const response = await this.api.post('/auth/visa/verify', data);
    return response.data;
  }

  async uploadVisaDocument(documentType: 'passport' | 'visa_grant' | 'coe' | 'vevo', file: File): Promise<any> {
    const form = new FormData();
    form.append('file', file);
    const response = await this.api.post(`/auth/visa/documents/upload?document_type=${encodeURIComponent(documentType)}`,
      form,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    );
    return response.data;
  }

  async uploadResume(file: File): Promise<{ resume_url: string }>{
    const form = new FormData();
    form.append('file', file);
    const response = await this.api.post('/auth/profile/resume', form, { headers: { 'Content-Type': 'multipart/form-data' } });
    return response.data;
  }

  // Email verification methods
  async requestEmailVerification(): Promise<{ verification_token: string; verify_url: string } | { message: string }>{
    const response = await this.api.post('/auth/verify/request');
    return response.data;
  }

  async confirmEmailVerification(token: string): Promise<User> {
    const response: AxiosResponse<User> = await this.api.get(`/auth/verify/confirm`, { params: { token } });
    // Update stored user with verified flag
    const stored = this.getCurrentUserFromStorage();
    if (stored && response.data) {
      localStorage.setItem('user', JSON.stringify(response.data));
    }
    return response.data;
  }

  // Employer job posting methods
  async createEmployerJob(data: EmployerJobCreate): Promise<Job> {
    const response: AxiosResponse<Job> = await this.api.post('/auth/employer/jobs', data);
    return response.data;
  }

  async updateEmployerJob(id: number, data: EmployerJobUpdate): Promise<Job> {
    const response: AxiosResponse<Job> = await this.api.put(`/auth/employer/jobs/${id}`, data);
    return response.data;
  }

  async listEmployerJobs(): Promise<Job[]> {
    const response: AxiosResponse<Job[]> = await this.api.get('/auth/employer/jobs');
    return response.data;
  }

  // Employer applications
  async listEmployerApplications(): Promise<Array<{ id: number; job_id: number; status: string; applied_at: string; updated_at: string; cover_letter?: string; resume_url?: string; notes?: string; job: any; user: any }>> {
    const response = await this.api.get('/auth/employer/applications');
    return response.data;
  }

  // Employer company logo upload
  async uploadCompanyLogo(file: File): Promise<{ company_logo_url: string }>{
    const form = new FormData();
    form.append('file', file);
    const response = await this.api.post('/auth/employer/company/logo', form, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  }

  async uploadJobDocument(jobId: number, file: File): Promise<{ job_document_url: string }>{
    const form = new FormData();
    form.append('file', file);
    const response = await this.api.post(`/auth/employer/jobs/${jobId}/document`, form, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  }

  // Utility methods
  private setAuth(authData: AuthResponse): void {
    localStorage.setItem('token', authData.access_token);
    localStorage.setItem('refresh_token', authData.refresh_token);
    localStorage.setItem('user', JSON.stringify(authData.user));
  }

  private clearAuth(): void {
    localStorage.removeItem('token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
  }

  isAuthenticated(): boolean {
    return !!localStorage.getItem('token');
  }

  getCurrentUserFromStorage(): User | null {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  }
}

export const apiService = new ApiService();
export default apiService;

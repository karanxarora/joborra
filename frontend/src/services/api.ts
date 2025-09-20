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
  JobDraft,
  JobDraftCreate,
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
    // If it's already absolute (e.g., Supabase public URL), return as-is
    if (/^https?:\/\//i.test(path)) return path;
    // Ensure we point to backend origin even if baseURL includes /api
    try {
      const url = new URL(this.baseURL);
      const origin = `${url.protocol}//${url.host}`;
      return `${origin}${path}`;
    } catch {
      return `${this.baseURL.replace(/\/api$/, '')}${path}`;
    }
  }

  // Simple method to get resume view URL
  async getResumeViewUrl(): Promise<string | null> {
    try {
      const response = await this.api.get('/auth/resume/view');
      return response.data.resume_url;
    } catch (error) {
      console.error('Failed to get resume view URL:', error);
      return null;
    }
  }

  // Auth methods
  async login(credentials: LoginForm): Promise<AuthResponse> {
    const response: AxiosResponse<AuthResponse> = await this.api.post('/auth/login', credentials);
    this.setAuth(response.data);
    return response.data;
  }

  // Google OAuth helpers
  getGoogleLoginUrl(): string {
    try {
      const url = new URL(this.baseURL);
      const origin = `${url.protocol}//${url.host}`;
      return `${origin}/api/auth/google/login`;
    } catch {
      return `${this.baseURL.replace(/\/$/, '')}/auth/google/login`;
    }
  }

  async googleLoginWithIdToken(id_token: string): Promise<AuthResponse> {
    const response: AxiosResponse<AuthResponse> = await this.api.post('/auth/oauth/google', { id_token });
    this.setAuth(response.data);
    return response.data;
  }

  // Forgot Password methods
  async forgotPassword(email: string): Promise<{ message: string; email_sent: boolean }> {
    const response = await this.api.post('/auth/forgot-password', { email });
    return response.data;
  }

  async resetPassword(token: string, newPassword: string): Promise<{ message: string; success: boolean }> {
    const response = await this.api.post('/auth/reset-password', { token, new_password: newPassword });
    return response.data;
  }

  async linkGoogleWithIdToken(id_token: string): Promise<User> {
    const response: AxiosResponse<User> = await this.api.post('/auth/oauth/google/link', { id_token });
    // Update local user cache
    const stored = this.getCurrentUserFromStorage();
    if (stored) {
      localStorage.setItem('user', JSON.stringify(response.data));
    }
    return response.data;
  }

  async register(userData: RegisterForm): Promise<any> {
    // Backend expects username; derive from email if UI omits it
    const email = userData.email || '';
    const derived = email.includes('@') ? email.split('@')[0] : email;
    const payload: any = { username: derived, ...userData };
    // Backend returns user object (no tokens)
    const response = await this.api.post('/auth/register', payload);
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
    // Persist updated user so UI reflects changes immediately
    if (response?.data) {
      localStorage.setItem('user', JSON.stringify(response.data));
    }
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

  async uploadVisaDocument(file: File): Promise<any> {
    const form = new FormData();
    form.append('file', file);
    const response = await this.api.post('/auth/visa/documents/upload', form, { headers: { 'Content-Type': 'multipart/form-data' } });
    return response.data;
  }

  async getVisaDocuments(): Promise<any> {
    const response = await this.api.get('/auth/visa/documents');
    return response.data;
  }

  async uploadResume(file: File): Promise<{ resume_url: string }>{
    const form = new FormData();
    form.append('file', file);
    const response = await this.api.post('/auth/profile/resume', form, { headers: { 'Content-Type': 'multipart/form-data' } });
    return response.data;
  }

  // Email verification methods - DISABLED FOR NOW
  // async requestEmailVerification(): Promise<{ verification_token: string; verify_url: string } | { message: string }>{
  //   const response = await this.api.post('/auth/verify/request');
  //   return response.data;
  // }

  // async confirmEmailVerification(token: string): Promise<User> {
  //   const response: AxiosResponse<User> = await this.api.get(`/auth/verify/confirm`, { params: { token } });
  //   // Update stored user with verified flag
  //   const stored = this.getCurrentUserFromStorage();
  //   if (stored && response.data) {
  //     localStorage.setItem('user', JSON.stringify(response.data);
  //   }
  //   return response.data;
  // }

  // Job Draft methods
  async createJobDraft(draftData: JobDraftCreate): Promise<JobDraft> {
    const response = await this.api.post('/auth/employer/job-drafts', draftData);
    return response.data;
  }

  async getJobDrafts(): Promise<JobDraft[]> {
    const response = await this.api.get('/auth/employer/job-drafts');
    return response.data;
  }

  async getJobDraft(draftId: number): Promise<JobDraft> {
    const response = await this.api.get(`/auth/employer/job-drafts/${draftId}`);
    return response.data;
  }

  async updateJobDraft(draftId: number, draftData: Partial<JobDraftCreate>): Promise<JobDraft> {
    const response = await this.api.put(`/auth/employer/job-drafts/${draftId}`, draftData);
    return response.data;
  }

  async deleteJobDraft(draftId: number): Promise<{ message: string }> {
    const response = await this.api.delete(`/auth/employer/job-drafts/${draftId}`);
    return response.data;
  }

  async publishJobDraft(draftId: number): Promise<Job> {
    const response = await this.api.post(`/auth/employer/job-drafts/${draftId}/publish`);
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

  async deleteJob(jobId: number): Promise<{ message: string }> {
    const response = await this.api.delete(`/auth/employer/jobs/${jobId}`);
    return response.data;
  }

  // Employer applications
  async listEmployerApplications(): Promise<Array<{ id: number; job_id: number; status: string; applied_at: string; updated_at: string; cover_letter?: string; resume_url?: string; notes?: string; job: any; user: any }>> {
    const response = await this.api.get('/auth/employer/applications');
    return response.data;
  }

  // Student favorites
  async listFavorites(): Promise<Array<{ id: number; job_id: number; created_at: string; notes?: string | null; job: Job }>> {
    const response = await this.api.get('/auth/student/favorites');
    return response.data;
  }

  async addFavorite(job_id: number, notes?: string | null): Promise<{ id: number; job_id: number; created_at: string; notes?: string | null }> {
    const response = await this.api.post('/auth/student/favorites', { job_id, notes: notes ?? null });
    return response.data;
  }

  async removeFavorite(favorite_id: number): Promise<{ message: string }> {
    const response = await this.api.delete(`/auth/student/favorites/${favorite_id}`);
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

  // AI Generation (Gemini-powered)
  async generateJobDescription(input: {
    title?: string;
    skills?: string[];
    role_category?: string;
    employment_type?: string;
    location?: string;
    prompt?: string;         // system prompt constructed on client
    model?: string;          // e.g., 'gemini-1.5-flash' | 'gemini-1.5-pro'
    context?: Record<string, any>; // optional structured context
  }): Promise<string> {
    const body: any = {
      title: input?.title || '',
      skills: input?.skills || [],
    };
    if (input?.prompt) body.prompt = input.prompt;
    if (input?.model) body.model = input.model;
    
    // Build context with additional job details
    const context = {
      ...input?.context,
      role_category: input?.role_category,
      employment_type: input?.employment_type,
      location: input?.location,
    };
    body.context = context;
    
    const resp: AxiosResponse<any> = await this.api.post('/ai/generate/job-description', body);
    const text = resp.data?.text || resp.data?.description || '';
    if (!text || typeof text !== 'string') {
      throw new Error('AI generated empty or invalid content');
    }
    return text;
  }

  // AI Services
  async getSkillRecommendations(query: string, context?: string): Promise<string[]> {
    try {
      const response = await this.api.post('/ai/skill-recommendations', {
        query,
        context
      });
      return response.data.skills || [];
    } catch (error) {
      console.error('Failed to get skill recommendations:', error);
      return [];
    }
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

import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../contexts/ToastContext';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import { 
  Briefcase, 
  Users, 
  TrendingUp, 
  Plus,
  Eye,
  Edit,
  Calendar,
  MapPin,
  DollarSign,
  Trash2
} from 'lucide-react';
import apiService from '../services/api';

interface JobStats {
  total_jobs: number;
  active_jobs: number;
  total_applications: number;
  pending_applications: number;
}

interface JobSummary {
  id: number;
  title: string;
  location: string;
  applications_count: number;
  posted_date: string;
  is_active: boolean;
  salary_min?: number;
  salary_max?: number;
}

const EmployerDashboardPage: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [stats, setStats] = useState<JobStats | null>(null);
  const [recentJobs, setRecentJobs] = useState<JobSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [deletingJobId, setDeletingJobId] = useState<number | null>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      // Load employer jobs and applications
      const [jobsResponse, applicationsResponse] = await Promise.all([
        apiService.listEmployerJobs(),
        apiService.listEmployerApplications()
      ]);

      const jobs = jobsResponse || [];
      const applications = applicationsResponse || [];

      // Calculate stats
      const totalJobs = jobs.length;
      // For now, consider all jobs as active since is_active is not in the Job interface
      const activeJobs = jobs.length;
      const totalApplications = applications.length;
      const pendingApplications = applications.filter(app => 
        app.status === 'applied' || app.status === 'In Review'
      ).length;

      setStats({
        total_jobs: totalJobs,
        active_jobs: activeJobs,
        total_applications: totalApplications,
        pending_applications: pendingApplications
      });

      // Get recent jobs (last 5)
      const recent = jobs
        .sort((a, b) => new Date(b.posted_date || b.scraped_at || b.created_at).getTime() - new Date(a.posted_date || a.scraped_at || a.created_at).getTime())
        .slice(0, 5)
        .map(job => ({
          id: job.id,
          title: job.title,
          location: job.location || 'Location not specified',
          applications_count: applications.filter(app => app.job_id === job.id).length,
          posted_date: job.posted_date || job.scraped_at || job.created_at,
          is_active: job.is_active !== false, // Use actual is_active field
          salary_min: job.salary_min,
          salary_max: job.salary_max
        }));

      setRecentJobs(recent);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatSalary = (amount: number) => {
    if (amount >= 1000) {
      return `$${Math.round(amount / 1000)}k`;
    }
    return `$${amount}`;
  };

  const formatDate = (dateString: string) => {
    if (!dateString) return 'Date not available';
    try {
      return new Date(dateString).toLocaleDateString('en-AU', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    } catch (error) {
      return 'Invalid Date';
    }
  };

  const handleDeleteJob = async (jobId: number) => {
    if (!window.confirm('Are you sure you want to delete this job posting? This action cannot be undone.')) {
      return;
    }

    try {
      setDeletingJobId(jobId);
      await apiService.deleteJob(jobId);
      toast('Job deleted successfully', 'success');
      // Reload dashboard data
      await loadDashboardData();
    } catch (error) {
      console.error('Failed to delete job:', error);
      toast('Failed to delete job', 'error');
    } finally {
      setDeletingJobId(null);
    }
  };

  const handleViewJob = (jobId: number) => {
    navigate(`/employer/jobs/${jobId}`);
  };

  const handleEditJob = (jobId: number) => {
    // For now, navigate to post job page
    // TODO: Create a dedicated job edit page
    navigate(`/employer/post-job?edit=${jobId}`);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900">Employer Dashboard</h1>
          <p className="text-slate-600 mt-2">
            Welcome back, {user?.full_name || user?.email}! Manage your job postings and applications.
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="p-6">
            <div className="flex items-center">
              <div className="p-2 bg-primary-100 rounded-lg">
                <Briefcase className="h-6 w-6 text-primary-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-slate-600">Total Jobs</p>
                <p className="text-2xl font-bold text-slate-900">{stats?.total_jobs || 0}</p>
              </div>
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg">
                <TrendingUp className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-slate-600">Active Jobs</p>
                <p className="text-2xl font-bold text-slate-900">{stats?.active_jobs || 0}</p>
              </div>
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Users className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-slate-600">Total Applications</p>
                <p className="text-2xl font-bold text-slate-900">{stats?.total_applications || 0}</p>
              </div>
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center">
              <div className="p-2 bg-amber-100 rounded-lg">
                <Calendar className="h-6 w-6 text-amber-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-slate-600">Pending Review</p>
                <p className="text-2xl font-bold text-slate-900">{stats?.pending_applications || 0}</p>
              </div>
            </div>
          </Card>
        </div>

        {/* Quick Actions */}
        <div className="mb-8">
          <Card className="p-6">
            <h2 className="text-lg font-semibold text-slate-900 mb-4">Quick Actions</h2>
            <div className="flex flex-wrap gap-4">
              <Button 
                onClick={() => navigate('/employer/post-job')}
                className="flex items-center gap-2"
              >
                <Plus className="h-4 w-4" />
                Post New Job
              </Button>
              <Button 
                variant="outline"
                onClick={() => navigate('/employer/applications')}
                className="flex items-center gap-2"
              >
                <Users className="h-4 w-4" />
                View Applications
              </Button>
              <Button 
                variant="outline"
                onClick={() => navigate('/employer/company')}
                className="flex items-center gap-2"
              >
                <Edit className="h-4 w-4" />
                Company Info
              </Button>
            </div>
          </Card>
        </div>

        {/* Recent Jobs */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <Card className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-slate-900">Recent Job Postings</h2>
              <Button 
                variant="ghost" 
                size="sm"
                onClick={() => navigate('/employer/post-job')}
              >
                View All
              </Button>
            </div>
            
            {recentJobs.length === 0 ? (
              <div className="text-center py-8">
                <Briefcase className="h-12 w-12 text-slate-300 mx-auto mb-4" />
                <p className="text-slate-600 mb-4">No job postings yet</p>
                <Button onClick={() => navigate('/employer/post-job')}>
                  Post Your First Job
                </Button>
              </div>
            ) : (
              <div className="space-y-4">
                {recentJobs.map((job) => (
                  <div key={job.id} className="border border-slate-200 rounded-lg p-4 hover:border-slate-300 hover:shadow-sm transition-all cursor-pointer" onClick={() => handleViewJob(job.id)}>
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h3 className="font-medium text-slate-900">{job.title}</h3>
                        <div className="flex items-center text-sm text-slate-600 mt-1">
                          <MapPin className="h-4 w-4 mr-1" />
                          {job.location}
                        </div>
                        <div className="flex items-center text-sm text-slate-600 mt-1">
                          <Calendar className="h-4 w-4 mr-1" />
                          Posted {formatDate(job.posted_date)}
                        </div>
                        {job.salary_min && job.salary_max && (
                          <div className="flex items-center text-sm text-slate-600 mt-1">
                            <DollarSign className="h-4 w-4 mr-1" />
                            {formatSalary(job.salary_min)} - {formatSalary(job.salary_max)}
                          </div>
                        )}
                      </div>
                      <div className="flex items-center gap-2 ml-4">
                        <div className="text-right">
                          <div className="text-sm font-medium text-slate-900">
                            {job.applications_count} applications
                          </div>
                          <div className={`text-xs px-2 py-1 rounded-full ${
                            job.is_active 
                              ? 'bg-green-100 text-green-800' 
                              : 'bg-slate-100 text-slate-800'
                          }`}>
                            {job.is_active ? 'Active' : 'Inactive'}
                          </div>
                        </div>
                        <div className="flex items-center gap-1" onClick={(e) => e.stopPropagation()}>
                          <Button 
                            variant="ghost" 
                            size="sm"
                            onClick={() => handleViewJob(job.id)}
                            title="View Job Details"
                          >
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Button 
                            variant="ghost" 
                            size="sm"
                            onClick={() => handleEditJob(job.id)}
                            title="Edit Job"
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button 
                            variant="ghost" 
                            size="sm"
                            onClick={() => handleDeleteJob(job.id)}
                            disabled={deletingJobId === job.id}
                            title="Delete Job"
                            className="text-red-600 hover:text-red-700 hover:bg-red-50"
                          >
                            {deletingJobId === job.id ? (
                              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-red-600"></div>
                            ) : (
                              <Trash2 className="h-4 w-4" />
                            )}
                          </Button>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>

          {/* Recent Applications */}
          <Card className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-slate-900">Recent Applications</h2>
              <Button 
                variant="ghost" 
                size="sm"
                onClick={() => navigate('/employer/applications')}
              >
                View All
              </Button>
            </div>
            
            <div className="text-center py-8">
              <Users className="h-12 w-12 text-slate-300 mx-auto mb-4" />
              <p className="text-slate-600 mb-4">No applications yet</p>
              <p className="text-sm text-slate-500">
                Applications will appear here once candidates start applying to your jobs.
              </p>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default EmployerDashboardPage;

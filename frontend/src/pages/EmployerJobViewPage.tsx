import React, { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../contexts/ToastContext';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import { 
  ArrowLeft,
  MapPin,
  Calendar,
  DollarSign,
  Clock,
  Users,
  Briefcase,
  Edit,
  Trash2,
  Building2
} from 'lucide-react';
import apiService from '../services/api';

interface Job {
  id: number;
  title: string;
  description: string;
  location: string;
  state?: string;
  city?: string;
  salary_min?: number;
  salary_max?: number;
  salary_currency?: string;
  employment_type?: string;
  experience_level?: string;
  remote_option: boolean;
  visa_sponsorship: boolean;
  visa_types?: string[];
  required_skills?: string[];
  preferred_skills?: string[];
  education_requirements?: string;
  posted_date?: string;
  expires_at?: string;
  is_active: boolean;
  company_id?: number;
}

const EmployerJobViewPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { toast } = useToast();
  const [job, setJob] = useState<Job | null>(null);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState(false);

  const loadJob = useCallback(async () => {
    try {
      setLoading(true);
      const jobData = await apiService.getJobById(parseInt(id!));
      setJob(jobData);
    } catch (error) {
      console.error('Failed to load job:', error);
      toast('Failed to load job details', 'error');
      navigate('/employer/dashboard');
    } finally {
      setLoading(false);
    }
  }, [id, toast, navigate]);

  useEffect(() => {
    if (id) {
      loadJob();
    }
  }, [id, loadJob]);

  const handleDeleteJob = async () => {
    if (!window.confirm('Are you sure you want to delete this job posting? This action cannot be undone.')) {
      return;
    }

    try {
      setDeleting(true);
      await apiService.deleteJob(job!.id);
      toast('Job deleted successfully', 'success');
      navigate('/employer/dashboard');
    } catch (error) {
      console.error('Failed to delete job:', error);
      toast('Failed to delete job', 'error');
    } finally {
      setDeleting(false);
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
        month: 'long',
        day: 'numeric'
      });
    } catch (error) {
      return 'Invalid Date';
    }
  };

  const getEmploymentTypeLabel = (type: string) => {
    const labels: { [key: string]: string } = {
      'FULL_TIME': 'Full-time',
      'PART_TIME': 'Part-time',
      'CONTRACT': 'Contract',
      'CASUAL': 'Casual',
      'INTERNSHIP': 'Internship'
    };
    return labels[type] || type;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!job) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-slate-900 mb-4">Job Not Found</h2>
          <p className="text-slate-600 mb-6">The job you're looking for doesn't exist or has been removed.</p>
          <Button onClick={() => navigate('/employer/dashboard')}>
            Back to Dashboard
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <Button 
            variant="ghost" 
            onClick={() => navigate('/employer/dashboard')}
            className="mb-4"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Dashboard
          </Button>
          
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-3xl font-bold text-slate-900">{job.title}</h1>
              <div className="flex items-center text-slate-600 mt-2">
                <Building2 className="h-5 w-5 mr-2" />
                <span>{user?.company_name || 'Your Company'}</span>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <Button 
                variant="outline"
                onClick={() => navigate(`/employer/post-job?edit=${job.id}`)}
              >
                <Edit className="h-4 w-4 mr-2" />
                Edit Job
              </Button>
              <Button 
                variant="outline"
                onClick={() => navigate(`/employer/applications?job=${job.id}`)}
              >
                <Users className="h-4 w-4 mr-2" />
                View Applications
              </Button>
              <Button 
                variant="outline"
                onClick={handleDeleteJob}
                disabled={deleting}
                className="text-red-600 hover:text-red-700 hover:bg-red-50"
              >
                {deleting ? (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-red-600 mr-2"></div>
                ) : (
                  <Trash2 className="h-4 w-4 mr-2" />
                )}
                Delete
              </Button>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Job Description */}
            <Card className="p-6">
              <h2 className="text-xl font-semibold text-slate-900 mb-4">Job Description</h2>
              <div 
                className="prose prose-slate max-w-none"
                dangerouslySetInnerHTML={{ __html: job.description || 'No description provided.' }}
              />
            </Card>

            {/* Requirements */}
            {(job.required_skills && Array.isArray(job.required_skills) && job.required_skills.length > 0) && (
              <Card className="p-6">
                <h2 className="text-xl font-semibold text-slate-900 mb-4">Required Skills</h2>
                <div className="flex flex-wrap gap-2">
                  {job.required_skills.map((skill, index) => (
                    <span 
                      key={index}
                      className="px-3 py-1 bg-primary-100 text-primary-800 rounded-full text-sm"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </Card>
            )}

            {(job.preferred_skills && Array.isArray(job.preferred_skills) && job.preferred_skills.length > 0) && (
              <Card className="p-6">
                <h2 className="text-xl font-semibold text-slate-900 mb-4">Preferred Skills</h2>
                <div className="flex flex-wrap gap-2">
                  {job.preferred_skills.map((skill, index) => (
                    <span 
                      key={index}
                      className="px-3 py-1 bg-slate-100 text-slate-800 rounded-full text-sm"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </Card>
            )}

            {job.education_requirements && (
              <Card className="p-6">
                <h2 className="text-xl font-semibold text-slate-900 mb-4">Education Requirements</h2>
                <p className="text-slate-700">{job.education_requirements}</p>
              </Card>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Job Details */}
            <Card className="p-6">
              <h2 className="text-lg font-semibold text-slate-900 mb-4">Job Details</h2>
              <div className="space-y-4">
                <div className="flex items-center">
                  <MapPin className="h-5 w-5 text-slate-400 mr-3" />
                  <div>
                    <p className="text-sm text-slate-600">Location</p>
                    <p className="font-medium text-slate-900">
                      {job.location}
                      {job.city && job.state && `, ${job.city}, ${job.state}`}
                    </p>
                  </div>
                </div>

                <div className="flex items-center">
                  <Calendar className="h-5 w-5 text-slate-400 mr-3" />
                  <div>
                    <p className="text-sm text-slate-600">Posted</p>
                    <p className="font-medium text-slate-900">{formatDate(job.posted_date || '')}</p>
                  </div>
                </div>

                {job.expires_at && (
                  <div className="flex items-center">
                    <Clock className="h-5 w-5 text-slate-400 mr-3" />
                    <div>
                      <p className="text-sm text-slate-600">Expires</p>
                      <p className="font-medium text-slate-900">{formatDate(job.expires_at)}</p>
                    </div>
                  </div>
                )}

                {job.salary_min && job.salary_max && (
                  <div className="flex items-center">
                    <DollarSign className="h-5 w-5 text-slate-400 mr-3" />
                    <div>
                      <p className="text-sm text-slate-600">Salary</p>
                      <p className="font-medium text-slate-900">
                        {formatSalary(job.salary_min)} - {formatSalary(job.salary_max)} {job.salary_currency || 'AUD'}
                      </p>
                    </div>
                  </div>
                )}

                {job.employment_type && (
                  <div className="flex items-center">
                    <Briefcase className="h-5 w-5 text-slate-400 mr-3" />
                    <div>
                      <p className="text-sm text-slate-600">Employment Type</p>
                      <p className="font-medium text-slate-900">{getEmploymentTypeLabel(job.employment_type)}</p>
                    </div>
                  </div>
                )}

                {job.experience_level && (
                  <div className="flex items-center">
                    <Users className="h-5 w-5 text-slate-400 mr-3" />
                    <div>
                      <p className="text-sm text-slate-600">Experience Level</p>
                      <p className="font-medium text-slate-900">{job.experience_level}</p>
                    </div>
                  </div>
                )}
              </div>
            </Card>

            {/* Job Status */}
            <Card className="p-6">
              <h2 className="text-lg font-semibold text-slate-900 mb-4">Job Status</h2>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-600">Status</span>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    job.is_active 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-slate-100 text-slate-800'
                  }`}>
                    {job.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
                
                {job.remote_option && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-slate-600">Remote Work</span>
                    <span className="text-sm font-medium text-slate-900">Available</span>
                  </div>
                )}
                
                {job.visa_sponsorship && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-slate-600">Visa Sponsorship</span>
                    <span className="text-sm font-medium text-slate-900">Available</span>
                  </div>
                )}
              </div>
            </Card>

            {/* Visa Types */}
            {job.visa_types && Array.isArray(job.visa_types) && job.visa_types.length > 0 && (
              <Card className="p-6">
                <h2 className="text-lg font-semibold text-slate-900 mb-4">Accepted Visa Types</h2>
                <div className="space-y-2">
                  {job.visa_types.map((visaType, index) => (
                    <div key={index} className="text-sm text-slate-700">
                      • {visaType}
                    </div>
                  ))}
                </div>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default EmployerJobViewPage;

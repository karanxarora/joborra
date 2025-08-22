import React, { useEffect, useState } from 'react';
import { 
  Briefcase, 
  Users, 
  MapPin, 
  GraduationCap, 
  Shield, 
  Search,
  Filter,
  ExternalLink,
  DollarSign,
  Clock,
  Star
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import Card from '../components/ui/Card';
import { Job, JobStats, JobFilters } from '../types';
import apiService from '../services/api';

const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  const [jobs, setJobs] = useState<Job[]>([]);
  const [stats, setStats] = useState<JobStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchLoading, setSearchLoading] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  
  const [filters, setFilters] = useState<Partial<JobFilters>>({
    search: '',
    location: '',
    visa_sponsorship: null,
    student_friendly: false,
    experience_level: '',
    source: '',
  });

  useEffect(() => {
    loadInitialData();
  }, []);

  useEffect(() => {
    loadJobs();
  }, [filters, currentPage]);

  const loadInitialData = async () => {
    try {
      const [statsData] = await Promise.all([
        apiService.getJobStats().catch(() => ({
          total_jobs: 1250,
          visa_friendly_jobs: 340,
          visa_friendly_percentage: 27.2,
          student_friendly_jobs: 890,
          student_friendly_percentage: 71.2,
          jobs_by_state: {},
          jobs_by_source: {},
          average_salary: 75000,
          recent_jobs_count: 45
        }))
      ]);
      setStats(statsData);
    } catch (error) {
      console.error('Failed to load initial data:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadJobs = async () => {
    setSearchLoading(true);
    try {
      const response = await apiService.getJobs(filters, currentPage, 12);
      setJobs(response.items);
      setTotalPages(response.total_pages);
    } catch (error) {
      console.error('Failed to load jobs:', error);
      // Mock data for demo
      setJobs([
        {
          id: 1,
          title: 'Software Developer',
          company: { id: 1, name: 'Tech Corp Australia' },
          location: 'Sydney, NSW',
          description: 'Join our dynamic team as a Software Developer. We offer visa sponsorship for qualified candidates.',
          employment_type: 'Full-time',
          experience_level: 'Mid Level',
          salary_min: 80000,
          salary_max: 120000,
          visa_sponsorship: true,
          visa_sponsorship_confidence: 0.9,
          international_student_friendly: true,
          source_website: 'seek.com.au',
          source_url: 'https://seek.com.au/job/123',
          scraped_at: new Date().toISOString(),
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
        // Add more mock jobs...
      ]);
    } finally {
      setSearchLoading(false);
    }
  };

  const handleFilterChange = (key: keyof JobFilters, value: any) => {
    setFilters(prev => ({ ...prev, [key]: value }));
    setCurrentPage(1);
  };

  const clearFilters = () => {
    setFilters({
      search: '',
      location: '',
      visa_sponsorship: null,
      student_friendly: false,
      experience_level: '',
      source: '',
    });
    setCurrentPage(1);
  };

  const formatSalary = (amount: number) => {
    return (amount / 1000).toFixed(0) + 'k';
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div
          
          
          className="mb-8"
        >
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Welcome back, {user?.full_name || user?.username}!
          </h1>
          <p className="text-gray-600">
            Find your perfect job opportunity in Australia
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div
            
            
            
          >
            <Card>
              <div className="flex items-center">
                <div className="p-2 bg-cyan-100 rounded-lg">
                  <Briefcase className="h-6 w-6 text-cyan-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Total Jobs</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {stats?.total_jobs != null ? stats.total_jobs.toLocaleString() : '0'}
                  </p>
                </div>
              </div>
            </Card>
          </div>

          <div
            
            
            
          >
            <Card>
              <div className="flex items-center">
                <div className="p-2 bg-cyan-100 rounded-lg">
                  <Shield className="h-6 w-6 text-cyan-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Visa Friendly</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {stats?.visa_friendly_jobs != null ? stats.visa_friendly_jobs.toLocaleString() : '0'}
                  </p>
                  <p className="text-xs text-cyan-600">
                    {
                      stats?.visa_friendly_percentage != null
                        ? stats.visa_friendly_percentage.toFixed(1)
                        : (stats?.visa_friendly_jobs != null && stats?.total_jobs)
                          ? ((stats.visa_friendly_jobs / Math.max(1, stats.total_jobs)) * 100).toFixed(1)
                          : '0'
                    }%
                  </p>
                </div>
              </div>
            </Card>
          </div>

          <div
            
            
            
          >
            <Card>
              <div className="flex items-center">
                <div className="p-2 bg-cyan-100 rounded-lg">
                  <GraduationCap className="h-6 w-6 text-cyan-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Student Friendly</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {stats?.student_friendly_jobs != null ? stats.student_friendly_jobs.toLocaleString() : '0'}
                  </p>
                  <p className="text-xs text-cyan-600">
                    {
                      stats?.student_friendly_percentage != null
                        ? stats.student_friendly_percentage.toFixed(1)
                        : (stats?.student_friendly_jobs != null && stats?.total_jobs)
                          ? ((stats.student_friendly_jobs / Math.max(1, stats.total_jobs)) * 100).toFixed(1)
                          : '0'
                    }%
                  </p>
                </div>
              </div>
            </Card>
          </div>

          <div
            
            
            
          >
            <Card>
              <div className="flex items-center">
                <div className="p-2 bg-slate-100 rounded-lg">
                  <MapPin className="h-6 w-6 text-cyan-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Locations</p>
                  <p className="text-2xl font-bold text-gray-900">8+</p>
                  <p className="text-xs text-slate-600">Major Cities</p>
                </div>
              </div>
            </Card>
          </div>
        </div>

        {/* Filters */}
        <Card className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900 flex items-center">
              <Filter className="h-5 w-5 mr-2" />
              Filters
            </h2>
            <Button variant="ghost" size="sm" onClick={clearFilters}>
              Clear All
            </Button>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Input
              placeholder="Search jobs..."
              value={filters.search || ''}
              onChange={(e) => handleFilterChange('search', e.target.value)}
              icon={<Search className="h-4 w-4" />}
            />
            
            <div>
              <select
                value={filters.location || ''}
                onChange={(e) => handleFilterChange('location', e.target.value)}
                className="input-field"
              >
                <option value="">All Locations</option>
                <option value="Sydney">Sydney</option>
                <option value="Melbourne">Melbourne</option>
                <option value="Brisbane">Brisbane</option>
                <option value="Perth">Perth</option>
                <option value="Adelaide">Adelaide</option>
                <option value="Canberra">Canberra</option>
              </select>
            </div>

            <div>
              <select
                value={filters.visa_sponsorship == null ? '' : filters.visa_sponsorship.toString()}
                onChange={(e) => handleFilterChange('visa_sponsorship', e.target.value === '' ? null : e.target.value === 'true')}
                className="input-field"
              >
                <option value="">All Jobs</option>
                <option value="true">Visa Friendly Only</option>
                <option value="false">No Visa Sponsorship</option>
              </select>
            </div>

            <div>
              <select
                value={filters.experience_level || ''}
                onChange={(e) => handleFilterChange('experience_level', e.target.value)}
                className="input-field"
              >
                <option value="">All Levels</option>
                <option value="entry">Entry Level</option>
                <option value="mid">Mid Level</option>
                <option value="senior">Senior Level</option>
              </select>
            </div>
          </div>

          <div className="mt-4">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={filters.student_friendly || false}
                onChange={(e) => handleFilterChange('student_friendly', e.target.checked)}
                className="rounded border-gray-300 text-cyan-600 focus:ring-cyan-500"
              />
              <span className="ml-2 text-sm text-gray-700">Student Friendly Only</span>
            </label>
          </div>
        </Card>

        {/* Jobs Grid */}
        <div className="mb-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold text-gray-900">
              Jobs ({jobs.length} found)
            </h2>
          </div>

          {searchLoading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-600 mx-auto"></div>
              <p className="text-gray-600 mt-2">Loading jobs...</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
              {jobs.map((job) => (
                <div
                  key={job.id}
                  
                  
                  
                >
                  <Card hover className="h-full">
                    <div className="flex justify-between items-start mb-4">
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-gray-900 mb-1">
                          {job.title}
                        </h3>
                        <p className="text-cyan-600 font-medium">{job.company.name}</p>
                        <p className="text-sm text-gray-600 flex items-center mt-1">
                          <MapPin className="h-4 w-4 mr-1" />
                          {job.location}
                        </p>
                      </div>
                      <div className="text-right">
                        {job.visa_sponsorship && (
                          <div className="bg-cyan-100 text-cyan-800 text-xs px-2 py-1 rounded-full mb-1">
                            <Shield className="h-3 w-3 inline mr-1" />
                            Visa Friendly
                          </div>
                        )}
                        {job.international_student_friendly && (
                          <div className="bg-cyan-100 text-cyan-800 text-xs px-2 py-1 rounded-full">
                            <GraduationCap className="h-3 w-3 inline mr-1" />
                            Student OK
                          </div>
                        )}
                      </div>
                    </div>

                    <div className="space-y-2 mb-4">
                      <div className="flex items-center text-sm text-gray-600">
                        <Clock className="h-4 w-4 mr-2" />
                        <span>{job.employment_type}</span>
                        <span className="mx-2">•</span>
                        <span>{job.experience_level}</span>
                      </div>
                      
                      {job.salary_min && job.salary_max && (
                        <div className="flex items-center text-sm">
                          <DollarSign className="h-4 w-4 mr-2 text-cyan-600" />
                          <span className="bg-slate-100 text-slate-800 px-2 py-1 rounded text-xs">
                            ${formatSalary(job.salary_min)} - ${formatSalary(job.salary_max)}
                          </span>
                        </div>
                      )}

                      {job.visa_sponsorship && (
                        <div className="flex items-center text-sm text-gray-600">
                          <Star className="h-4 w-4 mr-2" />
                          <span>Visa Confidence: </span>
                          <span className="font-medium ml-1">
                            {Math.round(job.visa_sponsorship_confidence * 100)}%
                          </span>
                        </div>
                      )}
                    </div>

                    <p className="text-gray-700 text-sm mb-4 line-clamp-3">
                      {job.description}
                    </p>

                    <div className="flex justify-between items-center pt-4 border-t border-gray-100">
                      <div className="flex items-center text-xs text-gray-500">
                        <span>{job.source_website}</span>
                      </div>
                      <a
                        href={job.source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        <Button size="sm" icon={<ExternalLink className="h-4 w-4" />}>
                          View Job
                        </Button>
                      </a>
                    </div>
                  </Card>
                </div>
              ))}
            </div>
          )}

          {jobs.length === 0 && !searchLoading && (
            <div className="text-center py-8">
              <Search className="h-12 w-12 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-600">No jobs found matching your criteria.</p>
              <Button onClick={clearFilters} className="mt-4">
                Clear Filters
              </Button>
            </div>
          )}
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex justify-center">
            <nav className="flex items-center space-x-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                disabled={currentPage === 1}
              >
                Previous
              </Button>
              
              {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                const page = i + 1;
                return (
                  <Button
                    key={page}
                    variant={page === currentPage ? 'primary' : 'outline'}
                    size="sm"
                    onClick={() => setCurrentPage(page)}
                  >
                    {page}
                  </Button>
                );
              })}
              
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                disabled={currentPage === totalPages}
              >
                Next
              </Button>
            </nav>
          </div>
        )}
      </div>
    </div>
  );
};

export default DashboardPage;

import React, { useEffect, useState } from 'react';
import { 
  Search,
  Filter,
  MapPin,
  ExternalLink,
  ChevronDown
} from 'lucide-react';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import Card from '../components/ui/Card';
import { Job, JobFilters } from '../types';
import JobCard from '../components/jobs/JobCard';
import apiService from '../services/api';

const JobsPage: React.FC = () => {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [showFilters, setShowFilters] = useState(false);
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  
  const [filters, setFilters] = useState<Partial<JobFilters>>({
    search: '',
    location: '',
    visa_sponsorship: null,
    student_friendly: false,
    category: undefined,
    work_type: undefined,
    remote_friendly: undefined,
    visa_types: undefined,
    industry: undefined,
  });

  useEffect(() => {
    loadJobs();
  }, [filters, currentPage]);

  const loadJobs = async () => {
    setLoading(true);
    try {
      const response = await apiService.getJobs(filters, currentPage, 12);
      setJobs(response.items);
      setTotalPages(response.total_pages);
      if (response.items && response.items.length > 0) {
        setSelectedJob(response.items[0]);
      } else {
        setSelectedJob(null);
      }
    } catch (error) {
      console.error('Failed to load jobs:', error);
      // Mock data for demo
      setJobs([
        {
          id: 1,
          title: 'Frontend Developer',
          company: { id: 1, name: 'Innovation Labs' },
          location: 'Melbourne, VIC',
          description: 'Join our team building next-generation web applications. We welcome international talent and provide visa sponsorship.',
          employment_type: 'Full-time',
          experience_level: 'Mid Level',
          salary_min: 75000,
          salary_max: 95000,
          visa_sponsorship: true,
          visa_sponsorship_confidence: 0.85,
          international_student_friendly: true,
          source_website: 'seek.com.au',
          source_url: 'https://seek.com.au/job/456',
          scraped_at: new Date().toISOString(),
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
        {
          id: 2,
          title: 'Marketing Assistant',
          company: { id: 2, name: 'Digital Marketing Co' },
          location: 'Sydney, NSW',
          description: 'Part-time marketing role perfect for students. Flexible hours and great learning opportunities.',
          employment_type: 'Part-time',
          experience_level: 'Entry Level',
          salary_min: 25,
          salary_max: 35,
          visa_sponsorship: false,
          visa_sponsorship_confidence: 0.1,
          international_student_friendly: true,
          source_website: 'indeed.com.au',
          source_url: 'https://indeed.com.au/job/789',
          scraped_at: new Date().toISOString(),
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
        {
          id: 3,
          title: 'Data Analyst',
          company: { id: 3, name: 'Analytics Plus' },
          location: 'Brisbane, QLD',
          description: 'Analyze data to drive business insights. Graduate program available with potential visa sponsorship.',
          employment_type: 'Full-time',
          experience_level: 'Entry Level',
          salary_min: 65000,
          salary_max: 80000,
          visa_sponsorship: true,
          visa_sponsorship_confidence: 0.7,
          international_student_friendly: false,
          source_website: 'linkedin.com',
          source_url: 'https://linkedin.com/job/101112',
          scraped_at: new Date().toISOString(),
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        }
      ]);
      setTotalPages(5);
      setSelectedJob(null);
    } finally {
      setLoading(false);
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
      category: undefined,
      work_type: undefined,
      remote_friendly: undefined,
      visa_types: undefined,
      industry: undefined,
    });
    setCurrentPage(1);
  };

  const formatSalary = (amount: number) => {
    if (amount < 1000) {
      return `$${amount}/hr`;
    }
    return `$${(amount / 1000).toFixed(0)}k`;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div
          
          
          className="mb-8"
        >
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Find Jobs</h1>
          <p className="text-gray-600">
            Discover visa-friendly and student-friendly opportunities across Australia
          </p>
        </div>

        {/* Search Bar */}
        <Card className="mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <Input
                placeholder="Search for jobs, companies, or keywords..."
                value={filters.search || ''}
                onChange={(e) => handleFilterChange('search', e.target.value)}
                icon={<Search className="h-5 w-5" />}
              />
            </div>
            <div className="flex gap-2">
              <Button
                variant="outline"
                onClick={() => setShowFilters(!showFilters)}
                icon={<Filter className="h-4 w-4" />}
              >
                Filters
                <ChevronDown className={`h-4 w-4 ml-1 transition-transform ${showFilters ? 'rotate-180' : ''}`} />
              </Button>
              <Button onClick={loadJobs} loading={loading}>
                Search
              </Button>
            </div>
          </div>

          {/* Advanced Filters */}
          {showFilters && (
            <div
              
              
              
              className="mt-6 pt-6 border-t border-gray-200"
            >
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Location
                  </label>
                  <select
                    value={filters.location || ''}
                    onChange={(e) => handleFilterChange('location', e.target.value)}
                    className="input-field"
                  >
                    <option value="">All Locations</option>
                    <option value="Sydney">Sydney, NSW</option>
                    <option value="Melbourne">Melbourne, VIC</option>
                    <option value="Brisbane">Brisbane, QLD</option>
                    <option value="Perth">Perth, WA</option>
                    <option value="Adelaide">Adelaide, SA</option>
                    <option value="Canberra">Canberra, ACT</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Visa Sponsorship
                  </label>
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
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Category
                  </label>
                  <select
                    value={filters.category || ''}
                    onChange={(e) => handleFilterChange('category', e.target.value || undefined)}
                    className="input-field"
                  >
                    <option value="">All</option>
                    <option value="casual">Casual</option>
                    <option value="career">Career</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Work Type</label>
                  <select
                    value={filters.work_type || ''}
                    onChange={(e) => handleFilterChange('work_type', e.target.value || undefined)}
                    className="input-field"
                  >
                    <option value="">Any</option>
                    <option value="Full-time">Full-time</option>
                    <option value="Part-time">Part-time</option>
                    <option value="Contract">Contract</option>
                    <option value="Internship">Internship</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Industry</label>
                  <select
                    value={filters.industry || ''}
                    onChange={(e) => handleFilterChange('industry', e.target.value || undefined)}
                    className="input-field"
                  >
                    <option value="">All</option>
                    <option value="Software">Software</option>
                    <option value="Education">Education</option>
                    <option value="Healthcare">Healthcare</option>
                    <option value="Finance">Finance</option>
                    <option value="Retail">Retail</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Salary Range (min/max)</label>
                  <div className="flex gap-2">
                    <input
                      type="number"
                      className="input-field w-full"
                      placeholder="Min"
                      value={(filters.salary_min as number | undefined) ?? ''}
                      onChange={(e) => handleFilterChange('salary_min', e.target.value ? Number(e.target.value) : undefined)}
                    />
                    <input
                      type="number"
                      className="input-field w-full"
                      placeholder="Max"
                      value={(filters.salary_max as number | undefined) ?? ''}
                      onChange={(e) => handleFilterChange('salary_max', e.target.value ? Number(e.target.value) : undefined)}
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Visa Accepted</label>
                  <select
                    multiple
                    value={(filters.visa_types as string[] | undefined) ?? []}
                    onChange={(e) => {
                      const options = Array.from(e.target.selectedOptions).map(o => o.value);
                      handleFilterChange('visa_types', options.length ? options : undefined);
                    }}
                    className="input-field h-24"
                  >
                    <option value="Subclass 482">Subclass 482 (TSS)</option>
                    <option value="Subclass 186">Subclass 186 (ENS)</option>
                    <option value="Subclass 494">Subclass 494 (Regional)</option>
                    <option value="Subclass 485">Subclass 485 (Graduate)</option>
                    <option value="Subclass 500">Subclass 500 (Student)</option>
                  </select>
                </div>
              </div>

              <div className="flex items-center justify-between">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={filters.student_friendly || false}
                    onChange={(e) => handleFilterChange('student_friendly', e.target.checked)}
                    className="rounded border-gray-300 text-cyan-600 focus:ring-cyan-500"
                  />
                  <span className="ml-2 text-sm text-gray-700">Student Friendly Only</span>
                </label>
                
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={!!filters.remote_friendly}
                    onChange={(e) => handleFilterChange('remote_friendly', e.target.checked || undefined)}
                    className="rounded border-gray-300 text-cyan-600 focus:ring-cyan-500"
                  />
                  <span className="ml-2 text-sm text-gray-700">Remote Friendly</span>
                </label>

                <Button variant="ghost" size="sm" onClick={clearFilters}>
                  Clear All Filters
                </Button>
              </div>
            </div>
          )}
        </Card>

        {/* Results Header */}
        <div className="flex justify-between items-center mb-3 md:mb-5">
          <h2 className="text-lg font-semibold text-gray-900">
            {loading ? 'Loading...' : `${jobs.length} Jobs Found`}
          </h2>
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-600">Sort by:</span>
            <select className="text-sm border border-gray-300 rounded px-2 py-1 focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500">
              <option value="latest">Latest</option>
              <option value="salary">Salary</option>
              <option value="relevance">Relevance</option>
              <option value="visa">Visa Confidence</option>
            </select>
          </div>
        </div>

        {/* Jobs Grid - Master/Detail */}
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-600 mx-auto"></div>
            <p className="text-gray-600 mt-4">Finding the best jobs for you...</p>
          </div>
        ) : (
          <>
            <div className="grid grid-cols-1 lg:grid-cols-5 gap-6 mb-10">
              {/* Left: Job list */}
              <div className="lg:col-span-3 space-y-4 max-h-[75vh] overflow-auto pr-1 scroll-smooth">
                {jobs.map((job) => (
                  <JobCard
                    key={job.id}
                    job={job}
                    selected={selectedJob?.id === job.id}
                    onClick={() => setSelectedJob(job)}
                  />
                ))}
              </div>

              {/* Right: Details panel */}
              <div className="lg:col-span-2">
                <Card className="sticky top-6 rounded-xl shadow-sm">
                  {selectedJob ? (
                    <div>
                      <div className="flex items-start justify-between">
                        <div>
                          <h3 className="text-2xl font-semibold text-gray-900">{selectedJob.title}</h3>
                          <div className="text-cyan-700 font-medium text-sm md:text-base">{selectedJob.company.name}</div>
                          <div className="mt-1 text-sm text-gray-600 flex items-center">
                            <MapPin className="h-4 w-4 mr-1" /> {selectedJob.location}
                          </div>
                        </div>
                      </div>

                      <div className="mt-4 flex flex-wrap gap-2">
                        {selectedJob.visa_sponsorship && (
                          <span className="inline-flex items-center gap-1 rounded-full bg-cyan-100 text-cyan-700 px-2 py-0.5 text-xs">
                            Visa Friendly
                          </span>
                        )}
                        {selectedJob.international_student_friendly && (
                          <span className="inline-flex items-center gap-1 rounded-full bg-cyan-100 text-cyan-700 px-2 py-0.5 text-xs">
                            Student OK
                          </span>
                        )}
                        {selectedJob.salary_min && selectedJob.salary_max && (
                          <span className="inline-flex items-center gap-1 rounded-full bg-slate-100 text-slate-700 px-2 py-0.5 text-xs">
                            {formatSalary(selectedJob.salary_min)} - {formatSalary(selectedJob.salary_max)}
                          </span>
                        )}
                      </div>

                      <div className="mt-6 border-t border-gray-100 pt-5">
                        <div className="text-[15px] md:text-[16px] leading-relaxed text-gray-800 whitespace-pre-line">
                          {selectedJob.description}
                        </div>
                      </div>

                      <div className="mt-6 flex gap-2">
                        <a href={selectedJob.source_url} target="_blank" rel="noopener noreferrer">
                          <Button icon={<ExternalLink className="h-4 w-4" />}>Apply</Button>
                        </a>
                        <Button variant="outline">Save</Button>
                      </div>
                    </div>
                  ) : (
                    <div className="text-gray-600">Select a job to see details</div>
                  )}
                </Card>
              </div>
            </div>

            {jobs.length === 0 && (
              <div className="text-center py-12">
                <Search className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No jobs found</h3>
                <p className="text-gray-600 mb-4">
                  Try adjusting your search criteria or clearing filters
                </p>
                <Button onClick={clearFilters}>Clear All Filters</Button>
              </div>
            )}

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
          </>
        )}
      </div>
    </div>
  );
};

export default JobsPage;

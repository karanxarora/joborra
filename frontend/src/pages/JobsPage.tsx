import React, { useEffect, useState } from 'react';
import { 
  Search,
  MapPin,
  ExternalLink,
  Bookmark,
} from 'lucide-react';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import Card from '../components/ui/Card';
import { Job, JobFilters } from '../types';
import JobCard from '../components/jobs/JobCard';
import apiService from '../services/api';
import { useFavorites } from '../contexts/FavoritesContext';
import { useToast } from '../contexts/ToastContext';

const JobsPage: React.FC = () => {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  // UI state simplified to match example screenshot
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const { map: favoritesMap, add: addFavorite, remove: removeFavorite } = useFavorites();
  const { toast } = useToast();
  const [saving, setSaving] = useState<Record<number, boolean>>({});
  
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

  // Location autocomplete state
  const [locationInput, setLocationInput] = useState<string>('');
  const [locSuggestions, setLocSuggestions] = useState<string[]>([]);
  const [locLoading, setLocLoading] = useState<boolean>(false);
  const [showLocDropdown, setShowLocDropdown] = useState<boolean>(false);

  // Keep input in sync if filters reset
  useEffect(() => {
    setLocationInput(String(filters.location || ''));
  }, [filters.location]);

  useEffect(() => {
    loadJobs();
  }, [filters, currentPage]);

  // favorites are preloaded by FavoritesProvider

  // Debounced fetch for location suggestions
  useEffect(() => {
    const q = locationInput?.trim() || '';
    if (!q) {
      setLocSuggestions([]);
      return;
    }
    setLocLoading(true);
    const t = setTimeout(async () => {
      try {
        const items = await apiService.getLocationSuggestions(q, 8);
        setLocSuggestions(items);
      } catch (e) {
        setLocSuggestions([]);
      } finally {
        setLocLoading(false);
      }
    }, 250);
    return () => clearTimeout(t);
  }, [locationInput]);

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

  const isSaved = (jobId: number) => !!favoritesMap[jobId];

  const toggleSave = async (job: Job) => {
    const existing = favoritesMap[job.id];
    setSaving((prev) => ({ ...prev, [job.id]: true }));
    try {
      if (existing) {
        const ok = await removeFavorite(existing);
        if (ok) toast('Removed from Saved', 'success'); else toast('Failed to remove', 'error');
      } else {
        const id = await addFavorite(job.id);
        if (id) toast('Saved job', 'success'); else toast('Failed to save', 'error');
      }
    } finally {
      setSaving((prev) => ({ ...prev, [job.id]: false }));
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
    <div className="min-h-screen bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-6 text-center">
          <h1 className="text-2xl md:text-3xl font-bold text-slate-900">Find Your Next Job</h1>
          <p className="text-slate-600 mt-1">Verified jobs welcoming international students</p>
        </div>

        {/* Search Row */}
        <Card className="mb-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div>
              <label className="block text-xs font-medium text-slate-600 mb-1">What</label>
              <Input
                placeholder="Job title, keywords, or company"
                value={filters.search || ''}
                onChange={(e) => handleFilterChange('search', e.target.value)}
                icon={<Search className="h-4 w-4" />}
              />
            </div>
            <div className="relative">
              <label className="block text-xs font-medium text-slate-600 mb-1">Where</label>
              <input
                className="input-field w-full"
                placeholder="Suburb, city, or region"
                value={locationInput}
                onChange={(e) => {
                  const v = e.target.value;
                  setLocationInput(v);
                  handleFilterChange('location', v);
                }}
                onFocus={() => setShowLocDropdown(true)}
              />
              {showLocDropdown && (locLoading || locSuggestions.length > 0) && (
                <div className="absolute z-20 mt-1 w-full rounded-md border bg-white shadow-lg max-h-64 overflow-auto thin-scrollbar">
                  {locLoading && (
                    <div className="px-3 py-2 text-sm text-slate-500">Searching…</div>
                  )}
                  {!locLoading && locSuggestions.map((s) => (
                    <button
                      key={s}
                      type="button"
                      className="w-full text-left px-3 py-2 text-sm hover:bg-slate-50"
                      onMouseDown={(e) => {
                        // use mousedown to prevent input blur before click
                        e.preventDefault();
                        setLocationInput(s);
                        handleFilterChange('location', s);
                        setShowLocDropdown(false);
                      }}
                    >
                      {s}
                    </button>
                  ))}
                  {!locLoading && locSuggestions.length === 0 && locationInput && (
                    <div className="px-3 py-2 text-sm text-slate-500">No matches</div>
                  )}
                </div>
              )}
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-600 mb-1">Job Category</label>
              <select
                className="input-field w-full"
                value={filters.category || ''}
                onChange={(e) => handleFilterChange('category', e.target.value || undefined)}
              >
                <option value="">All Categories</option>
                <option value="Software">Software</option>
                <option value="Design">Design</option>
                <option value="Marketing">Marketing</option>
                <option value="Sales">Sales</option>
              </select>
            </div>
          </div>
          <div className="mt-3 flex justify-center">
            <Button onClick={loadJobs} loading={loading}>Search</Button>
          </div>
        </Card>

        {/* Filter Pills Row */}
        <div className="flex flex-wrap gap-2 mb-6">
          <div>
            <select
              className="px-3 py-2 rounded-md border text-sm text-slate-700"
              value={filters.work_type || ''}
              onChange={(e) => handleFilterChange('work_type', e.target.value || undefined)}
            >
              <option value="">Work Type</option>
              <option value="Full-time">Full-time</option>
              <option value="Part-time">Part-time</option>
              <option value="Contract">Contract</option>
              <option value="Internship">Internship</option>
            </select>
          </div>
          <div>
            <select
              className="px-3 py-2 rounded-md border text-sm text-slate-700"
              value={filters.visa_types && (filters.visa_types as string[])[0] || ''}
              onChange={(e) => handleFilterChange('visa_types', e.target.value ? [e.target.value] : undefined)}
            >
              <option value="">Visa Accepted</option>
              <option value="Subclass 500">Subclass 500 (Student)</option>
              <option value="Subclass 485">Subclass 485 (Graduate)</option>
              <option value="Subclass 482">Subclass 482 (TSS)</option>
            </select>
          </div>
          <div>
            <select
              className="px-3 py-2 rounded-md border text-sm text-slate-700"
              value={String(!!filters.remote_friendly)}
              onChange={(e) => handleFilterChange('remote_friendly', e.target.value === 'true' ? true : undefined)}
            >
              <option value="false">Remote Friendly</option>
              <option value="true">Remote Friendly</option>
            </select>
          </div>
          <div>
            <select
              className="px-3 py-2 rounded-md border text-sm text-slate-700"
              value={(filters.salary_min as number | undefined) ? 'custom' : ''}
              onChange={(e) => {
                if (e.target.value === 'custom') {
                  handleFilterChange('salary_min', 60000);
                  handleFilterChange('salary_max', 120000);
                } else {
                  handleFilterChange('salary_min', undefined);
                  handleFilterChange('salary_max', undefined);
                }
              }}
            >
              <option value="">Salary</option>
              <option value="custom">$60k - $120k</option>
            </select>
          </div>
        </div>

        {/* Results Header */}
        <div className="mb-2 text-slate-700 text-sm">{loading ? 'Loading…' : `${jobs.length} Jobs Found`}</div>

        {/* Jobs Grid - Master/Detail */}
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-600 mx-auto"></div>
            <p className="text-gray-600 mt-4">Finding the best jobs for you...</p>
          </div>
        ) : (
          <>
            <div className="grid grid-cols-1 lg:grid-cols-5 gap-6 mb-10">
              {/* Left: Job list (narrower) */}
              <div className="lg:col-span-2 space-y-4 max-h-[75vh] overflow-auto pr-1 scroll-smooth thin-scrollbar">
                {jobs.map((job) => (
                  <JobCard
                    key={job.id}
                    job={job}
                    selected={selectedJob?.id === job.id}
                    onClick={() => setSelectedJob(job)}
                    isSaved={isSaved(job.id)}
                    onToggleSave={() => toggleSave(job)}
                    saving={!!saving[job.id]}
                  />
                ))}
              </div>

              {/* Right: Details panel (wider) */}
              <div className="lg:col-span-3">
                <Card className="sticky top-6 rounded-xl shadow-sm" padding="sm">
                  {selectedJob ? (
                    <div>
                      {/* Header */}
                      <div className="flex items-start justify-between">
                        <div className="space-y-1">
                          <h3 className="text-[22px] md:text-2xl font-semibold text-slate-900">{selectedJob.title}</h3>
                          <div className="text-slate-600 font-medium text-sm md:text-[15px]">{selectedJob.company.name}</div>
                          <div className="mt-1 text-sm text-slate-600 flex items-center">
                            <MapPin className="h-4 w-4 mr-1" /> {selectedJob.location}
                          </div>
                        </div>
                      </div>

                      {/* Meta chips row */}
                      <div className="mt-3 flex flex-wrap items-center gap-2">
                        {selectedJob.employment_type && (
                          <span className="inline-flex items-center rounded-full border border-slate-200 bg-white text-slate-700 px-2.5 py-0.5 text-xs">
                            {selectedJob.employment_type}
                          </span>
                        )}
                        {selectedJob.source_website && (
                          <span className="inline-flex items-center rounded-full border border-slate-200 bg-white text-slate-700 px-2.5 py-0.5 text-xs">
                            {selectedJob.source_website}
                          </span>
                        )}
                        {(selectedJob.created_at || selectedJob.scraped_at) && (
                          <span className="inline-flex items-center rounded-full border border-slate-200 bg-white text-slate-700 px-2.5 py-0.5 text-xs">
                            {new Date(selectedJob.created_at || selectedJob.scraped_at).toLocaleDateString()}
                          </span>
                        )}
                        {selectedJob.salary_min && selectedJob.salary_max && (
                          <span className="inline-flex items-center rounded-full bg-slate-100 text-slate-700 px-2.5 py-0.5 text-xs">
                            {formatSalary(selectedJob.salary_min)} - {formatSalary(selectedJob.salary_max)}
                          </span>
                        )}
                      </div>

                      {/* Badges */}
                      <div className="mt-3 flex flex-wrap gap-2">
                        {selectedJob.visa_sponsorship && (
                          <span className="inline-flex items-center rounded-full bg-cyan-100 text-cyan-700 px-2.5 py-0.5 text-xs">
                            Visa Friendly
                          </span>
                        )}
                        {selectedJob.international_student_friendly && (
                          <span className="inline-flex items-center rounded-full bg-cyan-100 text-cyan-700 px-2.5 py-0.5 text-xs">
                            Student OK
                          </span>
                        )}
                      </div>

                      {/* Actions */}
                      <div className="mt-5 flex gap-2">
                        <a href={selectedJob.source_url} target="_blank" rel="noopener noreferrer">
                          <Button icon={<ExternalLink className="h-4 w-4" />}>Apply</Button>
                        </a>
                        <Button variant="outline" onClick={() => toggleSave(selectedJob)} disabled={!!saving[selectedJob.id]} aria-busy={!!saving[selectedJob.id]}>
                          <Bookmark
                            className={
                              isSaved(selectedJob.id)
                                ? 'h-4 w-4 mr-1 text-cyan-600 fill-current'
                                : 'h-4 w-4 mr-1 text-slate-600'
                            }
                          />
                          <span className="hidden sm:inline">{isSaved(selectedJob.id) ? 'Saved' : 'Save'}</span>
                        </Button>
                      </div>

                      {/* Description */}
                      <div className="mt-5 border-t border-slate-200 pt-5">
                        <div className="text-[15px] md:text-[16px] leading-7 text-slate-800 whitespace-pre-line">
                          {selectedJob.description}
                        </div>
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

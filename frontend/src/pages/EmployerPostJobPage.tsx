import React, { useEffect, useMemo, useRef, useState, useCallback } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import { EmployerJobCreate, JobDraftCreate } from '../types';
import apiService from '../services/api';
import Button from '../components/ui/Button';
import Card from '../components/ui/Card';
import Input from '../components/ui/Input';
import Select, { SelectOption } from '../components/ui/Select';
import LocationInput, { LocationData } from '../components/ui/LocationInput';
import { useToast } from '../contexts/ToastContext';
import { extractErrorMessage } from '../utils/errorUtils';
import { useAuth } from '../contexts/AuthContext';
import { MapPin, Clock, DollarSign, ShieldCheck, GraduationCap, Building2 } from 'lucide-react';

const EmployerPostJobPage: React.FC = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const { user } = useAuth();
  const [searchParams] = useSearchParams();

  const [form, setForm] = useState<EmployerJobCreate>({
    title: '',
    description: '',
    location: '',
    city: '',
    state: '',
    employment_type: '',
    job_type: '',
    role_category: '',
    salary: '',
    salary_min: undefined,
    salary_max: undefined,
    salary_currency: 'AUD',
    experience_level: '',
    remote_option: false,
    visa_sponsorship: false,
    visa_types: [] as string[],
    international_student_friendly: false,
    required_skills: [],
    preferred_skills: [],
    education_requirements: '',
    expires_at: undefined,
  });

  const [skillsInput, setSkillsInput] = useState('');
  const [preferredSkillsInput, setPreferredSkillsInput] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loadingDraft, setLoadingDraft] = useState(false);
  const [loadingJob, setLoadingJob] = useState(false);
  const [success, setSuccess] = useState<string | null>(null);
  const [step, setStep] = useState(0); // 0..4
  const [isEditing, setIsEditing] = useState(false);
  const [editingJobId, setEditingJobId] = useState<number | null>(null);

  // Role category options
  const roleCategoryOptions: SelectOption[] = [
    {
      value: 'SERVICE_RETAIL_HOSPITALITY',
      label: 'Service, Retail & Hospitality (open to any degree)',
      hint: 'Customer-facing or operations roles — e.g., café, restaurant, petrol station, supermarket, retail, delivery, call centre, hospitality.'
    },
    {
      value: 'STUDY_ALIGNED_PROFESSIONAL',
      label: 'Study-aligned / Professional (field-specific)',
      hint: 'Roles aligned to a discipline — e.g., engineering, nursing, IT, accounting, education, lab roles.'
    }
  ];

  // Employment basis options
  const employmentBasisOptions: SelectOption[] = [
    { value: 'CASUAL', label: 'Casual' },
    { value: 'PART_TIME', label: 'Part-time' },
    { value: 'FULL_TIME', label: 'Full-time' },
    { value: 'FIXED_TERM', label: 'Fixed-term' }
  ];

  // Address autocomplete - removed unused variables

  // Textarea ref for description
  const descRef = useRef<HTMLTextAreaElement | null>(null);

  // Visa types with descriptions (matching student sign-up options)
  const VISA_TYPES: Array<{ value: string; label: string; description: string }> = useMemo(() => ([
    { value: '', label: 'Select visa type (optional)', description: '' },
    { value: 'Student Visa (subclass 500)', label: 'Student Visa (subclass 500)', description: 'International student visa for studying in Australia.' },
    { value: 'Temporary Graduate (subclass 485)', label: 'Temporary Graduate (subclass 485)', description: 'Post-study work visa for recent graduates.' },
    { value: 'Skilled Independent (subclass 189)', label: 'Skilled Independent (subclass 189)', description: 'Permanent visa for skilled workers without sponsorship.' },
    { value: 'Skilled Nominated (subclass 190)', label: 'Skilled Nominated (subclass 190)', description: 'Permanent visa for skilled workers nominated by a state.' },
    { value: 'Skilled Work Regional (subclass 491)', label: 'Skilled Work Regional (subclass 491)', description: 'Regional skilled work visa.' },
    { value: 'Employer Sponsored TSS (subclass 482)', label: 'Employer Sponsored TSS (subclass 482)', description: 'Temporary Skill Shortage visa (employer-sponsored).' },
    { value: 'Employer Nomination (subclass 186)', label: 'Employer Nomination (subclass 186)', description: 'Employer Nomination Scheme (permanent).' },
    { value: 'Working Holiday (subclass 417/462)', label: 'Working Holiday (subclass 417/462)', description: 'Working holiday visa for young people.' },
    { value: 'Other/Not Sure', label: 'Other/Not Sure', description: 'Other visa type or not sure of visa status.' },
  ]), []);

  const loadDraftData = useCallback(async (draftId: number) => {
    try {
      setLoadingDraft(true);
      const draft = await apiService.getJobDraft(draftId);
      if (draft) {
        // Populate form with draft data
        setForm({
          title: draft.title || '',
          description: draft.description || '',
          location: draft.location || '',
          city: draft.city || '',
          state: draft.state || '',
          employment_type: draft.employment_type || '',
          job_type: draft.job_type || '',
          role_category: draft.role_category || '',
          salary: draft.salary || '',
          salary_min: draft.salary_min,
          salary_max: draft.salary_max,
          salary_currency: draft.salary_currency || 'AUD',
          experience_level: draft.experience_level || '',
          remote_option: draft.remote_option || false,
          visa_sponsorship: draft.visa_sponsorship || false,
          visa_types: Array.isArray(draft.visa_types) ? draft.visa_types : [],
          international_student_friendly: draft.international_student_friendly || false,
          required_skills: draft.required_skills || [],
          preferred_skills: draft.preferred_skills || [],
          education_requirements: draft.education_requirements || '',
          expires_at: draft.expires_at,
        });
        
        // Set the step to where the user left off
        setStep(draft.step || 0);
        
        // Update description in rich text editor if present
        if (draft.description && descRef.current) {
          descRef.current.innerHTML = draft.description;
        }
        
        toast('Draft loaded successfully!', 'success');
      }
    } catch (error) {
      console.error('Failed to load draft:', error);
      toast('Failed to load draft data', 'error');
    } finally {
      setLoadingDraft(false);
    }
  }, [toast]);

  const loadJobData = useCallback(async (jobId: number) => {
    try {
      setLoadingJob(true);
      const job = await apiService.getJobById(jobId);
      if (job) {
        // Populate form with job data
        setForm({
          title: job.title || '',
          description: job.description || '',
          location: job.location || '',
          city: job.city || '',
          state: job.state || '',
          employment_type: job.employment_type || '',
          job_type: job.job_type || '',
          role_category: (job as any).role_category || '',
          salary: job.salary || '',
          salary_min: job.salary_min,
          salary_max: job.salary_max,
          salary_currency: job.salary_currency || 'AUD',
          experience_level: job.experience_level || '',
          remote_option: job.remote_option || false,
          visa_sponsorship: job.visa_sponsorship || false,
          visa_types: Array.isArray(job.visa_types) ? job.visa_types : [],
          international_student_friendly: job.international_student_friendly || false,
          required_skills: job.required_skills || [],
          preferred_skills: job.preferred_skills || [],
          education_requirements: job.education_requirements || '',
          expires_at: job.expires_at,
        });
        
        // Set skills inputs for display
        setSkillsInput(job.required_skills ? job.required_skills.join(', ') : '');
        setPreferredSkillsInput(job.preferred_skills ? job.preferred_skills.join(', ') : '');
        
        // Update description in textarea if present
        if (job.description && descRef.current) {
          descRef.current.value = job.description;
        }
        
        setIsEditing(true);
        setEditingJobId(jobId);
        
        // If job has no visa types, advance to step 3 (visa types step)
        // Parse visa_types to check if it's empty (job.visa_types comes as JSON string from backend)
        let parsedVisaTypes = [];
        if (Array.isArray(job.visa_types)) {
          parsedVisaTypes = job.visa_types;
        } else if (typeof job.visa_types === 'string' && job.visa_types.trim()) {
          try {
            parsedVisaTypes = JSON.parse(job.visa_types);
          } catch (e) {
            console.warn('Failed to parse visa_types:', e);
            parsedVisaTypes = [];
          }
        }
        
        if (parsedVisaTypes.length === 0) {
          setStep(3);
          toast('Job data loaded! Please select at least one visa type.', 'info');
        } else {
          toast('Job data loaded successfully!', 'success');
        }
      }
    } catch (error) {
      console.error('Failed to load job:', error);
      toast('Failed to load job data', 'error');
    } finally {
      setLoadingJob(false);
    }
  }, [toast]);

  // Load draft data if draft parameter is present in URL
  useEffect(() => {
    const draftId = searchParams.get('draft');
    const editId = searchParams.get('edit');
    
    if (draftId) {
      loadDraftData(parseInt(draftId));
    } else if (editId) {
      loadJobData(parseInt(editId));
    }
  }, [searchParams, loadDraftData, loadJobData]);



  const saveDraft = async () => {
    try {
      setSubmitting(true);
      setError(null);
      setSuccess(null);

      // Basic validation for draft
      if (!form.title || form.title.trim().length < 3) {
        setError('Title must be at least 3 characters to save as draft.');
        setSubmitting(false);
        return;
      }
      
      // Only validate visa types if user has reached step 3 (where visa types are visible)
      if (step >= 3 && (!form.visa_types || !Array.isArray(form.visa_types) || form.visa_types.length === 0)) {
        setError('Please select at least one visa type.');
        setSubmitting(false);
        return;
      }
      
      if (!form.employment_type) {
        setError('Please select an employment basis.');
        setSubmitting(false);
        return;
      }

      const draftData: JobDraftCreate = {
        title: form.title,
        description: form.description || undefined,
        location: form.location || undefined,
        city: form.city || undefined,
        state: form.state || undefined,
        salary_min: form.salary_min,
        salary_max: form.salary_max,
        salary_currency: form.salary_currency,
        salary: form.salary || undefined,
        employment_type: form.employment_type,
        job_type: form.job_type || undefined,
        role_category: form.role_category || undefined,
        experience_level: form.experience_level,
        remote_option: form.remote_option,
        visa_sponsorship: form.visa_sponsorship,
        visa_types: (form.visa_types && Array.isArray(form.visa_types) && form.visa_types.length > 0) ? form.visa_types : undefined,
        international_student_friendly: form.international_student_friendly,
        required_skills: form.required_skills,
        preferred_skills: form.preferred_skills,
        education_requirements: form.education_requirements || undefined,
        expires_at: form.expires_at,
        step: step
      };

      const draftId = searchParams.get('draft');
      if (draftId) {
        // Update existing draft
        await apiService.updateJobDraft(parseInt(draftId), draftData);
        toast('Draft updated successfully!', 'success');
      } else {
        // Create new draft
        await apiService.createJobDraft(draftData);
        toast('Draft saved successfully!', 'success');
      }
      
      // Navigate to drafts page after a short delay
      setTimeout(() => {
        navigate('/employer/drafts');
      }, 1500);
      
    } catch (error: any) {
      console.error('Failed to save draft:', error);
      const errorMessage = error.response?.data?.detail || 'Failed to save draft';
      setError(errorMessage);
      toast(errorMessage, 'error');
    } finally {
      setSubmitting(false);
    }
  };

  const steps = useMemo(() => [
    'Basics',
    'Requirements',
    'Compensation',
    'Accepted Visas',
    'Review & Publish'
  ], []);

  const handleChange = (key: keyof EmployerJobCreate, value: any) => {
    setForm(prev => ({ ...prev, [key]: value }));
  };

  const handleLocationSelect = (locationData: LocationData) => {
    setForm(prev => ({
      ...prev,
      location: locationData.location,
      city: locationData.city,
      state: locationData.state
    }));
  };

  const addSkill = () => {
    const value = skillsInput.trim();
    if (!value) return;
    handleChange('required_skills', [ ...(form.required_skills || []), value ]);
    setSkillsInput('');
  };

  const addPreferredSkill = () => {
    const value = preferredSkillsInput.trim();
    if (!value) return;
    handleChange('preferred_skills', [ ...(form.preferred_skills || []), value ]);
    setPreferredSkillsInput('');
  };

  const removeSkill = (idx: number) => {
    const next = (form.required_skills || []).filter((_, i) => i !== idx);
    handleChange('required_skills', next);
  };

  const removePreferredSkill = (idx: number) => {
    const next = (form.preferred_skills || []).filter((_, i) => i !== idx);
    handleChange('preferred_skills', next);
  };

  const onSubmit = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setSubmitting(true);
    setError(null);
    setSuccess(null);

    try {
      // Final validation
      if (!form.title || form.title.trim().length < 5) {
        setError('Title must be at least 5 characters.');
        setSubmitting(false);
        return;
      }
      
      // Validate visa types - all jobs must have at least one visa type selected
      if (step >= 3 && (!form.visa_types || !Array.isArray(form.visa_types) || form.visa_types.length === 0)) {
        setError('Please select at least one visa type.');
        setSubmitting(false);
        return;
      }
      
      if (!form.employment_type) {
        setError('Please select an employment basis.');
        setSubmitting(false);
        return;
      }
      
      if (!form.description || form.description.trim().length < 20) {
        setError('Description must be at least 20 characters.');
        setSubmitting(false);
        return;
      }
      if (!form.role_category) {
        setError('Role category is required.');
        setSubmitting(false);
        return;
      }

      const jobData = {
        ...form,
        // Normalize empty strings to undefined for optional fields
        job_type: form.job_type || undefined,
        salary: form.salary || undefined,
        visa_types: (form.visa_types && Array.isArray(form.visa_types) && form.visa_types.length > 0) ? form.visa_types : undefined,
        education_requirements: form.education_requirements || undefined,
        city: form.city || undefined,
        state: form.state || undefined,
        location: form.location || undefined,
        experience_level: form.experience_level || undefined,
      };

      let result;
      if (isEditing && editingJobId) {
        // Update existing job
        result = await apiService.updateEmployerJob(editingJobId, jobData);
        toast('Job updated successfully!', 'success');
        setSuccess('Job updated successfully. Redirecting to dashboard…');
        // Redirect to employer dashboard after short delay
        setTimeout(() => navigate('/employer/dashboard'), 900);
      } else {
        // Create new job
        result = await apiService.createEmployerJob(jobData);
        toast('Job posted successfully!', 'success');
        setSuccess('Job posted successfully. Redirecting to dashboard…');
        // Redirect employer to their dashboard after short delay
        setTimeout(() => navigate('/employer/dashboard'), 900);
      }

      if (file) {
        try {
          await apiService.uploadJobDocument(result.id, file);
        } catch (uploadErr: any) {
          // Non-fatal, job is created/updated
          console.error('Document upload failed', uploadErr);
        }
      }
    } catch (err: any) {
      const action = isEditing ? 'update' : 'create';
      const msg = err?.response?.data?.detail || err?.message || `Failed to ${action} job`;
      setError(msg);
    } finally {
      setSubmitting(false);
    }
  };

  const canProceedFromStep = (s: number): string | null => {
    if (s === 0) {
      if (!form.title || form.title.trim().length < 5) return 'Title must be at least 5 characters.';
      return null;
    }
    if (s === 1) {
      if (!form.description || form.description.trim().length < 20) return 'Description must be at least 20 characters.';
      return null;
    }
    return null;
  };

  const next = () => {
    const msg = canProceedFromStep(step);
    if (msg) { setError(msg); return; }
    setError(null);
    setStep((v) => Math.min(steps.length - 1, v + 1));
  };

  const back = () => {
    setError(null);
    setStep((v) => Math.max(0, v - 1));
  };

  // Helper functions for display labels
  const getRoleCategoryLabel = (value: string) => {
    const option = roleCategoryOptions.find(opt => opt.value === value);
    return option ? option.label : value;
  };

  const getEmploymentBasisLabel = (value: string) => {
    const option = employmentBasisOptions.find(opt => opt.value === value);
    return option ? option.label : value;
  };

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {loadingDraft && (
        <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-center">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-3"></div>
            <span className="text-blue-700">Loading draft...</span>
          </div>
        </div>
      )}
      {loadingJob && (
        <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg">
          <div className="flex items-center">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-green-600 mr-3"></div>
            <span className="text-green-700">Loading job data...</span>
          </div>
        </div>
      )}
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl md:text-3xl font-bold text-slate-900">
          {isEditing ? 'Edit Job' : 'Post a Job'}
        </h1>
        <Link to="/employer/company" className="text-sm text-primary-700 hover:underline">Update company info</Link>
      </div>

      {/* Stepper */}
      <div className="mb-6">
        <div className="flex items-center">
          {steps.map((label, i) => (
            <React.Fragment key={label}>
              <div className="flex items-center">
                <div className={`h-8 w-8 rounded-full flex items-center justify-center text-sm font-semibold border ${i <= step ? 'bg-primary-100 border-primary-300' : 'bg-white border-slate-300'}`}>{i+1}</div>
                <div className="hidden sm:block text-sm font-medium ml-2">{label}</div>
              </div>
              {i < steps.length - 1 && (
                <div className={`flex-1 h-px mx-4 ${i < step ? 'bg-primary-300' : 'bg-slate-200'}`} />
              )}
            </React.Fragment>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className={step === 4 ? "lg:col-span-12" : "lg:col-span-8"}>
          <Card>
            <form onSubmit={(e)=>{e.preventDefault();}} className="space-y-6 p-6">
              {error && (
                <div className="p-3 rounded border border-amber-300 bg-amber-50 text-amber-900 text-sm">{extractErrorMessage(error)}</div>
              )}

              {/* Step content */}
              {step === 0 && (
                <>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <Input
                      label="Job Title"
                      value={form.title}
                      onChange={(e) => handleChange('title', e.target.value)}
                      required
                    />
                    <Select
                      label="Role category"
                      value={form.role_category || ''}
                      onChange={(value) => handleChange('role_category', value)}
                      options={roleCategoryOptions}
                      placeholder="Select role category"
                      required
                      helperText="Both categories are equally valued on Joborra. Choose the one that best matches the nature of this role so students can find it faster."
                    />
                    <Select
                      label="Employment basis"
                      value={form.employment_type || ''}
                      onChange={(value) => handleChange('employment_type', value)}
                      options={employmentBasisOptions}
                      placeholder="Select employment basis"
                      required
                    />
                    <Input
                      label="Experience Level"
                      placeholder="e.g., entry/mid/senior"
                      value={form.experience_level || ''}
                      onChange={(e) => handleChange('experience_level', e.target.value)}
                    />
                    <LocationInput
                      label="Location"
                      value={form.location || ''}
                      onChange={(value) => handleChange('location', value)}
                      onLocationSelect={handleLocationSelect}
                      placeholder="e.g., Sydney, NSW"
                    />
                    <div className="grid grid-cols-2 gap-4">
                      <Input label="City" value={form.city || ''} onChange={(e) => handleChange('city', e.target.value)} />
                      <Input label="State" value={form.state || ''} onChange={(e) => handleChange('state', e.target.value)} />
                    </div>
                  </div>
                </>
              )}

              {step === 1 && (
                <>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                    {/* Job description textarea */}
                    <div className="flex items-center gap-2 mb-2">
                      <Button
                        type="button"
                        className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white border-0 shadow-md hover:shadow-lg transition-all duration-200 font-medium"
                        onClick={async () => {
                          try {
                            const draft = await apiService.generateJobDescription({ 
                              title: form.title, 
                              skills: form.required_skills || [],
                              role_category: form.role_category,
                              employment_type: form.employment_type,
                              location: form.location || form.city || form.state,
                              context: {
                                company_name: user?.company_name || 'Our Company',
                                visa_sponsorship: form.visa_sponsorship,
                                international_student_friendly: form.international_student_friendly
                              }
                            });
                            handleChange('description', draft);
                            toast('Job description generated successfully!', 'success');
                          } catch (error) {
                            console.error('AI generation failed:', error);
                            toast('AI generation failed. Please try again or write the description manually.', 'error');
                          }
                        }}
                      >
                        ✨ AI Auto Generate
                      </Button>
                    </div>
                    <textarea
                      ref={descRef}
                      className="w-full rounded-md border border-gray-300 p-2 min-h-[200px] focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-vertical"
                      value={form.description || ''}
                      onChange={(e) => handleChange('description', e.target.value)}
                      placeholder="Enter job description..."
                      style={{
                        lineHeight: '1.6',
                        fontSize: '14px',
                        direction: 'ltr',
                        textAlign: 'left',
                        fontFamily: 'inherit'
                      }}
                      dir="ltr"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Required Skills</label>
                    <div className="flex gap-2">
                      <Input value={skillsInput} onChange={(e) => setSkillsInput(e.target.value)} placeholder="Add a skill" />
                      <Button type="button" onClick={addSkill}>Add</Button>
                    </div>
                    <div className="flex flex-wrap gap-2 mt-2">
                      {(form.required_skills || []).map((s, i) => (
                        <span key={i} className="px-2 py-1 bg-slate-100 rounded text-sm">
                          {s}
                          <button type="button" onClick={() => removeSkill(i)} className="ml-2 text-red-500">×</button>
                        </span>
                      ))}
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Preferred Skills</label>
                    <div className="flex gap-2">
                      <Input value={preferredSkillsInput} onChange={(e) => setPreferredSkillsInput(e.target.value)} placeholder="Add a preferred skill" />
                      <Button type="button" onClick={addPreferredSkill}>Add</Button>
                    </div>
                    <div className="flex flex-wrap gap-2 mt-2">
                      {(form.preferred_skills || []).map((s, i) => (
                        <span key={i} className="px-2 py-1 bg-slate-100 rounded text-sm">
                          {s}
                          <button type="button" onClick={() => removePreferredSkill(i)} className="ml-2 text-red-500">×</button>
                        </span>
                      ))}
                    </div>
                  </div>
                </>
              )}

              {step === 2 && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <Input
                    label="Salary (text) — optional"
                    placeholder="e.g., $90k-$120k + super"
                    value={form.salary || ''}
                    onChange={(e) => handleChange('salary', e.target.value)}
                  />
                  <Input
                    label="Salary Min — optional"
                    type="number"
                    value={form.salary_min === undefined ? '' : form.salary_min}
                    onChange={(e) => handleChange('salary_min', e.target.value ? Number(e.target.value) : undefined)}
                  />
                  <Input
                    label="Salary Max — optional"
                    type="number"
                    value={form.salary_max === undefined ? '' : form.salary_max}
                    onChange={(e) => handleChange('salary_max', e.target.value ? Number(e.target.value) : undefined)}
                  />
                </div>
              )}

              {step === 3 && (
                <>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Visa Sponsorship</label>
                      <select
                        className="w-full rounded-md border border-gray-300 p-2 focus:ring-cyan-500 focus:border-cyan-500"
                        value={String(!!form.visa_sponsorship)}
                        onChange={(e) => handleChange('visa_sponsorship', e.target.value === 'true')}
                      >
                        <option value="false">No</option>
                        <option value="true">Yes</option>
                      </select>
                    </div>

                    <div className="md:col-span-2">
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Visa Types <span className="text-red-500">*</span>
                      </label>
                      <div className="space-y-2">
                        {VISA_TYPES.filter(v => v.value !== '').map(v => (
                          <label key={v.value} className="flex items-center space-x-2">
                            <input
                              type="checkbox"
                              className="rounded border-gray-300 text-cyan-600 focus:ring-cyan-500"
                              checked={form.visa_types?.includes(v.value) || false}
                              onChange={(e) => {
                                if (e.target.checked) {
                                  handleChange('visa_types', [...(form.visa_types || []), v.value]);
                                } else {
                                  handleChange('visa_types', (form.visa_types || []).filter(vt => vt !== v.value));
                                }
                              }}
                            />
                            <span className="text-sm text-gray-700">{v.label}</span>
                          </label>
                        ))}
                      </div>
                      {form.visa_types && Array.isArray(form.visa_types) && form.visa_types.length > 0 && (
                        <p className="mt-2 text-xs text-gray-500">
                          Selected: {form.visa_types.join(', ')}
                        </p>
                      )}
                      {(!form.visa_types || !Array.isArray(form.visa_types) || form.visa_types.length === 0) && (
                        <p className="mt-1 text-xs text-red-500">
                          Please select at least one visa type
                        </p>
                      )}
                    </div>

                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Detailed Job Document</label>
                    <input
                      type="file"
                      accept=".pdf,.doc,.docx,.txt,.md"
                      onChange={(e) => setFile(e.target.files && e.target.files[0] ? e.target.files[0] : null)}
                      className="block w-full text-sm text-gray-700 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-cyan-50 file:text-cyan-700 hover:file:bg-cyan-100"
                    />
                    <p className="text-xs text-gray-500 mt-1">Accepted: PDF, DOC, DOCX, TXT, MD</p>
                  </div>
                </>
              )}

              {step === 4 && (
                <div className="space-y-6">
                  <div className="text-slate-700 text-sm">This is how your job posting will appear to job seekers:</div>
                  
                  {/* Job Posting Preview */}
                  <Card className="p-6 bg-white border-2 border-slate-200">
                    {/* Header */}
                    <div className="flex items-start justify-between mb-4">
                      <div className="space-y-1">
                        <h3 className="text-[22px] md:text-2xl font-semibold text-slate-900">{form.title || 'Job Title'}</h3>
                        <div className="text-slate-600 font-medium text-sm md:text-[15px]">{user?.company_name || 'Your Company'}</div>
                        <div className="mt-1 text-sm text-slate-600 flex items-center">
                          <MapPin className="h-4 w-4 mr-1" /> {form.location || form.city || form.state || 'Location'}
                        </div>
                      </div>
                      <div className="h-12 w-12 rounded-lg bg-gray-100 flex items-center justify-center text-gray-500">
                        <Building2 className="h-5 w-5" />
                      </div>
                    </div>

                    {/* Meta chips row */}
                    <div className="mb-4 flex flex-wrap items-center gap-2">
                      {form.employment_type && (
                        <span className="inline-flex items-center rounded-full border border-slate-200 bg-white text-slate-700 px-2.5 py-0.5 text-xs">
                          <Clock className="h-3 w-3 mr-1" />
                          {getEmploymentBasisLabel(form.employment_type)}
                        </span>
                      )}
                      {form.experience_level && (
                        <span className="inline-flex items-center rounded-full border border-slate-200 bg-white text-slate-700 px-2.5 py-0.5 text-xs">
                          {form.experience_level}
                        </span>
                      )}
                      {form.salary_min && form.salary_max && (
                        <span className="inline-flex items-center rounded-full bg-slate-100 text-slate-700 px-2.5 py-0.5 text-xs">
                          <DollarSign className="h-3 w-3 mr-1" />
                          ${Math.round(form.salary_min/1000)}k - ${Math.round(form.salary_max/1000)}k
                        </span>
                      )}
                    </div>

                    {/* Badges */}
                    <div className="mb-4 flex flex-wrap gap-2">
                      <span className="inline-flex items-center rounded-full bg-cyan-100 text-cyan-700 px-2.5 py-0.5 text-xs">
                        New
                      </span>
                      {form.visa_sponsorship && (
                        <span className="inline-flex items-center rounded-full bg-cyan-100 text-cyan-700 px-2.5 py-0.5 text-xs">
                          <ShieldCheck className="h-3 w-3 mr-1" /> Visa Friendly
                        </span>
                      )}
                      {form.visa_types && form.visa_types.length > 0 && (
                        <span className="inline-flex items-center rounded-full bg-cyan-100 text-cyan-700 px-2.5 py-0.5 text-xs">
                          <GraduationCap className="h-3 w-3 mr-1" /> {form.visa_types[0]}
                        </span>
                      )}
                    </div>

                    {/* Skills */}
                    {(form.required_skills && form.required_skills.length > 0) && (
                      <div className="mb-4">
                        <div className="text-sm font-medium text-slate-700 mb-2">Required Skills:</div>
                        <div className="flex flex-wrap gap-2">
                          {form.required_skills.slice(0, 8).map((skill, i) => (
                            <span key={i} className="px-2 py-1 bg-slate-100 rounded text-xs text-slate-700">{skill}</span>
                          ))}
                          {form.required_skills.length > 8 && (
                            <span className="px-2 py-1 bg-slate-100 rounded text-xs text-slate-700">+{form.required_skills.length - 8} more</span>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Description Preview */}
                    <div className="border-t border-slate-200 pt-4">
                      <div className="text-[15px] md:text-[16px] leading-7 text-slate-800">
                        {form.description ? (
                          <div dangerouslySetInnerHTML={{ __html: form.description }} />
                        ) : (
                          <p className="text-slate-500 italic">Add a compelling job description to attract candidates...</p>
                        )}
                      </div>
                    </div>

                    {/* Apply Button */}
                    <div className="mt-6 pt-4 border-t border-slate-200">
                      <Button className="w-full">
                        Apply Now
                      </Button>
                    </div>
                  </Card>
                </div>
              )}

              {/* Footer buttons */}
              <div className="flex justify-between pt-2">
                <div className="flex gap-2">
                  <Button type="button" variant="outline" onClick={() => navigate('/employer/dashboard')}>Cancel</Button>
                  <Button type="button" variant="outline" onClick={saveDraft} loading={submitting}>
                    {submitting ? 'Saving...' : 'Save Draft'}
                  </Button>
                </div>
                <div className="flex gap-2">
                  {step > 0 && (
                    <Button type="button" variant="outline" onClick={back}>Back</Button>
                  )}
                  {step < steps.length - 1 ? (
                    <Button type="button" onClick={next}>Next</Button>
                  ) : (
                    <Button type="button" onClick={() => onSubmit()} disabled={submitting}>
                      {submitting 
                        ? (isEditing ? 'Updating…' : 'Publishing…') 
                        : (isEditing ? 'Update Job' : 'Publish Job')
                      }
                    </Button>
                  )}
                </div>
              </div>
            </form>
          </Card>
        </div>

        {/* Summary card (sticky on desktop) - hidden on final step */}
        {step !== 4 && (
          <div className="lg:col-span-4">
            <div className="lg:sticky lg:top-6">
              <Card className="p-6">
                <div className="text-sm text-slate-600 mb-2">Live Preview</div>
                <div className="text-lg font-semibold text-slate-900">{form.title || 'Job Title'}</div>
                <div className="text-slate-700">{user?.company_name || 'Your company'}</div>
                <div className="mt-1 text-sm text-slate-600">{form.location || form.city || form.state || 'Location'}</div>
                <div className="mt-1 text-xs text-slate-600">
                  {form.role_category ? getRoleCategoryLabel(form.role_category) : 'Role category'} • {form.employment_type ? getEmploymentBasisLabel(form.employment_type) : 'Employment basis'}
                </div>
                <div 
                  className="mt-3 text-sm text-slate-700 line-clamp-4"
                  dangerouslySetInnerHTML={{ 
                    __html: form.description || 'Add a compelling description to attract candidates.' 
                  }}
                />
                <div className="mt-4 flex flex-wrap gap-2">
                  {(form.required_skills || []).slice(0,6).map((s, i) => (
                    <span key={i} className="px-2 py-1 bg-slate-100 rounded text-xs text-slate-700">{s}</span>
                  ))}
                </div>
              </Card>
            </div>
          </div>
        )}
      </div>

      {/* VISA Disclaimer */}
      <div className="mt-6">
        <Card className="p-6 bg-slate-50 border-slate-200">
          <div className="text-sm text-slate-700 whitespace-pre-wrap">
            Joborra verifies VISA statuses and conditions based on the information provided by the user. Therefore, Joborra is not liable for any visa verification errors that arise from lack of truthful information from the user or the unprecedented update in the integrated VISA verifiying service. Joborra does not verify employment eligibility on behalf of employers.
          </div>
        </Card>
      </div>

      {success && (
        <div className="mt-6">
          <Card className="p-6">
            <div className="text-green-700 font-medium">{success}</div>
            <div className="text-sm text-slate-600 mt-1">We are redirecting you to your profile…</div>
          </Card>
        </div>
      )}
    </div>
  );
};

export default EmployerPostJobPage;

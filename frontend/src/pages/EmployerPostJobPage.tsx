import React, { useEffect, useMemo, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { EmployerJobCreate } from '../types';
import apiService from '../services/api';
import Button from '../components/ui/Button';
import Card from '../components/ui/Card';
import Input from '../components/ui/Input';

const EmployerPostJobPage: React.FC = () => {
  const navigate = useNavigate();

  const [form, setForm] = useState<EmployerJobCreate>({
    title: '',
    description: '',
    location: '',
    city: '',
    state: '',
    employment_type: 'Full-time',
    job_type: '',
    salary: '',
    salary_min: undefined,
    salary_max: undefined,
    salary_currency: 'AUD',
    experience_level: 'mid',
    remote_option: false,
    visa_sponsorship: false,
    visa_type: '',
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
  const [success, setSuccess] = useState<string | null>(null);
  const [step, setStep] = useState(0); // 0..4

  // Address autocomplete
  const [locationQuery, setLocationQuery] = useState('');
  const [locationSuggestions, setLocationSuggestions] = useState<string[]>([]);
  const [showLocationSuggestions, setShowLocationSuggestions] = useState(false);
  useEffect(() => {
    const q = locationQuery.trim();
    if (!q) { setLocationSuggestions([]); return; }
    const t = setTimeout(async () => {
      try {
        const items = await apiService.getLocationSuggestions(q, 8);
        setLocationSuggestions(items);
      } catch (e) {
        setLocationSuggestions([]);
      }
    }, 250);
    return () => clearTimeout(t);
  }, [locationQuery]);

  // Rich text editor (basic) for description
  const descRef = useRef<HTMLDivElement | null>(null);
  const applyCmd = (cmd: 'bold' | 'italic' | 'insertUnorderedList') => {
    document.execCommand(cmd);
    // Sync back
    const html = descRef.current?.innerHTML || '';
    handleChange('description', html);
  };

  // Visa types with descriptions
  const VISA_TYPES: Array<{ value: string; label: string; description: string }> = useMemo(() => ([
    { value: '', label: 'Select visa type (optional)', description: '' },
    { value: '482', label: 'Subclass 482 (TSS)', description: 'Temporary Skill Shortage visa (employer-sponsored).' },
    { value: '186', label: 'Subclass 186 (ENS)', description: 'Employer Nomination Scheme (permanent).' },
    { value: '494', label: 'Subclass 494 (Regional)', description: 'Skilled Employer Sponsored Regional (provisional).' },
    { value: '407', label: 'Subclass 407 (Training)', description: 'Training visa for workplace-based training.' },
    { value: '400', label: 'Subclass 400 (Temporary Work)', description: 'Short-term, highly specialised work.' },
  ]), []);

  // Draft support (localStorage)
  useEffect(() => {
    try {
      const raw = localStorage.getItem('job_draft');
      if (raw) {
        const draft = JSON.parse(raw);
        if (window.confirm('A saved draft was found. Do you want to load it?')) {
          setForm((prev) => ({ ...prev, ...draft }));
          if (draft?.description && descRef.current) {
            descRef.current.innerHTML = draft.description;
          }
        }
      }
    } catch {}
  }, []);

  const saveDraft = () => {
    try {
      const data = { ...form };
      localStorage.setItem('job_draft', JSON.stringify(data));
      setSuccess('Draft saved locally');
      setTimeout(() => setSuccess(null), 1200);
    } catch (e) {
      setError('Failed to save draft');
    }
  };

  const steps = useMemo(() => [
    'Basics',
    'Requirements',
    'Compensation',
    'Options',
    'Review & Publish'
  ], []);

  const handleChange = (key: keyof EmployerJobCreate, value: any) => {
    setForm(prev => ({ ...prev, [key]: value }));
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
      if (!form.description || form.description.trim().length < 20) {
        setError('Description must be at least 20 characters.');
        setSubmitting(false);
        return;
      }

      const created = await apiService.createEmployerJob({
        ...form,
        // Normalize empty strings to undefined for optional fields
        job_type: form.job_type || undefined,
        salary: form.salary || undefined,
        visa_type: form.visa_type || undefined,
        education_requirements: form.education_requirements || undefined,
        city: form.city || undefined,
        state: form.state || undefined,
        location: form.location || undefined,
        experience_level: form.experience_level || undefined,
      });

      if (file) {
        try {
          await apiService.uploadJobDocument(created.id, file);
        } catch (uploadErr: any) {
          // Non-fatal, job is created
          console.error('Document upload failed', uploadErr);
        }
      }

      setSuccess('Job posted successfully. Redirecting to your profile…');
      // Redirect employer to their profile after short delay
      setTimeout(() => navigate('/profile'), 900);
    } catch (err: any) {
      const msg = err?.response?.data?.detail || err?.message || 'Failed to create job';
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

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl md:text-3xl font-bold text-slate-900">Post a Job</h1>
        <a href="/employer/company" className="text-sm text-primary-700 hover:underline">Update company info</a>
      </div>

      {/* Stepper */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          {steps.map((label, i) => (
            <div key={label} className="flex-1 flex items-center">
              <div className={`flex items-center gap-2 ${i <= step ? 'text-primary-700' : 'text-slate-400'}`}>
                <div className={`h-8 w-8 rounded-full flex items-center justify-center text-sm font-semibold border ${i <= step ? 'bg-primary-100 border-primary-300' : 'bg-white border-slate-300'}`}>{i+1}</div>
                <div className="hidden sm:block text-sm font-medium">{label}</div>
              </div>
              {i < steps.length - 1 && (
                <div className={`flex-1 h-px mx-3 ${i < step ? 'bg-primary-300' : 'bg-slate-200'}`} />
              )}
            </div>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-8">
          <Card>
            <form onSubmit={(e)=>{e.preventDefault();}} className="space-y-6 p-6">
              {error && (
                <div className="p-3 rounded border border-amber-300 bg-amber-50 text-amber-900 text-sm">{error}</div>
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
                    <Input
                      label="Job Type (Category)"
                      placeholder="e.g., Software Engineering"
                      value={form.job_type || ''}
                      onChange={(e) => handleChange('job_type', e.target.value)}
                    />
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Employment Type</label>
                      <select
                        className="w-full rounded-md border border-gray-300 p-2 focus:ring-cyan-500 focus:border-cyan-500"
                        value={form.employment_type || ''}
                        onChange={(e) => handleChange('employment_type', e.target.value)}
                      >
                        <option value="">Select</option>
                        <option>Full-time</option>
                        <option>Part-time</option>
                        <option>Contract</option>
                        <option>Casual</option>
                        <option>Internship</option>
                      </select>
                    </div>
                    <Input
                      label="Experience Level"
                      placeholder="e.g., entry/mid/senior"
                      value={form.experience_level || ''}
                      onChange={(e) => handleChange('experience_level', e.target.value)}
                    />
                    {/* Address Autocomplete */}
                    <div className="relative">
                      <label className="block text-sm font-medium text-gray-700 mb-1">Location</label>
                      <input
                        className="w-full rounded-md border border-gray-300 p-2 focus:ring-cyan-500 focus:border-cyan-500"
                        placeholder="e.g., Sydney, NSW"
                        value={form.location || ''}
                        onChange={(e) => { handleChange('location', e.target.value); setLocationQuery(e.target.value); setShowLocationSuggestions(true); }}
                        onFocus={() => setShowLocationSuggestions(true)}
                        onBlur={() => setTimeout(()=>setShowLocationSuggestions(false), 150)}
                      />
                      {showLocationSuggestions && locationSuggestions.length > 0 && (
                        <div className="absolute z-10 mt-1 w-full rounded-md border border-slate-200 bg-white shadow">
                          {locationSuggestions.map((s) => (
                            <button
                              type="button"
                              key={s}
                              className="w-full text-left px-3 py-2 text-sm hover:bg-slate-50"
                              onClick={() => { handleChange('location', s); setLocationQuery(s); setShowLocationSuggestions(false); }}
                            >
                              {s}
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
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
                    {/* Basic rich editor */}
                    <div className="flex items-center gap-2 mb-2">
                      <Button type="button" variant="outline" onClick={() => applyCmd('bold')}>Bold</Button>
                      <Button type="button" variant="outline" onClick={() => applyCmd('italic')}>Italic</Button>
                      <Button type="button" variant="outline" onClick={() => applyCmd('insertUnorderedList')}>Bullets</Button>
                      <Button
                        type="button"
                        variant="outline"
                        onClick={async () => {
                          const draft = await apiService.generateJobDescription({ title: form.title, skills: form.required_skills || [] });
                          handleChange('description', draft);
                          if (descRef.current) descRef.current.innerHTML = draft;
                        }}
                      >AI Generate</Button>
                    </div>
                    <div
                      ref={descRef}
                      className="w-full rounded-md border border-gray-300 p-2 min-h-[200px] focus:outline-none"
                      contentEditable
                      suppressContentEditableWarning
                      onInput={(e) => handleChange('description', (e.target as HTMLDivElement).innerHTML)}
                      dangerouslySetInnerHTML={{ __html: form.description || '' }}
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
                    label="Salary Min"
                    type="number"
                    value={form.salary_min === undefined ? '' : form.salary_min}
                    onChange={(e) => handleChange('salary_min', e.target.value ? Number(e.target.value) : undefined)}
                  />
                  <Input
                    label="Salary Max"
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
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Visa Type (optional)</label>
                      <select
                        className="w-full rounded-md border border-gray-300 p-2 focus:ring-cyan-500 focus:border-cyan-500"
                        value={form.visa_type || ''}
                        onChange={(e) => handleChange('visa_type', e.target.value)}
                      >
                        {VISA_TYPES.map(v => (
                          <option key={v.value} value={v.value}>{v.label}</option>
                        ))}
                      </select>
                      {form.visa_type && (
                        <div className="text-xs text-slate-600 mt-1">{VISA_TYPES.find(v=>v.value===form.visa_type)?.description}</div>
                      )}
                    </div>
                    <div className="flex items-center mt-6">
                      <input
                        id="studentFriendly"
                        type="checkbox"
                        className="rounded border-gray-300 text-cyan-600 focus:ring-cyan-500 mr-2"
                        checked={!!form.international_student_friendly}
                        onChange={(e) => handleChange('international_student_friendly', e.target.checked)}
                      />
                      <label htmlFor="studentFriendly" className="text-sm text-gray-700">Student Friendly</label>
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
                <div className="space-y-4">
                  <div className="text-slate-700 text-sm">Review your job details before publishing.</div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    <div className="rounded border border-slate-200 p-3">
                      <div className="font-medium text-slate-900">Basics</div>
                      <div className="mt-2 text-slate-700">{form.title} • {form.job_type || '—'} • {form.employment_type || '—'}</div>
                      <div className="text-slate-700">{form.location || '—'} {form.city || ''} {form.state || ''}</div>
                    </div>
                    <div className="rounded border border-slate-200 p-3">
                      <div className="font-medium text-slate-900">Compensation</div>
                      <div className="mt-2 text-slate-700">{form.salary || '—'} ({form.salary_min ?? '—'} - {form.salary_max ?? '—'})</div>
                    </div>
                    <div className="rounded border border-slate-200 p-3 md:col-span-2">
                      <div className="font-medium text-slate-900">Requirements</div>
                      <div className="mt-2">
                        <div className="text-slate-700">Required: {(form.required_skills || []).join(', ') || '—'}</div>
                        <div className="text-slate-700">Preferred: {(form.preferred_skills || []).join(', ') || '—'}</div>
                      </div>
                    </div>
                    <div className="rounded border border-slate-200 p-3 md:col-span-2">
                      <div className="font-medium text-slate-900">Options</div>
                      <div className="mt-2 text-slate-700">Visa Sponsorship: {form.visa_sponsorship ? 'Yes' : 'No'} {form.visa_type ? `(${form.visa_type})` : ''} • Student Friendly: {form.international_student_friendly ? 'Yes' : 'No'}</div>
                    </div>
                  </div>
                </div>
              )}

              {/* Footer buttons */}
              <div className="flex justify-between pt-2">
                <div className="flex gap-2">
                  <Button type="button" variant="outline" onClick={() => navigate('/jobs')}>Cancel</Button>
                  <Button type="button" variant="outline" onClick={saveDraft}>Save Draft</Button>
                </div>
                <div className="flex gap-2">
                  {step > 0 && (
                    <Button type="button" variant="outline" onClick={back}>Back</Button>
                  )}
                  {step < steps.length - 1 ? (
                    <Button type="button" onClick={next}>Next</Button>
                  ) : (
                    <Button type="button" onClick={() => onSubmit()} disabled={submitting}>
                      {submitting ? 'Publishing…' : 'Publish Job'}
                    </Button>
                  )}
                </div>
              </div>
            </form>
          </Card>
        </div>

        {/* Summary card (sticky on desktop) */}
        <div className="lg:col-span-4">
          <div className="lg:sticky lg:top-6">
            <Card className="p-6">
              <div className="text-sm text-slate-600 mb-2">Live Preview</div>
              <div className="text-lg font-semibold text-slate-900">{form.title || 'Job Title'}</div>
              <div className="text-slate-700">Your company</div>
              <div className="mt-1 text-sm text-slate-600">{form.location || form.city || form.state || 'Location'}</div>
              <div className="mt-3 text-sm text-slate-700 line-clamp-4 whitespace-pre-wrap">{form.description || 'Add a compelling description to attract candidates.'}</div>
              <div className="mt-4 flex flex-wrap gap-2">
                {(form.required_skills || []).slice(0,6).map((s, i) => (
                  <span key={i} className="px-2 py-1 bg-slate-100 rounded text-xs text-slate-700">{s}</span>
                ))}
              </div>
            </Card>
          </div>
        </div>
      </div>

      {/* VISA Disclaimer */}
      <div className="mt-6">
        <Card className="p-6 bg-slate-50 border-slate-200">
          <div className="text-sm text-slate-700 whitespace-pre-wrap">
            Joborra verifies VISA statuses and conditions based on the information provided by the user. Therefore, Joborra is not liable for any visa verification errors that arise from lack of truthful information from the user or the unprecedented update in the integrated VISA verifiying service. Joborra does not verify employment eligibility on behalf of employers.
            <br />
            It is the responsibility of each user to ensure they are legally permitted to work in Australia.
            <br />
            We recommend checking your visa status through the VEVO website or consulting a registered migration agent.
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

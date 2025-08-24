import React, { useMemo, useState } from 'react';
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

      setSuccess('Job posted successfully.');
      // Redirect to jobs list or employer jobs overview after short delay
      setTimeout(() => navigate('/jobs'), 900);
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
                    <Input
                      label="Location"
                      placeholder="e.g., Sydney, NSW"
                      value={form.location || ''}
                      onChange={(e) => handleChange('location', e.target.value)}
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
                    <textarea
                      className="w-full rounded-md border border-gray-300 p-2 focus:ring-cyan-500 focus:border-cyan-500 min-h-[160px]"
                      value={form.description}
                      onChange={(e) => handleChange('description', e.target.value)}
                      required
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
                    label="Salary (text)"
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
                    <Input
                      label="Visa Type (optional)"
                      placeholder="e.g., Subclass 482"
                      value={form.visa_type || ''}
                      onChange={(e) => handleChange('visa_type', e.target.value)}
                    />
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
                <Button type="button" variant="outline" onClick={() => navigate('/jobs')}>Cancel</Button>
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

      {success && (
        <div className="mt-6">
          <Card className="p-6">
            <div className="text-green-700 font-medium">{success}</div>
            <div className="text-sm text-slate-600 mt-1">We are redirecting you to the jobs list…</div>
          </Card>
        </div>
      )}
    </div>
  );
};

export default EmployerPostJobPage;

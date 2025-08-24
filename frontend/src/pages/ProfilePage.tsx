import React, { useEffect, useState } from 'react';
import Card from '../components/ui/Card';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';
import { useAuth } from '../contexts/AuthContext';
import apiService from '../services/api';
import { AU_UNIVERSITIES } from '../constants/universities';

const ProfilePage: React.FC = () => {
  const { user: ctxUser, refreshUser } = useAuth();
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [verifyLink, setVerifyLink] = useState<string | null>(null);
  // Sub-tab state
  const [activeTab, setActiveTab] = useState<'profile' | 'visa'>('profile');
  // Visa state
  const [loadingVisa, setLoadingVisa] = useState(false);
  const [visaInfo, setVisaInfo] = useState<any | null>(null);
  const [visaSubmitting, setVisaSubmitting] = useState(false);
  const [visaMsg, setVisaMsg] = useState<string | null>(null);
  // Visa document upload state
  const [visaDocType, setVisaDocType] = useState<'passport' | 'visa_grant' | 'coe' | 'vevo'>('vevo');
  const [visaDocUploading, setVisaDocUploading] = useState(false);
  const [visaDocFile, setVisaDocFile] = useState<File | null>(null);
  // Removed sensitive PII fields from visa form; VEVO upload only
  // Resume upload state
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [resumeUploading, setResumeUploading] = useState(false);
  const [form, setForm] = useState({
    full_name: '',
    university: '',
    degree: '',
    graduation_year: '' as number | string,
    visa_status: '',
    // Study details (student)
    course_name: '',
    institution_name: '',
    course_start_date: '',
    course_end_date: '',
    coe_number: '',
    company_name: '',
    company_website: '',
    company_size: '',
    industry: '',
  });

  // Education & Experience (UI-level for now)
  const [education, setEducation] = useState([
    { institution: '', degree: '', field: '', start_year: '', end_year: '' },
  ] as Array<{ institution: string; degree: string; field: string; start_year: string; end_year: string } >);
  const [experience, setExperience] = useState([
    { company: '', title: '', start: '', end: '', description: '' },
  ] as Array<{ company: string; title: string; start: string; end: string; description: string } >);

  useEffect(() => {
    setForm({
      full_name: ctxUser?.full_name || '',
      university: ctxUser?.university || '',
      degree: ctxUser?.degree || '',
      graduation_year: ctxUser?.graduation_year || '',
      visa_status: ctxUser?.visa_status || '',
      course_name: ctxUser?.course_name || '',
      institution_name: ctxUser?.institution_name || '',
      course_start_date: ctxUser?.course_start_date ? ctxUser.course_start_date.substring(0, 10) : '',
      course_end_date: ctxUser?.course_end_date ? ctxUser.course_end_date.substring(0, 10) : '',
      coe_number: ctxUser?.coe_number || '',
      company_name: ctxUser?.company_name || '',
      company_website: ctxUser?.company_website || '',
      company_size: ctxUser?.company_size || '',
      industry: ctxUser?.industry || '',
    });
    // TODO: hydrate education/experience from backend when available
  }, [ctxUser]);

  // Derive avatar initials from name/email
  const initials = React.useMemo(() => {
    const src = (ctxUser?.full_name || ctxUser?.email || '').trim();
    if (!src) return '?';
    const parts = src.split(/[\s._-]+/).filter(Boolean);
    if (parts.length === 1) return parts[0].substring(0, 2).toUpperCase();
    return (parts[0].substring(0, 1) + parts[1].substring(0, 1)).toUpperCase();
  }, [ctxUser]);

  // Load visa status for students
  useEffect(() => {
    const loadVisa = async () => {
      if (ctxUser?.role !== 'student') return;
      setLoadingVisa(true);
      setVisaMsg(null);
      try {
        const info = await apiService.getVisaStatus();
        setVisaInfo(info);
      } catch (e) {
        setVisaMsg('Failed to load visa status');
      } finally {
        setLoadingVisa(false);
      }
    };
    loadVisa();
  }, [ctxUser]);

  const onUploadResume = async () => {
    if (!resumeFile) return;
    setResumeUploading(true);
    setMessage(null);
    try {
      await apiService.uploadResume(resumeFile);
      await refreshUser();
      setMessage('Resume uploaded successfully');
      setResumeFile(null);
    } catch (err) {
      setMessage('Failed to upload resume. Please upload a PDF file.');
    } finally {
      setResumeUploading(false);
    }
  };

  const onUploadVisaDoc = async () => {
    if (!visaDocFile) return;
    setVisaDocUploading(true);
    setVisaMsg(null);
    try {
      await apiService.uploadVisaDocument(visaDocType, visaDocFile);
      const info = await apiService.getVisaStatus();
      setVisaInfo(info);
      setVisaMsg('Document uploaded successfully');
      setVisaDocFile(null);
    } catch (err) {
      setVisaMsg('Failed to upload document. Allowed: PDF, JPG, PNG, DOC, DOCX');
    } finally {
      setVisaDocUploading(false);
    }
  };

  const onSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setMessage(null);
    try {
      const payload: any = {
        full_name: form.full_name,
        university: form.university || undefined,
        degree: form.degree || undefined,
        graduation_year: form.graduation_year ? Number(form.graduation_year) : undefined,
        visa_status: form.visa_status || undefined,
        // Study (only include for students)
        course_name: ctxUser?.role === 'student' && form.course_name ? form.course_name : undefined,
        institution_name: ctxUser?.role === 'student' && form.institution_name ? form.institution_name : undefined,
        course_start_date: ctxUser?.role === 'student' && form.course_start_date ? new Date(form.course_start_date).toISOString() : undefined,
        course_end_date: ctxUser?.role === 'student' && form.course_end_date ? new Date(form.course_end_date).toISOString() : undefined,
        coe_number: ctxUser?.role === 'student' && form.coe_number ? form.coe_number : undefined,
        company_name: form.company_name || undefined,
        company_website: form.company_website || undefined,
        company_size: form.company_size || undefined,
        industry: form.industry || undefined,
      };
      await apiService.updateProfile(payload);
      await refreshUser();
      setMessage('Profile updated successfully');
    } catch (err) {
      setMessage('Failed to update profile');
    } finally {
      setSaving(false);
    }
  };

  // Removed submitVisa form; VEVO upload only

  return (
    <div className="min-h-screen">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl md:text-3xl font-bold tracking-tight text-slate-900">Your Profile</h1>
          <div className="flex items-center gap-2">
            {ctxUser?.role === 'employer' && (
              <>
                <a href="/employer/post-job" className="inline-flex items-center px-3 py-2 rounded-md text-sm font-medium bg-primary-600 text-white hover:bg-primary-700">Post a Job</a>
                <a href="/employer/company" className="inline-flex items-center px-3 py-2 rounded-md text-sm font-medium border border-slate-300 text-slate-700 hover:bg-slate-50">Company Info</a>
              </>
            )}
          </div>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Sidebar */}
          <aside className="lg:col-span-4">
            <Card className="p-6">
              <div className="flex items-center gap-4">
                <div className="h-14 w-14 rounded-full bg-primary-100 text-primary-700 flex items-center justify-center font-semibold">
                  {initials}
                </div>
                <div>
                  <div className="font-medium text-slate-900">{ctxUser?.full_name || 'Your name'}</div>
                  <div className="text-sm text-slate-600">{ctxUser?.email}</div>
                </div>
              </div>
              {ctxUser?.role === 'student' && (
                <div className="mt-4 grid grid-cols-3 gap-3 text-center">
                  <div className="rounded-md border border-slate-200 p-3">
                    <div className="text-sm text-slate-600">Visa</div>
                    <div className="text-sm font-semibold text-slate-900">{visaInfo?.verification_status || '—'}</div>
                  </div>
                  <div className="rounded-md border border-slate-200 p-3">
                    <div className="text-sm text-slate-600">Resume</div>
                    <div className="text-sm font-semibold text-slate-900">{ctxUser?.resume_url ? 'Uploaded' : 'Missing'}</div>
                  </div>
                  <div className="rounded-md border border-slate-200 p-3">
                    <div className="text-sm text-slate-600">Verified</div>
                    <div className="text-sm font-semibold text-slate-900">{ctxUser?.is_verified ? 'Yes' : 'No'}</div>
                  </div>
                </div>
              )}
              <div className="mt-4 flex flex-wrap gap-2">
                <button className={`px-3 py-2 text-sm rounded-md border ${activeTab==='profile'?'border-primary-600 text-primary-700':'border-slate-200 text-slate-700'}`} onClick={()=>setActiveTab('profile')}>Profile</button>
                {ctxUser?.role === 'student' && (
                  <>
                    <button className={`px-3 py-2 text-sm rounded-md border ${activeTab==='visa'?'border-primary-600 text-primary-700':'border-slate-200 text-slate-700'}`} onClick={()=>setActiveTab('visa')}>Visa</button>
                    <a href="/applications" className="px-3 py-2 text-sm rounded-md border border-slate-200 text-slate-700 hover:bg-slate-50">View Applications</a>
                  </>
                )}
              </div>

              {/* Quick Links */}
              <div className="mt-4 border-t border-slate-200 pt-4 space-y-2">
                {ctxUser?.role === 'student' && (
                  <a href="/applications" className="block text-sm text-primary-700 hover:underline">Submitted Applications</a>
                )}
                {ctxUser?.role === 'employer' && (
                  <>
                    <a href="/employer/post-job" className="block text-sm text-primary-700 hover:underline">Post a Job</a>
                    <a href="/employer/company" className="block text-sm text-primary-700 hover:underline">Company Information</a>
                  </>
                )}
              </div>
            </Card>
          </aside>

          {/* Main content */}
          <section className="lg:col-span-8">
            {/* Sub-tabs (desktop hidden since we have sidebar buttons) */}
            <div className="border-b border-slate-200 mb-6 lg:hidden">
              <nav className="-mb-px flex items-center justify-between" aria-label="Tabs">
                <button
                  className={`whitespace-nowrap py-4 px-1 border-b-2 text-sm font-medium ${activeTab === 'profile' ? 'border-primary-600 text-primary-700' : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'}`}
                  onClick={() => setActiveTab('profile')}
                >
                  Profile Details
                </button>
                {ctxUser?.role === 'student' && (
                  <div className="flex items-center gap-4">
                    <button
                      className={`whitespace-nowrap py-4 px-1 border-b-2 text-sm font-medium ${activeTab === 'visa' ? 'border-primary-600 text-primary-700' : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'}`}
                      onClick={() => setActiveTab('visa')}
                    >
                      Visa Verification
                    </button>
                    <a href="/applications" className="inline-flex items-center px-3 py-1.5 rounded-md text-xs font-medium border border-slate-300 text-slate-700 hover:bg-slate-50">View Applications</a>
                  </div>
                )}
              </nav>
            </div>

            {/* Profile Details Tab */}
            {activeTab === 'profile' && (
              <Card className="p-6 space-y-8">
            {/* Email verification banner */}
            {!ctxUser?.is_verified && (
              <div className="rounded-md border border-amber-300 bg-amber-50 p-4 text-amber-900">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <div className="font-medium">Verify your email to unlock all features</div>
                    <div className="text-sm mt-1">Your account is not verified yet. Click the button below to get a verification link.</div>
                  </div>
                  <Button
                    type="button"
                    variant="outline"
                    onClick={async () => {
                      setSaving(true); setMessage(null);
                      try {
                        const res: any = await apiService.requestEmailVerification();
                        if ((res as any)?.verify_url) {
                          setVerifyLink((res as any).verify_url);
                          setMessage('Verification link generated. Use the button below or copy the link.');
                        } else {
                          setMessage('If not already verified, a link has been issued.');
                        }
                      } catch (e) {
                        setMessage('Failed to issue verification link');
                      } finally {
                        setSaving(false);
                      }
                    }}
                  >
                    Send verification link
                  </Button>
                </div>
              </div>
            )}
            {/* Show the verification link in a properly wrapped box with actions */}
            {!ctxUser?.is_verified && verifyLink && (
              <div className="mt-4 rounded-md border border-slate-200 bg-white p-3">
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <div className="text-sm font-medium text-slate-800 mb-1">Verification link</div>
                    <a
                      href={verifyLink}
                      className="text-sm text-cyan-700 underline break-all"
                      target="_blank"
                      rel="noreferrer"
                    >
                      {verifyLink}
                    </a>
                  </div>
                  <div className="flex-shrink-0 flex gap-2">
                    <Button
                      type="button"
                      variant="outline"
                      onClick={async () => {
                        try { await navigator.clipboard.writeText(verifyLink); setMessage('Link copied to clipboard'); } catch { setMessage('Copy failed'); }
                      }}
                    >
                      Copy link
                    </Button>
                    <a href={verifyLink} target="_blank" rel="noreferrer">
                      <Button type="button">Open</Button>
                    </a>
                  </div>
                </div>
              </div>
            )}
            <form onSubmit={onSave} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input label="Full Name" value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} required />
                <Input label="Visa Status" value={form.visa_status} onChange={(e) => setForm({ ...form, visa_status: e.target.value })} />
              </div>

              {ctxUser?.role === 'student' ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">University</label>
                    <select
                      value={form.university}
                      onChange={(e) => setForm({ ...form, university: e.target.value })}
                      className="input-field w-full"
                    >
                      <option value="">Select your university</option>
                      {AU_UNIVERSITIES.map((u) => (
                        <option key={u} value={u}>{u}</option>
                      ))}
                    </select>
                  </div>
                  <Input label="Degree" value={form.degree} onChange={(e) => setForm({ ...form, degree: e.target.value })} />
                  <Input label="Graduation Year" type="number" value={form.graduation_year} onChange={(e) => setForm({ ...form, graduation_year: e.target.value })} />
                  {/* Study details */}
                  <Input label="Course Name" value={form.course_name} onChange={(e) => setForm({ ...form, course_name: e.target.value })} />
                  <Input label="Institution Name" value={form.institution_name} onChange={(e) => setForm({ ...form, institution_name: e.target.value })} />
                  <Input label="Course Start Date" type="date" value={form.course_start_date} onChange={(e) => setForm({ ...form, course_start_date: e.target.value })} />
                  <Input label="Course End Date" type="date" value={form.course_end_date} onChange={(e) => setForm({ ...form, course_end_date: e.target.value })} />
                  <Input label="COE Number" value={form.coe_number} onChange={(e) => setForm({ ...form, coe_number: e.target.value })} />
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Input label="Company Name" value={form.company_name} onChange={(e) => setForm({ ...form, company_name: e.target.value })} />
                  <Input label="Company Website" value={form.company_website} onChange={(e) => setForm({ ...form, company_website: e.target.value })} />
                  <Input label="Company Size" value={form.company_size} onChange={(e) => setForm({ ...form, company_size: e.target.value })} />
                  <Input label="Industry" value={form.industry} onChange={(e) => setForm({ ...form, industry: e.target.value })} />
                </div>
              )}

              {message && <div className="text-sm text-slate-700">{message}</div>}

              <div className="flex justify-end">
                <Button type="submit" loading={saving}>Save Changes</Button>
              </div>
            </form>
            {/* Resume Upload */}
            {ctxUser?.role === 'student' && (
              <div className="mt-8 border-t border-slate-200 pt-6">
                <h3 className="text-lg font-semibold text-slate-900 mb-3">Resume</h3>
                {ctxUser?.resume_url && (
                  <div className="text-sm text-slate-600 mb-2">
                    Current resume: <a className="text-cyan-600 underline" href={apiService.getFileUrl(ctxUser.resume_url)} target="_blank" rel="noreferrer">View</a>
                  </div>
                )}
                <div className="flex items-center gap-3">
                  <input
                    type="file"
                    accept="application/pdf"
                    onChange={(e) => setResumeFile(e.target.files?.[0] || null)}
                    className="block w-full text-sm text-slate-900"
                  />
                  <Button type="button" onClick={onUploadResume} loading={resumeUploading} disabled={!resumeFile}>Upload PDF</Button>
                </div>
                <p className="text-xs text-slate-500 mt-1">PDF only. Max size 10MB.</p>
              </div>
            )}
              </Card>
            )}

            {/* Visa Verification Tab (students only) */}
            {activeTab === 'visa' && ctxUser?.role === 'student' && (
              <Card className="p-6">
            {/* Status */}
            <div className="mb-6">
              {loadingVisa ? (
                <div className="text-slate-600">Loading visa status...</div>
              ) : visaInfo ? (
                <div>
                  <div className="text-sm text-slate-700">
                    <span className="font-medium">Status:</span>{' '}
                    {visaInfo.verification_status || (visaInfo.has_verification ? 'pending' : 'not_started')}
                  </div>
                  {visaInfo.verification_message && (
                    <div className="text-sm text-slate-600 mt-1">{visaInfo.verification_message}</div>
                  )}
                </div>
              ) : (
                <div className="text-slate-600">No visa info yet.</div>
              )}
            </div>

            {/* VEVO upload only, no PII */}
            <div>
              <h3 className="text-lg font-semibold text-slate-900 mb-3">Upload VEVO Result</h3>
              <p className="text-sm text-slate-600 mb-3">Please upload your VEVO check result (PDF, JPG, or PNG). Do not upload passport or other PII documents.</p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-3">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Document Type</label>
                  <select
                    value={visaDocType}
                    onChange={(e) => setVisaDocType(e.target.value as any)}
                    className="input-field w-full"
                  >
                    <option value="vevo">VEVO Result</option>
                  </select>
                </div>
                <div className="md:col-span-2 flex items-end">
                  <input
                    type="file"
                    accept=".pdf,.jpg,.jpeg,.png,application/pdf,image/*"
                    onChange={(e) => setVisaDocFile(e.target.files?.[0] || null)}
                    className="block w-full text-sm text-slate-900"
                  />
                </div>
              </div>
              <div className="flex justify-end">
                <Button type="button" onClick={onUploadVisaDoc} loading={visaDocUploading} disabled={!visaDocFile}>Upload VEVO</Button>
              </div>
              <p className="text-xs text-slate-500 mt-1">Allowed: PDF, JPG, PNG. Max size 10MB.</p>
              {visaMsg && <div className="text-sm text-slate-600 mt-2">{visaMsg}</div>}
            </div>

            {/* Education Section */}
            {ctxUser?.role === 'student' && (
              <div>
                <h3 className="text-lg font-semibold text-slate-900 mb-3">Education</h3>
                {education.map((ed, idx) => (
                  <div key={idx} className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                    <Input label="Institution" value={ed.institution} onChange={(e) => {
                      const next = [...education]; next[idx].institution = e.target.value; setEducation(next);
                    }} />
                    <Input label="Degree" value={ed.degree} onChange={(e) => {
                      const next = [...education]; next[idx].degree = e.target.value; setEducation(next);
                    }} />
                    <Input label="Field of Study" value={ed.field} onChange={(e) => {
                      const next = [...education]; next[idx].field = e.target.value; setEducation(next);
                    }} />
                    <div className="grid grid-cols-2 gap-4">
                      <Input label="Start Year" value={ed.start_year} onChange={(e) => {
                        const next = [...education]; next[idx].start_year = e.target.value; setEducation(next);
                      }} />
                      <Input label="End Year" value={ed.end_year} onChange={(e) => {
                        const next = [...education]; next[idx].end_year = e.target.value; setEducation(next);
                      }} />
                    </div>
                  </div>
                ))}
                <div className="flex gap-2">
                  <Button type="button" variant="outline" onClick={() => setEducation([...education, { institution: '', degree: '', field: '', start_year: '', end_year: '' }])}>Add Education</Button>
                </div>
              </div>
            )}

            {/* Experience Section */}
            <div>
              <h3 className="text-lg font-semibold text-slate-900 mb-3">Experience</h3>
              {experience.map((ex, idx) => (
                <div key={idx} className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                  <Input label="Company" value={ex.company} onChange={(e) => {
                    const next = [...experience]; next[idx].company = e.target.value; setExperience(next);
                  }} />
                  <Input label="Title" value={ex.title} onChange={(e) => {
                    const next = [...experience]; next[idx].title = e.target.value; setExperience(next);
                  }} />
                  <div className="grid grid-cols-2 gap-4">
                    <Input label="Start Date" type="month" value={ex.start} onChange={(e) => {
                      const next = [...experience]; next[idx].start = e.target.value; setExperience(next);
                    }} />
                    <Input label="End Date" type="month" value={ex.end} onChange={(e) => {
                      const next = [...experience]; next[idx].end = e.target.value; setExperience(next);
                    }} />
                  </div>
                  <Input label="Description" value={ex.description} onChange={(e) => {
                    const next = [...experience]; next[idx].description = e.target.value; setExperience(next);
                  }} />
                </div>
              ))}
              <div className="flex gap-2">
                <Button type="button" variant="outline" onClick={() => setExperience([...experience, { company: '', title: '', start: '', end: '', description: '' }])}>Add Experience</Button>
              </div>
            </div>
              </Card>
            )}
          </section>
        </div>
      </div>
    </div>
  );
};
export default ProfilePage;

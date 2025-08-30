import React, { useEffect, useMemo, useState } from 'react';
import Card from '../components/ui/Card';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';
import SkillInput from '../components/ui/SkillInput';
import GoogleIcon from '../components/ui/GoogleIcon';
import { useAuth } from '../contexts/AuthContext';
import apiService from '../services/api';
import { useToast } from '../contexts/ToastContext';

const ProfilePage: React.FC = () => {
  const { user: ctxUser, refreshUser } = useAuth();
  const { toast } = useToast();
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [resumeMessage, setResumeMessage] = useState<string | null>(null);
  const [verifyLink, setVerifyLink] = useState<string | null>(null);
  // Sub-tab state
  const [activeTab, setActiveTab] = useState<'profile' | 'visa'>('profile');
  // Visa state
  const [loadingVisa, setLoadingVisa] = useState(false);
  const [visaInfo, setVisaInfo] = useState<any | null>(null);
  
  const [visaMsg, setVisaMsg] = useState<string | null>(null);
  // Visa document upload state
  const [visaDocUploading, setVisaDocUploading] = useState(false);
  const [visaDocFile, setVisaDocFile] = useState<File | null>(null);
  const [visaConsentGiven, setVisaConsentGiven] = useState(false);
  // Removed sensitive PII fields from visa form; VEVO upload only
  // Resume upload state
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [resumeUploading, setResumeUploading] = useState(false);
  const [form, setForm] = useState({
    full_name: '',
    visa_status: '',
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
  // Skills & Extracurriculars (UI only for now)
  const [skills, setSkills] = useState<string[]>([]);
  const [skillInput, setSkillInput] = useState('');
  const [activities, setActivities] = useState<string[]>([]);
  const [activityInput, setActivityInput] = useState('');

  useEffect(() => {
    setForm({
      full_name: ctxUser?.full_name || '',
      visa_status: ctxUser?.visa_status || '',
      company_name: ctxUser?.company_name || '',
      company_website: ctxUser?.company_website || '',
      company_size: ctxUser?.company_size || '',
      industry: ctxUser?.industry || '',
    });
    // Hydrate education/experience from backend JSON strings if present
    try {
      const rawEdu = (ctxUser as any)?.education;
      if (rawEdu) {
        const parsed = typeof rawEdu === 'string' ? JSON.parse(rawEdu) : rawEdu;
        if (Array.isArray(parsed) && parsed.length > 0) setEducation(parsed);
      }
    } catch {}
    try {
      const rawExp = (ctxUser as any)?.experience;
      if (rawExp) {
        const parsed = typeof rawExp === 'string' ? JSON.parse(rawExp) : rawExp;
        if (Array.isArray(parsed) && parsed.length > 0) setExperience(parsed);
      }
    } catch {}
    // Try hydrate skills & activities from localStorage (UI-only persistence for now)
    try {
      const sk = localStorage.getItem('profile_skills');
      if (sk) setSkills(JSON.parse(sk));
      const act = localStorage.getItem('profile_activities');
      if (act) setActivities(JSON.parse(act));
    } catch {}
  }, [ctxUser]);

  // Google Account Linking
  const [linking, setLinking] = useState(false);
  const isGoogleLinked = useMemo(() => ctxUser?.oauth_provider === 'google', [ctxUser]);

  const ensureGoogleScript = (): Promise<void> => {
    return new Promise((resolve, reject) => {
      if ((window as any).google?.accounts?.id) return resolve();
      const existing = document.getElementById('google-identity-services');
      if (existing) {
        existing.addEventListener('load', () => resolve());
        return;
      }
      const script = document.createElement('script');
      script.src = 'https://accounts.google.com/gsi/client';
      script.async = true;
      script.defer = true;
      script.id = 'google-identity-services';
      script.onload = () => resolve();
      script.onerror = () => reject(new Error('Failed to load Google Identity Services'));
      document.head.appendChild(script);
    });
  };

  const onLinkGoogle = async () => {
    setMessage(null);
    setLinking(true);
    try {
      await ensureGoogleScript();
      const google: any = (window as any).google;
      const clientId = (process as any).env.REACT_APP_GOOGLE_CLIENT_ID || (window as any).REACT_APP_GOOGLE_CLIENT_ID;
      if (!clientId) throw new Error('Google Client ID not configured');
      let resolved = false;
      await new Promise<void>((resolve, reject) => {
        try {
          google.accounts.id.initialize({
            client_id: clientId,
            callback: async (resp: any) => {
              if (resolved) return;
              resolved = true;
              const id_token = resp?.credential;
              if (!id_token) {
                reject(new Error('No ID token received'));
                return;
              }
              try {
                await apiService.linkGoogleWithIdToken(id_token);
                await refreshUser();
                setMessage('Google account linked successfully');
                toast('Google account linked', 'success');
                resolve();
              } catch (err: any) {
                const detail = err?.response?.data?.detail || '';
                if (detail === 'link_required' || /link_required/i.test(detail)) {
                  toast('This email is already in use. Sign in with password, then link Google here.', 'error');
                } else if (/email/i.test(detail) && /mismatch|different/i.test(detail)) {
                  toast('Email mismatch between your account and Google profile.', 'error');
                } else if (detail) {
                  toast(detail, 'error');
                } else {
                  toast('Failed to link Google account', 'error');
                }
                setMessage(detail || 'Failed to link Google account');
                reject(err);
              }
            },
            auto_select: false,
            cancel_on_tap_outside: true,
            context: 'use',
          });
          // Use the prompt flow to get an ID token popup
          google.accounts.id.prompt((notification: any) => {
            if (notification.isNotDisplayed() || notification.isSkippedMoment()) {
              // As a fallback, render a one-time button and simulate click
              const container = document.createElement('div');
              document.body.appendChild(container);
              google.accounts.id.renderButton(container, { theme: 'outline', size: 'large' });
              const btn = container.querySelector('div[role="button"]') as HTMLElement | null;
              if (!btn) {
                setMessage('Google Sign-In not available');
                reject(new Error('GIS button render failed'));
              }
            }
          });
        } catch (e) {
          reject(e);
        }
      });
    } catch (e: any) {
      if (!message) setMessage(e?.message || 'Failed to start Google linking');
    } finally {
      setLinking(false);
    }
  };

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
    setResumeMessage(null);
    try {
      await apiService.uploadResume(resumeFile);
      await refreshUser();
      setResumeMessage('Resume uploaded successfully');
      setResumeFile(null);
    } catch (err) {
      setResumeMessage('Failed to upload resume. Please upload a PDF file.');
    } finally {
      setResumeUploading(false);
    }
  };

  const onUploadVisaDoc = async () => {
    if (!visaDocFile || !visaConsentGiven) return;
    setVisaDocUploading(true);
    setVisaMsg(null);
    try {
      await apiService.uploadVisaDocument(visaDocFile);
      const info = await apiService.getVisaStatus();
      setVisaInfo(info);
      setVisaMsg('VEVO document uploaded successfully');
      setVisaDocFile(null);
      setVisaConsentGiven(false);
    } catch (err) {
      setVisaMsg('Failed to upload VEVO document. Allowed: PDF, JPG, PNG, DOC, DOCX');
    } finally {
      setVisaDocUploading(false);
    }
  };

  const onSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setMessage(null);
    try {
      // Map education fields from first education entry to keep backend fields populated
      let derivedUniversity: string | undefined = undefined;
      let derivedDegree: string | undefined = undefined;
      let derivedGradYear: number | undefined = undefined;
      if (ctxUser?.role === 'student' && education && education.length > 0) {
        const ed0: any = education[0] || {};
        derivedUniversity = ed0.institution || undefined;
        derivedDegree = ed0.degree || undefined;
        const gy = (ed0.end_year || '').toString().trim();
        if (gy && /^\d{4}$/.test(gy)) {
          derivedGradYear = Number(gy);
        }
      }
      const payload: any = {
        full_name: form.full_name,
        university: derivedUniversity,
        degree: derivedDegree,
        graduation_year: derivedGradYear,
        visa_status: form.visa_status || undefined,
        company_name: form.company_name || undefined,
        company_website: form.company_website || undefined,
        company_size: form.company_size || undefined,
        industry: form.industry || undefined,
        // Persist education/experience as JSON strings (backend stores TEXT)
        education: ctxUser?.role === 'student' ? JSON.stringify(education || []) : undefined,
        experience: JSON.stringify(experience || []),
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
                    <div className="text-sm font-semibold text-slate-900">{visaInfo?.verification_status || 'Pending Verification'}</div>
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
            {/* Google Account Linking */}
            <div className="rounded-md border border-slate-200 p-4">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <div className="font-medium text-slate-900">Google Account</div>
                  <div className="text-sm text-slate-600 mt-1">
                    {isGoogleLinked ? 'Your account is linked with Google Sign-In.' : 'Link your Google account to sign in seamlessly and enhance security.'}
                  </div>
                </div>
                <Button type="button" variant="outline" onClick={onLinkGoogle} disabled={isGoogleLinked} loading={linking}>
                  <GoogleIcon className="h-4 w-4 mr-2" />
                  {isGoogleLinked ? 'Linked' : 'Link Google Account'}
                </Button>
              </div>
            </div>

            <form onSubmit={onSave} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input label="Full Name" value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} required />
                <Input label="Visa Status" value={form.visa_status} onChange={(e) => setForm({ ...form, visa_status: e.target.value })} />
              </div>

              {ctxUser?.role === 'student' ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Student-specific fields can be added here if needed in the future */}
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
                {resumeMessage && (
                  <div className={`text-sm mt-2 ${resumeMessage.includes('successfully') ? 'text-green-600' : 'text-red-600'}`}>
                    {resumeMessage}
                  </div>
                )}
              </div>
            )}
            {/* Education Section (moved from Visa tab) */}
            {ctxUser?.role === 'student' && (
              <div className="mt-8 border-t border-slate-200 pt-6">
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
            {/* Experience Section (students only) */}
            {ctxUser?.role === 'student' && (
              <div className="mt-8 border-t border-slate-200 pt-6">
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
            )}
            {/* Skills (students only) */}
            {ctxUser?.role === 'student' && (
              <div className="mt-8 border-t border-slate-200 pt-6">
                <h3 className="text-lg font-semibold text-slate-900 mb-3">Skills</h3>
                <div className="mb-2">
                  <SkillInput
                    value={skillInput}
                    onChange={setSkillInput}
                    onAdd={() => {
                      const v = skillInput.trim();
                      if (!v) return;
                      const next = [...skills, v];
                      setSkills(next);
                      setSkillInput('');
                      try {
                        localStorage.setItem('profile_skills', JSON.stringify(next));
                      } catch {}
                    }}
                    placeholder="Type a skill for AI-powered suggestions..."
                    context={education.length > 0 ? education[0].field || education[0].degree : undefined}
                  />
                </div>
                <div className="flex flex-wrap gap-2">
                  {skills.map((s, i) => (
                    <span key={`${s}-${i}`} className="px-2 py-1 bg-slate-100 rounded text-sm">
                      {s}
                      <button type="button" className="ml-2 text-red-500" onClick={()=>{
                        const next = skills.filter((_, idx)=> idx!==i); setSkills(next); try{ localStorage.setItem('profile_skills', JSON.stringify(next)); } catch{}
                      }}>×</button>
                    </span>
                  ))}
                </div>
              </div>
            )}
            {/* Extracurricular Activities (students only) */}
            {ctxUser?.role === 'student' && (
              <div className="mt-8 border-t border-slate-200 pt-6">
                <h3 className="text-lg font-semibold text-slate-900 mb-3">Extracurricular Activities</h3>
                <div className="flex gap-2 mb-2">
                  <Input value={activityInput} onChange={(e)=>setActivityInput(e.target.value)} placeholder="Add an activity (clubs, volunteering, leadership)" />
                  <Button type="button" variant="outline" onClick={()=>{
                    const v = activityInput.trim(); if(!v) return; const next=[...activities, v]; setActivities(next); setActivityInput('');
                    try{ localStorage.setItem('profile_activities', JSON.stringify(next)); } catch{}
                  }}>Add</Button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {activities.map((a, i) => (
                    <span key={`${a}-${i}`} className="px-2 py-1 bg-slate-100 rounded text-sm">
                      {a}
                      <button type="button" className="ml-2 text-red-500" onClick={()=>{
                        const next = activities.filter((_, idx)=> idx!==i); setActivities(next); try{ localStorage.setItem('profile_activities', JSON.stringify(next)); } catch{}
                      }}>×</button>
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Save button at the very end */}
            <div className="mt-8 flex justify-end">
              <Button type="button" onClick={onSave} loading={saving}>Save Changes</Button>
            </div>
              </Card>
            )}

            {/* Visa Verification Tab (students only) */}
            {activeTab === 'visa' && ctxUser?.role === 'student' && (
              <Card className="p-6">
            {/* Status */}
            <div className="mb-6">
              {loadingVisa ? (
                <div className="text-slate-600">Loading visa status...</div>
              ) : (
                <div>
                  {(() => {
                    const raw = visaInfo?.verification_status || (visaInfo?.has_verification ? 'pending' : 'not_started');
                    const s = String(raw || '').toLowerCase();
                    // Simplified 2-step process: Pending and Verified
                    const steps = ['pending', 'verified'];
                    const isVerified = s.includes('verify') || s.includes('review');
                    const idx = isVerified ? 1 : 0;
                    return (
                      <>
                        <div className="text-sm text-slate-700 mb-2">
                          <span className="font-medium">Status:</span> {
                            isVerified ? 'Verified' : 
                            s.includes('pending') || s.includes('review') ? 'Under Review' : 
                            'Not Started'
                          }
                        </div>
                        <div className="flex items-center justify-between">
                          {steps.map((label, i) => (
                            <div key={label} className="flex-1 flex items-center">
                              <div className={`h-2 w-2 rounded-full ${i<=idx?'bg-primary-600':'bg-slate-300'}`} />
                              {i < steps.length-1 && (
                                <div className={`flex-1 h-[2px] mx-2 ${i<idx?'bg-primary-300':'bg-slate-200'}`} />
                              )}
                            </div>
                          ))}
                        </div>
                        <div className="flex justify-between text-xs text-slate-500 mt-1">
                          <span>Under Review</span>
                          <span>Verified</span>
                        </div>
                        {visaInfo?.verification_message && (
                          <div className="text-sm text-slate-600 mt-2">{visaInfo.verification_message}</div>
                        )}
                      </>
                    );
                  })()}
                </div>
              )}
            </div>

            {/* Visa Documents Upload */}
            <div>
              {/* Visa Disclaimer */}
              <div className="mt-2 mb-5 rounded-md border border-amber-200 bg-amber-50 p-4 text-amber-900">
                <div className="font-medium">Visa verification disclaimer</div>
                <p className="text-sm mt-1">
                  Joborra verifies visa statuses based on the information and documents you provide. While we
                  strive for accuracy, we are not liable for errors arising from inaccurate user information or
                  changes in external services. Please independently verify your status via VEVO or consult a
                  registered migration agent. Avoid uploading unnecessary personally identifiable information (PII).
                </p>
              </div>
              <h3 className="text-lg font-semibold text-slate-900 mb-3">VEVO Document Upload</h3>
              <p className="text-sm text-slate-600 mb-3">Upload your VEVO (Visa Entitlement Verification Online) document to verify your visa status.</p>
              
              <div className="mb-4">
                <label className="block text-sm font-medium text-slate-700 mb-2">VEVO Document</label>
                <input
                  type="file"
                  accept=".pdf,.jpg,.jpeg,.png,application/pdf,image/*,.doc,.docx"
                  onChange={(e) => setVisaDocFile(e.target.files?.[0] || null)}
                  className="block w-full text-sm text-slate-900"
                />
                <p className="text-xs text-slate-500 mt-1">Allowed: PDF, JPG, PNG, DOC, DOCX. Max size 10MB.</p>
              </div>

              <div className="mb-4">
                <div className="flex items-start">
                  <input
                    id="visa-consent"
                    type="checkbox"
                    checked={visaConsentGiven}
                    onChange={(e) => setVisaConsentGiven(e.target.checked)}
                    className="mt-1 h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                  />
                  <label htmlFor="visa-consent" className="ml-2 text-sm text-slate-700">
                    I consent to uploading my VEVO document for visa verification purposes. I understand that this document will be used to verify my visa status and may be stored securely by Joborra.
                  </label>
                </div>
              </div>

              <div className="flex justify-end">
                <Button 
                  type="button" 
                  onClick={onUploadVisaDoc} 
                  loading={visaDocUploading} 
                  disabled={!visaDocFile || !visaConsentGiven}
                >
                  Upload VEVO Document
                </Button>
              </div>
              {visaMsg && <div className="text-sm text-slate-600 mt-2">{visaMsg}</div>}
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

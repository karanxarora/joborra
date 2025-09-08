import React, { useEffect, useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import Card from '../components/ui/Card';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';
import SkillInput from '../components/ui/SkillInput';

import { useAuth } from '../contexts/AuthContext';
import apiService from '../services/api';

const ProfilePage: React.FC = () => {
  const { user: ctxUser, refreshUser } = useAuth();
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [resumeMessage, setResumeMessage] = useState<string | null>(null);
  // const [verifyLink, setVerifyLink] = useState<string | null>(null);  // DISABLED FOR NOW
  const [resumeViewUrl, setResumeViewUrl] = useState<string | null>(null);
  const [resumeViewError, setResumeViewError] = useState<string | null>(null);
  const [visaDocs, setVisaDocs] = useState<any>(null);
  const [visaDocsLoading, setVisaDocsLoading] = useState<boolean>(false);
  const [isEditing, setIsEditing] = useState(false);
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
  // Company logo upload state
  const [logoFile, setLogoFile] = useState<File | null>(null);
  const [form, setForm] = useState({
    full_name: '',
    contact_number: '',
    visa_status: '',
    company_name: '',
    company_website: '',
    company_size: '',
    industry: '',
    company_description: '',
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

  // Helper function to sort education entries by end year (most recent first)
  const sortEducationByDate = (eduArray: any[]) => {
    return [...eduArray].sort((a, b) => {
      const yearA = parseInt(a.end_year) || 0;
      const yearB = parseInt(b.end_year) || 0;
      return yearB - yearA; // Most recent first
    });
  };

  // Helper function to sort experience entries by end date (most recent first)
  const sortExperienceByDate = (expArray: any[]) => {
    return [...expArray].sort((a, b) => {
      // Handle "Present" or empty end dates as most recent
      const endA = a.end?.toLowerCase();
      const endB = b.end?.toLowerCase();
      
      if (endA === 'present' || endA === '' || !endA) return -1;
      if (endB === 'present' || endB === '' || !endB) return 1;
      
      // Parse dates for comparison
      const dateA = new Date(a.end);
      const dateB = new Date(b.end);
      
      return dateB.getTime() - dateA.getTime(); // Most recent first
    });
  };



  useEffect(() => {
    setForm({
      full_name: ctxUser?.full_name || '',
      contact_number: ctxUser?.contact_number || '',
      visa_status: ctxUser?.visa_status || '',
      company_name: ctxUser?.company_name || '',
      company_website: ctxUser?.company_website || '',
      company_size: ctxUser?.company_size || '',
      industry: ctxUser?.industry || '',
      company_description: ctxUser?.company_description || '',
    });
    // Hydrate education/experience from backend JSON strings if present
    try {
      const rawEdu = (ctxUser as any)?.education;
      if (rawEdu) {
        const parsed = typeof rawEdu === 'string' ? JSON.parse(rawEdu) : rawEdu;
        if (Array.isArray(parsed) && parsed.length > 0 && parsed[0].institution) {
          setEducation(sortEducationByDate(parsed));
        } else if (ctxUser?.university && ctxUser?.degree && ctxUser?.graduation_year) {
          // Prefill education from signup data if no education exists
          const degreeDuration = ctxUser.degree?.toLowerCase().includes('master') || ctxUser.degree?.toLowerCase().includes('phd') ? 2 : 3;
          const prefilledEducation = [{
            institution: ctxUser.university,
            degree: ctxUser.degree,
            field: ctxUser.degree, // Use degree as field of study
            start_year: (ctxUser.graduation_year - degreeDuration).toString(),
            end_year: ctxUser.graduation_year.toString()
          }];
          setEducation(prefilledEducation);
        }
      } else if (ctxUser?.university && ctxUser?.degree && ctxUser?.graduation_year) {
        // Prefill education from signup data if no education data exists
        const degreeDuration = ctxUser.degree?.toLowerCase().includes('master') || ctxUser.degree?.toLowerCase().includes('phd') ? 2 : 3;
        const prefilledEducation = [{
          institution: ctxUser.university,
          degree: ctxUser.degree,
          field: ctxUser.degree, // Use degree as field of study
          start_year: (ctxUser.graduation_year - degreeDuration).toString(),
          end_year: ctxUser.graduation_year.toString()
        }];
        setEducation(prefilledEducation);
      }
    } catch {}
    try {
      const rawExp = (ctxUser as any)?.experience;
      if (rawExp) {
        const parsed = typeof rawExp === 'string' ? JSON.parse(rawExp) : rawExp;
        if (Array.isArray(parsed) && parsed.length > 0) setExperience(sortExperienceByDate(parsed));
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

  // Load visa documents (e.g., VEVO) for current user
  useEffect(() => {
    const loadDocs = async () => {
      if (ctxUser?.role !== 'student') return;
      setVisaDocsLoading(true);
      try {
        const docs = await apiService.getVisaDocuments();
        setVisaDocs(docs);
      } catch {
        setVisaDocs(null);
      } finally {
        setVisaDocsLoading(false);
      }
    };
    loadDocs();
  }, [ctxUser]);

  const getResumeViewUrl = useCallback(async () => {
    if (!ctxUser?.resume_url) {
      setResumeViewUrl(null);
      setResumeViewError(null);
      return;
    }
    
    try {
      console.log('Getting resume view URL for user:', ctxUser.id);
      const url = await apiService.getResumeViewUrl();
      console.log('Got resume view URL:', url);
      setResumeViewUrl(url);
      setResumeViewError(null);
    } catch (err: any) {
      console.error('Failed to get resume view URL:', err);
      setResumeViewUrl(null);
      setResumeViewError(err.response?.data?.detail || 'Failed to load resume');
    }
  }, [ctxUser?.resume_url, ctxUser?.id]);

  // Get resume view URL when component first loads
  useEffect(() => {
    if (ctxUser?.resume_url && !resumeViewUrl) {
      getResumeViewUrl();
    }
  }, [ctxUser?.id, ctxUser?.resume_url, resumeViewUrl, getResumeViewUrl]); // Include all dependencies

  const onUploadResume = async () => {
    if (!resumeFile) return;
    setResumeUploading(true);
    setResumeMessage(null);
    try {
      const response = await apiService.uploadResume(resumeFile);
      console.log('Upload response:', response);
      
      // Use the resolved URL directly from the upload response
      if (response.resume_url) {
        setResumeViewUrl(response.resume_url);
        setResumeViewError(null);
        console.log('Upload response:', response);
        console.log('Set resume view URL to:', response.resume_url);
        console.log('URL type:', typeof response.resume_url);
        console.log('URL starts with https:', response.resume_url.startsWith('https'));
      }
      
      await refreshUser();
      setResumeMessage('Resume uploaded successfully');
      setResumeFile(null);
    } catch (err: any) {
      console.error('ProfilePage: Upload failed:', err);
      const errorMessage = err?.response?.data?.detail || err?.message || 'Failed to upload resume. Please try again.';
      setResumeMessage(errorMessage);
    } finally {
      setResumeUploading(false);
    }
  };

  const onUploadVisaDoc = async () => {
    if (!visaDocFile || !visaConsentGiven) return;
    setVisaDocUploading(true);
    setVisaMsg(null);
    try {
      const resp = await apiService.uploadVisaDocument(visaDocFile);
      // Immediately expose the new VEVO link without waiting for another fetch
      setVisaDocs((prev:any)=>({
        ...(prev || {}),
        vevo: { resolved_url: resp?.document_url || null, url: resp?.document_url || null }
      }));
      // Also refresh the full docs list in background to be consistent
      try {
        const docs = await apiService.getVisaDocuments();
        setVisaDocs(docs);
      } catch {}
      const info = await apiService.getVisaStatus();
      setVisaInfo(info);
      setVisaMsg('VEVO document uploaded successfully');
      setVisaDocFile(null);
      setVisaConsentGiven(false);
    } catch (err: any) {
      const errorMessage = err?.response?.data?.detail || err?.message || 'Failed to upload VEVO document. Please try again.';
      setVisaMsg(errorMessage);
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
        contact_number: form.contact_number || undefined,
        university: derivedUniversity,
        degree: derivedDegree,
        graduation_year: derivedGradYear,
        visa_status: form.visa_status || undefined,
        company_name: form.company_name || undefined,
        company_website: form.company_website || undefined,
        company_size: form.company_size || undefined,
        industry: form.industry || undefined,
        company_description: form.company_description || undefined,
        // Persist education/experience as JSON strings (backend stores TEXT)
        education: ctxUser?.role === 'student' ? JSON.stringify(education || []) : undefined,
        experience: JSON.stringify(experience || []),
      };
      const updated = await apiService.updateProfile(payload);
      // Logo upload if provided
      if (logoFile) {
        const res = await apiService.uploadCompanyLogo(logoFile);
        const newUser = { ...updated, company_logo_url: res.company_logo_url } as any;
        localStorage.setItem('user', JSON.stringify(newUser));
        setMessage('Profile and logo updated successfully');
      } else {
        setMessage('Profile updated successfully');
      }
      await refreshUser();
      setIsEditing(false); // Exit edit mode after successful save
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
          <h1 className="text-2xl md:text-3xl font-bold tracking-tight text-slate-900">
            {ctxUser?.role === 'employer' ? 'Company Profile' : 'Your Profile'}
          </h1>
          <div className="flex items-center gap-2">
            {ctxUser?.role === 'employer' && (
              <Link to="/employer/post-job" className="inline-flex items-center px-3 py-2 rounded-md text-sm font-medium bg-primary-600 text-white hover:bg-primary-700">Post a Job</Link>
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
              {/* Email verification banner - DISABLED FOR NOW */}
              {/* {!ctxUser?.is_verified && (
                <div className="mt-4 rounded-md border border-amber-300 bg-amber-50 p-3 text-amber-900">
                  <div className="text-xs mt-1">Your account is not verified yet. Click the button below to get a verification link.</div>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    className="mt-2 w-full"
                    onClick={async () => {
                      setSaving(true); setMessage(null);
                      try {
                        const res: any = await apiService.requestEmailVerification();
                        if ((res as any)?.verify_url) {
                          setVerifyLink((res as any).verify_url);
                          setMessage('Verification link generated. Use the button below or copy the link.');
                        } else {
                          setMessage('Verification email sent! Check your inbox.');
                        }
                      } catch (err: any) {
                        setMessage(err?.response?.data?.detail || 'Failed to send verification email');
                      } finally {
                        setSaving(false);
                      }
                    }}
                    disabled={saving}
                  >
                    {saving ? 'Sending...' : 'Send Verification Email'}
                  </Button>
                  {verifyLink && (
                    <div className="mt-2">
                      <div className="text-xs text-amber-700 mb-1">Verification link:</div>
                      <div className="text-xs bg-white p-2 rounded border break-all">{verifyLink}</div>
                    </div>
                  )}
                </div>
              )} */}
              {ctxUser?.role === 'student' && (
                <div className="mt-4 grid grid-cols-2 gap-3 text-center">
                  <div className="rounded-md border border-slate-200 p-3">
                    <div className="text-sm text-slate-600">Visa</div>
                    <div className="text-sm font-semibold text-slate-900">{visaInfo?.verification_status || 'Pending Verification'}</div>
                  </div>
                  <div className="rounded-md border border-slate-200 p-3">
                    <div className="text-sm text-slate-600">Resume</div>
                    <div className="text-sm font-semibold text-slate-900">{ctxUser?.resume_url ? 'Uploaded' : 'Missing'}</div>
                  </div>
                </div>
              )}
              <div className="mt-4 flex flex-wrap gap-2">
                <button className={`px-3 py-2 text-sm rounded-md border ${activeTab==='profile'?'border-primary-600 text-primary-700':'border-slate-200 text-slate-700'}`} onClick={()=>setActiveTab('profile')}>Profile</button>
                {ctxUser?.role === 'student' && (
                  <button className={`px-3 py-2 text-sm rounded-md border ${activeTab==='visa'?'border-primary-600 text-primary-700':'border-slate-200 text-slate-700'}`} onClick={()=>setActiveTab('visa')}>Visa</button>
                )}
              </div>

              {/* Quick Links */}
              <div className="mt-4 border-t border-slate-200 pt-4 space-y-2">
                {ctxUser?.role === 'employer' && (
                  <Link to="/employer/post-job" className="block text-sm text-primary-700 hover:underline">Post a Job</Link>
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
                    <span className="inline-flex items-center px-3 py-1.5 rounded-md text-xs font-medium border border-slate-300 text-slate-400 cursor-not-allowed" title="Disabled for Pilot">View Applications</span>
                  </div>
                )}
              </nav>
            </div>

            {/* Profile Details Tab */}
            {activeTab === 'profile' && (
              <Card className={`p-6 space-y-8 ${!isEditing ? 'bg-slate-50' : 'bg-white'}`}>
                {/* Profile Header with Edit Button */}
                <div className="flex items-center justify-between">
                  <h2 className="text-xl font-semibold text-slate-900">Profile Details</h2>
                  {!isEditing ? (
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => setIsEditing(true)}
                    >
                      Edit Profile
                    </Button>
                  ) : (
                    <div className="flex gap-2">
                      <Button
                        type="button"
                        variant="outline"
                        onClick={() => {
                          setIsEditing(false);
                          setMessage(null);
                          // Reset form to original values
                          setForm({
                            full_name: ctxUser?.full_name || '',
                            contact_number: ctxUser?.contact_number || '',
                            visa_status: ctxUser?.visa_status || '',
                            company_name: ctxUser?.company_name || '',
                            company_website: ctxUser?.company_website || '',
                            company_size: ctxUser?.company_size || '',
                            industry: ctxUser?.industry || '',
                            company_description: ctxUser?.company_description || '',
                          });
                        }}
                      >
                        Cancel
                      </Button>
                      <Button type="button" onClick={onSave} loading={saving}>
                        Save Changes
                      </Button>
                    </div>
                  )}
                </div>

                {message && (
                  <div className={`p-3 rounded-md ${message.includes('successfully') ? 'bg-green-50 text-green-700 border border-green-200' : 'bg-red-50 text-red-700 border border-red-200'}`}>
                    {message}
                  </div>
                )}

            <form onSubmit={onSave} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input 
                  label="Full Name" 
                  value={form.full_name} 
                  onChange={(e) => setForm({ ...form, full_name: e.target.value })} 
                  required 
                  disabled={!isEditing}
                />
                <Input 
                  label="Contact Number" 
                  value={form.contact_number} 
                  onChange={(e) => setForm({ ...form, contact_number: e.target.value })} 
                  placeholder="+61 4XX XXX XXX"
                  disabled={!isEditing}
                />
                {ctxUser?.role === 'student' && (
                  <Input 
                    label="Visa Status" 
                    value={form.visa_status} 
                    onChange={(e) => setForm({ ...form, visa_status: e.target.value })} 
                    disabled={!isEditing}
                  />
                )}
              </div>

              {ctxUser?.role === 'student' ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Student-specific fields can be added here if needed in the future */}
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Input 
                    label="Company Name" 
                    value={form.company_name} 
                    onChange={(e) => setForm({ ...form, company_name: e.target.value })} 
                    disabled={!isEditing}
                  />
                  <Input 
                    label="Company Website" 
                    value={form.company_website} 
                    onChange={(e) => setForm({ ...form, company_website: e.target.value })} 
                    disabled={!isEditing}
                  />
                  <Input 
                    label="Company Size" 
                    value={form.company_size} 
                    onChange={(e) => setForm({ ...form, company_size: e.target.value })} 
                    disabled={!isEditing}
                  />
                  <Input 
                    label="Industry" 
                    value={form.industry} 
                    onChange={(e) => setForm({ ...form, industry: e.target.value })} 
                    disabled={!isEditing}
                  />
                </div>
              )}

              {/* Company Details and Logo (employers only) */}
              {ctxUser?.role === 'employer' && (
                <>
                  <div className="mt-6">
                    <label className="block text-sm font-medium text-gray-700 mb-2">Company Details</label>
                    <textarea
                      value={form.company_description}
                      onChange={(e) => setForm({ ...form, company_description: e.target.value })}
                      placeholder="Tell us about your company... Include information like:
• Company mission and values
• What makes your company unique
• Company culture and work environment
• Growth opportunities for employees
• Any awards or recognition
• Company history or milestones
• Benefits and perks you offer
• Team structure and collaboration style"
                      rows={8}
                      disabled={!isEditing}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent resize-vertical disabled:bg-gray-100 disabled:text-gray-500"
                    />
                    <p className="text-xs text-slate-500 mt-1">
                      This information will help students understand your company better and make more informed decisions about applying to your roles.
                    </p>
                  </div>

                  <div className="mt-6">
                    <label className="block text-sm font-medium text-gray-700 mb-1">Company Logo</label>
                    {ctxUser?.company_logo_url && (
                      <div className="text-sm text-slate-600 mb-2">
                        Current logo: <a className="text-cyan-600 underline" href={apiService.getFileUrl(ctxUser.company_logo_url)} target="_blank" rel="noreferrer">View</a>
                      </div>
                    )}
                    {isEditing ? (
                      <>
                        <input
                          type="file"
                          accept="image/*"
                          onChange={(e) => setLogoFile(e.target.files?.[0] || null)}
                          className="block w-full text-sm text-gray-700 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-cyan-50 file:text-cyan-700 hover:file:bg-cyan-100"
                        />
                        <p className="text-xs text-slate-500 mt-1">PNG, JPG, JPEG, WEBP, or SVG.</p>
                      </>
                    ) : (
                      <p className="text-sm text-slate-500">Click "Edit Profile" to upload a new logo</p>
                    )}
                  </div>
                </>
              )}

            </form>
            {/* Resume Upload */}
            {ctxUser?.role === 'student' && (
              <div className="mt-8 border-t border-slate-200 pt-6">
                <h3 className="text-lg font-semibold text-slate-900 mb-3">Resume</h3>
                {ctxUser?.resume_url && (
                  <div className="text-sm text-slate-600 mb-2">
                    Current resume: {resumeViewUrl ? (
                      <a 
                        href={resumeViewUrl} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-cyan-600 hover:text-cyan-700 underline"
                      >
                        View
                      </a>
                    ) : resumeViewError ? (
                      <span className="text-red-600">Error: {resumeViewError}</span>
                    ) : (
                      <span className="text-slate-500">Loading...</span>
                    )}
                  </div>
                )}
                {isEditing ? (
                  <>
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
                  </>
                ) : (
                  <p className="text-sm text-slate-500">Click "Edit Profile" to upload a new resume</p>
                )}
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
                    {idx === 0 && education.length > 1 && (
                      <div className="col-span-full mb-2">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                          Most Recent
                        </span>
                      </div>
                    )}
                    <Input 
                      label="Institution" 
                      value={ed.institution} 
                      onChange={(e) => {
                        const next = [...education]; next[idx].institution = e.target.value; setEducation(next);
                      }} 
                      disabled={!isEditing}
                    />
                    <Input 
                      label="Degree" 
                      value={ed.degree} 
                      onChange={(e) => {
                        const next = [...education]; next[idx].degree = e.target.value; setEducation(next);
                      }} 
                      disabled={!isEditing}
                    />
                    <Input 
                      label="Field of Study" 
                      value={ed.field} 
                      onChange={(e) => {
                        const next = [...education]; next[idx].field = e.target.value; setEducation(next);
                      }} 
                      disabled={!isEditing}
                    />
                    <div className="grid grid-cols-2 gap-4">
                                            <Input 
                        label="Start Year" 
                        value={ed.start_year} 
                        onChange={(e) => {
                          const next = [...education]; next[idx].start_year = e.target.value; setEducation(next);
                        }} 
                        disabled={!isEditing}
                      />
                      <Input 
                        label="End Year" 
                        value={ed.end_year} 
                        onChange={(e) => {
                          const next = [...education]; next[idx].end_year = e.target.value;
                          setEducation(sortEducationByDate(next));
                        }} 
                        disabled={!isEditing}
                      />
                    </div>
                    {education.length > 1 && isEditing && (
                      <div className="col-span-full flex justify-end">
                        <Button 
                          type="button" 
                          variant="outline" 
                          size="sm"
                          onClick={() => {
                            const next = education.filter((_, i) => i !== idx);
                            setEducation(sortEducationByDate(next));
                          }}
                          className="text-red-600 hover:text-red-700 hover:bg-red-50"
                        >
                          Remove
                        </Button>
                      </div>
                    )}
                  </div>
                ))}
                {isEditing && (
                  <div className="flex gap-2 items-center">
                    <Button type="button" variant="outline" onClick={() => {
                      const newEducation = [...education, { institution: '', degree: '', field: '', start_year: '', end_year: '' }];
                      setEducation(sortEducationByDate(newEducation));
                    }}>
                      Add Education
                    </Button>
                    {education.length === 1 && ctxUser?.university && ctxUser?.degree && ctxUser?.graduation_year && (
                      <span className="text-xs text-slate-500">
                        (Prefilled from signup data)
                      </span>
                    )}
                  </div>
                )}
              </div>
            )}
            {/* Experience Section (students only) */}
            {ctxUser?.role === 'student' && (
              <div className="mt-8 border-t border-slate-200 pt-6">
                <h3 className="text-lg font-semibold text-slate-900 mb-3">Experience</h3>
                {experience.map((ex, idx) => (
                  <div key={idx} className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                    {idx === 0 && experience.length > 1 && (
                      <div className="col-span-full mb-2">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          Most Recent
                        </span>
                      </div>
                    )}
                    <Input 
                      label="Company" 
                      value={ex.company} 
                      onChange={(e) => {
                        const next = [...experience]; next[idx].company = e.target.value; setExperience(next);
                      }} 
                      disabled={!isEditing}
                    />
                    <Input 
                      label="Title" 
                      value={ex.title} 
                      onChange={(e) => {
                        const next = [...experience]; next[idx].title = e.target.value; setExperience(next);
                      }} 
                      disabled={!isEditing}
                    />
                    <div className="grid grid-cols-2 gap-4">
                      <Input 
                        label="Start Date" 
                        type="month" 
                        value={ex.start} 
                        onChange={(e) => {
                          const next = [...experience]; next[idx].start = e.target.value; setExperience(next);
                        }} 
                        disabled={!isEditing}
                      />
                      <div className="space-y-2">
                        {ex.end === 'Present' ? (
                          <div>
                            <label className="block text-sm font-medium text-slate-700 mb-2">End Date</label>
                            <div className="relative">
                              <div className="flex items-center justify-between px-3 py-2 border border-slate-300 rounded-md bg-slate-50 h-10">
                                <div className="flex items-center space-x-2">
                                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                                  <span className="text-slate-700 font-medium text-sm">Present</span>
                                </div>
                                <button
                                  type="button"
                                  onClick={() => {
                                    const next = [...experience]; 
                                    next[idx].end = ''; 
                                    setExperience(sortExperienceByDate(next));
                                  }}
                                  className="text-xs text-slate-500 hover:text-slate-700 hover:bg-slate-200 px-2 py-1 rounded transition-colors"
                                >
                                  Edit
                                </button>
                              </div>
                            </div>
                          </div>
                        ) : (
                          <>
                                                        <Input 
                              label="End Date" 
                              type="month" 
                              value={ex.end} 
                              onChange={(e) => {
                                const next = [...experience]; 
                                next[idx].end = e.target.value; 
                                setExperience(sortExperienceByDate(next));
                              }} 
                              disabled={!isEditing}
                            />
                            {isEditing && (
                              <button
                                type="button"
                                onClick={() => {
                                  const next = [...experience]; 
                                  next[idx].end = 'Present';
                                  setExperience(sortExperienceByDate(next));
                                }}
                                className="w-full text-xs text-blue-600 hover:text-blue-800 hover:bg-blue-50 py-1 px-2 rounded border border-blue-200 transition-colors"
                              >
                                Set as Present
                              </button>
                            )}
                          </>
                        )}
                      </div>
                    </div>
                    <Input 
                      label="Description" 
                      value={ex.description} 
                      onChange={(e) => {
                        const next = [...experience]; next[idx].description = e.target.value; setExperience(next);
                      }} 
                      disabled={!isEditing}
                    />
                    {experience.length > 1 && isEditing && (
                      <div className="col-span-full flex justify-end">
                        <Button 
                          type="button" 
                          variant="outline" 
                          size="sm"
                          onClick={() => {
                            const next = experience.filter((_, i) => i !== idx);
                            setExperience(sortExperienceByDate(next));
                          }}
                          className="text-red-600 hover:text-red-700 hover:bg-red-50"
                        >
                          Remove
                        </Button>
                      </div>
                    )}
                  </div>
                ))}
                {isEditing && (
                  <div className="flex gap-2">
                    <Button type="button" variant="outline" onClick={() => {
                      const newExperience = [...experience, { company: '', title: '', start: '', end: '', description: '' }];
                      setExperience(sortExperienceByDate(newExperience));
                    }}>Add Experience</Button>
                  </div>
                )}
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
                    disabled={!isEditing}
                  />
                </div>
                <div className="flex flex-wrap gap-2">
                  {skills.map((s, i) => (
                    <span key={`${s}-${i}`} className="px-2 py-1 bg-slate-100 rounded text-sm">
                      {s}
                      {isEditing && (
                        <button type="button" className="ml-2 text-red-500" onClick={()=>{
                          const next = skills.filter((_, idx)=> idx!==i); setSkills(next); try{ localStorage.setItem('profile_skills', JSON.stringify(next)); } catch{}
                        }}>×</button>
                      )}
                    </span>
                  ))}
                </div>
              </div>
            )}
            {/* Extracurricular Activities (students only) */}
            {ctxUser?.role === 'student' && (
              <div className="mt-8 border-t border-slate-200 pt-6">
                <h3 className="text-lg font-semibold text-slate-900 mb-3">Extracurricular Activities</h3>
                {isEditing && (
                  <div className="flex gap-2 mb-2">
                    <Input 
                      value={activityInput} 
                      onChange={(e)=>setActivityInput(e.target.value)} 
                      placeholder="Add an activity (clubs, volunteering, leadership)" 
                    />
                    <Button type="button" variant="outline" onClick={()=>{
                      const v = activityInput.trim(); if(!v) return; const next=[...activities, v]; setActivities(next); setActivityInput('');
                      try{ localStorage.setItem('profile_activities', JSON.stringify(next)); } catch{}
                    }}>Add</Button>
                  </div>
                )}
                {activities.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {activities.map((a, i) => (
                      <span key={`${a}-${i}`} className="px-2 py-1 bg-slate-100 rounded text-sm">
                        {a}
                        {isEditing && (
                          <button type="button" className="ml-2 text-red-500" onClick={()=>{
                            const next = activities.filter((_, idx)=> idx!==i); setActivities(next); try{ localStorage.setItem('profile_activities', JSON.stringify(next)); } catch{}
                          }}>×</button>
                        )}
                      </span>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-slate-500">
                    {isEditing ? "No activities added yet. Use the input above to add activities." : "No activities added yet. Click 'Edit Profile' to add activities."}
                  </p>
                )}
              </div>
            )}


              </Card>
            )}

            {/* Visa Verification Tab (students only) */}
            {activeTab === 'visa' && ctxUser?.role === 'student' && (
              <Card className="p-6">
                <div className="pt-4">
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

              <div className="flex items-center justify-between">
                <div>
                  {(() => {
                    const v = visaInfo as any;
                    const vevoUrl = (visaDocs?.vevo?.resolved_url)
                      || (v?.vevo_document_url || null);
                    return visaDocsLoading ? (
                      <span className="text-sm text-slate-500">Loading documents…</span>
                    ) : vevoUrl ? (
                      <a
                        href={vevoUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-cyan-600 hover:text-cyan-700 underline text-sm"
                      >
                        View VEVO Document
                      </a>
                    ) : (
                      <span className="text-sm text-slate-500">No VEVO document uploaded</span>
                    );
                  })()}
                </div>
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

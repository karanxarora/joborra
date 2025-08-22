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
  const [visaForm, setVisaForm] = useState({
    visa_subclass: '500',
    passport_number: '',
    passport_country: '',
    passport_expiry: '',
    course_name: '',
    institution_name: '',
    course_start_date: '',
    course_end_date: '',
    coe_number: '',
  });
  // Resume upload state
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [resumeUploading, setResumeUploading] = useState(false);
  const [form, setForm] = useState({
    full_name: '',
    university: '',
    degree: '',
    graduation_year: '' as number | string,
    visa_status: '',
    company_name: '',
    company_website: '',
    company_size: '',
    industry: '',
  });

  useEffect(() => {
    setForm({
      full_name: ctxUser?.full_name || '',
      university: ctxUser?.university || '',
      degree: ctxUser?.degree || '',
      graduation_year: ctxUser?.graduation_year || '',
      visa_status: ctxUser?.visa_status || '',
      company_name: ctxUser?.company_name || '',
      company_website: ctxUser?.company_website || '',
      company_size: ctxUser?.company_size || '',
      industry: ctxUser?.industry || '',
    });
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

  const onSubmitVisa = async (e: React.FormEvent) => {
    e.preventDefault();
    setVisaSubmitting(true);
    setVisaMsg(null);
    try {
      // Build payload respecting backend schema (omit empty fields)
      const payload: any = {
        visa_subclass: visaForm.visa_subclass,
        passport_number: visaForm.passport_number,
        passport_country: visaForm.passport_country,
      };
      if (visaForm.passport_expiry) payload.passport_expiry = new Date(visaForm.passport_expiry).toISOString();
      if (visaForm.course_name) payload.course_name = visaForm.course_name;
      if (visaForm.institution_name) payload.institution_name = visaForm.institution_name;
      if (visaForm.course_start_date) payload.course_start_date = new Date(visaForm.course_start_date).toISOString();
      if (visaForm.course_end_date) payload.course_end_date = new Date(visaForm.course_end_date).toISOString();
      if (visaForm.coe_number) payload.coe_number = visaForm.coe_number;

      await apiService.submitVisaVerification(payload);
      const info = await apiService.getVisaStatus();
      setVisaInfo(info);
      setVisaMsg('Visa verification submitted');
    } catch (err) {
      setVisaMsg('Failed to submit visa verification');
    } finally {
      setVisaSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-2xl md:text-3xl font-bold tracking-tight text-slate-900 mb-6">Your Profile</h1>
        {/* Sub-tabs */}
        <div className="border-b border-slate-200 mb-6">
          <nav className="-mb-px flex space-x-6" aria-label="Tabs">
            <button
              className={`whitespace-nowrap py-4 px-1 border-b-2 text-sm font-medium ${activeTab === 'profile' ? 'border-cyan-600 text-cyan-600' : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'}`}
              onClick={() => setActiveTab('profile')}
            >
              Profile Details
            </button>
            {ctxUser?.role === 'student' && (
              <button
                className={`whitespace-nowrap py-4 px-1 border-b-2 text-sm font-medium ${activeTab === 'visa' ? 'border-cyan-600 text-cyan-600' : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'}`}
                onClick={() => setActiveTab('visa')}
              >
                Visa Verification
              </button>
            )}
          </nav>
        </div>

        {/* Profile Details Tab */}
        {activeTab === 'profile' && (
          <Card className="p-6">
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
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Input label="Company Name" value={form.company_name} onChange={(e) => setForm({ ...form, company_name: e.target.value })} />
                  <Input label="Company Website" value={form.company_website} onChange={(e) => setForm({ ...form, company_website: e.target.value })} />
                  <Input label="Company Size" value={form.company_size} onChange={(e) => setForm({ ...form, company_size: e.target.value })} />
                  <Input label="Industry" value={form.industry} onChange={(e) => setForm({ ...form, industry: e.target.value })} />
                </div>
              )}

              {message && <div className="text-sm text-slate-600">{message}</div>}

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

            {/* Start verification form when none exists */}
            {(!visaInfo || !visaInfo.has_verification) && (
              <form onSubmit={onSubmitVisa} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Input label="Visa Subclass (e.g., 500)" value={visaForm.visa_subclass} onChange={(e) => setVisaForm({ ...visaForm, visa_subclass: e.target.value })} required />
                  <Input label="Passport Number" value={visaForm.passport_number} onChange={(e) => setVisaForm({ ...visaForm, passport_number: e.target.value })} required />
                  <Input label="Passport Country (ISO-3)" value={visaForm.passport_country} onChange={(e) => setVisaForm({ ...visaForm, passport_country: e.target.value.toUpperCase() })} required />
                  <Input label="Passport Expiry" type="date" value={visaForm.passport_expiry} onChange={(e) => setVisaForm({ ...visaForm, passport_expiry: e.target.value })} />
                  <Input label="Course Name" value={visaForm.course_name} onChange={(e) => setVisaForm({ ...visaForm, course_name: e.target.value })} />
                  <Input label="Institution Name" value={visaForm.institution_name} onChange={(e) => setVisaForm({ ...visaForm, institution_name: e.target.value })} />
                  <Input label="Course Start Date" type="date" value={visaForm.course_start_date} onChange={(e) => setVisaForm({ ...visaForm, course_start_date: e.target.value })} />
                  <Input label="Course End Date" type="date" value={visaForm.course_end_date} onChange={(e) => setVisaForm({ ...visaForm, course_end_date: e.target.value })} />
                  <Input label="COE Number" value={visaForm.coe_number} onChange={(e) => setVisaForm({ ...visaForm, coe_number: e.target.value })} />
                </div>

                {visaMsg && <div className="text-sm text-slate-600">{visaMsg}</div>}
                <div className="flex justify-end">
                  <Button type="submit" loading={visaSubmitting}>Start Verification</Button>
                </div>
              </form>
            )}

            {/* If verification exists, encourage docs/vevo actions - could be added later */}
            {visaInfo?.has_verification && (
              <div className="mt-6">
                <h3 className="text-lg font-semibold text-slate-900 mb-3">Upload Supporting Documents</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-3">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">Document Type</label>
                    <select
                      value={visaDocType}
                      onChange={(e) => setVisaDocType(e.target.value as any)}
                      className="input-field w-full"
                    >
                      <option value="vevo">VEVO Result</option>
                      <option value="passport">Passport</option>
                      <option value="visa_grant">Visa Grant Notice</option>
                      <option value="coe">COE</option>
                    </select>
                  </div>
                  <div className="md:col-span-2 flex items-end">
                    <input
                      type="file"
                      accept=".pdf,.jpg,.jpeg,.png,.doc,.docx,application/pdf,image/*,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                      onChange={(e) => setVisaDocFile(e.target.files?.[0] || null)}
                      className="block w-full text-sm text-slate-900"
                    />
                  </div>
                </div>
                <div className="flex justify-end">
                  <Button type="button" onClick={onUploadVisaDoc} loading={visaDocUploading} disabled={!visaDocFile}>Upload Document</Button>
                </div>
                <p className="text-xs text-slate-500 mt-1">Allowed: PDF, JPG, PNG, DOC, DOCX. Max size 10MB.</p>
                {visaMsg && <div className="text-sm text-slate-600 mt-2">{visaMsg}</div>}
              </div>
            )}
          </Card>
        )}
      </div>
    </div>
  );
};

export default ProfilePage;

import React, { useEffect, useState } from 'react';
import Card from '../components/ui/Card';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';
import apiService from '../services/api';
import { User } from '../types';

const EmployerCompanyInfoPage: React.FC = () => {
  const [form, setForm] = useState<Partial<User>>({
    company_name: '',
    company_website: '',
    company_size: '',
    industry: '',
  });
  const [logoFile, setLogoFile] = useState<File | null>(null);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const u = apiService.getCurrentUserFromStorage();
    if (u) {
      setForm({
        company_name: u.company_name || '',
        company_website: u.company_website || '',
        company_size: u.company_size || '',
        industry: u.industry || '',
      });
    }
  }, []);

  const handleChange = (key: keyof User, value: any) => {
    setForm((prev) => ({ ...prev, [key]: value }));
  };

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setMessage(null);
    setError(null);
    try {
      // Save profile fields
      const updated = await apiService.updateProfile({
        company_name: form.company_name,
        company_website: form.company_website,
        company_size: form.company_size,
        industry: form.industry,
      });
      // Persist locally for immediate UI reflection
      localStorage.setItem('user', JSON.stringify(updated));
      // Logo upload if provided
      if (logoFile) {
        const res = await apiService.uploadCompanyLogo(logoFile);
        const newUser = { ...updated, company_logo_url: res.company_logo_url } as any;
        localStorage.setItem('user', JSON.stringify(newUser));
        setMessage('Company details and logo saved.');
      } else {
        setMessage('Company details saved.');
      }
    } catch (err: any) {
      const msg = err?.response?.data?.detail || err?.message || 'Failed to save company info';
      setError(msg);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-2xl md:text-3xl font-bold text-slate-900 mb-4">Company Information</h1>
      <p className="text-slate-600 mb-6">Keep your company profile up to date. These details appear on your job posts.</p>
      <Card>
        <form onSubmit={onSubmit} className="p-6 space-y-6">
          {error && <div className="p-3 rounded bg-red-50 text-red-700 text-sm">{error}</div>}
          {message && <div className="p-3 rounded bg-green-50 text-green-700 text-sm">{message}</div>}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input
              label="Company Name"
              value={form.company_name || ''}
              onChange={(e) => handleChange('company_name', e.target.value)}
              required
            />
            <Input
              label="Website"
              placeholder="https://example.com"
              value={form.company_website || ''}
              onChange={(e) => handleChange('company_website', e.target.value)}
            />
            <Input
              label="Company Size"
              placeholder="e.g., 11-50, 51-200"
              value={form.company_size || ''}
              onChange={(e) => handleChange('company_size', e.target.value)}
            />
            <Input
              label="Industry"
              placeholder="e.g., Software, Hospitality"
              value={form.industry || ''}
              onChange={(e) => handleChange('industry', e.target.value)}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Company Logo</label>
            <input
              type="file"
              accept="image/*"
              onChange={(e) => setLogoFile(e.target.files?.[0] || null)}
              className="block w-full text-sm text-gray-700 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-cyan-50 file:text-cyan-700 hover:file:bg-cyan-100"
            />
            <p className="text-xs text-slate-500 mt-1">PNG, JPG, JPEG, WEBP, or SVG.</p>
          </div>

          <div className="flex justify-end gap-3">
            <Button type="submit" disabled={saving}>{saving ? 'Saving…' : 'Save'}</Button>
          </div>
        </form>
      </Card>
    </div>
  );
};

export default EmployerCompanyInfoPage;

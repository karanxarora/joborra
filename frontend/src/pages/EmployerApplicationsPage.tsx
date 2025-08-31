import React, { useEffect, useState, useMemo } from 'react';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import DisabledButton from '../components/ui/DisabledButton';
import apiService from '../services/api';

interface EmployerApplicationItem {
  id: number;
  job_id: number;
  status: string;
  applied_at: string;
  updated_at: string;
  cover_letter?: string;
  resume_url?: string;
  notes?: string;
  job: {
    id: number;
    title: string;
    location?: string;
    city?: string;
    state?: string;
    company?: { id?: number | null; name: string; website?: string | null };
  };
  user: {
    id: number;
    full_name: string;
    email: string;
    university?: string | null;
    degree?: string | null;
    graduation_year?: number | null;
    resume_url?: string | null;
  };
}

const statusPalette: Record<string, string> = {
  applied: 'bg-amber-100 text-amber-800 ring-amber-200',
  reviewed: 'bg-sky-100 text-sky-800 ring-sky-200',
  interviewed: 'bg-indigo-100 text-indigo-800 ring-indigo-200',
  rejected: 'bg-rose-100 text-rose-800 ring-rose-200',
  offered: 'bg-emerald-100 text-emerald-800 ring-emerald-200',
};

const EmployerApplicationsPage: React.FC = () => {
  const [items, setItems] = useState<EmployerApplicationItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<'All' | 'applied' | 'reviewed' | 'interviewed' | 'offered' | 'rejected'>('All');

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await apiService.listEmployerApplications();
        setItems(data || []);
      } catch (e: any) {
        setError(e?.response?.data?.detail || e?.message || 'Failed to load applications');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const filtered = useMemo(() => {
    if (filter === 'All') return items;
    return items.filter((x) => x.status?.toLowerCase() === filter);
  }, [items, filter]);

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold text-slate-900">Applications</h1>
          <p className="text-slate-600">View applicants for your posted jobs.</p>
        </div>
      </div>

      <div className="flex flex-wrap gap-2 mb-6">
        {(['All','applied','reviewed','interviewed','offered','rejected'] as const).map((s) => (
          <button
            key={s}
            onClick={() => setFilter(s)}
            className={`px-3 py-1.5 rounded-full text-sm font-medium border transition-colors ${
              filter === s ? 'bg-primary-600 border-primary-600 text-white' : 'bg-white border-slate-300 text-slate-700 hover:bg-slate-50'
            }`}
          >
            {s[0].toUpperCase() + s.slice(1)}
          </button>
        ))}
      </div>

      {loading && <Card className="p-6">Loading applications…</Card>}
      {error && <Card className="p-3 bg-red-50 text-red-700">{error}</Card>}

      <div className="space-y-3">
        {!loading && !error && filtered.map((app) => {
          const statusKey = (app.status || '').toLowerCase();
          const badge = statusPalette[statusKey] || 'bg-slate-100 text-slate-800 ring-slate-200';
          const loc = app.job.city && app.job.state ? `${app.job.city}, ${app.job.state}` : (app.job.location || '');
          const resume = app.user.resume_url || app.resume_url;
          const resumeHref = resume ? apiService.getFileUrl(resume) : undefined;
          return (
            <Card key={app.id} className="p-4">
              <div className="flex items-start justify-between gap-4">
                <div className="min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <h2 className="text-base md:text-lg font-semibold text-slate-900 truncate">
                      {app.user.full_name} <span className="text-slate-400 font-normal">applied for</span> {app.job.title}
                    </h2>
                    <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium ring-1 ring-inset ${badge}`}>
                      {app.status}
                    </span>
                  </div>
                  <div className="text-sm text-slate-600 mt-1 truncate">
                    {app.user.email} • {app.user.university || '—'} {app.user.degree ? `• ${app.user.degree}` : ''}
                  </div>
                  <div className="text-xs text-slate-500 mt-1">
                    Job: {app.job.company?.name || 'Your company'} • {loc || '—'}
                  </div>
                  <div className="text-xs text-slate-500 mt-1">Applied on {new Date(app.applied_at).toLocaleDateString()}</div>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  {resumeHref && (
                    <a href={resumeHref} target="_blank" rel="noreferrer">
                      <Button variant="secondary">View Resume</Button>
                    </a>
                  )}
                  {/* Placeholder actions for future: shortlist, reject */}
                  <DisabledButton variant="ghost">Shortlist</DisabledButton>
                </div>
              </div>
            </Card>
          );
        })}
        {!loading && !error && filtered.length === 0 && (
          <Card className="p-6 text-center text-slate-600">No applications.</Card>
        )}
      </div>
    </div>
  );
};

export default EmployerApplicationsPage;

import React, { useMemo, useState } from 'react';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';

interface ApplicationItem {
  id: number;
  job_title: string;
  company_name: string;
  location: string;
  applied_at: string; // ISO date
  status: 'In Review' | 'Interview' | 'Rejected' | 'Offer' | 'Hired';
}

const statusColors: Record<ApplicationItem['status'], string> = {
  'In Review': 'bg-amber-100 text-amber-800 ring-amber-200',
  'Interview': 'bg-indigo-100 text-indigo-800 ring-indigo-200',
  'Rejected': 'bg-rose-100 text-rose-800 ring-rose-200',
  'Offer': 'bg-emerald-100 text-emerald-800 ring-emerald-200',
  'Hired': 'bg-cyan-100 text-cyan-800 ring-cyan-200',
};

const SubmittedApplicationsPage: React.FC = () => {
  // Placeholder demo data to match UI while backend integration is pending
  const [items] = useState<ApplicationItem[]>([
    { id: 1, job_title: 'Software Engineer', company_name: 'Acme Corp', location: 'Sydney, NSW', applied_at: '2025-08-10', status: 'In Review' },
    { id: 2, job_title: 'Data Analyst', company_name: 'Bluewave', location: 'Melbourne, VIC', applied_at: '2025-08-05', status: 'Interview' },
    { id: 3, job_title: 'Product Manager', company_name: 'Nimbus', location: 'Remote', applied_at: '2025-07-28', status: 'Rejected' },
    { id: 4, job_title: 'Frontend Developer', company_name: 'Orbit Labs', location: 'Brisbane, QLD', applied_at: '2025-08-15', status: 'In Review' },
    { id: 5, job_title: 'QA Engineer', company_name: 'Pioneer', location: 'Adelaide, SA', applied_at: '2025-08-01', status: 'Offer' },
  ]);

  const tabs: Array<{ key: 'All' | ApplicationItem['status']; label: string }> = [
    { key: 'All', label: 'All' },
    { key: 'In Review', label: 'In Review' },
    { key: 'Interview', label: 'Interview' },
    { key: 'Offer', label: 'Offer' },
    { key: 'Hired', label: 'Hired' },
    { key: 'Rejected', label: 'Rejected' },
  ];

  const [active, setActive] = useState<typeof tabs[number]['key']>('All');

  const filtered = useMemo(() => {
    if (active === 'All') return items;
    return items.filter((it) => it.status === active);
  }, [items, active]);

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-2xl md:text-3xl font-bold text-slate-900 mb-2">Submitted Applications</h1>
      <p className="text-slate-600 mb-6">Track your applications and their latest status.</p>

      {/* Filters */}
      <div className="flex flex-wrap gap-2 mb-6">
        {tabs.map((t) => (
          <button
            key={t.key}
            onClick={() => setActive(t.key)}
            className={`px-3 py-1.5 rounded-full text-sm font-medium border transition-colors ${
              active === t.key
                ? 'bg-primary-600 border-primary-600 text-white'
                : 'bg-white border-slate-300 text-slate-700 hover:bg-slate-50'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* List */}
      <div className="space-y-3">
        {filtered.map((app) => (
          <Card key={app.id} className="p-4">
            <div className="flex items-start justify-between gap-4">
              <div className="min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <h2 className="text-base md:text-lg font-semibold text-slate-900 truncate">{app.job_title}</h2>
                  <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium ring-1 ring-inset ${statusColors[app.status]}`}>
                    {app.status}
                  </span>
                </div>
                <div className="text-sm text-slate-600 mt-1 truncate">
                  {app.company_name} • {app.location}
                </div>
                <div className="text-xs text-slate-500 mt-1">Applied on {new Date(app.applied_at).toLocaleDateString()}</div>
              </div>
              <div className="flex items-center gap-2 shrink-0">
                <Button variant="secondary">View Job</Button>
                <Button variant="ghost" disabled>Withdraw</Button>
              </div>
            </div>
          </Card>
        ))}
        {filtered.length === 0 && (
          <Card className="p-6 text-center text-slate-600">No applications in this filter.</Card>
        )}
      </div>
    </div>
  );
};

export default SubmittedApplicationsPage;

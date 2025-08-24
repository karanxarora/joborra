import React from 'react';
import { MapPin, ShieldCheck, GraduationCap, DollarSign, Clock, Building2, Bookmark } from 'lucide-react';
import Card from '../ui/Card';
import Button from '../ui/Button';
import { Job } from '../../types';

interface JobCardProps {
  job: Job;
  selected?: boolean;
  onClick?: () => void;
  isSaved?: boolean;
  onToggleSave?: () => void;
  saving?: boolean;
}

const badgeBase = 'inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-medium';

const JobCard: React.FC<JobCardProps> = ({ job, selected, onClick, isSaved, onToggleSave, saving }) => {
  const snippet = React.useMemo(() => {
    const raw = (job.description || '').replace(/\r\n/g, '\n');
    const lines = raw.split('\n')
      .map(l => l.trim())
      .filter(l => !!l)
      .map(l => l.replace(/^[-*•]\s+/, ''));
    const first = lines[0] || '';
    // Trim overly long first line but keep sentence boundary if possible
    if (first.length > 220) {
      const cut = first.slice(0, 220);
      const lastPeriod = cut.lastIndexOf('.');
      return (lastPeriod > 80 ? cut.slice(0, lastPeriod + 1) : cut) + (cut.length < first.length ? '…' : '');
    }
    return first;
  }, [job.description]);
  return (
    <Card
      className={`relative cursor-pointer border rounded-xl transition-all duration-200
        ${selected
          ? 'bg-cyan-50 border-2 border-cyan-300 shadow-md'
          : 'bg-white border-gray-100 shadow-sm hover:shadow-md hover:-translate-y-[1px]'}
      `}
      padding="sm"
    >
      <div className="flex gap-3" onClick={onClick}>
        {/* Company avatar/logo placeholder */}
        <div className="h-12 w-12 rounded-lg bg-gray-100 flex items-center justify-center text-gray-500">
          <Building2 className="h-5 w-5" />
        </div>

        <div className="flex-1 min-w-0">
          {/* Title and company */}
          <div className="flex items-start justify-between gap-2">
            <div className="min-w-0">
              <h3 className="text-[15px] font-semibold text-gray-900 truncate">{job.title}</h3>
              <div className="text-[13px] text-cyan-600 font-medium truncate">{job.company.name}</div>
            </div>
          </div>

          {/* Location and meta */}
          <div className="mt-1 flex flex-wrap items-center gap-x-3 gap-y-1 text-[12px] text-gray-600">
            <span className="inline-flex items-center"><MapPin className="h-3.5 w-3.5 mr-1" />{job.location}</span>
            {job.employment_type && <span className="inline-flex items-center"><Clock className="h-3.5 w-3.5 mr-1" />{job.employment_type}</span>}
          </div>

          {/* Badges */}
          <div className="mt-2 flex flex-wrap gap-2">
            {/* New tag (mock: show for recently scraped) */}
            <span className={`${badgeBase} bg-cyan-100 text-cyan-700`}>New</span>

            {job.visa_sponsorship && (
              <span className={`${badgeBase} bg-cyan-100 text-cyan-700`}>
                <ShieldCheck className="h-3 w-3" /> Visa Friendly
              </span>
            )}

            <span className={`${badgeBase} bg-cyan-100 text-cyan-700`}>
              <GraduationCap className="h-3 w-3" /> Subclass 500 (Student Visa)
            </span>

            {typeof job.salary_min === 'number' && typeof job.salary_max === 'number' && (
              <span className={`${badgeBase} bg-slate-100 text-slate-700`}>
                <DollarSign className="h-3 w-3" /> ${Math.round(job.salary_min/1000)}k - ${Math.round(job.salary_max/1000)}k
              </span>
            )}
          </div>

          {/* Snippet */}
          <p className="mt-2 text-[13.5px] text-gray-700 leading-relaxed line-clamp-2">{snippet}</p>
        </div>
      </div>

      {/* Footer meta removed: no date on compact card */}

      {/* Floating bookmark control */}
      {onToggleSave && (
        <button
          type="button"
          aria-label={isSaved ? 'Saved' : 'Save'}
          className={`absolute right-3 bottom-3 inline-flex items-center justify-center h-8 w-8 rounded-full border transition-colors
            ${saving ? 'opacity-60 cursor-not-allowed' : 'hover:bg-slate-50'}
            ${isSaved ? 'border-cyan-200 bg-white' : 'border-slate-200 bg-white'}`}
          onClick={(e) => { e.stopPropagation(); if (!saving && onToggleSave) onToggleSave(); }}
          disabled={!!saving}
        >
          <Bookmark
            className={isSaved ? 'h-4 w-4 text-cyan-600 fill-current' : 'h-4 w-4 text-slate-600'}
          />
        </button>
      )}
    </Card>
  );
};

export default JobCard;

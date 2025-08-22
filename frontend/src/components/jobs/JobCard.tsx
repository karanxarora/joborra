import React from 'react';
import { MapPin, ShieldCheck, GraduationCap, DollarSign, Clock, Building2, Globe2 } from 'lucide-react';
import Card from '../ui/Card';
import Button from '../ui/Button';
import { Job } from '../../types';

interface JobCardProps {
  job: Job;
  selected?: boolean;
  onClick?: () => void;
}

const badgeBase = 'inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-medium';

const JobCard: React.FC<JobCardProps> = ({ job, selected, onClick }) => {
  return (
    <Card
      className={`cursor-pointer border ${selected ? 'ring-2 ring-cyan-500 border-cyan-100' : 'border-gray-100'} rounded-xl shadow-sm hover:shadow-md transition-all duration-200 hover:-translate-y-[1px] bg-white`}
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
            {job.source_website && <span className="inline-flex items-center"><Globe2 className="h-3.5 w-3.5 mr-1" />{job.source_website}</span>}
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
          <p className="mt-3 text-[13.5px] text-gray-700 leading-relaxed line-clamp-3">{job.description}</p>
        </div>
      </div>

      {/* Footer actions */}
      <div className="mt-4 flex items-center justify-between">
        <div className="text-[11px] text-gray-500">{new Date(job.created_at || job.scraped_at).toLocaleDateString()}</div>
        <div className="flex gap-2">
          <a href={job.source_url} target="_blank" rel="noopener noreferrer">
            <Button size="sm">Apply</Button>
          </a>
        </div>
      </div>
    </Card>
  );
};

export default JobCard;

import React, { useState } from 'react';
import Button from '../../components/ui/Button';

interface Props {
  onSearch?: (what: string, where: string) => void;
}

const SearchBar: React.FC<Props> = ({ onSearch }) => {
  const [what, setWhat] = useState('');
  const [where, setWhere] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch?.(what, where);
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-sm border border-slate-200 p-3 flex items-stretch gap-3">
      <div className="flex-1">
        <label className="block text-xs font-medium text-slate-500 mb-1">What</label>
        <input
          type="text"
          value={what}
          onChange={(e) => setWhat(e.target.value)}
          placeholder="e.g. Cafe Assistant, Software Intern"
          className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
        />
      </div>
      <div className="flex-1">
        <label className="block text-xs font-medium text-slate-500 mb-1">Where</label>
        <input
          type="text"
          value={where}
          onChange={(e) => setWhere(e.target.value)}
          placeholder="e.g. Sydney, Melbourne"
          className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
        />
      </div>
      <div className="flex items-end">
        <Button type="submit" className="px-6">Search</Button>
      </div>
    </form>
  );
};

export default SearchBar;

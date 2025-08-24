import React, { useState } from 'react';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import JobCard from '../components/jobs/JobCard';
import { useFavorites } from '../contexts/FavoritesContext';
import { useToast } from '../contexts/ToastContext';

const SavedJobsPage: React.FC = () => {
  const { favorites, loading, remove } = useFavorites();
  const { toast } = useToast();
  const [saving, setSaving] = useState<Record<number, boolean>>({});

  const unsave = async (favoriteId: number) => {
    setSaving((prev) => ({ ...prev, [favoriteId]: true }));
    try {
      const ok = await remove(favoriteId);
      if (ok) toast('Removed from Saved', 'success'); else toast('Failed to remove', 'error');
    } finally {
      setSaving((prev) => ({ ...prev, [favoriteId]: false }));
    }
  };

  return (
    <div className="min-h-screen bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6 text-center">
          <h1 className="text-2xl md:text-3xl font-bold text-slate-900">My Saved Jobs</h1>
          <p className="text-slate-600 mt-1">Jobs you've saved to review later</p>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-600 mx-auto"></div>
            <p className="text-gray-600 mt-4">Loading your saved jobs...</p>
          </div>
        ) : favorites.length === 0 ? (
          <Card className="text-center py-12">
            <p className="text-slate-700 mb-4">You haven't saved any jobs yet.</p>
            <a href="/jobs">
              <Button>Browse Jobs</Button>
            </a>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {favorites.map((fav) => (
              <JobCard
                key={fav.id}
                job={fav.job}
                isSaved={true}
                onToggleSave={() => unsave(fav.id)}
                saving={!!saving[fav.id]}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default SavedJobsPage;

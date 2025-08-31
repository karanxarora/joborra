import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { JobDraft } from '../types';
import apiService from '../services/api';
import Button from '../components/ui/Button';
import Card from '../components/ui/Card';
import { Edit, Trash2, Eye, Calendar, MapPin, DollarSign } from 'lucide-react';
import { useToast } from '../contexts/ToastContext';

const JobDraftsPage: React.FC = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [drafts, setDrafts] = useState<JobDraft[]>([]);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState<number | null>(null);

  const loadDrafts = useCallback(async () => {
    try {
      setLoading(true);
      const data = await apiService.getJobDrafts();
      setDrafts(data);
    } catch (error) {
      console.error('Failed to load drafts:', error);
      toast('Failed to load job drafts', 'error');
    } finally {
      setLoading(false);
    }
  }, [toast]);

  useEffect(() => {
    loadDrafts();
  }, [loadDrafts]);

  const handleDeleteDraft = async (draftId: number) => {
    if (!window.confirm('Are you sure you want to delete this draft? This action cannot be undone.')) {
      return;
    }

    try {
      setDeleting(draftId);
      await apiService.deleteJobDraft(draftId);
      setDrafts(drafts.filter(draft => draft.id !== draftId));
      toast('Draft deleted successfully', 'success');
    } catch (error) {
      console.error('Failed to delete draft:', error);
      toast('Failed to delete draft', 'error');
    } finally {
      setDeleting(null);
    }
  };

  const handlePublishDraft = async (draftId: number) => {
    try {
      await apiService.publishJobDraft(draftId);
      setDrafts(drafts.filter(draft => draft.id !== draftId));
      toast('Job published successfully!', 'success');
      navigate('/employer/dashboard');
    } catch (error) {
      console.error('Failed to publish draft:', error);
      toast('Failed to publish job', 'error');
    }
  };

  const handleEditDraft = (draftId: number) => {
    navigate(`/employer/post-job?draft=${draftId}`);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-AU', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStepName = (step: number) => {
    const steps = ['Basics', 'Requirements', 'Compensation', 'Options', 'Review & Publish'];
    return steps[step] || 'Unknown';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading job drafts...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Job Drafts</h1>
              <p className="mt-2 text-gray-600">
                Manage your saved job postings and continue editing them.
              </p>
            </div>
            <Button
              onClick={() => navigate('/employer/post-job')}
              className="bg-cyan-600 hover:bg-cyan-700"
            >
              Create New Job
            </Button>
          </div>
        </div>

        {/* Drafts List */}
        {drafts.length === 0 ? (
          <Card className="p-12 text-center">
            <div className="mx-auto w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mb-6">
              <Edit className="w-12 h-12 text-gray-400" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No job drafts yet</h3>
            <p className="text-gray-600 mb-6">
              Start creating a job posting and save it as a draft to see it here.
            </p>
            <Button
              onClick={() => navigate('/employer/post-job')}
              className="bg-cyan-600 hover:bg-cyan-700"
            >
              Create Your First Job
            </Button>
          </Card>
        ) : (
          <div className="grid gap-6">
            {drafts.map((draft) => (
              <Card key={draft.id} className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-3">
                      <h3 className="text-xl font-semibold text-gray-900">{draft.title}</h3>
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-cyan-100 text-cyan-800">
                        Step {draft.step + 1}: {getStepName(draft.step)}
                      </span>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                      {draft.location && (
                        <div className="flex items-center text-sm text-gray-600">
                          <MapPin className="w-4 h-4 mr-2" />
                          {draft.location}
                        </div>
                      )}
                      {draft.employment_type && (
                        <div className="flex items-center text-sm text-gray-600">
                          <Calendar className="w-4 h-4 mr-2" />
                          {draft.employment_type}
                        </div>
                      )}
                      {draft.salary && (
                        <div className="flex items-center text-sm text-gray-600">
                          <DollarSign className="w-4 h-4 mr-2" />
                          {draft.salary}
                        </div>
                      )}
                    </div>

                    {draft.description && (
                      <p className="text-gray-600 text-sm mb-4 line-clamp-2">
                        {draft.description}
                      </p>
                    )}

                    <div className="flex items-center text-xs text-gray-500">
                      <span>Created: {formatDate(draft.created_at)}</span>
                      {draft.updated_at && draft.updated_at !== draft.created_at && (
                        <span className="ml-4">Updated: {formatDate(draft.updated_at)}</span>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center gap-2 ml-6">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleEditDraft(draft.id)}
                      className="flex items-center gap-2"
                    >
                      <Edit className="w-4 h-4" />
                      Edit
                    </Button>
                    
                    <Button
                      size="sm"
                      onClick={() => handlePublishDraft(draft.id)}
                      className="bg-cyan-600 hover:bg-cyan-700 flex items-center gap-2"
                    >
                      <Eye className="w-4 h-4" />
                      Publish
                    </Button>
                    
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDeleteDraft(draft.id)}
                      disabled={deleting === draft.id}
                      className="text-red-600 border-red-300 hover:bg-red-50 flex items-center gap-2"
                    >
                      <Trash2 className="w-4 h-4" />
                      {deleting === draft.id ? 'Deleting...' : 'Delete'}
                    </Button>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default JobDraftsPage;

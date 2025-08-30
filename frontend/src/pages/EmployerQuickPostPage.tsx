import React, { useMemo, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import apiService from '../services/api';
import Button from '../components/ui/Button';
import Card from '../components/ui/Card';
import Input from '../components/ui/Input';

const EmployerQuickPostPage: React.FC = () => {
  const navigate = useNavigate();

  const [title, setTitle] = useState('');
  const [location, setLocation] = useState('');
  const [employmentType, setEmploymentType] = useState('Casual');
  const [payText, setPayText] = useState('');
  const [studentFriendly, setStudentFriendly] = useState(true);
  const [visaSponsorship, setVisaSponsorship] = useState(false);
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const descRef = useRef<HTMLTextAreaElement | null>(null);

  const canPublish = useMemo(() => {
    return title.trim().length >= 5 && description.trim().length >= 20;
  }, [title, description]);

  const onAIGenerate = async () => {
    setError(null);
    const sysPrompt = `You are an expert HR copywriter. Write a concise, friendly, student‑inclusive job description.

Constraints:
- 160–260 words.
- Use Australian spelling.
- Plain text paragraphs and short bullet lists only; no markdown headers.
- Emphasise international student friendliness and legal work constraints if applicable.

Job context:
- Title: ${title || 'N/A'}
- Location: ${location || 'N/A'}
- Employment type: ${employmentType || 'N/A'}
- Pay text: ${payText || 'N/A'}
- International student friendly: ${studentFriendly ? 'Yes' : 'No'}
- Visa sponsorship available: ${visaSponsorship ? 'Yes' : 'No'}

Output sections (no labels needed):
1) 2–3 sentence overview of the role and team.
2) 4–6 bullet points of day‑to‑day responsibilities.
3) 3–5 bullet points of what you’re looking for (soft skills welcomed).`;

    const draft = await apiService.generateJobDescription({
      title,
      skills: [],
      prompt: sysPrompt,
      model: 'gemini-1.5-flash',
      context: {
        title,
        location,
        employment_type: employmentType,
        salary: payText,
        international_student_friendly: studentFriendly,
        visa_sponsorship: visaSponsorship,
      },
    });
    setDescription(draft);
    if (descRef.current) descRef.current.value = draft;
  };

  const onPublish = async () => {
    setError(null);
    setSuccess(null);
    if (!canPublish) {
      setError('Please add a clear title (>= 5 chars) and a description (>= 20 chars).');
      return;
    }
    setLoading(true);
    try {
      await apiService.createEmployerJob({
        title: title.trim(),
        description,
        location: location || undefined,
        employment_type: employmentType,
        salary: payText || undefined,
        international_student_friendly: studentFriendly,
        visa_sponsorship: visaSponsorship,
        experience_level: 'entry',
      });
      setSuccess('Job published! Redirecting…');
      setTimeout(() => navigate('/profile'), 900);
    } catch (e: any) {
      const msg = e?.response?.data?.detail || e?.message || 'Failed to publish job';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-6">
        <h1 className="text-2xl md:text-3xl font-bold text-slate-900">Post a Job in 60 seconds</h1>
        <p className="text-slate-600 text-sm mt-1">Minimal fields. You can refine later.</p>
      </div>

      {error && (
        <div className="p-3 rounded border border-amber-300 bg-amber-50 text-amber-900 text-sm mb-4">{error}</div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Form */}
        <div className="lg:col-span-7">
          <Card className="p-6 space-y-5">
            <Input
              label="Job title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g., Retail Assistant (Casual)"
              required
            />

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Employment Type</label>
                <select
                  className="w-full rounded-md border border-gray-300 p-2 focus:ring-cyan-500 focus:border-cyan-500"
                  value={employmentType}
                  onChange={(e) => setEmploymentType(e.target.value)}
                >
                  <option>Casual</option>
                  <option>Part-time</option>
                  <option>Full-time</option>
                  <option>Contract</option>
                  <option>Internship</option>
                </select>
              </div>
              <Input
                label="Location"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                placeholder="e.g., Newcastle, NSW"
              />
            </div>

            <Input
              label="Pay (text)"
              value={payText}
              onChange={(e) => setPayText(e.target.value)}
              placeholder="e.g., $29.50/hr + penalties"
            />

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">About the job</label>
              <div className="flex gap-2 mb-2">
                <Button type="button" variant="outline" onClick={onAIGenerate}>Auto-generate</Button>
              </div>
              <textarea
                ref={descRef}
                className="w-full rounded-md border border-gray-300 p-2 min-h-[180px] focus:outline-none"
                placeholder="Describe the role, team, and what success looks like…"
                onChange={(e) => setDescription(e.target.value)}
                defaultValue={description}
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="flex items-center gap-2">
                <input
                  id="studentFriendly"
                  type="checkbox"
                  className="rounded border-gray-300 text-cyan-600 focus:ring-cyan-500"
                  checked={studentFriendly}
                  onChange={(e) => setStudentFriendly(e.target.checked)}
                />
                <label htmlFor="studentFriendly" className="text-sm text-gray-700">International Student Friendly</label>
              </div>
              <div className="flex items-center gap-2">
                <input
                  id="visaSponsor"
                  type="checkbox"
                  className="rounded border-gray-300 text-cyan-600 focus:ring-cyan-500"
                  checked={visaSponsorship}
                  onChange={(e) => setVisaSponsorship(e.target.checked)}
                />
                <label htmlFor="visaSponsor" className="text-sm text-gray-700">Visa Sponsorship</label>
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <Button type="button" variant="outline" onClick={() => navigate('/jobs')}>Cancel</Button>
              <Button type="button" onClick={onPublish} disabled={loading || !canPublish}>
                {loading ? 'Publishing…' : 'Publish'}
              </Button>
            </div>
          </Card>
        </div>

        {/* Live Preview */}
        <div className="lg:col-span-5">
          <div className="lg:sticky lg:top-6">
            <Card className="p-6">
              <div className="text-sm text-slate-600 mb-2">Live Preview</div>
              <div className="text-lg font-semibold text-slate-900">{title || 'Job title'}</div>
              <div className="text-slate-700">Your company</div>
              <div className="mt-1 text-sm text-slate-600">{location || 'Location'}</div>
              <div className="mt-1 text-xs text-slate-600">{employmentType || '—'} • {payText || 'Pay —'}</div>
              <div className="mt-3 text-sm text-slate-700 whitespace-pre-wrap">
                {description || 'Add a short description to attract candidates.'}
              </div>
              <div className="mt-4 text-xs text-slate-600">
                {studentFriendly ? 'International-student friendly.' : ''} {visaSponsorship ? 'Visa sponsorship available.' : ''}
              </div>
            </Card>
          </div>
        </div>
      </div>

      
      {success && (
        <div className="mt-6">
          <Card className="p-6">
            <div className="text-green-700 font-medium">{success}</div>
            <div className="text-sm text-slate-600 mt-1">We are redirecting you…</div>
          </Card>
        </div>
      )}
    </div>
  );
};

export default EmployerQuickPostPage;

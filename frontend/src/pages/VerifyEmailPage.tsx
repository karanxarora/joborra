// Email verification page - DISABLED FOR NOW
/*
import React, { useEffect, useState } from 'react';
import { useSearchParams, Link, useNavigate } from 'react-router-dom';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import apiService from '../services/api';
import { useToast } from '../contexts/ToastContext';
import { extractErrorMessage } from '../utils/errorUtils';

const VerifyEmailPage: React.FC = () => {
  const [params] = useSearchParams();
  const token = params.get('token') || '';
  const [status, setStatus] = useState<'idle' | 'verifying' | 'success' | 'error'>('idle');
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const { toast } = useToast();

  useEffect(() => {
    const verify = async () => {
      if (!token) return;
      setStatus('verifying');
      setError(null);
      try {
        await apiService.confirmEmailVerification(token);
        setStatus('success');
        toast('Email verified successfully. Welcome!', 'success');
        setTimeout(() => navigate('/profile'), 1200);
      } catch (e: any) {
        setStatus('error');
        const msg = e?.response?.data?.detail || 'Verification failed or token expired.';
        setError(msg);
        toast(msg, 'error');
      }
    };
    verify();
  }, [token, navigate, toast]);

  return (
    <div className="min-h-screen">
      <div className="max-w-lg mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <Card className="p-6 text-center">
          <h1 className="text-1xl font-bold text-slate-900 mb-2">Verify your email</h1>
          {status === 'idle' && (
            <p className="text-slate-600">Waiting for token...</p>
          )}
          {status === 'verifying' && (
            <p className="text-slate-600">Verifying your email...</p>
          )}
          {status === 'success' && (
            <div>
              <p className="text-slate-700 mb-4">Your email has been verified.</p>
              <Link to="/profile"><Button>Go to Profile</Button></Link>
            </div>
          )}
          {status === 'error' && (
            <div>
              <p className="text-red-600 mb-4">{extractErrorMessage(error)}</p>
              <Link to="/profile"><Button variant="outline">Back to Profile</Button></Link>
            </div>
          )}
        </Card>
      </div>
    </div>
  );
};

export default VerifyEmailPage;
*/

// Empty export to make this a module
export {};

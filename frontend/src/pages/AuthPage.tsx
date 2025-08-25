import React, { useEffect, useMemo, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Mail, Lock, User, Building, GraduationCap, Calendar } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import Card from '../components/ui/Card';
import { LoginForm, RegisterForm } from '../types';
import { AU_UNIVERSITIES } from '../constants/universities';
import { DEGREES } from '../constants/degrees';
import { useToast } from '../contexts/ToastContext';
import apiService from '../services/api';

const AuthPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'login' | 'register'>('login');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { login, register } = useAuth();
  const navigate = useNavigate();
  const { toast } = useToast();

  const [loginForm, setLoginForm] = useState<LoginForm>({
    email: '',
    password: '',
  });

  // Local-only field (not sent to backend yet)
  const [dob, setDob] = useState<string>('');

  const [registerForm, setRegisterForm] = useState<RegisterForm>({
    email: '',
    password: '',
    full_name: '',
    role: 'student',
    university: '',
    degree: '',
    graduation_year: undefined,
    visa_status: '',
  });

  const visaOptions = useMemo(() => [
    'Student Visa (500)',
    'Temporary Graduate (485)',
    'Skilled Independent (189)',
    'Skilled Nominated (190)',
    'Skilled Work Regional (491)',
    'Employer Sponsored TSS (482)',
    'Employer Nomination (186)',
    'Working Holiday (417/462)',
    'Other/Not Sure',
  ], []);

  const gradYears = useMemo(() => {
    const current = new Date().getFullYear();
    const years: number[] = [];
    for (let y = current - 10; y <= current + 6; y++) years.push(y);
    return years;
  }, []);

  // Handle OAuth redirect tokens (?oauth=success&access_token=...)
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get('oauth') === 'success' && params.get('access_token')) {
      const access = params.get('access_token')!;
      const refresh = params.get('refresh_token') || '';
      localStorage.setItem('token', access);
      if (refresh) localStorage.setItem('refresh_token', refresh);
      // Clean URL
      window.history.replaceState({}, document.title, window.location.pathname);
      // Fetch user and finalize login
      (async () => {
        try {
          const me = await apiService.getCurrentUser();
          localStorage.setItem('user', JSON.stringify(me));
          toast('Signed in with Google', 'success');
          navigate('/');
        } catch (e) {
          setError('Failed to complete Google sign-in');
        }
      })();
    }
  }, [navigate, toast]);

  // Google Identity Services sign-in (ID token flow)
  const [googleLoading, setGoogleLoading] = useState(false);
  const ensureGoogleScript = (): Promise<void> => {
    return new Promise((resolve, reject) => {
      if ((window as any).google?.accounts?.id) return resolve();
      const existing = document.getElementById('google-identity-services');
      if (existing) {
        existing.addEventListener('load', () => resolve());
        return;
      }
      const script = document.createElement('script');
      script.src = 'https://accounts.google.com/gsi/client';
      script.async = true;
      script.defer = true;
      script.id = 'google-identity-services';
      script.onload = () => resolve();
      script.onerror = () => reject(new Error('Failed to load Google Identity Services'));
      document.head.appendChild(script);
    });
  };

  const onGoogleSignIn = async () => {
    setError(null);
    setGoogleLoading(true);
    try {
      await ensureGoogleScript();
      const google: any = (window as any).google;
      const clientId = (process as any).env.REACT_APP_GOOGLE_CLIENT_ID || (window as any).REACT_APP_GOOGLE_CLIENT_ID;
      if (!clientId) throw new Error('Google Client ID not configured');

      let settled = false;
      await new Promise<void>((resolve, reject) => {
        try {
          google.accounts.id.initialize({
            client_id: clientId,
            callback: async (resp: any) => {
              if (settled) return;
              settled = true;
              const id_token = resp?.credential;
              if (!id_token) {
                reject(new Error('No ID token received'));
                return;
              }
              try {
                await apiService.googleLoginWithIdToken(id_token);
                toast('Signed in with Google', 'success');
                navigate('/');
                resolve();
              } catch (err: any) {
                const detail = err?.response?.data?.detail || '';
                if (detail === 'link_required' || /link_required/i.test(detail)) {
                  toast('An account with this email exists. Sign in with password, then link Google in Profile.', 'error');
                } else if (detail) {
                  toast(detail, 'error');
                } else {
                  toast('Google sign-in failed', 'error');
                }
                reject(err);
              }
            },
            auto_select: false,
            cancel_on_tap_outside: true,
            context: 'signin',
          });
          // Trigger a prompt; if not displayed, render a fallback button moment
          google.accounts.id.prompt((notification: any) => {
            if (notification.isNotDisplayed() || notification.isSkippedMoment()) {
              const container = document.createElement('div');
              document.body.appendChild(container);
              google.accounts.id.renderButton(container, { theme: 'outline', size: 'large' });
            }
          });
        } catch (e) {
          reject(e);
        }
      });
    } catch (e: any) {
      if (e?.message) setError(e.message);
    } finally {
      setGoogleLoading(false);
    }
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await login(loginForm);
      toast('Successfully logged in', 'success');
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await register(registerForm);
      // Request verification email automatically (best-effort)
      try {
        const res: any = await apiService.requestEmailVerification();
        if (res && (res as any).email_sent) {
          toast('Account created. Verification email sent. Please check your inbox.', 'success', 6000);
        } else if (res && (res as any).verify_url) {
          toast('Account created. Copy the verification link shown in your profile to verify.', 'info', 6000);
        } else {
          toast('Account created. Please request a verification link from your Profile.', 'info', 6000);
        }
      } catch (ve: any) {
        const code = ve?.response?.status;
        if (code === 429) {
          toast('Account created. Please wait a moment before requesting verification again.', 'info', 6000);
        } else {
          toast('Account created. Please verify your email to unlock all features.', 'info', 6000);
        }
      }
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-lg w-full space-y-8">
        {/* Header */}
        <div className="text-center">
          <div className="mb-8">
            <h1 className="text-4xl font-bold tracking-tight text-slate-900 mb-2">Joborra</h1>
            <p className="text-base text-slate-600 font-normal">
              🇦🇺 Your Gateway to Australian Career Success
            </p>
            <p className="text-sm text-slate-500 mt-2">
              Join 10,000+ international students who found their dream jobs
            </p>
          </div>
        </div>

        <Card className="p-8">
          {/* OAuth quick sign-in (GIS ID token flow) */}
          <div className="mb-6">
            <Button
              type="button"
              variant="outline"
              className="w-full"
              onClick={onGoogleSignIn}
              loading={googleLoading}
            >
              Continue with Google
            </Button>
            <div className="flex items-center my-6">
              <div className="flex-1 h-px bg-slate-200" />
              <span className="px-3 text-xs uppercase tracking-wide text-slate-500">or</span>
              <div className="flex-1 h-px bg-slate-200" />
            </div>
          </div>
          {/* Tab Navigation */}
          <div className="flex space-x-2 bg-slate-100 p-1 rounded-xl mb-8">
            <button
              onClick={() => setActiveTab('login')}
              className={`w-1/2 py-3 px-4 text-center rounded-lg font-medium text-sm transition-colors ${
                activeTab === 'login'
                  ? 'bg-white text-primary-700'
                  : 'text-slate-600 hover:text-slate-800'
              }`}
            >
              Welcome Back
            </button>
            <button
              onClick={() => setActiveTab('register')}
              className={`w-1/2 py-3 px-4 text-center rounded-lg font-medium text-sm transition-colors ${
                activeTab === 'register'
                  ? 'bg-white text-primary-700'
                  : 'text-slate-600 hover:text-slate-800'
              }`}
            >
              Join Joborra
            </button>
          </div>

          {/* Error Display */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
              <div className="flex items-center">
                <span className="text-red-500 mr-2">⚠️</span>
                <span className="font-medium">{error}</span>
              </div>
            </div>
          )}

          {/* Login Form */}
          {activeTab === 'login' && (
            <form
              onSubmit={handleLogin}
              className="space-y-6"
            >
              <div>
                <Input
                  label="Email"
                  type="email"
                  value={loginForm.email}
                  onChange={(e) => setLoginForm({ ...loginForm, email: e.target.value })}
                  icon={<Mail className="h-4 w-4" />}
                  required
                />
              </div>
              <div>
                <Input
                  label="Password"
                  type="password"
                  value={loginForm.password}
                  onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })}
                  icon={<Lock className="h-4 w-4" />}
                  required
                />
              </div>
              <Button
                type="submit"
                loading={loading}
                className="w-full"
                size="lg"
              >
                Sign In
              </Button>
            </form>
          )}

          {/* Register Form */}
          {activeTab === 'register' && (
            <form
              onSubmit={handleRegister}
              className="space-y-6"
            >
              <div className="grid grid-cols-1 gap-4">
                <Input
                  label="Full Name"
                  value={registerForm.full_name}
                  onChange={(e) => setRegisterForm({ ...registerForm, full_name: e.target.value })}
                  icon={<User className="h-4 w-4" />}
                  required
                />
                <Input
                  label="Email"
                  type="email"
                  value={registerForm.email}
                  onChange={(e) => setRegisterForm({ ...registerForm, email: e.target.value })}
                  icon={<Mail className="h-4 w-4" />}
                  required
                />
                <Input
                  label="Password"
                  type="password"
                  value={registerForm.password}
                  onChange={(e) => setRegisterForm({ ...registerForm, password: e.target.value })}
                  icon={<Lock className="h-4 w-4" />}
                  helperText="Minimum 8 characters"
                  required
                />
              </div>

              {/* Role Selection */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  I am a
                </label>
                <div className="grid grid-cols-2 gap-3">
                  <button
                    type="button"
                    onClick={() => setRegisterForm({ ...registerForm, role: 'student' })}
                    className={`p-3 border rounded-lg text-sm font-medium transition-colors ${
                      registerForm.role === 'student'
                        ? 'border-primary-500 bg-primary-50 text-primary-700'
                        : 'border-slate-300 hover:border-slate-400'
                    }`}
                  >
                    <GraduationCap className="h-5 w-5 mx-auto mb-1" />
                    Student
                  </button>
                  <button
                    type="button"
                    onClick={() => setRegisterForm({ ...registerForm, role: 'employer' })}
                    className={`p-3 border rounded-lg text-sm font-medium transition-colors ${
                      registerForm.role === 'employer'
                        ? 'border-primary-500 bg-primary-50 text-primary-700'
                        : 'border-slate-300 hover:border-slate-400'
                    }`}
                  >
                    <Building className="h-5 w-5 mx-auto mb-1" />
                    Employer
                  </button>
                </div>
              </div>

              {/* Student-specific fields */}
              {registerForm.role === 'student' && (
                <div
                  
                  
                  className="space-y-6"
                >
                  <Input
                    label="Date of Birth"
                    type="date"
                    value={dob}
                    onChange={(e) => setDob(e.target.value)}
                    helperText="We currently don't store DOB. This is for future profile enhancements."
                  />
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">
                      University
                    </label>
                    <div className="relative">
                      <select
                        value={registerForm.university || ''}
                        onChange={(e) => setRegisterForm({ ...registerForm, university: e.target.value })}
                        className="input-field w-full"
                      >
                        <option value="">Select your university</option>
                        {AU_UNIVERSITIES.map((u) => (
                          <option key={u} value={u}>{u}</option>
                        ))}
                      </select>
                      <GraduationCap className="h-4 w-4 absolute left-3 top-3 text-slate-400 pointer-events-none" />
                    </div>
                  </div>
                  {/* Degree with autocomplete suggestions */}
                  <div>
                    <Input
                      label="Degree/Course"
                      value={registerForm.degree || ''}
                      onChange={(e) => setRegisterForm({ ...registerForm, degree: e.target.value })}
                      list="degree-options"
                    />
                    <datalist id="degree-options">
                      {DEGREES.map((d) => (
                        <option key={d} value={d} />
                      ))}
                    </datalist>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">Graduation Year</label>
                    <div className="relative">
                      <select
                        value={registerForm.graduation_year || ''}
                        onChange={(e) => setRegisterForm({ ...registerForm, graduation_year: e.target.value ? parseInt(e.target.value) : undefined })}
                        className="input-field w-full"
                      >
                        <option value="">Select year</option>
                        {gradYears.map((y) => (
                          <option key={y} value={y}>{y}</option>
                        ))}
                      </select>
                      <Calendar className="h-4 w-4 absolute left-3 top-3 text-slate-400 pointer-events-none" />
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">Visa Type</label>
                    <select
                      value={registerForm.visa_status || ''}
                      onChange={(e) => setRegisterForm({ ...registerForm, visa_status: e.target.value })}
                      className="input-field w-full"
                    >
                      <option value="">Select visa type</option>
                      {visaOptions.map((v) => (
                        <option key={v} value={v}>{v}</option>
                      ))}
                    </select>
                  </div>
                </div>
              )}

              {/* Employer-specific fields */}
              {registerForm.role === 'employer' && (
                <div
                  
                  
                  className="space-y-6"
                >
                  <Input
                    label="Company Name"
                    value={registerForm.company_name || ''}
                    onChange={(e) => setRegisterForm({ ...registerForm, company_name: e.target.value })}
                    icon={<Building className="h-4 w-4" />}
                  />
                  <Input
                    label="Company Website"
                    type="url"
                    value={registerForm.company_website || ''}
                    onChange={(e) => setRegisterForm({ ...registerForm, company_website: e.target.value })}
                  />
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1">
                        Company Size
                      </label>
                      <select
                        value={registerForm.company_size || ''}
                        onChange={(e) => setRegisterForm({ ...registerForm, company_size: e.target.value })}
                        className="input-field"
                      >
                        <option value="">Select size</option>
                        <option value="1-10">1-10 employees</option>
                        <option value="11-50">11-50 employees</option>
                        <option value="51-200">51-200 employees</option>
                        <option value="201-1000">201-1000 employees</option>
                        <option value="1000+">1000+ employees</option>
                      </select>
                    </div>
                    <Input
                      label="Industry"
                      value={registerForm.industry || ''}
                      onChange={(e) => setRegisterForm({ ...registerForm, industry: e.target.value })}
                    />
                  </div>
                </div>
              )}

              <Button
                type="submit"
                loading={loading}
                className="w-full"
                size="lg"
              >
                Create Account
              </Button>
            </form>
          )}
        </Card>

        {/* Footer */}
        <div className="text-center text-sm text-slate-600">
          <p>
            By signing up, you agree to our{' '}
            <Link to="/about" className="text-primary-600 hover:text-primary-500">
              Terms of Service
            </Link>{' '}
            and{' '}
            <Link to="/about" className="text-primary-600 hover:text-primary-500">
              Privacy Policy
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default AuthPage;

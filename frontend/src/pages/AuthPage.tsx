import React, { useEffect, useMemo, useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { Mail, Lock, User, Building, GraduationCap, Calendar, Phone, ExternalLink, MapPin } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import Card from '../components/ui/Card';
import { LoginForm, RegisterForm } from '../types';
import { AU_UNIVERSITIES } from '../constants/universities';
import { AUSTRALIAN_SUBURBS } from '../constants/australianSuburbs';
// import { DEGREES } from '../constants/degrees';
import { useToast } from '../contexts/ToastContext';
import apiService from '../services/api';
import LogoIcon from '../components/ui/LogoIcon';

import { extractErrorMessage } from '../utils/errorUtils';

const AuthPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const [activeTab, setActiveTab] = useState<'login' | 'register'>('login');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { login, register } = useAuth();
  const navigate = useNavigate();
  const { toast } = useToast();

  // Set initial tab based on URL parameter
  useEffect(() => {
    const tab = searchParams.get('tab');
    if (tab === 'register' || tab === 'signup') {
      setActiveTab('register');
    } else if (tab === 'login') {
      setActiveTab('login');
    }
  }, [searchParams]);

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
    contact_number: '',
    role: undefined,
    university: '',
    degree: '',
    graduation_year: undefined,
    visa_status: '',
  });

  // Split name fields (UI-only), keep full_name for backend
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [citySuburb, setCitySuburb] = useState('');
  const [citySuggestions, setCitySuggestions] = useState<string[]>([]);
  const [showCitySuggestions, setShowCitySuggestions] = useState(false);

  const visaOptions = useMemo(() => [
    'Student Visa (subclass 500)',
    'Temporary Graduate (subclass 485)',
    'Skilled Independent (subclass 189)',
    'Skilled Nominated (subclass 190)',
    'Skilled Work Regional (subclass 491)',
    'Employer Sponsored TSS (subclass 482)',
    'Employer Nomination (subclass 186)',
    'Working Holiday (subclass 417/462)',
    'Other/Not Sure',
  ], []);

  const australianSuburbs = AUSTRALIAN_SUBURBS;

  const gradYears = useMemo(() => {
    const current = new Date().getFullYear();
    const years: number[] = [];
    for (let y = current - 10; y <= current + 6; y++) years.push(y);
    return years;
  }, []);

  // Handle city/suburb autocomplete
  const handleCityChange = (value: string) => {
    setCitySuburb(value);
    if (value.length > 1) {
      const filtered = australianSuburbs.filter(suburb =>
        suburb.toLowerCase().includes(value.toLowerCase())
      ).slice(0, 10); // Limit to 10 suggestions
      setCitySuggestions(filtered);
      setShowCitySuggestions(true);
    } else {
      setCitySuggestions([]);
      setShowCitySuggestions(false);
    }
  };

  const selectCity = (city: string) => {
    setCitySuburb(city);
    setShowCitySuggestions(false);
    setCitySuggestions([]);
  };

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
          toast('Signed in successfully', 'success');
          // Redirect based on user role
          if (me.role === 'employer') {
            navigate('/employer/dashboard');
          } else {
            navigate('/profile');
          }
        } catch (e) {
          setError('Failed to complete sign-in');
        }
      })();
    }
  }, [navigate, toast]);



  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await login(loginForm);
      toast('Successfully logged in', 'success');
      // Get user from context after login
      const currentUser = await apiService.getCurrentUser();
      // Redirect based on user role
      if (currentUser.role === 'employer') {
        navigate('/employer/dashboard');
      } else {
        navigate('/profile');
      }
    } catch (err: any) {
      setError(extractErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Build full_name from split fields
      const full_name = `${firstName} ${lastName}`.trim();
      const payload: RegisterForm = { 
        ...registerForm, 
        full_name, 
        city_suburb: citySuburb,
        date_of_birth: dob ? new Date(dob).toISOString() : undefined
      };
      // Normalize company website (allow domain without protocol)
      if (payload.company_website && !/^https?:\/\//i.test(payload.company_website)) {
        payload.company_website = `https://${payload.company_website}`;
      }
      await register(payload);
      // Email verification disabled for now
      // try {
      //   const res: any = await apiService.requestEmailVerification();
      //   if (res && (res as any).email_sent) {
      //     toast('Account created. Verification email sent. Please check your inbox.', 'success', 6000);
      //   } else if (res && (res as any).verify_url) {
      //     toast('Account created. Copy the verification link shown in your profile to verify.', 'info', 6000);
      //   } else {
      //     toast('Account created. Please request a verification link from your Profile.', 'info', 6000);
      //   }
      // } catch (ve: any) {
      //   const code = ve?.response?.status;
      //   if (code === 429) {
      //     toast('Account created. Please wait a moment before requesting verification again.', 'info', 6000);
      //   } else {
      //     // toast('Account created. Please verify your email to unlock all features.', 'info', 6000);  // DISABLED FOR NOW
      //   }
      // }
      if (payload.role === 'employer') {
        navigate('/employer/dashboard');
      } else {
        navigate('/profile');
      }
    } catch (err: any) {
      setError(extractErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-lg w-full space-y-8">
        {/* Header */}
        <div className="text-center">
          <div className="mb-8 flex flex-col items-center">
            <LogoIcon className="h-12 w-12 mb-3" />
            <h1 className="text-4xl font-bold tracking-tight text-slate-900 mb-2">Joborra</h1>
            <p className="text-base text-slate-700 font-semibold">
              1<sup>st</sup> International Students' Job Portal
            </p>
            <p className="text-sm text-slate-600 mt-2">
              Join the Joborra Pilot — Verified jobs for international students. Confident hiring for employers.
            </p>
          </div>
        </div>

        <Card className="p-8">
          {/* Tabs and Forms */}
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
                <span className="font-medium">{extractErrorMessage(error)}</span>
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
              
              {/* Forgot Password Link */}
              <div className="text-right">
                <button
                  type="button"
                  onClick={() => navigate('/forgot-password')}
                  className="text-sm text-blue-600 hover:text-blue-500 transition-colors"
                >
                  Forgot your password?
                </button>
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
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <Input
                    label="First Name"
                    value={firstName}
                    onChange={(e) => {
                      setFirstName(e.target.value);
                      const fn = e.target.value;
                      setRegisterForm((prev) => ({ ...prev, full_name: `${fn} ${lastName}`.trim() }));
                    }}
                    icon={<User className="h-4 w-4" />}
                    required
                  />
                  <Input
                    label="Last Name"
                    value={lastName}
                    onChange={(e) => {
                      setLastName(e.target.value);
                      const ln = e.target.value;
                      setRegisterForm((prev) => ({ ...prev, full_name: `${firstName} ${ln}`.trim() }));
                    }}
                    required
                  />
                </div>
                <Input
                  label="Email"
                  type="email"
                  value={registerForm.email}
                  onChange={(e) => setRegisterForm({ ...registerForm, email: e.target.value })}
                  icon={<Mail className="h-4 w-4" />}
                  required
                />
                <Input
                  label="Contact Number (optional)"
                  type="tel"
                  placeholder="4XX XXX XXX"
                  value={registerForm.contact_number || ''}
                  onChange={(e) => {
                    let value = e.target.value;
                    // Remove any existing +61 prefix and non-digits except spaces
                    value = value.replace(/^\+61\s*/, '').replace(/[^\d\s]/g, '');
                    // Add +61 prefix automatically
                    const formattedNumber = value ? `+61 ${value}` : '';
                    setRegisterForm({ ...registerForm, contact_number: formattedNumber });
                  }}
                  icon={<Phone className="h-4 w-4" />}
                  helperText="Australian mobile number (country code +61 added automatically)"
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

              {/* Role Selection (default none) */}
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
              {/* Student-specific fields (only when role selected as student) */}
              {registerForm.role === 'student' && (
                <div className="space-y-6">
                  <Input
                    label="Date of Birth"
                    type="date"
                    value={dob}
                    onChange={(e) => setDob(e.target.value)}
                    required
                  />
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">
                      University
                    </label>
                    <div className="relative">
                      <select
                        value={registerForm.university || ''}
                        onChange={(e) => setRegisterForm({ ...registerForm, university: e.target.value })}
                        className="input-field w-full pl-10"
                      >
                        <option value="">Select your university</option>
                        {AU_UNIVERSITIES.map((u) => (
                          <option key={u} value={u}>{u}</option>
                        ))}
                      </select>
                      <GraduationCap className="h-4 w-4 absolute left-3 top-3 text-slate-400 pointer-events-none" />
                    </div>
                  </div>
                  
                  {/* City/Suburb field with autocomplete */}
                  <div className="relative">
                    <label className="block text-sm font-medium text-slate-700 mb-2">
                      City/Suburb
                    </label>
                    <div className="relative">
                      <input
                        type="text"
                        value={citySuburb}
                        onChange={(e) => handleCityChange(e.target.value)}
                        onBlur={() => setTimeout(() => setShowCitySuggestions(false), 200)}
                        onFocus={() => citySuburb.length > 1 && setShowCitySuggestions(true)}
                        placeholder="Start typing your city or suburb..."
                        className="input-field w-full pl-10"
                        required
                      />
                      <MapPin className="h-4 w-4 absolute left-3 top-3 text-slate-400 pointer-events-none" />
                      
                      {/* Autocomplete suggestions */}
                      {showCitySuggestions && citySuggestions.length > 0 && (
                        <div className="absolute z-10 w-full mt-1 bg-white border border-slate-200 rounded-md shadow-lg max-h-60 overflow-y-auto">
                          {citySuggestions.map((suggestion, index) => (
                            <div
                              key={index}
                              className="px-4 py-2 hover:bg-slate-50 cursor-pointer text-sm"
                              onClick={() => selectCity(suggestion)}
                            >
                              {suggestion}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                  
                  {/* Degree free text input */}
                  <div>
                    <Input
                      label="Degree/Course"
                      placeholder="e.g., Bachelor of Computer Science, Master of Business Administration"
                      value={registerForm.degree || ''}
                      onChange={(e) => setRegisterForm({ ...registerForm, degree: e.target.value })}
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">Graduation Year</label>
                    <div className="relative">
                      <select
                        value={registerForm.graduation_year || ''}
                        onChange={(e) => setRegisterForm({ ...registerForm, graduation_year: e.target.value ? parseInt(e.target.value) : undefined })}
                        className="input-field w-full pl-10"
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
                    <div className="flex items-center gap-2 mb-2">
                      <label className="block text-sm font-medium text-slate-700">Visa Type</label>
                      <a 
                        href="https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-listing" 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-cyan-600 hover:text-cyan-700 transition-colors"
                        title="Learn about Australian visa types"
                      >
                        <ExternalLink className="h-4 w-4" />
                      </a>
                    </div>
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

              {/* Employer-specific fields (only when role selected as employer) */}
              {registerForm.role === 'employer' && (
                <div className="space-y-6">
                  <Input
                    label="Company Name"
                    value={registerForm.company_name || ''}
                    onChange={(e) => setRegisterForm({ ...registerForm, company_name: e.target.value })}
                    icon={<Building className="h-4 w-4" />}
                    required
                  />
                  <Input
                    label="Your Role/Title in the Company"
                    value={registerForm.employer_role_title || ''}
                    onChange={(e) => setRegisterForm({ ...registerForm, employer_role_title: e.target.value })}
                    placeholder="e.g., HR Manager, CEO, Hiring Manager"
                    required
                  />
                  <Input
                    label="Company ABN"
                    value={registerForm.company_abn || ''}
                    onChange={(e) => {
                      let value = e.target.value;
                      // Remove any non-digit characters except spaces and hyphens
                      value = value.replace(/[^\d\s-]/g, '');
                      // Limit to 11 digits
                      const digits = value.replace(/[^\d]/g, '');
                      if (digits.length <= 11) {
                        setRegisterForm({ ...registerForm, company_abn: value });
                      }
                    }}
                    placeholder="XX XXX XXX XXX"
                    helperText="11-digit Australian Business Number"
                    required
                  />
                  <Input
                    label="Company Website (optional)"
                    type="text"
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
                        required
                      >
                        <option value="">Select size</option>
                        <option value="1-10">1-10 employees</option>
                        <option value="11-50">11-50 employees</option>
                        <option value="51-200">51-200 employees</option>
                        <option value="201-1000">201-1000 employees</option>
                        <option value="1000+">1000+ employees</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1">Industry</label>
                      <select
                        value={registerForm.industry || ''}
                        onChange={(e) => setRegisterForm({ ...registerForm, industry: e.target.value })}
                        className="input-field w-full"
                        required
                      >
                        <option value="">Select industry</option>
                        {[
                          'Technology', 'Finance', 'Healthcare', 'Education', 'Retail', 'Hospitality',
                          'Manufacturing', 'Construction', 'Transportation', 'Professional Services',
                          'Government', 'Non-Profit', 'Agriculture', 'Energy', 'Media & Entertainment'
                        ].map((ind) => (
                          <option key={ind} value={ind}>{ind}</option>
                        ))}
                      </select>
                    </div>
                  </div>
                </div>
              )}

              {/* Submit */}
              <Button type="submit" loading={loading} className="w-full" size="lg">
                Create Account
              </Button>
            </form>
          )}


        </Card>

        {/* Footer */}
        <div className="text-center text-sm text-slate-600">
          <p>
            By signing up, you agree to our{' '}
            <Link to="/terms" className="text-primary-600 hover:text-primary-500">
              Terms of Service
            </Link>{' '}
            and{' '}
            <Link to="/privacy" className="text-primary-600 hover:text-primary-500">
              Privacy Policy
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default AuthPage;

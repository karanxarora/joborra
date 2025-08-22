import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Mail, Lock, User, Building, GraduationCap, Calendar } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import Card from '../components/ui/Card';
import { LoginForm, RegisterForm } from '../types';
import { AU_UNIVERSITIES } from '../constants/universities';

const AuthPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'login' | 'register'>('login');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { login, register } = useAuth();
  const navigate = useNavigate();

  const [loginForm, setLoginForm] = useState<LoginForm>({
    email: '',
    password: '',
  });

  const [registerForm, setRegisterForm] = useState<RegisterForm>({
    email: '',
    username: '',
    password: '',
    full_name: '',
    role: 'student',
    university: '',
    degree: '',
    graduation_year: undefined,
    visa_status: '',
  });

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await login(loginForm);
      navigate('/dashboard');
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
      navigate('/dashboard');
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
          {/* Tab Navigation */}
          <div className="flex space-x-2 bg-slate-100 p-1 rounded-xl mb-8">
            <button
              onClick={() => setActiveTab('login')}
              className={`w-1/2 py-3 px-4 text-center rounded-lg font-medium text-sm transition-colors ${
                activeTab === 'login'
                  ? 'bg-white text-cyan-700'
                  : 'text-slate-600 hover:text-slate-800'
              }`}
            >
              Welcome Back
            </button>
            <button
              onClick={() => setActiveTab('register')}
              className={`w-1/2 py-3 px-4 text-center rounded-lg font-medium text-sm transition-colors ${
                activeTab === 'register'
                  ? 'bg-white text-cyan-700'
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
                  label="Username"
                  value={registerForm.username}
                  onChange={(e) => setRegisterForm({ ...registerForm, username: e.target.value })}
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
                        ? 'border-cyan-500 bg-cyan-50 text-cyan-700'
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
                        ? 'border-cyan-500 bg-cyan-50 text-cyan-700'
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
                  <Input
                    label="Degree/Course"
                    value={registerForm.degree || ''}
                    onChange={(e) => setRegisterForm({ ...registerForm, degree: e.target.value })}
                  />
                  <Input
                    label="Graduation Year"
                    type="number"
                    value={registerForm.graduation_year || ''}
                    onChange={(e) => setRegisterForm({ ...registerForm, graduation_year: parseInt(e.target.value) || undefined })}
                    icon={<Calendar className="h-4 w-4" />}
                  />
                  <Input
                    label="Visa Status"
                    value={registerForm.visa_status || ''}
                    onChange={(e) => setRegisterForm({ ...registerForm, visa_status: e.target.value })}
                    placeholder="e.g., Student Visa (500)"
                  />
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
            <a href="#" className="text-cyan-600 hover:text-cyan-500">
              Terms of Service
            </a>{' '}
            and{' '}
            <a href="#" className="text-cyan-600 hover:text-cyan-500">
              Privacy Policy
            </a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default AuthPage;

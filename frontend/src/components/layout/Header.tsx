import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { LogOut, User, Menu, X, ChevronDown, Bookmark, ClipboardList, Sparkles } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import Button from '../ui/Button';
import LogoIcon from '../ui/LogoIcon';
import { useToast } from '../../contexts/ToastContext';

const Header: React.FC = () => {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false);
  const [menuOpen, setMenuOpen] = React.useState(false);
  const { toast } = useToast();

  const handleLogout = async () => {
    const confirm = window.confirm('Are you sure you want to log out?');
    if (!confirm) return;
    try {
      await logout();
      toast('Logged out successfully', 'success');
      navigate('/');
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  return (
    <header className="bg-white border-b sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-4">
          {/* Logo */}
          <Link to="/" className="flex items-center">
            <div
              
              className="flex items-center"
            >
              {/* Brand icon, inherits theme color via Tailwind */}
              <LogoIcon className="h-8 w-8 text-primary-600 mr-3" />
              {/* Brand name */}
              <span className="text-xl font-bold text-slate-900 hidden sm:inline">Joborra</span>
            </div>
            <span className="ml-3 px-2 py-1 bg-primary-100 text-primary-800 text-xs font-medium rounded-full hidden sm:inline">
              1st International Student's Job Portal
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-6">
            <nav className="flex items-center space-x-6">
              <Link to="/jobs" className="text-slate-600 hover:text-primary-600 transition-colors">
                Browse Jobs
              </Link>
              {isAuthenticated && user?.role === 'student' && (
                <Link to="/saved" className="text-slate-600 hover:text-primary-600 transition-colors">
                  Saved Jobs
                </Link>
              )}
              {/* For Employers: only show the employer action to employers; unauthenticated users go to auth; students don't see it */}
              {!isAuthenticated && (
                <Link to="/auth" className="text-slate-600 hover:text-primary-600 transition-colors">
                  For Employers
                </Link>
              )}
              {isAuthenticated && user?.role === 'employer' && (
                <Link to="/employer/post-job" className="text-slate-600 hover:text-primary-600 transition-colors">
                  For Employers
                </Link>
              )}
              {isAuthenticated && user?.role === 'employer' && (
                <Link to="/employer/applications" className="text-slate-600 hover:text-primary-600 transition-colors">
                  Applications
                </Link>
              )}
              <Link to="/about" className="text-slate-600 hover:text-primary-600 transition-colors">
                About
              </Link>
            </nav>

            {/* Auth Section */}
            {isAuthenticated ? (
              <div className="relative">
                <button
                  onClick={() => setMenuOpen((v) => !v)}
                  className="flex items-center gap-2 px-3 py-2 border rounded-md text-sm text-slate-700 hover:bg-slate-50"
                >
                  <User className="h-4 w-4 text-slate-500" />
                  <span>
                    Welcome, {user?.full_name || user?.email}
                  </span>
                  <ChevronDown className="h-4 w-4 text-slate-500" />
                </button>
                {menuOpen && (
                  <div className="absolute right-0 mt-2 w-72 bg-white border border-slate-200 rounded-lg shadow-xl py-2 z-50">
                    {/* Header: name and email */}
                    <div className="px-3 pb-2">
                      <div className="flex items-start gap-2">
                        <div className="h-8 w-8 rounded-full bg-slate-100 flex items-center justify-center">
                          <User className="h-4 w-4 text-slate-500" />
                        </div>
                        <div className="min-w-0">
                          <div className="text-sm font-medium text-slate-900 truncate">{user?.full_name || 'User'}</div>
                          <div className="text-xs text-slate-500 truncate">{user?.email}</div>
                        </div>
                      </div>
                    </div>
                    <div className="my-2 border-t border-slate-100" />

                    {/* Student-specific items */}
                    {user?.role === 'student' && (
                      <>
                        <Link
                          to="/saved"
                          className="flex items-center gap-2 px-3 py-2 text-sm text-slate-700 hover:bg-slate-50"
                          onClick={() => setMenuOpen(false)}
                        >
                          <Bookmark className="h-4 w-4 text-slate-500" />
                          My Saved Jobs
                        </Link>
                        <Link
                          to="/applications"
                          className="flex items-center gap-2 px-3 py-2 text-sm text-slate-700 hover:bg-slate-50"
                          onClick={() => setMenuOpen(false)}
                        >
                          <ClipboardList className="h-4 w-4 text-slate-500" />
                          My Applications
                        </Link>
                      </>
                    )}

                    {/* Profile */}
                    <Link
                      to="/profile"
                      className="flex items-center gap-2 px-3 py-2 text-sm text-slate-700 hover:bg-slate-50"
                      onClick={() => setMenuOpen(false)}
                    >
                      <User className="h-4 w-4 text-slate-500" />
                      Profile
                    </Link>

                    {/* Employer-specific items */}
                    {user?.role === 'employer' && (
                      <>
                        <Link
                          to="/employer/post-job"
                          className="flex items-center gap-2 px-3 py-2 text-sm text-slate-700 hover:bg-slate-50"
                          onClick={() => setMenuOpen(false)}
                        >
                          <ClipboardList className="h-4 w-4 text-slate-500" />
                          Post a Job
                        </Link>
                        <Link
                          to="/employer/applications"
                          className="flex items-center gap-2 px-3 py-2 text-sm text-slate-700 hover:bg-slate-50"
                          onClick={() => setMenuOpen(false)}
                        >
                          <ClipboardList className="h-4 w-4 text-slate-500" />
                          Applications
                        </Link>
                      </>
                    )}

                    {/* Job Recommendations (placeholder) */}
                    <div className="px-3 py-2">
                      <div className="flex items-center gap-2 text-sm text-slate-700">
                        <Sparkles className="h-4 w-4 text-slate-500" />
                        Job Recommendations
                      </div>
                      <div className="text-[11px] text-slate-400 ml-6">(Personalized jobs will appear here soon)</div>
                    </div>

                    <div className="my-2 border-t border-slate-100" />

                    {/* Logout button */}
                    <div className="px-3 pb-2">
                      <button
                        className="w-full inline-flex items-center justify-center gap-2 px-3 py-2 text-sm text-white bg-primary-600 hover:bg-primary-700 rounded-md"
                        onClick={() => { setMenuOpen(false); handleLogout(); }}
                      >
                        <LogOut className="h-4 w-4" /> Logout
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex items-center space-x-3">
                <Link to="/auth">
                  <Button variant="outline" size="sm">
                    Login
                  </Button>
                </Link>
                <Link to="/auth">
                  <Button size="sm">
                    Get Started
                  </Button>
                </Link>
              </div>
            )}
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                icon={mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
              >
                {mobileMenuOpen ? 'Close' : 'Menu'}
              </Button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <div
            
            
            
            className="md:hidden py-4 border-t border-gray-100"
          >
            <nav className="flex flex-col space-y-4">
              {isAuthenticated && (
                <Link
                  to="/jobs"
                  className="text-slate-600 hover:text-primary-600 transition-colors"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Find Jobs
                </Link>
              )}
              {isAuthenticated && user?.role === 'student' && (
                <Link
                  to="/saved"
                  className="text-slate-600 hover:text-primary-600 transition-colors"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Saved Jobs
                </Link>
              )}
              <Link
                to="/about"
                className="text-slate-600 hover:text-primary-600 transition-colors"
                onClick={() => setMobileMenuOpen(false)}
              >
                About
              </Link>
              {/** Dashboard link hidden while disabled (mobile) */}
              {isAuthenticated && user?.role === 'employer' && (
                <Link
                  to="/employer/post-job"
                  className="text-slate-600 hover:text-primary-600 transition-colors"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Post a Job
                </Link>
              )}
              {isAuthenticated && user?.role === 'employer' && (
                <Link
                  to="/employer/applications"
                  className="text-slate-600 hover:text-primary-600 transition-colors"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Applications
                </Link>
              )}
            </nav>

            <div className="mt-4 pt-4 border-t border-gray-100">
              {isAuthenticated ? (
                <div className="space-y-3">
                  <div className="flex items-center space-x-2">
                    <User className="h-4 w-4 text-slate-500" />
                    <span className="text-sm text-slate-700">
                      {user?.full_name || user?.email}
                    </span>
                  </div>
                  <Link to="/profile" onClick={() => setMobileMenuOpen(false)}>
                    <Button variant="ghost" size="sm" className="w-full">
                      Profile
                    </Button>
                  </Link>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleLogout}
                    icon={<LogOut className="h-4 w-4" />}
                    className="w-full"
                  >
                    Logout
                  </Button>
                </div>
              ) : (
                <div className="space-y-3">
                  <Link to="/auth" onClick={() => setMobileMenuOpen(false)}>
                    <Button variant="outline" size="sm" className="w-full">
                      Login
                    </Button>
                  </Link>
                  <Link to="/auth" onClick={() => setMobileMenuOpen(false)}>
                    <Button size="sm" className="w-full">
                      Get Started
                    </Button>
                  </Link>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;

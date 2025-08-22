import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Briefcase, LogOut, User, Menu, X } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import Button from '../ui/Button';

const Header: React.FC = () => {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false);

  const handleLogout = async () => {
    try {
      await logout();
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
              <Briefcase className="h-8 w-8 text-cyan-600 mr-3" />
              <h1 className="text-2xl font-bold tracking-tight text-slate-900">Joborra</h1>
            </div>
            <span className="ml-3 px-2 py-1 bg-cyan-100 text-cyan-800 text-xs font-medium rounded-full hidden sm:inline">
              Australia's Job Portal
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-6">
            <nav className="flex items-center space-x-6">
              {isAuthenticated && (
                <Link to="/jobs" className="text-slate-600 hover:text-cyan-600 transition-colors">
                  Find Jobs
                </Link>
              )}
              <Link to="/about" className="text-slate-600 hover:text-cyan-600 transition-colors">
                About
              </Link>
              {/** Dashboard link hidden while disabled */}
              {isAuthenticated && (
                <Link to="/profile" className="text-slate-600 hover:text-cyan-600 transition-colors">
                  Profile
                </Link>
              )}
              {isAuthenticated && user?.role === 'employer' && (
                <Link to="/employer/post-job" className="text-slate-600 hover:text-cyan-600 transition-colors">
                  Post a Job
                </Link>
              )}
            </nav>

            {/* Auth Section */}
            {isAuthenticated ? (
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  <User className="h-4 w-4 text-slate-500" />
                  <span className="text-sm text-slate-700">
                    {user?.full_name || user?.email}
                  </span>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleLogout}
                  icon={<LogOut className="h-4 w-4" />}
                >
                  Logout
                </Button>
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
                  className="text-slate-600 hover:text-cyan-600 transition-colors"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Find Jobs
                </Link>
              )}
              <Link
                to="/about"
                className="text-slate-600 hover:text-cyan-600 transition-colors"
                onClick={() => setMobileMenuOpen(false)}
              >
                About
              </Link>
              {/** Dashboard link hidden while disabled (mobile) */}
              {isAuthenticated && (
                <Link
                  to="/profile"
                  className="text-slate-600 hover:text-cyan-600 transition-colors"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Profile
                </Link>
              )}
              {isAuthenticated && user?.role === 'employer' && (
                <Link
                  to="/employer/post-job"
                  className="text-slate-600 hover:text-cyan-600 transition-colors"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Post a Job
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

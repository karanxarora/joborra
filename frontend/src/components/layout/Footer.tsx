import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import DisabledLink from '../ui/DisabledLink';

const Footer: React.FC = () => {
  const { isAuthenticated, user } = useAuth();
  
  return (
    <footer className="bg-white border-t mt-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <h3 className="text-xl font-bold tracking-tight text-slate-900">Joborra</h3>
            <p className="text-sm text-gray-600 mt-2">
              Visa-friendly and student-friendly jobs across Australia.
            </p>
            <div className="mt-3">
              <Link to="/about" className="text-slate-600 hover:text-cyan-600 text-sm font-semibold">About Us</Link>
            </div>
          </div>
          <div>
            <h4 className="text-sm font-semibold text-slate-900 mb-3">Product</h4>
            <ul className="space-y-2 text-sm">
              <li>
                {isAuthenticated && user?.role === 'employer' ? (
                  <Link to="/employer/post-job" className="text-slate-600 hover:text-cyan-600">Post Jobs</Link>
                ) : (
                  <DisabledLink>Find Jobs</DisabledLink>
                )}
              </li>
              <li><DisabledLink>Saved Jobs</DisabledLink></li>
              <li><Link to="/profile" className="text-slate-600 hover:text-cyan-600">Profile</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="text-sm font-semibold text-slate-900 mb-3">Resources</h4>
            <ul className="space-y-2 text-sm">
              <li><Link to="/employer-visa-guide" className="text-slate-600 hover:text-cyan-600">Visa Guide</Link></li>
              <li><DisabledLink>Employer Sponsors</DisabledLink></li>
              <li><DisabledLink>Support</DisabledLink></li>
            </ul>
          </div>
          <div>
            <h4 className="text-sm font-semibold text-slate-900 mb-3">Stay Updated</h4>
            <p className="text-sm text-gray-600 mb-3">Get the latest visa-friendly roles.</p>
            <form className="flex gap-2">
              <input type="email" placeholder="Email address" className="input-field"/>
              <button type="submit" className="btn-primary">Subscribe</button>
            </form>
          </div>
        </div>
        <div className="mt-8 pt-6 border-t flex flex-col md:flex-row items-center justify-between text-sm text-slate-500">
          <p>© {new Date().getFullYear()} Joborra. All rights reserved.</p>
          <div className="space-x-4 mt-2 md:mt-0">
            <Link to="/privacy" className="hover:text-cyan-600">Privacy</Link>
            <Link to="/terms" className="hover:text-cyan-600">Terms</Link>
            <a href="mailto:manav@joborra.com" target="_blank" rel="noopener noreferrer" className="hover:text-cyan-600">Contact</a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;

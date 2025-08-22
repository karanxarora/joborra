import React from 'react';
import { Link } from 'react-router-dom';

const Footer: React.FC = () => {
  return (
    <footer className="bg-white border-t mt-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <h3 className="text-xl font-bold tracking-tight text-slate-900">Joborra</h3>
            <p className="text-sm text-gray-600 mt-2">
              Visa-friendly and student-friendly jobs across Australia.
            </p>
          </div>
          <div>
            <h4 className="text-sm font-semibold text-slate-900 mb-3">Product</h4>
            <ul className="space-y-2 text-sm">
              <li><Link to="/jobs" className="text-slate-600 hover:text-cyan-600">Find Jobs</Link></li>
              <li><Link to="/dashboard" className="text-slate-600 hover:text-cyan-600">Dashboard</Link></li>
              <li><Link to="/profile" className="text-slate-600 hover:text-cyan-600">Profile</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="text-sm font-semibold text-slate-900 mb-3">Resources</h4>
            <ul className="space-y-2 text-sm">
              <li><a href="#" className="text-slate-600 hover:text-cyan-600">Visa Guide</a></li>
              <li><a href="#" className="text-slate-600 hover:text-cyan-600">Employer Sponsors</a></li>
              <li><a href="#" className="text-slate-600 hover:text-cyan-600">Support</a></li>
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
            <a href="#" className="hover:text-cyan-600">Privacy</a>
            <a href="#" className="hover:text-cyan-600">Terms</a>
            <a href="#" className="hover:text-cyan-600">Contact</a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;

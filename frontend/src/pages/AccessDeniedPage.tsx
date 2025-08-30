import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';

interface AccessDeniedState {
  from?: string;
  requiredRole?: 'student' | 'employer';
  currentRole?: string | null;
}

const AccessDeniedPage: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const state = (location.state || {}) as AccessDeniedState;

  const { from, requiredRole, currentRole } = state;

  return (
    <div className="min-h-[70vh] flex items-center justify-center px-4">
      <div className="max-w-lg w-full bg-white border border-slate-200 rounded-lg shadow-sm p-8 text-center">
        <div className="mx-auto mb-4 h-12 w-12 rounded-full bg-red-50 flex items-center justify-center">
          <span className="text-red-600 text-2xl">!</span>
        </div>
        <h1 className="text-2xl font-semibold text-slate-800 mb-2">Access denied</h1>
        <p className="text-slate-600 mb-4">
          You dont have permission to view this page.
        </p>
        {requiredRole && (
          <p className="text-sm text-slate-500 mb-6">
            Required role: <span className="font-medium">{requiredRole}</span>
            {typeof currentRole !== 'undefined' && (
              <>
                {" "}| Your role: <span className="font-medium">{currentRole || 'guest'}</span>
              </>
            )}
          </p>
        )}

        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <button
            onClick={() => (from ? navigate(from, { replace: true }) : navigate('/', { replace: true }))}
            className="px-4 py-2 rounded-md border border-slate-300 text-slate-700 hover:bg-slate-50"
          >
            Go back
          </button>
          <Link
            to="/"
            className="px-4 py-2 rounded-md bg-primary-600 text-white hover:bg-primary-700"
          >
            Home
          </Link>
        </div>

        {requiredRole === 'employer' && (
          <p className="mt-6 text-sm text-slate-500">
            Want to post jobs? <Link to="/auth?tab=register" className="text-primary-600 hover:underline">Create an employer account</Link>.
          </p>
        )}
      </div>
    </div>
  );
};

export default AccessDeniedPage;

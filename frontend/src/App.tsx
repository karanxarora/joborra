import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Header from './components/layout/Header';
import { ToastProvider } from './contexts/ToastContext';
import { FavoritesProvider } from './contexts/FavoritesContext';
import Footer from './components/layout/Footer';
import PilotBanner from './components/PilotBanner';
import HomePage from './pages/HomePage';
import AuthPage from './pages/AuthPage';
// import DashboardPage from './pages/DashboardPage'; // disabled for now
import JobsPage from './pages/JobsPage';
import ProfilePage from './pages/ProfilePage';
import AboutPage from './pages/AboutPage';
import TermsPage from './pages/TermsPage';
import PrivacyPage from './pages/PrivacyPage';
import './App.css';
import EmployerPostJobPage from './pages/EmployerPostJobPage';
import EmployerQuickPostPage from './pages/EmployerQuickPostPage';
// import VerifyEmailPage from './pages/VerifyEmailPage';  // DISABLED FOR NOW
import ForgotPasswordPage from './pages/ForgotPasswordPage';
import ResetPasswordPage from './pages/ResetPasswordPage';

import EmployerApplicationsPage from './pages/EmployerApplicationsPage';
import EmployerDashboardPage from './pages/EmployerDashboardPage';
import AccessDeniedPage from './pages/AccessDeniedPage';
import SavedJobsPage from './pages/SavedJobsPage';
import EmployerVisaGuidePage from './pages/EmployerVisaGuidePage';
import JobDraftsPage from './pages/JobDraftsPage';
import EmployerJobViewPage from './pages/EmployerJobViewPage';
import EmployerCompanyInfoPage from './pages/EmployerCompanyInfoPage';
import HowItWorksPage from './pages/HowItWorksPage';

// Protected Route Component
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();
  
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-600"></div>
      </div>
    );
  }
  
  return isAuthenticated ? <>{children}</> : <Navigate to="/auth" replace />;
};

// Role-protected Route Component
const RoleProtectedRoute: React.FC<{ children: React.ReactNode; role: 'student' | 'employer' }> = ({ children, role }) => {
  const { isAuthenticated, isLoading, user } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-600"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/auth" replace />;
  }

  // user?.role is expected to be 'student' or 'employer'
  if (user?.role !== role) {
    return (
      <Navigate
        to="/access-denied"
        replace
        state={{
          from: location.pathname,
          requiredRole: role,
          currentRole: user?.role ?? null,
        }}
      />
    );
  }

  return <>{children}</>;
};

// Main App Component
const AppContent: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Header />
      <PilotBanner />
      <main className="flex-1">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/auth" element={<AuthPage />} />
          <Route 
            path="/jobs" 
            element={
              <ProtectedRoute>
                <JobsPage />
              </ProtectedRoute>
            } 
          />
          <Route
            path="/employer/fast-post"
            element={
              <RoleProtectedRoute role="employer">
                <EmployerQuickPostPage />
              </RoleProtectedRoute>
            }
          />
          <Route
            path="/employer/post-job"
            element={
              <RoleProtectedRoute role="employer">
                <EmployerPostJobPage />
              </RoleProtectedRoute>
            }
          />
          <Route
            path="/saved"
            element={
              <RoleProtectedRoute role="student">
                <SavedJobsPage />
              </RoleProtectedRoute>
            }
          />

          <Route
            path="/employer/applications"
            element={
              <RoleProtectedRoute role="employer">
                <EmployerApplicationsPage />
              </RoleProtectedRoute>
            }
          />
          <Route
            path="/employer/dashboard"
            element={
              <RoleProtectedRoute role="employer">
                <EmployerDashboardPage />
              </RoleProtectedRoute>
            }
          />
          <Route
            path="/employer/jobs/:id"
            element={
              <RoleProtectedRoute role="employer">
                <EmployerJobViewPage />
              </RoleProtectedRoute>
            }
          />
          <Route
            path="/employer/drafts"
            element={
              <RoleProtectedRoute role="employer">
                <JobDraftsPage />
              </RoleProtectedRoute>
            }
          />
          <Route
            path="/employer/company"
            element={
              <RoleProtectedRoute role="employer">
                <EmployerCompanyInfoPage />
              </RoleProtectedRoute>
            }
          />
          <Route path="/about" element={<AboutPage />} />
          <Route path="/how-it-works" element={<HowItWorksPage />} />
          <Route path="/employer-visa-guide" element={<EmployerVisaGuidePage />} />
          <Route path="/terms" element={<TermsPage />} />
          <Route path="/privacy" element={<PrivacyPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          {/* <Route path="/verify-email" element={<VerifyEmailPage />} />  DISABLED FOR NOW */}
          <Route path="/forgot-password" element={<ForgotPasswordPage />} />
          <Route path="/reset-password" element={<ResetPasswordPage />} />
          <Route path="/access-denied" element={<AccessDeniedPage />} />
          {/** Dashboard disabled for now */}
          {/**
          <Route 
            path="/dashboard" 
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            } 
          />
          */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
      <Footer />
    </div>
  );
};

function App() {
  useEffect(() => {
    // Handle ResizeObserver errors globally
    const handleResizeObserverError = (e: ErrorEvent) => {
      if (e.message === 'ResizeObserver loop completed with undelivered notifications.') {
        e.stopImmediatePropagation();
      }
    };

    window.addEventListener('error', handleResizeObserverError);
    
    return () => {
      window.removeEventListener('error', handleResizeObserverError);
    };
  }, []);

  return (
    <Router>
      <AuthProvider>
        <ToastProvider>
          <FavoritesProvider>
            <AppContent />
          </FavoritesProvider>
        </ToastProvider>
      </AuthProvider>
    </Router>
  );
}

export default App;

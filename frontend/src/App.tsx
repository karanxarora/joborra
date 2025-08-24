import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Header from './components/layout/Header';
import { ToastProvider } from './contexts/ToastContext';
import { FavoritesProvider } from './contexts/FavoritesContext';
import Footer from './components/layout/Footer';
import HomePage from './pages/HomePage';
import AuthPage from './pages/AuthPage';
// import DashboardPage from './pages/DashboardPage'; // disabled for now
import JobsPage from './pages/JobsPage';
import ProfilePage from './pages/ProfilePage';
import AboutPage from './pages/AboutPage';
import './App.css';
import EmployerPostJobPage from './pages/EmployerPostJobPage';
import VerifyEmailPage from './pages/VerifyEmailPage';
import EmployerCompanyInfoPage from './pages/EmployerCompanyInfoPage';
import EmployerApplicationsPage from './pages/EmployerApplicationsPage';
import SubmittedApplicationsPage from './pages/SubmittedApplicationsPage';
import AccessDeniedPage from './pages/AccessDeniedPage';
import SavedJobsPage from './pages/SavedJobsPage';

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
            path="/employer/post-job"
            element={
              <RoleProtectedRoute role="employer">
                <EmployerPostJobPage />
              </RoleProtectedRoute>
            }
          />
          <Route
            path="/applications"
            element={
              <RoleProtectedRoute role="student">
                <SubmittedApplicationsPage />
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
            path="/employer/company"
            element={
              <RoleProtectedRoute role="employer">
                <EmployerCompanyInfoPage />
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
          <Route path="/about" element={<AboutPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/verify-email" element={<VerifyEmailPage />} />
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

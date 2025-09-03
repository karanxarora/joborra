import React, { useState, useEffect } from 'react';

const PilotBanner: React.FC = () => {
  const [isVisible, setIsVisible] = useState(false);
  const [isDismissed, setIsDismissed] = useState(false);

  useEffect(() => {
    // Check if banner was previously dismissed
    const dismissed = localStorage.getItem('pilot-banner-dismissed');
    if (!dismissed) {
      // Show banner after a short delay for better UX
      const timer = setTimeout(() => setIsVisible(true), 1000);
      return () => clearTimeout(timer);
    }
  }, []);

  const handleDismiss = () => {
    setIsVisible(false);
    setIsDismissed(true);
    // Remember dismissal for 24 hours
    localStorage.setItem('pilot-banner-dismissed', 'true');
    // Auto-remove from localStorage after 24 hours
    setTimeout(() => {
      localStorage.removeItem('pilot-banner-dismissed');
    }, 24 * 60 * 60 * 1000);
  };

  if (!isVisible || isDismissed) {
    return null;
  }

  return (
    <div className="fixed top-0 left-0 right-0 z-50 bg-gradient-to-r from-cyan-600 to-blue-600 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between py-3">
          <div className="flex items-center space-x-3">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center">
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                </svg>
              </div>
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium">
                <span className="font-semibold">🚀 We're in Pilot Mode!</span>
                <span className="hidden sm:inline ml-2">
                  We're actively improving Joborra. Please bear with us as we enhance your experience.
                </span>
                <span className="sm:hidden ml-2">
                  Pilot mode - improvements in progress!
                </span>
              </p>
            </div>
          </div>
          <div className="flex-shrink-0">
            <button
              onClick={handleDismiss}
              className="bg-white/20 hover:bg-white/30 rounded-full p-1.5 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-white/50"
              aria-label="Dismiss banner"
            >
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PilotBanner;

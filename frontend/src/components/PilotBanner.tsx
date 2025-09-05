import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';

const PilotBanner: React.FC = () => {
  const [isVisible, setIsVisible] = useState(false);
  const location = useLocation();

  useEffect(() => {
    // Check if banner was dismissed in this session
    const dismissed = sessionStorage.getItem('pilot-banner-dismissed');
    if (!dismissed) {
      setIsVisible(true);
    }
  }, []);

  const handleDismiss = () => {
    setIsVisible(false);
    sessionStorage.setItem('pilot-banner-dismissed', 'true');
  };

  const handleLinkClick = (linkType: string) => {
    // Track analytics if needed
    console.log(`Pilot banner link clicked: ${linkType}`);
  };

  if (!isVisible) return null;

  return (
    <div className="bg-blue-600 text-white py-3 px-4 relative">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <svg 
            className="w-5 h-5 text-white" 
            fill="currentColor" 
            viewBox="0 0 20 20"
          >
            <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
          </svg>
          <span className="text-sm font-medium">
            Pilot mode: Browsing is paused. Share your profile — we'll match behind the scenes and email you roles that best match your profile.
          </span>
        </div>
        
        <div className="flex items-center space-x-4">
          <a 
            href="/how-it-works" 
            className="text-sm underline hover:text-blue-200 transition-colors"
            onClick={() => handleLinkClick('how-matching-works')}
          >
            How matching works
          </a>
          <a 
            href="/privacy" 
            className="text-sm underline hover:text-blue-200 transition-colors"
            onClick={() => handleLinkClick('privacy')}
          >
            Privacy
          </a>
          <button
            onClick={handleDismiss}
            className="text-white hover:text-blue-200 transition-colors ml-2"
            aria-label="Dismiss banner"
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
};

export default PilotBanner;
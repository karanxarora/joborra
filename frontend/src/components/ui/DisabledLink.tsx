import React, { useState } from 'react';

interface DisabledLinkProps {
  children: React.ReactNode;
  className?: string;
}

const DisabledLink: React.FC<DisabledLinkProps> = ({ children, className = "" }) => {
  const [showTooltip, setShowTooltip] = useState(false);

  return (
    <span 
      className={`text-slate-400 cursor-not-allowed relative inline-block ${className}`}
      title="Disabled for Pilot"
      onMouseEnter={() => setShowTooltip(true)}
      onMouseLeave={() => setShowTooltip(false)}
    >
      {children}
      
      {showTooltip && (
        <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 text-xs text-white bg-gray-800 rounded shadow-lg whitespace-nowrap z-50">
          Disabled for Pilot
          <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-800"></div>
        </div>
      )}
    </span>
  );
};

export default DisabledLink;

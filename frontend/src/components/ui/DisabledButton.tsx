import React, { useState } from 'react';

interface DisabledButtonProps {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'ghost' | 'outline';
  className?: string;
}

const DisabledButton: React.FC<DisabledButtonProps> = ({ 
  children, 
  variant = 'ghost', 
  className = "" 
}) => {
  const [showTooltip, setShowTooltip] = useState(false);
  
  const baseClasses = "inline-flex items-center justify-center px-4 py-2 text-sm font-medium rounded-md transition-colors cursor-not-allowed relative";
  
  const variantClasses = {
    primary: "bg-slate-300 text-slate-500",
    secondary: "bg-slate-200 text-slate-400",
    ghost: "text-slate-400 hover:text-slate-400",
    outline: "border border-slate-300 text-slate-400"
  };

  return (
    <div className="relative inline-block">
      <button 
        className={`${baseClasses} ${variantClasses[variant]} ${className}`}
        disabled
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
        title="Disabled for Pilot"
      >
        {children}
      </button>
      
      {showTooltip && (
        <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 text-xs text-white bg-gray-800 rounded shadow-lg whitespace-nowrap z-50">
          Disabled for Pilot
          <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-800"></div>
        </div>
      )}
    </div>
  );
};

export default DisabledButton;

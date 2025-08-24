import React from 'react';

// SVG logo that inherits color from parent via currentColor
// Usage: wrap with a Tailwind color class, e.g., <div className="text-cyan-600"><LogoIcon /></div>
const LogoIcon: React.FC<React.SVGProps<SVGSVGElement>> = (props) => {
  return (
    <svg
      viewBox="0 0 48 48"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-label="Joborra logo"
      {...props}
    >
      {/* Outer circle */}
      <circle cx="24" cy="24" r="21" stroke="currentColor" strokeWidth="4" fill="white" />
      {/* Smile arc */}
      <path
        d="M15 27c2.5 3.5 6 5.25 9 5.25s6.5-1.75 9-5.25"
        stroke="currentColor"
        strokeWidth="4"
        strokeLinecap="round"
        strokeLinejoin="round"
        fill="none"
      />
    </svg>
  );
};

export default LogoIcon;

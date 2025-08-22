import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  hover?: boolean;
  padding?: 'sm' | 'md' | 'lg';
}

const Card: React.FC<CardProps> = ({
  children,
  className = '',
  hover = false,
  padding = 'md',
}) => {
  const paddingClasses = {
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
  };

  const hoverClasses = hover ? '' : '';
  const baseClasses = `bg-white rounded-xl border border-slate-200 ${paddingClasses[padding]} ${hoverClasses} ${className}`;

  return <div className={baseClasses}>{children}</div>;
};

export default Card;

import React, { useState, useRef, useEffect } from 'react';
import { ChevronDown, HelpCircle } from 'lucide-react';

export interface SelectOption {
  value: string;
  label: string;
  hint?: string;
}

export interface SelectProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
  options: SelectOption[];
  placeholder?: string;
  required?: boolean;
  helperText?: string;
  className?: string;
  disabled?: boolean;
}

const Select: React.FC<SelectProps> = ({
  label,
  value,
  onChange,
  options,
  placeholder = "Select...",
  required = false,
  helperText,
  className = "",
  disabled = false,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [showTooltip, setShowTooltip] = useState(false);
  const [tooltipContent, setTooltipContent] = useState("");
  const selectRef = useRef<HTMLDivElement>(null);
  const tooltipRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (selectRef.current && !selectRef.current.contains(event.target as Node)) {
        setIsOpen(false);
        setShowTooltip(false); // Hide tooltip when dropdown closes
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  // Hide tooltip when dropdown closes
  useEffect(() => {
    if (!isOpen) {
      setShowTooltip(false);
    }
  }, [isOpen]);

  const selectedOption = options.find(option => option.value === value);

  const handleOptionClick = (option: SelectOption) => {
    onChange(option.value);
    setIsOpen(false);
    setShowTooltip(false); // Hide tooltip when option is selected
  };

  const handleMouseEnter = (option: SelectOption) => {
    if (option.hint) {
      setTooltipContent(option.hint);
      setShowTooltip(true);
    }
  };

  const handleMouseLeave = () => {
    setShowTooltip(false);
  };

  return (
    <div className={`relative ${className}`} ref={selectRef}>
      <label className="block text-sm font-medium text-slate-700 mb-1">
        {label}
      </label>
      
      <div className="relative">
        <button
          type="button"
          onClick={() => !disabled && setIsOpen(!isOpen)}
          disabled={disabled}
          className={`
            w-full px-3 py-2 text-left border rounded-md shadow-sm
            focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500
            ${disabled 
              ? 'bg-slate-50 text-slate-400 cursor-not-allowed' 
              : 'bg-white text-slate-900 hover:border-slate-400'
            }
            ${isOpen ? 'border-primary-500' : 'border-slate-300'}
          `}
        >
          <span className="block truncate">
            {selectedOption ? selectedOption.label : placeholder}
          </span>
          <span className="absolute inset-y-0 right-0 flex items-center pr-2 pointer-events-none">
            <ChevronDown className={`h-4 w-4 text-slate-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
          </span>
        </button>

        {isOpen && (
          <div className="absolute z-50 mt-1 w-full bg-white border border-slate-300 rounded-md shadow-lg max-h-60 overflow-auto">
            {options.map((option) => (
              <div
                key={option.value}
                className="relative px-3 py-2 cursor-pointer hover:bg-slate-50 flex items-center justify-between"
                onClick={() => handleOptionClick(option)}
                onMouseEnter={() => handleMouseEnter(option)}
                onMouseLeave={handleMouseLeave}
              >
                <span className="block truncate text-slate-900">{option.label}</span>
                {option.hint && (
                  <HelpCircle className="h-4 w-4 text-slate-400 ml-2 flex-shrink-0" />
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {showTooltip && tooltipContent && (
        <div
          ref={tooltipRef}
          className="absolute z-50 px-3 py-2 text-sm text-white bg-slate-900 rounded-md shadow-lg max-w-xs"
          style={{
            top: '100%',
            left: '0',
            marginTop: '4px',
          }}
        >
          {tooltipContent}
          <div className="absolute -top-1 left-4 w-2 h-2 bg-slate-900 transform rotate-45"></div>
        </div>
      )}

      {helperText && (
        <p className="mt-1 text-sm text-slate-500">{helperText}</p>
      )}
    </div>
  );
};

export default Select;

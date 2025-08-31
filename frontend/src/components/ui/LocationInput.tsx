import React, { useState, useRef, useEffect } from 'react';
import { MapPin } from 'lucide-react';
import { AUSTRALIAN_SUBURBS } from '../../constants/australianSuburbs';

export interface LocationData {
  location: string;
  city: string;
  state: string;
}

interface LocationInputProps {
  label: string;
  value: string;
  onChange: (location: string) => void;
  onLocationSelect?: (data: LocationData) => void;
  placeholder?: string;
  required?: boolean;
  className?: string;
}

const LocationInput: React.FC<LocationInputProps> = ({
  label,
  value,
  onChange,
  onLocationSelect,
  placeholder = "e.g., Sydney, NSW",
  required = false,
  className = "",
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [filteredLocations, setFilteredLocations] = useState<string[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node) &&
        inputRef.current &&
        !inputRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const filterLocations = (input: string) => {
    if (input.length < 2) {
      setFilteredLocations([]);
      return;
    }

    const filtered = AUSTRALIAN_SUBURBS.filter(location =>
      location.toLowerCase().includes(input.toLowerCase())
    ).slice(0, 10); // Limit to 10 suggestions

    setFilteredLocations(filtered);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const inputValue = e.target.value;
    onChange(inputValue);
    filterLocations(inputValue);
    setIsOpen(inputValue.length >= 2);
  };

  const handleLocationSelect = (selectedLocation: string) => {
    onChange(selectedLocation);
    setIsOpen(false);
    
    // Auto-fill city and state
    const locationData = parseLocation(selectedLocation);
    if (onLocationSelect) {
      onLocationSelect(locationData);
    }
  };

  const parseLocation = (location: string): LocationData => {
    // Extract city and state from location string
    let city = location;
    let state = 'NSW'; // Default to NSW as requested

    // Handle common patterns
    if (location.includes(',')) {
      const parts = location.split(',').map(part => part.trim());
      city = parts[0];
      if (parts.length > 1) {
        state = parts[1];
      }
    }

    // Special cases for major cities
    const majorCities: { [key: string]: { city: string; state: string } } = {
      'sydney': { city: 'Sydney', state: 'NSW' },
      'melbourne': { city: 'Melbourne', state: 'VIC' },
      'brisbane': { city: 'Brisbane', state: 'QLD' },
      'perth': { city: 'Perth', state: 'WA' },
      'adelaide': { city: 'Adelaide', state: 'SA' },
      'hobart': { city: 'Hobart', state: 'TAS' },
      'canberra': { city: 'Canberra', state: 'ACT' },
      'darwin': { city: 'Darwin', state: 'NT' },
      'newcastle': { city: 'Newcastle', state: 'NSW' },
      'wollongong': { city: 'Wollongong', state: 'NSW' },
      'gold coast': { city: 'Gold Coast', state: 'QLD' },
    };

    const lowerLocation = location.toLowerCase();
    for (const [key, data] of Object.entries(majorCities)) {
      if (lowerLocation.includes(key)) {
        return { location, city: data.city, state: data.state };
      }
    }

    // For NSW suburbs (most of our list), extract the suburb name
    if (state === 'NSW') {
      city = location.split(',')[0].trim();
    }

    return { location, city, state };
  };

  return (
    <div className={`relative ${className}`} ref={dropdownRef}>
      <label className="block text-sm font-medium text-slate-700 mb-1">
        {label}
      </label>
      
      <div className="relative">
        <input
          ref={inputRef}
          type="text"
          value={value}
          onChange={handleInputChange}
          onFocus={() => value.length >= 2 && setIsOpen(true)}
          placeholder={placeholder}
          required={required}
          className="input-field w-full pl-10"
        />
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <MapPin className="h-4 w-4 text-slate-400" />
        </div>
      </div>

      {isOpen && filteredLocations.length > 0 && (
        <div className="absolute z-50 mt-1 w-full bg-white border border-slate-300 rounded-md shadow-lg max-h-60 overflow-auto">
          {filteredLocations.map((location, index) => (
            <div
              key={index}
              className="px-3 py-2 cursor-pointer hover:bg-slate-50 flex items-center"
              onClick={() => handleLocationSelect(location)}
            >
              <MapPin className="h-4 w-4 text-slate-400 mr-2 flex-shrink-0" />
              <span className="text-slate-900">{location}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default LocationInput;

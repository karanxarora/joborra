import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import PilotBanner from './PilotBanner';

// Mock react-router-dom
jest.mock('react-router-dom', () => ({
  useLocation: () => ({ pathname: '/' }),
}));

// Mock sessionStorage
const mockSessionStorage = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
Object.defineProperty(window, 'sessionStorage', {
  value: mockSessionStorage,
});

describe('PilotBanner', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockSessionStorage.getItem.mockReturnValue(null);
  });

  it('renders the banner when not dismissed', () => {
    render(<PilotBanner />);
    
    expect(screen.getByText(/Pilot mode: Browsing is paused/)).toBeInTheDocument();
    expect(screen.getByText('How matching works')).toBeInTheDocument();
    expect(screen.getByText('Privacy')).toBeInTheDocument();
  });

  it('does not render when dismissed', () => {
    mockSessionStorage.getItem.mockReturnValue('true');
    render(<PilotBanner />);
    
    expect(screen.queryByText(/Pilot mode: Browsing is paused/)).not.toBeInTheDocument();
  });

  it('dismisses banner when X button is clicked', () => {
    render(<PilotBanner />);
    
    const dismissButton = screen.getByLabelText('Dismiss banner');
    fireEvent.click(dismissButton);
    
    expect(mockSessionStorage.setItem).toHaveBeenCalledWith('pilot-banner-dismissed', 'true');
  });

  it('has correct links', () => {
    render(<PilotBanner />);
    
    const howItWorksLink = screen.getByText('How matching works');
    const privacyLink = screen.getByText('Privacy');
    
    expect(howItWorksLink.closest('a')).toHaveAttribute('href', '/how-it-works');
    expect(privacyLink.closest('a')).toHaveAttribute('href', '/privacy');
  });
});

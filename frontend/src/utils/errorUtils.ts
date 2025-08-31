/**
 * Utility functions for handling and displaying errors gracefully
 */

interface ValidationError {
  type: string;
  loc: (string | number)[];
  msg: string;
  input?: any;
  ctx?: any;
  url?: string;
}

/**
 * Parse validation errors from API responses into user-friendly messages
 */
export function parseValidationError(error: any): string {
  // If it's already a string, return as-is
  if (typeof error === 'string') {
    return error;
  }

  // If it's an array of validation errors (Pydantic format)
  if (Array.isArray(error)) {
    return error.map(parseValidationError).join('\n');
  }

  // If it's a single validation error object
  if (error && typeof error === 'object') {
    // Handle Pydantic validation errors
    if (error.type && error.loc && error.msg) {
      const field = error.loc[error.loc.length - 1]; // Get the last part of the location
      const fieldName = formatFieldName(field);
      return `${fieldName}: ${error.msg}`;
    }

    // Handle other error objects
    if (error.message) {
      return error.message;
    }

    if (error.detail) {
      return error.detail;
    }

    if (error.error) {
      return error.error;
    }

    // Fallback to JSON string for unknown objects
    return JSON.stringify(error);
  }

  // Fallback for any other type
  return String(error);
}

/**
 * Format field names to be more user-friendly
 */
function formatFieldName(field: string | number): string {
  if (typeof field === 'number') {
    return `Field ${field}`;
  }

  // Convert snake_case to Title Case
  return field
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

/**
 * Extract the main error message from API response
 */
export function extractErrorMessage(error: any): string {
  // Handle axios error responses
  if (error?.response?.data) {
    const data = error.response.data;
    
    // Handle validation errors
    if (Array.isArray(data)) {
      return parseValidationError(data);
    }
    
    // Handle single error object
    if (data.detail) {
      return parseValidationError(data.detail);
    }
    
    // Handle error message
    if (data.message) {
      return data.message;
    }
    
    // Handle error field
    if (data.error) {
      return parseValidationError(data.error);
    }
  }
  
  // Handle direct error message
  if (error?.message) {
    return error.message;
  }
  
  // Fallback
  return parseValidationError(error) || 'An unexpected error occurred';
}

/**
 * Check if error is a validation error
 */
export function isValidationError(error: any): boolean {
  if (Array.isArray(error)) {
    return error.some(item => item.type && item.loc && item.msg);
  }
  
  if (error && typeof error === 'object') {
    return !!(error.type && error.loc && error.msg);
  }
  
  return false;
}

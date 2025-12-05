export interface ValidationResult {
  isValid: boolean;  // Indicates if validation passed
  errors: string[];  // List of error messages
}

// Function to validate email structure
export function isValidEmail(email: string): boolean {
  const emailPattern = /^[\w-.]+@([\w-]+.)+[\w-]{2,4}$/;
  return emailPattern.test(email);
}

// Function to validate password based on requirements
export function isValidPassword(password: string, requirements = {
  minLength: 8,
  requireUppercase: true,
  requireLowercase: true,
  requireNumbers: true,
  requireSpecialChars: false
}): ValidationResult {
  const errors: string[] = [];
  if (requirements.minLength && password.length < requirements.minLength) {
    errors.push(`Password should be at least ${requirements.minLength} characters long.`);
  }
  if (requirements.requireUppercase && !/[A-Z]/.test(password)) {
    errors.push('Password should contain at least one uppercase letter.');
  }
  if (requirements.requireLowercase && !/[a-z]/.test(password)) {
    errors.push('Password should contain at least one lowercase letter.');
  }
  if (requirements.requireNumbers && !/[0-9]/.test(password)) {
    errors.push('Password should contain at least one number.');
  }
  if (requirements.requireSpecialChars && !/[^A-Za-z0-9]/.test(password)) {
    errors.push('Password should contain at least one special character.');
  }
  return { isValid: errors.length === 0, errors };
}

// Function to validate string length
export function isValidLength(value: string, min = 0, max = Infinity): ValidationResult {
  const errors: string[] = [];
  if (value.length < min) {
    errors.push(`Must be at least ${min} characters.`);
  }
  if (value.length > max) {
    errors.push(`Must be no more than ${max} characters.`);
  }
  return { isValid: errors.length === 0, errors };
}

// Function to validate number within range
export function isValidNumber(value: number, min = -Infinity, max = Infinity): ValidationResult {
  const errors: string[] = [];
  if (value < min) {
    errors.push(`Must be at least ${min}.`);
  }
  if (value > max) {
    errors.push(`Must be no more than ${max}.`);
  }
  return { isValid: errors.length === 0, errors };
}

// Function to check if a field is required
export function isRequired(value: any): boolean {
  return value !== undefined && value !== null && value !== '';
}
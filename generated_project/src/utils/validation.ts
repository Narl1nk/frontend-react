export interface ValidationResult {
  isValid: boolean;
  errors: string[];
}

export function isValidEmail(email: string): boolean {
  const regex = /^[\w-.]+@([\w-]+\.)+[\w-]{2,4}$/;
  return regex.test(email);
}

export function isValidPassword(password: string, requirements = {
  min_length: 8,
  require_uppercase: true,
  require_lowercase: true,
  require_numbers: true,
  require_special_chars: false
}): ValidationResult {
  const errors: string[] = [];
  if (password.length < requirements.min_length) errors.push('Password must be at least ' + requirements.min_length + ' characters.');
  if (requirements.require_uppercase && !/[A-Z]/.test(password)) errors.push('Password must contain at least one uppercase letter.');
  if (requirements.require_lowercase && !/[a-z]/.test(password)) errors.push('Password must contain at least one lowercase letter.');
  if (requirements.require_numbers && !/[0-9]/.test(password)) errors.push('Password must contain at least one number.');
  if (requirements.require_special_chars && !/[!@#$%^&*(),.?":{}|<>]/.test(password)) errors.push('Password must contain at least one special character.');

  return { isValid: errors.length === 0, errors };
}

export function isValidLength(value: string, min = 0, max = Infinity): ValidationResult {
  const errors: string[] = [];
  if (value.length < min) errors.push(`Minimum length is ${min}.`);
  if (value.length > max) errors.push(`Maximum length is ${max}.`);  
  return { isValid: errors.length === 0, errors };
}

export function isValidNumber(value: number, min = -Infinity, max = Infinity): ValidationResult {
  const errors: string[] = [];
  if (value < min) errors.push(`Minimum value is ${min}.`);
  if (value > max) errors.push(`Maximum value is ${max}.`);
  return { isValid: errors.length === 0, errors };
}

export function isRequired(value: any): boolean {
  return value !== undefined && value !== null && value !== '';
}
export interface ValidationResult {
  isValid: boolean;
  errors: string[];
}

export function isValidEmail(email: string): boolean {
  const re = /^[\w-.]+@([\w-]+\.)+[\w-]{2,4}$/;
  return re.test(email);
}

export function isValidPassword(password: string, requirements = {
  min_length: 8,
  require_uppercase: true,
  require_lowercase: true,
  require_numbers: true,
  require_special_chars: true
}): ValidationResult {
  const errors: string[] = [];
  if (password.length < requirements.min_length) {
    errors.push(`Password must be at least ${requirements.min_length} characters long.`);
  }
  if (requirements.require_uppercase && !/[A-Z]/.test(password)) {
    errors.push('Password must contain at least one uppercase letter.');
  }
  if (requirements.require_lowercase && !/[a-z]/.test(password)) {
    errors.push('Password must contain at least one lowercase letter.');
  }
  if (requirements.require_numbers && !/\d/.test(password)) {
    errors.push('Password must contain at least one number.');
  }
  if (requirements.require_special_chars && !/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
    errors.push('Password must contain at least one special character.');
  }
  return { isValid: errors.length === 0, errors };
}

export function isValidLength(value: string, min = 0, max = Infinity): ValidationResult {
  const errors: string[] = [];
  if (value.length < min) {
    errors.push(`Value must be at least ${min} characters long.`);
  }
  if (value.length > max) {
    errors.push(`Value must not exceed ${max} characters.`);
  }
  return { isValid: errors.length === 0, errors };
}

export function isValidNumber(value: number, min = Number.NEGATIVE_INFINITY, max = Number.POSITIVE_INFINITY): ValidationResult {
  const errors: string[] = [];
  if (value < min) {
    errors.push(`Value must be at least ${min}.`);
  }
  if (value > max) {
    errors.push(`Value must not exceed ${max}.`);
  }
  return { isValid: errors.length === 0, errors };
}

export function isRequired(value: any): boolean {
  return value !== undefined && value !== null && value !== '';
}

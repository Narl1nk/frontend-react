// Function to format date based on format type
export function formatDate(date: string | Date, format: 'short' | 'long' | 'iso' = 'iso'): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  const options: Intl.DateTimeFormatOptions = {};
  switch (format) {
    case 'short':
      options.year = '2-digit';
      options.month = '2-digit';
      options.day = '2-digit';
      break;
    case 'long':
      options.year = 'numeric';
      options.month = 'long';
      options.day = 'numeric';
      break;
    case 'iso':
    default:
      return dateObj.toISOString();
  }
  return dateObj.toLocaleDateString(undefined, options);
}

// Function to format date and time
export function formatDateTime(date: string | Date): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  return dateObj.toLocaleString();
}

// Function to format relative time
export function formatRelativeTime(date: string | Date): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  const now = new Date();
  const diff = Math.abs(now.getTime() - dateObj.getTime());
  const seconds = Math.floor(diff / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);

  if (days > 0) {
    return `${days} days ago`;
  } else if (hours > 0) {
    return `${hours} hours ago`;
  } else if (minutes > 0) {
    return `${minutes} minutes ago`;
  } else {
    return `${seconds} seconds ago`;
  }
}

// Function to format currency
export function formatCurrency(amount: number, currency: string = 'USD'): string {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency }).format(amount);
}

// Function to format number with decimals
export function formatNumber(value: number, decimals: number = 2): string {
  return value.toLocaleString(undefined, { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
}

// Function to format percentage
export function formatPercentage(value: number, decimals: number = 2): string {
  return `${(value * 100).toFixed(decimals)}%`;
}

// Function to truncate strings and add ellipsis
export function truncate(text: string, maxLength: number): string {
  if (text.length > maxLength) {
    return `${text.substring(0, maxLength - 3)}...`;
  }
  return text;
}

// Function to capitalize first letter of string
export function capitalize(text: string): string {
  return text.charAt(0).toUpperCase() + text.slice(1);
}

// Function to convert string to title case
export function toTitleCase(text: string): string {
  return text.split(' ').map(word => capitalize(word)).join(' ');
}

// Function to format boolean values
export function formatBoolean(value: boolean, format: 'yes/no' | 'true/false' | 'on/off' = 'true/false'): string {
  switch (format) {
    case 'yes/no':
      return value ? 'Yes' : 'No';
    case 'on/off':
      return value ? 'On' : 'Off';
    case 'true/false':
    default:
      return value ? 'True' : 'False';
  }
}
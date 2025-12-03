export function formatDate(date: string | Date, format: 'short' | 'long' | 'iso' = 'iso'): string {
  const d = new Date(date);
  switch (format) {
    case 'short':
      return d.toLocaleDateString();
    case 'long':
      return d.toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' });
    case 'iso':
    default:
      return d.toISOString().slice(0, 10);
  }
}

export function formatDateTime(date: string | Date): string {
  return new Date(date).toLocaleString();
}

export function formatRelativeTime(date: string | Date): string {
  const deltaSeconds = Math.floor((Date.now() - new Date(date).getTime()) / 1000);
  if (deltaSeconds < 60) return 'just now';
  if (deltaSeconds < 3600) return `${Math.floor(deltaSeconds / 60)} minutes ago`;
  if (deltaSeconds < 86400) return `${Math.floor(deltaSeconds / 3600)} hours ago`;
  return `${Math.floor(deltaSeconds / 86400)} days ago`;
}

export function formatCurrency(amount: number, currency: string = 'USD'): string {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency }).format(amount);
}

export function formatNumber(value: number, decimals: number = 0): string {
  return new Intl.NumberFormat('en-US', { minimumFractionDigits: decimals, maximumFractionDigits: decimals }).format(value);
}

export function formatPercentage(value: number, decimals: number = 2): string {
  return `${formatNumber(value * 100, decimals)}%`;
}

export function truncate(text: string, maxLength: number): string {
  return text.length > maxLength ? text.substring(0, maxLength - 3) + '...' : text;
}

export function capitalize(text: string): string {
  return text.charAt(0).toUpperCase() + text.slice(1);
}

export function toTitleCase(text: string): string {
  return text.replace(/\w\S*/g, (txt) => txt.charAt(0).toUpperCase() + txt.substring(1).toLowerCase());
}

export function formatBoolean(value: boolean, format: 'yes-no' | 'true-false' | 'on-off' = 'true-false'): string {
  const formats = {
    'yes-no': value ? 'Yes' : 'No',
    'true-false': value ? 'True' : 'False',
    'on-off': value ? 'On' : 'Off'
  };
  return formats[format];
}
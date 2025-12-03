export function formatDate(date: string | Date, format: 'short' | 'long' | 'ISO' = 'ISO'): string {
  const options: Intl.DateTimeFormatOptions =
    format === 'short'
      ? { year: 'numeric', month: '2-digit', day: '2-digit' }
      : format === 'long'
      ? { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }
      : {};
  return new Date(date).toLocaleDateString(undefined, options);
}

export function formatDateTime(date: string | Date): string {
  const options: Intl.DateTimeFormatOptions = { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit' };
  return new Date(date).toLocaleString(undefined, options);
}

export function formatRelativeTime(date: string | Date): string {
  const deltaSeconds = Math.floor((new Date().getTime() - new Date(date).getTime()) / 1000);
  const days = Math.floor(deltaSeconds / 86400);
  const hours = Math.floor(deltaSeconds / 3600) % 24;
  const minutes = Math.floor(deltaSeconds / 60) % 60;

  if (days > 0) return `${days} day(s) ago`;
  if (hours > 0) return `${hours} hour(s) ago`;
  if (minutes > 0) return `${minutes} minute(s) ago`;
  return 'just now';
}

export function formatCurrency(amount: number, currency: string = 'USD'): string {
  return new Intl.NumberFormat(undefined, { style: 'currency', currency }).format(amount);
}

export function formatNumber(value: number, decimals: number = 2): string {
  return value.toFixed(decimals).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

export function formatPercentage(value: number, decimals: number = 2): string {
  return `${(value * 100).toFixed(decimals)}%`;
}

export function truncate(text: string, maxLength: number): string {
  return text.length > maxLength ? `${text.substring(0, maxLength)}...` : text;
}

export function capitalize(text: string): string {
  return text.charAt(0).toUpperCase() + text.slice(1).toLowerCase();
}

export function toTitleCase(text: string): string {
  return text.replace(/\w\S*/g, (txt) => txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase());
}

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

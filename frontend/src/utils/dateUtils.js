/**
 * Utilidades de fecha en zona horaria local para evitar desfases UTC (Mexico UTC-6).
 */

export function getLocalDateISO(date = new Date()) {
  const target = date instanceof Date ? date : new Date(date);
  const year = target.getFullYear();
  const month = String(target.getMonth() + 1).padStart(2, '0');
  const day = String(target.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

export function formatLocalDate(dateString, locale = 'es-MX', options = undefined) {
  if (!dateString) return '';
  try {
    if (typeof dateString === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(dateString.trim())) {
      const [year, month, day] = dateString.trim().split('-').map(Number);
      const localDate = new Date(year, month - 1, day);
      return localDate.toLocaleDateString(locale, options);
    }
    const parsed = new Date(dateString);
    if (Number.isNaN(parsed.getTime())) return String(dateString);
    return parsed.toLocaleDateString(locale, options);
  } catch {
    return String(dateString);
  }
}

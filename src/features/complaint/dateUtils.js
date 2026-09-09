const DISPLAY_DATE = /^(\d{2})\/(\d{2})\/(\d{4})$/;

export function isValidDisplayDate(value) {
  const match = String(value || '').match(DISPLAY_DATE);
  if (!match) return false;
  const [, day, month, year] = match;
  const date = new Date(Number(year), Number(month) - 1, Number(day));
  return date.getFullYear() === Number(year)
    && date.getMonth() === Number(month) - 1
    && date.getDate() === Number(day);
}

export function normalizeDate(value) {
  if (!value) return '';
  const text = String(value).trim();
  if (isValidDisplayDate(text)) return text;

  const slashOrDash = text.match(/^(\d{1,2})[-/](\d{1,2})[-/](\d{4})$/);
  if (slashOrDash) {
    const [, first, second, year] = slashOrDash;
    const day = text.includes('-') && Number(first) <= 12 ? second : first;
    const month = text.includes('-') && Number(first) <= 12 ? first : second;
    const normalized = `${String(day).padStart(2, '0')}/${String(month).padStart(2, '0')}/${year}`;
    return isValidDisplayDate(normalized) ? normalized : '';
  }

  const iso = text.match(/^(\d{4})-(\d{2})-(\d{2})$/);
  if (iso) return normalizeDate(`${iso[3]}/${iso[2]}/${iso[1]}`);

  const parsed = new Date(text);
  if (Number.isNaN(parsed.getTime())) return '';
  const normalized = `${String(parsed.getDate()).padStart(2, '0')}/${String(parsed.getMonth() + 1).padStart(2, '0')}/${parsed.getFullYear()}`;
  return isValidDisplayDate(normalized) ? normalized : '';
}

export function displayToNativeDate(value) {
  if (!isValidDisplayDate(value)) return '';
  const [day, month, year] = value.split('/');
  return `${year}-${month}-${day}`;
}

export function nativeToDisplayDate(value) {
  if (!value) return '';
  const [year, month, day] = value.split('-');
  return `${day}/${month}/${year}`;
}

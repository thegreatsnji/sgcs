const DATE_REGEX = /^(\d{2})\/(\d{2})\/(\d{4})$/;

export function isValidDisplayDate(value: string): boolean {
  const match = DATE_REGEX.exec(value.trim());
  if (!match) return false;
  const day = Number(match[1]);
  const month = Number(match[2]);
  const year = Number(match[3]);
  const date = new Date(year, month - 1, day);
  return date.getFullYear() === year && date.getMonth() === month - 1 && date.getDate() === day;
}

export function getAgeFromDisplayDate(value: string): number | null {
  if (!isValidDisplayDate(value)) return null;
  const match = DATE_REGEX.exec(value.trim());
  if (!match) return null;
  const birth = new Date(Number(match[3]), Number(match[2]) - 1, Number(match[1]));
  const today = new Date();
  let age = today.getFullYear() - birth.getFullYear();
  const monthDiff = today.getMonth() - birth.getMonth();
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
    age -= 1;
  }
  return age;
}

export function formatDisplayDate(value?: string | null): string {
  if (!value) return "—";
  return value;
}

export function formatDisplayDateTime(value?: string | null): string {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString("pt-PT", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

import { GB_COUNTRY_CODE, GB_PHONE_LOCAL_LENGTH } from "@/constants/phone";

/** Remove o prefixo +245 para edição no formulário. */
export function stripCountryCode(phone: string): string {
  const trimmed = phone.trim();
  if (trimmed.startsWith(GB_COUNTRY_CODE)) {
    return trimmed.slice(GB_COUNTRY_CODE.length);
  }
  if (trimmed.startsWith("245")) {
    return trimmed.slice(3);
  }
  return trimmed.replace(/\D/g, "");
}

/** Combina dígitos locais com o código de país. */
export function toFullPhone(localDigits: string): string {
  const digits = localDigits.replace(/\D/g, "");
  return `${GB_COUNTRY_CODE}${digits}`;
}

/** Valida dígitos locais (sem código de país). */
export function isValidLocalPhone(localDigits: string): boolean {
  const digits = localDigits.replace(/\D/g, "");
  return /^[0-9]{7,9}$/.test(digits);
}

/** Normaliza entrada do utilizador para apenas dígitos locais. */
export function sanitizeLocalPhoneInput(value: string): string {
  return value.replace(/\D/g, "").slice(0, GB_PHONE_LOCAL_LENGTH);
}

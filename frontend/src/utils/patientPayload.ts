import type { PatientPayload } from "@/types/patient";
import { displayDateToApi } from "@/utils/date";

function omitEmpty<T extends Record<string, unknown>>(obj: T): Partial<T> {
  const out: Record<string, unknown> = {};
  for (const [key, value] of Object.entries(obj)) {
    if (value === undefined || value === null) continue;
    if (typeof value === "string" && value.trim() === "") continue;
    if (Array.isArray(value) && value.length === 0) continue;
    out[key] = value;
  }
  return out as Partial<T>;
}

/** Normaliza campos enviados à API — evita 400 por strings vazias em choices/e-mail. */
export function normalizePatientPayload(payload: Partial<PatientPayload>): Record<string, unknown> {
  const out: Record<string, unknown> = {};

  if (payload.first_name != null) out.first_name = payload.first_name.trim();
  if (payload.last_name != null) out.last_name = payload.last_name.trim();
  if (payload.birth_date != null) out.birth_date = displayDateToApi(payload.birth_date);
  if (payload.gender != null) out.gender = payload.gender;
  if (payload.phone != null) out.phone = payload.phone.trim();

  const optional = omitEmpty({
    document_type: payload.document_type,
    document_number: payload.document_number?.trim(),
    email: payload.email?.trim(),
    address_street: payload.address_street?.trim(),
    address_city: payload.address_city?.trim(),
    address_region: payload.address_region?.trim(),
    address_country: payload.address_country?.trim(),
    address_postal_code: payload.address_postal_code?.trim(),
    nationality: payload.nationality?.trim(),
    blood_type: payload.blood_type,
    marital_status: payload.marital_status,
    occupation: payload.occupation?.trim(),
    emergency_contacts: payload.emergency_contacts,
  });

  return { ...out, ...optional };
}

export function normalizePatientCreatePayload(payload: PatientPayload): Record<string, unknown> {
  return normalizePatientPayload(payload);
}

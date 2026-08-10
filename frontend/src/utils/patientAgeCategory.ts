/** Limite alinhado com menores na ficha (contacto de emergência, etc.). */
export const MINOR_AGE_THRESHOLD = 18;

export type PatientAgeCategory = "ADULT" | "MINOR";

export const PATIENT_AGE_CATEGORY_LABELS: Record<PatientAgeCategory, string> = {
  ADULT: "Adulto",
  MINOR: "Menor de idade",
};

export function getPatientAgeCategory(age: number | null | undefined): PatientAgeCategory | null {
  if (age == null || !Number.isFinite(age)) return null;
  return age < MINOR_AGE_THRESHOLD ? "MINOR" : "ADULT";
}

import { getAgeFromDisplayDate } from "@/utils/date";

export type AgeGroup = "" | "child" | "adult" | "senior";

export const AGE_GROUP_LABELS: Record<Exclude<AgeGroup, "">, string> = {
  child: "0–17 anos",
  adult: "18–64 anos",
  senior: "65+ anos",
};

export function getPatientAge(birthDate?: string | null): number | null {
  if (!birthDate) return null;
  return getAgeFromDisplayDate(birthDate);
}

export function matchesAgeGroup(age: number | null, group: AgeGroup): boolean {
  if (!group) return true;
  if (age === null) return false;
  if (group === "child") return age < 18;
  if (group === "adult") return age >= 18 && age < 65;
  return age >= 65;
}

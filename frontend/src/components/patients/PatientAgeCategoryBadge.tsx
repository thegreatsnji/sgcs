import { PATIENT_AGE_CATEGORY_LABELS, type PatientAgeCategory } from "@/utils/patientAgeCategory";

const STYLES: Record<PatientAgeCategory, string> = {
  ADULT: "bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-200",
  MINOR: "bg-sky-100 text-sky-900 dark:bg-sky-950/50 dark:text-sky-200",
};

export function PatientAgeCategoryBadge({
  category,
  className = "",
}: {
  category: PatientAgeCategory | null;
  className?: string;
}) {
  if (!category) return null;
  return (
    <span
      className={`inline-flex items-center rounded-lg px-2.5 py-1 text-xs font-semibold ${STYLES[category]} ${className}`}
    >
      {PATIENT_AGE_CATEGORY_LABELS[category]}
    </span>
  );
}

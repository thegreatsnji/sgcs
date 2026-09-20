import { Badge } from "@/design-system";
import { ALLERGY_SEVERITY_LABELS } from "@/constants/patients";
import type { PatientAllergy } from "@/types/patient";

interface AllergyAlertBannerProps {
  allergies: PatientAllergy[];
}

export function AllergyAlertBanner({ allergies }: AllergyAlertBannerProps) {
  const severe = allergies.filter(
    (item) => item.is_active && (item.severity === "GRAVE" || item.severity === "ANAFILAXIA"),
  );

  if (severe.length === 0) return null;

  return (
    <div className="rounded-lg border border-red-200 bg-red-50 p-4">
      <p className="text-sm font-semibold text-red-900">Alergias graves registadas</p>
      <div className="mt-2 flex flex-wrap gap-2">
        {severe.map((allergy) => (
          <Badge key={allergy.id} variant="danger">
            {allergy.allergen}: {ALLERGY_SEVERITY_LABELS[allergy.severity]}
          </Badge>
        ))}
      </div>
    </div>
  );
}

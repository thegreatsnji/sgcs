import { getAgeFromDisplayDate } from "@/utils/date";

interface ComputedAgeHintProps {
  birthDate?: string | null;
  className?: string;
}

/** Idade derivada da data de nascimento (DD/MM/AAAA) — não duplicar manualmente. */
export function ComputedAgeHint({ birthDate, className = "" }: ComputedAgeHintProps) {
  const age = birthDate ? getAgeFromDisplayDate(birthDate) : null;
  if (age === null) return null;
  return (
    <p className={`text-xs text-text-muted ${className}`}>
      Idade: <span className="font-semibold text-text">{age} anos</span> (calculada automaticamente)
    </p>
  );
}

import type { LaboratoryResult } from "@/types/laboratoryResult";
import { formatDisplayDateTime } from "@/utils/date";

interface ResultadoTimelineProps {
  resultado: LaboratoryResult;
}

export function ResultadoTimeline({ resultado }: ResultadoTimelineProps) {
  const events = [
    {
      label: "Resultado registado",
      date: resultado.data_resultado,
      actor: resultado.responsavel_nome,
    },
    {
      label: "Resultado validado",
      date: resultado.data_validacao,
      actor: resultado.validado_por_nome,
    },
    {
      label: "Resultado entregue",
      date: resultado.data_publicacao,
      actor: null,
    },
  ].filter((e) => e.date);

  return (
    <ol className="space-y-4 border-l-2 border-slate-200 pl-4">
      {events.map((event) => (
        <li key={event.label} className="relative">
          <span className="absolute -left-[1.35rem] top-1 h-2.5 w-2.5 rounded-full bg-primary-600" />
          <p className="text-sm font-medium text-slate-800">{event.label}</p>
          <p className="text-xs text-slate-500">
            {formatDisplayDateTime(event.date!)}
            {event.actor ? ` — ${event.actor}` : ""}
          </p>
        </li>
      ))}
    </ol>
  );
}

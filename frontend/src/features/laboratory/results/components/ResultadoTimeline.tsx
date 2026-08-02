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
      color: "bg-primary-500",
    },
    {
      label: "Resultado validado",
      date: resultado.data_validacao,
      actor: resultado.validado_por_nome,
      color: "bg-emerald-500",
    },
    {
      label: "Resultado entregue",
      date: resultado.data_publicacao,
      actor: null,
      color: "bg-sky-500",
    },
  ].filter((e) => e.date);

  if (events.length === 0) {
    return <p className="text-sm text-slate-500">Sem eventos registados.</p>;
  }

  return (
    <ol className="relative space-y-0">
      <div className="absolute top-2 bottom-2 left-[9px] w-px bg-slate-200" aria-hidden />
      {events.map((event) => (
        <li key={event.label} className="relative flex gap-4 py-3">
          <span className={`relative z-10 mt-1 h-2.5 w-2.5 shrink-0 rounded-full ${event.color}`} />
          <div>
            <p className="text-sm font-medium text-slate-900">{event.label}</p>
            <p className="text-xs text-slate-500">
              {formatDisplayDateTime(event.date!)}
              {event.actor ? ` · ${event.actor}` : ""}
            </p>
          </div>
        </li>
      ))}
    </ol>
  );
}

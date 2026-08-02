import { Badge, Card } from "@/design-system";
import { APPOINTMENT_STATUS_LABELS } from "@/constants/appointments";
import type { ClinicalRecord } from "@/types/clinicalRecord";
import type { AppointmentStatus } from "@/types/appointment";
import { formatDisplayDateTime } from "@/utils/date";

interface ConsultationSidebarProps {
  data: ClinicalRecord;
}

export function ConsultationSidebar({ data }: ConsultationSidebarProps) {
  const severeAllergies = data.paciente.allergies.filter((a) =>
    ["GRAVE", "ANAFILAXIA", "SEVERE"].includes(a.severity),
  );

  return (
    <aside className="space-y-4 xl:sticky xl:top-20 xl:self-start">
      {severeAllergies.length > 0 && (
        <Card title="Alertas" className="border-red-200 bg-red-50/50">
          <ul className="space-y-2 text-sm text-red-800">
            {severeAllergies.map((a) => (
              <li key={a.id} className="flex items-start gap-2">
                <span className="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-red-500" aria-hidden />
                <span>
                  <strong>{a.allergen}</strong> — {a.severity}
                  {a.reaction && <span className="block text-xs text-red-600">{a.reaction}</span>}
                </span>
              </li>
            ))}
          </ul>
        </Card>
      )}

      <Card title="Linha do tempo">
        {data.ultimas_consultas.length === 0 ? (
          <p className="text-sm text-slate-500">Sem consultas anteriores.</p>
        ) : (
          <ul className="relative space-y-0">
            <div className="absolute top-1 bottom-1 left-[7px] w-px bg-slate-200" aria-hidden />
            {data.ultimas_consultas.slice(0, 6).map((visit) => (
              <li key={visit.id} className="relative flex gap-3 py-2.5">
                <span className="relative z-10 mt-1.5 h-2 w-2 shrink-0 rounded-full bg-primary-500" />
                <div className="min-w-0">
                  <p className="text-xs font-medium text-slate-900">
                    {formatDisplayDateTime(visit.scheduled_at)}
                  </p>
                  <p className="text-[11px] text-slate-500">
                    {APPOINTMENT_STATUS_LABELS[visit.status as AppointmentStatus]}
                    {visit.doctor && ` · ${visit.doctor}`}
                  </p>
                  {visit.diagnosis && (
                    <p className="mt-0.5 line-clamp-2 text-[11px] text-slate-600">{visit.diagnosis}</p>
                  )}
                </div>
              </li>
            ))}
          </ul>
        )}
      </Card>

      <Card title="Resultados recentes">
        {(data.resultados_laboratoriais ?? []).length === 0 ? (
          <p className="text-sm text-slate-500">Sem resultados laboratoriais.</p>
        ) : (
          <ul className="divide-y divide-slate-100">
            {(data.resultados_laboratoriais ?? []).slice(0, 5).map((r) => (
              <li key={r.id} className="py-2.5 first:pt-0">
                <p className="text-sm font-medium text-slate-900">{r.numero_pedido}</p>
                <div className="mt-1 flex items-center gap-2">
                  <Badge variant={r.estado === "VALIDADO" ? "success" : "warning"}>
                    {r.estado}
                  </Badge>
                  {r.data_resultado && (
                    <span className="text-[11px] text-slate-500">{r.data_resultado}</span>
                  )}
                </div>
              </li>
            ))}
          </ul>
        )}
      </Card>

      {data.paciente.chronic_diseases.length > 0 && (
        <Card title="Condições crónicas">
          <ul className="space-y-1.5 text-sm text-slate-700">
            {data.paciente.chronic_diseases.map((d) => (
              <li key={d.id}>{d.disease_name}</li>
            ))}
          </ul>
        </Card>
      )}
    </aside>
  );
}

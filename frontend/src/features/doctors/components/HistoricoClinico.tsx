import type { HistoricoTerapeutico } from "@/types/doctors";

interface HistoricoClinicoProps {
  historico?: HistoricoTerapeutico;
  isLoading?: boolean;
}

export function HistoricoClinico({ historico, isLoading }: HistoricoClinicoProps) {
  if (isLoading) {
    return <p className="text-sm text-slate-500">A carregar histórico...</p>;
  }

  if (!historico) {
    return <p className="text-sm text-slate-500">Indique o ID do paciente para consultar o histórico.</p>;
  }

  return (
    <div className="grid gap-6 md:grid-cols-2">
      <div>
        <h4 className="mb-2 font-medium text-slate-800">Prescrições</h4>
        <ul className="space-y-1 text-sm">
          {historico.prescricoes.map((p) => (
            <li key={p.id} className="rounded border border-slate-100 px-3 py-2">
              #{p.id}: {p.estado} ({new Date(p.created_at).toLocaleDateString("pt-PT")})
            </li>
          ))}
          {!historico.prescricoes.length && <li className="text-slate-500">Nenhuma prescrição.</li>}
        </ul>
      </div>
      <div>
        <h4 className="mb-2 font-medium text-slate-800">Tratamentos</h4>
        <ul className="space-y-1 text-sm">
          {historico.tratamentos.map((t) => (
            <li key={t.id} className="rounded border border-slate-100 px-3 py-2">
              {t.tipo}: {t.estado}
            </li>
          ))}
          {!historico.tratamentos.length && <li className="text-slate-500">Nenhum tratamento.</li>}
        </ul>
      </div>
    </div>
  );
}

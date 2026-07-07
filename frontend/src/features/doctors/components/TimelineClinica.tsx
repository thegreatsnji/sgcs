export interface EventoClinico {
  id: number;
  tipo: string;
  data: string;
  titulo: string;
  descricao?: string;
}

interface TimelineClinicaProps {
  eventos: EventoClinico[];
}

const tipoCores: Record<string, string> = {
  MELHORIA: "bg-green-100 text-green-800",
  AGRAVAMENTO: "bg-red-100 text-red-800",
  ESTAVEL: "bg-slate-100 text-slate-800",
};

export function TimelineClinica({ eventos }: TimelineClinicaProps) {
  if (!eventos.length) {
    return <p className="text-sm text-slate-500">Sem evoluções clínicas registadas.</p>;
  }

  return (
    <ol className="relative border-l border-slate-200 pl-6">
      {eventos.map((ev) => (
        <li key={ev.id} className="mb-6">
          <span className="absolute -left-1.5 mt-1.5 h-3 w-3 rounded-full bg-primary-500" />
          <time className="text-xs text-slate-500">{new Date(ev.data).toLocaleString("pt-PT")}</time>
          <div className="mt-1 flex items-center gap-2">
            <span className={`rounded px-2 py-0.5 text-xs font-medium ${tipoCores[ev.tipo] ?? "bg-slate-100"}`}>
              {ev.tipo}
            </span>
            <span className="font-medium text-slate-800">{ev.titulo}</span>
          </div>
          {ev.descricao && <p className="mt-1 text-sm text-slate-600">{ev.descricao}</p>}
        </li>
      ))}
    </ol>
  );
}

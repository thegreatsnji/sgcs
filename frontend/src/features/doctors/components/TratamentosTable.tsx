import type { Tratamento } from "@/types/doctors";

interface TratamentosTableProps {
  tratamentos: Tratamento[];
  onFinish?: (id: number) => void;
}

export function TratamentosTable({ tratamentos, onFinish }: TratamentosTableProps) {
  if (!tratamentos.length) {
    return <p className="text-sm text-slate-500">Sem tratamentos registados.</p>;
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full text-sm">
        <thead>
          <tr className="border-b border-slate-200 text-left text-slate-600">
            <th className="py-2 pr-4">Tipo</th>
            <th className="py-2 pr-4">Descrição</th>
            <th className="py-2 pr-4">Início</th>
            <th className="py-2 pr-4">Fim</th>
            <th className="py-2 pr-4">Estado</th>
            <th className="py-2">Acções</th>
          </tr>
        </thead>
        <tbody>
          {tratamentos.map((t) => (
            <tr key={t.id} className="border-b border-slate-100">
              <td className="py-2 pr-4 font-medium">{t.tipo}</td>
              <td className="py-2 pr-4">{t.descricao}</td>
              <td className="py-2 pr-4">{t.data_inicio}</td>
              <td className="py-2 pr-4">{t.data_fim ?? "—"}</td>
              <td className="py-2 pr-4">{t.estado}</td>
              <td className="py-2">
                {onFinish && t.estado === "EM_CURSO" && (
                  <button
                    type="button"
                    className="text-primary-600 hover:underline"
                    onClick={() => onFinish(t.id)}
                  >
                    Concluir
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

interface Medicamento {
  id?: number;
  nome: string;
  dosagem: string;
  forma_farmaceutica?: string;
  via?: string;
  frequencia: string;
  duracao: string;
  posologia?: string;
  estado?: string;
}

interface MedicamentosTableProps {
  medicamentos: Medicamento[];
  onApprove?: (prescricaoId: number) => void;
  prescricaoId?: number;
  estadoPrescricao?: string;
}

export function MedicamentosTable({ medicamentos, onApprove, prescricaoId, estadoPrescricao }: MedicamentosTableProps) {
  if (!medicamentos.length) {
    return <p className="text-sm text-slate-500">Sem medicamentos prescritos.</p>;
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full text-sm">
        <thead>
          <tr className="border-b border-slate-200 text-left text-slate-600">
            <th className="py-2 pr-4">Nome</th>
            <th className="py-2 pr-4">Dosagem</th>
            <th className="py-2 pr-4">Frequência</th>
            <th className="py-2 pr-4">Duração</th>
            <th className="py-2 pr-4">Posologia</th>
            <th className="py-2">Estado</th>
          </tr>
        </thead>
        <tbody>
          {medicamentos.map((med, i) => (
            <tr key={med.id ?? i} className="border-b border-slate-100">
              <td className="py-2 pr-4 font-medium">{med.nome}</td>
              <td className="py-2 pr-4">{med.dosagem}</td>
              <td className="py-2 pr-4">{med.frequencia}</td>
              <td className="py-2 pr-4">{med.duracao}</td>
              <td className="py-2 pr-4">{med.posologia || "—"}</td>
              <td className="py-2">{med.estado ?? "—"}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {onApprove && prescricaoId && estadoPrescricao === "RASCUNHO" && (
        <button
          type="button"
          className="mt-3 rounded bg-primary-600 px-3 py-1.5 text-sm text-white hover:bg-primary-700"
          onClick={() => onApprove(prescricaoId)}
        >
          Aprovar prescrição
        </button>
      )}
    </div>
  );
}

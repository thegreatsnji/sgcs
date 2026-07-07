import { useState } from "react";

import { Button, Card } from "@/design-system";
import { ParametroEditor } from "@/features/laboratory/results/components/ParametroEditor";
import type { ParametroResultado } from "@/types/laboratoryResult";

export interface ResultadoFormValues {
  pedido_laboratorial: number;
  observacoes: string;
  conclusao: string;
  parametros: ParametroResultado[];
}

interface ResultadoFormProps {
  initial?: Partial<ResultadoFormValues>;
  pedidoLabel?: string;
  onSubmit: (values: ResultadoFormValues) => void;
  isPending?: boolean;
  disabled?: boolean;
  showPedidoField?: boolean;
}

export function ResultadoForm({
  initial,
  pedidoLabel,
  onSubmit,
  isPending,
  disabled,
  showPedidoField = false,
}: ResultadoFormProps) {
  const [pedidoId, setPedidoId] = useState(initial?.pedido_laboratorial ?? 0);
  const [observacoes, setObservacoes] = useState(initial?.observacoes ?? "");
  const [conclusao, setConclusao] = useState(initial?.conclusao ?? "");
  const [parametros, setParametros] = useState<ParametroResultado[]>(initial?.parametros ?? []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      pedido_laboratorial: pedidoId,
      observacoes,
      conclusao,
      parametros: parametros.filter((p) => p.nome && p.valor),
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {showPedidoField ? (
        <div>
          <label className="mb-1 block text-sm font-medium text-slate-700">ID do pedido</label>
          <input
            type="number"
            className="w-full rounded border border-slate-300 px-3 py-2 text-sm"
            value={pedidoId || ""}
            disabled={disabled}
            onChange={(e) => setPedidoId(Number(e.target.value))}
            required
          />
        </div>
      ) : pedidoLabel ? (
        <Card title="Pedido">
          <p className="text-sm font-medium text-slate-800">{pedidoLabel}</p>
        </Card>
      ) : null}

      <Card title="Parâmetros">
        <ParametroEditor value={parametros} onChange={setParametros} disabled={disabled} />
      </Card>

      <div className="grid gap-4 lg:grid-cols-2">
        <div>
          <label className="mb-1 block text-sm font-medium text-slate-700">Observações</label>
          <textarea
            className="min-h-24 w-full rounded border border-slate-300 px-3 py-2 text-sm"
            value={observacoes}
            disabled={disabled}
            onChange={(e) => setObservacoes(e.target.value)}
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-slate-700">Conclusão</label>
          <textarea
            className="min-h-24 w-full rounded border border-slate-300 px-3 py-2 text-sm"
            value={conclusao}
            disabled={disabled}
            onChange={(e) => setConclusao(e.target.value)}
          />
        </div>
      </div>

      {!disabled && (
        <Button type="submit" variant="primary" disabled={isPending}>
          {isPending ? "A guardar..." : "Guardar resultado"}
        </Button>
      )}
    </form>
  );
}

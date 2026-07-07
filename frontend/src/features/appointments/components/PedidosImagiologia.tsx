import { Badge, Button, Card, Table } from "@/design-system";
import { PRIORITY_LABELS } from "@/constants/appointments";
import type { ExamOrder } from "@/types/clinicalRecord";

interface PedidosImagiologiaProps {
  pedidos: ExamOrder[];
  disabled?: boolean;
  onAdd: (data: { tipo_exame: string; prioridade?: string; observacoes?: string }) => void;
  isPending?: boolean;
}

export function PedidosImagiologia({ pedidos, disabled, onAdd, isPending }: PedidosImagiologiaProps) {
  return (
    <div className="space-y-4">
      <Card title="Pedidos de imagiologia">
        <p className="mb-3 text-sm text-slate-500">
          Pedidos preparados para integração futura com o módulo de imagiologia.
        </p>
        <Table<ExamOrder>
          data={pedidos}
          getRowKey={(row) => row.id}
          emptyMessage="Nenhum pedido emitido nesta consulta."
          columns={[
            { key: "tipo_exame", header: "Exame" },
            {
              key: "prioridade",
              header: "Prioridade",
              render: (row) =>
                PRIORITY_LABELS[row.prioridade as keyof typeof PRIORITY_LABELS] ?? row.prioridade,
            },
            {
              key: "estado",
              header: "Estado",
              render: (row) => <Badge>{row.estado}</Badge>,
            },
          ]}
        />
      </Card>

      {!disabled && (
        <Card title="Novo pedido de imagiologia">
          <form
            className="space-y-4"
            onSubmit={(e) => {
              e.preventDefault();
              const fd = new FormData(e.currentTarget);
              onAdd({
                tipo_exame: String(fd.get("tipo_exame")),
                prioridade: String(fd.get("prioridade") ?? "NORMAL"),
                observacoes: String(fd.get("observacoes") ?? ""),
              });
              e.currentTarget.reset();
            }}
          >
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">Tipo de exame</label>
              <input name="tipo_exame" required className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm" />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">Prioridade</label>
              <select name="prioridade" className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm">
                {Object.entries(PRIORITY_LABELS).map(([v, l]) => (
                  <option key={v} value={v}>{l}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">Observações</label>
              <textarea name="observacoes" rows={2} className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm" />
            </div>
            <Button type="submit" disabled={isPending}>Emitir pedido</Button>
          </form>
        </Card>
      )}
    </div>
  );
}

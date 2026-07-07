import { Button, Card } from "@/design-system";
import type { FollowUp } from "@/types/clinicalRecord";

interface SeguimentoFormProps {
  initial?: FollowUp | null;
  disabled?: boolean;
  onSubmit: (data: { data_retorno: string; motivo: string; observacoes?: string }) => void;
  isPending?: boolean;
}

export function SeguimentoForm({ initial, disabled, onSubmit, isPending }: SeguimentoFormProps) {
  return (
    <Card title="Seguimento / consulta de retorno">
      <form
        className="space-y-4 max-w-lg"
        onSubmit={(e) => {
          e.preventDefault();
          const fd = new FormData(e.currentTarget);
          onSubmit({
            data_retorno: String(fd.get("data_retorno")),
            motivo: String(fd.get("motivo")),
            observacoes: String(fd.get("observacoes") ?? ""),
          });
        }}
      >
        <div>
          <label className="mb-1 block text-sm font-medium text-slate-700">Data de retorno</label>
          <input
            name="data_retorno"
            type="date"
            required
            defaultValue={initial?.data_retorno?.slice(0, 10) ?? ""}
            disabled={disabled}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm disabled:bg-slate-50"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-slate-700">Motivo</label>
          <input
            name="motivo"
            required
            defaultValue={initial?.motivo ?? ""}
            disabled={disabled}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm disabled:bg-slate-50"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-slate-700">Observações</label>
          <textarea
            name="observacoes"
            rows={3}
            defaultValue={initial?.observacoes ?? ""}
            disabled={disabled}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm disabled:bg-slate-50"
          />
        </div>
        {!disabled && (
          <Button type="submit" disabled={isPending}>
            Agendar seguimento
          </Button>
        )}
      </form>
    </Card>
  );
}

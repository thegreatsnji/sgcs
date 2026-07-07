import { Badge, Button, Card, Table } from "@/design-system";
import type { ClinicalDiagnosis } from "@/types/clinicalRecord";

interface DiagnosticosTabProps {
  diagnosticos: ClinicalDiagnosis[];
  disabled?: boolean;
  onAdd: (data: { codigo_cid10: string; descricao: string; tipo: string }) => void;
  isPending?: boolean;
}

export function DiagnosticosTab({ diagnosticos, disabled, onAdd, isPending }: DiagnosticosTabProps) {
  return (
    <div className="space-y-4">
      <Card title="Diagnósticos (CID-10)">
        <Table<ClinicalDiagnosis>
          data={diagnosticos}
          getRowKey={(row) => row.id}
          emptyMessage="Nenhum diagnóstico registado."
          columns={[
            { key: "codigo_cid10", header: "CID-10" },
            { key: "descricao", header: "Descrição" },
            {
              key: "tipo",
              header: "Tipo",
              render: (row) => (
                <Badge variant={row.tipo === "PRINCIPAL" ? "info" : "default"}>
                  {row.tipo === "PRINCIPAL" ? "Principal" : "Secundário"}
                </Badge>
              ),
            },
          ]}
        />
      </Card>

      {!disabled && (
        <Card title="Adicionar diagnóstico">
          <form
            className="grid gap-4 sm:grid-cols-2"
            onSubmit={(e) => {
              e.preventDefault();
              const fd = new FormData(e.currentTarget);
              onAdd({
                codigo_cid10: String(fd.get("codigo_cid10")),
                descricao: String(fd.get("descricao")),
                tipo: String(fd.get("tipo") ?? "PRINCIPAL"),
              });
              e.currentTarget.reset();
            }}
          >
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">Código CID-10</label>
              <input
                name="codigo_cid10"
                required
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">Tipo</label>
              <select name="tipo" className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm">
                <option value="PRINCIPAL">Principal</option>
                <option value="SECUNDARIO">Secundário</option>
              </select>
            </div>
            <div className="sm:col-span-2">
              <label className="mb-1 block text-sm font-medium text-slate-700">Descrição</label>
              <input
                name="descricao"
                required
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
              />
            </div>
            <Button type="submit" disabled={isPending}>
              Adicionar
            </Button>
          </form>
        </Card>
      )}
    </div>
  );
}

import { Table } from "@/design-system";
import type { FeatureFlag } from "@/types/settings";

export function FeatureFlagTable({
  flags,
  onToggle,
}: {
  flags: FeatureFlag[];
  onToggle: (codigo: string, activo: boolean) => void;
}) {
  return (
    <Table<FeatureFlag>
      data={flags}
      getRowKey={(f) => f.id}
      columns={[
        { key: "codigo", header: "Código" },
        { key: "nome", header: "Nome" },
        {
          key: "activo",
          header: "Estado",
          render: (f) => (
            <button
              type="button"
              className={`rounded px-2 py-1 text-xs ${f.activo ? "bg-green-100 text-green-800" : "bg-slate-100"}`}
              onClick={() => onToggle(f.codigo, !f.activo)}
            >
              {f.activo ? "Activo" : "Inactivo"}
            </button>
          ),
        },
      ]}
    />
  );
}

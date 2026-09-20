import { Button, Card } from "@/design-system";
import type { SOAPNote } from "@/types/clinicalRecord";

interface SOAPFormProps {
  initial?: SOAPNote | null;
  disabled?: boolean;
  onSubmit: (data: SOAPNote) => void;
  onAutosave?: (data: SOAPNote) => void;
  isPending?: boolean;
}

const FIELDS: Array<{ key: keyof SOAPNote; label: string; rows: number }> = [
  { key: "subjetivo", label: "Subjetivo (S)", rows: 3 },
  { key: "objetivo", label: "Objetivo (O)", rows: 3 },
  { key: "avaliacao", label: "Avaliação (A)", rows: 3 },
  { key: "plano", label: "Plano (P)", rows: 3 },
];

export function SOAPForm({ initial, disabled, onSubmit, onAutosave, isPending }: SOAPFormProps) {
  return (
    <Card title="Anotação clínica (SOAP)">
      <form
        onSubmit={(e) => {
          e.preventDefault();
          const fd = new FormData(e.currentTarget);
          onSubmit({
            subjetivo: String(fd.get("subjetivo") ?? ""),
            objetivo: String(fd.get("objetivo") ?? ""),
            avaliacao: String(fd.get("avaliacao") ?? ""),
            plano: String(fd.get("plano") ?? ""),
          });
        }}
        className="space-y-4"
      >
        {FIELDS.map(({ key, label, rows }) => (
          <div key={key}>
            <label className="mb-1 block text-sm font-medium text-slate-700">{label}</label>
            <textarea
              name={key}
              rows={rows}
              defaultValue={initial?.[key] ?? ""}
              disabled={disabled}
              onBlur={
                onAutosave && !disabled
                  ? (e) => {
                      const form = e.currentTarget.form;
                      if (!form) return;
                      const fd = new FormData(form);
                      onAutosave({
                        subjetivo: String(fd.get("subjetivo") ?? ""),
                        objetivo: String(fd.get("objetivo") ?? ""),
                        avaliacao: String(fd.get("avaliacao") ?? ""),
                        plano: String(fd.get("plano") ?? ""),
                      });
                    }
                  : undefined
              }
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm disabled:bg-slate-50"
            />
          </div>
        ))}
        {!disabled && (
          <Button type="submit" disabled={isPending}>
            Guardar SOAP
          </Button>
        )}
      </form>
    </Card>
  );
}

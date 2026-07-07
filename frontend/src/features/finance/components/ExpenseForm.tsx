import { Button } from "@/design-system";

interface ExpenseFormProps {
  onSubmit: (values: Record<string, string>) => void;
  isPending?: boolean;
}

export function ExpenseForm({ onSubmit, isPending }: ExpenseFormProps) {
  return (
    <form
      className="grid gap-4 sm:grid-cols-2"
      onSubmit={(e) => {
        e.preventDefault();
        const form = new FormData(e.currentTarget);
        onSubmit(Object.fromEntries(form.entries()) as Record<string, string>);
      }}
    >
      <input name="fornecedor" placeholder="Fornecedor" className="rounded border px-3 py-2 text-sm" required />
      <select name="categoria" className="rounded border px-3 py-2 text-sm" defaultValue="OUTROS">
        <option value="MEDICAMENTOS">Medicamentos</option>
        <option value="ENERGIA">Energia</option>
        <option value="SALARIOS">Salários</option>
        <option value="OUTROS">Outros</option>
      </select>
      <input name="valor" type="number" step="0.01" placeholder="Valor" className="rounded border px-3 py-2 text-sm" required />
      <input name="data" type="date" className="rounded border px-3 py-2 text-sm" required />
      <textarea name="descricao" placeholder="Descrição" className="sm:col-span-2 rounded border px-3 py-2 text-sm" required />
      <Button type="submit" variant="primary" disabled={isPending}>Guardar despesa</Button>
    </form>
  );
}

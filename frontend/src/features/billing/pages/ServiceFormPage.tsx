import { useMutation } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";

import { Button, Card, useToast } from "@/design-system";
import { BillingSubNav } from "@/features/billing/components/BillingSubNav";
import { billingService } from "@/services/billing/billing.service";
import { getApiErrorMessage } from "@/utils/api-error";

export function ServiceFormPage() {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const mutation = useMutation({
    mutationFn: billingService.createService,
    onSuccess: () => {
      showToast("Serviço criado.", "success");
      void navigate("/billing/services");
    },
    onError: (e) => showToast(getApiErrorMessage(e), "error"),
  });

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-slate-900">Novo serviço</h2>
      <BillingSubNav />
      <Card>
        <form
          className="grid gap-4 sm:grid-cols-2"
          onSubmit={(e) => {
            e.preventDefault();
            const form = new FormData(e.currentTarget);
            mutation.mutate({
              codigo: String(form.get("codigo")),
              nome: String(form.get("nome")),
              descricao: String(form.get("descricao") || ""),
              categoria: String(form.get("categoria")),
              preco: String(form.get("preco")),
            });
          }}
        >
          <input name="codigo" placeholder="Código" className="rounded border px-3 py-2 text-sm" required />
          <input name="nome" placeholder="Nome" className="rounded border px-3 py-2 text-sm" required />
          <select name="categoria" className="rounded border px-3 py-2 text-sm" defaultValue="CONSULTA">
            <option value="CONSULTA">Consulta</option>
            <option value="EXAME">Exame</option>
            <option value="PROCEDIMENTO">Procedimento</option>
            <option value="OUTRO">Outro</option>
          </select>
          <input name="preco" type="number" step="0.01" placeholder="Preço" className="rounded border px-3 py-2 text-sm" required />
          <textarea name="descricao" placeholder="Descrição" className="sm:col-span-2 rounded border px-3 py-2 text-sm" />
          <Button type="submit" variant="primary" disabled={mutation.isPending}>Guardar</Button>
        </form>
      </Card>
    </div>
  );
}

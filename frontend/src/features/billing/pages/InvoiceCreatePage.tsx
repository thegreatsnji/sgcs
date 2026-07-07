import { useMutation, useQuery } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";

import { Button, Card, LoadingState, useToast } from "@/design-system";
import { BillingSubNav } from "@/features/billing/components/BillingSubNav";
import { billingService } from "@/services/billing/billing.service";
import { getApiErrorMessage } from "@/utils/api-error";

export function InvoiceCreatePage() {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const { data: quotes } = useQuery({ queryKey: ["billing-quotes-approved"], queryFn: () => billingService.listQuotes({ estado: "APROVADO" }) });
  const { data: services } = useQuery({ queryKey: ["billing-services"], queryFn: () => billingService.listServices({ activo: true }) });
  const mutation = useMutation({
    mutationFn: billingService.createInvoice,
    onSuccess: (inv) => {
      showToast("Fatura criada.", "success");
      void navigate(`/billing/invoices/${inv.id}`);
    },
    onError: (e) => showToast(getApiErrorMessage(e), "error"),
  });

  if (!quotes || !services) return <LoadingState />;

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Nova fatura</h2>
      <BillingSubNav />
      <Card title="A partir de orçamento">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            const orcamento = Number(new FormData(e.currentTarget).get("orcamento"));
            if (orcamento) mutation.mutate({ orcamento });
          }}
          className="flex flex-wrap gap-3"
        >
          <select name="orcamento" className="rounded border px-3 py-2 text-sm">
            <option value="">— Orçamento aprovado —</option>
            {quotes.results.map((q) => (
              <option key={q.id} value={q.id}>{q.numero} — {q.paciente_nome}</option>
            ))}
          </select>
          <Button type="submit" variant="primary">Gerar fatura</Button>
        </form>
      </Card>
      <Card title="Fatura directa">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            const form = new FormData(e.currentTarget);
            mutation.mutate({
              paciente: Number(form.get("paciente")),
              itens: [{ servico: Number(form.get("servico")), quantidade: 1 }],
            });
          }}
          className="grid gap-3 sm:grid-cols-3"
        >
          <input name="paciente" placeholder="ID paciente" className="rounded border px-3 py-2 text-sm" required />
          <select name="servico" className="rounded border px-3 py-2 text-sm">
            {services.results.map((s) => <option key={s.id} value={s.id}>{s.nome}</option>)}
          </select>
          <Button type="submit" variant="secondary">Criar</Button>
        </form>
      </Card>
    </div>
  );
}

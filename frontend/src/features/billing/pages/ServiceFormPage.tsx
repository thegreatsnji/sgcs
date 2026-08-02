import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate, useParams } from "react-router-dom";

import { Button, Card, LoadingState, useToast } from "@/design-system";
import { SERVICE_CATEGORY_OPTIONS } from "@/constants/serviceCategories";
import { BillingSubNav } from "@/features/billing/components/BillingSubNav";
import { useAuth } from "@/contexts/AuthContext";
import { billingService } from "@/services/billing/billing.service";
import { getApiErrorMessage } from "@/utils/api-error";

export function ServiceFormPage() {
  const { id } = useParams<{ id: string }>();
  const isEdit = Boolean(id);
  const serviceId = Number(id);
  const navigate = useNavigate();
  const { showToast } = useToast();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const canChangePrice = user?.role === "ADMINISTRADOR";

  const { data: existing, isLoading } = useQuery({
    queryKey: ["billing-service", serviceId],
    queryFn: () => billingService.getService(serviceId),
    enabled: isEdit && Number.isFinite(serviceId),
  });

  const mutation = useMutation({
    mutationFn: (payload: object) =>
      isEdit ? billingService.updateService(serviceId, payload) : billingService.createService(payload),
    onSuccess: (svc) => {
      showToast(isEdit ? "Serviço actualizado." : "Serviço criado.", "success");
      void queryClient.invalidateQueries({ queryKey: ["billing-services"] });
      void navigate(isEdit ? `/billing/services/${svc.id}` : "/billing/services");
    },
    onError: (e) => showToast(getApiErrorMessage(e), "error"),
  });

  if (isEdit && isLoading) return <LoadingState />;

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-slate-900">{isEdit ? "Editar serviço" : "Novo serviço"}</h2>
      <BillingSubNav />
      <Card>
        <form
          className="grid gap-4 sm:grid-cols-2"
          onSubmit={(e) => {
            e.preventDefault();
            const form = new FormData(e.currentTarget);
            const payload: Record<string, unknown> = {
              codigo: String(form.get("codigo")),
              nome: String(form.get("nome")),
              descricao: String(form.get("descricao") || ""),
              categoria: String(form.get("categoria")),
              activo: form.get("activo") === "on",
            };
            if (canChangePrice) {
              payload.preco = String(form.get("preco"));
              const motivo = String(form.get("motivo_alteracao_preco") || "");
              if (motivo) payload.motivo_alteracao_preco = motivo;
            }
            mutation.mutate(payload);
          }}
        >
          <input
            name="codigo"
            placeholder="Código"
            className="rounded border px-3 py-2 text-sm"
            required
            defaultValue={existing?.codigo}
            readOnly={isEdit}
          />
          <input
            name="nome"
            placeholder="Nome"
            className="rounded border px-3 py-2 text-sm"
            required
            defaultValue={existing?.nome}
          />
          <select
            name="categoria"
            className="rounded border px-3 py-2 text-sm"
            defaultValue={existing?.categoria ?? "CONSULTA"}
          >
            {SERVICE_CATEGORY_OPTIONS.map((c) => (
              <option key={c.value} value={c.value}>
                {c.label}
              </option>
            ))}
          </select>
          {canChangePrice ? (
            <>
              <input
                name="preco"
                type="number"
                step="1"
                min={0}
                placeholder="Preço (FCFA)"
                className="rounded border px-3 py-2 text-sm"
                defaultValue={existing?.preco ?? "0"}
              />
              {isEdit ? (
                <input
                  name="motivo_alteracao_preco"
                  placeholder="Motivo da alteração de preço"
                  className="sm:col-span-2 rounded border px-3 py-2 text-sm"
                />
              ) : null}
            </>
          ) : (
            <p className="text-sm text-slate-600 sm:col-span-2">
              Preço: {existing ? `${existing.preco} FCFA` : "—"} (apenas Administrador pode alterar)
            </p>
          )}
          <label className="flex items-center gap-2 text-sm">
            <input type="checkbox" name="activo" defaultChecked={existing?.activo ?? true} />
            Activo
          </label>
          <textarea
            name="descricao"
            placeholder="Descrição"
            className="sm:col-span-2 rounded border px-3 py-2 text-sm"
            defaultValue={existing?.descricao}
          />
          <Button type="submit" variant="primary" disabled={mutation.isPending}>
            Guardar
          </Button>
        </form>
      </Card>
    </div>
  );
}

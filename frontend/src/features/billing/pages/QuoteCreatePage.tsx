import { useMutation, useQuery } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";

import { Card, LoadingState, useToast } from "@/design-system";
import { BillingSubNav } from "@/features/billing/components/BillingSubNav";
import { QuoteForm } from "@/features/billing/components/QuoteForm";
import { billingService } from "@/services/billing/billing.service";
import { getApiErrorMessage } from "@/utils/api-error";

export function QuoteCreatePage() {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const { data: services, isLoading } = useQuery({
    queryKey: ["billing-services"],
    queryFn: () => billingService.listServices({ activo: true }),
  });
  const mutation = useMutation({
    mutationFn: billingService.createQuote,
    onSuccess: () => {
      showToast("Orçamento criado.", "success");
      void navigate("/billing/quotes");
    },
    onError: (e) => showToast(getApiErrorMessage(e), "error"),
  });

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Novo orçamento</h2>
      <BillingSubNav />
      {isLoading || !services ? <LoadingState /> : (
        <Card title="Dados do orçamento">
          <QuoteForm services={services.results} onSubmit={(v) => mutation.mutate(v)} isPending={mutation.isPending} />
        </Card>
      )}
    </div>
  );
}

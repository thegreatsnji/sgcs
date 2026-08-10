import { useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link, useParams, useSearchParams } from "react-router-dom";

import { Button, LoadingState } from "@/design-system";
import { SauVidaReceiptPrint } from "@/features/billing/components/SauVidaReceiptPrint";
import { ReceptionAtendimentoBanner } from "@/features/reception/components/ReceptionAtendimentoBanner";
import { billingService } from "@/services/billing/billing.service";

export function ReceiptDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [searchParams] = useSearchParams();
  const receiptId = Number(id);
  const segundaVia = searchParams.get("segunda_via") === "1";
  const autoPrint = searchParams.get("imprimir") === "1";
  const retorno = searchParams.get("retorno");

  const { data, isLoading } = useQuery({
    queryKey: ["billing-receipt", receiptId],
    queryFn: () => billingService.getReceipt(receiptId),
    enabled: Number.isFinite(receiptId),
  });

  useEffect(() => {
    if (!autoPrint || isLoading) return;
    const t = window.setTimeout(() => window.print(), 400);
    return () => window.clearTimeout(t);
  }, [autoPrint, isLoading]);

  if (isLoading || !data) return <LoadingState />;

  return (
    <div className="receipt-page space-y-6">
      <ReceptionAtendimentoBanner retorno={retorno} />
      <div className="no-print flex flex-wrap items-center gap-2">
        <Link to={`/billing/invoices`} className="text-sm font-medium text-primary-600 hover:text-primary-700">
          ← Faturação
        </Link>
        <Button type="button" variant="primary" onClick={() => window.print()}>
          Imprimir
        </Button>
        <Link to={`/billing/receipts/${receiptId}?segunda_via=1&imprimir=1`}>
          <Button type="button" variant="secondary">
            Segunda via
          </Button>
        </Link>
        {retorno ? (
          <Link to={decodeURIComponent(retorno)}>
            <Button type="button" variant="primary">
              Continuar — notificar médico →
            </Button>
          </Link>
        ) : (
          <Link to="/reception/atendimento?passo=1">
            <Button type="button" variant="outline">
              Voltar à receção
            </Button>
          </Link>
        )}
      </div>

      <div className="receipt-print-root mx-auto">
        <SauVidaReceiptPrint receiptId={receiptId} segundaVia={segundaVia} />
      </div>
    </div>
  );
}

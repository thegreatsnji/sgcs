import { useQuery } from "@tanstack/react-query";
import { useParams } from "react-router-dom";

import { LoadingState } from "@/design-system";
import { BillingSubNav } from "@/features/billing/components/BillingSubNav";
import { ReceiptPreview } from "@/features/billing/components/ReceiptPreview";
import { billingService } from "@/services/billing/billing.service";

export function ReceiptDetailPage() {
  const { id } = useParams<{ id: string }>();
  const receiptId = Number(id);
  const { data, isLoading } = useQuery({
    queryKey: ["billing-receipt", receiptId],
    queryFn: () => billingService.getReceipt(receiptId),
    enabled: Number.isFinite(receiptId),
  });

  if (isLoading || !data) return <LoadingState />;

  return (
    <div className="space-y-6">
      <BillingSubNav />
      <ReceiptPreview receipt={data} />
    </div>
  );
}

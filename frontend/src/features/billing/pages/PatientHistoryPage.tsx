import { useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { Button, Card, LoadingState } from "@/design-system";
import { BillingSubNav } from "@/features/billing/components/BillingSubNav";
import { billingService } from "@/services/billing/billing.service";

export function PatientHistoryPage() {
  const [patientId, setPatientId] = useState("");
  const id = Number(patientId);
  const { data, isLoading, refetch, isFetched } = useQuery({
    queryKey: ["billing-patient-history", id],
    queryFn: () => billingService.getPatientHistory(id),
    enabled: false,
  });

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Histórico financeiro</h2>
      <BillingSubNav />
      <div className="flex flex-wrap gap-2">
        <input
          className="rounded border px-3 py-2 text-sm"
          placeholder="ID do paciente"
          value={patientId}
          onChange={(e) => setPatientId(e.target.value)}
        />
        <Button variant="primary" onClick={() => void refetch()} disabled={!Number.isFinite(id)}>
          Consultar
        </Button>
      </div>
      {isLoading && <LoadingState />}
      {isFetched && data && (
        <>
          <Card title="Resumo">
            <dl className="grid gap-2 text-sm sm:grid-cols-3">
              <div><dt className="text-slate-500">Total faturado</dt><dd>{data.resumo.total_faturado} FCFA</dd></div>
              <div><dt className="text-slate-500">Total pago</dt><dd>{data.resumo.total_pago} FCFA</dd></div>
              <div><dt className="text-slate-500">Saldo</dt><dd>{data.resumo.saldo} FCFA</dd></div>
            </dl>
          </Card>
          <Card title="Faturas">
            <ul className="text-sm">{data.faturas.map((f) => <li key={f.id}>{f.numero} — {f.estado} — {f.total} FCFA</li>)}</ul>
          </Card>
        </>
      )}
    </div>
  );
}

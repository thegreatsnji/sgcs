import { useMutation, useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";

import { Button, Card, LoadingState, useToast } from "@/design-system";
import { InvoiceSummaryPanel } from "@/features/billing/components/InvoiceSummaryPanel";
import {
  ServiceSearchPicker,
  type InvoiceLineDraft,
} from "@/features/billing/components/ServiceSearchPicker";
import { MOTIVOS_REDUCAO } from "@/features/billing/constants/reducao";
import { ReceptionAtendimentoBanner } from "@/features/reception/components/ReceptionAtendimentoBanner";
import { PatientSearchSelect } from "@/features/reception/components/PatientSearchSelect";
import { billingService } from "@/services/billing/billing.service";
import { getApiErrorMessage } from "@/utils/api-error";

function buildItensPayload(lines: InvoiceLineDraft[]) {
  return lines.map((l) => ({
    servico: l.servico.id,
    quantidade: l.quantidade,
    ...(l.aplicarReducao && l.precoCobrado != null
      ? {
          preco_cobrado: l.precoCobrado,
          motivo_reducao: l.motivoReducao,
          observacao_reducao: l.observacaoReducao,
          autorizacao_reducao_id: l.autorizacaoReducaoId,
        }
      : {}),
  }));
}

function validateLines(lines: InvoiceLineDraft[]): string | null {
  for (const line of lines) {
    if (!line.aplicarReducao) continue;
    if (!line.motivoReducao) return "Indique o motivo da redução em todos os itens.";
    if (line.motivoReducao === "OUTRO" && !line.observacaoReducao?.trim()) {
      return "Observação obrigatória quando o motivo é «Outro».";
    }
  }
  return null;
}

export function InvoiceCreatePage() {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [searchParams] = useSearchParams();
  const initialPatient = Number(searchParams.get("paciente")) || null;
  const retorno = searchParams.get("retorno");

  const [patientId, setPatientId] = useState<number | null>(
    Number.isFinite(initialPatient) && initialPatient ? initialPatient : null,
  );
  const [lines, setLines] = useState<InvoiceLineDraft[]>([]);
  const [observacoes, setObservacoes] = useState("");

  const {
    data: services,
    isLoading: servicesLoading,
    isError: servicesError,
    refetch,
  } = useQuery({
    queryKey: ["billing-services-operacional"],
    queryFn: () =>
      billingService.listServices({ activo: true, operacional: true, page_size: 500 }),
  });

  const mutation = useMutation({
    mutationFn: billingService.createInvoice,
    onError: (e) => showToast(getApiErrorMessage(e), "error"),
  });

  const popularIds = useMemo(
    () => services?.results.slice(0, 6).map((s) => s.id) ?? [],
    [services?.results],
  );

  async function submit(goReceipt: boolean) {
    if (!patientId || lines.length === 0) {
      showToast("Seleccione o paciente e adicione pelo menos um serviço.", "error");
      return;
    }
    const validation = validateLines(lines);
    if (validation) {
      showToast(validation, "error");
      return;
    }
    const inv = await mutation.mutateAsync({
      paciente: patientId,
      itens: buildItensPayload(lines),
      ...(observacoes.trim() ? { observacoes: observacoes.trim() } : {}),
    });
    showToast("Fatura criada.", "success");
    const retornoQs = retorno ? `&retorno=${encodeURIComponent(retorno)}` : "";
    if (goReceipt) {
      void navigate(`/billing/invoices/${inv.id}?pagar=1${retornoQs}`);
    } else {
      void navigate(`/billing/invoices/${inv.id}${retorno ? `?retorno=${encodeURIComponent(retorno)}` : ""}`);
    }
  }

  if (servicesLoading && !services) {
    return <LoadingState message="A carregar catálogo operacional…" />;
  }

  return (
    <div className="space-y-6">
      <ReceptionAtendimentoBanner retorno={retorno} />
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-text sm:text-3xl">Nova fatura</h1>
          <p className="mt-1 text-sm text-text-muted">
            {retorno
              ? "Adicione os serviços e registe o pagamento integral na receção."
              : "Catálogo SauVida V1 · preço oficial e valor cobrado na mesma vista."}
          </p>
        </div>
        {retorno ? null : (
          <Link to="/billing/invoices" className="text-sm font-medium text-primary-600 hover:text-primary-700">
            ← Voltar à lista
          </Link>
        )}
      </div>

      <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_340px]">
        <div className="space-y-6">
          <Card title="Paciente">
            <PatientSearchSelect value={patientId} onChange={setPatientId} />
          </Card>

          <Card title="Serviços e itens">
            <ServiceSearchPicker
              services={services?.results ?? []}
              isLoading={servicesLoading}
              error={servicesError}
              onRetry={() => void refetch()}
              lines={lines}
              onChange={setLines}
              popularServiceIds={popularIds}
            />
          </Card>

          <label className="block text-sm">
            <span className="font-medium text-text">Observações internas</span>
            <textarea
              className="mt-1 w-full rounded-xl border border-border bg-surface px-3 py-2 text-sm"
              rows={2}
              value={observacoes}
              onChange={(e) => setObservacoes(e.target.value)}
              placeholder="Opcional — visível na ficha da fatura"
            />
          </label>
        </div>

        <div className="space-y-4">
          <InvoiceSummaryPanel lines={lines} />
          <div className="flex flex-col gap-2">
            <Button
              variant="primary"
              className="w-full"
              disabled={mutation.isPending}
              onClick={() => void submit(false)}
            >
              Guardar fatura
            </Button>
            <Button
              variant="secondary"
              className="w-full"
              disabled={mutation.isPending}
              onClick={() => void submit(true)}
            >
              Guardar e receber pagamento
            </Button>
            <Button variant="ghost" className="w-full" onClick={() => void navigate(-1)}>
              Cancelar
            </Button>
          </div>
          <p className="text-xs text-text-muted">
            Motivos de redução: {MOTIVOS_REDUCAO.length} opções configuradas. Autorização da Direção
            quando aplicável.
          </p>
        </div>
      </div>
    </div>
  );
}

import { useMutation, useQuery } from "@tanstack/react-query";
import { useEffect, useMemo, useRef, useState } from "react";
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
import {
  VISIT_PURPOSE_LABELS,
  VISIT_PURPOSE_SERVICE_CODIGO,
  type VisitPurpose,
} from "@/features/reception/constants/visitPurpose";
import { billingService } from "@/services/billing/billing.service";
import { patientsService } from "@/services/patients";
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

function parseVisitTipo(raw: string | null): VisitPurpose | null {
  if (raw === "CONSULTA" || raw === "CONTROLE") return raw;
  return null;
}

export function InvoiceCreatePage() {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [searchParams] = useSearchParams();
  const initialPatient = Number(searchParams.get("paciente")) || null;
  const prefillServicoId = Number(searchParams.get("servico")) || null;
  const pedidoLabId = Number(searchParams.get("pedido_lab")) || null;
  const retorno =
    searchParams.get("retorno") ||
    (pedidoLabId ? "/reception/lab-orders" : null);
  const visitTipo = parseVisitTipo(searchParams.get("tipo"));
  const fromLabSettle = Boolean(initialPatient && (pedidoLabId || prefillServicoId));
  const fromAtendimento = Boolean(retorno && initialPatient) || fromLabSettle;
  const suggestedCodigo = visitTipo ? VISIT_PURPOSE_SERVICE_CODIGO[visitTipo] : null;
  const prefillDone = useRef(false);

  const [patientId, setPatientId] = useState<number | null>(
    Number.isFinite(initialPatient) && initialPatient ? initialPatient : null,
  );
  const [lines, setLines] = useState<InvoiceLineDraft[]>([]);
  const [observacoes, setObservacoes] = useState("");

  const { data: lockedPatient } = useQuery({
    queryKey: ["patient-brief", patientId],
    queryFn: () => patientsService.get(patientId!),
    enabled: fromAtendimento && Boolean(patientId),
  });

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

  useEffect(() => {
    if (prefillDone.current || !prefillServicoId || !services?.results?.length) return;
    const svc = services.results.find((s) => s.id === prefillServicoId);
    if (!svc) return;
    prefillDone.current = true;
    setLines((prev) => {
      if (prev.some((l) => l.servico.id === svc.id)) return prev;
      return [...prev, { servico: svc, quantidade: 1 }];
    });
  }, [prefillServicoId, services?.results]);

  const mutation = useMutation({
    mutationFn: billingService.createInvoice,
    onError: (e) => showToast(getApiErrorMessage(e), "error"),
  });

  const popularIds = useMemo(
    () => services?.results.slice(0, 6).map((s) => s.id) ?? [],
    [services?.results],
  );

  function extraQs(base: string) {
    const parts = [base];
    if (retorno) parts.push(`retorno=${encodeURIComponent(retorno)}`);
    if (pedidoLabId) parts.push(`pedido_lab=${pedidoLabId}`);
    return parts.filter(Boolean).join("&");
  }

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
    if (goReceipt) {
      void navigate(`/billing/invoices/${inv.id}?${extraQs("pagar=1")}`);
    } else {
      const qs = extraQs("");
      void navigate(`/billing/invoices/${inv.id}${qs ? `?${qs}` : ""}`);
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
            {fromLabSettle
              ? "Retorno só para pagar exames — sem triagem. Confirme o serviço e cobre o utente."
              : retorno
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
            {fromAtendimento && patientId ? (
              <div className="rounded-xl border border-primary-200 bg-primary-50/50 px-4 py-3">
                <p className="text-xs font-semibold tracking-wide text-primary-700 uppercase">
                  {fromLabSettle ? "Utente — exames a regularizar" : "Utente do atendimento"}
                </p>
                <p className="mt-1 text-base font-semibold text-slate-900">
                  {lockedPatient?.full_name ?? "A carregar…"}
                </p>
                {lockedPatient?.patient_number ? (
                  <p className="text-sm text-slate-600">{lockedPatient.patient_number}</p>
                ) : null}
                {visitTipo ? (
                  <p className="mt-2 text-sm text-slate-600">
                    Tipo: {VISIT_PURPOSE_LABELS[visitTipo]}
                  </p>
                ) : null}
                <p className="mt-2 text-xs text-slate-500">
                  O utente está bloqueado neste fluxo para evitar troca acidental.
                </p>
              </div>
            ) : (
              <PatientSearchSelect value={patientId} onChange={setPatientId} />
            )}
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
              suggestedCodigo={suggestedCodigo}
              autoAddSuggested={fromAtendimento && Boolean(suggestedCodigo) && !prefillServicoId}
            />
          </Card>

          <label className="block text-sm">
            <span className="font-medium text-text">Observações internas</span>
            <textarea
              className="mt-1 w-full rounded-xl border border-border bg-surface px-3 py-2 text-sm"
              rows={2}
              value={observacoes}
              onChange={(e) => setObservacoes(e.target.value)}
              placeholder="Opcional. Visível na ficha da fatura"
            />
          </label>
        </div>

        <div className="space-y-4">
          <InvoiceSummaryPanel lines={lines} />
          <div className="flex flex-col gap-2">
            {retorno || fromLabSettle ? (
              <>
                <Button
                  variant="primary"
                  className="w-full"
                  disabled={mutation.isPending}
                  onClick={() => void submit(true)}
                >
                  Guardar e receber pagamento
                </Button>
                <Button
                  variant="secondary"
                  className="w-full"
                  disabled={mutation.isPending}
                  onClick={() => void submit(false)}
                >
                  Guardar fatura
                </Button>
              </>
            ) : (
              <>
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
              </>
            )}
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

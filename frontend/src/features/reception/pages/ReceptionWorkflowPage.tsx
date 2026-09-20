import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { useCallback, useEffect, useMemo, useState } from "react";

import { Button, Card } from "@/design-system";
import { ReceptionAtendimentoStepper } from "@/features/reception/components/ReceptionAtendimentoStepper";
import { ReceptionDoctorNotifyPanel } from "@/features/reception/components/ReceptionDoctorNotifyPanel";
import { PatientSearchSelect } from "@/features/reception/components/PatientSearchSelect";
import { TriageCheckInWizard } from "@/features/reception/components/TriageCheckInWizard";
import {
  buildAtendimentoUrl,
  encodeAtendimentoReturn,
  parseAtendimentoStep,
  type ReceptionAtendimentoStepId,
} from "@/features/reception/constants/atendimentoSteps";
import { useReceptionHotkeys } from "@/hooks/useReceptionHotkeys";
import { formatCurrency } from "@/features/billing/utils/formatBilling";
import { useReceptionPaymentReady } from "@/features/reception/hooks/useReceptionPaymentReady";
import { billingService } from "@/services/billing/billing.service";
import { patientsService } from "@/services/patients";
import type { PatientListItem } from "@/types/patient";
import type { CheckInResponse, VisitPurpose } from "@/types/reception";
import { VISIT_PURPOSE_LABELS } from "@/features/reception/constants/visitPurpose";

export function ReceptionWorkflowPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [searchParams, setSearchParams] = useSearchParams();

  const step = parseAtendimentoStep(searchParams.get("passo"));
  const patientIdParam = Number(searchParams.get("paciente")) || null;
  const queueIdParam = Number(searchParams.get("fila")) || null;

  const [selected, setSelected] = useState<PatientListItem | null>(null);
  const [queueEntryId, setQueueEntryId] = useState<number | null>(queueIdParam);
  const [visitPurpose, setVisitPurpose] = useState<VisitPurpose>("CONSULTA");

  const patientId = selected?.id ?? patientIdParam;
  const displayName = selected?.full_name ?? "Utente";

  const { isPaymentReady, partialInvoice, isLoading: paymentGateLoading } = useReceptionPaymentReady(
    patientId,
  );

  const { data: patientFromUrl } = useQuery({
    queryKey: ["patient-atendimento", patientIdParam],
    queryFn: () => patientsService.get(patientIdParam!),
    enabled: !!patientIdParam && !selected,
  });

  useEffect(() => {
    if (!patientFromUrl || selected) return;
    setSelected({
      id: patientFromUrl.id,
      full_name: patientFromUrl.full_name,
      first_name: patientFromUrl.first_name,
      last_name: patientFromUrl.last_name,
      patient_number: patientFromUrl.patient_number,
      phone: patientFromUrl.phone ?? null,
      birth_date: patientFromUrl.birth_date,
      gender: patientFromUrl.gender,
      is_active: patientFromUrl.is_active,
      created_at: patientFromUrl.created_at,
      updated_at: patientFromUrl.updated_at,
    });
  }, [patientFromUrl, selected]);

  useEffect(() => {
    if (queueIdParam) setQueueEntryId(queueIdParam);
  }, [queueIdParam]);

  const maxReachable = useMemo((): ReceptionAtendimentoStepId => {
    if (!patientId) return 1;
    if (!queueEntryId) return 2;
    if (isPaymentReady) return 4;
    return 3;
  }, [patientId, queueEntryId, isPaymentReady]);

  const goToStep = useCallback(
    (passo: ReceptionAtendimentoStepId) => {
      setSearchParams((prev) => {
        const next = new URLSearchParams(prev);
        next.set("passo", String(passo));
        if (patientId) next.set("paciente", String(patientId));
        if (queueEntryId) next.set("fila", String(queueEntryId));
        return next;
      });
    },
    [patientId, queueEntryId, setSearchParams],
  );

  const { data: receiptsData } = useQuery({
    queryKey: ["billing-receipts", "atendimento", patientId],
    queryFn: () => billingService.listReceipts({ page: 1, page_size: 30 }),
    enabled: step === 3 && !!patientId,
  });

  const patientReceipts = useMemo(() => {
    if (!selected || !receiptsData?.results) return [];
    return receiptsData.results.filter((r) => r.paciente_nome === selected.full_name).slice(0, 5);
  }, [receiptsData?.results, selected]);

  useEffect(() => {
    if (step !== 4 || paymentGateLoading || isPaymentReady || !patientId) return;
    goToStep(3);
  }, [step, paymentGateLoading, isPaymentReady, patientId, goToStep]);

  /** Já pago: saltar o ecrã intermédio e ir directamente escolher o médico. */
  useEffect(() => {
    if (step !== 3 || paymentGateLoading || !isPaymentReady || !patientId) return;
    goToStep(4);
  }, [step, paymentGateLoading, isPaymentReady, patientId, goToStep]);

  const returnAfterPay = encodeAtendimentoReturn({
    passo: 4,
    paciente: patientId,
    queue: queueEntryId,
  });

  useReceptionHotkeys(true, {
    onRefresh: () => {
      void queryClient.invalidateQueries({ queryKey: ["reception-dashboard"] });
      void queryClient.invalidateQueries({ queryKey: ["reception-queue"] });
      void queryClient.invalidateQueries({ queryKey: ["billing-receipts"] });
      void queryClient.invalidateQueries({ queryKey: ["billing-invoices"] });
    },
    onCancel: () => {
      setSelected(null);
      setQueueEntryId(null);
      void navigate("/dashboard/reception");
    },
  });

  function onPatientChange(id: number | null) {
    if (!id) {
      setSelected(null);
      setSearchParams({ passo: "1" });
    }
  }

  function onPatientSelect(patient: PatientListItem | null) {
    setSelected(patient);
    if (patient) {
      setSearchParams({
        passo: "2",
        paciente: String(patient.id),
      });
    }
  }

  function onTriageComplete(result: CheckInResponse) {
    setQueueEntryId(result.queue_entry.id);
    const purpose = result.check_in.visit_purpose;
    setVisitPurpose(purpose === "CONSULTA" || purpose === "CONTROLE" ? purpose : "CONSULTA");
    setSearchParams({
      passo: "3",
      paciente: String(result.check_in.patient.id),
      fila: String(result.queue_entry.id),
    });
    void queryClient.invalidateQueries({ queryKey: ["reception-dashboard"] });
  }

  const patientSummary = selected
    ? {
        id: selected.id,
        full_name: selected.full_name,
        patient_number: selected.patient_number,
        phone: selected.phone ?? null,
        birth_date: selected.birth_date ?? null,
      }
    : null;

  const invoiceNewUrl =
    patientId &&
    `/billing/invoices/new?paciente=${patientId}&pagar=1&tipo=${visitPurpose}&retorno=${returnAfterPay}`;

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-xs font-semibold tracking-widest text-emerald-700 uppercase">Receção</p>
          <h1 className="text-2xl font-bold tracking-tight text-text sm:text-3xl">Atendimento do utente</h1>
          <p className="mt-1 text-sm text-text-muted">
            Triagem → <strong className="font-semibold text-text">pagamento e recibo</strong> → só depois encaminhar
            para o médico.
          </p>
        </div>
        <Link
          to="/dashboard/reception"
          className="text-sm font-semibold text-primary-600 hover:text-primary-700"
        >
          ← Painel
        </Link>
      </div>

      <ReceptionAtendimentoStepper
        current={step}
        maxReachable={maxReachable}
        onStepClick={(s) => {
          if (s === 1 || (patientId && s <= maxReachable)) goToStep(s);
        }}
      />

      {step === 1 && (
        <Card title="1. Identificar utente" description="Pesquise por nome, telefone ou n.º de processo.">
          <PatientSearchSelect
            value={patientId}
            onChange={onPatientChange}
            onSelectPatient={onPatientSelect}
          />
          <div className="mt-6 flex flex-wrap gap-2 border-t border-border pt-6">
            <Link to={`/patients/new?retorno=${encodeAtendimentoReturn({ passo: 1 })}`}>
              <Button variant="outline">Registar novo paciente (ficha completa)</Button>
            </Link>
          </div>
        </Card>
      )}

      {step === 2 && patientId && (
        <div className="space-y-4">
          <TriageCheckInWizard
            initialPatientId={patientId}
            initialPatientSummary={patientSummary}
            hideProgressNav
            onCheckInSuccess={onTriageComplete}
          />
          <Button type="button" variant="ghost" onClick={() => goToStep(1)}>
            ← Alterar utente
          </Button>
        </div>
      )}

      {step === 2 && !patientId && (
        <Card title="Seleccione um utente">
          <p className="text-sm text-text-muted">Volte ao passo 1 para escolher o paciente.</p>
          <Button type="button" className="mt-4" onClick={() => goToStep(1)}>
            Ir para passo 1
          </Button>
        </Card>
      )}

      {step === 3 && patientId && (
        <Card
          title="3. Pagamento e recibo"
          description="Na SauVida o utente paga na receção antes da consulta. Emita o recibo e entregue-o ao paciente."
        >
          <p className="text-sm text-text-muted">
            Utente: <strong className="text-text">{displayName}</strong>
            <span className="ml-2 text-xs">
              · {VISIT_PURPOSE_LABELS[visitPurpose]}
            </span>
          </p>

          <p className="mt-2 text-xs text-text-muted">
            Na fatura pode ajustar o preço (redução) com motivo registado, por exemplo dificuldade financeira.
          </p>

          <div className="mt-6 flex flex-wrap gap-3">
            {invoiceNewUrl ? (
              <Link to={invoiceNewUrl}>
                <Button variant="primary">Criar fatura e cobrar</Button>
              </Link>
            ) : null}
          </div>

          <p className="mt-4 text-xs text-text-muted">
            O utente deve pagar o <strong>valor total</strong> da fatura de hoje antes da consulta. O recibo
            abre após confirmar o pagamento.
          </p>

          {partialInvoice && !isPaymentReady ? (
            <div
              className="mt-4 rounded-xl border border-amber-200 bg-amber-50 p-4 dark:border-amber-900/50 dark:bg-amber-950/30"
              role="alert"
            >
              <p className="text-sm font-semibold text-amber-900 dark:text-amber-200">Pagamento incompleto</p>
              <p className="mt-1 text-sm text-amber-800/90 dark:text-amber-100/90">
                Fatura {partialInvoice.numero}: pago {formatCurrency(partialInvoice.total_pago)} de{" "}
                {formatCurrency(partialInvoice.total)}.
              </p>
              <Link
                className="mt-3 inline-block"
                to={`/billing/invoices/${partialInvoice.id}?pagar=1&retorno=${returnAfterPay}`}
              >
                <Button size="sm" variant="primary">
                  Completar pagamento
                </Button>
              </Link>
            </div>
          ) : null}

          {isPaymentReady ? (
            <div className="mt-6 rounded-xl border border-emerald-200 bg-emerald-50/80 p-4 dark:border-emerald-900/40 dark:bg-emerald-950/30">
              <p className="text-sm font-semibold text-emerald-900 dark:text-emerald-200">Pagamento registado</p>
              {patientReceipts.length > 0 ? (
                <ul className="mt-3 space-y-2">
                  {patientReceipts.map((r) => (
                    <li key={r.id} className="flex flex-wrap items-center justify-between gap-2 text-sm">
                      <span className="font-medium text-text">{r.numero}</span>
                      <Link to={`/billing/receipts/${r.id}?imprimir=1&retorno=${returnAfterPay}`}>
                        <Button size="sm" variant="secondary">
                          Reimprimir
                        </Button>
                      </Link>
                    </li>
                  ))}
                </ul>
              ) : null}
              <Button
                type="button"
                className="mt-4"
                variant="primary"
                disabled={!isPaymentReady}
                onClick={() => goToStep(4)}
              >
                Pagamento feito. Ir para o médico →
              </Button>
            </div>
          ) : null}

        <p className="mt-4 text-xs text-amber-800 dark:text-amber-200">
          O passo «Médico» só abre com fatura de hoje totalmente paga.
        </p>

          <Button type="button" variant="ghost" className="mt-4" onClick={() => goToStep(2)}>
            ← Triagem
          </Button>
        </Card>
      )}

      {step === 4 && isPaymentReady && (
        <>
          <ReceptionDoctorNotifyPanel
            queueEntryId={queueEntryId}
            patientId={patientId}
            patientName={displayName}
            paidFirst
            paymentConfirmed
          />
          <Card title="Concluir atendimento">
            <p className="text-sm text-text-muted">
              Depois de cobrar e notificar o médico, o utente pode aguardar a chamada para consulta.
            </p>
            <div className="mt-4 flex flex-wrap gap-2">
              <Link to={buildAtendimentoUrl({ passo: 1 })}>
                <Button variant="primary">Novo atendimento</Button>
              </Link>
              <Link to="/reception/queue">
                <Button type="button" variant="secondary">
                  Abrir fila
                </Button>
              </Link>
            </div>
          </Card>
        </>
      )}
    </div>
  );
}

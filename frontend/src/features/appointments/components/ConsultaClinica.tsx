import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Link } from "react-router-dom";

import { Badge, Button, Card, ErrorState, useToast } from "@/design-system";
import { AutoSaveIndicator } from "@/features/appointments/components/AutoSaveIndicator";
import { ConsultationPatientHeader } from "@/features/appointments/components/ConsultationPatientHeader";
import { ConsultationSidebar } from "@/features/appointments/components/ConsultationSidebar";
import { ConsultationSkeleton } from "@/features/appointments/components/AppointmentsSkeleton";
import { ConsultationSubNav } from "@/features/appointments/components/ConsultationSubNav";
import { DiagnosticosTab } from "@/features/appointments/components/DiagnosticosTab";
import { PedidosImagiologia } from "@/features/appointments/components/PedidosImagiologia";
import { PedidosLaboratorio } from "@/features/appointments/components/PedidosLaboratorio";
import { ResultadosLaboratorioTab } from "@/features/appointments/components/ResultadosLaboratorioTab";
import { SeguimentoForm } from "@/features/appointments/components/SeguimentoForm";
import { SinaisVitaisForm } from "@/features/appointments/components/SinaisVitaisForm";
import { SOAPForm } from "@/features/appointments/components/SOAPForm";
import { AppointmentStatusBadge } from "@/features/appointments/components/AppointmentStatusBadge";
import { PrescricaoForm } from "@/features/doctors/components/PrescricaoForm";
import { appointmentsService } from "@/services/appointments";
import { doctorsService } from "@/services/doctors";
import type { MedicamentoPrescrito } from "@/types/doctors";
import type { ClinicalTab } from "@/types/clinicalRecord";
import type { AppointmentStatus } from "@/types/appointment";
import { getApiErrorMessage } from "@/utils/api-error";
import { formatDisplayDateTime } from "@/utils/date";

const EHR_TABS: { id: ClinicalTab; label: string }[] = [
  { id: "resumo", label: "Resumo" },
  { id: "vitais", label: "Sinais Vitais" },
  { id: "soap", label: "Notas SOAP" },
  { id: "diagnosticos", label: "Diagnósticos" },
  { id: "laboratorio", label: "Laboratório" },
  { id: "prescricao", label: "Prescrição" },
  { id: "imagiologia", label: "Imagiologia" },
  { id: "seguimento", label: "Seguimento" },
];

interface ConsultaClinicaProps {
  appointmentId: number;
}

export function ConsultaClinica({ appointmentId }: ConsultaClinicaProps) {
  const { showToast } = useToast();
  const queryClient = useQueryClient();
  const [tab, setTab] = useState<ClinicalTab>("resumo");
  const [lastSaved, setLastSaved] = useState<Date | null>(null);

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["clinical-record", appointmentId],
    queryFn: () => appointmentsService.getClinicalRecord(appointmentId),
    enabled: Number.isFinite(appointmentId),
  });

  const invalidate = () => {
    void queryClient.invalidateQueries({ queryKey: ["clinical-record", appointmentId] });
    void queryClient.invalidateQueries({ queryKey: ["appointment", appointmentId] });
  };

  const onSaved = () => setLastSaved(new Date());

  const vitalsMutation = useMutation({
    mutationFn: (payload: object) => appointmentsService.saveVitalSigns(appointmentId, payload),
    onSuccess: () => { showToast("Sinais vitais guardados.", "success"); onSaved(); invalidate(); },
    onError: (e) => showToast(getApiErrorMessage(e), "error"),
  });

  const soapMutation = useMutation({
    mutationFn: (payload: object) =>
      appointmentsService.updateClinical(appointmentId, payload as Record<string, string>),
    onSuccess: () => { onSaved(); invalidate(); },
    onError: (e) => showToast(getApiErrorMessage(e), "error"),
  });

  const diagnosisMutation = useMutation({
    mutationFn: (payload: { codigo_cid10: string; descricao: string; tipo: string }) =>
      appointmentsService.addDiagnosis(appointmentId, payload),
    onSuccess: () => { showToast("Diagnóstico adicionado.", "success"); onSaved(); invalidate(); },
    onError: (e) => showToast(getApiErrorMessage(e), "error"),
  });

  const labMutation = useMutation({
    mutationFn: (payload: object) => appointmentsService.addLabOrder(
      appointmentId,
      payload as { tipo_exame?: string; servico_id?: number },
    ),
    onSuccess: () => { showToast("Pedido de laboratório emitido.", "success"); onSaved(); invalidate(); },
    onError: (e) => showToast(getApiErrorMessage(e), "error"),
  });

  const imagingMutation = useMutation({
    mutationFn: (payload: object) => appointmentsService.addImagingOrder(appointmentId, payload as { tipo_exame: string }),
    onSuccess: () => { showToast("Pedido de imagiologia emitido.", "success"); onSaved(); invalidate(); },
    onError: (e) => showToast(getApiErrorMessage(e), "error"),
  });

  const followUpMutation = useMutation({
    mutationFn: (payload: { data_retorno: string; motivo: string; observacoes?: string }) =>
      appointmentsService.saveFollowUp(appointmentId, payload),
    onSuccess: () => { showToast("Recomendação de seguimento registada.", "success"); onSaved(); invalidate(); },
    onError: (e) => showToast(getApiErrorMessage(e), "error"),
  });

  const prescriptionMutation = useMutation({
    mutationFn: (payload: {
      consulta_id: number;
      observacoes?: string;
      medicamentos: MedicamentoPrescrito[];
    }) => doctorsService.createPrescription(payload),
    onSuccess: () => {
      showToast("Prescrição criada.", "success");
      onSaved();
      void queryClient.invalidateQueries({ queryKey: ["doctor-prescriptions"] });
    },
    onError: (e) => showToast(getApiErrorMessage(e), "error"),
  });

  const finishMutation = useMutation({
    mutationFn: () => appointmentsService.finish(appointmentId),
    onSuccess: () => {
      showToast("Consulta concluída.", "success");
      invalidate();
      void queryClient.invalidateQueries({ queryKey: ["consultation-queue"] });
    },
    onError: (e) => showToast(getApiErrorMessage(e), "error"),
  });

  const isSaving =
    vitalsMutation.isPending ||
    soapMutation.isPending ||
    diagnosisMutation.isPending ||
    labMutation.isPending ||
    imagingMutation.isPending ||
    followUpMutation.isPending ||
    prescriptionMutation.isPending;

  if (isLoading || !data) return <ConsultationSkeleton />;
  if (isError) return <ErrorState message="Não foi possível carregar o prontuário." onRetry={() => void refetch()} />;

  const editavel = data.consulta.editavel;

  return (
    <div className="space-y-6 pb-24">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900 sm:text-2xl">Prontuário Electrónico</h1>
          <p className="text-sm text-slate-500">Registo clínico da consulta</p>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <AutoSaveIndicator isSaving={isSaving} lastSaved={lastSaved} />
          <AppointmentStatusBadge status={data.consulta.status as AppointmentStatus} />
        </div>
      </div>

      <ConsultationSubNav />

      <div className="grid gap-6 xl:grid-cols-[1fr_300px]">
        <div className="min-w-0 space-y-6">
          <ConsultationPatientHeader paciente={data.paciente} consulta={data.consulta} />

          <nav
            className="flex gap-1 overflow-x-auto rounded-2xl border border-slate-200/80 bg-white p-1.5 shadow-sm"
            aria-label="Secções do prontuário"
          >
            {EHR_TABS.map((t) => (
              <button
                key={t.id}
                type="button"
                onClick={() => setTab(t.id)}
                className={`shrink-0 rounded-xl px-4 py-2.5 text-sm font-medium transition focus-ring ${
                  tab === t.id
                    ? "bg-primary-600 text-white shadow-md shadow-primary-600/20"
                    : "text-slate-600 hover:bg-slate-100"
                }`}
              >
                {t.label}
              </button>
            ))}
          </nav>

          <div className="animate-fade-in">
            {tab === "resumo" && (
              <Card title="Resumo da consulta">
                <dl className="grid gap-4 text-sm sm:grid-cols-2">
                  <div>
                    <dt className="text-xs font-semibold text-slate-400 uppercase">Motivo</dt>
                    <dd className="mt-1 text-slate-900">{data.consulta.chief_complaint || "—"}</dd>
                  </div>
                  <div>
                    <dt className="text-xs font-semibold text-slate-400 uppercase">Início</dt>
                    <dd className="mt-1 text-slate-900">
                      {data.consulta.started_at ? formatDisplayDateTime(data.consulta.started_at) : "—"}
                    </dd>
                  </div>
                  <div className="sm:col-span-2">
                    <dt className="text-xs font-semibold text-slate-400 uppercase">Notas clínicas</dt>
                    <dd className="mt-1 text-slate-700">{data.consulta.clinical_notes || "—"}</dd>
                  </div>
                  <div className="sm:col-span-2">
                    <dt className="text-xs font-semibold text-slate-400 uppercase">Diagnóstico</dt>
                    <dd className="mt-1 text-slate-700">{data.consulta.diagnosis || "—"}</dd>
                  </div>
                </dl>
                <Link
                  to={`/patients/${data.paciente.id}`}
                  className="mt-4 inline-block text-sm font-medium text-primary-600 hover:text-primary-700"
                >
                  Ver ficha completa do paciente →
                </Link>
              </Card>
            )}

            {tab === "vitais" && (
              <SinaisVitaisForm
                initial={data.sinais_vitais}
                triage={data.sinais_vitais_triagem}
                disabled={!editavel}
                onSubmit={(v) => vitalsMutation.mutate(v)}
                isPending={vitalsMutation.isPending}
              />
            )}

            {tab === "soap" && (
              <SOAPForm
                initial={data.anotacao_soap}
                disabled={!editavel}
                onSubmit={(v) => soapMutation.mutate(v)}
                onAutosave={(v: import("@/types/clinicalRecord").SOAPNote) => soapMutation.mutate(v)}
                isPending={soapMutation.isPending}
              />
            )}

            {tab === "diagnosticos" && (
              <DiagnosticosTab
                diagnosticos={data.diagnosticos}
                disabled={!editavel}
                onAdd={(d) => diagnosisMutation.mutate(d)}
                isPending={diagnosisMutation.isPending}
              />
            )}

            {tab === "laboratorio" && (
              <div className="space-y-6">
                <PedidosLaboratorio
                  pedidos={data.pedidos_laboratorio}
                  disabled={!editavel}
                  onAdd={(d) => labMutation.mutateAsync(d)}
                  isPending={labMutation.isPending}
                />
                <ResultadosLaboratorioTab resultados={data.resultados_laboratoriais ?? []} />
              </div>
            )}

            {tab === "imagiologia" && (
              <PedidosImagiologia
                pedidos={data.pedidos_imagiologia}
                disabled={!editavel}
                onAdd={(d) => imagingMutation.mutate(d)}
                isPending={imagingMutation.isPending}
              />
            )}

            {tab === "prescricao" && (
              <Card title="Prescrição">
                <PrescricaoForm
                  consultaId={appointmentId}
                  onSubmit={(values) => prescriptionMutation.mutate(values)}
                  isPending={prescriptionMutation.isPending}
                />
              </Card>
            )}

            {tab === "seguimento" && (
              <SeguimentoForm
                initial={data.seguimento}
                disabled={!editavel}
                onSubmit={(d) => followUpMutation.mutate(d)}
                isPending={followUpMutation.isPending}
              />
            )}

            {!editavel && (
              <Badge variant="default" className="mt-4">
                Prontuário bloqueado. Consulta concluída.
              </Badge>
            )}
          </div>
        </div>

        <ConsultationSidebar data={data} />
      </div>

      {editavel && (
        <div className="fixed right-0 bottom-0 left-0 z-40 border-t border-slate-200 bg-white/95 px-4 py-3 backdrop-blur-md lg:left-64">
          <div className="mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-3">
            <AutoSaveIndicator isSaving={isSaving} lastSaved={lastSaved} />
            <div className="flex gap-2">
              <Link to="/consultations/queue">
                <Button variant="outline">Voltar à fila</Button>
              </Link>
              <Button
                variant="primary"
                onClick={() => finishMutation.mutate()}
                disabled={finishMutation.isPending}
                isLoading={finishMutation.isPending}
              >
                Concluir consulta
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

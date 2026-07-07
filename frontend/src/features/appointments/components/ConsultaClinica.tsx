import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Link } from "react-router-dom";

import { Badge, Button, Card, ErrorState, LoadingState, Table, useToast } from "@/design-system";
import { APPOINTMENT_STATUS_LABELS } from "@/constants/appointments";
import { AppointmentStatusBadge } from "@/features/appointments/components/AppointmentStatusBadge";
import { ConsultationSubNav } from "@/features/appointments/components/ConsultationSubNav";
import { DiagnosticosTab } from "@/features/appointments/components/DiagnosticosTab";
import { PedidosImagiologia } from "@/features/appointments/components/PedidosImagiologia";
import { PedidosLaboratorio } from "@/features/appointments/components/PedidosLaboratorio";
import { ResultadosLaboratorioTab } from "@/features/appointments/components/ResultadosLaboratorioTab";
import { ResumoPaciente } from "@/features/appointments/components/ResumoPaciente";
import { SeguimentoForm } from "@/features/appointments/components/SeguimentoForm";
import { SinaisVitaisForm } from "@/features/appointments/components/SinaisVitaisForm";
import { SOAPForm } from "@/features/appointments/components/SOAPForm";
import { CLINICAL_TABS } from "@/features/appointments/utils/vitals";
import { appointmentsService } from "@/services/appointments";
import type { ClinicalTab } from "@/types/clinicalRecord";
import type { AppointmentStatus } from "@/types/appointment";
import { getApiErrorMessage } from "@/utils/api-error";
import { formatDisplayDateTime } from "@/utils/date";

interface ConsultaClinicaProps {
  appointmentId: number;
}

export function ConsultaClinica({ appointmentId }: ConsultaClinicaProps) {
  const { showToast } = useToast();
  const queryClient = useQueryClient();
  const [tab, setTab] = useState<ClinicalTab>("resumo");

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["clinical-record", appointmentId],
    queryFn: () => appointmentsService.getClinicalRecord(appointmentId),
    enabled: Number.isFinite(appointmentId),
  });

  const invalidate = () => {
    void queryClient.invalidateQueries({ queryKey: ["clinical-record", appointmentId] });
    void queryClient.invalidateQueries({ queryKey: ["appointment", appointmentId] });
  };

  const vitalsMutation = useMutation({
    mutationFn: (payload: object) => appointmentsService.saveVitalSigns(appointmentId, payload),
    onSuccess: () => { showToast("Sinais vitais guardados.", "success"); invalidate(); },
    onError: (e) => showToast(getApiErrorMessage(e), "error"),
  });

  const soapMutation = useMutation({
    mutationFn: (payload: object) =>
      appointmentsService.updateClinical(appointmentId, payload as Record<string, string>),
    onSuccess: () => { showToast("SOAP guardado.", "success"); invalidate(); },
    onError: (e) => showToast(getApiErrorMessage(e), "error"),
  });

  const diagnosisMutation = useMutation({
    mutationFn: (payload: { codigo_cid10: string; descricao: string; tipo: string }) =>
      appointmentsService.addDiagnosis(appointmentId, payload),
    onSuccess: () => { showToast("Diagnóstico adicionado.", "success"); invalidate(); },
    onError: (e) => showToast(getApiErrorMessage(e), "error"),
  });

  const labMutation = useMutation({
    mutationFn: (payload: object) => appointmentsService.addLabOrder(appointmentId, payload as { tipo_exame: string }),
    onSuccess: () => { showToast("Pedido de laboratório emitido.", "success"); invalidate(); },
    onError: (e) => showToast(getApiErrorMessage(e), "error"),
  });

  const imagingMutation = useMutation({
    mutationFn: (payload: object) => appointmentsService.addImagingOrder(appointmentId, payload as { tipo_exame: string }),
    onSuccess: () => { showToast("Pedido de imagiologia emitido.", "success"); invalidate(); },
    onError: (e) => showToast(getApiErrorMessage(e), "error"),
  });

  const followUpMutation = useMutation({
    mutationFn: (payload: { data_retorno: string; motivo: string; observacoes?: string }) =>
      appointmentsService.saveFollowUp(appointmentId, payload),
    onSuccess: () => { showToast("Seguimento agendado.", "success"); invalidate(); },
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

  if (isLoading || !data) return <LoadingState message="A carregar prontuário clínico..." />;
  if (isError) return <ErrorState message="Não foi possível carregar o prontuário." onRetry={() => void refetch()} />;

  const editavel = data.consulta.editavel;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">Prontuário clínico</h2>
          <p className="text-sm text-slate-500">{data.consulta.appointment_number}</p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <AppointmentStatusBadge status={data.consulta.status as AppointmentStatus} />
          {editavel && (
            <Button variant="primary" onClick={() => finishMutation.mutate()} disabled={finishMutation.isPending}>
              Concluir consulta
            </Button>
          )}
        </div>
      </div>

      <ConsultationSubNav />
      <ResumoPaciente paciente={data.paciente} />

      <div className="flex flex-wrap gap-1 border-b border-slate-200">
        {CLINICAL_TABS.map((t) => (
          <button
            key={t.id}
            type="button"
            onClick={() => setTab(t.id as ClinicalTab)}
            className={`px-4 py-2 text-sm font-medium transition-colors ${
              tab === t.id
                ? "border-b-2 border-primary-600 text-primary-700"
                : "text-slate-500 hover:text-slate-800"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === "resumo" && (
        <Card title="Resumo da consulta">
          <dl className="grid gap-3 text-sm sm:grid-cols-2">
            <div>
              <dt className="text-slate-500">Motivo</dt>
              <dd>{data.consulta.chief_complaint || "—"}</dd>
            </div>
            <div>
              <dt className="text-slate-500">Início</dt>
              <dd>{data.consulta.started_at ? formatDisplayDateTime(data.consulta.started_at) : "—"}</dd>
            </div>
            <div className="sm:col-span-2">
              <dt className="text-slate-500">Notas clínicas</dt>
              <dd>{data.consulta.clinical_notes || "—"}</dd>
            </div>
          </dl>
          <Link to={`/patients/${data.paciente.id}`} className="mt-4 inline-block text-sm font-medium text-primary-700 hover:underline">
            Ver ficha completa do paciente
          </Link>
        </Card>
      )}

      {tab === "vitais" && (
        <SinaisVitaisForm
          initial={data.sinais_vitais}
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
        <PedidosLaboratorio
          pedidos={data.pedidos_laboratorio}
          disabled={!editavel}
          onAdd={(d) => labMutation.mutate(d)}
          isPending={labMutation.isPending}
        />
      )}

      {tab === "resultados_laboratorio" && (
        <ResultadosLaboratorioTab resultados={data.resultados_laboratoriais ?? []} />
      )}

      {tab === "imagiologia" && (
        <PedidosImagiologia
          pedidos={data.pedidos_imagiologia}
          disabled={!editavel}
          onAdd={(d) => imagingMutation.mutate(d)}
          isPending={imagingMutation.isPending}
        />
      )}

      {tab === "seguimento" && (
        <SeguimentoForm
          initial={data.seguimento}
          disabled={!editavel}
          onSubmit={(d) => followUpMutation.mutate(d)}
          isPending={followUpMutation.isPending}
        />
      )}

      {tab === "historico" && (
        <div className="space-y-4">
          <Card title="Últimas consultas">
            <Table<(typeof data.ultimas_consultas)[number]>
              data={data.ultimas_consultas}
              getRowKey={(row) => row.id}
              emptyMessage="Sem histórico."
              columns={[
                { key: "appointment_number", header: "N.º" },
                {
                  key: "scheduled_at",
                  header: "Data",
                  render: (row) => formatDisplayDateTime(row.scheduled_at),
                },
                {
                  key: "status",
                  header: "Estado",
                  render: (row) => (
                    <Badge>{APPOINTMENT_STATUS_LABELS[row.status as AppointmentStatus]}</Badge>
                  ),
                },
                { key: "diagnosis", header: "Diagnóstico" },
              ]}
            />
          </Card>
          {!editavel && (
            <Badge variant="default">Prontuário bloqueado — consulta concluída.</Badge>
          )}
        </div>
      )}
    </div>
  );
}

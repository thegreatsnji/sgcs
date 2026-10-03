import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { Badge, Button, Card, ErrorState, LoadingState, useToast } from "@/design-system";
import { AppointmentStatusBadge } from "@/features/appointments/components/AppointmentStatusBadge";
import { AppointmentSubNav } from "@/features/appointments/components/AppointmentSubNav";
import { appointmentsService } from "@/services/appointments";
import { getApiErrorMessage } from "@/utils/api-error";
import { formatDisplayDateTime } from "@/utils/date";

export function AppointmentDetailPage() {
  const { id } = useParams<{ id: string }>();
  const appointmentId = Number(id);
  const { showToast } = useToast();
  const queryClient = useQueryClient();
  const [diagnosis, setDiagnosis] = useState("");
  const [clinicalNotes, setClinicalNotes] = useState("");

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["appointment", appointmentId],
    queryFn: () => appointmentsService.get(appointmentId),
    enabled: Number.isFinite(appointmentId),
  });

  useEffect(() => {
    if (!data) return;
    setDiagnosis(data.diagnosis);
    setClinicalNotes(data.clinical_notes);
  }, [data]);

  const finishMutation = useMutation({
    mutationFn: () => appointmentsService.finish(appointmentId, { diagnosis, clinical_notes: clinicalNotes }),
    onSuccess: () => {
      showToast("Consulta concluída.", "success");
      void queryClient.invalidateQueries({ queryKey: ["appointment", appointmentId] });
    },
    onError: (e) => showToast(getApiErrorMessage(e), "error"),
  });

  const startMutation = useMutation({
    mutationFn: () => appointmentsService.start(appointmentId),
    onSuccess: () => {
      showToast("Consulta iniciada.", "success");
      void refetch();
    },
    onError: (e) => showToast(getApiErrorMessage(e), "error"),
  });

  if (!Number.isFinite(appointmentId)) return <ErrorState message="Consulta inválida." />;
  if (isLoading || !data) return <LoadingState message="A carregar consulta..." />;
  if (isError) return <ErrorState message="Erro ao carregar." onRetry={() => void refetch()} />;

  const editable = data.status === "EM_CONSULTA";

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">Consulta {data.appointment_number}</h2>
          <p className="text-slate-600">{data.patient.full_name}</p>
        </div>
        <AppointmentStatusBadge status={data.status} />
      </div>
      <AppointmentSubNav />
      <div className="grid gap-6 lg:grid-cols-2">
        <Card title="Informação">
          <dl className="space-y-2 text-sm">
            <div><dt className="text-slate-500">Data/hora</dt><dd>{formatDisplayDateTime(data.scheduled_at)}</dd></div>
            <div><dt className="text-slate-500">Médico</dt><dd>{data.doctor?.full_name ?? "—"}</dd></div>
            <div><dt className="text-slate-500">Duração</dt><dd>{data.duration_minutes} min</dd></div>
            <div><dt className="text-slate-500">Motivo</dt><dd>{data.chief_complaint || "—"}</dd></div>
            <Link to={`/appointments/${data.id}/edit`} className="text-primary-700 hover:underline">Editar consulta</Link>
            <Link to={`/patients/${data.patient.id}`} className="block text-primary-700 hover:underline">Ficha do paciente</Link>
          </dl>
        </Card>
        <Card title="Registo clínico">
          <div className="space-y-3">
            <textarea value={diagnosis} onChange={(e) => setDiagnosis(e.target.value)} disabled={!editable} rows={3} className="w-full rounded-lg border px-3 py-2 text-sm" placeholder="Diagnóstico" />
            <textarea value={clinicalNotes} onChange={(e) => setClinicalNotes(e.target.value)} disabled={!editable} rows={4} className="w-full rounded-lg border px-3 py-2 text-sm" placeholder="Notas clínicas" />
            {data.status === "CONFIRMADA" || data.status === "EM_ESPERA" ? (
              <Button onClick={() => startMutation.mutate()} disabled={startMutation.isPending}>Iniciar consulta</Button>
            ) : null}
            {editable && (
              <Button onClick={() => finishMutation.mutate()} disabled={finishMutation.isPending}>Concluir consulta</Button>
            )}
            {data.status === "CONCLUIDA" && <Badge variant="success">Consulta concluída</Badge>}
          </div>
        </Card>
      </div>
    </div>
  );
}

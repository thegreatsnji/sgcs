import { useMutation, useQuery } from "@tanstack/react-query";
import { useEffect, useState } from "react";

import { Button, Card, useToast } from "@/design-system";
import { receptionService } from "@/services/reception";
import { getApiErrorMessage } from "@/utils/api-error";

export interface ReceptionDoctorNotifyPanelProps {
  queueEntryId: number | null;
  patientId: number | null;
  patientName: string;
  /** Fluxo SauVida: pagamento já efectuado na receção. */
  paidFirst?: boolean;
  /** Pagamento confirmado hoje — obrigatório antes de notificar médico. */
  paymentConfirmed?: boolean;
  onNotified?: () => void;
  onSkip?: () => void;
}

export function ReceptionDoctorNotifyPanel({
  queueEntryId,
  patientId,
  patientName,
  paidFirst = false,
  paymentConfirmed = true,
  onNotified,
  onSkip,
}: ReceptionDoctorNotifyPanelProps) {
  const { showToast } = useToast();
  const [doctorId, setDoctorId] = useState<number | null>(null);

  const { data: doctorOptions, isLoading: doctorsLoading } = useQuery({
    queryKey: ["doctor-assignment-options", patientId],
    queryFn: () => receptionService.getDoctorAssignmentOptions(patientId!),
    enabled: paymentConfirmed && patientId != null,
  });

  useEffect(() => {
    if (doctorOptions?.suggested_doctor_id) {
      setDoctorId(doctorOptions.suggested_doctor_id);
    }
  }, [doctorOptions?.suggested_doctor_id]);

  const assignMutation = useMutation({
    mutationFn: () => {
      if (!queueEntryId) throw new Error("Sem entrada na fila.");
      if (!doctorId) throw new Error("Seleccione o médico.");
      return receptionService.assignToDoctor({ queue_id: queueEntryId, doctor_id: doctorId });
    },
    onSuccess: (result) => {
      const doctorLabel = result.consulta?.doctor_name ?? "médico";
      showToast(`Utente atribuído a ${doctorLabel}.`, "success");
      onNotified?.();
    },
    onError: (e) => showToast(getApiErrorMessage(e), "error"),
  });

  const callMutation = useMutation({
    mutationFn: () => {
      if (!queueEntryId) throw new Error("Sem entrada na fila.");
      return receptionService.updateQueueEntry(queueEntryId, { status: "CALLED" });
    },
    onSuccess: () => showToast("Utente chamado (sala de espera).", "success"),
    onError: (e) => showToast(getApiErrorMessage(e), "error"),
  });

  if (!paymentConfirmed) {
    return (
      <Card title="4. Encaminhar para médico" description="Pagamento em falta">
        <p className="text-sm text-text-muted">
          Registe o pagamento e imprima o recibo no <strong>passo 3</strong> antes de notificar o médico.
        </p>
      </Card>
    );
  }

  if (!queueEntryId) {
    return (
      <Card title="4. Encaminhar para médico" description="Conclua a triagem e o pagamento antes deste passo.">
        <p className="text-sm text-text-muted">
          Sem registo na fila. Volte à <strong>triagem</strong> ou continue a partir do painel da receção.
        </p>
        {onSkip ? (
          <Button type="button" variant="outline" className="mt-4" onClick={onSkip}>
            Voltar
          </Button>
        ) : null}
      </Card>
    );
  }

  const preferred = doctorOptions?.preferred_doctor;

  return (
    <Card
      title="4. Atribuir médico"
      description={
        paidFirst
          ? `${patientName} já pagou. Escolha o médico — o utente habitual é sugerido se estiver disponível.`
          : `${patientName} está na fila. Atribua ao médico disponível.`
      }
    >
      {doctorsLoading ? (
        <p className="text-sm text-text-muted">A carregar médicos…</p>
      ) : (
        <div className="space-y-4">
          {preferred ? (
            <p className="text-sm text-text-muted">
              Médico habitual: <strong className="text-text">{preferred.full_name}</strong>
              {preferred.available ? (
                <span className="text-emerald-700 dark:text-emerald-400"> · disponível</span>
              ) : (
                <span className="text-amber-700 dark:text-amber-300">
                  · em consulta — escolha outro médico
                </span>
              )}
            </p>
          ) : (
            <p className="text-sm text-text-muted">Primeira visita ou sem médico anterior registado.</p>
          )}

          <div className="space-y-1">
            <label htmlFor="doctor_id" className="block text-sm font-medium text-text">
              Médico responsável
            </label>
            <select
              id="doctor_id"
              className="w-full rounded-xl border border-border bg-surface px-3 py-2.5 text-sm text-text shadow-sm outline-none focus:border-primary-500 focus:ring-2 focus:ring-primary-100"
              value={doctorId ?? ""}
              onChange={(e) => setDoctorId(Number(e.target.value) || null)}
            >
              <option value="">Seleccionar médico…</option>
              {doctorOptions?.doctors.map((doc) => (
                <option key={doc.id} value={doc.id} disabled={!doc.available}>
                  {doc.full_name}
                  {doc.is_preferred ? " (habitual)" : ""}
                  {!doc.available ? " — em consulta" : ""}
                  {doc.available && doc.waiting_count > 0 ? ` — ${doc.waiting_count} em espera` : ""}
                </option>
              ))}
            </select>
          </div>
        </div>
      )}

      <div className="mt-6 flex flex-wrap gap-3">
        <Button
          type="button"
          variant="secondary"
          onClick={() => callMutation.mutate()}
          disabled={callMutation.isPending}
        >
          {callMutation.isPending ? "A chamar…" : "Chamar utente"}
        </Button>
        <Button
          type="button"
          variant="primary"
          onClick={() => assignMutation.mutate()}
          disabled={assignMutation.isPending || !doctorId}
        >
          {assignMutation.isPending ? "A atribuir…" : "Confirmar médico e notificar"}
        </Button>
      </div>
    </Card>
  );
}

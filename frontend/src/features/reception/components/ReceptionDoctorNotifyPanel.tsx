import { useMutation, useQuery } from "@tanstack/react-query";
import { useEffect, useMemo, useState } from "react";

import { Button, Card, useToast } from "@/design-system";
import { receptionService } from "@/services/reception";
import type { DoctorAssignmentOption } from "@/types/reception";
import { getApiErrorMessage } from "@/utils/api-error";

export interface ReceptionDoctorNotifyPanelProps {
  queueEntryId: number | null;
  patientId: number | null;
  patientName: string;
  checkInId?: number | null;
  /** Fluxo SauVida: pagamento já efectuado na receção. */
  paidFirst?: boolean;
  /** Pagamento confirmado hoje — obrigatório antes de notificar médico. */
  paymentConfirmed?: boolean;
  /** Já existe médico atribuído (reatribuição). */
  reassign?: boolean;
  onNotified?: () => void;
  onSkip?: () => void;
}

function sortDoctorsForDesk(doctors: DoctorAssignmentOption[]): DoctorAssignmentOption[] {
  return [...doctors].sort((a, b) => {
    if (a.available !== b.available) return a.available ? -1 : 1;
    if (a.waiting_count !== b.waiting_count) return a.waiting_count - b.waiting_count;
    return a.full_name.localeCompare(b.full_name, "pt");
  });
}

export function ReceptionDoctorNotifyPanel({
  queueEntryId,
  patientId,
  patientName,
  checkInId = null,
  paidFirst = false,
  paymentConfirmed = true,
  reassign = false,
  onNotified,
  onSkip,
}: ReceptionDoctorNotifyPanelProps) {
  const { showToast } = useToast();
  const [doctorId, setDoctorId] = useState<number | null>(null);

  const { data: doctorOptions, isLoading: doctorsLoading } = useQuery({
    queryKey: ["doctor-assignment-options", patientId, queueEntryId, checkInId],
    queryFn: () =>
      receptionService.getDoctorAssignmentOptions(patientId ?? undefined, {
        queue_id: queueEntryId ?? undefined,
        check_in_id: checkInId ?? undefined,
      }),
    enabled: paymentConfirmed && patientId != null,
  });

  const sortedDoctors = useMemo(
    () => sortDoctorsForDesk(doctorOptions?.doctors ?? []),
    [doctorOptions?.doctors],
  );

  useEffect(() => {
    // Preservar médico da marcação quando válido — sem auto-balanceamento.
    const scheduled = doctorOptions?.scheduled_doctor;
    if (scheduled?.available) {
      setDoctorId(scheduled.id);
      return;
    }
    setDoctorId(null);
  }, [doctorOptions?.scheduled_doctor]);

  const assignMutation = useMutation({
    mutationFn: () => {
      if (!queueEntryId) throw new Error("Sem entrada na fila.");
      if (!doctorId) throw new Error("Seleccione o médico.");
      return receptionService.assignToDoctor({ queue_id: queueEntryId, doctor_id: doctorId });
    },
    onSuccess: (result) => {
      const doctorLabel = result.consulta?.doctor_name ?? "médico";
      showToast(
        reassign ? `Médico alterado para ${doctorLabel}.` : `Utente encaminhado para ${doctorLabel}.`,
        "success",
      );
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
          Registe o pagamento e imprima o recibo no <strong>passo 3</strong> antes de encaminhar para o médico.
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
  const scheduled = doctorOptions?.scheduled_doctor;
  const availableCount = sortedDoctors.filter((d) => d.available).length;

  return (
    <Card
      title={reassign ? "4. Alterar médico" : "4. Encaminhar para médico"}
      description={
        paidFirst
          ? `${patientName} já pagou. Escolha o médico disponível que vai atender.`
          : `${patientName} está na fila. Escolha o médico conforme a disponibilidade.`
      }
    >
      {doctorsLoading ? (
        <p className="text-sm text-text-muted">A carregar médicos…</p>
      ) : (
        <div className="space-y-4">
          <p className="text-sm text-text-muted">
            Há vários médicos no sistema. A receção escolhe manualmente conforme a disponibilidade
            {availableCount > 0 ? (
              <>
                {" "}
                (<span className="font-medium text-emerald-700 dark:text-emerald-400">
                  ({availableCount} disponível{availableCount === 1 ? "" : "eis"} agora)
                </span>
              </>
            ) : null}
            .
          </p>

          {scheduled ? (
            <p className="text-sm text-text-muted">
              Médico da marcação: <strong className="text-text">{scheduled.full_name}</strong>
              {scheduled.available ? (
                <span className="text-emerald-700 dark:text-emerald-400"> · disponível</span>
              ) : (
                <span className="text-amber-700 dark:text-amber-300">
                  · indisponível: seleccione outro médico
                </span>
              )}
            </p>
          ) : preferred ? (
            <p className="text-sm text-text-muted">
              Médico habitual: <strong className="text-text">{preferred.full_name}</strong>
              {preferred.available ? (
                <span className="text-emerald-700 dark:text-emerald-400"> · disponível</span>
              ) : (
                <span className="text-amber-700 dark:text-amber-300">
                  · indisponível: escolha outro médico
                </span>
              )}
            </p>
          ) : null}

          {sortedDoctors.length === 0 ? (
            <p className="rounded-xl border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-900 dark:border-amber-800 dark:bg-amber-950/40 dark:text-amber-100">
              Não há médicos activos no sistema. O utente permanece na fila — o pagamento já registado
              não se perde. Encaminhe quando houver médico disponível.
            </p>
          ) : null}

          {sortedDoctors.length > 0 && availableCount === 0 ? (
            <p className="rounded-xl border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-900 dark:border-amber-800 dark:bg-amber-950/40 dark:text-amber-100">
              Todos os médicos estão em consulta. O utente permanece na fila; volte a encaminhar quando
              houver disponibilidade.
            </p>
          ) : null}

          {sortedDoctors.length > 0 ? (
            <fieldset className="space-y-2">
              <legend className="mb-1 text-sm font-medium text-text">Seleccionar médico</legend>
              <ul className="space-y-2">
                {sortedDoctors.map((doc) => {
                  const selected = doctorId === doc.id;
                  const label =
                    doc.availability_label ??
                    (doc.available ? "Disponível" : "Indisponível");
                  return (
                    <li key={doc.id}>
                      <label
                        className={[
                          "flex cursor-pointer items-start gap-3 rounded-xl border px-3 py-3 transition",
                          !doc.available
                            ? "cursor-not-allowed border-border bg-surface-muted/40 opacity-70"
                            : selected
                              ? "border-primary-500 bg-primary-50/80 ring-2 ring-primary-100 dark:bg-primary-950/30"
                              : "border-border bg-surface hover:border-primary-300",
                        ].join(" ")}
                      >
                        <input
                          type="radio"
                          name="doctor_id"
                          className="mt-1"
                          value={doc.id}
                          checked={selected}
                          disabled={!doc.available}
                          onChange={() => setDoctorId(doc.id)}
                        />
                        <span className="min-w-0 flex-1">
                          <span className="block font-medium text-text">{doc.full_name}</span>
                          <span className="mt-0.5 flex flex-wrap gap-x-2 text-xs text-text-muted">
                            <span
                              className={
                                doc.available
                                  ? "font-semibold text-emerald-700 dark:text-emerald-400"
                                  : "font-semibold text-amber-700 dark:text-amber-300"
                              }
                            >
                              {label}
                            </span>
                            {doc.is_preferred ? <span>· habitual</span> : null}
                            {scheduled?.id === doc.id ? <span>· marcação</span> : null}
                          </span>
                        </span>
                      </label>
                    </li>
                  );
                })}
              </ul>
            </fieldset>
          ) : null}
        </div>
      )}

      <div className="mt-6 flex flex-wrap gap-3">
        {!reassign ? (
          <Button
            type="button"
            variant="secondary"
            onClick={() => callMutation.mutate()}
            disabled={callMutation.isPending}
          >
            {callMutation.isPending ? "A chamar…" : "Chamar utente"}
          </Button>
        ) : null}
        <Button
          type="button"
          variant="primary"
          onClick={() => assignMutation.mutate()}
          disabled={assignMutation.isPending || !doctorId}
        >
          {assignMutation.isPending
            ? "A confirmar…"
            : reassign
              ? "Confirmar alteração"
              : "Encaminhar para médico"}
        </Button>
      </div>
    </Card>
  );
}

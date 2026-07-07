import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { useNavigate } from "react-router-dom";

import { Button, Card, useToast } from "@/design-system";
import { PRIORITY_LABELS } from "@/constants/appointments";
import { PatientSearchSelect } from "@/features/reception/components/PatientSearchSelect";
import { AppointmentSubNav } from "@/features/appointments/components/AppointmentSubNav";
import {
  appointmentFormSchema,
  type AppointmentFormValues,
} from "@/features/appointments/schemas/appointmentSchema";
import { appointmentsService } from "@/services/appointments";
import { getApiErrorMessage } from "@/utils/api-error";
import { useState } from "react";

export function AppointmentFormPage() {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [patientId, setPatientId] = useState<number | null>(null);

  const { register, handleSubmit, setValue, formState: { errors } } = useForm<AppointmentFormValues>({
    resolver: zodResolver(appointmentFormSchema),
    defaultValues: { duration_minutes: 30, priority: "NORMAL" },
  });

  const mutation = useMutation({
    mutationFn: appointmentsService.create,
    onSuccess: (created) => {
      showToast("Consulta criada com sucesso.", "success");
      navigate(`/appointments/${created.id}`);
    },
    onError: (e) => showToast(getApiErrorMessage(e), "error"),
  });

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Nova Consulta</h2>
      </div>
      <AppointmentSubNav />
      <div className="max-w-xl">
        <Card title="Dados da consulta">
          <form
            onSubmit={handleSubmit((values) =>
              mutation.mutate({
                patient_id: values.patient_id,
                doctor_id: values.doctor_id,
                scheduled_at: values.scheduled_at,
                duration_minutes: values.duration_minutes,
                priority: values.priority,
                chief_complaint: values.chief_complaint,
                notes: values.notes,
              }),
            )}
            className="space-y-4"
          >
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">Paciente</label>
              <PatientSearchSelect
                value={patientId}
                onChange={(id) => {
                  setPatientId(id);
                  if (id) setValue("patient_id", id, { shouldValidate: true });
                }}
              />
              {errors.patient_id && <p className="text-sm text-red-600">{errors.patient_id.message}</p>}
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">Data e hora</label>
              <input type="datetime-local" {...register("scheduled_at")} className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm" />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">Duração (min)</label>
              <input type="number" {...register("duration_minutes", { valueAsNumber: true })} className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm" />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">Prioridade</label>
              <select {...register("priority")} className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm">
                {Object.entries(PRIORITY_LABELS).map(([value, label]) => (
                  <option key={value} value={value}>{label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">Motivo da consulta</label>
              <textarea {...register("chief_complaint")} rows={2} className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm" />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">Observações</label>
              <textarea {...register("notes")} rows={2} className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm" />
            </div>
            <Button type="submit" disabled={mutation.isPending}>Agendar consulta</Button>
          </form>
        </Card>
      </div>
    </div>
  );
}

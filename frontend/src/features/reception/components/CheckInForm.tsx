import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

import { Button, Card, useToast } from "@/design-system";
import { PRIORITY_OPTIONS } from "@/constants/reception";
import { PatientSearchSelect } from "@/features/reception/components/PatientSearchSelect";
import { receptionService } from "@/services/reception";
import type { QueuePriority } from "@/types/reception";
import { getApiErrorMessage } from "@/utils/api-error";

const checkInSchema = z.object({
  patient_id: z.number({ required_error: "Seleccione um paciente." }).positive(),
  priority: z.enum(["LOW", "NORMAL", "HIGH", "EMERGENCY"]),
  notes: z.string().optional(),
});

type CheckInFormValues = z.infer<typeof checkInSchema>;

export function CheckInForm() {
  const { showToast } = useToast();
  const queryClient = useQueryClient();
  const [selectedPatientId, setSelectedPatientId] = useState<number | null>(null);

  const {
    register,
    handleSubmit,
    reset,
    setValue,
    formState: { errors },
  } = useForm<CheckInFormValues>({
    resolver: zodResolver(checkInSchema),
    defaultValues: { priority: "NORMAL", notes: "" },
  });

  const mutation = useMutation({
    mutationFn: receptionService.checkIn,
    onSuccess: () => {
      showToast("Check-in efectuado com sucesso.", "success");
      reset({ priority: "NORMAL", notes: "" });
      setSelectedPatientId(null);
      void queryClient.invalidateQueries({ queryKey: ["reception-queue"] });
      void queryClient.invalidateQueries({ queryKey: ["reception-dashboard"] });
      void queryClient.invalidateQueries({ queryKey: ["reception-history"] });
    },
    onError: (error) => showToast(getApiErrorMessage(error), "error"),
  });

  const onSubmit = (values: CheckInFormValues) => {
    mutation.mutate({
      patient_id: values.patient_id,
      priority: values.priority as QueuePriority,
      notes: values.notes,
    });
  };

  return (
    <Card title="Novo check-in">
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div>
          <label className="mb-1 block text-sm font-medium text-slate-700">Paciente</label>
          <PatientSearchSelect
            value={selectedPatientId}
            onChange={(patientId) => {
              setSelectedPatientId(patientId);
              setValue("patient_id", patientId ?? 0, { shouldValidate: true });
            }}
          />
          {errors.patient_id && (
            <p className="mt-1 text-sm text-red-600">{errors.patient_id.message}</p>
          )}
        </div>

        <div>
          <label htmlFor="priority" className="mb-1 block text-sm font-medium text-slate-700">
            Prioridade
          </label>
          <select
            id="priority"
            {...register("priority")}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
          >
            {PRIORITY_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="notes" className="mb-1 block text-sm font-medium text-slate-700">
            Notas
          </label>
          <textarea
            id="notes"
            rows={3}
            {...register("notes")}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            placeholder="Observações opcionais..."
          />
        </div>

        <Button type="submit" disabled={mutation.isPending}>
          {mutation.isPending ? "A processar..." : "Efectuar check-in"}
        </Button>
      </form>
    </Card>
  );
}

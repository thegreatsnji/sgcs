import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { Button, Card, useToast } from "@/design-system";
import { REFERRAL_DEPARTMENT_OPTIONS } from "@/constants/reception";
import { PatientSearchSelect } from "@/features/reception/components/PatientSearchSelect";
import { ReceptionSubNav } from "@/features/reception/components/ReceptionSubNav";
import { receptionService } from "@/services/reception";
import type { ReferralDepartment } from "@/types/reception";
import { getApiErrorMessage } from "@/utils/api-error";

const referralSchema = z.object({
  patient_id: z.number({ required_error: "Seleccione um paciente." }).positive(),
  to_department: z.enum(["DOCTOR", "LAB", "BILLING"]),
  reason: z.string().min(3, "Indique o motivo do encaminhamento."),
});

type ReferralFormValues = z.infer<typeof referralSchema>;

export function ReferralPage() {
  const { showToast } = useToast();
  const [selectedPatientId, setSelectedPatientId] = useState<number | null>(null);

  const {
    register,
    handleSubmit,
    reset,
    setValue,
    formState: { errors },
  } = useForm<ReferralFormValues>({
    resolver: zodResolver(referralSchema),
    defaultValues: { to_department: "DOCTOR" },
  });

  const mutation = useMutation({
    mutationFn: receptionService.createReferral,
    onSuccess: () => {
      showToast("Encaminhamento registado com sucesso.", "success");
      reset({ to_department: "DOCTOR", reason: "" });
      setSelectedPatientId(null);
    },
    onError: (error) => showToast(getApiErrorMessage(error), "error"),
  });

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Encaminhamentos</h2>
        <p className="mt-1 text-slate-600">
          Encaminhe utentes para médico, laboratório ou faturação.
        </p>
      </div>

      <ReceptionSubNav />

      <div className="max-w-xl">
        <Card title="Novo encaminhamento">
          <form
            onSubmit={handleSubmit((values) =>
              mutation.mutate({
                patient_id: values.patient_id,
                to_department: values.to_department as ReferralDepartment,
                reason: values.reason,
              }),
            )}
            className="space-y-4"
          >
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">Paciente</label>
              <PatientSearchSelect
                value={selectedPatientId}
                onChange={(patientId) => {
                  setSelectedPatientId(patientId);
                  if (patientId) {
                    setValue("patient_id", patientId, { shouldValidate: true });
                  }
                }}
              />
              {errors.patient_id && (
                <p className="mt-1 text-sm text-red-600">{errors.patient_id.message}</p>
              )}
            </div>

            <div>
              <label htmlFor="to_department" className="mb-1 block text-sm font-medium text-slate-700">
                Destino
              </label>
              <select
                id="to_department"
                {...register("to_department")}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
              >
                {REFERRAL_DEPARTMENT_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label htmlFor="reason" className="mb-1 block text-sm font-medium text-slate-700">
                Motivo
              </label>
              <textarea
                id="reason"
                rows={4}
                {...register("reason")}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
                placeholder="Descreva o motivo do encaminhamento..."
              />
              {errors.reason && (
                <p className="mt-1 text-sm text-red-600">{errors.reason.message}</p>
              )}
            </div>

            <Button type="submit" disabled={mutation.isPending}>
              {mutation.isPending ? "A registar..." : "Registar encaminhamento"}
            </Button>
          </form>
        </Card>
      </div>
    </div>
  );
}

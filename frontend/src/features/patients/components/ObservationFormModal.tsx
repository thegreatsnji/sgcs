import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect } from "react";
import { useForm } from "react-hook-form";

import { Modal } from "@/design-system";
import { OBSERVATION_TYPE_LABELS } from "@/constants/patients";
import { observationFormSchema, type ObservationFormData } from "@/schemas/patientSchema";
import type { ObservationType, PatientObservation } from "@/types/patient";

import { SelectField } from "./SelectField";

interface ObservationFormModalProps {
  open: boolean;
  initial?: PatientObservation | null;
  isSubmitting?: boolean;
  onClose: () => void;
  onSubmit: (data: ObservationFormData) => void;
}

export function ObservationFormModal({
  open,
  initial,
  isSubmitting,
  onClose,
  onSubmit,
}: ObservationFormModalProps) {
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<ObservationFormData>({
    resolver: zodResolver(observationFormSchema),
    defaultValues: {
      observation_type: "CLINICA",
      content: "",
      is_pinned: false,
    },
  });

  useEffect(() => {
    if (open) {
      reset(
        initial
          ? {
              observation_type: initial.observation_type,
              content: initial.content,
              is_pinned: initial.is_pinned,
            }
          : {
              observation_type: "CLINICA",
              content: "",
              is_pinned: false,
            },
      );
    }
  }, [open, initial, reset]);

  return (
    <Modal
      open={open}
      title={initial ? "Editar observação" : "Nova observação"}
      cancelLabel="Cancelar"
      confirmLabel={isSubmitting ? "A guardar..." : "Guardar"}
      onClose={onClose}
      onConfirm={handleSubmit(onSubmit)}
    >
      <form className="grid gap-4" onSubmit={(event) => event.preventDefault()}>
        <SelectField
          label="Tipo"
          error={errors.observation_type?.message}
          options={(Object.entries(OBSERVATION_TYPE_LABELS) as [ObservationType, string][]).map(
            ([value, label]) => ({ value, label }),
          )}
          {...register("observation_type")}
        />
        <div>
          <label className="mb-1.5 block text-sm font-medium text-slate-700">Conteúdo</label>
          <textarea
            className={`min-h-28 w-full rounded-lg border px-3 py-2 text-sm outline-none transition focus:border-primary-500 focus:ring-2 focus:ring-primary-100 ${
              errors.content ? "border-red-500" : "border-slate-300"
            }`}
            {...register("content")}
          />
          {errors.content?.message && <p className="mt-1 text-xs text-red-600">{errors.content.message}</p>}
        </div>
        <label className="flex items-center gap-2 text-sm text-slate-700">
          <input type="checkbox" {...register("is_pinned")} />
          Fixar no topo
        </label>
      </form>
    </Modal>
  );
}

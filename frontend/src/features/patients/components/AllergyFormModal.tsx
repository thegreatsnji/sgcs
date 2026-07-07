import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect } from "react";
import { useForm } from "react-hook-form";

import { Input, Modal } from "@/design-system";
import { ALLERGY_SEVERITY_LABELS } from "@/constants/patients";
import { allergyFormSchema, type AllergyFormData } from "@/schemas/patientSchema";
import type { AllergySeverity, PatientAllergy } from "@/types/patient";

import { SelectField } from "./SelectField";

interface AllergyFormModalProps {
  open: boolean;
  initial?: PatientAllergy | null;
  isSubmitting?: boolean;
  onClose: () => void;
  onSubmit: (data: AllergyFormData) => void;
}

export function AllergyFormModal({
  open,
  initial,
  isSubmitting,
  onClose,
  onSubmit,
}: AllergyFormModalProps) {
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<AllergyFormData>({
    resolver: zodResolver(allergyFormSchema),
    defaultValues: {
      allergen: "",
      severity: "MODERADA",
      reaction: "",
      diagnosed_at: "",
      notes: "",
    },
  });

  useEffect(() => {
    if (open) {
      reset(
        initial
          ? {
              allergen: initial.allergen,
              severity: initial.severity,
              reaction: initial.reaction ?? "",
              diagnosed_at: initial.diagnosed_at ?? "",
              notes: initial.notes ?? "",
            }
          : {
              allergen: "",
              severity: "MODERADA",
              reaction: "",
              diagnosed_at: "",
              notes: "",
            },
      );
    }
  }, [open, initial, reset]);

  return (
    <Modal
      open={open}
      title={initial ? "Editar alergia" : "Registar alergia"}
      cancelLabel="Cancelar"
      confirmLabel={isSubmitting ? "A guardar..." : "Guardar"}
      onClose={onClose}
      onConfirm={handleSubmit(onSubmit)}
    >
      <form className="grid gap-4" onSubmit={(event) => event.preventDefault()}>
        <Input label="Alergénio" error={errors.allergen?.message} {...register("allergen")} />
        <SelectField
          label="Severidade"
          error={errors.severity?.message}
          options={(Object.entries(ALLERGY_SEVERITY_LABELS) as [AllergySeverity, string][]).map(
            ([value, label]) => ({ value, label }),
          )}
          {...register("severity")}
        />
        <Input label="Reação" error={errors.reaction?.message} {...register("reaction")} />
        <Input
          label="Diagnosticado em"
          placeholder="DD/MM/AAAA"
          error={errors.diagnosed_at?.message}
          {...register("diagnosed_at")}
        />
        <Input label="Notas" error={errors.notes?.message} {...register("notes")} />
      </form>
    </Modal>
  );
}

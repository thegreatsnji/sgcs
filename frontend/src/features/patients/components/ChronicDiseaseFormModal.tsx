import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect } from "react";
import { useForm } from "react-hook-form";

import { Input, Modal } from "@/design-system";
import { CHRONIC_DISEASE_STATUS_LABELS } from "@/constants/patients";
import { chronicDiseaseFormSchema, type ChronicDiseaseFormData } from "@/schemas/patientSchema";
import type { ChronicDiseaseStatus, PatientChronicDisease } from "@/types/patient";

import { SelectField } from "./SelectField";

interface ChronicDiseaseFormModalProps {
  open: boolean;
  initial?: PatientChronicDisease | null;
  isSubmitting?: boolean;
  onClose: () => void;
  onSubmit: (data: ChronicDiseaseFormData) => void;
}

export function ChronicDiseaseFormModal({
  open,
  initial,
  isSubmitting,
  onClose,
  onSubmit,
}: ChronicDiseaseFormModalProps) {
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<ChronicDiseaseFormData>({
    resolver: zodResolver(chronicDiseaseFormSchema),
    defaultValues: {
      disease_name: "",
      icd_code: "",
      diagnosed_at: "",
      status: "ATIVA",
      notes: "",
    },
  });

  useEffect(() => {
    if (open) {
      reset(
        initial
          ? {
              disease_name: initial.disease_name,
              icd_code: initial.icd_code ?? "",
              diagnosed_at: initial.diagnosed_at ?? "",
              status: initial.status,
              notes: initial.notes ?? "",
            }
          : {
              disease_name: "",
              icd_code: "",
              diagnosed_at: "",
              status: "ATIVA",
              notes: "",
            },
      );
    }
  }, [open, initial, reset]);

  return (
    <Modal
      open={open}
      title={initial ? "Editar doença crónica" : "Registar doença crónica"}
      cancelLabel="Cancelar"
      confirmLabel={isSubmitting ? "A guardar..." : "Guardar"}
      onClose={onClose}
      onConfirm={handleSubmit(onSubmit)}
    >
      <form className="grid gap-4" onSubmit={(event) => event.preventDefault()}>
        <Input label="Doença" error={errors.disease_name?.message} {...register("disease_name")} />
        <Input label="Código CID" error={errors.icd_code?.message} {...register("icd_code")} />
        <Input
          label="Diagnosticado em"
          placeholder="DD/MM/AAAA"
          error={errors.diagnosed_at?.message}
          {...register("diagnosed_at")}
        />
        <SelectField
          label="Estado"
          error={errors.status?.message}
          options={(Object.entries(CHRONIC_DISEASE_STATUS_LABELS) as [ChronicDiseaseStatus, string][]).map(
            ([value, label]) => ({ value, label }),
          )}
          {...register("status")}
        />
        <Input label="Notas" error={errors.notes?.message} {...register("notes")} />
      </form>
    </Modal>
  );
}

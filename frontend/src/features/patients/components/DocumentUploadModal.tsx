import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";

import { Input, Modal } from "@/design-system";
import { PATIENT_DOCUMENT_TYPE_LABELS } from "@/constants/patients";
import { documentUploadSchema, type DocumentUploadFormData } from "@/schemas/patientSchema";
import type { PatientDocumentType } from "@/types/patient";

import { SelectField } from "./SelectField";

interface DocumentUploadModalProps {
  open: boolean;
  isSubmitting?: boolean;
  onClose: () => void;
  onSubmit: (data: DocumentUploadFormData) => void;
}

export function DocumentUploadModal({
  open,
  isSubmitting,
  onClose,
  onSubmit,
}: DocumentUploadModalProps) {
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<DocumentUploadFormData>({
    resolver: zodResolver(documentUploadSchema),
    defaultValues: {
      document_type: "OUTRO",
      title: "",
      document_number: "",
      description: "",
      issued_at: "",
      expires_at: "",
    },
  });

  const submit = handleSubmit((data) => {
    onSubmit(data);
    reset();
  });

  return (
    <Modal
      open={open}
      title="Carregar documento"
      description="Selecione o ficheiro e preencha os metadados."
      cancelLabel="Cancelar"
      confirmLabel={isSubmitting ? "A carregar..." : "Carregar"}
      onClose={() => {
        reset();
        onClose();
      }}
      onConfirm={submit}
    >
      <form className="grid gap-4" onSubmit={(event) => event.preventDefault()}>
        <div>
          <label className="mb-1.5 block text-sm font-medium text-slate-700">Ficheiro</label>
          <input type="file" className="block w-full text-sm" {...register("file")} />
          {errors.file?.message && <p className="mt-1 text-xs text-red-600">{errors.file.message}</p>}
        </div>
        <SelectField
          label="Tipo de documento"
          error={errors.document_type?.message}
          options={(Object.entries(PATIENT_DOCUMENT_TYPE_LABELS) as [PatientDocumentType, string][]).map(
            ([value, label]) => ({ value, label }),
          )}
          {...register("document_type")}
        />
        <Input label="Título" error={errors.title?.message} {...register("title")} />
        <Input label="N.º documento" error={errors.document_number?.message} {...register("document_number")} />
        <Input label="Descrição" error={errors.description?.message} {...register("description")} />
        <Input
          label="Emitido em"
          placeholder="DD/MM/AAAA"
          error={errors.issued_at?.message}
          {...register("issued_at")}
        />
        <Input
          label="Validade"
          placeholder="DD/MM/AAAA"
          error={errors.expires_at?.message}
          {...register("expires_at")}
        />
      </form>
    </Modal>
  );
}

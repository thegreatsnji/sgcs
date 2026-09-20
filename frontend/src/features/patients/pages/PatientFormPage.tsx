import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";

import {
  Button,
  Card,
  ErrorState,
  LoadingState,
  Modal,
  useToast,
} from "@/design-system";
import { PhoneInput } from "@/components/forms";
import { ComputedAgeHint } from "@/components/forms/ComputedAgeHint";
import { DisplayDateInput } from "@/components/forms/DisplayDateInput";
import { DuplicateAlert } from "@/features/patients/components/DuplicateAlert";
import { EmergencyContactForm } from "@/features/patients/components/EmergencyContactForm";
import { SelectField } from "@/features/patients/components/SelectField";
import {
  BLOOD_TYPE_LABELS,
  DOCUMENT_TYPE_LABELS,
  PATIENT_GENDER_LABELS,
} from "@/constants/patients";
import { useDebouncedValue } from "@/hooks/useDebouncedValue";
import { usePermissions } from "@/hooks/usePermissions";
import { patientFormSchema, type PatientFormData } from "@/schemas/patientSchema";
import { patientsService } from "@/services/patients";
import type {
  BloodType,
  DocumentType,
  PatientGender,
  PatientPayload,
} from "@/types/patient";
import { getApiErrorMessage } from "@/utils/api-error";
import { displayDateToApi, isValidDisplayDate } from "@/utils/date";
import { joinFullName, splitFullName } from "@/utils/fullName";
import { stripCountryCode, toFullPhone, isValidLocalPhone } from "@/utils/phone";

function toPayload(data: PatientFormData): PatientPayload {
  const { first_name, last_name } = splitFullName(data.full_name);
  return {
    first_name,
    last_name,
    document_type: data.document_type || undefined,
    document_number: data.document_number || undefined,
    birth_date: data.birth_date,
    gender: data.gender,
    phone: toFullPhone(data.phone),
    address_street: data.address_street || undefined,
    blood_type: data.blood_type || undefined,
    emergency_contacts: data.emergency_contacts.map((contact) => ({
      ...contact,
      phone: toFullPhone(contact.phone),
      email: contact.email || undefined,
    })),
  };
}

export function PatientFormPage() {
  const { id } = useParams();
  const [searchParams] = useSearchParams();
  const returnTo = searchParams.get("retorno");
  const isEdit = Boolean(id);
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { showToast } = useToast();
  const { hasPermission } = usePermissions();
  const [showCancelModal, setShowCancelModal] = useState(false);

  const canAccess = isEdit ? hasPermission("patients.edit") : hasPermission("patients.create");
  const canEditBloodType = hasPermission("appointments.clinical");
  const patientId = Number(id);

  const { data: patient, isLoading, isError, refetch } = useQuery({
    queryKey: ["patient", id],
    queryFn: () => patientsService.get(patientId),
    enabled: isEdit,
  });

  const {
    register,
    control,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting, isDirty },
  } = useForm<PatientFormData>({
    resolver: zodResolver(patientFormSchema),
    values: patient
      ? {
          full_name: joinFullName(patient.first_name, patient.last_name),
          document_type: patient.document_type ?? "",
          document_number: patient.document_number ?? "",
          birth_date: patient.birth_date ?? "",
          gender: patient.gender ?? "M",
          phone: stripCountryCode(patient.phone ?? ""),
          address_street: patient.address_street ?? "",
          blood_type: patient.blood_type ?? "",
          emergency_contacts:
            patient.emergency_contacts?.map((contact) => ({
              name: contact.name,
              phone: stripCountryCode(contact.phone),
              email: contact.email ?? "",
              relationship: contact.relationship,
              is_primary: contact.is_primary,
            })) ?? [],
        }
      : undefined,
    defaultValues: {
      full_name: "",
      document_type: "",
      document_number: "",
      birth_date: "",
      gender: "M",
      phone: "",
      address_street: "",
      blood_type: "",
      emergency_contacts: [],
    },
  });

  const watchedBirthDate = watch("birth_date");

  const watched = watch(["full_name", "birth_date", "phone", "document_number"]);
  const nameParts = splitFullName(watched[0] ?? "");
  const birthDateValid = Boolean(watched[1] && isValidDisplayDate(watched[1]));
  const phoneLocal = watched[2] ?? "";
  const phoneValid = isValidLocalPhone(phoneLocal);
  const duplicateParams = {
    first_name: nameParts.first_name,
    last_name: nameParts.last_name,
    birth_date: birthDateValid ? displayDateToApi(watched[1]!) : "",
    phone: phoneValid ? toFullPhone(phoneLocal) : undefined,
    document_number: watched[3] || undefined,
  };
  const debouncedDuplicateParams = useDebouncedValue(duplicateParams, 500);

  const { data: duplicateResult } = useQuery({
    queryKey: ["patient-duplicate", debouncedDuplicateParams],
    queryFn: () => patientsService.checkDuplicate(debouncedDuplicateParams),
    enabled:
      !isEdit &&
      Boolean(nameParts.first_name && birthDateValid && debouncedDuplicateParams.birth_date),
    retry: false,
  });

  const mutation = useMutation({
    mutationFn: async (formData: PatientFormData) => {
      const payload = toPayload(formData);
      if (isEdit) return patientsService.update(patientId, payload);
      return patientsService.create(payload);
    },
    onSuccess: (saved) => {
      showToast(isEdit ? "Paciente atualizado com sucesso." : "Paciente registado com sucesso.", "success");
      void queryClient.invalidateQueries({ queryKey: ["patients"] });
      void queryClient.invalidateQueries({ queryKey: ["patient", String(saved.id)] });
      navigate(returnTo && returnTo.startsWith("/") ? returnTo : `/patients/${saved.id}`);
    },
    onError: (error) => showToast(getApiErrorMessage(error), "error"),
  });

  const statusMutation = useMutation({
    mutationFn: (active: boolean) =>
      active ? patientsService.activate(patientId) : patientsService.deactivate(patientId),
    onSuccess: (_, active) => {
      showToast(active ? "Paciente ativado." : "Paciente desativado.", "success");
      void queryClient.invalidateQueries({ queryKey: ["patient", id] });
      void queryClient.invalidateQueries({ queryKey: ["patients"] });
    },
    onError: (error) => showToast(getApiErrorMessage(error), "error"),
  });

  useEffect(() => {
    if (!canAccess) navigate("/patients");
  }, [canAccess, navigate]);

  if (!canAccess) return null;
  if (isEdit && isLoading) return <LoadingState message="A carregar paciente..." />;
  if (isEdit && isError) {
    return <ErrorState message="Não foi possível carregar o paciente." onRetry={() => void refetch()} />;
  }

  const cancelTarget = isEdit ? `/patients/${id}` : "/patients";

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">
          {isEdit ? "Editar Paciente" : "Novo Paciente"}
        </h2>
        <p className="text-sm text-slate-500">
          {isEdit
            ? `Processo ${patient?.patient_number}`
            : "Dados guardados na ficha do utente. A triagem e a consulta usam a mesma informação."}
        </p>
      </div>

      {!isEdit && duplicateResult?.has_duplicates && duplicateResult.matches?.length > 0 && (
        <DuplicateAlert matches={duplicateResult.matches} />
      )}

      <form onSubmit={handleSubmit((data) => mutation.mutate(data))} className="space-y-6">
        <Card title="Dados do utente" description="Nome, contacto e identificação mínima">
          <div className="grid gap-4 md:grid-cols-2">
            <input type="text" className="hidden" autoComplete="off" />
            <div className="md:col-span-2">
              <label className="mb-1.5 block text-sm font-medium text-slate-700">Nome completo</label>
              <input
                className={`w-full rounded-lg border px-3 py-2 text-sm ${errors.full_name ? "border-red-500" : "border-slate-300"}`}
                placeholder="Ex.: Maria Santos ou João Pedro Camará"
                autoComplete="name"
                {...register("full_name")}
              />
              {errors.full_name?.message && (
                <p className="mt-1 text-xs text-red-600">{errors.full_name.message}</p>
              )}
            </div>
            <div>
              <DisplayDateInput
                label="Data de nascimento"
                error={errors.birth_date?.message}
                {...register("birth_date")}
              />
              <ComputedAgeHint birthDate={watchedBirthDate} className="mt-1.5" />
            </div>
            <SelectField
              label="Género"
              options={(Object.entries(PATIENT_GENDER_LABELS) as [PatientGender, string][]).map(([value, label]) => ({
                value,
                label,
              }))}
              error={errors.gender?.message}
              {...register("gender")}
            />
            <div>
              <PhoneInput
                label="Telefone de contacto"
                error={errors.phone?.message}
                hint="Introduza 7 a 9 dígitos após +245"
                {...register("phone")}
              />
            </div>
            {canEditBloodType && (
              <SelectField
                label="Grupo sanguíneo (opcional)"
                placeholder="Selecionar"
                options={(Object.entries(BLOOD_TYPE_LABELS) as [BloodType, string][]).map(([value, label]) => ({
                  value,
                  label,
                }))}
                error={errors.blood_type?.message}
                {...register("blood_type")}
              />
            )}
            <SelectField
              label="Tipo de documento (opcional)"
              placeholder="Selecionar"
              options={(Object.entries(DOCUMENT_TYPE_LABELS) as [DocumentType, string][]).map(([value, label]) => ({
                value,
                label,
              }))}
              error={errors.document_type?.message}
              {...register("document_type")}
            />
            <div>
              <label className="mb-1.5 block text-sm font-medium text-slate-700">N.º documento (opcional)</label>
              <input
                className={`w-full rounded-lg border px-3 py-2 text-sm ${errors.document_number ? "border-red-500" : "border-slate-300"}`}
                {...register("document_number")}
              />
              {errors.document_number?.message && (
                <p className="mt-1 text-xs text-red-600">{errors.document_number.message}</p>
              )}
            </div>
            <div className="md:col-span-2">
              <label className="mb-1.5 block text-sm font-medium text-slate-700">Morada (opcional)</label>
              <input
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
                placeholder="Bairro ou rua"
                {...register("address_street")}
              />
            </div>
          </div>
        </Card>

        <Card title="Contactos de emergência" description="Obrigatório para menores de 18 anos">
          <EmergencyContactForm control={control} register={register} errors={errors} />
        </Card>

        <div className="flex flex-wrap gap-3">
          <Button type="submit" isLoading={isSubmitting || mutation.isPending}>
            Guardar
          </Button>
          <Button
            type="button"
            variant="ghost"
            onClick={() => (isDirty ? setShowCancelModal(true) : navigate(cancelTarget))}
          >
            Cancelar
          </Button>
          {isEdit && hasPermission("patients.delete") && patient && (
            <Button
              type="button"
              variant="danger"
              onClick={() => statusMutation.mutate(!patient.is_active)}
              isLoading={statusMutation.isPending}
            >
              {patient.is_active ? "Desativar" : "Ativar"}
            </Button>
          )}
        </div>
      </form>

      <Modal
        open={showCancelModal}
        title="Descartar alterações?"
        description="Existem alterações não guardadas."
        confirmLabel="Descartar"
        onConfirm={() => navigate(cancelTarget)}
        onClose={() => setShowCancelModal(false)}
      />
    </div>
  );
}

import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { useNavigate, useParams } from "react-router-dom";

import {
  Button,
  Card,
  ErrorState,
  LoadingState,
  Modal,
  useToast,
} from "@/design-system";
import { PhoneInput } from "@/components/forms";
import { DuplicateAlert } from "@/features/patients/components/DuplicateAlert";
import { EmergencyContactForm } from "@/features/patients/components/EmergencyContactForm";
import { SelectField } from "@/features/patients/components/SelectField";
import {
  BLOOD_TYPE_LABELS,
  DOCUMENT_TYPE_LABELS,
  MARITAL_STATUS_LABELS,
  PATIENT_GENDER_LABELS,
} from "@/constants/patients";
import { useDebouncedValue } from "@/hooks/useDebouncedValue";
import { usePermissions } from "@/hooks/usePermissions";
import { patientFormSchema, type PatientFormData } from "@/schemas/patientSchema";
import { patientsService } from "@/services/patients";
import type {
  BloodType,
  DocumentType,
  MaritalStatus,
  PatientGender,
  PatientPayload,
} from "@/types/patient";
import { getApiErrorMessage } from "@/utils/api-error";
import { stripCountryCode, toFullPhone } from "@/utils/phone";

function toPayload(data: PatientFormData): PatientPayload {
  return {
    first_name: data.first_name,
    last_name: data.last_name,
    document_type: data.document_type || null,
    document_number: data.document_number || null,
    birth_date: data.birth_date,
    gender: data.gender,
    phone: toFullPhone(data.phone),
    email: data.email || null,
    address_street: data.address_street || null,
    address_city: data.address_city || null,
    address_region: data.address_region || null,
    address_country: data.address_country || null,
    address_postal_code: data.address_postal_code || null,
    nationality: data.nationality || null,
    blood_type: data.blood_type || null,
    marital_status: data.marital_status || null,
    occupation: data.occupation || null,
    emergency_contacts: data.emergency_contacts.map((contact) => ({
      ...contact,
      phone: toFullPhone(contact.phone),
      email: contact.email || null,
    })),
  };
}

export function PatientFormPage() {
  const { id } = useParams();
  const isEdit = Boolean(id);
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { showToast } = useToast();
  const { hasPermission } = usePermissions();
  const [showCancelModal, setShowCancelModal] = useState(false);

  const canAccess = isEdit ? hasPermission("patients.edit") : hasPermission("patients.create");
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
          first_name: patient.first_name,
          last_name: patient.last_name,
          document_type: patient.document_type ?? "",
          document_number: patient.document_number ?? "",
          birth_date: patient.birth_date ?? "",
          gender: patient.gender ?? "M",
          phone: stripCountryCode(patient.phone ?? ""),
          email: patient.email ?? "",
          address_street: patient.address_street ?? "",
          address_city: patient.address_city ?? "",
          address_region: patient.address_region ?? "",
          address_country: patient.address_country ?? "",
          address_postal_code: patient.address_postal_code ?? "",
          nationality: patient.nationality ?? "",
          blood_type: patient.blood_type ?? "",
          marital_status: patient.marital_status ?? "",
          occupation: patient.occupation ?? "",
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
      first_name: "",
      last_name: "",
      document_type: "",
      document_number: "",
      birth_date: "",
      gender: "M",
      phone: "",
      email: "",
      address_street: "",
      address_city: "",
      address_region: "",
      address_country: "",
      address_postal_code: "",
      nationality: "",
      blood_type: "",
      marital_status: "",
      occupation: "",
      emergency_contacts: [],
    },
  });

  const watched = watch(["first_name", "last_name", "birth_date", "phone", "document_number"]);
  const duplicateParams = {
    first_name: watched[0],
    last_name: watched[1],
    birth_date: watched[2],
    phone: watched[3] ? toFullPhone(watched[3]) : undefined,
    document_number: watched[4] || undefined,
  };
  const debouncedDuplicateParams = useDebouncedValue(duplicateParams, 500);

  const { data: duplicateResult } = useQuery({
    queryKey: ["patient-duplicate", debouncedDuplicateParams],
    queryFn: () => patientsService.checkDuplicate(debouncedDuplicateParams),
    enabled:
      !isEdit &&
      Boolean(debouncedDuplicateParams.first_name && debouncedDuplicateParams.last_name && debouncedDuplicateParams.birth_date),
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
      navigate(`/patients/${saved.id}`);
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
          {isEdit ? `Processo ${patient?.patient_number}` : "Registo de novo utente"}
        </p>
      </div>

      {!isEdit && duplicateResult?.has_duplicates && (
        <DuplicateAlert matches={duplicateResult.matches} />
      )}

      <form onSubmit={handleSubmit((data) => mutation.mutate(data))} className="space-y-6">
        <Card title="Dados pessoais" description="Informação de identificação do paciente">
          <div className="grid gap-4 md:grid-cols-2">
            <input type="text" className="hidden" autoComplete="off" />
            <div>
              <label className="mb-1.5 block text-sm font-medium text-slate-700">Nome</label>
              <input
                className={`w-full rounded-lg border px-3 py-2 text-sm ${errors.first_name ? "border-red-500" : "border-slate-300"}`}
                {...register("first_name")}
              />
              {errors.first_name?.message && <p className="mt-1 text-xs text-red-600">{errors.first_name.message}</p>}
            </div>
            <div>
              <label className="mb-1.5 block text-sm font-medium text-slate-700">Apelido</label>
              <input
                className={`w-full rounded-lg border px-3 py-2 text-sm ${errors.last_name ? "border-red-500" : "border-slate-300"}`}
                {...register("last_name")}
              />
              {errors.last_name?.message && <p className="mt-1 text-xs text-red-600">{errors.last_name.message}</p>}
            </div>
            <SelectField
              label="Tipo de documento"
              placeholder="Selecionar"
              options={(Object.entries(DOCUMENT_TYPE_LABELS) as [DocumentType, string][]).map(([value, label]) => ({
                value,
                label,
              }))}
              error={errors.document_type?.message}
              {...register("document_type")}
            />
            <div>
              <label className="mb-1.5 block text-sm font-medium text-slate-700">N.º documento</label>
              <input
                className={`w-full rounded-lg border px-3 py-2 text-sm ${errors.document_number ? "border-red-500" : "border-slate-300"}`}
                {...register("document_number")}
              />
              {errors.document_number?.message && (
                <p className="mt-1 text-xs text-red-600">{errors.document_number.message}</p>
              )}
            </div>
            <div>
              <label className="mb-1.5 block text-sm font-medium text-slate-700">Data de nascimento</label>
              <input
                placeholder="DD/MM/AAAA"
                className={`w-full rounded-lg border px-3 py-2 text-sm ${errors.birth_date ? "border-red-500" : "border-slate-300"}`}
                {...register("birth_date")}
              />
              {errors.birth_date?.message && <p className="mt-1 text-xs text-red-600">{errors.birth_date.message}</p>}
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
            <SelectField
              label="Grupo sanguíneo"
              placeholder="Selecionar"
              options={(Object.entries(BLOOD_TYPE_LABELS) as [BloodType, string][]).map(([value, label]) => ({
                value,
                label,
              }))}
              error={errors.blood_type?.message}
              {...register("blood_type")}
            />
            <SelectField
              label="Estado civil"
              placeholder="Selecionar"
              options={(Object.entries(MARITAL_STATUS_LABELS) as [MaritalStatus, string][]).map(([value, label]) => ({
                value,
                label,
              }))}
              error={errors.marital_status?.message}
              {...register("marital_status")}
            />
            <div>
              <label className="mb-1.5 block text-sm font-medium text-slate-700">Nacionalidade</label>
              <input className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm" {...register("nationality")} />
            </div>
            <div>
              <label className="mb-1.5 block text-sm font-medium text-slate-700">Profissão</label>
              <input className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm" {...register("occupation")} />
            </div>
          </div>
        </Card>

        <Card title="Contactos" description="Telefone e e-mail do paciente">
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <PhoneInput
                label="Telefone"
                error={errors.phone?.message}
                hint="Introduza apenas os dígitos após +245"
                {...register("phone")}
              />
            </div>
            <div>
              <label className="mb-1.5 block text-sm font-medium text-slate-700">E-mail</label>
              <input
                className={`w-full rounded-lg border px-3 py-2 text-sm ${errors.email ? "border-red-500" : "border-slate-300"}`}
                {...register("email")}
              />
              {errors.email?.message && <p className="mt-1 text-xs text-red-600">{errors.email.message}</p>}
            </div>
          </div>
        </Card>

        <Card title="Morada">
          <div className="grid gap-4 md:grid-cols-2">
            <input className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm md:col-span-2" placeholder="Rua" {...register("address_street")} />
            <input className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm" placeholder="Cidade" {...register("address_city")} />
            <input className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm" placeholder="Região" {...register("address_region")} />
            <input className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm" placeholder="País" {...register("address_country")} />
            <input className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm" placeholder="Código postal" {...register("address_postal_code")} />
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

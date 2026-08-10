import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState, type ReactNode } from "react";
import { useForm, type Resolver } from "react-hook-form";
import { Link } from "react-router-dom";

import { IconPatients } from "@/components/icons";
import { PatientAgeCategoryBadge } from "@/components/patients/PatientAgeCategoryBadge";
import { ComputedAgeHint } from "@/components/forms/ComputedAgeHint";
import { DisplayDateInput } from "@/components/forms/DisplayDateInput";
import { PhoneInput } from "@/components/forms";
import { Button, Card, Input, useToast } from "@/design-system";
import { BLOOD_TYPE_LABELS, MARITAL_STATUS_LABELS, PATIENT_GENDER_LABELS } from "@/constants/patients";
import { useAuth } from "@/contexts/AuthContext";
import { PatientSearchSelect } from "@/features/reception/components/PatientSearchSelect";
import { TriageColorPicker } from "@/features/reception/components/TriageColorPicker";
import { TriageWizardSteps, type WizardStep } from "@/features/reception/components/TriageWizardSteps";
import {
  VISIT_PURPOSE_LABELS,
  type VisitPurpose,
} from "@/features/reception/constants/visitPurpose";
import {
  quickPatientSchema,
  triageSchema,
  type QuickPatientFormData,
  type TriageFormData,
} from "@/features/reception/schemas/triageSchema";
import { patientsService } from "@/services/patients";
import { receptionService } from "@/services/reception";
import type { PatientDetail, PatientListItem } from "@/types/patient";
import type { TriageColor } from "@/types/reception";
import { getApiErrorMessage } from "@/utils/api-error";
import { formatDisplayDate, getAgeFromDisplayDate } from "@/utils/date";
import { splitFullName } from "@/utils/fullName";
import { getPatientAgeCategory } from "@/utils/patientAgeCategory";
import { getVitalWarnings } from "@/utils/clinicalVitals";
import { toFullPhone } from "@/utils/phone";

interface SelectedPatient {
  id: number;
  full_name: string;
  patient_number: string;
  phone: string | null;
  birth_date?: string | null;
}

function resolveAgeFromBirthDate(birthDate?: string | null): number | null {
  if (!birthDate) return null;
  return getAgeFromDisplayDate(birthDate);
}

export interface TriageCheckInWizardProps {
  /** Se definido, abre directamente na triagem deste utente. */
  initialPatientId?: number | null;
  initialPatientSummary?: SelectedPatient | null;
  /** Não reinicia o assistente após check-in (fluxo de atendimento). */
  onCheckInSuccess?: (result: import("@/types/reception").CheckInResponse) => void;
  hideProgressNav?: boolean;
}

function FormSection({ title, description, children }: { title: string; description?: string; children: ReactNode }) {
  return (
    <section className="space-y-4">
      <div>
        <h4 className="text-sm font-semibold text-text">{title}</h4>
        {description && <p className="mt-0.5 text-xs text-text-muted">{description}</p>}
      </div>
      {children}
    </section>
  );
}

function selectClassName() {
  return "w-full rounded-xl border border-border bg-surface px-3 py-2.5 text-sm text-text shadow-sm outline-none transition focus:border-primary-500 focus:ring-2 focus:ring-primary-100 dark:focus:ring-primary-900";
}

function FichaReadonlyField({ label, value }: { label: string; value: string }) {
  return (
    <div className="min-w-0 space-y-1">
      <p className="text-xs font-medium text-text-muted">{label}</p>
      <p className="truncate text-sm font-medium text-text">{value || "—"}</p>
    </div>
  );
}

function formatPatientResidence(patient: PatientDetail | undefined): string {
  if (!patient) return "—";
  const parts = [
    patient.address_street,
    patient.address_city,
    patient.address_region,
    patient.address_country,
  ]
    .map((p) => p?.trim())
    .filter(Boolean);
  return parts.length ? parts.join(", ") : "—";
}

function vitalsDateLabel(): string {
  return new Date().toLocaleDateString("pt-PT", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });
}

export function TriageCheckInWizard({
  initialPatientId = null,
  initialPatientSummary = null,
  onCheckInSuccess,
  hideProgressNav = false,
}: TriageCheckInWizardProps = {}) {
  const { showToast } = useToast();
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [step, setStep] = useState<WizardStep>(
    initialPatientSummary || initialPatientId ? "triage" : "search",
  );
  const [selectedPatient, setSelectedPatient] = useState<SelectedPatient | null>(
    initialPatientSummary,
  );

  const registerForm = useForm<QuickPatientFormData>({
    resolver: zodResolver(quickPatientSchema),
    defaultValues: {
      full_name: "",
      birth_date: "",
      gender: "M",
      phone: "",
      blood_type: "",
      emergency_contact_name: "",
      emergency_contact_phone: "",
    },
  });

  const triageForm = useForm<TriageFormData>({
    resolver: zodResolver(triageSchema) as Resolver<TriageFormData>,
    defaultValues: {
      age_at_check_in: undefined,
      weight: undefined,
      height_cm: undefined,
      race: "",
      temperature: undefined,
      blood_pressure: "",
      spo2: undefined,
      heart_rate: undefined,
      respiratory_rate: undefined,
      symptoms: "",
      triage_color: "GREEN",
      visit_purpose: "CONSULTA",
      notes: "",
    },
  });

  const { data: patientDetail } = useQuery({
    queryKey: ["patient", selectedPatient?.id],
    queryFn: () => patientsService.get(selectedPatient!.id),
    enabled: step === "triage" && selectedPatient != null,
  });

  const patientBirthDate = patientDetail?.birth_date ?? selectedPatient?.birth_date ?? null;
  const computedPatientAge = resolveAgeFromBirthDate(patientBirthDate);

  useEffect(() => {
    if (computedPatientAge !== null) {
      triageForm.setValue("age_at_check_in", computedPatientAge);
    }
  }, [computedPatientAge, triageForm]);

  const registerMutation = useMutation({
    mutationFn: patientsService.create,
    onSuccess: (patient) => {
      setSelectedPatient({
        id: patient.id,
        full_name: patient.full_name,
        patient_number: patient.patient_number,
        phone: patient.phone ?? null,
        birth_date: patient.birth_date ?? null,
      });
      const age = resolveAgeFromBirthDate(patient.birth_date);
      if (age !== null) triageForm.setValue("age_at_check_in", age);
      setStep("triage");
      showToast("Paciente registado. Prossiga com a triagem.", "success");
    },
    onError: (error) => showToast(getApiErrorMessage(error), "error"),
  });

  const checkInMutation = useMutation({
    mutationFn: receptionService.checkIn,
    onSuccess: (result) => {
      showToast("Triagem concluída. Paciente adicionado à fila.", "success");
      void queryClient.invalidateQueries({ queryKey: ["reception-queue"] });
      void queryClient.invalidateQueries({ queryKey: ["reception-dashboard"] });
      void queryClient.invalidateQueries({ queryKey: ["reception-history"] });
      void queryClient.invalidateQueries({ queryKey: ["patients-search"] });
      if (onCheckInSuccess) {
        onCheckInSuccess(result);
        return;
      }
      resetWizard();
    },
    onError: (error) => showToast(getApiErrorMessage(error), "error"),
  });

  const resetWizard = () => {
    setStep("search");
    setSelectedPatient(null);
    registerForm.reset();
    triageForm.reset({
      triage_color: "GREEN",
      visit_purpose: "CONSULTA",
      notes: "",
      blood_pressure: "",
      symptoms: "",
      race: "",
      age_at_check_in: undefined,
    });
  };

  const handlePatientSelect = (patient: PatientListItem | null) => {
    if (!patient) {
      setSelectedPatient(null);
      return;
    }
    setSelectedPatient({
      id: patient.id,
      full_name: patient.full_name,
      patient_number: patient.patient_number,
      phone: patient.phone ?? null,
      birth_date: patient.birth_date ?? null,
    });
    const age = resolveAgeFromBirthDate(patient.birth_date);
    if (age !== null) triageForm.setValue("age_at_check_in", age);
    setStep("triage");
  };

  const onRegisterSubmit = registerForm.handleSubmit((values) => {
    const { first_name, last_name } = splitFullName(values.full_name);
    const age = getAgeFromDisplayDate(values.birth_date);
    registerMutation.mutate({
      first_name,
      last_name,
      gender: values.gender,
      phone: toFullPhone(values.phone.trim()),
      birth_date: values.birth_date.trim(),
      blood_type: values.blood_type || undefined,
      emergency_contacts:
        age !== null && age < 18
          ? [
              {
                name: values.emergency_contact_name!.trim(),
                phone: toFullPhone(values.emergency_contact_phone!.trim()),
                relationship: "OUTRO" as const,
                is_primary: true,
              },
            ]
          : undefined,
    });
  });

  const onTriageSubmit = triageForm.handleSubmit((values) => {
    if (!selectedPatient) return;
    const ageAtCheckIn =
      computedPatientAge ?? values.age_at_check_in ?? getAgeFromDisplayDate(patientBirthDate ?? "");
    if (ageAtCheckIn == null) {
      showToast("Registe a data de nascimento na ficha do utente para calcular a idade.", "error");
      return;
    }
    checkInMutation.mutate({
      patient_id: selectedPatient.id,
      triage_color: values.triage_color,
      age_at_check_in: ageAtCheckIn,
      weight: values.weight,
      height_cm: values.height_cm,
      race: values.race?.trim() || undefined,
      temperature: values.temperature,
      blood_pressure: values.blood_pressure.trim(),
      spo2: values.spo2,
      heart_rate: values.heart_rate,
      respiratory_rate: values.respiratory_rate,
      symptoms: values.symptoms.trim(),
      visit_purpose: values.visit_purpose,
      notes: values.notes?.trim(),
    });
  });

  const watchedBirthDate = registerForm.watch("birth_date");
  const registerMinorAge = getAgeFromDisplayDate(watchedBirthDate ?? "");
  const triageColor = triageForm.watch("triage_color") as TriageColor;
  const displayGender =
    patientDetail?.gender != null
      ? PATIENT_GENDER_LABELS[patientDetail.gender as keyof typeof PATIENT_GENDER_LABELS] ??
        patientDetail.gender
      : "—";
  const displayMarital =
    patientDetail?.marital_status != null
      ? MARITAL_STATUS_LABELS[patientDetail.marital_status] ?? patientDetail.marital_status
      : "—";
  const nurseName = user?.role === "ENFERMEIRO" ? user.full_name : "—";
  const doctorName = user?.role === "MEDICO" ? user.full_name : "—";
  const ageCategory = getPatientAgeCategory(computedPatientAge);
  const vitalWarnings = getVitalWarnings({
    temperature: triageForm.watch("temperature"),
    blood_pressure: triageForm.watch("blood_pressure"),
    spo2: triageForm.watch("spo2"),
    heart_rate: triageForm.watch("heart_rate"),
    respiratory_rate: triageForm.watch("respiratory_rate"),
  });

  return (
    <div className="space-y-6">
      {!hideProgressNav ? <TriageWizardSteps current={step} /> : null}

      {step === "search" && (
        <Card title="Identificar utente" description="Pesquise na base de dados da clínica antes de iniciar a triagem.">
          <div className="space-y-6">
            <PatientSearchSelect
              value={selectedPatient?.id ?? null}
              onSelectPatient={handlePatientSelect}
            />

            <div className="flex flex-col gap-4 rounded-2xl border border-primary-200/60 bg-gradient-to-br from-primary-50/80 via-surface to-surface p-5 dark:border-primary-800/40 dark:from-primary-950/30 sm:flex-row sm:items-center sm:justify-between">
              <div className="flex items-start gap-4">
                <span className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-primary-600 text-white shadow-lg shadow-primary-600/25">
                  <IconPatients className="h-6 w-6" />
                </span>
                <div>
                  <p className="font-semibold text-text">Paciente não encontrado?</p>
                  <p className="mt-1 text-sm text-text-muted">
                    Registe um novo utente com os dados essenciais e continue para a triagem.
                  </p>
                </div>
              </div>
              <Button type="button" className="shrink-0 sm:min-w-[200px]" onClick={() => setStep("register")}>
                Registar novo paciente
              </Button>
            </div>
          </div>
        </Card>
      )}

      {step === "register" && (
        <Card title="Registo rápido" description="Preencha os dados mínimos para criar o processo clínico.">
          <form onSubmit={onRegisterSubmit} className="space-y-6" noValidate>
            <FormSection title="Dados pessoais">
              <div className="grid gap-4 sm:grid-cols-2">
                <Input
                  label="Nome completo"
                  error={registerForm.formState.errors.full_name?.message}
                  {...registerForm.register("full_name")}
                />
                <div className="space-y-1">
                  <label htmlFor="gender" className="block text-sm font-medium text-text">
                    Sexo
                  </label>
                  <select id="gender" {...registerForm.register("gender")} className={selectClassName()}>
                    {Object.entries(PATIENT_GENDER_LABELS).map(([value, label]) => (
                      <option key={value} value={value}>
                        {label}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <DisplayDateInput
                    label="Data de nascimento"
                    error={registerForm.formState.errors.birth_date?.message}
                    {...registerForm.register("birth_date")}
                  />
                  <ComputedAgeHint birthDate={watchedBirthDate} className="mt-1.5" />
                </div>
                <PhoneInput
                  label="Telefone"
                  error={registerForm.formState.errors.phone?.message}
                  {...registerForm.register("phone")}
                />
                <div className="space-y-1">
                  <label htmlFor="blood_type" className="block text-sm font-medium text-text">
                    Tipo de sangue <span className="font-normal text-text-muted">(opcional)</span>
                  </label>
                  <select id="blood_type" {...registerForm.register("blood_type")} className={selectClassName()}>
                    <option value="">Não indicado</option>
                    {Object.entries(BLOOD_TYPE_LABELS).map(([value, label]) => (
                      <option key={value} value={value}>
                        {label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </FormSection>

            {registerMinorAge !== null && registerMinorAge < 18 && (
              <FormSection
                title="Contacto de emergência"
                description="Obrigatório para pacientes menores de idade."
              >
                <div className="grid gap-4 rounded-2xl border border-amber-200/80 bg-amber-50/50 p-4 dark:border-amber-900/50 dark:bg-amber-950/20 sm:grid-cols-2">
                  <Input
                    label="Nome do contacto"
                    error={registerForm.formState.errors.emergency_contact_name?.message}
                    {...registerForm.register("emergency_contact_name")}
                  />
                  <PhoneInput
                    label="Telefone de emergência"
                    error={registerForm.formState.errors.emergency_contact_phone?.message}
                    {...registerForm.register("emergency_contact_phone")}
                  />
                </div>
              </FormSection>
            )}

            <div className="flex flex-wrap gap-3 border-t border-border pt-5">
              <Button type="button" variant="secondary" onClick={() => setStep("search")}>
                Voltar
              </Button>
              <Button type="submit" disabled={registerMutation.isPending}>
                {registerMutation.isPending ? "A registar..." : "Registar e continuar"}
              </Button>
            </div>
          </form>
        </Card>
      )}

      {step === "triage" && selectedPatient && (
        <div className="space-y-4">
          <div className="flex flex-wrap items-start justify-between gap-4 rounded-2xl border border-border bg-surface px-5 py-4">
            <div className="flex items-start gap-4">
              <img
                src="/branding/clinica-sauvida-logo.png"
                alt="Sãu Vida"
                className="h-10 w-auto object-contain"
              />
              <div>
                <h3 className="text-lg font-bold tracking-tight text-text">Ficha de Triagem</h3>
                <div className="mt-1 flex flex-wrap items-center gap-2">
                  <p className="text-sm text-text-muted">
                    {selectedPatient.patient_number}
                    {selectedPatient.phone ? ` · ${selectedPatient.phone}` : ""}
                  </p>
                  <PatientAgeCategoryBadge category={ageCategory} />
                </div>
              </div>
            </div>
            <div className="flex flex-wrap items-center gap-3">
              <Button type="button" variant="secondary" size="sm" onClick={() => setStep("search")}>
                Alterar paciente
              </Button>
            </div>
          </div>

          <Card>
            <form onSubmit={onTriageSubmit} className="space-y-8" noValidate>
              <div className="border-b border-border pb-6">
                <TriageColorPicker
                  value={triageColor}
                  onChange={(color) => triageForm.setValue("triage_color", color, { shouldValidate: true })}
                  error={triageForm.formState.errors.triage_color?.message}
                />
              </div>

              <FormSection
                title="Dados da ficha clínica"
                description="Só leitura aqui — altere na ficha do utente (nome, morada, nacionalidade, etc.)."
              >
                <div className="flex flex-wrap items-center justify-end gap-2">
                  <Link
                    to={`/patients/${selectedPatient.id}/edit`}
                    className="text-xs font-semibold text-primary-600 hover:text-primary-700"
                  >
                    Abrir ficha para editar →
                  </Link>
                </div>
                <div className="grid gap-4 rounded-2xl border border-dashed border-border bg-surface-muted/30 p-4 sm:grid-cols-2 lg:grid-cols-3">
                  <FichaReadonlyField label="Nome" value={selectedPatient.full_name} />
                  <FichaReadonlyField
                    label="Data de nascimento"
                    value={formatDisplayDate(patientDetail?.birth_date)}
                  />
                  <FichaReadonlyField label="Sexo" value={displayGender} />
                  {computedPatientAge !== null ? (
                    <FichaReadonlyField
                      label="Idade (anos)"
                      value={`${computedPatientAge} anos`}
                    />
                  ) : (
                    <FichaReadonlyField label="Idade (anos)" value="—" />
                  )}
                  <div className="min-w-0 space-y-1">
                    <p className="text-xs font-medium text-text-muted">Categoria (relatórios)</p>
                    <div className="pt-0.5">
                      <PatientAgeCategoryBadge category={ageCategory} />
                      {!ageCategory && (
                        <p className="text-sm text-text-muted">—</p>
                      )}
                    </div>
                  </div>
                  <FichaReadonlyField
                    label="Nacionalidade"
                    value={patientDetail?.nationality?.trim() || "—"}
                  />
                  <FichaReadonlyField label="Residência" value={formatPatientResidence(patientDetail)} />
                  <FichaReadonlyField label="Estado civil" value={displayMarital} />
                  <FichaReadonlyField
                    label="Profissão"
                    value={patientDetail?.occupation?.trim() || "—"}
                  />
                </div>
              </FormSection>

              <FormSection
                title="Medições nesta triagem"
                description="Peso, altura e raça — podem mudar em cada visita."
              >
                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                  <Input
                    label="Peso (kg)"
                    type="number"
                    step="0.1"
                    error={triageForm.formState.errors.weight?.message}
                    {...triageForm.register("weight", { valueAsNumber: true })}
                  />
                  <Input
                    label="Altura (cm)"
                    type="number"
                    hint="Opcional"
                    error={triageForm.formState.errors.height_cm?.message}
                    {...triageForm.register("height_cm", { valueAsNumber: true })}
                  />
                  <Input
                    label="Raça"
                    hint="Opcional"
                    error={triageForm.formState.errors.race?.message}
                    {...triageForm.register("race")}
                  />
                </div>
                {computedPatientAge === null && (
                  <Input
                    className="mt-4 max-w-xs"
                    label="Idade (anos)"
                    type="number"
                    hint="Só se a ficha não tem data de nascimento"
                    error={triageForm.formState.errors.age_at_check_in?.message}
                    {...triageForm.register("age_at_check_in", { valueAsNumber: true })}
                  />
                )}
              </FormSection>

              <FormSection
                title="Tipo de atendimento (faturação)"
                description="Consulta e controlo têm preços diferentes no catálogo."
              >
                <div className="flex flex-col gap-3 sm:flex-row">
                  {(["CONSULTA", "CONTROLE"] as VisitPurpose[]).map((value) => (
                    <label
                      key={value}
                      className={`flex cursor-pointer items-start gap-3 rounded-xl border p-4 transition ${
                        triageForm.watch("visit_purpose") === value
                          ? "border-primary-500 bg-primary-50/50 ring-2 ring-primary-500/20 dark:bg-primary-950/20"
                          : "border-border hover:border-primary-300"
                      }`}
                    >
                      <input
                        type="radio"
                        className="mt-1"
                        value={value}
                        {...triageForm.register("visit_purpose")}
                      />
                      <span className="text-sm font-medium text-text">{VISIT_PURPOSE_LABELS[value]}</span>
                    </label>
                  ))}
                </div>
              </FormSection>

              <FormSection title="Queixas" description="Motivo da visita e sintomas referidos.">
                <textarea
                  id="symptoms"
                  rows={4}
                  {...triageForm.register("symptoms")}
                  className="w-full rounded-xl border border-border bg-surface px-4 py-3 text-sm text-text shadow-sm outline-none transition focus:border-primary-500 focus:ring-2 focus:ring-primary-100 dark:focus:ring-primary-900"
                  placeholder="Descreva as queixas do utente..."
                />
                {triageForm.formState.errors.symptoms?.message && (
                  <div
                    role="alert"
                    className="flex items-start gap-2 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800 dark:border-red-900/60 dark:bg-red-950/50 dark:text-red-200"
                  >
                    <span
                      className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-md bg-red-600 text-xs font-bold text-white"
                      aria-hidden
                    >
                      !
                    </span>
                    <span>{triageForm.formState.errors.symptoms.message}</span>
                  </div>
                )}
              </FormSection>

              <FormSection title="Sinais vitais">
                {vitalWarnings.length > 0 && (
                  <div
                    className="rounded-xl border border-amber-200 bg-amber-50/90 p-4 text-sm text-amber-900 dark:border-amber-900/50 dark:bg-amber-950/30 dark:text-amber-100"
                    role="status"
                  >
                    <p className="font-semibold">Confirme os valores — fora do habitual</p>
                    <ul className="mt-2 list-disc space-y-1 pl-5">
                      {vitalWarnings.map((w) => (
                        <li key={w.field}>{w.message}</li>
                      ))}
                    </ul>
                    <p className="mt-2 text-xs text-amber-800/90 dark:text-amber-200/90">
                      Pode guardar se a medição está correcta (ex. hipotermia grave, oxímetro em
                      dedo frio).
                    </p>
                  </div>
                )}
                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                  <Input
                    label="TA (mmHg)"
                    placeholder="120/80"
                    hint="Sistólica / diastólica"
                    error={triageForm.formState.errors.blood_pressure?.message}
                    {...triageForm.register("blood_pressure")}
                  />
                  <Input
                    label="T (°C)"
                    type="number"
                    step="0.1"
                    hint="Normal ~36–37; abaixo de 35 pode indicar hipotermia"
                    error={triageForm.formState.errors.temperature?.message}
                    {...triageForm.register("temperature", { valueAsNumber: true })}
                  />
                  <Input
                    label="SpO₂ (%)"
                    type="number"
                    hint="Opcional"
                    error={triageForm.formState.errors.spo2?.message}
                    {...triageForm.register("spo2", { valueAsNumber: true })}
                  />
                  <Input
                    label="FC (b/min)"
                    type="number"
                    hint="Opcional — habitual entre 60 e 100"
                    error={triageForm.formState.errors.heart_rate?.message}
                    {...triageForm.register("heart_rate", { valueAsNumber: true })}
                  />
                  <Input
                    label="FR (c/min)"
                    type="number"
                    hint="Opcional"
                    error={triageForm.formState.errors.respiratory_rate?.message}
                    {...triageForm.register("respiratory_rate", { valueAsNumber: true })}
                  />
                  <FichaReadonlyField label="Data" value={vitalsDateLabel()} />
                </div>
              </FormSection>

              <Input label="Notas adicionais" hint="Opcional" {...triageForm.register("notes")} />

              <FormSection title="Profissionais">
                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="rounded-xl border border-border bg-surface px-4 py-3">
                    <p className="text-xs font-medium text-text-muted">Enfermeiro/a</p>
                    <p className="mt-1 text-sm font-medium text-text">{nurseName}</p>
                  </div>
                  <div className="rounded-xl border border-border bg-surface px-4 py-3">
                    <p className="text-xs font-medium text-text-muted">Médico/a</p>
                    <p className="mt-1 text-sm font-medium text-text">{doctorName}</p>
                  </div>
                </div>
                {user?.full_name && user.role === "RECECIONISTA" && (
                  <p className="text-xs text-text-muted">
                    Triagem registada por recepção: {user.full_name}
                  </p>
                )}
              </FormSection>

              <div className="flex flex-wrap gap-3 border-t border-border pt-5">
                <Button type="button" variant="secondary" onClick={() => setStep("search")}>
                  Voltar
                </Button>
                <Button type="submit" disabled={checkInMutation.isPending} className="min-w-[220px]">
                  {checkInMutation.isPending ? "A processar..." : "Concluir triagem"}
                </Button>
              </div>
            </form>
          </Card>
        </div>
      )}
    </div>
  );
}

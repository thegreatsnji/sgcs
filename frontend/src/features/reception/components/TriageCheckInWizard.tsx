import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useState, type ReactNode } from "react";
import { useForm } from "react-hook-form";

import { IconPatients } from "@/components/icons";
import { PhoneInput } from "@/components/forms";
import { Button, Card, Input, useToast } from "@/design-system";
import { BLOOD_TYPE_LABELS, PATIENT_GENDER_LABELS } from "@/constants/patients";
import { PatientSearchSelect } from "@/features/reception/components/PatientSearchSelect";
import { TriageColorPicker } from "@/features/reception/components/TriageColorPicker";
import { TriageWizardSteps, type WizardStep } from "@/features/reception/components/TriageWizardSteps";
import {
  quickPatientSchema,
  triageSchema,
  type QuickPatientFormData,
  type TriageFormData,
} from "@/features/reception/schemas/triageSchema";
import { patientsService } from "@/services/patients";
import { receptionService } from "@/services/reception";
import type { PatientListItem } from "@/types/patient";
import type { TriageColor } from "@/types/reception";
import { getApiErrorMessage } from "@/utils/api-error";
import { ageToBirthDateDisplay } from "@/utils/date";
import { toFullPhone } from "@/utils/phone";

interface SelectedPatient {
  id: number;
  full_name: string;
  patient_number: string;
  phone: string | null;
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

export function TriageCheckInWizard() {
  const { showToast } = useToast();
  const queryClient = useQueryClient();
  const [step, setStep] = useState<WizardStep>("search");
  const [selectedPatient, setSelectedPatient] = useState<SelectedPatient | null>(null);

  const registerForm = useForm<QuickPatientFormData>({
    resolver: zodResolver(quickPatientSchema),
    defaultValues: {
      first_name: "",
      last_name: "",
      gender: "M",
      phone: "",
      age: 30,
      blood_type: "",
      emergency_contact_name: "",
      emergency_contact_phone: "",
    },
  });

  const triageForm = useForm<TriageFormData>({
    resolver: zodResolver(triageSchema),
    defaultValues: {
      age_at_check_in: 30,
      weight: undefined,
      temperature: undefined,
      blood_pressure: "",
      symptoms: "",
      triage_color: "GREEN",
      notes: "",
    },
  });

  const registerMutation = useMutation({
    mutationFn: patientsService.create,
    onSuccess: (patient) => {
      setSelectedPatient({
        id: patient.id,
        full_name: patient.full_name,
        patient_number: patient.patient_number,
        phone: patient.phone ?? null,
      });
      triageForm.setValue("age_at_check_in", registerForm.getValues("age"));
      setStep("triage");
      showToast("Paciente registado. Prossiga com a triagem.", "success");
    },
    onError: (error) => showToast(getApiErrorMessage(error), "error"),
  });

  const checkInMutation = useMutation({
    mutationFn: receptionService.checkIn,
    onSuccess: () => {
      showToast("Triagem concluída. Paciente adicionado à fila.", "success");
      resetWizard();
      void queryClient.invalidateQueries({ queryKey: ["reception-queue"] });
      void queryClient.invalidateQueries({ queryKey: ["reception-dashboard"] });
      void queryClient.invalidateQueries({ queryKey: ["reception-history"] });
      void queryClient.invalidateQueries({ queryKey: ["patients-search"] });
    },
    onError: (error) => showToast(getApiErrorMessage(error), "error"),
  });

  const resetWizard = () => {
    setStep("search");
    setSelectedPatient(null);
    registerForm.reset();
    triageForm.reset({
      age_at_check_in: 30,
      triage_color: "GREEN",
      notes: "",
      blood_pressure: "",
      symptoms: "",
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
    });
    if (patient.birth_date) {
      const match = /^(\d{2})\/(\d{2})\/(\d{4})$/.exec(patient.birth_date);
      if (match) {
        const birth = new Date(Number(match[3]), Number(match[2]) - 1, Number(match[1]));
        const today = new Date();
        let age = today.getFullYear() - birth.getFullYear();
        const monthDiff = today.getMonth() - birth.getMonth();
        if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
          age -= 1;
        }
        triageForm.setValue("age_at_check_in", age);
      }
    }
    setStep("triage");
  };

  const onRegisterSubmit = registerForm.handleSubmit((values) => {
    registerMutation.mutate({
      first_name: values.first_name.trim(),
      last_name: values.last_name.trim(),
      gender: values.gender,
      phone: toFullPhone(values.phone.trim()),
      birth_date: ageToBirthDateDisplay(values.age),
      blood_type: values.blood_type || undefined,
      emergency_contacts:
        values.age < 18
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
    checkInMutation.mutate({
      patient_id: selectedPatient.id,
      triage_color: values.triage_color,
      age_at_check_in: values.age_at_check_in,
      weight: values.weight,
      temperature: values.temperature,
      blood_pressure: values.blood_pressure.trim(),
      symptoms: values.symptoms.trim(),
      notes: values.notes?.trim(),
    });
  });

  const watchedAge = registerForm.watch("age");
  const triageColor = triageForm.watch("triage_color") as TriageColor;

  return (
    <div className="space-y-6">
      <TriageWizardSteps current={step} />

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
          <form onSubmit={onRegisterSubmit} className="space-y-6">
            <FormSection title="Dados pessoais">
              <div className="grid gap-4 sm:grid-cols-2">
                <Input
                  label="Nome"
                  error={registerForm.formState.errors.first_name?.message}
                  {...registerForm.register("first_name")}
                />
                <Input
                  label="Apelido"
                  error={registerForm.formState.errors.last_name?.message}
                  {...registerForm.register("last_name")}
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
                <Input
                  label="Idade"
                  type="number"
                  min={0}
                  max={120}
                  error={registerForm.formState.errors.age?.message}
                  {...registerForm.register("age", { valueAsNumber: true })}
                />
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

            {watchedAge < 18 && (
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
          <div className="flex flex-wrap items-center justify-between gap-4 rounded-2xl border border-border bg-gradient-to-r from-surface via-primary-50/30 to-surface px-5 py-4 dark:from-surface dark:via-primary-950/20 dark:to-surface">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-primary-600 dark:text-primary-400">
                Utente seleccionado
              </p>
              <p className="mt-1 text-lg font-bold text-text">{selectedPatient.full_name}</p>
              <p className="text-sm text-text-muted">
                {selectedPatient.patient_number}
                {selectedPatient.phone ? ` · ${selectedPatient.phone}` : ""}
              </p>
            </div>
            <Button type="button" variant="secondary" size="sm" onClick={() => setStep("search")}>
              Alterar paciente
            </Button>
          </div>

          <Card title="Triagem clínica" description="Registe sinais vitais, sintomas e classifique a urgência.">
            <form onSubmit={onTriageSubmit} className="space-y-8">
              <FormSection title="Sinais vitais" description="Medições na recepção.">
                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                  <Input
                    label="Idade"
                    type="number"
                    min={0}
                    max={120}
                    error={triageForm.formState.errors.age_at_check_in?.message}
                    {...triageForm.register("age_at_check_in", { valueAsNumber: true })}
                  />
                  <Input
                    label="Peso (kg)"
                    type="number"
                    step="0.1"
                    min={0}
                    error={triageForm.formState.errors.weight?.message}
                    {...triageForm.register("weight", { valueAsNumber: true })}
                  />
                  <Input
                    label="Temperatura (°C)"
                    type="number"
                    step="0.1"
                    min={34}
                    max={43}
                    error={triageForm.formState.errors.temperature?.message}
                    {...triageForm.register("temperature", { valueAsNumber: true })}
                  />
                  <Input
                    label="Pressão arterial"
                    placeholder="120/80"
                    hint="Sistólica / diastólica"
                    error={triageForm.formState.errors.blood_pressure?.message}
                    {...triageForm.register("blood_pressure")}
                  />
                </div>
              </FormSection>

              <FormSection title="Sintomas" description="Motivo da visita e queixas principais.">
                <textarea
                  id="symptoms"
                  rows={4}
                  {...triageForm.register("symptoms")}
                  className="w-full rounded-xl border border-border bg-surface px-4 py-3 text-sm text-text shadow-sm outline-none transition focus:border-primary-500 focus:ring-2 focus:ring-primary-100 dark:focus:ring-primary-900"
                  placeholder="Ex.: febre há 2 dias, dor de cabeça, tonturas..."
                />
                {triageForm.formState.errors.symptoms?.message && (
                  <p className="text-xs text-red-600">{triageForm.formState.errors.symptoms.message}</p>
                )}
              </FormSection>

              <TriageColorPicker
                value={triageColor}
                onChange={(color) => triageForm.setValue("triage_color", color, { shouldValidate: true })}
                error={triageForm.formState.errors.triage_color?.message}
              />

              <Input label="Notas adicionais" hint="Opcional" {...triageForm.register("notes")} />

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

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useParams } from "react-router-dom";

import {
  Badge,
  Button,
  Card,
  EmptyState,
  ErrorState,
  LoadingState,
  Table,
  useToast,
} from "@/design-system";
import { AllergyFormModal } from "@/features/patients/components/AllergyFormModal";
import { AllergyAlertBanner } from "@/features/patients/components/AllergyAlertBanner";
import { ChronicDiseaseFormModal } from "@/features/patients/components/ChronicDiseaseFormModal";
import { ObservationFormModal } from "@/features/patients/components/ObservationFormModal";
import { PatientHeader } from "@/features/patients/components/PatientHeader";
import { PatientSubNav } from "@/features/patients/components/PatientSubNav";
import {
  ALLERGY_SEVERITY_LABELS,
  CHRONIC_DISEASE_STATUS_LABELS,
  OBSERVATION_TYPE_LABELS,
} from "@/constants/patients";
import { usePermissions } from "@/hooks/usePermissions";
import type { AllergyFormData, ChronicDiseaseFormData, ObservationFormData } from "@/schemas/patientSchema";
import { patientsService } from "@/services/patients";
import type { PatientAllergy, PatientChronicDisease, PatientObservation } from "@/types/patient";
import { getApiErrorMessage } from "@/utils/api-error";
import { formatDisplayDate } from "@/utils/date";

export function PatientClinicalPage() {
  const { id } = useParams();
  const patientId = Number(id);
  const queryClient = useQueryClient();
  const { showToast } = useToast();
  const { hasPermission } = usePermissions();

  const [allergyModal, setAllergyModal] = useState<PatientAllergy | null | "new">(null);
  const [diseaseModal, setDiseaseModal] = useState<PatientChronicDisease | null | "new">(null);
  const [observationModal, setObservationModal] = useState<PatientObservation | null | "new">(null);

  const { data: patient, isLoading: patientLoading } = useQuery({
    queryKey: ["patient", id],
    queryFn: () => patientsService.get(patientId),
  });

  const { data: allergies, isLoading: allergiesLoading, isError, refetch } = useQuery({
    queryKey: ["patient-allergies", id],
    queryFn: () => patientsService.listAllergies(patientId),
  });

  const { data: diseases } = useQuery({
    queryKey: ["patient-chronic-diseases", id],
    queryFn: () => patientsService.listChronicDiseases(patientId),
  });

  const { data: observations } = useQuery({
    queryKey: ["patient-observations", id],
    queryFn: () => patientsService.listObservations(patientId),
  });

  const invalidateClinical = () => {
    void queryClient.invalidateQueries({ queryKey: ["patient-allergies", id] });
    void queryClient.invalidateQueries({ queryKey: ["patient-chronic-diseases", id] });
    void queryClient.invalidateQueries({ queryKey: ["patient-observations", id] });
    void queryClient.invalidateQueries({ queryKey: ["patient", id] });
    void queryClient.invalidateQueries({ queryKey: ["patient-history", id] });
  };

  const allergyMutation = useMutation({
    mutationFn: (payload: AllergyFormData) => {
      const body = {
        ...payload,
        reaction: payload.reaction || null,
        diagnosed_at: payload.diagnosed_at || null,
        notes: payload.notes || null,
      };
      if (allergyModal && allergyModal !== "new") {
        return patientsService.updateAllergy(patientId, allergyModal.id, body);
      }
      return patientsService.createAllergy(patientId, body);
    },
    onSuccess: () => {
      showToast("Alergia guardada com sucesso.", "success");
      setAllergyModal(null);
      invalidateClinical();
    },
    onError: (error) => showToast(getApiErrorMessage(error), "error"),
  });

  const diseaseMutation = useMutation({
    mutationFn: (payload: ChronicDiseaseFormData) => {
      const body = {
        ...payload,
        icd_code: payload.icd_code || null,
        diagnosed_at: payload.diagnosed_at || null,
        notes: payload.notes || null,
      };
      if (diseaseModal && diseaseModal !== "new") {
        return patientsService.updateChronicDisease(patientId, diseaseModal.id, body);
      }
      return patientsService.createChronicDisease(patientId, body);
    },
    onSuccess: () => {
      showToast("Doença crónica guardada com sucesso.", "success");
      setDiseaseModal(null);
      invalidateClinical();
    },
    onError: (error) => showToast(getApiErrorMessage(error), "error"),
  });

  const observationMutation = useMutation({
    mutationFn: (payload: ObservationFormData) => {
      if (observationModal && observationModal !== "new") {
        return patientsService.updateObservation(patientId, observationModal.id, payload);
      }
      return patientsService.createObservation(patientId, payload);
    },
    onSuccess: () => {
      showToast("Observação guardada com sucesso.", "success");
      setObservationModal(null);
      invalidateClinical();
    },
    onError: (error) => showToast(getApiErrorMessage(error), "error"),
  });

  const deleteAllergy = useMutation({
    mutationFn: (allergyId: number) => patientsService.deleteAllergy(patientId, allergyId),
    onSuccess: () => {
      showToast("Alergia removida.", "success");
      invalidateClinical();
    },
    onError: (error) => showToast(getApiErrorMessage(error), "error"),
  });

  if (patientLoading || allergiesLoading) return <LoadingState message="A carregar ficha clínica..." />;
  if (isError || !patient) {
    return <ErrorState message="Não foi possível carregar a ficha clínica." onRetry={() => void refetch()} />;
  }

  const allergyRows = allergies?.results ?? [];
  const diseaseRows = diseases?.results ?? [];
  const observationRows = observations?.results ?? [];
  const canEdit = hasPermission("patients.edit");

  return (
    <div className="space-y-6">
      <PatientHeader patient={patient} />
      <PatientSubNav />
      <AllergyAlertBanner allergies={allergyRows} />

      <Card
        title="Alergias"
        footer={
          canEdit ? (
            <Button onClick={() => setAllergyModal("new")}>Registar alergia</Button>
          ) : undefined
        }
      >
        {allergyRows.length === 0 ? (
          <EmptyState title="Sem alergias" description="Não existem alergias registadas." />
        ) : (
          <Table<PatientAllergy>
            getRowKey={(row) => row.id}
            data={allergyRows}
            columns={[
              { key: "allergen", header: "Alergénio" },
              {
                key: "severity",
                header: "Severidade",
                render: (row) => ALLERGY_SEVERITY_LABELS[row.severity],
              },
              { key: "reaction", header: "Reação" },
              {
                key: "diagnosed_at",
                header: "Diagnosticado em",
                render: (row) => formatDisplayDate(row.diagnosed_at),
              },
              {
                key: "actions",
                header: "Ações",
                render: (row) =>
                  canEdit ? (
                    <div className="flex gap-2">
                      <Button size="sm" variant="outline" onClick={() => setAllergyModal(row)}>
                        Editar
                      </Button>
                      <Button size="sm" variant="danger" onClick={() => deleteAllergy.mutate(row.id)}>
                        Remover
                      </Button>
                    </div>
                  ) : null,
              },
            ]}
          />
        )}
      </Card>

      <Card
        title="Doenças crónicas"
        footer={
          canEdit ? (
            <Button onClick={() => setDiseaseModal("new")}>Registar doença</Button>
          ) : undefined
        }
      >
        {diseaseRows.length === 0 ? (
          <EmptyState title="Sem doenças crónicas" description="Não existem registos clínicos." />
        ) : (
          <Table<PatientChronicDisease>
            getRowKey={(row) => row.id}
            data={diseaseRows}
            columns={[
              { key: "disease_name", header: "Doença" },
              { key: "icd_code", header: "CID" },
              {
                key: "status",
                header: "Estado",
                render: (row) => CHRONIC_DISEASE_STATUS_LABELS[row.status],
              },
              {
                key: "diagnosed_at",
                header: "Diagnosticado em",
                render: (row) => formatDisplayDate(row.diagnosed_at),
              },
              {
                key: "actions",
                header: "Ações",
                render: (row) =>
                  canEdit ? (
                    <Button size="sm" variant="outline" onClick={() => setDiseaseModal(row)}>
                      Editar
                    </Button>
                  ) : null,
              },
            ]}
          />
        )}
      </Card>

      <Card
        title="Observações"
        footer={
          canEdit ? (
            <Button onClick={() => setObservationModal("new")}>Nova observação</Button>
          ) : undefined
        }
      >
        {observationRows.length === 0 ? (
          <EmptyState title="Sem observações" description="Ainda não foram registadas observações." />
        ) : (
          <div className="space-y-3">
            {observationRows.map((observation) => (
              <div key={observation.id} className="rounded-lg border border-slate-200 p-4">
                <div className="mb-2 flex flex-wrap items-center gap-2">
                  <Badge variant="info">{OBSERVATION_TYPE_LABELS[observation.observation_type]}</Badge>
                  {observation.is_pinned && <Badge variant="warning">Fixada</Badge>}
                </div>
                <p className="text-sm text-slate-700">{observation.content}</p>
                {canEdit && (
                  <div className="mt-3">
                    <Button size="sm" variant="outline" onClick={() => setObservationModal(observation)}>
                      Editar
                    </Button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </Card>

      <AllergyFormModal
        open={allergyModal !== null}
        initial={allergyModal && allergyModal !== "new" ? allergyModal : null}
        isSubmitting={allergyMutation.isPending}
        onClose={() => setAllergyModal(null)}
        onSubmit={(data) => allergyMutation.mutate(data)}
      />
      <ChronicDiseaseFormModal
        open={diseaseModal !== null}
        initial={diseaseModal && diseaseModal !== "new" ? diseaseModal : null}
        isSubmitting={diseaseMutation.isPending}
        onClose={() => setDiseaseModal(null)}
        onSubmit={(data) => diseaseMutation.mutate(data)}
      />
      <ObservationFormModal
        open={observationModal !== null}
        initial={observationModal && observationModal !== "new" ? observationModal : null}
        isSubmitting={observationMutation.isPending}
        onClose={() => setObservationModal(null)}
        onSubmit={(data) => observationMutation.mutate(data)}
      />
    </div>
  );
}

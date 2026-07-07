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
import { DocumentUploadModal } from "@/features/patients/components/DocumentUploadModal";
import { PatientHeader } from "@/features/patients/components/PatientHeader";
import { PatientSubNav } from "@/features/patients/components/PatientSubNav";
import { PATIENT_DOCUMENT_TYPE_LABELS } from "@/constants/patients";
import { usePermissions } from "@/hooks/usePermissions";
import type { DocumentUploadFormData } from "@/schemas/patientSchema";
import { patientsService } from "@/services/patients";
import type { PatientDocument } from "@/types/patient";
import { getApiErrorMessage } from "@/utils/api-error";
import { formatDisplayDate } from "@/utils/date";

export function PatientDocumentsPage() {
  const { id } = useParams();
  const patientId = Number(id);
  const queryClient = useQueryClient();
  const { showToast } = useToast();
  const { hasPermission } = usePermissions();
  const [uploadOpen, setUploadOpen] = useState(false);

  const { data: patient, isLoading: patientLoading } = useQuery({
    queryKey: ["patient", id],
    queryFn: () => patientsService.get(patientId),
  });

  const { data: documents, isLoading, isError, refetch } = useQuery({
    queryKey: ["patient-documents", id],
    queryFn: () => patientsService.listDocuments(patientId),
  });

  const { data: photos } = useQuery({
    queryKey: ["patient-photos", id],
    queryFn: () => patientsService.listPhotos(patientId),
  });

  const uploadMutation = useMutation({
    mutationFn: (formData: DocumentUploadFormData) => {
      const data = new FormData();
      const file = formData.file instanceof FileList ? formData.file[0] : formData.file;
      if (file) data.append("file", file);
      data.append("document_type", formData.document_type);
      data.append("title", formData.title);
      if (formData.document_number) data.append("document_number", formData.document_number);
      if (formData.description) data.append("description", formData.description);
      if (formData.issued_at) data.append("issued_at", formData.issued_at);
      if (formData.expires_at) data.append("expires_at", formData.expires_at);
      return patientsService.uploadDocument(patientId, data);
    },
    onSuccess: () => {
      showToast("Documento carregado com sucesso.", "success");
      setUploadOpen(false);
      void queryClient.invalidateQueries({ queryKey: ["patient-documents", id] });
      void queryClient.invalidateQueries({ queryKey: ["patient-history", id] });
    },
    onError: (error) => showToast(getApiErrorMessage(error), "error"),
  });

  const deleteMutation = useMutation({
    mutationFn: (documentId: number) => patientsService.deleteDocument(patientId, documentId),
    onSuccess: () => {
      showToast("Documento removido.", "success");
      void queryClient.invalidateQueries({ queryKey: ["patient-documents", id] });
    },
    onError: (error) => showToast(getApiErrorMessage(error), "error"),
  });

  if (patientLoading || isLoading) return <LoadingState message="A carregar documentos..." />;
  if (isError || !patient) {
    return <ErrorState message="Não foi possível carregar os documentos." onRetry={() => void refetch()} />;
  }

  const documentRows = documents?.results ?? [];
  const photoRows = photos?.results ?? [];
  const canUpload = hasPermission("patients.create");
  const canEdit = hasPermission("patients.edit");

  return (
    <div className="space-y-6">
      <PatientHeader patient={patient} />
      <PatientSubNav />

      <Card
        title="Documentos"
        footer={
          canUpload ? <Button onClick={() => setUploadOpen(true)}>Carregar documento</Button> : undefined
        }
      >
        {documentRows.length === 0 ? (
          <EmptyState title="Sem documentos" description="Não existem documentos associados." />
        ) : (
          <Table<PatientDocument>
            getRowKey={(row) => row.id}
            data={documentRows}
            columns={[
              { key: "title", header: "Título" },
              {
                key: "document_type",
                header: "Tipo",
                render: (row) => PATIENT_DOCUMENT_TYPE_LABELS[row.document_type],
              },
              {
                key: "expires_at",
                header: "Validade",
                render: (row) => formatDisplayDate(row.expires_at),
              },
              {
                key: "file_url",
                header: "Ficheiro",
                render: (row) =>
                  row.file_url ? (
                    <a href={row.file_url} target="_blank" rel="noreferrer" className="text-primary-700 underline">
                      Abrir
                    </a>
                  ) : (
                    "—"
                  ),
              },
              {
                key: "actions",
                header: "Ações",
                render: (row) =>
                  canEdit ? (
                    <Button size="sm" variant="danger" onClick={() => deleteMutation.mutate(row.id)}>
                      Remover
                    </Button>
                  ) : null,
              },
            ]}
          />
        )}
      </Card>

      <Card title="Fotografias">
        {photoRows.length === 0 ? (
          <EmptyState title="Sem fotografias" description="Não existem fotografias do paciente." />
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {photoRows.map((photo) => (
              <div key={photo.id} className="overflow-hidden rounded-lg border border-slate-200">
                {photo.file_url ? (
                  <img src={photo.file_url} alt={photo.title ?? "Foto do paciente"} className="h-40 w-full object-cover" />
                ) : (
                  <div className="flex h-40 items-center justify-center bg-slate-100 text-sm text-slate-500">
                    Sem imagem
                  </div>
                )}
                <div className="p-3 text-sm">
                  <div className="font-medium text-slate-900">{photo.title ?? "Fotografia"}</div>
                  {photo.is_primary && <Badge variant="success">Principal</Badge>}
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>

      <DocumentUploadModal
        open={uploadOpen}
        isSubmitting={uploadMutation.isPending}
        onClose={() => setUploadOpen(false)}
        onSubmit={(data) => uploadMutation.mutate(data)}
      />
    </div>
  );
}

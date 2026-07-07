import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import {
  Badge,
  Button,
  Card,
  EmptyState,
  ErrorState,
  LoadingState,
  Modal,
  Pagination,
  Table,
  useToast,
} from "@/design-system";
import { PatientFilters } from "@/features/patients/components/PatientFilters";
import { PATIENT_GENDER_LABELS, PATIENT_PAGE_SIZE } from "@/constants/patients";
import { useDebouncedValue } from "@/hooks/useDebouncedValue";
import { usePermissions } from "@/hooks/usePermissions";
import { patientsService } from "@/services/patients";
import type { PatientListItem } from "@/types/patient";
import { getApiErrorMessage } from "@/utils/api-error";
import { formatDisplayDate } from "@/utils/date";

export function PatientsListPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { showToast } = useToast();
  const { hasPermission } = usePermissions();

  const [search, setSearch] = useState("");
  const [gender, setGender] = useState("");
  const [isActive, setIsActive] = useState("true");
  const [page, setPage] = useState(1);
  const [deactivateTarget, setDeactivateTarget] = useState<PatientListItem | null>(null);

  const debouncedSearch = useDebouncedValue(search);

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["patients", page, debouncedSearch, gender, isActive],
    queryFn: () =>
      patientsService.list({
        page,
        search: debouncedSearch || undefined,
        gender: (gender as PatientListItem["gender"]) || undefined,
        is_active: isActive === "" ? undefined : isActive === "true",
      }),
  });

  const deactivateMutation = useMutation({
    mutationFn: (id: number) => patientsService.deactivate(id),
    onSuccess: () => {
      showToast("Paciente desativado com sucesso.", "success");
      setDeactivateTarget(null);
      void queryClient.invalidateQueries({ queryKey: ["patients"] });
    },
    onError: (error) => showToast(getApiErrorMessage(error), "error"),
  });

  const activateMutation = useMutation({
    mutationFn: (id: number) => patientsService.activate(id),
    onSuccess: () => {
      showToast("Paciente ativado com sucesso.", "success");
      void queryClient.invalidateQueries({ queryKey: ["patients"] });
    },
    onError: (error) => showToast(getApiErrorMessage(error), "error"),
  });

  const exportMutation = useMutation({
    mutationFn: () => patientsService.export("csv"),
    onSuccess: (result) => {
      showToast(
        result.ready ? "Exportação iniciada." : "Exportação em desenvolvimento.",
        result.ready ? "success" : "info",
      );
    },
    onError: (error) => showToast(getApiErrorMessage(error), "error"),
  });

  if (isLoading) return <LoadingState message="A carregar pacientes..." />;
  if (isError) return <ErrorState message="Não foi possível carregar a lista." onRetry={() => void refetch()} />;

  const patients = data?.results ?? [];
  const totalPages = Math.max(1, Math.ceil((data?.count ?? 0) / PATIENT_PAGE_SIZE));

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">Pacientes</h2>
          <p className="text-sm text-slate-500">Gestão de utentes da clínica</p>
        </div>
        <div className="flex flex-wrap gap-2">
          {hasPermission("patients.export") && (
            <Button variant="outline" onClick={() => exportMutation.mutate()} isLoading={exportMutation.isPending}>
              Exportar
            </Button>
          )}
          {hasPermission("patients.create") && (
            <Link to="/patients/new">
              <Button>+ Novo Paciente</Button>
            </Link>
          )}
        </div>
      </div>

      <Card>
        <div className="mb-4">
          <PatientFilters
            search={search}
            gender={gender}
            isActive={isActive}
            onSearchChange={(value) => {
              setSearch(value);
              setPage(1);
            }}
            onGenderChange={(value) => {
              setGender(value);
              setPage(1);
            }}
            onIsActiveChange={(value) => {
              setIsActive(value);
              setPage(1);
            }}
          />
        </div>

        {patients.length === 0 ? (
          <EmptyState
            title="Sem pacientes"
            description="Não foram encontrados registos com os filtros actuais."
          />
        ) : (
          <Table<PatientListItem>
            getRowKey={(row) => row.id}
            data={patients}
            columns={[
              { key: "patient_number", header: "N.º processo" },
              { key: "full_name", header: "Nome" },
              { key: "document_number", header: "Documento" },
              { key: "phone", header: "Telefone" },
              {
                key: "birth_date",
                header: "Nascimento",
                render: (row) => formatDisplayDate(row.birth_date),
              },
              {
                key: "gender",
                header: "Género",
                render: (row) => (row.gender ? PATIENT_GENDER_LABELS[row.gender] : "—"),
              },
              {
                key: "is_active",
                header: "Estado",
                render: (row) => (
                  <Badge variant={row.is_active ? "success" : "default"}>
                    {row.is_active ? "Ativo" : "Inativo"}
                  </Badge>
                ),
              },
              {
                key: "actions",
                header: "Ações",
                render: (row) => (
                  <div className="flex flex-wrap gap-2">
                    <Button size="sm" variant="outline" onClick={() => navigate(`/patients/${row.id}`)}>
                      Ver
                    </Button>
                    {hasPermission("patients.edit") && (
                      <Link to={`/patients/${row.id}/edit`}>
                        <Button size="sm" variant="secondary">
                          Editar
                        </Button>
                      </Link>
                    )}
                    {row.is_active
                      ? hasPermission("patients.delete") && (
                          <Button size="sm" variant="danger" onClick={() => setDeactivateTarget(row)}>
                            Desativar
                          </Button>
                        )
                      : hasPermission("patients.edit") && (
                          <Button size="sm" variant="ghost" onClick={() => activateMutation.mutate(row.id)}>
                            Ativar
                          </Button>
                        )}
                  </div>
                ),
              },
            ]}
          />
        )}

        <div className="mt-4 flex flex-wrap items-center justify-between gap-4">
          <span className="text-sm text-slate-600">Total: {data?.count ?? 0}</span>
          <Pagination page={page} totalPages={totalPages} onPageChange={setPage} />
        </div>
      </Card>

      <Modal
        open={Boolean(deactivateTarget)}
        title="Desativar paciente"
        description={`Confirma a desativação de ${deactivateTarget?.full_name}?`}
        confirmLabel="Desativar"
        onConfirm={() => deactivateTarget && deactivateMutation.mutate(deactivateTarget.id)}
        onClose={() => setDeactivateTarget(null)}
      />
    </div>
  );
}

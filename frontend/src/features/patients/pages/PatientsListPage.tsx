import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { Link } from "react-router-dom";

import { IconPatients } from "@/components/icons";
import { KpiCard } from "@/components/ui/KpiCard";
import {
  Button,
  EmptyState,
  ErrorState,
  Modal,
  Pagination,
  useToast,
} from "@/design-system";
import { PatientFilters } from "@/features/patients/components/PatientFilters";
import { PatientMobileCard } from "@/features/patients/components/PatientMobileCard";
import { PatientsListSkeleton } from "@/features/patients/components/PatientsListSkeleton";
import { PatientsTable } from "@/features/patients/components/PatientsTable";
import { PATIENT_PAGE_SIZE } from "@/constants/patients";
import { useDebouncedValue } from "@/hooks/useDebouncedValue";
import { usePermissions } from "@/hooks/usePermissions";
import { dashboardService } from "@/services/dashboard";
import { patientsService } from "@/services/patients";
import type { PatientListItem } from "@/types/patient";
import { getApiErrorMessage } from "@/utils/api-error";

import { getPatientAge, matchesAgeGroup, type AgeGroup } from "../utils/patientUtils";

export function PatientsListPage() {
  const queryClient = useQueryClient();
  const { showToast } = useToast();
  const { hasPermission } = usePermissions();

  const [search, setSearch] = useState("");
  const [gender, setGender] = useState("");
  const [isActive, setIsActive] = useState("true");
  const [ageGroup, setAgeGroup] = useState<AgeGroup>("");
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

  const { data: kpiData } = useQuery({
    queryKey: ["clinical-dashboard"],
    queryFn: dashboardService.getClinicalSummary,
    enabled: hasPermission("patients.view"),
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

  const patients = data?.results ?? [];

  const filteredPatients = useMemo(
    () =>
      ageGroup
        ? patients.filter((p) => matchesAgeGroup(getPatientAge(p.birth_date), ageGroup))
        : patients,
    [patients, ageGroup],
  );

  const totalPages = Math.max(1, Math.ceil((data?.count ?? 0) / PATIENT_PAGE_SIZE));

  if (isLoading) return <PatientsListSkeleton />;
  if (isError) return <ErrorState message="Não foi possível carregar a lista." onRetry={() => void refetch()} />;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">Pacientes</h1>
          <p className="mt-1 text-slate-500">Gestão profissional de utentes da clínica</p>
        </div>
        <div className="flex flex-wrap gap-2">
          {hasPermission("patients.export") && (
            <Button variant="outline" onClick={() => exportMutation.mutate()} isLoading={exportMutation.isPending}>
              Exportar
            </Button>
          )}
          {hasPermission("patients.create") && (
            <Link to="/patients/new">
              <Button size="lg">+ Novo Paciente</Button>
            </Link>
          )}
        </div>
      </div>

      {kpiData && (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <KpiCard
            label="Total de Pacientes"
            value={kpiData.cards.total_patients.toLocaleString("pt-PT")}
            icon={<IconPatients />}
            badge={{ text: "Registos totais", variant: "info" }}
          />
          <KpiCard
            label="Novos Recentes"
            value={kpiData.cards.new_patients_week}
            badge={{ text: "Últimos 7 dias", variant: "success" }}
          />
          <KpiCard
            label="Pacientes Activos"
            value={kpiData.cards.active_patients.toLocaleString("pt-PT")}
            badge={{ text: "Em acompanhamento", variant: "success" }}
          />
          <KpiCard
            label="Pacientes Inactivos"
            value={kpiData.cards.inactive_patients.toLocaleString("pt-PT")}
            badge={
              kpiData.cards.inactive_patients > 0
                ? { text: "Rever cadastro", variant: "warning" }
                : { text: "Sem pendências", variant: "default" }
            }
          />
        </div>
      )}

      <div className="overflow-hidden rounded-2xl border border-slate-200/80 bg-white shadow-sm">
        <div className="border-b border-slate-100 p-6">
          <PatientFilters
            search={search}
            gender={gender}
            isActive={isActive}
            ageGroup={ageGroup}
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
            onAgeGroupChange={(value) => setAgeGroup(value)}
          />
        </div>

        <div className="p-6 pt-0">
          {filteredPatients.length === 0 ? (
            <EmptyState
              title="Sem pacientes"
              description="Não foram encontrados registos com os filtros actuais. Tente ajustar a pesquisa ou os filtros."
            />
          ) : (
            <>
              <PatientsTable
                patients={filteredPatients}
                onDeactivate={setDeactivateTarget}
                onActivate={(id) => activateMutation.mutate(id)}
              />

              <div className="mt-4 space-y-3 md:hidden">
                {filteredPatients.map((patient) => (
                  <PatientMobileCard
                    key={patient.id}
                    patient={patient}
                    onDeactivate={setDeactivateTarget}
                    onActivate={(id) => activateMutation.mutate(id)}
                  />
                ))}
              </div>
            </>
          )}

          <div className="mt-6 flex flex-wrap items-center justify-between gap-4 border-t border-slate-100 pt-4">
            <span className="text-sm text-slate-600">
              {ageGroup
                ? `${filteredPatients.length} na página · ${data?.count ?? 0} total`
                : `Total: ${data?.count ?? 0}`}
            </span>
            <Pagination page={page} totalPages={totalPages} onPageChange={setPage} />
          </div>
        </div>
      </div>

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

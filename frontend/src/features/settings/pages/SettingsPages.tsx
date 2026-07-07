import { useQuery } from "@tanstack/react-query";

import { Card, ErrorState, LoadingState } from "@/design-system";
import { ClinicForm } from "@/features/settings/components/ClinicForm";
import { FeatureFlagTable } from "@/features/settings/components/FeatureFlagTable";
import { SettingsSubNav } from "@/features/settings/components/SettingsSubNav";
import { settingsService } from "@/services/settings/settings.service";

export function SettingsDashboardPage() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["settings-system"],
    queryFn: settingsService.getSystemDashboard,
  });

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Configurações</h2>
        <p className="mt-1 text-slate-600">Administração e configuração do sistema.</p>
      </div>
      <SettingsSubNav />
      {isLoading ? (
        <LoadingState message="A carregar..." />
      ) : isError || !data ? (
        <ErrorState message="Não foi possível carregar o painel." />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <Card title="Versão">
            <p className="text-xl font-bold">{(data.monitorizacao as { versao?: string }).versao}</p>
          </Card>
          <Card title="Health">
            <p className="text-xl font-bold">{(data.monitorizacao as { health?: string }).health}</p>
          </Card>
          <Card title="Utilizadores">
            <p className="text-xl font-bold">
              {(data.monitorizacao as { utilizadores?: { total?: number } }).utilizadores?.total ?? 0}
            </p>
          </Card>
        </div>
      )}
    </div>
  );
}

export function ClinicSettingsPage() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Dados da Clínica</h2>
      <SettingsSubNav />
      <Card title="Perfil da clínica">
        <ClinicForm />
      </Card>
    </div>
  );
}

export function DepartmentsPage() {
  const { data } = useQuery({ queryKey: ["departments"], queryFn: settingsService.listDepartments });
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Departamentos</h2>
      <SettingsSubNav />
      <Card title="Lista">
        <ul className="text-sm">
          {data?.results.map((d) => (
            <li key={d.id}>{d.nome}</li>
          ))}
        </ul>
      </Card>
    </div>
  );
}

export function SpecialtiesPage() {
  const { data } = useQuery({ queryKey: ["specialties"], queryFn: settingsService.listSpecialties });
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Especialidades</h2>
      <SettingsSubNav />
      <Card title="Lista">
        <ul className="text-sm">
          {data?.results.map((s) => (
            <li key={s.id}>{s.nome}</li>
          ))}
        </ul>
      </Card>
    </div>
  );
}

export function SecuritySettingsPage() {
  const { data } = useQuery({ queryKey: ["security"], queryFn: settingsService.getSecurity });
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Segurança</h2>
      <SettingsSubNav />
      <Card title="Políticas">
        <pre className="text-xs">{JSON.stringify(data, null, 2)}</pre>
      </Card>
    </div>
  );
}

export function FeatureFlagsPage() {
  const { data, refetch } = useQuery({ queryKey: ["feature-flags"], queryFn: settingsService.getFeatureFlags });
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Feature Flags</h2>
      <SettingsSubNav />
      {data && (
        <FeatureFlagTable
          flags={data}
          onToggle={(codigo, activo) => {
            void settingsService.updateFeatureFlag(codigo, activo).then(() => void refetch());
          }}
        />
      )}
    </div>
  );
}

export function SystemStatusPage() {
  const { data } = useQuery({ queryKey: ["settings-system"], queryFn: settingsService.getSystemDashboard });
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Estado do Sistema</h2>
      <SettingsSubNav />
      <Card title="Monitorização">
        <pre className="overflow-auto text-xs">{JSON.stringify(data?.monitorizacao, null, 2)}</pre>
      </Card>
    </div>
  );
}

function PlaceholderPage({ title }: { title: string }) {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">{title}</h2>
      <SettingsSubNav />
      <Card title={title}>
        <p className="text-sm text-slate-600">Configuração disponível via API.</p>
      </Card>
    </div>
  );
}

export const RoomsPage = () => <PlaceholderPage title="Consultórios / Salas" />;
export const WorkingHoursPage = () => <PlaceholderPage title="Horários" />;
export const ConsultationTypesPage = () => <PlaceholderPage title="Tipos de Consulta" />;
export const LaboratorySettingsPage = () => <PlaceholderPage title="Laboratório" />;
export const BillingSettingsPage = () => <PlaceholderPage title="Faturação" />;
export const EmailSettingsPage = () => <PlaceholderPage title="E-mail" />;
export const BackupPage = () => <PlaceholderPage title="Backups" />;

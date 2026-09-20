import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { Button, Card, ErrorState, LoadingState, Table, useToast } from "@/design-system";
import { SettingsSubNav } from "@/features/settings/components/SettingsSubNav";
import { billingService } from "@/services/billing/billing.service";
import { settingsService } from "@/services/settings/settings.service";
import type { MedicoPerfil } from "@/types/settings";
import { getApiErrorMessage } from "@/utils/api-error";

export function MedicoProfilesPage() {
  const { showToast } = useToast();
  const queryClient = useQueryClient();
  const [editingId, setEditingId] = useState<number | null>(null);

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["medico-perfis"],
    queryFn: settingsService.listMedicoPerfis,
  });

  const { data: specialties } = useQuery({
    queryKey: ["specialties"],
    queryFn: settingsService.listSpecialties,
  });
  const { data: departments } = useQuery({
    queryKey: ["departments"],
    queryFn: settingsService.listDepartments,
  });
  const { data: consultas } = useQuery({
    queryKey: ["billing-services-consulta"],
    queryFn: () => billingService.listServices({ categoria: "CONSULTA", page_size: 200 }),
  });

  const saveMutation = useMutation({
    mutationFn: ({ id, payload }: { id?: number; payload: object }) =>
      id ? settingsService.updateMedicoPerfil(id, payload) : settingsService.createMedicoPerfil(payload),
    onSuccess: () => {
      showToast("Perfil médico guardado.", "success");
      setEditingId(null);
      void queryClient.invalidateQueries({ queryKey: ["medico-perfis"] });
    },
    onError: (e) => showToast(getApiErrorMessage(e), "error"),
  });

  if (isLoading) return <LoadingState />;
  if (isError || !data) {
    return <ErrorState message="Erro ao carregar médicos." onRetry={() => void refetch()} />;
  }

  const editing = data.results.find((m) => m.id === editingId);

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-slate-900">Configuração de médicos</h2>
      <SettingsSubNav />
      <Card title="Lista de médicos">
        <Table<MedicoPerfil>
          data={data.results}
          getRowKey={(r) => r.id}
          columns={[
            { key: "utilizador_nome", header: "Nome" },
            { key: "especialidade_nome", header: "Especialidade", render: (r) => r.especialidade_nome ?? "—" },
            { key: "departamento_nome", header: "Departamento", render: (r) => r.departamento_nome ?? "—" },
            {
              key: "horario",
              header: "Horário",
              render: (r) =>
                r.horario_configurado ? "Configurado" : (
                  <span className="text-amber-700">Sem horário</span>
                ),
            },
            {
              key: "servico",
              header: "Consulta",
              render: (r) =>
                r.servico_consulta_nome
                  ? `${r.servico_consulta_nome} (${r.servico_consulta_preco ?? "—"} FCFA)`
                  : "—",
            },
            {
              key: "activo",
              header: "Estado",
              render: (r) => {
                const completo =
                  r.especialidade &&
                  r.departamento &&
                  r.servico_consulta &&
                  r.horario_configurado &&
                  r.activo &&
                  r.disponivel_marcacao;
                if (!completo) {
                  return <span className="text-amber-800">Pendente de configuração</span>;
                }
                return r.activo && r.disponivel_marcacao ? "Activo" : "Indisponível";
              },
            },
            {
              key: "actions",
              header: "Acções",
              render: (r) => (
                <Button variant="ghost" size="sm" type="button" onClick={() => setEditingId(r.id)}>
                  Configurar
                </Button>
              ),
            },
          ]}
        />
      </Card>

      {editing ? (
        <Card title={`Configurar: ${editing.utilizador_nome}`}>
          <form
            className="grid gap-4 sm:grid-cols-2"
            onSubmit={(e) => {
              e.preventDefault();
              const form = new FormData(e.currentTarget);
              const dias = form.getAll("dias").map(String);
              saveMutation.mutate({
                id: editing.id,
                payload: {
                  especialidade: Number(form.get("especialidade")) || null,
                  departamento: Number(form.get("departamento")) || null,
                  numero_profissional: String(form.get("numero_profissional") || ""),
                  duracao_consulta_minutos: Number(form.get("duracao_consulta_minutos") || 30),
                  servico_consulta: Number(form.get("servico_consulta")) || null,
                  activo: form.get("activo") === "on",
                  disponivel_marcacao: form.get("disponivel_marcacao") === "on",
                  dias_trabalho: dias,
                  horario_atendimento: {
                    inicio: String(form.get("hora_inicio") || "08:00"),
                    fim: String(form.get("hora_fim") || "17:00"),
                  },
                },
              });
            }}
          >
            <label className="text-sm">
              Especialidade
              <select
                name="especialidade"
                className="mt-1 w-full rounded border px-3 py-2"
                defaultValue={editing.especialidade ?? ""}
              >
                <option value="">—</option>
                {specialties?.results.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.nome}
                  </option>
                ))}
              </select>
            </label>
            <label className="text-sm">
              Departamento
              <select
                name="departamento"
                className="mt-1 w-full rounded border px-3 py-2"
                defaultValue={editing.departamento ?? ""}
              >
                <option value="">—</option>
                {departments?.results.map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.nome}
                  </option>
                ))}
              </select>
            </label>
            <input
              name="numero_profissional"
              placeholder="N.º profissional"
              className="rounded border px-3 py-2 text-sm"
              defaultValue={editing.numero_profissional}
            />
            <input
              name="duracao_consulta_minutos"
              type="number"
              min={5}
              placeholder="Duração consulta (min)"
              className="rounded border px-3 py-2 text-sm"
              defaultValue={editing.duracao_consulta_minutos}
            />
            <label className="text-sm sm:col-span-2">
              Serviço de consulta (preço vem do serviço)
              <select
                name="servico_consulta"
                className="mt-1 w-full rounded border px-3 py-2"
                defaultValue={editing.servico_consulta ?? ""}
              >
                <option value="">—</option>
                {consultas?.results.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.codigo}: {s.nome} ({s.preco} FCFA)
                  </option>
                ))}
              </select>
            </label>
            <fieldset className="sm:col-span-2">
              <legend className="text-sm font-medium">Dias de trabalho</legend>
              <div className="mt-2 flex flex-wrap gap-3 text-sm">
                {["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"].map((dia) => (
                  <label key={dia} className="flex items-center gap-1">
                    <input
                      type="checkbox"
                      name="dias"
                      value={dia}
                      defaultChecked={editing.dias_trabalho?.includes(dia)}
                    />
                    {dia}
                  </label>
                ))}
              </div>
            </fieldset>
            <input
              name="hora_inicio"
              type="time"
              className="rounded border px-3 py-2 text-sm"
              defaultValue={(editing.horario_atendimento as { inicio?: string })?.inicio ?? "08:00"}
            />
            <input
              name="hora_fim"
              type="time"
              className="rounded border px-3 py-2 text-sm"
              defaultValue={(editing.horario_atendimento as { fim?: string })?.fim ?? "17:00"}
            />
            <label className="flex items-center gap-2 text-sm">
              <input type="checkbox" name="activo" defaultChecked={editing.activo} />
              Activo
            </label>
            <label className="flex items-center gap-2 text-sm">
              <input type="checkbox" name="disponivel_marcacao" defaultChecked={editing.disponivel_marcacao} />
              Aceita marcações
            </label>
            <div className="flex gap-2 sm:col-span-2">
              <Button type="submit" variant="primary" disabled={saveMutation.isPending}>
                Guardar
              </Button>
              <Button type="button" variant="ghost" onClick={() => setEditingId(null)}>
                Cancelar
              </Button>
            </div>
          </form>
        </Card>
      ) : null}
    </div>
  );
}

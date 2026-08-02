import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Link } from "react-router-dom";

import { KpiCard } from "@/components/ui/KpiCard";
import { Avatar, Badge, Button, Card, Input, Modal, Skeleton, Table } from "@/design-system";
import { ASSIGNABLE_ROLES, ROLE_LABELS } from "@/constants/roles";
import { usersService } from "@/services/users";
import type { ManagedUser } from "@/types/user-management";
import { formatDisplayDateTime } from "@/utils/date";

export function UsersListPage() {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const [role, setRole] = useState("");
  const [status, setStatus] = useState<"" | "active" | "inactive">("");
  const [page, setPage] = useState(1);
  const [historyUser, setHistoryUser] = useState<ManagedUser | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ["users", page, search, role, status],
    queryFn: () =>
      usersService.list({
        page,
        search: search || undefined,
        role: role || undefined,
        is_active: status === "" ? undefined : status === "active",
      }),
  });

  const deactivateMutation = useMutation({
    mutationFn: usersService.deactivate,
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ["users"] }),
  });

  const activateMutation = useMutation({
    mutationFn: usersService.activate,
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ["users"] }),
  });

  const users = data?.results ?? [];
  const activeCount = users.filter((u) => u.is_active).length;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">Gestão de Utilizadores</h1>
          <p className="mt-1 text-slate-500">Criar, editar e administrar contas da clínica.</p>
        </div>
        <Link to="/admin/users/new">
          <Button size="lg">+ Criar Utilizador</Button>
        </Link>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <KpiCard label="Total" value={data?.count ?? 0} badge={{ text: "Contas registadas", variant: "default" }} />
        <KpiCard label="Activos (página)" value={activeCount} badge={{ text: "Nesta página", variant: "success" }} />
        <KpiCard label="Perfis" value={ASSIGNABLE_ROLES.length} badge={{ text: "Atribuíveis", variant: "info" }} />
      </div>

      <Card>
        <div className="mb-4 grid gap-4 md:grid-cols-4">
          <Input
            label="Pesquisar"
            placeholder="Nome, e-mail ou telefone"
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
          />
          <div>
            <label className="mb-1.5 block text-sm font-medium text-slate-700">Perfil</label>
            <select
              className="w-full rounded-xl border border-slate-200 px-3 py-2.5 text-sm focus:border-primary-300 focus:outline-none focus:ring-2 focus:ring-primary-100"
              value={role}
              onChange={(e) => {
                setRole(e.target.value);
                setPage(1);
              }}
            >
              <option value="">Todos</option>
              {ASSIGNABLE_ROLES.map((value) => (
                <option key={value} value={value}>
                  {ROLE_LABELS[value]}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="mb-1.5 block text-sm font-medium text-slate-700">Estado</label>
            <select
              className="w-full rounded-xl border border-slate-200 px-3 py-2.5 text-sm focus:border-primary-300 focus:outline-none focus:ring-2 focus:ring-primary-100"
              value={status}
              onChange={(e) => {
                setStatus(e.target.value as "" | "active" | "inactive");
                setPage(1);
              }}
            >
              <option value="">Todos</option>
              <option value="active">Activos</option>
              <option value="inactive">Inactivos</option>
            </select>
          </div>
        </div>

        {isLoading ? (
          <div className="space-y-3">
            {Array.from({ length: 5 }).map((_, i) => (
              <Skeleton key={i} className="h-14 w-full rounded-xl" />
            ))}
          </div>
        ) : (
          <Table<ManagedUser>
            data={users}
            getRowKey={(row) => row.id}
            emptyMessage="Nenhum utilizador encontrado."
            columns={[
              {
                key: "user",
                header: "Utilizador",
                render: (row) => (
                  <div className="flex items-center gap-3">
                    <Avatar name={row.full_name} src={row.photo_url ?? undefined} size="md" />
                    <div>
                      <p className="font-medium text-slate-900">{row.full_name}</p>
                      <p className="text-xs text-slate-500">{row.email}</p>
                    </div>
                  </div>
                ),
              },
              {
                key: "role",
                header: "Perfil",
                render: (row) => (
                  <Badge variant="info">{ROLE_LABELS[row.role] ?? row.role}</Badge>
                ),
              },
              {
                key: "phone",
                header: "Telefone",
                render: (row) => row.phone || "—",
              },
              {
                key: "is_active",
                header: "Estado",
                render: (row) => (
                  <Badge variant={row.is_active ? "success" : "danger"}>
                    {row.is_active ? "Activo" : "Inactivo"}
                  </Badge>
                ),
              },
              {
                key: "last_login",
                header: "Último acesso",
                render: (row) => (row.last_login ? formatDisplayDateTime(row.last_login) : "Nunca"),
              },
              {
                key: "actions",
                header: "Acções",
                render: (row) => (
                  <div className="flex flex-wrap gap-2">
                    <Link to={`/admin/users/${row.id}/edit`}>
                      <Button size="sm" variant="secondary">
                        Editar
                      </Button>
                    </Link>
                    <Button size="sm" variant="ghost" onClick={() => setHistoryUser(row)}>
                      Histórico
                    </Button>
                    {row.is_active ? (
                      <Button size="sm" variant="ghost" onClick={() => deactivateMutation.mutate(row.id)}>
                        Desactivar
                      </Button>
                    ) : (
                      <Button size="sm" variant="ghost" onClick={() => activateMutation.mutate(row.id)}>
                        Activar
                      </Button>
                    )}
                  </div>
                ),
              },
            ]}
          />
        )}

        <div className="mt-4 flex items-center justify-between text-sm text-slate-600">
          <span>Total: {data?.count ?? 0}</span>
          <div className="flex gap-2">
            <Button size="sm" variant="secondary" disabled={!data?.previous} onClick={() => setPage((p) => Math.max(1, p - 1))}>
              Anterior
            </Button>
            <Button size="sm" variant="secondary" disabled={!data?.next} onClick={() => setPage((p) => p + 1)}>
              Seguinte
            </Button>
          </div>
        </div>
      </Card>

      <Modal
        open={Boolean(historyUser)}
        onClose={() => setHistoryUser(null)}
        title="Histórico de acesso"
      >
        {historyUser && (
          <dl className="space-y-3 text-sm">
            <div>
              <dt className="text-slate-500">Utilizador</dt>
              <dd className="font-medium text-slate-900">{historyUser.full_name}</dd>
            </div>
            <div>
              <dt className="text-slate-500">Último login</dt>
              <dd>{historyUser.last_login ? formatDisplayDateTime(historyUser.last_login) : "Nunca"}</dd>
            </div>
            <div>
              <dt className="text-slate-500">Última actividade</dt>
              <dd>{historyUser.last_activity ? formatDisplayDateTime(historyUser.last_activity) : "—"}</dd>
            </div>
            <div>
              <dt className="text-slate-500">Conta criada</dt>
              <dd>{formatDisplayDateTime(historyUser.date_joined)}</dd>
            </div>
            <p className="rounded-lg bg-slate-50 p-3 text-xs text-slate-500">
              Para repor a palavra-passe, crie uma nova conta ou contacte o administrador do sistema. A edição de palavra-passe está disponível apenas na criação de utilizador.
            </p>
          </dl>
        )}
      </Modal>
    </div>
  );
}

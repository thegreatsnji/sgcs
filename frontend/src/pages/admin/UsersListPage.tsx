import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Link } from "react-router-dom";

import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { Spinner } from "@/components/ui/Spinner";
import { Table } from "@/components/tables/Table";
import { ROLE_LABELS } from "@/constants/roles";
import { usersService } from "@/services/users";
import type { ManagedUser } from "@/types/user-management";

export function UsersListPage() {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const [role, setRole] = useState("");
  const [page, setPage] = useState(1);

  const { data, isLoading } = useQuery({
    queryKey: ["users", page, search, role],
    queryFn: () =>
      usersService.list({
        page,
        search: search || undefined,
        role: role || undefined,
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

  const deleteMutation = useMutation({
    mutationFn: usersService.remove,
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ["users"] }),
  });

  if (isLoading) {
    return <Spinner label="A carregar utilizadores..." />;
  }

  const users = data?.results ?? [];

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">Utilizadores</h2>
          <p className="text-sm text-slate-500">Gestão completa de contas do sistema</p>
        </div>
        <Link to="/admin/users/new">
          <Button>Criar Utilizador</Button>
        </Link>
      </div>

      <Card>
        <div className="mb-4 grid gap-4 md:grid-cols-3">
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
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
              value={role}
              onChange={(e) => {
                setRole(e.target.value);
                setPage(1);
              }}
            >
              <option value="">Todos</option>
              {Object.entries(ROLE_LABELS).map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </div>
        </div>

        <Table<ManagedUser>
          columns={[
            { key: "full_name", header: "Nome" },
            { key: "email", header: "E-mail" },
            { key: "phone", header: "Telefone" },
            {
              key: "role",
              header: "Perfil",
              render: (row) => ROLE_LABELS[row.role] ?? row.role,
            },
            {
              key: "is_active",
              header: "Estado",
              render: (row) => (
                <Badge variant={row.is_active ? "success" : "danger"}>
                  {row.is_active ? "Ativo" : "Inativo"}
                </Badge>
              ),
            },
            {
              key: "actions",
              header: "Ações",
              render: (row) => (
                <div className="flex flex-wrap gap-2">
                  <Link to={`/admin/users/${row.id}/edit`}>
                    <Button size="sm" variant="secondary">
                      Editar
                    </Button>
                  </Link>
                  {row.is_active ? (
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => deactivateMutation.mutate(row.id)}
                    >
                      Desativar
                    </Button>
                  ) : (
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => activateMutation.mutate(row.id)}
                    >
                      Ativar
                    </Button>
                  )}
                  <Button
                    size="sm"
                    variant="danger"
                    onClick={() => deleteMutation.mutate(row.id)}
                  >
                    Eliminar
                  </Button>
                </div>
              ),
            },
          ]}
          data={users}
        />

        <div className="mt-4 flex items-center justify-between text-sm text-slate-600">
          <span>Total: {data?.count ?? 0}</span>
          <div className="flex gap-2">
            <Button
              size="sm"
              variant="secondary"
              disabled={!data?.previous}
              onClick={() => setPage((p) => Math.max(1, p - 1))}
            >
              Anterior
            </Button>
            <Button
              size="sm"
              variant="secondary"
              disabled={!data?.next}
              onClick={() => setPage((p) => p + 1)}
            >
              Seguinte
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
}

import { useQuery } from "@tanstack/react-query";

import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { Spinner } from "@/components/ui/Spinner";
import { permissionsService, rolesService } from "@/services/users";
import type { Permission, Role } from "@/types/user-management";

export function PermissionsPage() {
  const { data: rolesData, isLoading: rolesLoading } = useQuery({
    queryKey: ["roles"],
    queryFn: rolesService.list,
  });

  const { data: permissionsData, isLoading: permissionsLoading } = useQuery({
    queryKey: ["permissions"],
    queryFn: permissionsService.list,
  });

  if (rolesLoading || permissionsLoading) {
    return <Spinner label="A carregar permissões..." />;
  }

  const roles = rolesData?.results ?? [];
  const permissions = permissionsData?.results ?? [];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Perfis e Permissões</h2>
        <p className="text-sm text-slate-500">Sistema RBAC do SGCS</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {roles.map((role: Role) => (
          <Card key={role.id} title={role.name}>
            <p className="mb-3 text-sm text-slate-500">{role.description || "Sem descrição"}</p>
            <div className="mb-2 flex gap-2">
              {role.is_system && <Badge variant="info">Sistema</Badge>}
              <Badge>{role.permission_count} permissões</Badge>
            </div>
            <div className="flex flex-wrap gap-1">
              {role.permissions.slice(0, 8).map((perm: Permission) => (
                <Badge key={perm.id} variant="default">
                  {perm.codename}
                </Badge>
              ))}
            </div>
          </Card>
        ))}
      </div>

      <Card title="Todas as Permissões">
        <div className="grid gap-2 md:grid-cols-2 lg:grid-cols-3">
          {permissions.map((permission: Permission) => (
            <div key={permission.id} className="rounded-lg border border-slate-200 p-3 text-sm">
              <p className="font-medium text-slate-800">{permission.name}</p>
              <p className="text-slate-500">{permission.codename}</p>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}

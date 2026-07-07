import { useQuery } from "@tanstack/react-query";

import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { Spinner } from "@/components/ui/Spinner";
import { groupsService } from "@/services/users";
import type { Permission, UserGroup } from "@/types/user-management";

export function GroupsPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["groups"],
    queryFn: groupsService.list,
  });

  if (isLoading) {
    return <Spinner label="A carregar grupos..." />;
  }

  const groups = data?.results ?? [];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Grupos</h2>
        <p className="text-sm text-slate-500">Grupos personalizados com permissões específicas</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {groups.map((group: UserGroup) => (
          <Card key={group.id} title={group.name}>
            <p className="mb-3 text-sm text-slate-600">{group.description}</p>
            <div className="mb-3 flex gap-2">
              <Badge variant={group.is_active ? "success" : "danger"}>
                {group.is_active ? "Ativo" : "Inativo"}
              </Badge>
              <Badge>{group.members_count} membros</Badge>
              <Badge>{group.permissions.length} permissões</Badge>
            </div>
            <div className="flex flex-wrap gap-1">
              {group.permissions.slice(0, 6).map((perm: Permission) => (
                <Badge key={perm.id}>{perm.codename}</Badge>
              ))}
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}

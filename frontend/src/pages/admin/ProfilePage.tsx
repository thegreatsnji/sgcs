import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";

import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { Spinner } from "@/components/ui/Spinner";
import { Table } from "@/components/tables/Table";
import { ROLE_LABELS } from "@/constants/roles";
import { passwordFormSchema, profileFormSchema } from "@/schemas/userSchema";
import { usersService, type AccessHistoryItem, type UserSession } from "@/services/users";

export function ProfilePage() {
  const queryClient = useQueryClient();

  const { data: profile, isLoading } = useQuery({
    queryKey: ["profile"],
    queryFn: usersService.getProfile,
  });

  const { data: sessions } = useQuery({
    queryKey: ["profile-sessions"],
    queryFn: usersService.getSessions,
  });

  const { data: accessHistory } = useQuery({
    queryKey: ["profile-access-history"],
    queryFn: usersService.getAccessHistory,
  });

  const profileForm = useForm({
    resolver: zodResolver(profileFormSchema),
    values: profile
      ? {
          first_name: profile.first_name,
          last_name: profile.last_name,
          phone: profile.phone ?? "",
          gender: (profile.gender as "M" | "F" | "O" | "") ?? "",
          birth_date: profile.birth_date ?? "",
          position: profile.position ?? "",
        }
      : undefined,
  });

  const passwordForm = useForm({
    resolver: zodResolver(passwordFormSchema),
    defaultValues: {
      old_password: "",
      new_password: "",
      new_password_confirm: "",
    },
  });

  const updateProfile = useMutation({
    mutationFn: usersService.updateProfile,
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ["profile"] }),
  });

  const changePassword = useMutation({
    mutationFn: usersService.changePassword,
    onSuccess: () => passwordForm.reset(),
  });

  if (isLoading || !profile) {
    return <Spinner label="A carregar perfil..." />;
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Meu Perfil</h2>
        <p className="text-sm text-slate-500">{profile.email}</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card title="Dados Pessoais">
          <form
            onSubmit={profileForm.handleSubmit((data) => updateProfile.mutate(data))}
            className="space-y-4"
          >
            <Input label="Nome" {...profileForm.register("first_name")} />
            <Input label="Apelido" {...profileForm.register("last_name")} />
            <Input label="Telefone" {...profileForm.register("phone")} />
            <Input label="Cargo" {...profileForm.register("position")} />
            <Input label="Data de Nascimento" type="date" {...profileForm.register("birth_date")} />
            <Button type="submit" isLoading={updateProfile.isPending}>
              Guardar Perfil
            </Button>
          </form>
        </Card>

        <Card title="Informações da Conta">
          <div className="space-y-3 text-sm">
            <p><span className="font-medium">Perfil:</span> {ROLE_LABELS[profile.role]}</p>
            <p><span className="font-medium">Estado:</span> <Badge variant={profile.is_active ? "success" : "danger"}>{profile.is_active ? "Ativo" : "Inativo"}</Badge></p>
            <p><span className="font-medium">Criado em:</span> {profile.date_joined}</p>
            <p><span className="font-medium">Último login:</span> {profile.last_login ?? "—"}</p>
            <p><span className="font-medium">Última atividade:</span> {profile.last_activity ?? "—"}</p>
            <div>
              <p className="mb-2 font-medium">Permissões ({profile.permissions.length})</p>
              <div className="flex flex-wrap gap-1">
                {profile.permissions.slice(0, 12).map((perm: string) => (
                  <Badge key={perm}>{perm}</Badge>
                ))}
              </div>
            </div>
          </div>
        </Card>
      </div>

      <Card title="Alterar Palavra-passe">
        <form
          onSubmit={passwordForm.handleSubmit((data) => changePassword.mutate(data))}
          className="grid gap-4 md:grid-cols-3"
        >
          <Input label="Atual" type="password" {...passwordForm.register("old_password")} />
          <Input label="Nova" type="password" {...passwordForm.register("new_password")} />
          <Input label="Confirmar" type="password" {...passwordForm.register("new_password_confirm")} />
          <div className="md:col-span-3">
            <Button type="submit" isLoading={changePassword.isPending}>
              Alterar Palavra-passe
            </Button>
          </div>
        </form>
      </Card>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card title="Sessões Ativas">
          <Table
            columns={[
              { key: "ip_address", header: "IP" },
              { key: "user_agent", header: "Dispositivo" },
              { key: "last_activity", header: "Última atividade" },
            ]}
            data={(sessions?.results ?? []).filter((s: UserSession) => s.is_active)}
            emptyMessage="Sem sessões ativas."
          />
        </Card>

        <Card title="Últimos Acessos">
          <Table
            columns={[
              { key: "action", header: "Ação" },
              { key: "description", header: "Descrição" },
              { key: "created_at", header: "Data" },
            ]}
            data={accessHistory?.results ?? ([] as AccessHistoryItem[])}
          />
        </Card>
      </div>
    </div>
  );
}

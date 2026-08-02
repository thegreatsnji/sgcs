import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { useNavigate, useParams } from "react-router-dom";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { Spinner } from "@/components/ui/Spinner";
import { ASSIGNABLE_ROLES, ROLE_LABELS } from "@/constants/roles";
import { userFormSchema, type UserFormData } from "@/schemas/userSchema";
import { usersService } from "@/services/users";

export function UserFormPage() {
  const { id } = useParams();
  const isEdit = Boolean(id);
  const navigate = useNavigate();

  const { data: user, isLoading } = useQuery({
    queryKey: ["user", id],
    queryFn: () => usersService.get(Number(id)),
    enabled: isEdit,
  });

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<UserFormData>({
    resolver: zodResolver(userFormSchema),
    values: user
      ? {
          email: user.email,
          first_name: user.first_name,
          last_name: user.last_name,
          phone: user.phone ?? "",
          gender: (user.gender as "M" | "F" | "O" | "") ?? "",
          birth_date: user.birth_date ?? "",
          position: user.position ?? "",
          role: user.role,
          password: "",
          password_confirm: "",
        }
      : undefined,
    defaultValues: {
      email: "",
      first_name: "",
      last_name: "",
      phone: "",
      gender: "",
      birth_date: "",
      position: "",
      role: "RECECIONISTA",
      password: "",
      password_confirm: "",
    },
  });

  const mutation = useMutation({
    mutationFn: async (formData: UserFormData) => {
      const payload = {
        ...formData,
        gender: formData.gender || undefined,
        birth_date: formData.birth_date || null,
      };
      if (isEdit) {
        const { password, password_confirm, email, ...updatePayload } = payload;
        void password;
        void password_confirm;
        void email;
        return usersService.update(Number(id), updatePayload);
      }
      return usersService.create(payload);
    },
    onSuccess: () => navigate("/admin/users"),
  });

  if (isEdit && isLoading) {
    return <Spinner label="A carregar utilizador..." />;
  }

  return (
    <Card title={isEdit ? "Editar Utilizador" : "Criar Utilizador"}>
      <form onSubmit={handleSubmit((data) => mutation.mutate(data))} className="grid gap-4 md:grid-cols-2">
        <Input label="E-mail" type="email" disabled={isEdit} error={errors.email?.message} {...register("email")} />
        <Input label="Telefone" error={errors.phone?.message} {...register("phone")} />
        <Input label="Nome" error={errors.first_name?.message} {...register("first_name")} />
        <Input label="Apelido" error={errors.last_name?.message} {...register("last_name")} />
        <Input label="Cargo" error={errors.position?.message} {...register("position")} />
        <Input label="Data de Nascimento" type="date" error={errors.birth_date?.message} {...register("birth_date")} />

        <div>
          <label className="mb-1.5 block text-sm font-medium text-slate-700">Sexo</label>
          <select className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm" {...register("gender")}>
            <option value="">Selecionar</option>
            <option value="M">Masculino</option>
            <option value="F">Feminino</option>
            <option value="O">Outro</option>
          </select>
        </div>

        <div>
          <label className="mb-1.5 block text-sm font-medium text-slate-700">Perfil</label>
          <select className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm" {...register("role")}>
            {ASSIGNABLE_ROLES.map((value) => (
              <option key={value} value={value}>
                {ROLE_LABELS[value]}
              </option>
            ))}
          </select>
        </div>

        {!isEdit && (
          <>
            <Input
              label="Palavra-passe"
              type="password"
              error={errors.password?.message}
              {...register("password")}
            />
            <Input
              label="Confirmar Palavra-passe"
              type="password"
              error={errors.password_confirm?.message}
              {...register("password_confirm")}
            />
          </>
        )}

        <div className="md:col-span-2 flex gap-3">
          <Button type="submit" isLoading={isSubmitting || mutation.isPending}>
            Guardar
          </Button>
          <Button type="button" variant="secondary" onClick={() => navigate("/admin/users")}>
            Cancelar
          </Button>
        </div>
      </form>
    </Card>
  );
}

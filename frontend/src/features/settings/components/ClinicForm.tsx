import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { Button } from "@/design-system";
import { settingsService } from "@/services/settings/settings.service";

export function ClinicForm() {
  const queryClient = useQueryClient();
  const { data } = useQuery({ queryKey: ["settings-clinic"], queryFn: settingsService.getClinic });
  const mutation = useMutation({
    mutationFn: settingsService.updateClinic,
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ["settings-clinic"] }),
  });

  if (!data) return null;

  return (
    <form
      className="grid gap-4 sm:grid-cols-2"
      onSubmit={(e) => {
        e.preventDefault();
        const form = new FormData(e.currentTarget);
        mutation.mutate(Object.fromEntries(form.entries()) as never);
      }}
    >
      <input name="nome" defaultValue={data.nome} placeholder="Nome" className="rounded border px-3 py-2 text-sm" />
      <input name="nif" defaultValue={data.nif} placeholder="NIF" className="rounded border px-3 py-2 text-sm" />
      <input name="cidade" defaultValue={data.cidade} placeholder="Cidade" className="rounded border px-3 py-2 text-sm" />
      <input name="telefone" defaultValue={data.telefone} placeholder="Telefone" className="rounded border px-3 py-2 text-sm" />
      <input name="email" defaultValue={data.email} placeholder="E-mail" className="rounded border px-3 py-2 text-sm sm:col-span-2" />
      <Button type="submit" variant="primary" disabled={mutation.isPending}>Guardar</Button>
    </form>
  );
}

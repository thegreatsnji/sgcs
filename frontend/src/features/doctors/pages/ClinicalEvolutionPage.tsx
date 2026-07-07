import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { Card, LoadingState } from "@/design-system";
import { DoctorSubNav } from "@/features/doctors/components/DoctorSubNav";
import { TimelineClinica } from "@/features/doctors/components/TimelineClinica";
import { doctorsService } from "@/services/doctors/doctors.service";

export function ClinicalEvolutionPage() {
  const queryClient = useQueryClient();
  const [consultaId, setConsultaId] = useState("");
  const [tipo, setTipo] = useState("MELHORIA");
  const [observacoes, setObservacoes] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["doctor-evolutions"],
    queryFn: doctorsService.listEvolutions,
  });

  const mutation = useMutation({
    mutationFn: doctorsService.createEvolution,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["doctor-evolutions"] });
      setObservacoes("");
    },
  });

  const eventos =
    data?.results.map((e) => ({
      id: e.id,
      tipo: e.tipo,
      data: e.created_at,
      titulo: `Evolução #${e.id}`,
      descricao: e.observacoes,
    })) ?? [];

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Evolução clínica</h2>
      <DoctorSubNav />
      <Card title="Registar evolução">
        <form
          className="grid gap-3 sm:grid-cols-2"
          onSubmit={(e) => {
            e.preventDefault();
            mutation.mutate({
              consulta_id: Number(consultaId),
              tipo,
              observacoes,
            });
          }}
        >
          <input
            className="rounded border border-slate-300 px-3 py-2 text-sm"
            placeholder="ID da consulta"
            value={consultaId}
            onChange={(e) => setConsultaId(e.target.value)}
            required
          />
          <select
            className="rounded border border-slate-300 px-3 py-2 text-sm"
            value={tipo}
            onChange={(e) => setTipo(e.target.value)}
          >
            <option value="MELHORIA">Melhoria</option>
            <option value="AGRAVAMENTO">Agravamento</option>
            <option value="ESTAVEL">Estável</option>
          </select>
          <textarea
            className="sm:col-span-2 rounded border border-slate-300 px-3 py-2 text-sm"
            rows={3}
            placeholder="Observações e resposta ao tratamento"
            value={observacoes}
            onChange={(e) => setObservacoes(e.target.value)}
            required
          />
          <button
            type="submit"
            className="sm:col-span-2 rounded bg-primary-600 px-4 py-2 text-sm text-white hover:bg-primary-700 disabled:opacity-50"
            disabled={mutation.isPending}
          >
            {mutation.isPending ? "A registar..." : "Registar evolução"}
          </button>
        </form>
      </Card>
      <Card title="Linha temporal">
        {isLoading ? <LoadingState /> : <TimelineClinica eventos={eventos} />}
      </Card>
    </div>
  );
}

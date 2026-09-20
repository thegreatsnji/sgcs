import { useState } from "react";

import { Button } from "@/design-system";
import type { MedicamentoPrescrito } from "@/types/doctors";

interface PrescricaoFormProps {
  consultaId?: number;
  onSubmit: (values: {
    consulta_id: number;
    observacoes?: string;
    medicamentos: MedicamentoPrescrito[];
  }) => void;
  isPending?: boolean;
}

const medicamentoVazio: MedicamentoPrescrito = {
  nome: "",
  dosagem: "",
  frequencia: "",
  duracao: "",
  posologia: "",
};

export function PrescricaoForm({ consultaId: consultaIdProp, onSubmit, isPending }: PrescricaoFormProps) {
  const [consultaId, setConsultaId] = useState(
    consultaIdProp != null ? String(consultaIdProp) : "",
  );
  const [observacoes, setObservacoes] = useState("");
  const [medicamentos, setMedicamentos] = useState<MedicamentoPrescrito[]>([{ ...medicamentoVazio }]);

  const updateMed = (index: number, field: keyof MedicamentoPrescrito, value: string) => {
    setMedicamentos((prev) => prev.map((m, i) => (i === index ? { ...m, [field]: value } : m)));
  };

  return (
    <form
      className="space-y-4"
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit({
          consulta_id: Number(consultaId),
          observacoes,
          medicamentos: medicamentos.filter((m) => m.nome.trim()),
        });
      }}
    >
      <div>
        {consultaIdProp == null ? (
          <>
            <label className="mb-1 block text-sm text-slate-600">ID da consulta</label>
            <input
              className="w-full rounded border border-slate-300 px-3 py-2 text-sm"
              value={consultaId}
              onChange={(e) => setConsultaId(e.target.value)}
              required
            />
          </>
        ) : null}
      </div>
      <div>
        <label className="mb-1 block text-sm text-slate-600">Observações</label>
        <textarea
          className="w-full rounded border border-slate-300 px-3 py-2 text-sm"
          rows={2}
          value={observacoes}
          onChange={(e) => setObservacoes(e.target.value)}
        />
      </div>
      <div className="space-y-3">
        <p className="text-sm font-medium text-slate-700">Medicamentos</p>
        {medicamentos.map((med, i) => (
          <div key={i} className="grid gap-2 rounded border border-slate-200 p-3 sm:grid-cols-2">
            <input
              placeholder="Nome"
              className="rounded border border-slate-300 px-2 py-1.5 text-sm"
              value={med.nome}
              onChange={(e) => updateMed(i, "nome", e.target.value)}
            />
            <input
              placeholder="Dosagem"
              className="rounded border border-slate-300 px-2 py-1.5 text-sm"
              value={med.dosagem}
              onChange={(e) => updateMed(i, "dosagem", e.target.value)}
            />
            <input
              placeholder="Frequência (ex: 2x por dia)"
              className="rounded border border-slate-300 px-2 py-1.5 text-sm"
              value={med.frequencia}
              onChange={(e) => updateMed(i, "frequencia", e.target.value)}
            />
            <input
              placeholder="Duração (ex: 7 dias)"
              className="rounded border border-slate-300 px-2 py-1.5 text-sm"
              value={med.duracao}
              onChange={(e) => updateMed(i, "duracao", e.target.value)}
            />
            <input
              placeholder="Posologia"
              className="sm:col-span-2 rounded border border-slate-300 px-2 py-1.5 text-sm"
              value={med.posologia ?? ""}
              onChange={(e) => updateMed(i, "posologia", e.target.value)}
            />
          </div>
        ))}
        <button
          type="button"
          className="text-sm text-primary-600 hover:underline"
          onClick={() => setMedicamentos((prev) => [...prev, { ...medicamentoVazio }])}
        >
          + Adicionar medicamento
        </button>
      </div>
      <Button type="submit" variant="primary" disabled={isPending}>
        {isPending ? "A guardar..." : "Criar prescrição"}
      </Button>
    </form>
  );
}

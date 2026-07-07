import { useState } from "react";

import { Button } from "@/design-system";

interface SeguimentoFormProps {
  onSubmit: (values: {
    consulta_id: number;
    data_prevista: string;
    motivo: string;
    observacoes?: string;
  }) => void;
  isPending?: boolean;
}

export function SeguimentoForm({ onSubmit, isPending }: SeguimentoFormProps) {
  const [consultaId, setConsultaId] = useState("");
  const [dataPrevista, setDataPrevista] = useState("");
  const [motivo, setMotivo] = useState("");
  const [observacoes, setObservacoes] = useState("");

  return (
    <form
      className="grid gap-4 sm:grid-cols-2"
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit({
          consulta_id: Number(consultaId),
          data_prevista: dataPrevista,
          motivo,
          observacoes,
        });
      }}
    >
      <div>
        <label className="mb-1 block text-sm text-slate-600">ID da consulta de origem</label>
        <input
          className="w-full rounded border border-slate-300 px-3 py-2 text-sm"
          value={consultaId}
          onChange={(e) => setConsultaId(e.target.value)}
          required
        />
      </div>
      <div>
        <label className="mb-1 block text-sm text-slate-600">Data prevista</label>
        <input
          type="date"
          className="w-full rounded border border-slate-300 px-3 py-2 text-sm"
          value={dataPrevista}
          onChange={(e) => setDataPrevista(e.target.value)}
          required
        />
      </div>
      <div className="sm:col-span-2">
        <label className="mb-1 block text-sm text-slate-600">Motivo do seguimento</label>
        <input
          className="w-full rounded border border-slate-300 px-3 py-2 text-sm"
          value={motivo}
          onChange={(e) => setMotivo(e.target.value)}
          required
        />
      </div>
      <div className="sm:col-span-2">
        <label className="mb-1 block text-sm text-slate-600">Observações</label>
        <textarea
          className="w-full rounded border border-slate-300 px-3 py-2 text-sm"
          rows={2}
          value={observacoes}
          onChange={(e) => setObservacoes(e.target.value)}
        />
      </div>
      <div>
        <Button type="submit" variant="primary" disabled={isPending}>
          {isPending ? "A agendar..." : "Agendar seguimento"}
        </Button>
      </div>
    </form>
  );
}

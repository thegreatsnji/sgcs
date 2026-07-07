import { useState } from "react";

import { Button } from "@/design-system";

interface AltaFormProps {
  onSubmit: (values: {
    consulta_id: number;
    motivo: string;
    condicao: string;
    recomendacoes?: string;
    medicacao?: string;
    seguimento?: string;
    restricoes?: string;
  }) => void;
  isPending?: boolean;
}

export function AltaForm({ onSubmit, isPending }: AltaFormProps) {
  const [consultaId, setConsultaId] = useState("");
  const [motivo, setMotivo] = useState("");
  const [condicao, setCondicao] = useState("");
  const [recomendacoes, setRecomendacoes] = useState("");
  const [medicacao, setMedicacao] = useState("");
  const [seguimento, setSeguimento] = useState("");
  const [restricoes, setRestricoes] = useState("");

  return (
    <form
      className="grid gap-4 sm:grid-cols-2"
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit({
          consulta_id: Number(consultaId),
          motivo,
          condicao,
          recomendacoes,
          medicacao,
          seguimento,
          restricoes,
        });
      }}
    >
      <div>
        <label className="mb-1 block text-sm text-slate-600">ID da consulta</label>
        <input
          className="w-full rounded border border-slate-300 px-3 py-2 text-sm"
          value={consultaId}
          onChange={(e) => setConsultaId(e.target.value)}
          required
        />
      </div>
      <div>
        <label className="mb-1 block text-sm text-slate-600">Condição</label>
        <input
          className="w-full rounded border border-slate-300 px-3 py-2 text-sm"
          value={condicao}
          onChange={(e) => setCondicao(e.target.value)}
          required
        />
      </div>
      <div className="sm:col-span-2">
        <label className="mb-1 block text-sm text-slate-600">Motivo da alta</label>
        <textarea
          className="w-full rounded border border-slate-300 px-3 py-2 text-sm"
          rows={2}
          value={motivo}
          onChange={(e) => setMotivo(e.target.value)}
          required
        />
      </div>
      <div className="sm:col-span-2">
        <label className="mb-1 block text-sm text-slate-600">Recomendações</label>
        <textarea
          className="w-full rounded border border-slate-300 px-3 py-2 text-sm"
          rows={2}
          value={recomendacoes}
          onChange={(e) => setRecomendacoes(e.target.value)}
        />
      </div>
      <div>
        <label className="mb-1 block text-sm text-slate-600">Medicação de alta</label>
        <textarea
          className="w-full rounded border border-slate-300 px-3 py-2 text-sm"
          rows={2}
          value={medicacao}
          onChange={(e) => setMedicacao(e.target.value)}
        />
      </div>
      <div>
        <label className="mb-1 block text-sm text-slate-600">Seguimento</label>
        <textarea
          className="w-full rounded border border-slate-300 px-3 py-2 text-sm"
          rows={2}
          value={seguimento}
          onChange={(e) => setSeguimento(e.target.value)}
        />
      </div>
      <div className="sm:col-span-2">
        <label className="mb-1 block text-sm text-slate-600">Restrições</label>
        <textarea
          className="w-full rounded border border-slate-300 px-3 py-2 text-sm"
          rows={2}
          value={restricoes}
          onChange={(e) => setRestricoes(e.target.value)}
        />
      </div>
      <div className="sm:col-span-2">
        <Button type="submit" variant="primary" disabled={isPending}>
          {isPending ? "A emitir..." : "Emitir alta médica"}
        </Button>
      </div>
    </form>
  );
}

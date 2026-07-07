import { useState } from "react";

import { Button } from "@/design-system";

interface QuoteFormProps {
  services: Array<{ id: number; nome: string; preco: string }>;
  onSubmit: (values: {
    paciente: number;
    validade?: string;
    itens: Array<{ servico: number; quantidade: number }>;
  }) => void;
  isPending?: boolean;
}

export function QuoteForm({ services, onSubmit, isPending }: QuoteFormProps) {
  const [pacienteId, setPacienteId] = useState("");
  const [servicoId, setServicoId] = useState(services[0]?.id ?? 0);
  const [quantidade, setQuantidade] = useState(1);

  return (
    <form
      className="grid gap-4 sm:grid-cols-2"
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit({
          paciente: Number(pacienteId),
          itens: [{ servico: servicoId, quantidade }],
        });
      }}
    >
      <div>
        <label className="mb-1 block text-sm text-slate-600">ID do paciente</label>
        <input
          className="w-full rounded border border-slate-300 px-3 py-2 text-sm"
          value={pacienteId}
          onChange={(e) => setPacienteId(e.target.value)}
          required
        />
      </div>
      <div>
        <label className="mb-1 block text-sm text-slate-600">Serviço</label>
        <select
          className="w-full rounded border border-slate-300 px-3 py-2 text-sm"
          value={servicoId}
          onChange={(e) => setServicoId(Number(e.target.value))}
        >
          {services.map((s) => (
            <option key={s.id} value={s.id}>
              {s.nome} — {s.preco} FCFA
            </option>
          ))}
        </select>
      </div>
      <div>
        <label className="mb-1 block text-sm text-slate-600">Quantidade</label>
        <input
          type="number"
          min={1}
          className="w-full rounded border border-slate-300 px-3 py-2 text-sm"
          value={quantidade}
          onChange={(e) => setQuantidade(Number(e.target.value))}
        />
      </div>
      <div className="flex items-end">
        <Button type="submit" variant="primary" disabled={isPending}>
          {isPending ? "A guardar..." : "Criar orçamento"}
        </Button>
      </div>
    </form>
  );
}

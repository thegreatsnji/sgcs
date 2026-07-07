import { useState } from "react";

import { Button } from "@/design-system";

interface TemplateEditorProps {
  initial?: { nome: string; assunto: string; corpo: string };
  onSubmit: (values: { nome: string; assunto: string; corpo: string }) => void;
  isPending?: boolean;
}

export function TemplateEditor({ initial, onSubmit, isPending }: TemplateEditorProps) {
  const [nome, setNome] = useState(initial?.nome ?? "");
  const [assunto, setAssunto] = useState(initial?.assunto ?? "");
  const [corpo, setCorpo] = useState(initial?.corpo ?? "");

  return (
    <form
      className="space-y-3"
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit({ nome, assunto, corpo });
      }}
    >
      <input
        className="w-full rounded border border-slate-300 px-3 py-2 text-sm"
        placeholder="Nome do template"
        value={nome}
        onChange={(e) => setNome(e.target.value)}
        required
      />
      <input
        className="w-full rounded border border-slate-300 px-3 py-2 text-sm"
        placeholder="Assunto (use {{nome}}, {{data}}, etc.)"
        value={assunto}
        onChange={(e) => setAssunto(e.target.value)}
        required
      />
      <textarea
        className="w-full rounded border border-slate-300 px-3 py-2 text-sm"
        rows={6}
        placeholder="Corpo do e-mail"
        value={corpo}
        onChange={(e) => setCorpo(e.target.value)}
        required
      />
      <Button type="submit" variant="primary" disabled={isPending}>
        Guardar template
      </Button>
    </form>
  );
}

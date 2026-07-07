interface TemplatePreviewProps {
  assunto?: string;
  corpo?: string;
  mensagem?: string;
}

export function TemplatePreview({ assunto, corpo, mensagem }: TemplatePreviewProps) {
  return (
    <div className="rounded border border-slate-200 bg-slate-50 p-4 text-sm">
      <p className="mb-2 font-medium text-slate-800">Pré-visualização</p>
      {assunto && (
        <p>
          <span className="text-slate-600">Assunto: </span>
          {assunto}
        </p>
      )}
      {corpo && <pre className="mt-2 whitespace-pre-wrap text-slate-700">{corpo}</pre>}
      {mensagem && <p className="text-slate-700">{mensagem}</p>}
    </div>
  );
}

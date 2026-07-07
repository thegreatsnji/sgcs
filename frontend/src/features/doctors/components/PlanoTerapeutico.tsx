interface PlanoTerapeuticoProps {
  objectivos?: string;
  duracaoPrevista?: string;
  descricao?: string;
}

export function PlanoTerapeutico({ objectivos, duracaoPrevista, descricao }: PlanoTerapeuticoProps) {
  if (!objectivos && !duracaoPrevista && !descricao) {
    return <p className="text-sm text-slate-500">Sem plano terapêutico definido.</p>;
  }

  return (
    <div className="rounded border border-slate-200 bg-slate-50 p-4 text-sm">
      <h4 className="mb-2 font-medium text-slate-800">Plano terapêutico</h4>
      {descricao && (
        <p>
          <span className="text-slate-600">Descrição: </span>
          {descricao}
        </p>
      )}
      {objectivos && (
        <p>
          <span className="text-slate-600">Objectivos: </span>
          {objectivos}
        </p>
      )}
      {duracaoPrevista && (
        <p>
          <span className="text-slate-600">Duração prevista: </span>
          {duracaoPrevista}
        </p>
      )}
    </div>
  );
}

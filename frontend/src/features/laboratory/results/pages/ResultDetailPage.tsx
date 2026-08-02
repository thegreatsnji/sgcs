import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";

import { Button, Card, ErrorState, useToast } from "@/design-system";
import { LaboratorySubNav } from "@/features/laboratory/components/LaboratorySubNav";
import { LaboratoryTableSkeleton } from "@/features/laboratory/components/LaboratorySkeleton";
import {
  InterpretationPanel,
  LabPatientPanel,
} from "@/features/laboratory/results/components/ResultEntryLayout";
import { ParametroResultsTable } from "@/features/laboratory/results/components/ParametroResultsTable";
import { ResultadoStatusBadge } from "@/features/laboratory/results/components/ResultadoStatusBadge";
import { ResultadoTimeline } from "@/features/laboratory/results/components/ResultadoTimeline";
import { UploadResultado } from "@/features/laboratory/results/components/UploadResultado";
import { usePermissions } from "@/hooks/usePermissions";
import { laboratoryResultsService } from "@/services/laboratory";
import { getApiErrorMessage } from "@/utils/api-error";
import { formatDisplayDateTime } from "@/utils/date";

export function ResultDetailPage() {
  const { id } = useParams<{ id: string }>();
  const resultId = Number(id);
  const { showToast } = useToast();
  const queryClient = useQueryClient();
  const { hasPermission } = usePermissions();

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["laboratory-result", resultId],
    queryFn: () => laboratoryResultsService.get(resultId),
    enabled: Number.isFinite(resultId),
  });

  const invalidate = () => {
    void queryClient.invalidateQueries({ queryKey: ["laboratory-result", resultId] });
    void queryClient.invalidateQueries({ queryKey: ["laboratory-results"] });
  };

  const validateMutation = useMutation({
    mutationFn: () => laboratoryResultsService.validate(resultId),
    onSuccess: () => { showToast("Resultado validado.", "success"); invalidate(); },
    onError: (e) => showToast(getApiErrorMessage(e), "error"),
  });

  const publishMutation = useMutation({
    mutationFn: () => laboratoryResultsService.publish(resultId),
    onSuccess: () => { showToast("Resultado publicado ao médico.", "success"); invalidate(); },
    onError: (e) => showToast(getApiErrorMessage(e), "error"),
  });

  const uploadMutation = useMutation({
    mutationFn: ({ file, descricao }: { file: File; descricao: string }) =>
      laboratoryResultsService.uploadAttachment(resultId, file, descricao),
    onSuccess: () => { showToast("Anexo adicionado.", "success"); invalidate(); },
    onError: (e) => showToast(getApiErrorMessage(e), "error"),
  });

  if (!Number.isFinite(resultId)) return <ErrorState message="Resultado inválido." />;
  if (isLoading || !data) return <LaboratoryTableSkeleton rows={4} />;
  if (isError) return <ErrorState message="Erro ao carregar." onRetry={() => void refetch()} />;

  const canEdit = hasPermission("laboratory.results.edit") && data.editavel;
  const canValidate = hasPermission("laboratory.results.validate") && data.estado === "RESULTADO_PENDENTE";
  const canPublish = hasPermission("laboratory.results.publish") && data.estado === "VALIDADO";

  const validationStatus = (
    <div className="rounded-2xl border border-slate-200/80 bg-white p-4 shadow-sm">
      <p className="text-[10px] font-semibold tracking-widest text-slate-400 uppercase">Estado de validação</p>
      <div className="mt-2">
        <ResultadoStatusBadge status={data.estado} />
      </div>
      {data.data_validacao && (
        <p className="mt-2 text-xs text-slate-500">
          Validado: {formatDisplayDateTime(data.data_validacao)}
          {data.validado_por_nome && ` · ${data.validado_por_nome}`}
        </p>
      )}
    </div>
  );

  return (
    <div className="space-y-6 pb-8">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <Link to="/laboratory/results" className="text-sm font-medium text-primary-600 hover:text-primary-700">
          ← Voltar aos resultados
        </Link>
        <div className="flex flex-wrap gap-2">
          {canEdit && (
            <Link to={`/laboratory/results/${resultId}/edit`}>
              <Button variant="outline">Editar</Button>
            </Link>
          )}
          {canValidate && (
            <Button variant="primary" onClick={() => validateMutation.mutate()} isLoading={validateMutation.isPending}>
              Validar resultado
            </Button>
          )}
          {canPublish && (
            <Button variant="primary" onClick={() => publishMutation.mutate()} isLoading={publishMutation.isPending}>
              Publicar ao médico
            </Button>
          )}
        </div>
      </div>

      <LaboratorySubNav />

      <div className="grid gap-6 xl:grid-cols-[240px_1fr_280px]">
        <LabPatientPanel
          patient={{
            full_name: data.paciente_nome,
            numero_pedido: data.numero_pedido,
            medico_nome: data.medico_nome,
            estado: data.estado,
          }}
        />

        <div className="min-w-0 space-y-4">
          <ParametroResultsTable parametros={data.parametros} />
        </div>

        <InterpretationPanel
          observacoes={data.observacoes}
          conclusao={data.conclusao}
          validationStatus={validationStatus}
          timeline={<ResultadoTimeline resultado={data} />}
        />
      </div>

      {data.anexos.length > 0 && (
        <Card title="Anexos">
          <ul className="divide-y divide-slate-100">
            {data.anexos.map((anexo) => (
              <li key={anexo.id} className="flex items-center justify-between gap-2 py-3 first:pt-0">
                <span className="text-sm text-slate-700">{anexo.nome_ficheiro || anexo.descricao || anexo.tipo}</span>
                <a
                  href={laboratoryResultsService.downloadUrl(resultId, anexo.id)}
                  className="text-sm font-medium text-primary-600 hover:text-primary-700"
                  target="_blank"
                  rel="noreferrer"
                >
                  Descarregar
                </a>
              </li>
            ))}
          </ul>
        </Card>
      )}

      {canEdit && hasPermission("laboratory.results.create") && (
        <Card title="Anexar documento">
          <UploadResultado
            onUpload={(file, descricao) => uploadMutation.mutate({ file, descricao })}
            isPending={uploadMutation.isPending}
          />
        </Card>
      )}
    </div>
  );
}

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";

import { Button, Card, ErrorState, LoadingState, useToast } from "@/design-system";
import { LaboratorySubNav } from "@/features/laboratory/components/LaboratorySubNav";
import { ResultadoPreview } from "@/features/laboratory/results/components/ResultadoPreview";
import { ResultadoTimeline } from "@/features/laboratory/results/components/ResultadoTimeline";
import { UploadResultado } from "@/features/laboratory/results/components/UploadResultado";
import { usePermissions } from "@/hooks/usePermissions";
import { laboratoryResultsService } from "@/services/laboratory";
import { getApiErrorMessage } from "@/utils/api-error";

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
  if (isLoading || !data) return <LoadingState message="A carregar resultado..." />;
  if (isError) return <ErrorState message="Erro ao carregar." onRetry={() => void refetch()} />;

  const canEdit = hasPermission("laboratory.results.edit") && data.editavel;
  const canValidate = hasPermission("laboratory.results.validate") && data.estado === "RESULTADO_PENDENTE";
  const canPublish = hasPermission("laboratory.results.publish") && data.estado === "VALIDADO";

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <Link to="/laboratory/results" className="text-sm text-primary-700 hover:underline">
          ← Voltar aos resultados
        </Link>
        <div className="flex flex-wrap gap-2">
          {canEdit && (
            <Link to={`/laboratory/results/${resultId}/edit`}>
              <Button variant="secondary">Editar</Button>
            </Link>
          )}
          {canValidate && (
            <Button variant="primary" onClick={() => validateMutation.mutate()} disabled={validateMutation.isPending}>
              Validar
            </Button>
          )}
          {canPublish && (
            <Button variant="primary" onClick={() => publishMutation.mutate()} disabled={publishMutation.isPending}>
              Publicar
            </Button>
          )}
        </div>
      </div>
      <LaboratorySubNav />
      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <ResultadoPreview resultado={data} />
        </div>
        <Card title="Histórico">
          <ResultadoTimeline resultado={data} />
        </Card>
      </div>

      {data.anexos.length > 0 && (
        <Card title="Anexos">
          <ul className="space-y-2 text-sm">
            {data.anexos.map((anexo) => (
              <li key={anexo.id} className="flex items-center justify-between gap-2">
                <span>{anexo.nome_ficheiro || anexo.descricao || anexo.tipo}</span>
                <a
                  href={laboratoryResultsService.downloadUrl(resultId, anexo.id)}
                  className="text-primary-700 hover:underline"
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

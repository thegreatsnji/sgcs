import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate, useParams } from "react-router-dom";

import { Button, Card, LoadingState, useToast } from "@/design-system";
import { AppointmentSubNav } from "@/features/appointments/components/AppointmentSubNav";
import { appointmentsService } from "@/services/appointments";
import { getApiErrorMessage } from "@/utils/api-error";

export function AppointmentEditPage() {
  const { id } = useParams<{ id: string }>();
  const appointmentId = Number(id);
  const navigate = useNavigate();
  const { showToast } = useToast();
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ["appointment", appointmentId],
    queryFn: () => appointmentsService.get(appointmentId),
    enabled: Number.isFinite(appointmentId),
  });

  const mutation = useMutation({
    mutationFn: (payload: { scheduled_at: string }) => appointmentsService.update(appointmentId, payload),
    onSuccess: () => {
      showToast("Consulta actualizada.", "success");
      void queryClient.invalidateQueries({ queryKey: ["appointment", appointmentId] });
      navigate(`/appointments/${appointmentId}`);
    },
    onError: (e) => showToast(getApiErrorMessage(e), "error"),
  });

  if (isLoading || !data) return <LoadingState message="A carregar..." />;

  const defaultDateTime = data.scheduled_at.slice(0, 16);

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-slate-900">Editar Consulta {data.appointment_number}</h2>
      <AppointmentSubNav />
      <div className="max-w-xl">
        <Card title="Reagendar">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              const form = new FormData(e.currentTarget);
              mutation.mutate({ scheduled_at: new Date(String(form.get("scheduled_at"))).toISOString() });
            }}
            className="space-y-4"
          >
            <input
              name="scheduled_at"
              type="datetime-local"
              defaultValue={defaultDateTime}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            />
            <Button type="submit" disabled={mutation.isPending}>Guardar alterações</Button>
          </form>
        </Card>
      </div>
    </div>
  );
}

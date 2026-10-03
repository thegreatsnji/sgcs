import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { Card, LoadingState } from "@/design-system";
import { AltaForm } from "@/features/doctors/components/AltaForm";
import { DoctorSubNav } from "@/features/doctors/components/DoctorSubNav";
import { HistoricoClinico } from "@/features/doctors/components/HistoricoClinico";
import { MedicamentosTable } from "@/features/doctors/components/MedicamentosTable";
import { PlanoTerapeutico } from "@/features/doctors/components/PlanoTerapeutico";
import { PrescricaoForm } from "@/features/doctors/components/PrescricaoForm";
import { TratamentosTable } from "@/features/doctors/components/TratamentosTable";
import { doctorsService } from "@/services/doctors/doctors.service";

export function DoctorDashboardPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["doctor-prescriptions"],
    queryFn: doctorsService.listPrescriptions,
  });

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Módulo Médico</h2>
        <p className="mt-1 text-slate-600">Prescrições, tratamentos e evolução clínica.</p>
      </div>
      <DoctorSubNav />
      {isLoading ? (
        <LoadingState message="A carregar..." />
      ) : (
        <Card title="Prescrições recentes">
          <p className="text-sm text-slate-600">{data?.results.length ?? 0} prescrições registadas.</p>
        </Card>
      )}
    </div>
  );
}

export function PrescriptionsPage() {
  const queryClient = useQueryClient();
  const { data, isLoading } = useQuery({
    queryKey: ["doctor-prescriptions"],
    queryFn: doctorsService.listPrescriptions,
  });

  const createMutation = useMutation({
    mutationFn: doctorsService.createPrescription,
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ["doctor-prescriptions"] }),
  });

  const refetch = () => void queryClient.invalidateQueries({ queryKey: ["doctor-prescriptions"] });

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Prescrições</h2>
      <DoctorSubNav />
      <Card title="Nova prescrição">
        <PrescricaoForm onSubmit={(v) => createMutation.mutate(v)} isPending={createMutation.isPending} />
      </Card>
      {isLoading ? (
        <LoadingState />
      ) : (
        data?.results.map((p) => (
          <Card key={p.id} title={`Prescrição #${p.id} — ${p.paciente_nome ?? ""}`}>
            <MedicamentosTable
              medicamentos={p.medicamentos}
              prescricaoId={p.id}
              estadoPrescricao={p.estado}
              onApprove={() => void doctorsService.approvePrescription(p.id).then(refetch)}
            />
            <div className="mt-4">
              <PlanoTerapeutico />
            </div>
          </Card>
        ))
      )}
    </div>
  );
}

export function TreatmentsPage() {
  const queryClient = useQueryClient();
  const { data, isLoading } = useQuery({
    queryKey: ["doctor-treatments"],
    queryFn: doctorsService.listTreatments,
  });

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Tratamentos</h2>
      <DoctorSubNav />
      {isLoading ? (
        <LoadingState />
      ) : (
        <Card title="Lista de tratamentos">
          <TratamentosTable
            tratamentos={data?.results ?? []}
            onFinish={(id) =>
              void doctorsService.finishTreatment(id).then(() =>
                queryClient.invalidateQueries({ queryKey: ["doctor-treatments"] }),
              )
            }
          />
        </Card>
      )}
    </div>
  );
}

export function HistoryPage() {
  const [pacienteId, setPacienteId] = useState("");
  const { data, isLoading, refetch } = useQuery({
    queryKey: ["doctor-history", pacienteId],
    queryFn: () => doctorsService.getHistory(Number(pacienteId)),
    enabled: Boolean(pacienteId),
  });

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Histórico terapêutico</h2>
      <DoctorSubNav />
      <Card title="Consultar por paciente">
        <div className="mb-4 flex gap-2">
          <input
            className="rounded border border-slate-300 px-3 py-2 text-sm"
            placeholder="ID do paciente"
            value={pacienteId}
            onChange={(e) => setPacienteId(e.target.value)}
          />
          <button
            type="button"
            className="rounded bg-primary-600 px-4 py-2 text-sm text-white hover:bg-primary-700"
            onClick={() => void refetch()}
          >
            Pesquisar
          </button>
        </div>
        <HistoricoClinico historico={data} isLoading={isLoading} />
      </Card>
    </div>
  );
}

export function DischargePage() {
  const mutation = useMutation({ mutationFn: doctorsService.createDischarge });

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Alta médica</h2>
      <DoctorSubNav />
      <Card title="Emitir alta">
        <AltaForm onSubmit={(v) => mutation.mutate(v)} isPending={mutation.isPending} />
      </Card>
    </div>
  );
}

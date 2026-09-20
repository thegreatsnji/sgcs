import { api } from "@/services/api/client";
import type { ApiEnvelope, PaginatedResponse } from "@/types/api";
import type {
  AssignToDoctorPayload,
  AssignToDoctorResponse,
  CheckInPayload,
  CheckInResponse,
  ReceptionCheckIn,
  Referral,
  ReferralPayload,
  WaitingQueueEntry,
} from "@/types/reception";
import { unwrapApiData } from "@/utils/api-response";

async function getPaginated<T>(url: string, params?: object) {
  const { data } = await api.get<ApiEnvelope<PaginatedResponse<T>>>(url, { params });
  return unwrapApiData(data);
}

export const receptionService = {
  checkIn: async (payload: CheckInPayload) => {
    const { data } = await api.post<ApiEnvelope<CheckInResponse>>(
      "/reception/check-in/",
      payload,
    );
    return unwrapApiData(data);
  },

  getQueue: async (params?: {
    status?: string;
    priority?: string;
    page?: number;
    doctor?: number | "unassigned";
    unassigned?: boolean;
  }) => {
    const query: Record<string, string | number | boolean | undefined> = {
      status: params?.status,
      priority: params?.priority,
      page: params?.page,
    };
    if (params?.doctor === "unassigned" || params?.unassigned) {
      query.unassigned = true;
    } else if (typeof params?.doctor === "number") {
      query.doctor = params.doctor;
    }
    return getPaginated<WaitingQueueEntry>("/reception/queue/", query);
  },

  updateQueueEntry: async (queueId: number, payload: { status: string }) => {
    const { data } = await api.patch<ApiEnvelope<WaitingQueueEntry>>(
      `/reception/queue/${queueId}/`,
      payload,
    );
    return unwrapApiData(data);
  },

  assignToDoctor: async (payload: AssignToDoctorPayload) => {
    const { data } = await api.post<ApiEnvelope<AssignToDoctorResponse>>(
      "/reception/assign-to-doctor/",
      payload,
    );
    return unwrapApiData(data);
  },

  getDoctorAssignmentOptions: async (
    patientId?: number,
    extra?: { queue_id?: number; check_in_id?: number },
  ) => {
    const { data } = await api.get<ApiEnvelope<import("@/types/reception").DoctorAssignmentOptions>>(
      "/reception/doctor-assignment-options/",
      {
        params: {
          patient_id: patientId,
          queue_id: extra?.queue_id,
          check_in_id: extra?.check_in_id,
        },
      },
    );
    return unwrapApiData(data);
  },

  getHistory: async (params?: { patient?: number; page?: number }) =>
    getPaginated<ReceptionCheckIn>("/reception/history/", params),

  createReferral: async (payload: ReferralPayload) => {
    const { data } = await api.post<ApiEnvelope<Referral>>("/reception/referrals/", payload);
    return unwrapApiData(data);
  },

  getPendingClinicalLabOrders: async (params?: { estado_faturacao?: string }) => {
    const { data } = await api.get<
      ApiEnvelope<
        Array<{
          id: number;
          paciente_id: number;
          paciente_nome: string;
          paciente_codigo: string;
          tipo_exame: string;
          estado_faturacao: string;
          estado_faturacao_label: string;
          prioridade: string;
          created_at: string;
          servico: { id: number; codigo: string; nome: string } | null;
        }>
      >
    >("/reception/pending-clinical-lab-orders/", { params });
    return unwrapApiData(data);
  },

  markLabOrderBilled: async (orderId: number) => {
    const { data } = await api.post<
      ApiEnvelope<{ id: number; estado_faturacao: string; already_regularized: boolean }>
    >(`/reception/mark-lab-order-billed/${orderId}/`);
    return unwrapApiData(data);
  },
};

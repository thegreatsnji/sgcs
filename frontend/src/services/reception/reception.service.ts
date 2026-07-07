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

  getQueue: async (params?: { status?: string; priority?: string; page?: number }) =>
    getPaginated<WaitingQueueEntry>("/reception/queue/", params),

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

  getHistory: async (params?: { patient?: number; page?: number }) =>
    getPaginated<ReceptionCheckIn>("/reception/history/", params),

  createReferral: async (payload: ReferralPayload) => {
    const { data } = await api.post<ApiEnvelope<Referral>>("/reception/referrals/", payload);
    return unwrapApiData(data);
  },
};

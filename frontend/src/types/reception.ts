export type CheckInStatus = "WAITING" | "IN_CONSULTATION" | "COMPLETED" | "CANCELLED";

export type QueuePriority = "LOW" | "NORMAL" | "HIGH" | "EMERGENCY";

export type QueueStatus = "WAITING" | "CALLED" | "IN_SERVICE" | "COMPLETED" | "CANCELLED";

export type ReferralDepartment = "RECEPTION" | "DOCTOR" | "LAB" | "BILLING";

export type TriageColor = "GREEN" | "YELLOW" | "RED";

export interface ReceptionPatientSummary {
  id: number;
  full_name: string;
  patient_number: string;
  phone: string | null;
}

export interface ReceptionUserSummary {
  id: number;
  full_name: string;
}

export interface WaitingQueueEntry {
  id: number;
  check_in_id: number;
  patient: ReceptionPatientSummary;
  position: number;
  estimated_wait_minutes: number | null;
  status: QueueStatus;
  priority: QueuePriority;
  triage_color?: TriageColor | "";
  symptoms?: string;
  check_in_time: string;
  receptionist: ReceptionUserSummary;
  created_at: string;
  updated_at: string;
}

export interface ReceptionCheckIn {
  id: number;
  patient: ReceptionPatientSummary;
  receptionist: ReceptionUserSummary;
  check_in_time: string;
  status: CheckInStatus;
  priority: QueuePriority;
  triage_color?: TriageColor | "";
  age_at_check_in?: number | null;
  weight?: string | null;
  temperature?: string | null;
  blood_pressure?: string;
  symptoms?: string;
  notes: string;
  created_at: string;
}

export interface Referral {
  id: number;
  patient: ReceptionPatientSummary;
  check_in: number | null;
  from_department: ReferralDepartment;
  to_department: ReferralDepartment;
  reason: string;
  referred_by: ReceptionUserSummary | null;
  created_at: string;
}

export interface CheckInPayload {
  patient_id: number;
  priority?: QueuePriority;
  triage_color?: TriageColor;
  age_at_check_in?: number;
  weight?: number;
  temperature?: number;
  blood_pressure?: string;
  symptoms?: string;
  notes?: string;
}

export interface CheckInResponse {
  check_in: ReceptionCheckIn;
  queue_entry: WaitingQueueEntry;
}

export interface AssignToDoctorPayload {
  queue_id?: number;
  check_in_id?: number;
  reason?: string;
}

export interface AssignToDoctorResponse {
  referral: Referral;
  queue_entry: WaitingQueueEntry | null;
}

export interface ReferralPayload {
  patient_id: number;
  check_in_id?: number | null;
  to_department: ReferralDepartment;
  reason: string;
}

export interface ReceptionDashboardData {
  cards: {
    patients_waiting: number;
    average_wait_minutes: number;
    attended_today: number;
    active_emergencies: number;
  };
  queue_preview: Array<{
    id: number;
    position: number;
    status: string;
    estimated_wait_minutes: number | null;
    patient__full_name: string;
    patient__patient_number: string;
    check_in__priority: QueuePriority;
  }>;
  recent_reception_activity: Array<{
    action: string;
    description: string;
    user: string;
    created_at: string;
  }>;
}

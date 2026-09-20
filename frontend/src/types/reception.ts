export type CheckInStatus = "WAITING" | "IN_CONSULTATION" | "COMPLETED" | "CANCELLED";

export type QueuePriority = "LOW" | "NORMAL" | "HIGH" | "EMERGENCY";

export type QueueStatus = "WAITING" | "CALLED" | "IN_SERVICE" | "COMPLETED" | "CANCELLED";

export type ReferralDepartment = "RECEPTION" | "DOCTOR" | "LAB" | "BILLING";

export type TriageColor = "GREEN" | "YELLOW" | "RED";

export type PatientAgeCategoryAtCheckIn = "ADULT" | "MINOR";

export type VisitPurpose = "CONSULTA" | "CONTROLE";

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
  assigned_doctor?: ReceptionUserSummary | null;
  can_reassign_doctor?: boolean;
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
  age_category_at_check_in?: PatientAgeCategoryAtCheckIn | "";
  weight?: string | null;
  height_cm?: number | null;
  spo2?: number | null;
  heart_rate?: number | null;
  respiratory_rate?: number | null;
  race?: string;
  visit_purpose?: VisitPurpose | "";
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
  height_cm?: number;
  spo2?: number;
  heart_rate?: number;
  respiratory_rate?: number;
  race?: string;
  visit_purpose?: VisitPurpose;
  temperature?: number;
  blood_pressure?: string;
  symptoms?: string;
  notes?: string;
  unusual_vitals_confirmed?: boolean;
}

export interface CheckInResponse {
  check_in: ReceptionCheckIn;
  queue_entry: WaitingQueueEntry;
}

export interface AssignToDoctorPayload {
  queue_id?: number;
  check_in_id?: number;
  doctor_id?: number;
  reason?: string;
}

export interface DoctorAssignmentOption {
  id: number;
  full_name: string;
  available: boolean;
  waiting_count: number;
  is_preferred: boolean;
  availability_label?: string;
}

export interface DoctorAssignmentOptions {
  preferred_doctor: { id: number; full_name: string; available: boolean } | null;
  scheduled_doctor?: { id: number; full_name: string; available: boolean } | null;
  suggested_doctor_id: number | null;
  doctors: DoctorAssignmentOption[];
}

export interface AssignToDoctorResponse {
  referral: Referral;
  queue_entry: WaitingQueueEntry | null;
  consulta: {
    id: number;
    appointment_number: string;
    status: string;
    doctor_id?: number | null;
    doctor_name?: string | null;
  } | null;
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
    patient__id: number;
    patient__full_name: string;
    patient__patient_number: string;
    check_in__priority: QueuePriority;
    check_in__triage_color?: string;
    check_in__visit_purpose?: string;
    assigned_doctor__id?: number | null;
    assigned_doctor__full_name?: string | null;
  }>;
  recent_reception_activity: Array<{
    action: string;
    description: string;
    user: string;
    created_at: string;
  }>;
}

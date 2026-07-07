import type { UserRole } from "./user";

export interface ManagedUser extends Record<string, unknown> {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  phone?: string;
  gender?: string;
  birth_date?: string | null;
  position?: string;
  photo_url?: string | null;
  role: UserRole;
  is_active: boolean;
  date_joined: string;
  last_login: string | null;
  last_activity?: string | null;
}

export interface UserPayload {
  email?: string;
  first_name: string;
  last_name: string;
  phone?: string;
  gender?: string;
  birth_date?: string | null;
  position?: string;
  role?: UserRole;
  password?: string;
  password_confirm?: string;
  is_active?: boolean;
}

export interface UserFilters {
  page?: number;
  page_size?: number;
  search?: string;
  role?: string;
  is_active?: boolean;
  date_joined_after?: string;
  date_joined_before?: string;
  last_login_after?: string;
  last_login_before?: string;
  ordering?: string;
}

export interface Permission {
  id: number;
  module: string;
  action: string;
  codename: string;
  name: string;
  description: string;
}

export interface Role {
  id: number;
  name: string;
  slug: string;
  description: string;
  is_system: boolean;
  permissions: Permission[];
  permission_count: number;
}

export interface UserGroup {
  id: number;
  name: string;
  description: string;
  is_active: boolean;
  permissions: Permission[];
  members_count: number;
  created_at: string;
  updated_at: string;
}

export interface AuditLog {
  id: number;
  user: number | null;
  user_email: string | null;
  user_name: string | null;
  action: string;
  ip_address: string | null;
  user_agent: string;
  description: string;
  resource_type: string;
  resource_id: string;
  metadata: Record<string, unknown>;
  created_at: string;
}

export interface AdminDashboardData {
  cards: {
    total_users: number;
    active_users: number;
    inactive_users: number;
    new_users_week: number;
    active_sessions: number;
    total_patients: number;
    active_patients: number;
    inactive_patients: number;
    new_patients_week: number;
  };
  users_by_role: Array<{ role: string; count: number }>;
  logins_by_day: Array<{ date: string; count: number }>;
  recent_logins: Array<{
    user: string;
    email: string;
    ip_address: string | null;
    created_at: string;
  }>;
  recent_activity: Array<{
    action: string;
    description: string;
    user: string;
    created_at: string;
    resource_type?: string;
  }>;
  recent_patient_activity: Array<{
    action: string;
    description: string;
    user: string;
    created_at: string;
    resource_id: string;
  }>;
}

export interface ClinicalDashboardData {
  cards: {
    total_patients: number;
    active_patients: number;
    inactive_patients: number;
    new_patients_week: number;
  };
  recent_patients: Array<{
    id: number;
    full_name: string;
    patient_number: string;
    created_at: string;
  }>;
  recent_patient_activity: Array<{
    action: string;
    description: string;
    user: string;
    created_at: string;
    resource_id: string;
  }>;
}

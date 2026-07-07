export type EntityStatus = "active" | "inactive" | "archived";

export interface BaseEntity {
  id: number;
  created_at?: string;
  updated_at?: string;
}

export interface UserSummary {
  id: number;
  full_name: string;
}

export interface SelectOption<T = string> {
  label: string;
  value: T;
}

export type UserRole =
  | "ADMINISTRADOR"
  | "RECECIONISTA"
  | "MEDICO"
  | "ENFERMEIRO"
  | "LABORATORIO"
  | "FINANCEIRO";

export interface User {
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

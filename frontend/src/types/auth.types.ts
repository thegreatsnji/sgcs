import type { User } from "./user";

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  first_name: string;
  last_name: string;
  password: string;
  password_confirm: string;
  role: Exclude<import("./user").UserRole, "ADMINISTRADOR">;
}

export interface LoginResponse extends AuthTokens {
  user?: User;
}

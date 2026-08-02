import type { UserRole } from "@/types/user";

export const USER_ROLES = {
  ADMINISTRADOR: "ADMINISTRADOR",
  DIRECTOR: "DIRECTOR",
  RECECIONISTA: "RECECIONISTA",
  MEDICO: "MEDICO",
  ENFERMEIRO: "ENFERMEIRO",
  LABORATORIO: "LABORATORIO",
  FINANCEIRO: "FINANCEIRO",
} as const;

export const ROLE_LABELS: Record<string, string> = {
  ADMINISTRADOR: "Administrador",
  DIRECTOR: "Director",
  RECECIONISTA: "Rececionista",
  MEDICO: "Médico",
  ENFERMEIRO: "Enfermeiro",
  LABORATORIO: "Laboratório",
  FINANCEIRO: "Financeiro",
};

export const ASSIGNABLE_ROLES: UserRole[] = [
  "ADMINISTRADOR",
  "DIRECTOR",
  "RECECIONISTA",
  "MEDICO",
  "LABORATORIO",
];

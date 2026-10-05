import type { UserRole } from "@/types/user";

export function getRoleDashboardPath(role?: UserRole | string | null): string {
  switch (role) {
    case "ADMINISTRADOR":
      return "/dashboard/admin";
    case "DIRECTOR":
      return "/dashboard/director";
    case "MEDICO":
      return "/dashboard/doctor";
    case "RECECIONISTA":
      return "/dashboard/reception";
    case "LABORATORIO":
      return "/dashboard/laboratory";
    case "FINANCEIRO":
      return "/finance";
    case "ENFERMEIRO":
      return "/dashboard/nurse";
    default:
      return "/404";
  }
}

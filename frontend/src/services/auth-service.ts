/**
 * Re-export de compatibilidade.
 * Utilize `@/services/auth` em código novo.
 */
export {
  getCurrentUser,
  login,
  logout,
  register,
} from "./auth/auth.service";

import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { useQueryClient } from "@tanstack/react-query";

import { getCurrentUser, login as loginRequest, logout as logoutRequest } from "@/services/auth-service";
import type { LoginCredentials, User } from "@/types/auth";
import { clearStoredAuth, getStoredAuth, setStoredAuth } from "@/utils/auth-storage";

interface AuthContextValue {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginCredentials) => Promise<User>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const queryClient = useQueryClient();

  const refreshUser = useCallback(async () => {
    const auth = getStoredAuth();
    if (!auth?.access) {
      setUser(null);
      setIsLoading(false);
      return;
    }

    try {
      const currentUser = await Promise.race([
        getCurrentUser(),
        new Promise<never>((_, reject) => {
          window.setTimeout(() => reject(new Error("timeout")), 15_000);
        }),
      ]);
      setUser(currentUser);
    } catch {
      clearStoredAuth();
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const login = useCallback(async (credentials: LoginCredentials) => {
    const response = await loginRequest(credentials);
    setStoredAuth({ access: response.access, refresh: response.refresh });
    if (response.user) {
      setUser(response.user);
      void queryClient.invalidateQueries({ queryKey: ["profile-permissions"] });
      return response.user;
    }
    const currentUser = await getCurrentUser();
    setUser(currentUser);
    void queryClient.invalidateQueries({ queryKey: ["profile-permissions"] });
    return currentUser;
  }, [queryClient]);

  const logout = useCallback(async () => {
    const auth = getStoredAuth();
    if (auth?.refresh) {
      try {
        await logoutRequest(auth.refresh);
      } catch {
        // Sessão já pode estar inválida no servidor
      }
    }
    clearStoredAuth();
    setUser(null);
    void queryClient.invalidateQueries({ queryKey: ["profile-permissions"] });
  }, [queryClient]);

  const value = useMemo(
    () => ({
      user,
      isAuthenticated: Boolean(user),
      isLoading,
      login,
      logout,
      refreshUser,
    }),
    [user, isLoading, login, logout, refreshUser],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth deve ser utilizado dentro de AuthProvider.");
  }
  return context;
}

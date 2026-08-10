import { useQuery } from "@tanstack/react-query";
import { useCallback, useMemo } from "react";

import { useAuth } from "@/contexts/AuthContext";
import { usersService } from "@/services/users";

export function usePermissions() {
  const { user } = useAuth();

  const { data: profile, isLoading } = useQuery({
    queryKey: ["profile-permissions", user?.id],
    queryFn: usersService.getProfile,
    enabled: Boolean(user),
    staleTime: 5 * 60_000,
  });

  const permissions = profile?.permissions ?? [];

  const hasPermission = useCallback(
    (codename: string) => {
      if (!user) return false;
      if (user.role === "ADMINISTRADOR") return true;
      return permissions.includes(codename);
    },
    [permissions, user],
  );

  return useMemo(
    () => ({
      permissions,
      hasPermission,
      isLoading,
    }),
    [permissions, hasPermission, isLoading],
  );
}

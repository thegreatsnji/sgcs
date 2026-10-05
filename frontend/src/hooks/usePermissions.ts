import { useQuery } from "@tanstack/react-query";
import { useCallback, useMemo } from "react";

import { useAuth } from "@/contexts/AuthContext";
import { usersService } from "@/services/users";

export function usePermissions() {
  const { user } = useAuth();

  const { data: profile, isLoading, isError, refetch } = useQuery({
    queryKey: ["profile-permissions", user?.id],
    queryFn: usersService.getProfile,
    enabled: Boolean(user),
    staleTime: 5 * 60_000,
    retry: 2,
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
      isLoading: Boolean(user) && isLoading,
      isError,
      refetchPermissions: refetch,
    }),
    [permissions, hasPermission, isLoading, isError, refetch, user],
  );
}

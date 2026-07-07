import { useEffect } from "react";

import { useAuth } from "@/contexts/AuthContext";

export function useAuthBootstrap() {
  const { refreshUser } = useAuth();

  useEffect(() => {
    void refreshUser();
  }, [refreshUser]);
}

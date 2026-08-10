import { useQuery } from "@tanstack/react-query";

import { dashboardService } from "@/services/dashboard";

export function useReceptionDashboard(options?: { enabled?: boolean }) {
  return useQuery({
    queryKey: ["reception-dashboard"],
    queryFn: dashboardService.getReceptionSummary,
    refetchInterval: 30_000,
    enabled: options?.enabled ?? true,
  });
}

import { useQuery } from "@tanstack/react-query";

import { dashboardService } from "@/services/dashboard";

export function useConsultationDashboard() {
  return useQuery({
    queryKey: ["consultation-dashboard"],
    queryFn: dashboardService.getConsultationSummary,
    refetchInterval: 30_000,
  });
}

import { useQuery } from "@tanstack/react-query";

import { receptionService } from "@/services/reception";

export function useReceptionQueue(page = 1) {
  return useQuery({
    queryKey: ["reception-queue", page],
    queryFn: () => receptionService.getQueue({ page }),
    refetchInterval: 30_000,
  });
}

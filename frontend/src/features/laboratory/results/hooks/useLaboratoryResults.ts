import { useQuery } from "@tanstack/react-query";

import { laboratoryResultsService } from "@/services/laboratory";

export function useLaboratoryResults(params?: object) {
  return useQuery({
    queryKey: ["laboratory-results", params],
    queryFn: () => laboratoryResultsService.list(params),
  });
}

export function useLaboratoryResult(id: number) {
  return useQuery({
    queryKey: ["laboratory-result", id],
    queryFn: () => laboratoryResultsService.get(id),
    enabled: Number.isFinite(id),
  });
}

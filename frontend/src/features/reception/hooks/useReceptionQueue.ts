import { useQuery } from "@tanstack/react-query";



import { receptionService } from "@/services/reception";



export function useReceptionQueue(params: {

  page?: number;

  doctor?: number;

  unassigned?: boolean;

  status?: string;

  priority?: string;

} = {}) {

  const page = params.page ?? 1;

  return useQuery({

    queryKey: ["reception-queue", params],

    queryFn: () => receptionService.getQueue({ ...params, page }),

    refetchInterval: 15_000,

  });

}



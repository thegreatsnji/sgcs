import { LaboratoryTable } from "@/features/laboratory/components/LaboratoryTable";
import type { LaboratoryOrder } from "@/types/laboratory";

interface CollectionQueueProps {
  orders: LaboratoryOrder[];
  onCollect?: (order: LaboratoryOrder) => void;
}

export function CollectionQueue({ orders, onCollect }: CollectionQueueProps) {
  return (
    <LaboratoryTable orders={orders} onCollect={onCollect} />
  );
}

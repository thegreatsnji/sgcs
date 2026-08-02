import { EmptyState } from "@/design-system";
import { CollectionPatientCard } from "@/features/laboratory/components/CollectionPatientCard";
import type { LaboratoryOrder } from "@/types/laboratory";

interface CollectionQueueProps {
  orders: LaboratoryOrder[];
  onCollect?: (order: LaboratoryOrder) => void;
}

export function CollectionQueue({ orders, onCollect }: CollectionQueueProps) {
  if (orders.length === 0) {
    return (
      <EmptyState
        title="Fila de colheitas vazia"
        description="Não existem amostras aguardando colheita neste momento."
      />
    );
  }

  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
      {orders.map((order) => (
        <CollectionPatientCard key={order.id} order={order} onCollect={onCollect} />
      ))}
    </div>
  );
}

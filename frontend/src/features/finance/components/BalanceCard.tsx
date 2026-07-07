import { Card } from "@/design-system";

export function BalanceCard({ label, value }: { label: string; value: number | string }) {
  return (
    <Card title={label}>
      <p className="text-3xl font-bold text-primary-700">{value}</p>
    </Card>
  );
}

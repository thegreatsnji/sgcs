import { Card } from "@/design-system";

export function StatisticsCard({ label, value }: { label: string; value: string | number }) {
  return (
    <Card title={label}>
      <p className="text-xl font-semibold text-slate-900">{value}</p>
    </Card>
  );
}

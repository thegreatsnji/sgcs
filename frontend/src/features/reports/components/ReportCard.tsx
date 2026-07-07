import { Card } from "@/design-system";

export function ReportCard({ title, value, subtitle }: { title: string; value: string | number; subtitle?: string }) {
  return (
    <Card title={title}>
      <p className="text-2xl font-bold text-primary-700">{value}</p>
      {subtitle && <p className="mt-1 text-sm text-slate-500">{subtitle}</p>}
    </Card>
  );
}

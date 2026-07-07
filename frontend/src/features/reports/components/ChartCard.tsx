import { Card } from "@/design-system";

export function ChartCard({ title, data }: { title: string; data: Array<{ data: string; valor: number }> }) {
  if (!data.length) return null;
  const max = Math.max(...data.map((d) => d.valor), 1);
  return (
    <Card title={title}>
      <div className="flex h-32 items-end gap-1">
        {data.slice(-14).map((point) => (
          <div key={point.data} className="flex flex-1 flex-col items-center gap-1">
            <div
              className="w-full rounded-t bg-primary-500"
              style={{ height: `${Math.max(8, (point.valor / max) * 100)}%` }}
              title={`${point.data}: ${point.valor}`}
            />
            <span className="truncate text-[10px] text-slate-400">{point.data.slice(5)}</span>
          </div>
        ))}
      </div>
    </Card>
  );
}

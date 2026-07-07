import { Card } from "@/design-system";

export function SettingsCard({ title, children }: { title: string; children: React.ReactNode }) {
  return <Card title={title}>{children}</Card>;
}

export function SettingsSection({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="space-y-3">
      <h3 className="text-lg font-semibold text-slate-900">{title}</h3>
      {children}
    </section>
  );
}

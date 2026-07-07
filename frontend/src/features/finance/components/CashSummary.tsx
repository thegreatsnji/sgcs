import { Card } from "@/design-system";

export function CashSummary({ entradas, saidas, saldo }: { entradas: number; saidas: number; saldo: number }) {
  return (
    <Card title="Resumo do dia">
      <dl className="grid gap-2 text-sm sm:grid-cols-3">
        <div><dt className="text-slate-500">Entradas</dt><dd className="font-semibold text-green-700">{entradas} FCFA</dd></div>
        <div><dt className="text-slate-500">Saídas</dt><dd className="font-semibold text-red-700">{saidas} FCFA</dd></div>
        <div><dt className="text-slate-500">Saldo</dt><dd className="font-semibold">{saldo} FCFA</dd></div>
      </dl>
    </Card>
  );
}

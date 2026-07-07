import type { Notificacao } from "@/types/notifications";

import { NotificationStatusBadge } from "./NotificationStatusBadge";

interface NotificationTableProps {
  notificacoes: Notificacao[];
  onRead?: (id: number) => void;
}

export function NotificationTable({ notificacoes, onRead }: NotificationTableProps) {
  if (!notificacoes.length) {
    return <p className="text-sm text-slate-500">Sem notificações.</p>;
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full text-sm">
        <thead>
          <tr className="border-b border-slate-200 text-left text-slate-600">
            <th className="py-2 pr-4">Título</th>
            <th className="py-2 pr-4">Tipo</th>
            <th className="py-2 pr-4">Canal</th>
            <th className="py-2 pr-4">Estado</th>
            <th className="py-2 pr-4">Data</th>
            <th className="py-2">Acções</th>
          </tr>
        </thead>
        <tbody>
          {notificacoes.map((n) => (
            <tr key={n.id} className="border-b border-slate-100">
              <td className="py-2 pr-4 font-medium">{n.titulo}</td>
              <td className="py-2 pr-4">{n.tipo}</td>
              <td className="py-2 pr-4">{n.canal}</td>
              <td className="py-2 pr-4">
                <NotificationStatusBadge estado={n.estado} lida={n.lida} />
              </td>
              <td className="py-2 pr-4">{new Date(n.created_at).toLocaleString("pt-PT")}</td>
              <td className="py-2">
                {!n.lida && onRead && (
                  <button type="button" className="text-primary-600 hover:underline" onClick={() => onRead(n.id)}>
                    Marcar lida
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

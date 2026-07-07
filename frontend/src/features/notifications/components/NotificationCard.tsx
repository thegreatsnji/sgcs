import type { Notificacao } from "@/types/notifications";

import { NotificationStatusBadge } from "./NotificationStatusBadge";

interface NotificationCardProps {
  notificacao: Notificacao;
  onRead?: (id: number) => void;
}

export function NotificationCard({ notificacao, onRead }: NotificationCardProps) {
  return (
    <div className="rounded border border-slate-200 bg-white p-3 shadow-sm">
      <div className="flex items-start justify-between gap-2">
        <div>
          <p className="font-medium text-slate-900">{notificacao.titulo}</p>
          <p className="mt-1 text-sm text-slate-600">{notificacao.mensagem}</p>
          <p className="mt-2 text-xs text-slate-400">
            {new Date(notificacao.created_at).toLocaleString("pt-PT")}
          </p>
        </div>
        <NotificationStatusBadge estado={notificacao.estado} lida={notificacao.lida} />
      </div>
      {!notificacao.lida && onRead && (
        <button
          type="button"
          className="mt-2 text-sm text-primary-600 hover:underline"
          onClick={() => onRead(notificacao.id)}
        >
          Marcar como lida
        </button>
      )}
    </div>
  );
}

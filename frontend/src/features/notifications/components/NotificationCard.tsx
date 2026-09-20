import { Link } from "react-router-dom";

import type { Notificacao } from "@/types/notifications";
import { getNotificationHref } from "@/features/notifications/utils/notificationLinks";

import { NotificationStatusBadge } from "./NotificationStatusBadge";

interface NotificationCardProps {
  notificacao: Notificacao;
  onRead?: (id: number) => void;
}

export function NotificationCard({ notificacao, onRead }: NotificationCardProps) {
  const href = getNotificationHref(notificacao);

  return (
    <div className="rounded border border-border bg-surface p-3 shadow-sm">
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0">
          {href ? (
            <Link
              to={href}
              className="font-medium text-primary-700 hover:underline dark:text-primary-400"
              onClick={() => {
                if (!notificacao.lida && onRead) onRead(notificacao.id);
              }}
            >
              {notificacao.titulo}
            </Link>
          ) : (
            <p className="font-medium text-text">{notificacao.titulo}</p>
          )}
          <p className="mt-1 text-sm text-text-muted">{notificacao.mensagem}</p>
          <p className="mt-2 text-xs text-text-muted/80">
            {new Date(notificacao.created_at).toLocaleString("pt-PT")}
          </p>
        </div>
        <NotificationStatusBadge estado={notificacao.estado} lida={notificacao.lida} />
      </div>
      {!notificacao.lida && onRead && (
        <button
          type="button"
          className="mt-2 text-sm text-primary-600 hover:underline dark:text-primary-400"
          onClick={() => onRead(notificacao.id)}
        >
          Marcar como lida
        </button>
      )}
    </div>
  );
}

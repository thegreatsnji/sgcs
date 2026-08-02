import { Link } from "react-router-dom";

import type { Notificacao } from "@/types/notifications";

import { NotificationCard } from "./NotificationCard";

interface NotificationDropdownProps {
  notificacoes: Notificacao[];
  contador: number;
  onRead: (id: number) => void;
}

export function NotificationDropdown({ notificacoes, contador, onRead }: NotificationDropdownProps) {
  return (
    <div className="absolute right-0 z-50 mt-2 w-80 rounded-lg border border-border bg-surface-elevated shadow-lg">
      <div className="border-b border-border-subtle px-4 py-3">
        <p className="font-medium text-text">Notificações</p>
        <p className="text-xs text-text-muted">{contador} não lidas</p>
      </div>
      <div className="max-h-96 space-y-2 overflow-y-auto p-3">
        {notificacoes.length ? (
          notificacoes.map((n) => <NotificationCard key={n.id} notificacao={n} onRead={onRead} />)
        ) : (
          <p className="px-2 py-4 text-center text-sm text-text-muted">Sem notificações novas.</p>
        )}
      </div>
      <div className="border-t border-border-subtle p-2 text-center">
        <Link to="/notifications" className="text-sm text-primary-600 hover:underline dark:text-primary-400">
          Ver todas
        </Link>
      </div>
    </div>
  );
}

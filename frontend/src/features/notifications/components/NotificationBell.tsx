import { useState } from "react";
import { useQueryClient } from "@tanstack/react-query";

import { useUnreadNotifications } from "@/features/notifications/hooks/useNotifications";
import { notificationsService } from "@/services/notifications/notifications.service";

import { NotificationDropdown } from "./NotificationDropdown";

export function NotificationBell() {
  const [aberto, setAberto] = useState(false);
  const queryClient = useQueryClient();
  const { data } = useUnreadNotifications();

  const contador = data?.contador ?? 0;
  const notificacoes = data?.notificacoes ?? [];

  const marcarLida = async (id: number) => {
    await notificationsService.markRead(id);
    void queryClient.invalidateQueries({ queryKey: ["notifications-unread"] });
  };

  return (
    <div className="relative">
      <button
        type="button"
        className="relative rounded-full p-2 text-slate-600 hover:bg-slate-100"
        aria-label="Notificações"
        onClick={() => setAberto((v) => !v)}
      >
        <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6 6 0 10-12 0v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
          />
        </svg>
        {contador > 0 && (
          <span className="absolute -right-0.5 -top-0.5 flex h-4 min-w-4 items-center justify-center rounded-full bg-red-500 px-1 text-[10px] font-bold text-white">
            {contador > 9 ? "9+" : contador}
          </span>
        )}
      </button>
      {aberto && (
        <NotificationDropdown
          notificacoes={notificacoes}
          contador={contador}
          onRead={(id) => void marcarLida(id)}
        />
      )}
    </div>
  );
}

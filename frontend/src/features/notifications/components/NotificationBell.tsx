import { useState } from "react";
import { useQueryClient } from "@tanstack/react-query";

import { IconBell } from "@/components/icons";
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
        className="relative rounded-xl p-2.5 text-slate-500 transition hover:bg-slate-100 focus-ring"
        aria-label="Notificações"
        onClick={() => setAberto((v) => !v)}
      >
        <IconBell />
        {contador > 0 && (
          <span className="absolute -top-0.5 -right-0.5 flex h-4 min-w-4 items-center justify-center rounded-full bg-red-500 px-1 text-[10px] font-bold text-white ring-2 ring-white">
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

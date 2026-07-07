import { useQuery } from "@tanstack/react-query";

import { notificationsService } from "@/services/notifications/notifications.service";

export function useNotifications() {
  return useQuery({
    queryKey: ["notifications"],
    queryFn: notificationsService.list,
  });
}

export function useUnreadNotifications() {
  return useQuery({
    queryKey: ["notifications-unread"],
    queryFn: notificationsService.unread,
    refetchInterval: 60_000,
  });
}

export function useNotificationCenter() {
  const unread = useUnreadNotifications();
  const list = useNotifications();
  return { unread, list };
}

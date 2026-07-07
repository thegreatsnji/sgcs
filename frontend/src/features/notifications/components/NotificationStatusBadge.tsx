import { Badge } from "@/design-system";

interface NotificationStatusBadgeProps {
  estado: string;
  lida?: boolean;
}

const cores: Record<string, "default" | "success" | "warning" | "danger" | "info"> = {
  PENDENTE: "warning",
  PROCESSANDO: "info",
  ENVIADA: "info",
  ENTREGUE: "success",
  LIDA: "default",
  FALHOU: "danger",
  CANCELADA: "default",
};

export function NotificationStatusBadge({ estado, lida }: NotificationStatusBadgeProps) {
  const label = lida ? "Lida" : estado;
  return <Badge variant={cores[estado] ?? "default"}>{label}</Badge>;
}

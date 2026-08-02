import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

type ReceptionHotkeyHandlers = {
  onRefresh?: () => void;
  onCancel?: () => void;
  onPrint?: () => void;
};

/**
 * Atalhos da receção (F2–F5, Esc, Ctrl+P).
 * Activar apenas em páginas de fluxo operacional para não interferir com formulários.
 */
export function useReceptionHotkeys(enabled: boolean, handlers: ReceptionHotkeyHandlers = {}) {
  const navigate = useNavigate();

  useEffect(() => {
    if (!enabled) return;

    const handler = (e: KeyboardEvent) => {
      const target = e.target as HTMLElement | null;
      const tag = target?.tagName?.toLowerCase();
      const editing =
        tag === "input" ||
        tag === "textarea" ||
        tag === "select" ||
        target?.isContentEditable;

      if (e.key === "Escape" && handlers.onCancel) {
        e.preventDefault();
        handlers.onCancel();
        return;
      }

      if (e.ctrlKey && e.key.toLowerCase() === "p" && handlers.onPrint) {
        e.preventDefault();
        handlers.onPrint();
        return;
      }

      if (editing) return;

      switch (e.key) {
        case "F2":
          e.preventDefault();
          void navigate("/patients/new");
          break;
        case "F3":
          e.preventDefault();
          void navigate("/billing/invoices/new");
          break;
        case "F4":
          e.preventDefault();
          void navigate("/billing/payments");
          break;
        case "F5":
          e.preventDefault();
          if (handlers.onRefresh) handlers.onRefresh();
          else void navigate("/reception/queue");
          break;
        default:
          break;
      }
    };

    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [enabled, handlers, navigate]);
}

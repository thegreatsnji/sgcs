import { useEffect } from "react";

export function useKeyboardShortcuts() {
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.altKey && e.key === "p") {
        window.location.href = "/patients";
      }
      if (e.altKey && e.key === "n") {
        window.location.href = "/notifications";
      }
      if (e.altKey && e.key === "h") {
        window.location.href = "/";
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, []);
}

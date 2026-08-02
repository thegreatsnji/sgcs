import { Suspense } from "react";
import { Outlet } from "react-router-dom";

import { AppShell } from "@/components/layout/AppShell";
import { ErrorBoundary } from "@/components/ErrorBoundary";
import { LoadingState } from "@/design-system";
import { useKeyboardShortcuts } from "@/hooks/useKeyboardShortcuts";

export function AppLayout() {
  useKeyboardShortcuts();

  return (
    <AppShell>
      <ErrorBoundary>
        <Suspense fallback={<LoadingState message="A carregar módulo..." />}>
          <div className="animate-fade-in">
            <Outlet />
          </div>
        </Suspense>
      </ErrorBoundary>
    </AppShell>
  );
}

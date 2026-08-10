import { useState } from "react";

import { AppSidebar } from "./AppSidebar";
import { TopHeader } from "./TopHeader";

interface AppShellProps {
  children: React.ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <div className="flex min-h-screen bg-surface-muted">
      {/* Desktop sidebar */}
      <div className="app-chrome hidden shrink-0 lg:block">
        <AppSidebar collapsed={collapsed} onToggle={() => setCollapsed((v) => !v)} />
      </div>

      {/* Mobile drawer */}
      {mobileOpen && (
        <>
          <div
            className="app-chrome fixed inset-0 z-40 bg-slate-900/50 backdrop-blur-sm lg:hidden"
            onClick={() => setMobileOpen(false)}
            aria-hidden
          />
          <div className="app-chrome fixed inset-y-0 left-0 z-50 lg:hidden">
            <AppSidebar collapsed={false} onToggle={() => setMobileOpen(false)} />
          </div>
        </>
      )}

      <div className="flex min-w-0 flex-1 flex-col">
        <div className="app-chrome">
          <TopHeader onMenuClick={() => setMobileOpen(true)} />
        </div>
        <main className="flex-1 px-4 py-6 lg:px-8">{children}</main>
        <footer className="app-chrome flex flex-col items-center justify-between gap-2 border-t border-border bg-surface px-6 py-3 text-xs text-text-muted sm:flex-row">
          <span>© 2026 SauVida · Sistema de Gestão Clínica</span>
          <span className="inline-flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-emerald-500" aria-hidden />
            Servidores operacionais
            <span className="opacity-70">· v4.2.1</span>
          </span>
        </footer>
      </div>
    </div>
  );
}

import { memo, useState } from "react";
import { Link } from "react-router-dom";

import { IconLogout, IconMenu, IconSearch, IconUser } from "@/components/icons";
import { NotificationBell } from "@/features/notifications/components/NotificationBell";
import { useAuth } from "@/contexts/AuthContext";
import { useTheme } from "@/contexts/ThemeContext";
import { Avatar } from "@/design-system";

import { ROLE_LABELS } from "@/constants/roles";

interface TopHeaderProps {
  onMenuClick: () => void;
}

function TopHeaderComponent({ onMenuClick }: TopHeaderProps) {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const [profileOpen, setProfileOpen] = useState(false);
  const [search, setSearch] = useState("");

  return (
    <header className="sticky top-0 z-30 border-b border-border bg-surface/90 backdrop-blur-md">
      <div className="flex h-16 items-center gap-4 px-4 lg:px-6">
        <button
          type="button"
          onClick={onMenuClick}
          className="rounded-xl p-2 text-text-muted transition hover:bg-surface-muted lg:hidden focus-ring"
          aria-label="Abrir menu"
        >
          <IconMenu />
        </button>

        <div className="relative hidden max-w-xl flex-1 md:block">
          <IconSearch className="pointer-events-none absolute top-1/2 left-4 h-5 w-5 -translate-y-1/2 text-text-muted" />
          <input
            type="search"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && search.trim()) {
                window.location.href = `/patients`;
              }
            }}
            placeholder="Procurar pacientes, médicos ou exames..."
            className="h-11 w-full rounded-2xl border border-border bg-surface-muted pr-4 pl-11 text-sm text-text placeholder:text-text-muted transition focus:border-primary-300 focus:bg-surface focus:ring-2 focus:ring-primary-100 focus:outline-none dark:focus:ring-primary-900"
            aria-label="Pesquisa global"
          />
        </div>

        <div className="ml-auto flex items-center gap-2 sm:gap-3">
          <NotificationBell />

          <button
            type="button"
            onClick={toggleTheme}
            className="rounded-xl border border-border px-3 py-2 text-xs font-medium text-text-muted transition hover:bg-surface-muted focus-ring"
            aria-label={theme === "light" ? "Activar modo escuro" : "Activar modo claro"}
          >
            {theme === "light" ? "Escuro" : "Claro"}
          </button>

          {user && (
            <div className="relative">
              <button
                type="button"
                onClick={() => setProfileOpen((v) => !v)}
                className="flex items-center gap-3 rounded-2xl border border-border bg-surface py-1.5 pr-3 pl-1.5 transition hover:shadow-sm focus-ring"
                aria-expanded={profileOpen}
                aria-haspopup="menu"
              >
                <Avatar name={user.full_name} size="sm" />
                <div className="hidden text-left sm:block">
                  <p className="max-w-[140px] truncate text-sm font-semibold text-text">{user.full_name}</p>
                  <p className="text-xs text-text-muted">{ROLE_LABELS[user.role] ?? user.role}</p>
                </div>
              </button>

              {profileOpen && (
                <>
                  <div className="fixed inset-0 z-40" onClick={() => setProfileOpen(false)} aria-hidden />
                  <div
                    role="menu"
                    className="absolute right-0 z-50 mt-2 w-56 rounded-2xl border border-border bg-surface-elevated py-2 shadow-xl"
                  >
                    <Link
                      to="/admin/profile"
                      className="flex items-center gap-2 px-4 py-2.5 text-sm text-text hover:bg-surface-muted"
                      onClick={() => setProfileOpen(false)}
                    >
                      <IconUser className="h-4 w-4" />
                      Meu perfil
                    </Link>
                    <button
                      type="button"
                      role="menuitem"
                      onClick={() => {
                        setProfileOpen(false);
                        toggleTheme();
                      }}
                      className="flex w-full items-center gap-2 px-4 py-2.5 text-left text-sm text-text hover:bg-surface-muted"
                    >
                      {theme === "light" ? "Modo escuro" : "Modo claro"}
                    </button>
                    <button
                      type="button"
                      role="menuitem"
                      onClick={() => void logout()}
                      className="flex w-full items-center gap-2 px-4 py-2.5 text-left text-sm text-red-600 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-950/40"
                    >
                      <IconLogout className="h-4 w-4" />
                      Terminar sessão
                    </button>
                  </div>
                </>
              )}
            </div>
          )}
        </div>
      </div>
    </header>
  );
}

export const TopHeader = memo(TopHeaderComponent);

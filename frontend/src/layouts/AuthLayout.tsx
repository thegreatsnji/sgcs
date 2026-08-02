import { Outlet } from "react-router-dom";

import { IconLock } from "@/components/icons";

export function AuthLayout() {
  return (
    <div className="relative flex min-h-screen flex-col items-center justify-center overflow-hidden bg-[#f0f4f8] px-4 py-10 sm:px-6">
      {/* Ambient background */}
      <div className="pointer-events-none absolute inset-0" aria-hidden>
        <div className="auth-ambient absolute top-[8%] left-[12%] h-72 w-72 rounded-full bg-[#3b82f6]/20 blur-3xl" />
        <div className="auth-ambient-delayed absolute right-[10%] bottom-[12%] h-80 w-80 rounded-full bg-[#14b8a6]/15 blur-3xl" />
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,#ffffff_0%,#f0f4f8_55%,#e8edf4_100%)]" />
      </div>

      {/* Single login container */}
      <div className="auth-card relative z-10 w-full max-w-[440px] animate-slide-up overflow-hidden rounded-[28px] border border-slate-200/90 bg-white shadow-[0_8px_40px_-12px_rgba(30,64,175,0.18)]">
        {/* Brand */}
        <header className="border-b border-slate-100 px-8 pt-9 pb-7 text-center sm:px-10">
          <img
            src="/sauvida-logo.png"
            alt="SauVida — Fé que inspira, cuidado que transforma"
            className="mx-auto h-auto w-full max-w-[200px] object-contain"
            width={200}
            height={160}
          />
          <p className="mt-5 text-[10px] font-bold tracking-[0.22em] text-slate-400 uppercase">
            SGCS 2026 • Sistema Clínico
          </p>
          <p className="mx-auto mt-3 max-w-xs text-sm leading-relaxed text-slate-500 italic">
            Cuidar de vidas é a nossa missão, servir com amor é o nosso propósito.
          </p>
        </header>

        {/* Form */}
        <div className="px-8 py-8 sm:px-10 sm:py-9">
          <Outlet />
        </div>

        {/* Card footer */}
        <footer className="border-t border-slate-100 bg-slate-50/80 px-8 py-5 text-center sm:px-10">
          <p className="flex items-center justify-center gap-1.5 text-[11px] text-slate-400">
            <IconLock className="h-3.5 w-3.5 shrink-0 text-slate-400" />
            Encriptação de ponta a ponta activa
          </p>
          <p className="mt-2 text-[11px] text-slate-400">
            © 2026 SauVida. Todos os direitos reservados.
          </p>
        </footer>
      </div>
    </div>
  );
}

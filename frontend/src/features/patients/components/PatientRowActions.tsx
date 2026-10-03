import { memo, useEffect, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { usePermissions } from "@/hooks/usePermissions";
import type { PatientListItem } from "@/types/patient";

interface PatientRowActionsProps {
  patient: PatientListItem;
  onDeactivate?: (patient: PatientListItem) => void;
  onActivate?: (id: number) => void;
}

function PatientRowActionsComponent({ patient, onDeactivate, onActivate }: PatientRowActionsProps) {
  const navigate = useNavigate();
  const { hasPermission } = usePermissions();
  const [open, setOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const handleClick = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setOpen(false);
      }
    };
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") setOpen(false);
    };
    document.addEventListener("mousedown", handleClick);
    document.addEventListener("keydown", handleEscape);
    return () => {
      document.removeEventListener("mousedown", handleClick);
      document.removeEventListener("keydown", handleEscape);
    };
  }, [open]);

  const close = () => setOpen(false);

  return (
    <div className="relative" ref={menuRef}>
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="inline-flex h-9 w-9 items-center justify-center rounded-xl border border-slate-200 text-slate-500 transition hover:bg-slate-50 hover:text-slate-700 focus-ring"
        aria-label={`Acções para ${patient.full_name}`}
        aria-expanded={open}
        aria-haspopup="menu"
      >
        <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 20 20" aria-hidden>
          <path d="M10 6a2 2 0 110-4 2 2 0 010 4zm0 4a2 2 0 110-4 2 2 0 010 4zm0 4a2 2 0 110-4 2 2 0 010 4z" />
        </svg>
      </button>

      {open && (
        <div
          role="menu"
          className="absolute right-0 z-20 mt-1 w-52 rounded-2xl border border-slate-200 bg-white py-1.5 shadow-xl"
        >
          <button
            type="button"
            role="menuitem"
            className="flex w-full px-4 py-2.5 text-left text-sm text-slate-700 hover:bg-slate-50"
            onClick={() => {
              close();
              navigate(`/patients/${patient.id}`);
            }}
          >
            Ver perfil
          </button>
          {hasPermission("patients.edit") && (
            <Link
              to={`/patients/${patient.id}/edit`}
              role="menuitem"
              className="block px-4 py-2.5 text-sm text-slate-700 hover:bg-slate-50"
              onClick={close}
            >
              Editar
            </Link>
          )}
          <Link
            to={`/patients/${patient.id}/clinical`}
            role="menuitem"
            className="block px-4 py-2.5 text-sm text-slate-700 hover:bg-slate-50"
            onClick={close}
          >
            Histórico médico
          </Link>
          {hasPermission("appointments.view") && (
            <Link
              to="/appointments/list"
              role="menuitem"
              className="block px-4 py-2.5 text-sm text-slate-700 hover:bg-slate-50"
              onClick={close}
            >
              Consultas
            </Link>
          )}
          {patient.is_active
            ? hasPermission("patients.delete") &&
              onDeactivate && (
                <button
                  type="button"
                  role="menuitem"
                  className="flex w-full border-t border-slate-100 px-4 py-2.5 text-left text-sm text-red-600 hover:bg-red-50"
                  onClick={() => {
                    close();
                    onDeactivate(patient);
                  }}
                >
                  Desativar
                </button>
              )
            : hasPermission("patients.edit") &&
              onActivate && (
                <button
                  type="button"
                  role="menuitem"
                  className="flex w-full border-t border-slate-100 px-4 py-2.5 text-left text-sm text-primary-600 hover:bg-primary-50"
                  onClick={() => {
                    close();
                    onActivate(patient.id);
                  }}
                >
                  Ativar
                </button>
              )}
        </div>
      )}
    </div>
  );
}

export const PatientRowActions = memo(PatientRowActionsComponent);

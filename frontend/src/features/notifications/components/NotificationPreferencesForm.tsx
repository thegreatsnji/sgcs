import { useState } from "react";

import type { PreferenciaNotificacao } from "@/types/notifications";

import { Button } from "@/design-system";

interface NotificationPreferencesFormProps {
  preferencias: PreferenciaNotificacao;
  onSubmit: (values: Partial<PreferenciaNotificacao>) => void;
  isPending?: boolean;
}

const campos: Array<{ key: keyof PreferenciaNotificacao; label: string }> = [
  { key: "receber_email", label: "Receber e-mail" },
  { key: "receber_sms", label: "Receber SMS" },
  { key: "receber_internas", label: "Receber notificações internas" },
  { key: "receber_lembretes", label: "Receber lembretes" },
  { key: "receber_alertas_admin", label: "Receber alertas administrativos" },
];

export function NotificationPreferencesForm({
  preferencias: initial,
  onSubmit,
  isPending,
}: NotificationPreferencesFormProps) {
  const [preferencias, setPreferencias] = useState(initial);

  return (
    <form
      className="space-y-3"
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit(preferencias);
      }}
    >
      {campos.map((c) => (
        <label key={c.key} className="flex items-center gap-2 text-sm text-slate-700">
          <input
            type="checkbox"
            checked={preferencias[c.key]}
            onChange={(e) => setPreferencias((p) => ({ ...p, [c.key]: e.target.checked }))}
          />
          {c.label}
        </label>
      ))}
      <Button type="submit" variant="primary" disabled={isPending}>
        Guardar preferências
      </Button>
    </form>
  );
}

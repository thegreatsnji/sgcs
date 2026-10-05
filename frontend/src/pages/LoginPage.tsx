import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { useNavigate } from "react-router-dom";
import { isAxiosError } from "axios";

import { IconEye, IconEyeOff, IconKey, IconLogin, IconUser } from "@/components/icons";
import { useAuth } from "@/contexts/AuthContext";
import { loginSchema, type LoginFormData } from "@/utils/validation";
import { getRoleDashboardPath } from "@/utils/roleRouting";

function FieldIcon({ children }: { children: React.ReactNode }) {
  return (
    <span className="pointer-events-none absolute top-1/2 left-4 -translate-y-1/2 text-slate-400">
      {children}
    </span>
  );
}

function RememberToggle({
  checked,
  onChange,
}: {
  checked: boolean;
  onChange: (value: boolean) => void;
}) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      aria-label="Lembrar-me"
      onClick={() => onChange(!checked)}
      className={`relative h-6 w-11 shrink-0 rounded-full transition-colors focus-ring ${
        checked ? "bg-[#2563eb]" : "bg-slate-200"
      }`}
    >
      <span
        className={`absolute top-0.5 left-0.5 h-5 w-5 rounded-full bg-white shadow-sm transition-transform ${
          checked ? "translate-x-5" : "translate-x-0"
        }`}
      />
    </button>
  );
}

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [rememberMe, setRememberMe] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: "",
      password: "",
    },
  });

  const onSubmit = async (data: LoginFormData) => {
    setErrorMessage(null);
    try {
      const loggedInUser = await login(data);
      navigate(getRoleDashboardPath(loggedInUser.role), { replace: true });
    } catch (error) {
      if (isAxiosError(error)) {
        const detail = error.response?.data?.detail;
        if (typeof detail === "string") {
          setErrorMessage(
            detail === "No active account found with the given credentials."
              ? "Email ou palavra-passe incorrectos."
              : detail,
          );
        } else if (!error.response) {
          setErrorMessage("Não foi possível contactar o servidor. Tente novamente.");
        } else {
          setErrorMessage("Não foi possível iniciar sessão.");
        }
      } else {
        setErrorMessage("Ocorreu um erro inesperado. Tente novamente.");
      }
    }
  };

  const inputBase =
    "h-[52px] w-full rounded-2xl border border-slate-200 bg-white pl-12 text-[15px] text-slate-800 placeholder:text-slate-400 transition focus:border-[#2563eb] focus:ring-[3px] focus:ring-[#2563eb]/10 focus:outline-none";
  const inputError = "border-red-400 focus:border-red-500 focus:ring-red-500/10";

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6" noValidate>
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-slate-900">Acesso seguro</h2>
        <p className="mt-1.5 text-sm leading-relaxed text-slate-500">
          Inicie sessão para aceder ao sistema.
        </p>
      </div>

      {errorMessage && (
        <div
          role="alert"
          className="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
        >
          {errorMessage}
        </div>
      )}

      <div className="space-y-5">
        <div>
          <label
            htmlFor="email"
            className="mb-2 block text-[11px] font-bold tracking-[0.12em] text-slate-400 uppercase"
          >
            Utilizador ou e-mail
          </label>
          <div className="relative">
            <FieldIcon>
              <IconUser className="h-5 w-5" />
            </FieldIcon>
            <input
              id="email"
              type="email"
              autoComplete="email"
              placeholder="nome.utilizador@sauvida.gw"
              aria-invalid={!!errors.email}
              className={`${inputBase} pr-4 ${errors.email ? inputError : ""}`}
              {...register("email")}
            />
          </div>
          {errors.email && (
            <p className="mt-1.5 text-xs text-red-600" role="alert">
              {errors.email.message}
            </p>
          )}
        </div>

        <div>
          <div className="mb-2 flex items-center justify-between gap-3">
            <label
              htmlFor="password"
              className="text-[11px] font-bold tracking-[0.12em] text-slate-400 uppercase"
            >
              Palavra-passe
            </label>
            <button
              type="button"
              className="text-xs font-semibold text-[#2563eb] transition hover:text-[#1d4ed8] focus-ring rounded"
            >
              Recuperar acesso?
            </button>
          </div>
          <div className="relative">
            <FieldIcon>
              <IconKey className="h-5 w-5" />
            </FieldIcon>
            <input
              id="password"
              type={showPassword ? "text" : "password"}
              autoComplete="current-password"
              placeholder="••••••••"
              aria-invalid={!!errors.password}
              className={`${inputBase} pr-12 ${errors.password ? inputError : ""}`}
              {...register("password")}
            />
            <button
              type="button"
              onClick={() => setShowPassword((v) => !v)}
              className="absolute top-1/2 right-4 -translate-y-1/2 rounded-lg p-1 text-slate-400 transition hover:text-slate-600 focus-ring"
              aria-label={showPassword ? "Ocultar palavra-passe" : "Mostrar palavra-passe"}
            >
              {showPassword ? <IconEyeOff className="h-5 w-5" /> : <IconEye className="h-5 w-5" />}
            </button>
          </div>
          {errors.password && (
            <p className="mt-1.5 text-xs text-red-600" role="alert">
              {errors.password.message}
            </p>
          )}
        </div>
      </div>

      <div className="flex items-center gap-3">
        <RememberToggle checked={rememberMe} onChange={setRememberMe} />
        <span className="text-sm font-medium text-slate-600">Lembrar-me</span>
      </div>

      <button
        type="submit"
        disabled={isSubmitting}
        className="flex h-[52px] w-full items-center justify-center gap-2.5 rounded-full bg-primary-600 text-[15px] font-semibold text-white shadow-lg shadow-primary-600/25 transition hover:bg-primary-700 hover:shadow-primary-600/35 disabled:cursor-not-allowed disabled:opacity-60 focus-ring active:scale-[0.99]"
      >
        {isSubmitting ? (
          <>
            <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
            A autenticar...
          </>
        ) : (
          <>
            Autenticar
            <IconLogin className="h-5 w-5" />
          </>
        )}
      </button>
    </form>
  );
}

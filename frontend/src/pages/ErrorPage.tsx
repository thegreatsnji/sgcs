import { Link, useNavigate } from "react-router-dom";

import { IconLogo } from "@/components/icons";
import { Button } from "@/design-system";

export interface ErrorPageProps {
  code?: string;
  title: string;
  message: string;
  homeTo?: string;
  showBack?: boolean;
  onRetry?: () => void;
  onHome?: () => void;
  onBack?: () => void;
}

export function ErrorPageLayout({
  code,
  title,
  message,
  homeTo = "/",
  showBack = true,
  onRetry,
  onHome,
  onBack,
}: ErrorPageProps) {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-surface px-4 py-12 text-center text-text">
      <div className="mb-8 flex flex-col items-center gap-3">
        <IconLogo className="h-12 w-12 text-primary-600" />
        <p className="text-sm font-semibold tracking-wide text-primary-800 uppercase dark:text-primary-300">
          Clínica SauVida
        </p>
      </div>
      {code ? (
        <p className="font-mono text-6xl font-bold tracking-tight text-primary-700 dark:text-primary-400">{code}</p>
      ) : null}
      <h1 className="mt-4 text-2xl font-semibold text-text">{title}</h1>
      <p className="mt-3 max-w-md text-sm leading-relaxed text-text-muted">{message}</p>
      <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
        {showBack && onBack ? (
          <Button type="button" variant="outline" onClick={onBack}>
            Voltar
          </Button>
        ) : null}
        {onRetry ? (
          <Button type="button" variant="secondary" onClick={onRetry}>
            Tentar novamente
          </Button>
        ) : null}
        {onHome ? (
          <Button type="button" variant="primary" onClick={onHome}>
            Voltar ao início
          </Button>
        ) : (
          <Link to={homeTo}>
            <Button type="button" variant="primary">
              Voltar ao início
            </Button>
          </Link>
        )}
      </div>
    </div>
  );
}

export function ErrorPage(props: ErrorPageProps) {
  const navigate = useNavigate();
  return (
    <ErrorPageLayout
      {...props}
      onBack={props.onBack ?? (() => navigate(-1))}
    />
  );
}

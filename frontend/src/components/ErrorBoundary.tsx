import { Component, type ErrorInfo, type ReactNode } from "react";

import { Button } from "@/design-system";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
}

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError(): State {
    return { hasError: true };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error("Erro na interface:", error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex min-h-screen items-center justify-center bg-slate-50 p-6">
        <div className="max-w-md rounded-lg border border-red-200 bg-red-50 p-6 text-center">
          <h2 className="text-lg font-semibold text-red-800">Ocorreu um erro inesperado</h2>
          <p className="mt-2 text-sm text-red-700">Tente recarregar a página.</p>
          <Button className="mt-4" variant="primary" onClick={() => window.location.reload()}>
            Recarregar
          </Button>
        </div>
        </div>
      );
    }
    return this.props.children;
  }
}

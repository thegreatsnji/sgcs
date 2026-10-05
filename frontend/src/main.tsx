import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import App from "./App";
import "./index.css";
void import("./styles/print.css");

const rootEl = document.getElementById("root");

if (!rootEl) {
  document.body.innerHTML =
    "<p style=\"padding:2rem;font-family:system-ui\">Erro: elemento #root em falta.</p>";
} else {
  try {
    createRoot(rootEl).render(
      <StrictMode>
        <App />
      </StrictMode>,
    );
  } catch (error) {
    console.error(error);
    rootEl.innerHTML =
      "<div style=\"padding:2rem;font-family:system-ui;max-width:32rem\"><h1>SGCS</h1><p>Não foi possível iniciar a aplicação.</p><p>Abra a consola do browser (F12) ou limpe dados do site para <code>localhost:5173</code> e recarregue.</p></div>";
  }
}

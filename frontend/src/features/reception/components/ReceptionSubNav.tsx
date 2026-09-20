import { PillSubNav } from "@/components/layout/PillSubNav";
import { UI_COPY } from "@/constants/uiCopy";

/**
 * Sub-nav operacional da Receção.
 * Encaminhamentos removido — atribuição de médico fica no Atendimento passo 4 e na Fila.
 * Triagem isolada removida — usar Atendimento rápido.
 */
const links = [{ to: "/reception/queue", label: UI_COPY.nav.queue }];

export function ReceptionSubNav() {
  return <PillSubNav tabs={links} ariaLabel="Navegação da recepção" />;
}

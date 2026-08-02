export const MOTIVOS_REDUCAO = [
  { value: "DIFICULDADE_FINANCEIRA", label: "Dificuldade financeira do paciente" },
  { value: "APOIO_SOCIAL", label: "Apoio social" },
  { value: "PACIENTE_CARENCIADO", label: "Paciente carenciado" },
  { value: "DESCONTO_DIRECAO", label: "Desconto autorizado pela Direção" },
  { value: "CAMPANHA_CLINICA", label: "Campanha da clínica" },
  { value: "FUNCIONARIO_FAMILIAR", label: "Funcionário ou familiar" },
  { value: "PAGAMENTO_PARCIAL", label: "Pagamento parcial negociado" },
  { value: "CORTESIA", label: "Cortesia" },
  { value: "OUTRO", label: "Outro" },
] as const;

export function calcReducao(oficial: number, cobrado: number) {
  const diff = Math.max(0, oficial - cobrado);
  const pct = oficial > 0 ? (diff / oficial) * 100 : 0;
  return { diff, pct };
}

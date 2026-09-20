export interface ReceiptPrintData {
  recibo: {
    numero: string;
    emitido_em: string;
    segunda_via: boolean;
    tipo_documento: string;
    numero_livro: { sequencia: string; ano: string };
    data_emissao: { dia: string; mes: string; ano: string };
  };
  clinica: {
    nome: string;
    morada: string;
    telefone: string;
    email: string;
    mensagem_rodape: string;
    mostrar_ministerio: boolean;
    republica: string;
    logotipo_url: string | null;
  };
  paciente: { nome: string; numero_processo: string };
  fatura: { numero: string };
  pagamento: { valor: string; metodo: string; metodo_label: string; valor_extenso: string };
  exator: { nome: string };
  totais: Record<string, string>;
  itens: Array<{
    nome: string;
    quantidade: number;
    preco_oficial: string;
    preco_cobrado: string;
    valor_reducao: string;
    subtotal_cobrado: string;
  }>;
  referente_a: string;
  config: {
    mostrar_preco_oficial: boolean;
    mostrar_reducao: boolean;
    mostrar_saldo: boolean;
    formato: string;
  };
  textos: {
    recebi_de: string;
    importancia_de: string;
    referente_a: string;
    exator: string;
    data: string;
  };
}

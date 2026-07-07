import { z } from "zod";

export const parametroSchema = z.object({
  nome: z.string().min(1, "Nome obrigatório"),
  valor: z.string().min(1, "Valor obrigatório"),
  unidade: z.string().optional(),
  valor_minimo: z.string().optional(),
  valor_maximo: z.string().optional(),
});

export const resultadoSchema = z.object({
  pedido_laboratorial: z.number().positive(),
  observacoes: z.string().optional(),
  conclusao: z.string().optional(),
  parametros: z.array(parametroSchema).optional(),
});

export type ResultadoFormSchema = z.infer<typeof resultadoSchema>;

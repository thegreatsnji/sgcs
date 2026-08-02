import { z } from "zod";

import { isValidLocalPhone, toFullPhone } from "@/utils/phone";

export const localPhoneSchema = z
  .string()
  .min(1, "O telefone é obrigatório.")
  .refine(isValidLocalPhone, {
    message: "Introduza 7 a 9 dígitos após +245.",
  });

/** Valida dígitos locais e converte para +245XXXXXXXXX na submissão. */
export const fullPhoneSchema = localPhoneSchema.transform(toFullPhone);

export const optionalLocalPhoneSchema = z
  .string()
  .optional()
  .refine((value) => !value || isValidLocalPhone(value), {
    message: "Introduza 7 a 9 dígitos após +245.",
  });

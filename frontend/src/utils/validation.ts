import { z } from "zod";

export const loginSchema = z.object({
  email: z
    .string()
    .min(1, "O e-mail é obrigatório.")
    .email("Introduza um e-mail válido."),
  password: z
    .string()
    .min(1, "A palavra-passe é obrigatória.")
    .min(8, "A palavra-passe deve ter pelo menos 8 caracteres."),
});

export type LoginFormData = z.infer<typeof loginSchema>;

import { z } from "zod";

export const userFormSchema = z
  .object({
    email: z.string().email("E-mail inválido."),
    first_name: z.string().min(1, "O nome é obrigatório."),
    last_name: z.string().min(1, "O apelido é obrigatório."),
    phone: z.string().optional(),
    gender: z.enum(["M", "F", "O", ""]).optional(),
    birth_date: z.string().optional(),
    position: z.string().optional(),
    role: z.enum([
      "RECECIONISTA",
      "MEDICO",
      "ENFERMEIRO",
      "LABORATORIO",
      "FINANCEIRO",
      "ADMINISTRADOR",
    ]),
    password: z.string().optional(),
    password_confirm: z.string().optional(),
    is_active: z.boolean().optional(),
  })
  .refine(
    (data) => {
      if (data.password || data.password_confirm) {
        return data.password === data.password_confirm && (data.password?.length ?? 0) >= 8;
      }
      return true;
    },
    { message: "As palavras-passe devem coincidir e ter pelo menos 8 caracteres.", path: ["password_confirm"] },
  );

export type UserFormData = z.infer<typeof userFormSchema>;

export const profileFormSchema = z.object({
  first_name: z.string().min(1, "O nome é obrigatório."),
  last_name: z.string().min(1, "O apelido é obrigatório."),
  phone: z.string().optional(),
  gender: z.enum(["M", "F", "O", ""]).optional(),
  birth_date: z.string().optional(),
  position: z.string().optional(),
});

export const passwordFormSchema = z
  .object({
    old_password: z.string().min(1, "A palavra-passe atual é obrigatória."),
    new_password: z.string().min(8, "Mínimo de 8 caracteres."),
    new_password_confirm: z.string().min(8, "Confirme a palavra-passe."),
  })
  .refine((data) => data.new_password === data.new_password_confirm, {
    message: "As palavras-passe não coincidem.",
    path: ["new_password_confirm"],
  });

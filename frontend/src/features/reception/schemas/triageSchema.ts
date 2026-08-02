import { z } from "zod";

import { localPhoneSchema } from "@/schemas/phoneSchema";
import type { TriageColor } from "@/types/reception";

export const quickPatientSchema = z
  .object({
    first_name: z.string().min(1, "O nome é obrigatório."),
    last_name: z.string().min(1, "O apelido é obrigatório."),
    gender: z.enum(["M", "F", "O"], { message: "Seleccione o sexo." }),
    phone: localPhoneSchema,
    age: z.coerce.number().int().min(0, "Idade inválida.").max(120, "Idade inválida."),
    blood_type: z
      .enum(["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "DESCONHECIDO", ""])
      .optional(),
    emergency_contact_name: z.string().optional(),
    emergency_contact_phone: z.string().optional(),
  })
  .superRefine((data, ctx) => {
    if (data.age < 18) {
      if (!data.emergency_contact_name?.trim()) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          message: "Contacto de emergência obrigatório para menores.",
          path: ["emergency_contact_name"],
        });
      }
      if (!data.emergency_contact_phone?.trim()) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          message: "Telefone de emergência obrigatório para menores.",
          path: ["emergency_contact_phone"],
        });
      } else if (!localPhoneSchema.safeParse(data.emergency_contact_phone).success) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          message: "Introduza 7 a 9 dígitos após +245.",
          path: ["emergency_contact_phone"],
        });
      }
    }
  });

export const triageSchema = z.object({
  age_at_check_in: z.coerce.number().int().min(0).max(120),
  weight: z.coerce.number().positive("O peso deve ser superior a zero."),
  temperature: z.coerce
    .number()
    .min(34, "Temperatura inválida.")
    .max(43, "Temperatura inválida."),
  blood_pressure: z
    .string()
    .min(1, "Indique a pressão arterial.")
    .regex(/^\d{2,3}\/\d{2,3}$/, "Utilize o formato 120/80."),
  symptoms: z.string().min(3, "Descreva os sintomas do paciente."),
  triage_color: z.enum(["GREEN", "YELLOW", "RED"] as [TriageColor, TriageColor, TriageColor], {
    message: "Seleccione a cor de triagem.",
  }),
  notes: z.string().optional(),
});

export type QuickPatientFormData = z.infer<typeof quickPatientSchema>;
export type TriageFormData = z.infer<typeof triageSchema>;

import { z } from "zod";

import { localPhoneSchema } from "@/schemas/phoneSchema";
import type { TriageColor } from "@/types/reception";
import { getAgeFromDisplayDate, isValidDisplayDate } from "@/utils/date";

function optionalInt(min: number, max: number, fieldLabel: string) {
  const bounded = z
    .number({ message: `Indique um número válido para ${fieldLabel}.` })
    .int(`Utilize um número inteiro para ${fieldLabel}.`)
    .min(min, `${fieldLabel}: o valor mínimo é ${min}.`)
    .max(max, `${fieldLabel}: o valor máximo é ${max}.`);

  return z
    .union([z.string(), z.number(), z.undefined(), z.null()])
    .transform((val) => {
      if (val === "" || val === null || val === undefined) return undefined;
      const n = Number(val);
      return Number.isFinite(n) ? n : undefined;
    })
    .pipe(z.union([z.undefined(), bounded]).optional());
}

const birthDateFieldSchema = z
  .string()
  .min(1, "A data de nascimento é obrigatória.")
  .refine(isValidDisplayDate, { message: "Utilize o formato DD/MM/AAAA." })
  .refine((value) => {
    const age = getAgeFromDisplayDate(value);
    return age !== null && age <= 120;
  }, { message: "Data de nascimento inválida." })
  .refine((value) => {
    const match = /^(\d{2})\/(\d{2})\/(\d{4})$/.exec(value.trim());
    if (!match) return false;
    const date = new Date(Number(match[3]), Number(match[2]) - 1, Number(match[1]));
    return date <= new Date();
  }, { message: "A data de nascimento não pode ser futura." });

export const quickPatientSchema = z
  .object({
    full_name: z.string().min(1, "O nome completo é obrigatório."),
    birth_date: birthDateFieldSchema,
    gender: z.enum(["M", "F", "O"], { message: "Seleccione o sexo." }),
    phone: localPhoneSchema,
    blood_type: z
      .enum(["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "DESCONHECIDO", ""])
      .optional(),
    emergency_contact_name: z.string().optional(),
    emergency_contact_phone: z.string().optional(),
  })
  .superRefine((data, ctx) => {
    const age = getAgeFromDisplayDate(data.birth_date);
    if (age !== null && age < 18) {
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
  age_at_check_in: optionalInt(0, 120, "Idade"),
  weight: z.coerce.number().positive("O peso deve ser superior a zero."),
  height_cm: optionalInt(30, 250, "Altura"),
  race: z.string().max(80).optional(),
  temperature: z.coerce
    .number({ message: "Indique a temperatura." })
    .min(30, "Temperatura inválida (mín. 30 °C).")
    .max(43, "Temperatura inválida (máx. 43 °C)."),
  blood_pressure: z
    .string()
    .min(1, "Indique a pressão arterial.")
    .regex(/^\d{2,3}\/\d{2,3}$/, "Utilize o formato 120/80."),
  spo2: optionalInt(0, 100, "SpO₂"),
  heart_rate: optionalInt(20, 250, "FC"),
  respiratory_rate: optionalInt(5, 80, "FR"),
  symptoms: z.string().min(3, "Descreva as queixas do paciente."),
  triage_color: z.enum(["GREEN", "YELLOW", "RED"] as [TriageColor, TriageColor, TriageColor], {
    message: "Seleccione a cor de triagem.",
  }),
  visit_purpose: z.enum(["CONSULTA", "CONTROLE"]),
  notes: z.string().optional(),
});

export type QuickPatientFormData = z.infer<typeof quickPatientSchema>;
export type TriageFormData = z.output<typeof triageSchema>;

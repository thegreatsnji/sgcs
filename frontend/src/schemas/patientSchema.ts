import { z } from "zod";

import { localPhoneSchema } from "@/schemas/phoneSchema";
import { getAgeFromDisplayDate, isValidDisplayDate } from "@/utils/date";

const displayDateSchema = z
  .string()
  .min(1, "A data é obrigatória.")
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

export const emergencyContactSchema = z.object({
  name: z.string().min(1, "O nome é obrigatório."),
  phone: localPhoneSchema,
  email: z.string().email("E-mail inválido.").optional().or(z.literal("")),
  relationship: z.enum(["CONJUGE", "PAI", "MAE", "FILHO", "IRMAO", "AMIGO", "OUTRO"]),
  is_primary: z.boolean(),
});

export const patientFormSchema = z
  .object({
    first_name: z.string().min(1, "O nome é obrigatório."),
    last_name: z.string().min(1, "O apelido é obrigatório."),
    document_type: z.enum(["BI", "PASSAPORTE", "CARTAO_RESIDENTE", "OUTRO"]).optional().or(z.literal("")),
    document_number: z.string().optional(),
    birth_date: displayDateSchema,
    gender: z.enum(["M", "F", "O"], { message: "O género é obrigatório." }),
    phone: localPhoneSchema,
    email: z.string().email("E-mail inválido.").optional().or(z.literal("")),
    address_street: z.string().optional(),
    address_city: z.string().optional(),
    address_region: z.string().optional(),
    address_country: z.string().optional(),
    address_postal_code: z.string().optional(),
    nationality: z.string().optional(),
    blood_type: z
      .enum(["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "DESCONHECIDO", ""])
      .optional(),
    marital_status: z
      .enum(["SOLTEIRO", "CASADO", "DIVORCIADO", "VIUVO", "OUTRO", ""])
      .optional(),
    occupation: z.string().optional(),
    emergency_contacts: z.array(emergencyContactSchema),
  })
  .superRefine((data, ctx) => {
    const age = getAgeFromDisplayDate(data.birth_date);
    if (age !== null && age < 18 && data.emergency_contacts.length === 0) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: "Paciente menor de idade requer pelo menos um contacto de emergência.",
        path: ["emergency_contacts"],
      });
    }
  });

export type PatientFormData = z.infer<typeof patientFormSchema>;
export type EmergencyContactFormData = z.infer<typeof emergencyContactSchema>;

export const allergyFormSchema = z.object({
  allergen: z.string().min(1, "O alergénio é obrigatório."),
  severity: z.enum(["LEVE", "MODERADA", "GRAVE", "ANAFILAXIA"]),
  reaction: z.string().optional(),
  diagnosed_at: z
    .string()
    .optional()
    .refine((value) => !value || isValidDisplayDate(value), {
      message: "Utilize o formato DD/MM/AAAA.",
    }),
  notes: z.string().optional(),
});

export type AllergyFormData = z.infer<typeof allergyFormSchema>;

export const chronicDiseaseFormSchema = z.object({
  disease_name: z.string().min(1, "O nome da doença é obrigatório."),
  icd_code: z.string().optional(),
  diagnosed_at: z
    .string()
    .optional()
    .refine((value) => !value || isValidDisplayDate(value), {
      message: "Utilize o formato DD/MM/AAAA.",
    }),
  status: z.enum(["ATIVA", "CONTROLADA", "REMISSAO", "CURADA"]),
  notes: z.string().optional(),
});

export type ChronicDiseaseFormData = z.infer<typeof chronicDiseaseFormSchema>;

export const observationFormSchema = z.object({
  observation_type: z.enum(["CLINICA", "ENFERMAGEM", "ADMINISTRATIVA"]),
  content: z.string().min(1, "O conteúdo é obrigatório."),
  is_pinned: z.boolean(),
});

export type ObservationFormData = z.infer<typeof observationFormSchema>;

export const documentUploadSchema = z.object({
  file: z
    .custom<FileList | File | null>((value) => value instanceof File || value instanceof FileList, {
      message: "O ficheiro é obrigatório.",
    })
    .refine((value) => {
      if (value instanceof FileList) return value.length > 0;
      return value instanceof File;
    }, "O ficheiro é obrigatório."),
  document_type: z.enum([
    "BI",
    "PASSAPORTE",
    "CARTAO_SEGURO",
    "CONSENTIMENTO",
    "EXAME_EXTERNO",
    "DECLARACAO",
    "OUTRO",
  ]),
  title: z.string().min(1, "O título é obrigatório."),
  document_number: z.string().optional(),
  description: z.string().optional(),
  issued_at: z
    .string()
    .optional()
    .refine((value) => !value || isValidDisplayDate(value), {
      message: "Utilize o formato DD/MM/AAAA.",
    }),
  expires_at: z
    .string()
    .optional()
    .refine((value) => !value || isValidDisplayDate(value), {
      message: "Utilize o formato DD/MM/AAAA.",
    }),
});

export type DocumentUploadFormData = z.infer<typeof documentUploadSchema>;

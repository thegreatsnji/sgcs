import { z } from "zod";

export const appointmentFormSchema = z.object({
  patient_id: z.number({ required_error: "Seleccione um paciente." }).positive(),
  doctor_id: z.number().optional().nullable(),
  scheduled_at: z.string().min(1, "Indique a data e hora."),
  duration_minutes: z.number({ required_error: "Indique a duração." }).min(5).max(480),
  priority: z.enum(["LOW", "NORMAL", "HIGH", "EMERGENCY"], {
    required_error: "Seleccione a prioridade.",
  }),
  chief_complaint: z.string().optional(),
  notes: z.string().optional(),
});

export type AppointmentFormValues = z.infer<typeof appointmentFormSchema>;

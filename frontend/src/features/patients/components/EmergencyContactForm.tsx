import { useFieldArray, type Control, type FieldErrors, type UseFormRegister } from "react-hook-form";

import { Button, Input } from "@/design-system";
import { EMERGENCY_RELATIONSHIP_LABELS } from "@/constants/patients";
import type { PatientFormData } from "@/schemas/patientSchema";
import type { EmergencyRelationship } from "@/types/patient";

import { SelectField } from "./SelectField";

interface EmergencyContactFormProps {
  control: Control<PatientFormData>;
  register: UseFormRegister<PatientFormData>;
  errors: FieldErrors<PatientFormData>;
}

export function EmergencyContactForm({ control, register, errors }: EmergencyContactFormProps) {
  const { fields, append, remove } = useFieldArray({
    control,
    name: "emergency_contacts",
  });

  return (
    <div className="space-y-4">
      {fields.map((field, index) => (
        <div key={field.id} className="grid gap-4 rounded-lg border border-slate-200 p-4 md:grid-cols-2">
          <Input
            label="Nome"
            error={errors.emergency_contacts?.[index]?.name?.message}
            {...register(`emergency_contacts.${index}.name`)}
          />
          <Input
            label="Telefone"
            error={errors.emergency_contacts?.[index]?.phone?.message}
            {...register(`emergency_contacts.${index}.phone`)}
          />
          <Input
            label="E-mail"
            error={errors.emergency_contacts?.[index]?.email?.message}
            {...register(`emergency_contacts.${index}.email`)}
          />
          <SelectField
            label="Parentesco"
            error={errors.emergency_contacts?.[index]?.relationship?.message}
            options={(Object.entries(EMERGENCY_RELATIONSHIP_LABELS) as [EmergencyRelationship, string][]).map(
              ([value, label]) => ({ value, label }),
            )}
            {...register(`emergency_contacts.${index}.relationship`)}
          />
          <label className="flex items-center gap-2 text-sm text-slate-700 md:col-span-2">
            <input type="checkbox" {...register(`emergency_contacts.${index}.is_primary`)} />
            Contacto principal
          </label>
          <div className="md:col-span-2">
            <Button type="button" variant="ghost" onClick={() => remove(index)}>
              Remover contacto
            </Button>
          </div>
        </div>
      ))}
      {errors.emergency_contacts?.message && (
        <p className="text-xs text-red-600">{errors.emergency_contacts.message}</p>
      )}
      <Button
        type="button"
        variant="outline"
        onClick={() =>
          append({
            name: "",
            phone: "",
            email: "",
            relationship: "OUTRO",
            is_primary: fields.length === 0,
          })
        }
      >
        Adicionar contacto
      </Button>
    </div>
  );
}

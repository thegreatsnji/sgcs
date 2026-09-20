import type { Appointment } from "@/types/appointment";

/** Data local de hoje no formato API `YYYY-MM-DD`. */
export function localTodayIsoDate(): string {
  const today = new Date();
  const y = today.getFullYear();
  const m = String(today.getMonth() + 1).padStart(2, "0");
  const d = String(today.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}

export function isAppointmentToday(appointment: Appointment): boolean {
  const date = appointment.consultation_date || appointment.scheduled_at.slice(0, 10);
  return date === localTodayIsoDate();
}

/** Chegada física: marcação do dia ainda sem check-in na Receção. */
export function canConfirmArrival(appointment: Appointment): boolean {
  if (appointment.check_in) return false;
  if (!isAppointmentToday(appointment)) return false;
  return appointment.status === "AGENDADA" || appointment.status === "CONFIRMADA";
}

export function canConfirmBooking(appointment: Appointment): boolean {
  return appointment.status === "AGENDADA";
}

export function canCancelAppointment(appointment: Appointment): boolean {
  return (
    appointment.status === "AGENDADA" ||
    appointment.status === "CONFIRMADA" ||
    appointment.status === "EM_ESPERA"
  );
}

export function canStartConsultation(appointment: Appointment): boolean {
  return appointment.status === "CONFIRMADA" || appointment.status === "EM_ESPERA";
}

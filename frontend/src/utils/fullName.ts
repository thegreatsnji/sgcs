/** Divide nome completo para first_name / last_name (API e BD). */
export function splitFullName(fullName: string): { first_name: string; last_name: string } {
  const parts = fullName.trim().split(/\s+/).filter(Boolean);
  if (parts.length === 0) {
    return { first_name: "", last_name: "" };
  }
  if (parts.length === 1) {
    return { first_name: parts[0], last_name: parts[0] };
  }
  return { first_name: parts[0], last_name: parts.slice(1).join(" ") };
}

export function joinFullName(firstName: string, lastName: string): string {
  return `${firstName ?? ""} ${lastName ?? ""}`.trim().replace(/\s+/g, " ");
}

/** Recursos estáticos do livro de recibos (fallback quando não há logótipo no perfil). */
export const RECEIPT_BRANDING = {
  clinicLogo: "/branding/clinica-sauvida-logo.png",
  nationalEmblem: "/branding/emblema-guine-bissau.png",
  tagline: "Fé que inspira, cuidado que transforma.",
} as const;

export function resolveClinicLogoUrl(apiUrl?: string | null): string {
  if (!apiUrl) return RECEIPT_BRANDING.clinicLogo;
  if (apiUrl.startsWith("http://") || apiUrl.startsWith("https://")) return apiUrl;
  const base = import.meta.env.VITE_API_URL?.replace(/\/api\/v1\/?$/, "") ?? "";
  return `${base}${apiUrl.startsWith("/") ? apiUrl : `/${apiUrl}`}`;
}

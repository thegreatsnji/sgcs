const IMPORTED_SOURCE_MODULES = new Set([
  "MIGRACAO_EXCEL_SAUVIDA",
  "MIGRACAO",
  "IMPORTACAO",
]);

export function isImportedHistory(sourceModule?: string | null): boolean {
  if (!sourceModule) return false;
  const value = sourceModule.toUpperCase();
  return IMPORTED_SOURCE_MODULES.has(value) || value.includes("MIGRAC") || value.includes("IMPORT");
}

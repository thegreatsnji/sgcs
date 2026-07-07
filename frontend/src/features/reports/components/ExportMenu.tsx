import { Button } from "@/design-system";
import { reportsService } from "@/services/reports/reports.service";
import type { ReportFilters } from "@/types/reports";

export function ExportMenu({ tipo, filters }: { tipo: string; filters?: ReportFilters }) {
  const download = async (formato: "pdf" | "xlsx" | "csv") => {
    const { data } = await reportsService.exportReport(tipo, formato, filters);
    const blob = new Blob([data]);
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `relatorio_${tipo}.${formato === "xlsx" ? "xlsx" : formato}`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="flex flex-wrap gap-2">
      <Button variant="secondary" onClick={() => void download("pdf")}>PDF</Button>
      <Button variant="secondary" onClick={() => void download("xlsx")}>Excel</Button>
      <Button variant="secondary" onClick={() => void download("csv")}>CSV</Button>
    </div>
  );
}

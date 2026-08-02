import type { ReactNode } from "react";

export interface TableColumn<T> {
  key: string;
  header: string;
  render?: (row: T) => ReactNode;
}

export interface TableProps<T> {
  columns: TableColumn<T>[];
  data: T[];
  emptyMessage?: string;
  getRowKey: (row: T) => string | number;
}

export function Table<T>({
  columns,
  data,
  emptyMessage = "Sem registos.",
  getRowKey,
}: TableProps<T>) {
  if (data.length === 0) {
    return (
      <div className="rounded-lg border border-dashed border-border p-8 text-center text-sm text-text-muted">
        {emptyMessage}
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-border">
      <table className="min-w-full divide-y divide-border text-sm">
        <thead className="bg-surface-muted">
          <tr>
            {columns.map((column) => (
              <th
                key={column.key}
                className="px-4 py-3 text-left font-semibold text-text-muted"
              >
                {column.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-border-subtle bg-surface">
          {data.map((row) => (
            <tr key={getRowKey(row)} className="hover:bg-surface-muted">
              {columns.map((column) => (
                <td key={column.key} className="px-4 py-3 text-text">
                  {column.render
                    ? column.render(row)
                    : String((row as Record<string, unknown>)[column.key] ?? "")}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

"use client"

import { clsx } from "clsx"

export interface Column<T = any> {
  key: string
  label: string
  width?: string
  align?: "left" | "center" | "right"
  render?: (row: T, index: number) => React.ReactNode
}

interface DataTableProps<T = any> {
  columns: Column<T>[]
  data: T[]
  className?: string
  compact?: boolean
  onRowClick?: (row: T) => void
}

export function DataTable<T extends Record<string, any> = Record<string, any>>({
  columns,
  data,
  className,
  compact = false,
  onRowClick,
}: DataTableProps<T>) {
  return (
    <div className={clsx("overflow-x-auto", className)}>
      <table className="w-full">
        <thead>
          <tr className="border-b border-white/[0.06]">
            {columns.map((col) => (
              <th
                key={col.key}
                className={clsx(
                  "text-[11px] font-semibold uppercase tracking-wider text-gray-500",
                  compact ? "px-3 py-2" : "px-4 py-3",
                  col.align === "right" && "text-right",
                  col.align === "center" && "text-center",
                  (!col.align || col.align === "left") && "text-left"
                )}
                style={col.width ? { width: col.width } : undefined}
              >
                {col.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, rowIdx) => (
            <tr
              key={rowIdx}
              onClick={() => onRowClick?.(row)}
              className={clsx(
                "border-b border-white/[0.03] transition-colors",
                onRowClick && "cursor-pointer hover:bg-white/[0.03]"
              )}
            >
              {columns.map((col) => (
                <td
                  key={col.key}
                  className={clsx(
                    "text-sm",
                    compact ? "px-3 py-2" : "px-4 py-3",
                    col.align === "right" && "text-right",
                    col.align === "center" && "text-center"
                  )}
                >
                  {col.render ? col.render(row, rowIdx) : String(row[col.key] ?? "")}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

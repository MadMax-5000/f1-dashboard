"use client"

import { clsx } from "clsx"
import type { LucideIcon } from "lucide-react"

interface StatCardProps {
  label: string
  value: string | number
  subtitle?: string
  icon: LucideIcon
  trend?: { value: number; label: string }
}

export function StatCard({ label, value, subtitle, icon: Icon, trend }: StatCardProps) {
  return (
    <div className="group rounded-[14px] border border-f1-border bg-f1-surface p-6 transition-colors duration-200 hover:border-f1-accent/30">
      <div className="flex items-start justify-between mb-4">
        <span className="label-type uppercase text-gray-500">{label}</span>
        <div
          className="rounded-[10px] border border-f1-border bg-f1-darker p-2 transition-colors duration-200 group-hover:border-f1-accent/30"
        >
          <Icon size={16} className="text-f1-accent" />
        </div>
      </div>
      <div className="display-type text-[2.25rem] font-semibold leading-none text-white mb-1">{value}</div>
      {subtitle && <div className="text-sm text-gray-500">{subtitle}</div>}
      {trend && (
        <div className="mt-3 flex items-center gap-1.5">
          <span
            className={clsx(
              "label-type font-semibold",
              trend.value >= 0 ? "text-f1-accent" : "text-white"
            )}
          >
            {trend.value >= 0 ? "+" : ""}
            {trend.value}%
          </span>
          <span className="text-xs text-gray-600">{trend.label}</span>
        </div>
      )}
    </div>
  )
}

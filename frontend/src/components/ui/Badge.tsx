import { clsx } from "clsx"

interface BadgeProps {
  children: React.ReactNode
  variant?: "default" | "team" | "tyre" | "outline"
  teamName?: string
  teamColor?: string
  className?: string
}

export function Badge({ children, variant = "default", teamName, teamColor, className }: BadgeProps) {
  return (
    <span
      className={clsx(
        "inline-flex items-center gap-1.5 rounded-full px-3 py-1 label-type font-semibold uppercase",
        variant === "default" && "bg-f1-gray text-gray-300",
        variant === "outline" && "border border-white/[0.08] text-gray-400 bg-white/[0.03]",
        variant === "team" && "border border-white/[0.08] bg-white/[0.04] text-gray-300",
        variant === "tyre" && "bg-f1-accent text-black font-bold",
        className
      )}
    >
      {variant === "team" && teamName && (
        <span
          className="w-2 h-2 rounded-full shrink-0"
          style={{ backgroundColor: teamColor || "var(--color-f1-accent)" }}
        />
      )}
      {children}
    </span>
  )
}

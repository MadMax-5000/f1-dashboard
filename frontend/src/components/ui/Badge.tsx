import { clsx } from "clsx"

interface BadgeProps {
  children: React.ReactNode
  variant?: "default" | "team" | "tyre" | "outline"
  teamName?: string
  className?: string
}

export function Badge({ children, variant = "default", teamName, className }: BadgeProps) {
  return (
    <span
      className={clsx(
        "inline-flex items-center gap-1 rounded-full px-2.5 py-1 label-type font-semibold uppercase",
        variant === "default" && "bg-f1-gray text-gray-300",
        variant === "outline" && "border border-f1-border text-gray-400",
        variant === "team" && "border border-f1-border bg-f1-darker text-gray-300",
        variant === "tyre" && "bg-f1-accent text-black font-bold",
        className
      )}
    >
      {variant === "team" && teamName && (
        <span className="w-1.5 h-1.5 rounded-full bg-f1-accent" />
      )}
      {children}
    </span>
  )
}

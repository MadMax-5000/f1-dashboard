import { clsx } from "clsx"

interface CardProps {
  children: React.ReactNode
  className?: string
  hover?: boolean
  padding?: "sm" | "md" | "lg"
  onClick?: () => void
  glowColor?: string
}

export function Card({ children, className, hover = false, padding = "md", onClick, glowColor }: CardProps) {
  return (
    <div
      onClick={onClick}
      className={clsx(
        "group rounded-2xl border border-f1-border bg-f1-surface shadow-[0_2px_12px_rgba(0,0,0,0.25)]",
        hover && "card-glow transition-all duration-300 hover:border-white/[0.12] hover:bg-[#1a1d21] cursor-pointer",
        padding === "sm" && "p-4",
        padding === "md" && "p-5",
        padding === "lg" && "p-8",
        className
      )}
      style={glowColor ? { "--card-glow-color": `${glowColor}20` } as React.CSSProperties : undefined}
    >
      {children}
    </div>
  )
}

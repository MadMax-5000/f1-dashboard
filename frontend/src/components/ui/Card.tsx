import { clsx } from "clsx"

interface CardProps {
  children: React.ReactNode
  className?: string
  hover?: boolean
  padding?: "sm" | "md" | "lg"
  onClick?: () => void
}

export function Card({ children, className, hover = false, padding = "md", onClick }: CardProps) {
  return (
    <div
      onClick={onClick}
      className={clsx(
        "rounded-[14px] border border-f1-border bg-f1-surface",
        hover && "transition-all duration-200 hover:border-f1-accent/30 hover:bg-[#1b1e22] cursor-pointer",
        padding === "sm" && "p-3",
        padding === "md" && "p-6",
        padding === "lg" && "p-8",
        className
      )}
    >
      {children}
    </div>
  )
}

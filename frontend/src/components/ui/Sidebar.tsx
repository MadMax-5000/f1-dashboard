"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { clsx } from "clsx"
import {
  LayoutDashboard,
  Flag,
  Users,
  MapPin,
  Trophy,
  ChevronLeft,
  ChevronRight,
} from "lucide-react"
import { useState } from "react"

const NAV_ITEMS = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/races", label: "Races", icon: Flag },
  { href: "/drivers", label: "Drivers", icon: Users },
  { href: "/circuits", label: "Circuits", icon: MapPin },
  { href: "/standings", label: "Standings", icon: Trophy },
]

export function Sidebar() {
  const pathname = usePathname()
  const [collapsed, setCollapsed] = useState(false)

  return (
    <aside
      className={clsx(
        "h-screen sticky top-0 flex flex-col border-r border-f1-border bg-f1-surface transition-all duration-300 shrink-0",
        collapsed ? "w-[68px]" : "w-[220px]"
      )}
    >
      {/* Logo */}
      <Link href="/" className="flex items-center gap-2.5 px-5 h-16 border-b border-f1-border shrink-0">
        <div className="w-2.5 h-2.5 rounded-full bg-f1-accent animate-pulse-glow shrink-0" />
        {!collapsed && (
          <span className="display-type text-[1rem] font-semibold text-white whitespace-nowrap">
            F1 <span className="text-gray-400">Twin</span>
          </span>
        )}
      </Link>

      {/* Nav items */}
      <nav className="flex-1 py-4 px-3 space-y-1">
        {NAV_ITEMS.map((item) => {
          const isActive = pathname.startsWith(item.href)
          return (
            <Link
              key={item.href}
              href={item.href}
              className={clsx(
                "flex items-center gap-3 rounded-[10px] px-3 py-2.5 text-sm font-medium transition-all duration-200",
                isActive
                  ? "bg-f1-darker text-f1-accent accent-ring"
                  : "text-gray-500 hover:text-white hover:bg-f1-darker"
              )}
            >
              <item.icon size={18} className="shrink-0" />
              {!collapsed && <span>{item.label}</span>}
            </Link>
          )
        })}
      </nav>

      {/* Collapse toggle */}
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="flex items-center justify-center h-12 border-t border-f1-border text-gray-600 hover:text-white transition-colors"
      >
        {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
      </button>
    </aside>
  )
}

"use client"

import { Sidebar } from "@/components/ui/Sidebar"

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen bg-f1-darker text-f1-light">
      <Sidebar />
      <main className="flex-1 overflow-y-auto bg-f1-darker">
        {children}
      </main>
    </div>
  )
}

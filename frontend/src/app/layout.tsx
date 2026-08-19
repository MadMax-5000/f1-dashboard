import type { Metadata } from "next"
import "./globals.css"

export const metadata: Metadata = {
  title: "F1 Digital Twin",
  description: "AI-Powered Race Reconstruction, Strategy Analysis & Interactive Replay",
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen antialiased">
        {children}
      </body>
    </html>
  )
}

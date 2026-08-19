"use client"

import Link from "next/link"
import { motion } from "framer-motion"
import { ArrowLeft, Trophy, Zap, Target } from "lucide-react"
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts"
import { Card } from "@/components/ui/Card"
import { Badge } from "@/components/ui/Badge"
import { TEAM_COLORS } from "@/lib/mock-data"
import type { ApiDriver, ApiRace } from "@/lib/f1-api"

interface Props {
  driver: ApiDriver
  races: ApiRace[]
  headshotUrl?: string
}

export default function DriverDetailClient({ driver, races, headshotUrl }: Props) {
  const color = TEAM_COLORS[driver.team] || "#888"

  const raceResults = races.map((race) => {
    const result = race.results.find((r) => r.driverId === driver.id)
    return {
      race: `R${race.round}`,
      position: result?.position ?? 20,
      points: result?.points ?? 0,
    }
  })

  const stats = [
    { label: "Championship", value: `P${driver.position}`, icon: Trophy, color: "#ffd700" },
    { label: "Points", value: driver.points, icon: Target, color },
    { label: "Wins", value: driver.wins, icon: Zap, color: "#00ff87" },
  ]

  return (
    <div className="p-8 space-y-8">
      <Link href="/drivers" className="inline-flex items-center gap-1.5 text-xs text-gray-500 hover:text-white transition-colors">
        <ArrowLeft size={14} /> Back to Drivers
      </Link>

      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="flex items-end gap-6">
        {headshotUrl ? (
          <img
            src={headshotUrl}
            alt={`${driver.firstName} ${driver.lastName}`}
            className="w-20 h-20 rounded-2xl object-cover bg-white/[0.05]"
          />
        ) : (
          <div
            className="w-20 h-20 rounded-2xl flex items-center justify-center text-3xl font-black"
            style={{ backgroundColor: `${color}20`, color }}
          >
            {driver.number}
          </div>
        )}
        <div>
          <div className="text-sm text-gray-500">{driver.firstName}</div>
          <h1 className="text-4xl font-black text-white">{driver.lastName}</h1>
          <div className="flex items-center gap-3 mt-1">
            <Badge variant="team" teamName={driver.team}>{driver.team}</Badge>
            <span className="text-xs text-gray-600">{driver.nationality}</span>
          </div>
        </div>
      </motion.div>

      <div className="grid grid-cols-3 gap-4">
        {stats.map((s) => (
          <Card key={s.label} padding="sm" className="text-center">
            <s.icon size={18} className="mx-auto mb-2" style={{ color: s.color }} />
            <div className="text-2xl font-bold text-white">{s.value}</div>
            <div className="text-[10px] text-gray-600 uppercase">{s.label}</div>
          </Card>
        ))}
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        <Card>
          <h2 className="text-sm font-semibold text-white mb-4">Race Finishing Positions</h2>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={raceResults} margin={{ top: 5, right: 10, bottom: 5, left: 10 }}>
              <XAxis dataKey="race" tick={{ fill: "#666", fontSize: 10 }} axisLine={false} tickLine={false} />
              <YAxis reversed domain={[1, 20]} tick={{ fill: "#666", fontSize: 10 }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={{ backgroundColor: "#1a1a2e", border: "1px solid #ffffff10", borderRadius: 12, fontSize: 12 }} />
              <Bar dataKey="position" fill={color} radius={[4, 4, 0, 0]} barSize={20} fillOpacity={0.8} />
            </BarChart>
          </ResponsiveContainer>
        </Card>

        <Card>
          <h2 className="text-sm font-semibold text-white mb-4">Points per Race</h2>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={raceResults} margin={{ top: 5, right: 10, bottom: 5, left: 10 }}>
              <XAxis dataKey="race" tick={{ fill: "#666", fontSize: 10 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: "#666", fontSize: 10 }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={{ backgroundColor: "#1a1a2e", border: "1px solid #ffffff10", borderRadius: 12, fontSize: 12 }} />
              <Bar dataKey="points" fill="#00ff87" radius={[4, 4, 0, 0]} barSize={20} fillOpacity={0.8} />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </div>

      <Card>
        <h2 className="text-sm font-semibold text-white mb-4">Season Results</h2>
        <div className="space-y-2">
          {races.map((race) => {
            const result = race.results.find((r) => r.driverId === driver.id)
            if (!result) return null
            return (
              <Link
                key={race.id}
                href={`/races/${race.round}`}
                className="flex items-center justify-between p-3 rounded-xl hover:bg-white/[0.03] transition-colors"
              >
                <div className="flex items-center gap-3">
                  <span className={`text-sm font-bold w-8 text-center ${result.position <= 3 ? "text-f1-accent" : "text-gray-500"}`}>
                    P{result.position}
                  </span>
                  <div>
                    <div className="text-sm text-white">{race.name}</div>
                    <div className="text-xs text-gray-600">{race.date}</div>
                  </div>
                </div>
                <div className="text-sm font-bold text-white">{result.points} pts</div>
              </Link>
            )
          })}
        </div>
      </Card>
    </div>
  )
}

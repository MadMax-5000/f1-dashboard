"use client"

import Link from "next/link"
import { motion } from "framer-motion"
import { ArrowLeft, Clock, Flag } from "lucide-react"
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts"
import { Card } from "@/components/ui/Card"
import { Badge } from "@/components/ui/Badge"
import { DataTable } from "@/components/ui/DataTable"
import { generateLapTimes, TEAM_COLORS } from "@/lib/mock-data"
import type { ApiRace } from "@/lib/f1-api"

interface Props {
  race: ApiRace
}

export default function RaceDetailClient({ race }: Props) {
  const lapData = generateLapTimes(race.laps || 57).map((t, i) => ({ lap: i + 1, time: +t.toFixed(3) }))

  const columns = [
    {
      key: "position",
      label: "Pos",
      width: "50px",
      render: (row: (typeof race.results)[0]) => (
        <span className={`font-bold ${row.position <= 3 ? "text-f1-accent" : "text-gray-400"}`}>
          {row.positionText}
        </span>
      ),
    },
    {
      key: "driver",
      label: "Driver",
      render: (row: (typeof race.results)[0]) => (
        <div className="flex items-center gap-2">
          <span
            className="w-1 h-6 rounded-full"
            style={{ backgroundColor: TEAM_COLORS[row.team] || "#888" }}
          />
          <div>
            <div className="text-sm font-medium text-white">{row.driverFirstName} {row.driverLastName}</div>
            <div className="text-[11px] text-gray-600">{row.team}</div>
          </div>
        </div>
      ),
    },
    {
      key: "grid",
      label: "Grid",
      render: (row: (typeof race.results)[0]) => (
        <span className="font-mono text-sm text-gray-400">{row.grid}</span>
      ),
    },
    {
      key: "time",
      label: "Time",
      render: (row: (typeof race.results)[0]) => (
        <span className="font-mono text-sm text-gray-300">{row.time}</span>
      ),
    },
    {
      key: "points",
      label: "Pts",
      align: "right" as const,
      render: (row: (typeof race.results)[0]) => (
        <span className="font-bold text-white">{row.points}</span>
      ),
    },
    {
      key: "fl",
      label: "",
      width: "40px",
      render: (row: (typeof race.results)[0]) =>
        row.fastestLap ? <span className="text-purple-400 text-xs font-bold">FL</span> : null,
    },
  ]

  return (
    <div className="p-8 space-y-8">
      <div>
        <Link href="/races" className="inline-flex items-center gap-1.5 text-xs text-gray-500 hover:text-white transition-colors mb-4">
          <ArrowLeft size={14} /> Back to Races
        </Link>
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
          <div className="flex items-center gap-3 mb-1">
            <span className="text-xs font-bold text-f1-red">ROUND {race.round}</span>
            {race.isSprint && <Badge variant="outline">Sprint Weekend</Badge>}
          </div>
          <h1 className="text-3xl font-bold text-white mb-1">{race.name}</h1>
          <p className="text-sm text-gray-500">
            {race.circuitName} &middot; {race.city}, {race.country} &middot; {race.date}
          </p>
        </motion.div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        <Card padding="sm" className="text-center">
          <Flag size={16} className="mx-auto mb-1 text-gray-600" />
          <div className="text-xl font-bold text-white">{race.laps}</div>
          <div className="text-[10px] text-gray-600 uppercase">Laps</div>
        </Card>
        <Card padding="sm" className="text-center">
          <div className="text-xl font-bold text-white">{race.results.filter((r) => r.status === "Finished").length}</div>
          <div className="text-[10px] text-gray-600 uppercase">Finished</div>
        </Card>
        <Card padding="sm" className="text-center">
          <Clock size={16} className="mx-auto mb-1 text-f1-blue" />
          <div className="text-xl font-bold text-white">{race.results[0]?.time || "—"}</div>
          <div className="text-[10px] text-gray-600 uppercase">Winner Time</div>
        </Card>
      </div>

      <div className="grid lg:grid-cols-5 gap-6">
        <Card className="lg:col-span-3">
          <h2 className="text-sm font-semibold text-white mb-4">Race Results</h2>
          <DataTable columns={columns} data={race.results} compact />
        </Card>

        <Card className="lg:col-span-2">
          <h2 className="text-sm font-semibold text-white mb-4">Lap Times (Simulated)</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={lapData} margin={{ top: 5, right: 10, bottom: 5, left: 10 }}>
              <XAxis dataKey="lap" tick={{ fill: "#666", fontSize: 10 }} axisLine={false} tickLine={false} />
              <YAxis domain={["auto", "auto"]} tick={{ fill: "#666", fontSize: 10 }} axisLine={false} tickLine={false} />
              <Tooltip
                contentStyle={{ backgroundColor: "#1a1a2e", border: "1px solid #ffffff10", borderRadius: 12, fontSize: 12 }}
                labelFormatter={(v) => `Lap ${v}`}
              />
              <Line type="monotone" dataKey="time" stroke="#e10600" strokeWidth={1.5} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </Card>
      </div>
    </div>
  )
}

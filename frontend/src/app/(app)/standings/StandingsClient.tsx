"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { clsx } from "clsx"
import Link from "next/link"
import { Card } from "@/components/ui/Card"
import { Badge } from "@/components/ui/Badge"
import { TEAM_COLORS } from "@/lib/mock-data"
import type { ApiDriver, ApiConstructor } from "@/lib/f1-api"

type Tab = "drivers" | "constructors"

interface Props {
  drivers: ApiDriver[]
  constructors: ApiConstructor[]
  season: string
}

export default function StandingsClient({ drivers, constructors, season }: Props) {
  const [tab, setTab] = useState<Tab>("drivers")

  const maxDriverPts = drivers[0]?.points || 1
  const maxConstructorPts = Math.max(...constructors.map((c) => c.points), 1)

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white mb-1">Championship Standings</h1>
        <p className="text-sm text-gray-500">{season} Season</p>
      </div>

      <div className="flex gap-1 mb-8 bg-white/[0.03] p-1 rounded-xl w-fit">
        {(["drivers", "constructors"] as Tab[]).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={clsx(
              "px-5 py-2 rounded-lg text-sm font-medium transition-all duration-200 capitalize",
              tab === t ? "bg-f1-red text-white" : "text-gray-500 hover:text-white"
            )}
          >
            {t}
          </button>
        ))}
      </div>

      {tab === "drivers" && (
        <Card>
          <div className="space-y-1">
            {drivers.map((driver, i) => {
              const color = TEAM_COLORS[driver.team] || "#888"
              const pct = (driver.points / maxDriverPts) * 100
              return (
                <motion.div
                  key={driver.id}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.02 }}
                >
                  <Link
                    href={`/drivers/${driver.id}`}
                    className="flex items-center gap-4 p-3 rounded-xl hover:bg-white/[0.03] transition-colors group"
                  >
                    <span className={clsx("w-8 text-center text-sm font-bold", i < 3 ? "text-f1-accent" : "text-gray-600")}>
                      {driver.position}
                    </span>
                    <span className="w-1 h-8 rounded-full shrink-0" style={{ backgroundColor: color }} />
                    <div className="min-w-[140px]">
                      <div className="text-sm font-semibold text-white group-hover:text-f1-red transition-colors">
                        {driver.firstName} {driver.lastName}
                      </div>
                      <div className="text-[11px] text-gray-600">{driver.team}</div>
                    </div>
                    <div className="flex-1 flex items-center gap-3">
                      <div className="flex-1 h-2 rounded-full bg-white/[0.04] overflow-hidden">
                        <motion.div
                          className="h-full rounded-full"
                          style={{ backgroundColor: color }}
                          initial={{ width: 0 }}
                          animate={{ width: `${pct}%` }}
                          transition={{ delay: i * 0.03, duration: 0.6 }}
                        />
                      </div>
                      <span className="text-sm font-bold text-white w-12 text-right">{driver.points}</span>
                    </div>
                    <div className="flex gap-4 text-xs text-gray-600 shrink-0">
                      <span>{driver.wins}W</span>
                    </div>
                  </Link>
                </motion.div>
              )
            })}
          </div>
        </Card>
      )}

      {tab === "constructors" && (
        <Card>
          <div className="space-y-1">
            {constructors.map((team, i) => {
              const color = TEAM_COLORS[team.name] || "#888"
              const pct = (team.points / maxConstructorPts) * 100
              return (
                <motion.div
                  key={team.id}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.03 }}
                  className="flex items-center gap-4 p-3 rounded-xl hover:bg-white/[0.03] transition-colors"
                >
                  <span className={clsx("w-8 text-center text-sm font-bold", i < 3 ? "text-f1-accent" : "text-gray-600")}>
                    {team.position}
                  </span>
                  <span className="w-1 h-8 rounded-full shrink-0" style={{ backgroundColor: color }} />
                  <div className="min-w-[140px]">
                    <div className="text-sm font-semibold text-white">{team.name}</div>
                    <div className="text-[11px] text-gray-600">{team.wins} wins</div>
                  </div>
                  <div className="flex-1 flex items-center gap-3">
                    <div className="flex-1 h-2 rounded-full bg-white/[0.04] overflow-hidden">
                      <motion.div
                        className="h-full rounded-full"
                        style={{ backgroundColor: color }}
                        initial={{ width: 0 }}
                        animate={{ width: `${pct}%` }}
                        transition={{ delay: i * 0.04, duration: 0.6 }}
                      />
                    </div>
                    <span className="text-sm font-bold text-white w-12 text-right">{team.points}</span>
                  </div>
                </motion.div>
              )
            })}
          </div>
        </Card>
      )}
    </div>
  )
}

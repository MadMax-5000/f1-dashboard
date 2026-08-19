"use client"

import Link from "next/link"
import { motion } from "framer-motion"
import { Card } from "@/components/ui/Card"
import { Badge } from "@/components/ui/Badge"
import { TEAM_COLORS } from "@/lib/mock-data"
import type { ApiDriver } from "@/lib/f1-api"

interface Props {
  drivers: ApiDriver[]
  headshots: Record<string, string>
  season: string
}

export default function DriversClient({ drivers, headshots, season }: Props) {
  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white mb-1">Drivers</h1>
        <p className="text-sm text-gray-500">{season} Season &middot; {drivers.length} Drivers</p>
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
        {drivers.map((driver, i) => {
          const color = TEAM_COLORS[driver.team] || "#888"
          return (
            <motion.div
              key={driver.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.03, duration: 0.4 }}
            >
              <Link href={`/drivers/${driver.id}`}>
                <Card hover className="relative overflow-hidden">
                  <div className="absolute top-0 left-0 right-0 h-1 rounded-t-2xl" style={{ backgroundColor: color }} />
                  <div className="flex items-start justify-between mt-2 mb-3">
                    <div className="flex items-center gap-3">
                      {headshots[driver.code] ? (
                        <img
                          src={headshots[driver.code]}
                          alt={`${driver.firstName} ${driver.lastName}`}
                          className="w-14 h-14 rounded-full object-cover bg-white/[0.05]"
                        />
                      ) : (
                        <div
                          className="w-14 h-14 rounded-full flex items-center justify-center text-lg font-black"
                          style={{ backgroundColor: `${color}20`, color }}
                        >
                          {driver.number}
                        </div>
                      )}
                      <div>
                        <div className="text-xs text-gray-500">{driver.firstName}</div>
                        <div className="text-xl font-bold text-white">{driver.lastName}</div>
                      </div>
                    </div>
                    <div className="text-3xl font-black" style={{ color: `${color}40` }}>
                      {driver.number}
                    </div>
                  </div>

                  <Badge variant="team" teamName={driver.team} className="mb-4">
                    {driver.team}
                  </Badge>

                  <div className="grid grid-cols-2 gap-2 pt-3 border-t border-white/[0.06]">
                    <div className="text-center">
                      <div className="text-lg font-bold text-white">{driver.points}</div>
                      <div className="text-[10px] text-gray-600 uppercase">Points</div>
                    </div>
                    <div className="text-center">
                      <div className="text-lg font-bold text-f1-accent">{driver.wins}</div>
                      <div className="text-[10px] text-gray-600 uppercase">Wins</div>
                    </div>
                  </div>

                  <div className="flex items-center justify-between mt-3 pt-3 border-t border-white/[0.06]">
                    <span className="text-xs text-gray-600">{driver.nationality}</span>
                    <span className="text-xs font-bold" style={{ color }}>
                      P{driver.position}
                    </span>
                  </div>
                </Card>
              </Link>
            </motion.div>
          )
        })}
      </div>
    </div>
  )
}

"use client"

import Link from "next/link"
import { motion } from "framer-motion"
import { Calendar, Flag } from "lucide-react"
import { Card } from "@/components/ui/Card"
import { Badge } from "@/components/ui/Badge"
import type { ApiRace } from "@/lib/f1-api"

interface Props {
  races: ApiRace[]
  season: string
}

export default function RacesClient({ races, season }: Props) {
  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white mb-1">Race Calendar</h1>
        <p className="text-sm text-gray-500">{season} Season &middot; {races.length} Grands Prix</p>
      </div>

      <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-5">
        {races.map((race, i) => {
          const hasResults = race.results.length > 0
          const winner = race.results[0]
          return (
            <motion.div
              key={race.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05, duration: 0.4 }}
            >
              <Link href={`/races/${race.round}`}>
                <Card hover className="h-full">
                  <div className="flex items-center justify-between mb-4">
                    <span className="text-xs font-bold text-f1-red">ROUND {race.round}</span>
                    {race.isSprint && <Badge variant="outline">Sprint</Badge>}
                    {!hasResults && <Badge variant="outline">Upcoming</Badge>}
                  </div>

                  <h3 className="text-lg font-bold text-white mb-1">{race.name}</h3>
                  <div className="text-xs text-gray-500 mb-4">
                    {race.city}, {race.country}
                  </div>

                  {hasResults && (
                    <div className="grid grid-cols-2 gap-3 mb-4">
                      <div className="text-center">
                        <div className="text-lg font-bold text-white">{race.laps}</div>
                        <div className="text-[10px] text-gray-600 uppercase">Laps</div>
                      </div>
                      <div className="text-center">
                        <div className="text-lg font-bold text-white">{race.results.length}</div>
                        <div className="text-[10px] text-gray-600 uppercase">Classified</div>
                      </div>
                    </div>
                  )}

                  <div className="flex items-center justify-between pt-3 border-t border-white/[0.06]">
                    <div className="flex items-center gap-2">
                      <Calendar size={12} className="text-gray-600" />
                      <span className="text-xs text-gray-400">{race.date}</span>
                    </div>
                    {hasResults && winner && (
                      <div className="flex items-center gap-1.5">
                        <span className="text-[10px] text-gray-600 uppercase">Winner:</span>
                        <Badge variant="team" teamName={winner.team}>
                          {winner.driverCode}
                        </Badge>
                      </div>
                    )}
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

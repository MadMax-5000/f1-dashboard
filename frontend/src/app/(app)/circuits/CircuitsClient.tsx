"use client"

import { motion } from "framer-motion"
import { MapPin } from "lucide-react"
import { Card } from "@/components/ui/Card"
import { Badge } from "@/components/ui/Badge"
import { getCircuitSvgUrl } from "@/lib/f1-api"
import type { ApiRace } from "@/lib/f1-api"

interface Props {
  races: ApiRace[]
}

export default function CircuitsClient({ races }: Props) {
  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white mb-1">Circuits</h1>
        <p className="text-sm text-gray-500">{races.length} Tracks on the {races[0]?.date?.slice(0, 4)} Calendar</p>
      </div>

      <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-5">
        {races.map((race, i) => {
          const hasResults = race.results.length > 0
          const svgUrl = getCircuitSvgUrl(race.circuitId)
          return (
            <motion.div
              key={race.circuitId}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05, duration: 0.4 }}
            >
              <Card hover>
                {svgUrl && (
                  <div className="flex items-center justify-center mb-4 p-4 rounded-xl bg-white/[0.02]">
                    <img
                      src={svgUrl}
                      alt={`${race.circuitName} layout`}
                      className="h-24 w-auto opacity-60"
                    />
                  </div>
                )}
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h3 className="text-lg font-bold text-white">{race.circuitName}</h3>
                    <div className="flex items-center gap-1.5 mt-1">
                      <MapPin size={12} className="text-gray-600" />
                      <span className="text-xs text-gray-500">{race.city}, {race.country}</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2 my-3">
                  <Badge variant="outline">Round {race.round}</Badge>
                  {race.isSprint && <Badge variant="outline">Sprint</Badge>}
                  {!hasResults && <Badge variant="outline">Upcoming</Badge>}
                </div>

                <div className="grid grid-cols-2 gap-3 my-4">
                  <div className="text-center p-2 rounded-xl bg-white/[0.03]">
                    <div className="text-sm font-bold text-white">{race.name}</div>
                    <div className="text-[9px] text-gray-600 uppercase">Grand Prix</div>
                  </div>
                  <div className="text-center p-2 rounded-xl bg-white/[0.03]">
                    <div className="text-sm font-bold text-white">{race.laps || "—"}</div>
                    <div className="text-[9px] text-gray-600 uppercase">Race Laps</div>
                  </div>
                </div>

                <div className="pt-3 border-t border-white/[0.06]">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-gray-600">Race Date</span>
                    <span className="font-mono text-gray-300">{race.date}</span>
                  </div>
                  {hasResults && race.results[0] && (
                    <div className="flex items-center justify-between text-xs mt-1">
                      <span className="text-gray-600">Winner</span>
                      <span className="text-gray-400">{race.results[0].driverFirstName} {race.results[0].driverLastName}</span>
                    </div>
                  )}
                </div>
              </Card>
            </motion.div>
          )
        })}
      </div>
    </div>
  )
}

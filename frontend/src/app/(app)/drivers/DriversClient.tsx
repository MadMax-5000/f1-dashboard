"use client"

import { DriverStanding } from "@/lib/f1-api"

const TEAM_COLORS: Record<string, string> = {
  red_bull: "bg-blue-600",
  mclaren: "bg-orange-500",
  ferrari: "bg-red-600",
  mercedes: "bg-teal-500",
  aston_martin: "bg-green-700",
  alpine: "bg-pink-600",
  rb: "bg-blue-400",
  haas: "bg-gray-400",
  sauber: "bg-green-500",
  williams: "bg-blue-700",
  kick_sauber: "bg-green-500",
}

export default function DriversClient({ drivers }: { drivers: DriverStanding[] }) {
  if (!drivers.length) {
    return (
      <div className="p-8">
        <h1 className="text-2xl font-bold text-white mb-4">Drivers</h1>
        <p className="text-gray-400">No driver data available.</p>
      </div>
    )
  }

  return (
    <div className="p-8 space-y-6">
      <h1 className="text-2xl font-bold text-white">Driver Standings</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {drivers.map((d) => (
          <div
            key={d.driverId}
            className="bg-f1-surface border border-f1-border rounded-xl p-4 flex items-center gap-4"
          >
            <div className="text-2xl font-bold text-gray-600 w-10">
              {d.position}
            </div>
            <div className="flex-1">
              <p className="text-white font-semibold">{d.driver}</p>
              <div className="flex items-center gap-2 mt-1">
                <div className={`w-2 h-2 rounded-full ${TEAM_COLORS[d.constructorId] || "bg-gray-500"}`} />
                <span className="text-gray-400 text-sm">{d.constructor}</span>
              </div>
            </div>
            <div className="text-right">
              <p className="text-white font-bold text-lg">{d.points}</p>
              <p className="text-gray-500 text-xs">{d.wins} wins</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

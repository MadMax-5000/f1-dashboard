"use client"

import { RaceResult } from "@/lib/f1-api"

export default function RacesClient({ races }: { races: RaceResult[] }) {
  if (!races.length) {
    return (
      <div className="p-8">
        <h1 className="text-2xl font-bold text-white mb-4">Race Results</h1>
        <p className="text-gray-400">No race data available.</p>
      </div>
    )
  }

  return (
    <div className="p-8 space-y-6">
      <h1 className="text-2xl font-bold text-white">Race Results — {races[0]?.season}</h1>

      <div className="space-y-4">
        {races.map((race) => (
          <div key={race.round} className="bg-f1-surface border border-f1-border rounded-xl p-5">
            <div className="flex items-center justify-between mb-3">
              <div>
                <h2 className="text-white font-semibold">{race.raceName}</h2>
                <p className="text-gray-500 text-sm">Round {race.round} • {race.date}</p>
              </div>
              <span className="text-gray-500 text-sm">{race.circuitName}</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
              {race.results.slice(0, 3).map((r, i) => (
                <div
                  key={r.driverId}
                  className="flex items-center gap-3 bg-f1-darker rounded-lg px-3 py-2"
                >
                  <span className={`text-sm font-bold ${
                    i === 0 ? "text-yellow-400" : i === 1 ? "text-gray-300" : "text-amber-600"
                  }`}>
                    P{r.position}
                  </span>
                  <span className="text-white text-sm">{r.driver}</span>
                  <span className="text-gray-500 text-xs ml-auto">{r.constructor}</span>
                </div>
              ))}
            </div>

            <details className="mt-3">
              <summary className="text-gray-500 text-xs cursor-pointer hover:text-gray-300">
                Full classification
              </summary>
              <div className="mt-2 space-y-1">
                {race.results.map((r) => (
                  <div key={r.driverId} className="flex items-center gap-3 text-sm px-2 py-1">
                    <span className="text-gray-500 w-8">P{r.position}</span>
                    <span className="text-white flex-1">{r.driver}</span>
                    <span className="text-gray-500">{r.constructor}</span>
                    <span className="text-gray-400 w-12 text-right">{r.points} pts</span>
                    <span className="text-gray-600 w-20 text-right text-xs">{r.status}</span>
                  </div>
                ))}
              </div>
            </details>
          </div>
        ))}
      </div>
    </div>
  )
}

"use client"

import { useState } from "react"
import { fetchChampionshipPredictions } from "@/lib/predictions-api"

interface ChampResult {
  driver_id: string
  win_probability: number
  expected_final_points: number
  points_std: number
  current_points: number
}

const DEFAULT_STANDINGS: Record<string, number> = {
  verstappen: 300,
  norris: 260,
  leclerc: 220,
  piastri: 195,
  hamilton: 170,
  russell: 160,
  sainz: 140,
  alonso: 60,
}

const DEFAULT_WIN_PROBS: Record<string, number> = {
  verstappen: 0.30,
  norris: 0.25,
  leclerc: 0.18,
  piastri: 0.12,
  hamilton: 0.06,
  russell: 0.04,
  sainz: 0.03,
  alonso: 0.02,
}

export default function ChampionshipClient() {
  const [results, setResults] = useState<ChampResult[] | null>(null)
  const [loading, setLoading] = useState(false)
  const [remainingRaces, setRemainingRaces] = useState(5)

  const runSimulation = async () => {
    setLoading(true)
    const data = await fetchChampionshipPredictions({
      current_standings: DEFAULT_STANDINGS,
      remaining_races: remainingRaces,
      win_probabilities: DEFAULT_WIN_PROBS,
    })
    if (data?.probabilities) {
      setResults(data.probabilities)
    }
    setLoading(false)
  }

  return (
    <div className="p-8 space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white">Championship Predictions</h1>
        <p className="text-gray-400 mt-1">
          Monte Carlo simulation of remaining season (10,000 simulations)
        </p>
      </div>

      <div className="bg-f1-surface border border-f1-border rounded-xl p-6">
        <div className="flex items-center gap-4 mb-6">
          <label className="text-gray-400 text-sm">Remaining races:</label>
          <input
            type="number"
            min={1}
            max={24}
            value={remainingRaces}
            onChange={(e) => setRemainingRaces(Number(e.target.value))}
            className="bg-f1-darker border border-f1-border rounded-lg px-3 py-1.5 text-white w-20"
          />
          <button
            onClick={runSimulation}
            disabled={loading}
            className="bg-red-600 hover:bg-red-500 text-white px-4 py-1.5 rounded-lg font-medium transition-colors disabled:opacity-50"
          >
            {loading ? "Simulating..." : "Run Simulation"}
          </button>
        </div>

        {results && (
          <div className="space-y-4">
            {results.map((r, i) => (
              <div key={r.driver_id} className="flex items-center gap-4">
                <span className="text-gray-500 text-sm w-6">{i + 1}</span>
                <span className="text-white font-medium w-28 capitalize">
                  {r.driver_id.replace("_", " ")}
                </span>
                <div className="flex-1 h-8 bg-f1-darker rounded-full overflow-hidden relative">
                  <div
                    className="h-full bg-gradient-to-r from-blue-600 to-blue-400 rounded-full"
                    style={{ width: `${r.win_probability * 100}%` }}
                  />
                </div>
                <span className="text-white font-mono text-sm w-16 text-right">
                  {(r.win_probability * 100).toFixed(1)}%
                </span>
                <span className="text-gray-500 text-xs w-24 text-right">
                  {r.expected_final_points.toFixed(0)} pts (±{r.points_std.toFixed(0)})
                </span>
              </div>
            ))}
          </div>
        )}

        {!results && !loading && (
          <p className="text-gray-500 text-sm">
            Click "Run Simulation" to predict championship outcomes.
          </p>
        )}
      </div>
    </div>
  )
}

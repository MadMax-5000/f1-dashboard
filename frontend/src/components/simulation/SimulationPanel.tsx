"use client"

import { useF1Store } from "@/lib/store"

const SCENARIOS = [
  { id: "pit_one_lap_earlier", name: "Pit One Lap Earlier", icon: "⏪" },
  { id: "no_safety_car", name: "Remove Safety Car", icon: "🚗" },
  { id: "different_tyre_compound", name: "Different Tyre", icon: "🛞" },
  { id: "no_drs", name: "No DRS", icon: "⚡" },
  { id: "reduced_pit_time", name: "Faster Pit Stop", icon: "⏱" },
  { id: "different_weather", name: "Weather Change", icon: "🌧" },
]

export function SimulationPanel() {
  const twinState = useF1Store((s) => s.twinState)
  const isReplaying = useF1Store((s) => s.isReplaying)
  const counterfactuals = useF1Store((s) => s.counterfactuals)
  const focusedDriver = useF1Store((s) => s.focusedDriver)

  return (
    <div className="p-3 h-full flex flex-col">
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs text-gray-500 uppercase tracking-wider">Simulation & Strategy</span>
        <span className="text-xs text-gray-600">
          {twinState ? `Lap ${twinState.lapNumber}` : "No session"}
        </span>
      </div>

      {focusedDriver && (
        <>
          {/* Counterfactual Scenarios */}
          <div className="mb-3">
            <span className="text-[10px] text-gray-600 uppercase mb-2 block">
              What-If Scenarios
            </span>
            <div className="grid grid-cols-2 gap-1.5">
              {SCENARIOS.map((s) => (
                <button
                  key={s.id}
                  className="flex items-center gap-1.5 bg-f1-gray/30 hover:bg-f1-gray/50 
                             border border-f1-gray/50 px-2 py-1.5 rounded text-xs 
                             text-gray-400 hover:text-white transition-all"
                >
                  <span>{s.icon}</span>
                  <span>{s.name}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Strategy Recommendation */}
          <div className="bg-f1-gray/20 border border-f1-gray/50 rounded p-2 mb-2">
            <span className="text-[10px] text-gray-600 uppercase mb-1 block">
              Strategy Recommendation
            </span>
            <div className="flex items-center justify-between text-xs">
              <span className="text-gray-400">Pace:</span>
              <span className="text-f1-accent font-bold">NORMAL</span>
            </div>
            <div className="flex items-center justify-between text-xs mt-1">
              <span className="text-gray-400">Tyres:</span>
              <span className="text-f1-blue font-bold">STAY OUT</span>
            </div>
            <div className="flex items-center justify-between text-xs mt-1">
              <span className="text-gray-400">ERS:</span>
              <span className="text-f1-warning font-bold">BALANCED</span>
            </div>
            <div className="mt-2 pt-2 border-t border-f1-gray/50">
              <div className="flex items-center justify-between text-[10px]">
                <span className="text-gray-600">Pit Window:</span>
                <span className="text-gray-400">Laps 12-18</span>
              </div>
            </div>
          </div>

          {/* Counterfactual Results */}
          {counterfactuals.length > 0 && (
            <div className="flex-1 overflow-y-auto">
              <span className="text-[10px] text-gray-600 uppercase mb-1 block">
                Results
              </span>
              {counterfactuals.map((cf, idx) => (
                <div
                  key={idx}
                  className="bg-f1-gray/20 border border-f1-gray/50 rounded p-2 mb-1.5 text-xs"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-gray-400">{cf.scenarioId}</span>
                    <span className="text-f1-accent">
                      {cf.delta?.delta_position < 0
                        ? `${Math.abs(cf.delta.delta_position)} positions gained`
                        : cf.delta?.delta_position > 0
                          ? `${cf.delta.delta_position} positions lost`
                          : "No change"}
                    </span>
                  </div>
                  <div className="text-[10px] text-gray-600 mt-1">
                    Confidence: {(cf.confidence * 100).toFixed(0)}%
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {!focusedDriver && (
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="text-2xl mb-2">🎯</div>
            <p className="text-xs text-gray-600">
              Select a driver on the track to run simulations
            </p>
          </div>
        </div>
      )}
    </div>
  )
}

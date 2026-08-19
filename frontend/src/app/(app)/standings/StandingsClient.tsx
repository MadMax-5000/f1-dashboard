"use client"

import { useState } from "react"
import { DriverStanding, ConstructorStanding } from "@/lib/f1-api"

interface Props {
  drivers: DriverStanding[]
  constructors: ConstructorStanding[]
}

export default function StandingsClient({ drivers, constructors }: Props) {
  const [tab, setTab] = useState<"drivers" | "constructors">("drivers")

  return (
    <div className="p-8 space-y-6">
      <h1 className="text-2xl font-bold text-white">Championship Standings</h1>

      <div className="flex gap-2">
        <button
          onClick={() => setTab("drivers")}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            tab === "drivers" ? "bg-red-600 text-white" : "bg-f1-surface text-gray-400 hover:text-white"
          }`}
        >
          Drivers
        </button>
        <button
          onClick={() => setTab("constructors")}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            tab === "constructors" ? "bg-red-600 text-white" : "bg-f1-surface text-gray-400 hover:text-white"
          }`}
        >
          Constructors
        </button>
      </div>

      {tab === "drivers" && (
        <div className="bg-f1-surface border border-f1-border rounded-xl overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="border-b border-f1-border text-gray-500 text-xs uppercase">
                <th className="px-4 py-3 text-left">Pos</th>
                <th className="px-4 py-3 text-left">Driver</th>
                <th className="px-4 py-3 text-left">Team</th>
                <th className="px-4 py-3 text-right">Points</th>
                <th className="px-4 py-3 text-right">Wins</th>
              </tr>
            </thead>
            <tbody>
              {drivers.map((d) => (
                <tr key={d.driverId} className="border-b border-f1-border/50 hover:bg-f1-darker/50">
                  <td className="px-4 py-3 text-gray-400 font-mono">{d.position}</td>
                  <td className="px-4 py-3 text-white font-medium">{d.driver}</td>
                  <td className="px-4 py-3 text-gray-400">{d.constructor}</td>
                  <td className="px-4 py-3 text-white text-right font-bold">{d.points}</td>
                  <td className="px-4 py-3 text-gray-400 text-right">{d.wins}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {tab === "constructors" && (
        <div className="bg-f1-surface border border-f1-border rounded-xl overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="border-b border-f1-border text-gray-500 text-xs uppercase">
                <th className="px-4 py-3 text-left">Pos</th>
                <th className="px-4 py-3 text-left">Constructor</th>
                <th className="px-4 py-3 text-right">Points</th>
                <th className="px-4 py-3 text-right">Wins</th>
              </tr>
            </thead>
            <tbody>
              {constructors.map((c) => (
                <tr key={c.constructorId} className="border-b border-f1-border/50 hover:bg-f1-darker/50">
                  <td className="px-4 py-3 text-gray-400 font-mono">{c.position}</td>
                  <td className="px-4 py-3 text-white font-medium">{c.constructor}</td>
                  <td className="px-4 py-3 text-white text-right font-bold">{c.points}</td>
                  <td className="px-4 py-3 text-gray-400 text-right">{c.wins}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

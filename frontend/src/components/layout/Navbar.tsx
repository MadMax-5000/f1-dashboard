"use client"

import { useF1Store } from "@/lib/store"

export function Navbar() {
  const toggleDarkMode = useF1Store((s) => s.toggleDarkMode)
  const isReplaying = useF1Store((s) => s.isReplaying)
  const replaySpeed = useF1Store((s) => s.replaySpeed)
  const setReplaySpeed = useF1Store((s) => s.setReplaySpeed)

  return (
    <nav className="h-14 bg-f1-dark border-b border-f1-gray flex items-center justify-between px-6 shrink-0">
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-f1-red rounded-full animate-pulse-glow" />
          <span className="text-lg font-bold tracking-wider text-white">
            F1<span className="text-f1-red">DigitalTwin</span>
          </span>
        </div>
        <span className="text-xs text-gray-500 border-l border-f1-gray pl-4">
          AI-Powered Race Intelligence
        </span>
      </div>

      <div className="flex items-center gap-4">
        {isReplaying && (
          <div className="flex items-center gap-3 bg-f1-gray/50 px-3 py-1 rounded">
            <span className="text-xs text-f1-accent animate-pulse">● REC</span>
            <span className="text-xs text-gray-400">Speed:</span>
            <button
              onClick={() => setReplaySpeed(Math.max(0.1, replaySpeed - 0.5))}
              className="text-xs text-gray-400 hover:text-white px-1"
            >
              -
            </button>
            <span className="text-xs text-white w-8 text-center">
              {replaySpeed.toFixed(1)}x
            </span>
            <button
              onClick={() => setReplaySpeed(Math.min(10, replaySpeed + 0.5))}
              className="text-xs text-gray-400 hover:text-white px-1"
            >
              +
            </button>
          </div>
        )}
        <button
          onClick={toggleDarkMode}
          className="text-xs text-gray-400 hover:text-white transition-colors"
        >
          {useF1Store.getState().darkMode ? "☀" : "☾"}
        </button>
      </div>
    </nav>
  )
}

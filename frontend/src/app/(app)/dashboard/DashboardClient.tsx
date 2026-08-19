"use client"

interface Prediction {
  driver_id: string
  win_probability: number
  podium_probability: number
}

interface Props {
  predictions: {
    race_winner: Prediction[]
    qualifying: { driver_id: string; predicted_quali_position: number }[]
  } | null
}

export default function DashboardClient({ predictions }: Props) {
  if (!predictions) {
    return (
      <div className="p-8">
        <h1 className="text-2xl font-bold text-white mb-4">Race Predictions</h1>
        <div className="bg-f1-surface border border-f1-border rounded-xl p-6">
          <p className="text-gray-400">
            No predictions available. Run the data pipeline and train models first.
          </p>
          <pre className="mt-4 text-sm text-gray-500 bg-f1-darker p-4 rounded-lg">
{`# Collect data
python -m src.data.collect

# Build features
python -m src.features.engineering

# Train models
python -m src.models.race_winner
python -m src.models.qualifying

# Start API
uvicorn src.api.app:app --reload`}
          </pre>
        </div>
      </div>
    )
  }

  const winners = predictions.race_winner.slice(0, 10)
  const maxProb = winners[0]?.win_probability || 1

  return (
    <div className="p-8 space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white">Next Race Predictions</h1>
        <p className="text-gray-400 mt-1">Win & podium probabilities from ML models</p>
      </div>

      {/* Win Probabilities */}
      <div className="bg-f1-surface border border-f1-border rounded-xl p-6">
        <h2 className="text-lg font-semibold text-white mb-4">Win Probability</h2>
        <div className="space-y-3">
          {winners.map((p, i) => (
            <div key={p.driver_id} className="flex items-center gap-4">
              <span className="text-gray-500 text-sm w-6">{i + 1}</span>
              <span className="text-white font-medium w-32 capitalize">
                {p.driver_id.replace("_", " ")}
              </span>
              <div className="flex-1 h-6 bg-f1-darker rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-red-600 to-red-400 rounded-full transition-all"
                  style={{ width: `${(p.win_probability / maxProb) * 100}%` }}
                />
              </div>
              <span className="text-white font-mono text-sm w-16 text-right">
                {(p.win_probability * 100).toFixed(1)}%
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Podium Probabilities */}
      <div className="bg-f1-surface border border-f1-border rounded-xl p-6">
        <h2 className="text-lg font-semibold text-white mb-4">Podium Probability</h2>
        <div className="space-y-3">
          {winners.map((p, i) => (
            <div key={p.driver_id} className="flex items-center gap-4">
              <span className="text-gray-500 text-sm w-6">{i + 1}</span>
              <span className="text-white font-medium w-32 capitalize">
                {p.driver_id.replace("_", " ")}
              </span>
              <div className="flex-1 h-6 bg-f1-darker rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-amber-600 to-amber-400 rounded-full transition-all"
                  style={{ width: `${p.podium_probability * 100}%` }}
                />
              </div>
              <span className="text-white font-mono text-sm w-16 text-right">
                {(p.podium_probability * 100).toFixed(1)}%
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Qualifying Predictions */}
      {predictions.qualifying && (
        <div className="bg-f1-surface border border-f1-border rounded-xl p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Predicted Qualifying Order</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {predictions.qualifying.slice(0, 20).map((q, i) => (
              <div
                key={q.driver_id}
                className="flex items-center gap-2 bg-f1-darker rounded-lg px-3 py-2"
              >
                <span className="text-gray-500 text-xs font-mono">P{i + 1}</span>
                <span className="text-white text-sm capitalize">
                  {q.driver_id.replace("_", " ")}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

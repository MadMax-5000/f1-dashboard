"use client"

interface Props {
  metrics: {
    race_winner?: {
      win_log_loss: number
      win_accuracy: number
      podium_log_loss: number
      podium_accuracy: number
      test_size: number
    }
    qualifying?: {
      mae: number
      rmse: number
      test_size: number
    }
  } | null
}

function MetricCard({ label, value, unit }: { label: string; value: number | string; unit?: string }) {
  return (
    <div className="bg-f1-darker rounded-lg p-4">
      <p className="text-gray-500 text-xs uppercase tracking-wide">{label}</p>
      <p className="text-white text-2xl font-bold mt-1">
        {typeof value === "number" ? value.toFixed(3) : value}
        {unit && <span className="text-gray-500 text-sm ml-1">{unit}</span>}
      </p>
    </div>
  )
}

export default function ModelsClient({ metrics }: Props) {
  if (!metrics) {
    return (
      <div className="p-8">
        <h1 className="text-2xl font-bold text-white mb-4">Model Performance</h1>
        <div className="bg-f1-surface border border-f1-border rounded-xl p-6">
          <p className="text-gray-400">No model metrics available. Train models first.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="p-8 space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white">Model Performance</h1>
        <p className="text-gray-400 mt-1">Accuracy and calibration metrics for trained models</p>
      </div>

      {metrics.race_winner && (
        <div className="bg-f1-surface border border-f1-border rounded-xl p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Race Winner Model (XGBoost)</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <MetricCard label="Win Accuracy" value={metrics.race_winner.win_accuracy} />
            <MetricCard label="Win Log Loss" value={metrics.race_winner.win_log_loss} />
            <MetricCard label="Podium Accuracy" value={metrics.race_winner.podium_accuracy} />
            <MetricCard label="Podium Log Loss" value={metrics.race_winner.podium_log_loss} />
          </div>
          <p className="text-gray-500 text-xs mt-4">
            Evaluated on {metrics.race_winner.test_size} race entries (time-series split)
          </p>
        </div>
      )}

      {metrics.qualifying && (
        <div className="bg-f1-surface border border-f1-border rounded-xl p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Qualifying Model (LightGBM)</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            <MetricCard label="MAE" value={metrics.qualifying.mae} unit="positions" />
            <MetricCard label="RMSE" value={metrics.qualifying.rmse} unit="positions" />
            <MetricCard label="Test Size" value={metrics.qualifying.test_size} />
          </div>
        </div>
      )}
    </div>
  )
}

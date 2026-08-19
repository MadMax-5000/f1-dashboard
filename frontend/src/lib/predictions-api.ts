const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"

export async function fetchNextRacePredictions() {
  try {
    const res = await fetch(`${API_BASE}/predictions/next-race`, {
      next: { revalidate: 60 },
      cache: "no-store",
    })
    if (!res.ok) return null
    return res.json()
  } catch {
    return null
  }
}

export async function fetchChampionshipPredictions(body: {
  current_standings: Record<string, number>
  remaining_races: number
  win_probabilities: Record<string, number>
}) {
  try {
    const res = await fetch(`${API_BASE}/predictions/championship`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    })
    if (!res.ok) return null
    return res.json()
  } catch {
    return null
  }
}

export async function fetchModelPerformance() {
  try {
    const res = await fetch(`${API_BASE}/models/performance`, {
      cache: "no-store",
    })
    if (!res.ok) return null
    return res.json()
  } catch {
    return null
  }
}

export async function fetchStrategy(body: {
  circuit_id: string
  total_laps: number
  grid_position: number
}) {
  const res = await fetch(`${API_BASE}/predictions/strategy`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  })
  if (!res.ok) return null
  return res.json()
}

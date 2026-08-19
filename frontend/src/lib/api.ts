const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"

class F1ApiClient {
  private base: string

  constructor(base: string) {
    this.base = base
  }

  private async request<T>(path: string, init?: RequestInit): Promise<T> {
    const res = await fetch(`${this.base}${path}`, {
      headers: { "Content-Type": "application/json", ...init?.headers },
      ...init,
    })
    if (!res.ok) {
      throw new Error(`API error: ${res.status} ${res.statusText}`)
    }
    return res.json()
  }

  // Races
  async listRaces(season?: number) {
    const params = season ? `?season=${season}` : ""
    return this.request<unknown[]>(`/races${params}`)
  }

  async getRace(raceId: string) {
    return this.request<unknown>(`/races/${raceId}`)
  }

  async getRaceSessions(raceId: string) {
    return this.request<unknown>(`/races/${raceId}/sessions`)
  }

  async getRaceResults(raceId: string) {
    return this.request<unknown>(`/races/${raceId}/results`)
  }

  // Sessions
  async getSession(sessionId: string) {
    return this.request<unknown>(`/sessions/${sessionId}`)
  }

  async getSessionLaps(sessionId: string, driverId?: string) {
    const params = driverId ? `?driver_id=${driverId}` : ""
    return this.request<unknown>(`/sessions/${sessionId}/laps${params}`)
  }

  async getSessionEvents(sessionId: string) {
    return this.request<unknown>(`/sessions/${sessionId}/events`)
  }

  // Telemetry
  async getTelemetry(sessionId: string, driverId?: string) {
    const params = driverId ? `?driver_id=${driverId}` : ""
    return this.request<unknown>(`/telemetry/${sessionId}${params}`)
  }

  async compareTelemetry(sessionId: string, driverA: string, driverB: string) {
    return this.request<unknown>(
      `/telemetry/${sessionId}/compare?driver_a=${driverA}&driver_b=${driverB}`
    )
  }

  // Drivers
  async listDrivers() {
    return this.request<unknown[]>("/drivers")
  }

  async getDriver(driverId: string) {
    return this.request<unknown>(`/drivers/${driverId}`)
  }

  // Circuits
  async listCircuits() {
    return this.request<unknown[]>("/circuits")
  }

  async getCircuit(circuitId: string) {
    return this.request<unknown>(`/circuits/${circuitId}`)
  }

  async getCircuitMap(circuitId: string) {
    return this.request<unknown>(`/circuits/${circuitId}/map`)
  }

  // Digital Twin
  async reconstructSession(sessionId: string) {
    return this.request<unknown>(`/twin/reconstruct/${sessionId}`, {
      method: "POST",
    })
  }

  async getTwinState(sessionId: string, tick?: number) {
    const params = tick ? `?tick=${tick}` : ""
    return this.request<unknown>(`/twin/state/${sessionId}${params}`)
  }

  // Counterfactual
  async listCounterfactualScenarios() {
    return this.request<unknown>("/counterfactual/scenarios")
  }

  async runCounterfactual(data: {
    sessionId: string
    driverId: string
    scenarioType: string
    intervention: Record<string, unknown>
  }) {
    return this.request<unknown>("/counterfactual/simulate", {
      method: "POST",
      body: JSON.stringify(data),
    })
  }

  // Strategy
  async getStrategies(sessionId: string) {
    return this.request<unknown>(`/strategy/${sessionId}`)
  }

  async optimizeStrategy(data: {
    sessionId: string
    driverId: string
    objective?: string
  }) {
    return this.request<unknown>("/strategy/optimize", {
      method: "POST",
      body: JSON.stringify(data),
    })
  }

  // Predictions
  async predictLapTime(data: {
    sessionId: string
    driverId: string
    lapNumber: number
  }) {
    return this.request<unknown>("/predictions/predict", {
      method: "POST",
      body: JSON.stringify(data),
    })
  }

  // Simulation
  async runSimulation(data: {
    sessionId: string
    simulationType: string
    numRuns: number
  }) {
    return this.request<unknown>("/simulation/run", {
      method: "POST",
      body: JSON.stringify(data),
    })
  }

  async getSimulationResults(simulationId: string) {
    return this.request<unknown>(`/simulation/run/${simulationId}/results`)
  }
}

export const api = new F1ApiClient(API_BASE)

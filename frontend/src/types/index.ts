export interface Driver {
  id: string
  driverNumber: number
  broadcastName: string
  fullName: string
  tla: string
  teamName: string
  headshotUrl?: string
}

export interface Team {
  id: string
  name: string
  fullName: string
  nationality?: string
}

export interface Circuit {
  id: string
  name: string
  country?: string
  lengthKm?: number
  turns?: number
}

export interface Race {
  id: string
  season: number
  round: number
  name: string
  circuit: Circuit
  scheduledLaps?: number
  isSprintWeekend: boolean
}

export interface Session {
  id: string
  raceId: string
  sessionType: SessionType
  startTime?: string
  endTime?: string
  totalLaps?: number
}

export type SessionType =
  | "practice_1" | "practice_2" | "practice_3"
  | "qualifying" | "qualifying_1" | "qualifying_2" | "qualifying_3"
  | "sprint_qualifying" | "sprint"
  | "race"

export interface Lap {
  sessionId: string
  driverId: string
  lapNumber: number
  position?: number
  timeSeconds?: number
  sector1Time?: number
  sector2Time?: number
  sector3Time?: number
  speedTrapKmh?: number
  isPitLap: boolean
  tyreCompound?: string
  tyreAgeLaps?: number
}

export interface TelemetryPoint {
  sessionId: string
  driverId: string
  lapNumber: number
  timestamp: string
  distance: number
  speed?: number
  rpm?: number
  gear?: number
  throttle?: number
  brake?: number
  drs?: boolean
  x?: number
  y?: number
  z?: number
}

export interface RaceState {
  sessionId: string
  tick: number
  lapNumber: number
  phase: string
  order: string[]
  drivers: Record<string, DriverRaceState>
  safetyCar: boolean
  weather: WeatherState
}

export interface DriverRaceState {
  position: number
  lap: number
  speed: number
  x: number
  y: number
  tyre: string
  tyreAge: number
  fuel: number
  deltaLeader: number
}

export interface WeatherState {
  airTemp: number
  trackTemp: number
  rainfall: boolean
}

export interface RaceEvent {
  id: string
  sessionId: string
  eventType: string
  timestamp: string
  lapNumber: number
  message?: string
}

export interface Overtake {
  id: string
  sessionId: string
  lapNumber: number
  overtakingDriverId: string
  overtakenDriverId: string
  drsUsed: boolean
  location?: string
}

export interface CounterfactualScenario {
  id: string
  name: string
  description: string
  parameters: Record<string, unknown>
}

export interface CounterfactualResult {
  scenarioId: string
  originalOutcome: Record<string, unknown>
  counterfactualOutcome: Record<string, unknown>
  delta: Record<string, number>
  confidence: number
  probabilityDistribution?: Record<string, number>
  narrative?: string
}

export interface StrategyRecommendation {
  pitAction: string
  paceMode: string
  ersMode: string
  reasoning: Record<string, unknown>
  recommendedPitWindow: { earliest: number; ideal: number; latest: number }
  confidence: number
}

export interface Prediction {
  predictedLapTime: number
  baseLapTime: number
  adjustments: Record<string, number>
  confidence: number
  uncertainty: number
}

const BASE = "https://api.jolpi.ca/ergast/f1"
const SEASON = "2026"
const CACHE = { next: { revalidate: 3600 } } as RequestInit

async function fetchJson(path: string) {
  const res = await fetch(`${BASE}${path}`, CACHE)
  if (!res.ok) throw new Error(`Jolpica API error: ${res.status}`)
  return res.json()
}

// ─── Types matching existing app shape ───────────────────────────────────────

export interface ApiDriver {
  id: string
  number: number
  code: string
  firstName: string
  lastName: string
  team: string
  nationality: string
  points: number
  wins: number
  podiums: number
  position: number
}

export interface ApiConstructor {
  id: string
  name: string
  points: number
  position: number
  wins: number
}

export interface ApiRaceResult {
  position: number
  positionText: string
  driverId: string
  driverCode: string
  driverFirstName: string
  driverLastName: string
  team: string
  time: string
  points: number
  fastestLap: boolean
  gap: string
  laps: number
  status: string
  grid: number
}

export interface ApiRace {
  id: string
  round: number
  name: string
  circuitId: string
  circuitName: string
  city: string
  country: string
  date: string
  laps: number
  results: ApiRaceResult[]
  isSprint: boolean
}

export interface ApiCircuit {
  id: string
  name: string
  country: string
  city: string
}

// ─── Fetchers ────────────────────────────────────────────────────────────────

export async function fetchDriverStandings(): Promise<ApiDriver[]> {
  const data = await fetchJson(`/${SEASON}/driverStandings.json`)
  const list = data.MRData.StandingsTable.StandingsLists[0]?.DriverStandings ?? []
  return list.map((s: any) => ({
    id: s.Driver.driverId,
    number: parseInt(s.Driver.permanentNumber) || 0,
    code: s.Driver.code,
    firstName: s.Driver.givenName,
    lastName: s.Driver.familyName,
    team: s.Constructors[0]?.name ?? "",
    nationality: s.Driver.nationality,
    points: parseFloat(s.points),
    wins: parseInt(s.wins),
    podiums: 0,
    position: parseInt(s.position),
  }))
}

export async function fetchConstructorStandings(): Promise<ApiConstructor[]> {
  const data = await fetchJson(`/${SEASON}/constructorStandings.json`)
  const list = data.MRData.StandingsTable.StandingsLists[0]?.ConstructorStandings ?? []
  return list.map((s: any) => ({
    id: s.Constructor.constructorId,
    name: s.Constructor.name,
    points: parseFloat(s.points),
    position: parseInt(s.position),
    wins: parseInt(s.wins),
  }))
}

export async function fetchRaceSchedule(): Promise<ApiRace[]> {
  const data = await fetchJson(`/${SEASON}.json?limit=30`)
  const races = data.MRData.RaceTable.Races ?? []
  return races.map((r: any) => ({
    id: `${r.Circuit.circuitId}-${r.season}`,
    round: parseInt(r.round),
    name: r.raceName,
    circuitId: r.Circuit.circuitId,
    circuitName: r.Circuit.circuitName,
    city: r.Circuit.Location.locality,
    country: r.Circuit.Location.country,
    date: r.date,
    laps: 0,
    results: [],
    isSprint: !!r.Sprint,
  }))
}

export async function fetchRaceResults(round: number): Promise<ApiRace | null> {
  const data = await fetchJson(`/${SEASON}/${round}/results.json`)
  const races = data.MRData.RaceTable.Races ?? []
  if (races.length === 0) return null
  const r = races[0]
  const results: ApiRaceResult[] = (r.Results ?? []).map((res: any) => {
    const fl = res.FastestLap?.rank === "1"
    return {
      position: parseInt(res.position),
      positionText: res.positionText,
      driverId: res.Driver.driverId,
      driverCode: res.Driver.code,
      driverFirstName: res.Driver.givenName,
      driverLastName: res.Driver.familyName,
      team: res.Constructor.name,
      time: res.Time?.time ?? res.status,
      points: parseFloat(res.points),
      fastestLap: fl,
      gap: res.Time?.time ?? res.status,
      laps: parseInt(res.laps) || 0,
      status: res.status,
      grid: parseInt(res.grid) || 0,
    }
  })
  return {
    id: `${r.Circuit.circuitId}-${r.season}`,
    round: parseInt(r.round),
    name: r.raceName,
    circuitId: r.Circuit.circuitId,
    circuitName: r.Circuit.circuitName,
    city: r.Circuit.Location.locality,
    country: r.Circuit.Location.country,
    date: r.date,
    laps: results[0]?.laps ?? 0,
    results,
    isSprint: !!r.Sprint,
  }
}

export async function fetchAllCompletedRaces(): Promise<ApiRace[]> {
  const data = await fetchJson(`/${SEASON}/results.json?limit=600`)
  const races = data.MRData.RaceTable.Races ?? []
  return races.map((r: any) => {
    const results: ApiRaceResult[] = (r.Results ?? []).map((res: any) => ({
      position: parseInt(res.position),
      positionText: res.positionText,
      driverId: res.Driver.driverId,
      driverCode: res.Driver.code,
      driverFirstName: res.Driver.givenName,
      driverLastName: res.Driver.familyName,
      team: res.Constructor.name,
      time: res.Time?.time ?? res.status,
      points: parseFloat(res.points),
      fastestLap: res.FastestLap?.rank === "1",
      gap: res.Time?.time ?? res.status,
      laps: parseInt(res.laps) || 0,
      status: res.status,
      grid: parseInt(res.grid) || 0,
    }))
    return {
      id: `${r.Circuit.circuitId}-${r.season}`,
      round: parseInt(r.round),
      name: r.raceName,
      circuitId: r.Circuit.circuitId,
      circuitName: r.Circuit.circuitName,
      city: r.Circuit.Location.locality,
      country: r.Circuit.Location.country,
      date: r.date,
      laps: results[0]?.laps ?? 0,
      results,
      isSprint: !!r.Sprint,
    }
  })
}

export async function fetchDriverResults(driverId: string): Promise<ApiRace[]> {
  const data = await fetchJson(`/${SEASON}/drivers/${driverId}/results.json?limit=30`)
  const races = data.MRData.RaceTable.Races ?? []
  return races.map((r: any) => {
    const results: ApiRaceResult[] = (r.Results ?? []).map((res: any) => ({
      position: parseInt(res.position),
      positionText: res.positionText,
      driverId: res.Driver.driverId,
      driverCode: res.Driver.code,
      driverFirstName: res.Driver.givenName,
      driverLastName: res.Driver.familyName,
      team: res.Constructor.name,
      time: res.Time?.time ?? res.status,
      points: parseFloat(res.points),
      fastestLap: res.FastestLap?.rank === "1",
      gap: res.Time?.time ?? res.status,
      laps: parseInt(res.laps) || 0,
      status: res.status,
      grid: parseInt(res.grid) || 0,
    }))
    return {
      id: `${r.Circuit.circuitId}-${r.season}`,
      round: parseInt(r.round),
      name: r.raceName,
      circuitId: r.Circuit.circuitId,
      circuitName: r.Circuit.circuitName,
      city: r.Circuit.Location.locality,
      country: r.Circuit.Location.country,
      date: r.date,
      laps: results[0]?.laps ?? 0,
      results,
      isSprint: !!r.Sprint,
    }
  })
}

// ─── Driver Headshots (OpenF1) ───────────────────────────────────────────────

export async function fetchDriverHeadshots(): Promise<Record<string, string>> {
  try {
    const res = await fetch("https://api.openf1.org/v1/drivers?session_key=latest", CACHE)
    if (!res.ok) return {}
    const drivers: any[] = await res.json()
    const map: Record<string, string> = {}
    for (const d of drivers) {
      if (d.name_acronym && d.headshot_url) {
        map[d.name_acronym] = d.headshot_url
      }
    }
    return map
  } catch {
    return {}
  }
}

// ─── Circuit SVG Layouts ─────────────────────────────────────────────────────

const CIRCUIT_SVG_MAP: Record<string, string> = {
  albert_park: "melbourne-4",
  shanghai: "shanghai-1",
  suzuka: "suzuka-2",
  bahrain: "bahrain-2",
  jeddah: "jeddah-1",
  miami: "miami-1",
  imola: "imola-3",
  monaco: "monaco-5",
  villeneuve: "montreal-3",
  silverstone: "silverstone-7",
  spa: "spa-francorchamps-5",
  hungaroring: "hungaroring-2",
  zandvoort: "zandvoort-3",
  monza: "monza-7",
  baku: "baku-1",
  marina_bay: "singapore-3",
  losail: "losail-1",
  americas: "austin-1",
  rodriguez: "mexico-city-3",
  interlagos: "interlagos-3",
  vegas: "las-vegas-1",
  yas_marina: "yas-marina-2",
  catalunya: "catalunya-5",
  red_bull_ring: "spielberg-4",
}

export function getCircuitSvgUrl(circuitId: string): string | null {
  const layoutId = CIRCUIT_SVG_MAP[circuitId]
  if (!layoutId) return null
  return `https://raw.githubusercontent.com/julesr0y/f1-circuits-svg/main/circuits/minimal/white-outline/${layoutId}.svg`
}

export { SEASON }

const ERGAST_BASE = "https://api.jolpi.ca/ergast/f1"

export interface RaceResult {
  season: string
  round: string
  raceName: string
  circuitId: string
  circuitName: string
  date: string
  results: {
    position: string
    driver: string
    driverId: string
    constructor: string
    constructorId: string
    grid: string
    laps: string
    status: string
    points: string
    time?: string
  }[]
}

export interface DriverStanding {
  position: string
  points: string
  wins: string
  driverId: string
  driver: string
  nationality: string
  constructorId: string
  constructor: string
}

export interface ConstructorStanding {
  position: string
  points: string
  wins: string
  constructorId: string
  constructor: string
  nationality: string
}

export async function fetchRaceResults(year: number = 2025): Promise<RaceResult[]> {
  try {
    const res = await fetch(`${ERGAST_BASE}/${year}/results.json?limit=1000`, {
      next: { revalidate: 3600 },
    })
    if (!res.ok) return []
    const data = await res.json()
    const races = data.MRData.RaceTable.Races
    return races.map((race: any) => ({
      season: race.season,
      round: race.round,
      raceName: race.raceName,
      circuitId: race.Circuit.circuitId,
      circuitName: race.Circuit.circuitName,
      date: race.date,
      results: race.Results.map((r: any) => ({
        position: r.position,
        driver: `${r.Driver.givenName} ${r.Driver.familyName}`,
        driverId: r.Driver.driverId,
        constructor: r.Constructor.name,
        constructorId: r.Constructor.constructorId,
        grid: r.grid,
        laps: r.laps,
        status: r.status,
        points: r.points,
        time: r.Time?.time,
      })),
    }))
  } catch {
    return []
  }
}

export async function fetchDriverStandings(year: number = 2025): Promise<DriverStanding[]> {
  try {
    const res = await fetch(`${ERGAST_BASE}/${year}/driverStandings.json`, {
      next: { revalidate: 3600 },
    })
    if (!res.ok) return []
    const data = await res.json()
    const standings = data.MRData.StandingsTable.StandingsLists[0]?.DriverStandings || []
    return standings.map((s: any) => ({
      position: s.position,
      points: s.points,
      wins: s.wins,
      driverId: s.Driver.driverId,
      driver: `${s.Driver.givenName} ${s.Driver.familyName}`,
      nationality: s.Driver.nationality,
      constructorId: s.Constructors[0]?.constructorId,
      constructor: s.Constructors[0]?.name,
    }))
  } catch {
    return []
  }
}

export async function fetchConstructorStandings(year: number = 2025): Promise<ConstructorStanding[]> {
  try {
    const res = await fetch(`${ERGAST_BASE}/${year}/constructorStandings.json`, {
      next: { revalidate: 3600 },
    })
    if (!res.ok) return []
    const data = await res.json()
    const standings = data.MRData.StandingsTable.StandingsLists[0]?.ConstructorStandings || []
    return standings.map((s: any) => ({
      position: s.position,
      points: s.points,
      wins: s.wins,
      constructorId: s.Constructor.constructorId,
      constructor: s.Constructor.name,
      nationality: s.Constructor.nationality,
    }))
  } catch {
    return []
  }
}

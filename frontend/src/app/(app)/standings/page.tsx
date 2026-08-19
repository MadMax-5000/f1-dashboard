import { fetchDriverStandings, fetchConstructorStandings, SEASON } from "@/lib/f1-api"
import StandingsClient from "./StandingsClient"

export default async function StandingsPage() {
  const [drivers, constructors] = await Promise.all([
    fetchDriverStandings(),
    fetchConstructorStandings(),
  ])

  return <StandingsClient drivers={drivers} constructors={constructors} season={SEASON} />
}

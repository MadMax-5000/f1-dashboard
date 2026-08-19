import { fetchDriverStandings, fetchConstructorStandings } from "@/lib/f1-api"
import StandingsClient from "./StandingsClient"

export default async function StandingsPage() {
  const [drivers, constructors] = await Promise.all([
    fetchDriverStandings(2025),
    fetchConstructorStandings(2025),
  ])
  return <StandingsClient drivers={drivers} constructors={constructors} />
}

import { fetchDriverStandings, fetchConstructorStandings, fetchAllCompletedRaces, SEASON } from "@/lib/f1-api"
import DashboardClient from "./DashboardClient"

export default async function DashboardPage() {
  const [drivers, constructors, races] = await Promise.all([
    fetchDriverStandings(),
    fetchConstructorStandings(),
    fetchAllCompletedRaces(),
  ])

  return <DashboardClient drivers={drivers} constructors={constructors} races={races} season={SEASON} />
}

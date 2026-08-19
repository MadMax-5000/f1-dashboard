import { fetchRaceSchedule, fetchAllCompletedRaces, SEASON } from "@/lib/f1-api"
import RacesClient from "./RacesClient"

export default async function RacesPage() {
  const [schedule, completed] = await Promise.all([
    fetchRaceSchedule(),
    fetchAllCompletedRaces(),
  ])

  const races = schedule.map((race) => {
    const match = completed.find((c) => c.round === race.round)
    return match ?? race
  })

  return <RacesClient races={races} season={SEASON} />
}

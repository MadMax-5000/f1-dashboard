import { fetchRaceSchedule, fetchAllCompletedRaces } from "@/lib/f1-api"
import CircuitsClient from "./CircuitsClient"

export default async function CircuitsPage() {
  const [schedule, completed] = await Promise.all([
    fetchRaceSchedule(),
    fetchAllCompletedRaces(),
  ])

  const races = schedule.map((race) => {
    const match = completed.find((c) => c.round === race.round)
    return match ?? race
  })

  return <CircuitsClient races={races} />
}

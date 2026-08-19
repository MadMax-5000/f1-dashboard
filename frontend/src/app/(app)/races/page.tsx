import { fetchRaceResults } from "@/lib/f1-api"
import RacesClient from "./RacesClient"

export default async function RacesPage() {
  const races = await fetchRaceResults(2025)
  return <RacesClient races={races} />
}

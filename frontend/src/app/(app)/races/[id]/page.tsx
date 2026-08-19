import { fetchRaceResults } from "@/lib/f1-api"
import RaceDetailClient from "./RaceDetailClient"

export default async function RaceDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  const round = parseInt(id)
  if (isNaN(round)) return <div className="p-8 text-gray-500">Invalid race round.</div>

  const race = await fetchRaceResults(round)
  if (!race) return <div className="p-8 text-gray-500">Race not found or not yet completed.</div>

  return <RaceDetailClient race={race} />
}

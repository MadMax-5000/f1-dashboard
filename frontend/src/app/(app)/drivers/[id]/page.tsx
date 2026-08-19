import { fetchDriverStandings, fetchDriverResults, fetchDriverHeadshots } from "@/lib/f1-api"
import DriverDetailClient from "./DriverDetailClient"

export default async function DriverDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params

  const [drivers, races, headshots] = await Promise.all([
    fetchDriverStandings(),
    fetchDriverResults(id),
    fetchDriverHeadshots(),
  ])

  const driver = drivers.find((d) => d.id === id)
  if (!driver) return <div className="p-8 text-gray-500">Driver not found.</div>

  return <DriverDetailClient driver={driver} races={races} headshotUrl={headshots[driver.code]} />
}

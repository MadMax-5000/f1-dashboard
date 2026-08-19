import { fetchDriverStandings, fetchDriverHeadshots, SEASON } from "@/lib/f1-api"
import DriversClient from "./DriversClient"

export default async function DriversPage() {
  const [drivers, headshots] = await Promise.all([
    fetchDriverStandings(),
    fetchDriverHeadshots(),
  ])
  return <DriversClient drivers={drivers} headshots={headshots} season={SEASON} />
}

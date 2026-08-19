import { fetchDriverStandings } from "@/lib/f1-api"
import DriversClient from "./DriversClient"

export default async function DriversPage() {
  const drivers = await fetchDriverStandings(2025)
  return <DriversClient drivers={drivers} />
}

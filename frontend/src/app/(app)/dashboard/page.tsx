import { fetchNextRacePredictions } from "@/lib/predictions-api"
import DashboardClient from "./DashboardClient"

export default async function PredictionsPage() {
  const predictions = await fetchNextRacePredictions()

  return <DashboardClient predictions={predictions} />
}

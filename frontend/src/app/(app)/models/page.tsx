import { fetchModelPerformance } from "@/lib/predictions-api"
import ModelsClient from "./ModelsClient"

export default async function ModelsPage() {
  const metrics = await fetchModelPerformance()
  return <ModelsClient metrics={metrics} />
}

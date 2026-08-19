export const TEAM_COLORS: Record<string, string> = {
  McLaren: "#FF8000",
  "Red Bull": "#3671C6",
  Mercedes: "#27F4D2",
  Ferrari: "#E8002D",
  Williams: "#64C4FF",
  "RB F1 Team": "#6692FF",
  "Aston Martin": "#229971",
  "Haas F1 Team": "#B6BABD",
  Audi: "#52E252",
  "Alpine F1 Team": "#FF87BC",
  "Cadillac F1 Team": "#C0A44D",
}

export function generateLapTimes(laps: number, baseTime: number = 92): number[] {
  const times: number[] = []
  for (let i = 0; i < laps; i++) {
    const fuelEffect = (laps - i) * 0.03
    const tyreEffect = i > 20 ? (i - 20) * 0.04 : 0
    const variation = (Math.random() - 0.5) * 0.8
    times.push(baseTime + fuelEffect + tyreEffect + variation)
  }
  return times
}

export function generateSpeedTrace(points: number = 100): { distance: number; speed: number }[] {
  const trace: { distance: number; speed: number }[] = []
  let speed = 280
  for (let i = 0; i < points; i++) {
    const braking = Math.random() > 0.85
    if (braking) speed = 80 + Math.random() * 60
    else speed = Math.min(340, speed + (Math.random() * 15 - 3))
    trace.push({ distance: (i / points) * 5.4, speed })
  }
  return trace
}

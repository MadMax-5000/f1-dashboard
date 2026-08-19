"use client"

import { useEffect, useRef } from "react"
import * as d3 from "d3"
import { useF1Store } from "@/lib/store"

export function TelemetryPanel() {
  const svgRef = useRef<SVGSVGElement>(null)
  const twinState = useF1Store((s) => s.twinState)
  const focusedDriver = useF1Store((s) => s.focusedDriver)

  useEffect(() => {
    if (!svgRef.current || !twinState || !focusedDriver) return
    const svg = d3.select(svgRef.current)
    const width = svgRef.current.clientWidth
    const height = svgRef.current.clientHeight
    const margin = { top: 20, right: 20, bottom: 30, left: 50 }

    svg.selectAll("*").remove()

    const driver = twinState.drivers[focusedDriver]
    if (!driver) return

    const data = Array.from(
      { length: 60 },
      (_, i) => ({
        t: i,
        speed: driver.speed * (0.9 + Math.random() * 0.2),
        rpm: 8000 + Math.random() * 4000,
        throttle: Math.random(),
      })
    )

    const x = d3.scaleLinear().domain([0, 59]).range([margin.left, width - margin.right])
    const ySpeed = d3.scaleLinear().domain([0, 360]).range([height - margin.bottom, margin.top])
    const yThrottle = d3.scaleLinear().domain([0, 1]).range([height - margin.bottom, height - margin.top + 80])

    const g = svg.append("g")

    g.append("g")
      .attr("transform", `translate(0, ${height - margin.bottom})`)
      .call(d3.axisBottom(x).ticks(6))
      .attr("color", "#444")

    g.append("g")
      .attr("transform", `translate(${margin.left}, 0)`)
      .call(d3.axisLeft(ySpeed).ticks(5))
      .attr("color", "#444")

    const speedLine = d3
      .line<{ t: number; speed: number }>()
      .x((d) => x(d.t))
      .y((d) => ySpeed(d.speed))

    g.append("path")
      .datum(data)
      .attr("fill", "none")
      .attr("stroke", "#0088ff")
      .attr("stroke-width", 2)
      .attr("d", speedLine)

    const throttleBars = g
      .selectAll("rect")
      .data(data)
      .enter()
      .append("rect")
      .attr("x", (d) => x(d.t) - 3)
      .attr("y", (d) => yThrottle(d.throttle))
      .attr("width", 5)
      .attr("height", (d) => yThrottle(0) - yThrottle(d.throttle))
      .attr("fill", "#00ff87")
      .attr("opacity", 0.3)
  }, [twinState, focusedDriver])

  return (
    <div className="p-3 h-full">
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs text-gray-500 uppercase tracking-wider">
          Telemetry {focusedDriver ? `- Driver #${focusedDriver}` : ""}
        </span>
        <div className="flex gap-3 text-xs">
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-f1-blue" />
            Speed
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-f1-accent" />
            Throttle
          </span>
        </div>
      </div>
      <svg ref={svgRef} className="w-full h-[calc(100%-24px)]" />
    </div>
  )
}

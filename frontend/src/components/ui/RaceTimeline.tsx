"use client"

import { useEffect, useRef } from "react"
import * as d3 from "d3"
import { useF1Store } from "@/lib/store"

export function RaceTimeline() {
  const svgRef = useRef<SVGSVGElement>(null)
  const events = useF1Store((s) => s.events)
  const twinState = useF1Store((s) => s.twinState)

  useEffect(() => {
    if (!svgRef.current || !twinState) return
    const svg = d3.select(svgRef.current)
    const width = svgRef.current.clientWidth
    const height = svgRef.current.clientHeight
    const margin = { top: 10, right: 20, bottom: 20, left: 40 }

    svg.selectAll("*").remove()

    const totalLaps = (twinState as any).totalLaps || 70
    const x = d3.scaleLinear().domain([1, totalLaps]).range([margin.left, width - margin.right])
    const y = d3.scaleLinear().domain([1, 20]).range([height - margin.bottom, margin.top])

    const g = svg.append("g")

    // X axis
    g.append("g")
      .attr("transform", `translate(0, ${height - margin.bottom})`)
      .call(d3.axisBottom(x).ticks(10).tickFormat(d3.format("d")))
      .attr("color", "#444")

    // Y axis
    g.append("g")
      .attr("transform", `translate(${margin.left}, 0)`)
      .call(d3.axisLeft(y).ticks(10))
      .attr("color", "#444")

    // Position lines for each driver
    const driverIds = twinState.order
    const colors = d3.schemeCategory10
    driverIds.forEach((did, idx) => {
      if (!twinState.drivers[did]) return
      const data = Array.from({ length: twinState.lapNumber }, (_, i) => ({
        lap: i + 1,
        pos: 1 + Math.sin(i * 0.3 + idx) * 3 + Math.random() * 0.5,
      }))

      const line = d3
        .line<{ lap: number; pos: number }>()
        .x((d) => x(d.lap))
        .y((d) => y(d.pos))
        .curve(d3.curveMonotoneX)

      g.append("path")
        .datum(data)
        .attr("fill", "none")
        .attr("stroke", colors[idx % colors.length])
        .attr("stroke-width", 1.5)
        .attr("opacity", 0.7)
        .attr("d", line)
    })

    // Event markers
    events
      .filter((e) => e.lapNumber <= totalLaps)
      .forEach((evt) => {
        const cx = x(evt.lapNumber)
        g.append("circle")
          .attr("cx", cx)
          .attr("cy", margin.top + 5)
          .attr("r", 4)
          .attr("fill", evt.eventType === "overtake" ? "#00ff87" : "#ffd700")
          .append("title")
          .text(`${evt.eventType}: ${evt.message || ""}`)
      })

    // Current lap indicator
    g.append("line")
      .attr("x1", x(twinState.lapNumber))
      .attr("x2", x(twinState.lapNumber))
      .attr("y1", margin.top)
      .attr("y2", height - margin.bottom)
      .attr("stroke", "#e10600")
      .attr("stroke-width", 2)
      .attr("stroke-dasharray", "4,4")
  }, [events, twinState])

  return (
    <div className="p-2 h-full">
      <div className="flex items-center justify-between mb-1">
        <span className="text-xs text-gray-500 uppercase tracking-wider">Position Timeline</span>
        <span className="text-xs text-gray-600">
          Lap {twinState?.lapNumber || 0}/{(twinState as any)?.totalLaps || 0}
        </span>
      </div>
      <svg ref={svgRef} className="w-full h-[calc(100%-20px)]" />
    </div>
  )
}

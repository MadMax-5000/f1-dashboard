"use client"

import Link from "next/link"
import { motion } from "framer-motion"
import { Flag, Users, MapPin, TrendingUp } from "lucide-react"
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts"
import { StatCard } from "@/components/ui/StatCard"
import { Card } from "@/components/ui/Card"
import { Badge } from "@/components/ui/Badge"
import { TEAM_COLORS } from "@/lib/mock-data"
import type { ApiDriver, ApiConstructor, ApiRace } from "@/lib/f1-api"

interface Props {
  drivers: ApiDriver[]
  constructors: ApiConstructor[]
  races: ApiRace[]
  season: string
}

export default function DashboardClient({ drivers, constructors, races, season }: Props) {
  const standingsData = constructors.slice(0, 8).map((c, i) => ({
    name: c.name,
    points: c.points,
    color: i === 0 ? "#B4FF39" : "#3A3F46",
  }))

  const completedRaces = races.filter((r) => r.results.length > 0)
  const recentRaces = completedRaces.slice(-5).reverse()

  return (
    <div className="p-8 space-y-8">
      <div>
        <h1 className="display-type mb-1 text-4xl font-semibold text-white">Dashboard</h1>
        <p className="label-type text-gray-500 uppercase">{season} Season Overview</p>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="grid grid-cols-2 lg:grid-cols-4 gap-4"
      >
        <StatCard label="Completed Races" value={completedRaces.length} icon={Flag} subtitle={`${season} Season`} />
        <StatCard label="Active Drivers" value={drivers.length} icon={Users} subtitle={`${constructors.length} Teams`} />
        <StatCard label="Total Races" value={races.length} icon={MapPin} subtitle="Calendar" />
        <StatCard
          label="Total Wins"
          value={constructors.reduce((sum, c) => sum + c.wins, 0)}
          icon={TrendingUp}
          subtitle="All teams"
        />
      </motion.div>

      <div className="grid lg:grid-cols-5 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15, duration: 0.5 }}
          className="lg:col-span-3"
        >
          <Card>
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-xl font-semibold text-white">Constructor Standings</h2>
                <p className="label-type mt-1 text-gray-600 uppercase">Points after Round {completedRaces.length}</p>
              </div>
              <Link href="/standings" className="label-type text-gray-500 hover:text-f1-accent transition-colors uppercase">
                View all &rarr;
              </Link>
            </div>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={standingsData} layout="vertical" margin={{ left: 10, right: 20 }}>
                <XAxis type="number" tick={{ fill: "#666", fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis type="category" dataKey="name" tick={{ fill: "#aaa", fontSize: 11 }} axisLine={false} tickLine={false} width={85} />
                <Tooltip
                  contentStyle={{ backgroundColor: "#17191C", border: "1px solid #2A2E35", borderRadius: 10, fontSize: 12 }}
                  labelStyle={{ color: "#fff" }}
                  itemStyle={{ color: "#aaa" }}
                />
                <Bar dataKey="points" radius={[0, 6, 6, 0]} barSize={18}>
                  {standingsData.map((entry, i) => (
                    <Cell key={i} fill={entry.color} fillOpacity={0.8} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.25, duration: 0.5 }}
          className="lg:col-span-2"
        >
          <Card className="h-full">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-white">Recent Races</h2>
              <Link href="/races" className="label-type text-gray-500 hover:text-f1-accent transition-colors uppercase">
                All races &rarr;
              </Link>
            </div>
            <div className="space-y-3">
              {recentRaces.map((race) => {
                const winner = race.results[0]
                return (
                  <Link
                    key={race.id}
                    href={`/races/${race.round}`}
                    className="group flex items-center justify-between rounded-[10px] border border-transparent p-3 transition-colors hover:border-f1-border hover:bg-f1-darker"
                  >
                    <div className="min-w-0">
                      <div className="truncate text-sm font-medium text-white transition-colors group-hover:text-f1-accent">
                        R{race.round} &middot; {race.name}
                      </div>
                      <div className="text-xs text-gray-600 mt-0.5">{race.country}</div>
                    </div>
                    <div className="text-right shrink-0 ml-3">
                      <div className="label-type font-semibold text-white">{winner?.driverCode}</div>
                      <Badge variant="team" teamName={winner?.team} className="mt-0.5">
                        {winner?.team?.split(" ")[0]}
                      </Badge>
                    </div>
                  </Link>
                )
              })}
            </div>
          </Card>
        </motion.div>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.35, duration: 0.5 }}
        className="grid grid-cols-2 md:grid-cols-4 gap-4"
      >
        {[
          { href: "/races", label: "Race Calendar", desc: "Browse all races", icon: Flag },
          { href: "/drivers", label: "Driver Profiles", desc: "Stats & performance", icon: Users },
          { href: "/circuits", label: "Circuit Maps", desc: "Track details", icon: MapPin },
          { href: "/standings", label: "Championships", desc: "Live standings", icon: TrendingUp },
        ].map((item) => (
          <Link key={item.href} href={item.href}>
            <Card hover className="h-full">
              <item.icon size={20} className="mb-4 text-f1-accent" />
              <div className="mb-1 text-base font-semibold text-white">{item.label}</div>
              <div className="text-sm text-gray-600">{item.desc}</div>
            </Card>
          </Link>
        ))}
      </motion.div>
    </div>
  )
}

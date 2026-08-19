"use client"

import Link from "next/link"
import { motion } from "framer-motion"
import { ArrowRight, Cpu, GitBranch, Gauge, Zap, BarChart3, Globe } from "lucide-react"

const STATS = [
  { label: "Drivers", value: "20", icon: Gauge },
  { label: "Races Analyzed", value: "10", icon: BarChart3 },
  { label: "Data Points", value: "2.4M+", icon: Zap },
  { label: "Circuits", value: "10", icon: Globe },
]

const FEATURES = [
  {
    title: "Digital Twin Engine",
    description: "Full race reconstruction with tick-by-tick simulation of every car on track. Replay any moment from any angle.",
    icon: Cpu,
  },
  {
    title: "AI Strategy Analysis",
    description: "Reinforcement learning-based strategist that evaluates pit windows, tyre compounds, and pace modes in real time.",
    icon: GitBranch,
  },
  {
    title: "Counterfactual Simulation",
    description: "What if Hamilton pitted one lap earlier? Run alternate scenarios and see how the race would have unfolded.",
    icon: Zap,
  },
]

const fadeUp = {
  hidden: { opacity: 0, y: 30 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.1, duration: 0.6, ease: [0.25, 0.46, 0.45, 0.94] },
  }),
}

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-f1-darker grid-bg text-f1-light">
      {/* Nav */}
      <nav className="mx-auto flex max-w-7xl items-center justify-between px-8 py-5">
        <div className="flex items-center gap-2.5">
          <div className="w-2.5 h-2.5 rounded-full bg-f1-accent animate-pulse-glow" />
          <span className="display-type text-base font-semibold text-white">
            F1 <span className="text-gray-400">DigitalTwin</span>
          </span>
        </div>
        <Link
          href="/dashboard"
          className="label-type text-gray-400 hover:text-white transition-colors uppercase"
        >
          Launch App
        </Link>
      </nav>

      {/* Hero */}
      <section className="mx-auto flex max-w-7xl flex-col items-center justify-center px-8 pt-20 pb-28">
        <motion.div
          initial="hidden"
          animate="visible"
          className="text-center max-w-4xl mx-auto"
        >
          <motion.div custom={0} variants={fadeUp} className="mb-6">
            <span className="label-type inline-flex items-center gap-2 rounded-full border border-f1-border bg-f1-surface px-4 py-2 text-gray-400 uppercase">
              <span className="w-1.5 h-1.5 rounded-full bg-f1-accent animate-pulse" />
              AI-Powered Race Intelligence Platform
            </span>
          </motion.div>

          <motion.h1
            custom={1}
            variants={fadeUp}
            className="display-type mb-6 text-6xl font-semibold leading-[0.92] md:text-[6.5rem]"
          >
            <span className="text-white">F1 Digital</span>
            <br />
            <span className="text-f1-accent">Twin</span>
          </motion.h1>

          <motion.p
            custom={2}
            variants={fadeUp}
            className="mx-auto mb-10 max-w-2xl text-lg leading-relaxed text-gray-400 md:text-xl"
          >
            Reconstruct races. Simulate strategies. Explore counterfactuals.
            The most advanced Formula 1 analytics platform built with AI.
          </motion.p>

          <motion.div custom={3} variants={fadeUp} className="flex items-center justify-center gap-4">
            <Link
              href="/dashboard"
              className="group inline-flex items-center gap-2 rounded-[10px] bg-f1-accent px-6 py-3 text-sm font-semibold text-black transition-all duration-200 hover:brightness-95"
            >
              Enter Dashboard
              <ArrowRight size={16} className="transition-transform group-hover:translate-x-1" />
            </Link>
            <Link
              href="/races"
              className="inline-flex items-center gap-2 rounded-[10px] border border-f1-border bg-f1-surface px-6 py-3 text-sm font-medium text-gray-300 hover:bg-f1-gray hover:text-white transition-all duration-200"
            >
              Browse Races
            </Link>
          </motion.div>
        </motion.div>

        {/* Stats */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6, duration: 0.8 }}
          className="mt-24 grid w-full max-w-4xl grid-cols-2 gap-4 md:grid-cols-4"
        >
          {STATS.map((stat) => (
            <div
              key={stat.label}
              className="surface-panel rounded-[14px] p-5 text-center group"
            >
              <stat.icon size={18} className="mx-auto mb-3 text-f1-accent" />
              <div className="display-type mb-1 text-3xl font-semibold text-white">{stat.value}</div>
              <div className="label-type uppercase text-gray-500">{stat.label}</div>
            </div>
          ))}
        </motion.div>
      </section>

      {/* Features */}
      <section className="mx-auto max-w-6xl px-8 pb-28">
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="mb-16 text-center"
        >
          <h2 className="display-type mb-3 text-4xl font-semibold text-white">Powered by Advanced AI</h2>
          <p className="text-gray-500 max-w-xl mx-auto">
            Three core engines work together to deliver insights no other platform can.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-5">
          {FEATURES.map((feature, i) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.15, duration: 0.6 }}
              className="surface-panel rounded-[14px] p-6 group"
            >
              <div className="mb-5 flex h-10 w-10 items-center justify-center rounded-[10px] border border-f1-border bg-f1-darker">
                <feature.icon size={20} className="text-f1-accent" />
              </div>
              <h3 className="mb-2 text-xl font-semibold text-white">{feature.title}</h3>
              <p className="text-sm text-gray-500 leading-relaxed">{feature.description}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-f1-border px-8 py-6 text-center">
        <p className="label-type text-gray-600 uppercase">
          F1 Digital Twin &middot; Built with Next.js, Three.js, FastAPI & PyTorch
        </p>
      </footer>
    </div>
  )
}

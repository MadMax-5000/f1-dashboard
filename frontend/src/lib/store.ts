import { create } from "zustand"
import { immer } from "zustand/middleware/immer"
import type { RaceState, Race, Driver, RaceEvent, CounterfactualResult } from "@/types"

interface F1Store {
  races: Race[]
  selectedRace: Race | null
  selectedSession: string | null
  twinState: RaceState | null
  isReplaying: boolean
  replaySpeed: number
  replayTick: number
  events: RaceEvent[]
  counterfactuals: CounterfactualResult[]
  darkMode: boolean
  focusedDriver: string | null

  setRaces: (races: Race[]) => void
  setSelectedRace: (race: Race | null) => void
  setSelectedSession: (sessionId: string | null) => void
  setTwinState: (state: RaceState) => void
  setIsReplaying: (replaying: boolean) => void
  setReplaySpeed: (speed: number) => void
  setReplayTick: (tick: number) => void
  addEvents: (events: RaceEvent[]) => void
  addCounterfactual: (result: CounterfactualResult) => void
  setFocusedDriver: (driverId: string | null) => void
  toggleDarkMode: () => void
}

export const useF1Store = create<F1Store>()(
  immer((set) => ({
    races: [],
    selectedRace: null,
    selectedSession: null,
    twinState: null,
    isReplaying: false,
    replaySpeed: 1.0,
    replayTick: 0,
    events: [],
    counterfactuals: [],
    darkMode: true,
    focusedDriver: null,

    setRaces: (races) =>
      set((state) => {
        state.races = races
      }),

    setSelectedRace: (race) =>
      set((state) => {
        state.selectedRace = race
      }),

    setSelectedSession: (sessionId) =>
      set((state) => {
        state.selectedSession = sessionId
      }),

    setTwinState: (twinState) =>
      set((state) => {
        state.twinState = twinState
      }),

    setIsReplaying: (replaying) =>
      set((state) => {
        state.isReplaying = replaying
      }),

    setReplaySpeed: (speed) =>
      set((state) => {
        state.replaySpeed = speed
      }),

    setReplayTick: (tick) =>
      set((state) => {
        state.replayTick = tick
      }),

    addEvents: (events) =>
      set((state) => {
        state.events.push(...events)
      }),

    addCounterfactual: (result) =>
      set((state) => {
        state.counterfactuals.push(result)
      }),

    setFocusedDriver: (driverId) =>
      set((state) => {
        state.focusedDriver = driverId
      }),

    toggleDarkMode: () =>
      set((state) => {
        state.darkMode = !state.darkMode
      }),
  }))
)

# F1 Digital Twin

**AI-powered Formula 1 race analytics platform** — live standings, race results, driver profiles, circuit maps, and championship data sourced in real time from the 2026 F1 season.

Built with [Next.js 15](https://nextjs.org), [React 19](https://react.dev), [Tailwind CSS v4](https://tailwindcss.com), and [Framer Motion](https://www.framer.com/motion/).

---

## Features

| Page | Description |
|---|---|
| **Dashboard** | Season KPIs, constructor standings chart, and recent race winners |
| **Standings** | Full driver and constructor championship tables with animated progress bars |
| **Race Calendar** | All Grands Prix with results, winners, and sprint weekend indicators |
| **Race Detail** | Complete race classification, grid positions, fastest laps, and lap time chart |
| **Drivers** | Driver cards with official headshot photos, points, wins, and team colors |
| **Driver Detail** | Per-race finishing position and points charts, full season results list |
| **Circuits** | Track layout SVG drawings, circuit info, race dates, and winners |

### Data Sources

All data is fetched server-side and cached for one hour:

- **[Jolpica F1 API](https://github.com/jolpica/jolpica-f1)** — Ergast-compatible REST API providing driver/constructor standings, race schedules, results, and circuit information. Free, no API key required.
- **[OpenF1 API](https://openf1.org)** — Driver headshot image URLs sourced from official Formula 1 media assets. Free, no authentication required.
- **[f1-circuits-svg](https://github.com/julesr0y/f1-circuits-svg)** — High-quality SVG track layout drawings for every circuit on the calendar.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | Next.js 15 (App Router, Server Components) |
| UI | React 19, Tailwind CSS v4, Framer Motion |
| Charts | Recharts, D3.js |
| 3D (scaffolded) | Three.js via React Three Fiber |
| State | Zustand with Immer middleware |
| Icons | Lucide React |
| Language | TypeScript 5 |

---

## Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── page.tsx                        # Landing page
│   │   ├── layout.tsx                      # Root layout
│   │   └── (app)/                          # App shell (sidebar + main)
│   │       ├── dashboard/                  # Dashboard (server + client)
│   │       ├── standings/                  # Championship standings
│   │       ├── races/                      # Race calendar + [id] detail
│   │       ├── drivers/                    # Driver grid + [id] detail
│   │       └── circuits/                   # Circuit cards
│   ├── components/ui/                      # Shared UI components
│   │   ├── Sidebar.tsx
│   │   ├── Card.tsx
│   │   ├── Badge.tsx
│   │   ├── StatCard.tsx
│   │   └── DataTable.tsx
│   ├── lib/
│   │   ├── f1-api.ts                       # API client (Jolpica + OpenF1)
│   │   ├── mock-data.ts                    # Team colors + synthetic helpers
│   │   ├── api.ts                          # FastAPI client (future use)
│   │   └── store.ts                        # Zustand store (future use)
│   └── types/
│       └── index.ts                        # TypeScript interfaces
├── next.config.ts
├── tailwind.config.ts
├── tsconfig.json
└── package.json
```

### Architecture

Pages are **async Server Components** that fetch data at build/request time using `fetch()` with Next.js ISR caching (`revalidate: 3600`). Interactive elements (charts, animations, tabs) are extracted into `"use client"` components that receive data as props.

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   Jolpica F1 API │     │   OpenF1 API     │     │  GitHub Raw SVGs │
│  (standings,     │     │  (headshots)     │     │  (track layouts) │
│   results, etc.) │     │                  │     │                  │
└────────┬─────────┘     └────────┬─────────┘     └────────┬─────────┘
         │                        │                        │
         └────────────┬───────────┘────────────────────────┘
                      │
              ┌───────▼────────┐
              │ Server         │  fetch() + revalidate: 3600
              │ Components     │  (Next.js ISR)
              │ (page.tsx)     │
              └───────┬────────┘
                      │ props
              ┌───────▼────────┐
              │ Client         │  "use client"
              │ Components     │  (charts, animations)
              └────────────────┘
```

---

## Getting Started

### Prerequisites

- **Node.js** 18.17 or later
- **npm**, **yarn**, or **pnpm**

### Installation

```bash
git clone <repository-url>
cd f1/frontend
npm install
```

### Development

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Production Build

```bash
npm run build
npm start
```

### Type Checking

```bash
npm run typecheck
```

### Linting

```bash
npm run lint
```

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000/api/v1` | Backend API URL (for future FastAPI integration) |

No API keys are required — all external data sources used are free and public.

---

## Data Refresh

Static pages are regenerated via [Incremental Static Regeneration](https://nextjs.org/docs/app/building-your-application/data-fetching/incremental-static-regeneration) every **one hour**. Dynamic routes (`/drivers/[id]`, `/races/[id]`) are rendered on demand with the same one-hour cache.

The season is configured in `src/lib/f1-api.ts` via the `SEASON` constant. Update it to follow a different year.

---

## Acknowledgments

- [Jolpica F1](https://github.com/jolpica/jolpica-f1) for the open-source Ergast-compatible API
- [OpenF1](https://openf1.org) for driver headshot data
- [Jules Roy](https://github.com/julesr0y/f1-circuits-svg) for the circuit SVG assets
- Formula 1, FIA, and Formula One Management for the underlying data

---

## License

This project is for educational and personal use. Formula 1, F1, and related marks are trademarks of Formula One Licensing BV. This project is not associated with or endorsed by Formula 1.

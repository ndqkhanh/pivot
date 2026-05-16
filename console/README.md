# Pivot Console

Next.js web application for agent reliability monitoring and analysis.

## Features

- **Run Transcript View**: Real-time agent execution traces
- **Replay View**: Time-travel debugging with checkpoints
- **Eval Dashboard**: Statistical analysis and metrics
- **Policy Monitor**: Guardrail decisions and alerts

## Quick Start

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Open http://localhost:3000
```

## Architecture

```
Console (Next.js)
    ↓
API Routes
    ↓
Gateway + ClickHouse
```

## Pages

- `/` - Dashboard overview
- `/runs` - Run transcript list
- `/runs/[id]` - Run detail with trace view
- `/replay/[id]` - Replay interface
- `/eval` - Evaluation dashboard
- `/policy` - Policy decisions

## Tech Stack

- **Framework**: Next.js 14
- **UI**: React + TailwindCSS
- **Data**: TanStack Query
- **Charts**: Recharts

## Development

```bash
# Run dev server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

## License

Apache 2.0

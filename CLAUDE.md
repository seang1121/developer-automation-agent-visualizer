# DAAV — Developer, Automation & Agent Visualizer

Self-configuring dashboard for visualizing developer automations, AI agents, MCP servers, and Claude ecosystem tools.

## Stack
- Vite + React 19 + TypeScript 5.9 + Tailwind CSS 4.2
- Port: 3100
- All data lives in `src/data/*.json` (11 split data files)

## Commands
- `npm run dev` — start dev server on localhost:3100
- `npx tsc --noEmit` — type check
- `npm run build` — production build
- `/setup-daav` — auto-scan system and populate data files

## Rules
- No file over 300 lines
- Edit `src/data/*.json` to update data
- `daav.config.json` controls tabs and project configuration
- Dark theme only
- No personal data in sample files

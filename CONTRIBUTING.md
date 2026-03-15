# Contributing to DAAV

Thanks for your interest in contributing to the Developer, Automation & Agent Visualizer.

## Development Setup

```bash
git clone https://github.com/seang1121/developer-automation-agent-visualizer.git
cd developer-automation-agent-visualizer
npm install
npm run dev
```

The `predev` script automatically copies `.example.json` files to `.json` if they don't exist.

## Project Structure

- `src/components/cards/` — Individual item cards (agents, cron jobs, etc.)
- `src/components/layout/` — Sidebar, header, search, grid
- `src/components/shared/` — Reusable UI primitives
- `src/components/overview/` — Overview tab with stats, project grid, relationship map
- `src/components/tabs/` — Tab-level views
- `src/config/` — Config loader and icon registry
- `src/data/` — JSON data files (gitignored) and example data (committed)
- `src/hooks/` — React hooks
- `src/layout/` — Force-directed layout algorithm
- `src/types/` — TypeScript interfaces

## Guidelines

- TypeScript strict mode — no `any`
- No file over 300 lines
- Dark theme only (gray-950 background)
- All data changes go through `src/data/*.json`
- Test with `npx tsc --noEmit` before submitting

## Adding a Card Component

1. Create `src/components/cards/YourCard.tsx`
2. Add the type interface to `src/types/agents.ts`
3. Import and use in the relevant tab component

## Adding an Icon

Add SVG path data to `src/config/icons.ts` in the `iconRegistry` object.

## Pull Requests

- Keep PRs focused on a single change
- Include before/after screenshots for UI changes
- Ensure `tsc --noEmit` passes

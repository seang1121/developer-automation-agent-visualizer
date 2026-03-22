# Agent Command Center (ACC)

A self-configuring dashboard that auto-discovers your developer tools, AI agents, MCP servers, cron jobs, and developer ecosystem plugins — then visualizes everything in one place.

No manual setup. Run one command, see your entire dev infrastructure.

---

## What It Looks Like

```
+---------------------------------------------------------------+
|  Agent Command Center                          [Search...]     |
+----------+----------------------------------------------------+
|          |  Overview                                           |
| Overview |  +--------+ +--------+ +--------+ +--------+       |
| Betting  |  |Projects| |Agents  | |Cron    | |MCP     |       |
| OpenClaw |  |   5    | |  12    | |   8    | |  14    |       |
| March M. |  +--------+ +--------+ +--------+ +--------+       |
| Projects |                                                     |
| GitHub   |  Project Grid                                       |
| Automate |  +------------------+ +------------------+          |
| Ecosystm |  | betting-analyzer | | march-madness    |          |
|          |  | Flask / SQLite   | | Python / React   |          |
|          |  | 3 agents, 2 cron | | 1 agent, 1 cron  |          |
|          |  +------------------+ +------------------+          |
|          |                                                     |
|          |  Relationship Map (force-directed graph)            |
|          |        openclaw ---data---> betting                  |
|          |            \                  |                      |
|          |          trigger          publishes                  |
|          |              \              |                        |
|          |            discord       moltbook                   |
|          |                                                     |
+----------+----------------------------------------------------+
```

### Tab Views

| Tab | What You See |
|-----|-------------|
| **Overview** | Stats bar, project grid, force-directed relationship map |
| **Project Tabs** | Per-project detail: agents, schedulers, cron jobs, integration tree |
| **Projects** | All projects grouped by category |
| **GitHub Repos** | Git-tracked repos with remote URLs and status |
| **All Automations** | Every agent, scheduler, cron job, and script with filters |
| **Developer Ecosystem** | Claude commands, skills, MCP servers, hooks, marketplace plugins |

### Cards

Each entity gets a card with status, metadata, and tags:

```
+----------------------------------+
|  Nimrod Scheduler           [ON] |
|  Schedule: 11:55am EST daily     |
|  Type: cron  |  Project: betting |
|  [Python] [AI] [Scheduler]       |
+----------------------------------+
```

### Relationship Map

Force-directed SVG graph with curved edges, color-coded by type:

- **Blue** — data flow
- **Amber** — trigger
- **Green** — publish
- **Purple** — extends

Center node is configurable via `daav.config.json`.

---

## Quick Start

```bash
git clone https://github.com/seang1121/developer-automation-agent-visualizer.git
cd developer-automation-agent-visualizer
npm install
npm run dev
```

Opens at [http://localhost:3100](http://localhost:3100) with sample "Acme Labs" data.

---

## Auto-Discovery

ACC isn't a template you manually fill in. It scans your system automatically.

### With the CLI

```
/setup-daav
```

This slash command scans your local system for:
- AI commands, agents, and skills
- MCP servers and hooks from `~/.claude/settings.json`
- Git repos in your home directory
- Project metadata from `package.json`, `pyproject.toml`
- Cron jobs, schedulers, and automation scripts
- Cross-project relationships

All discovered data is written to `src/data/*.json` and a `daav.config.json` is generated.

---

## Project Structure

```
developer-automation-agent-visualizer/
├── public/
│   └── favicon.svg
├── scripts/
│   ├── dashboard_auto_sync.py      # Auto-sync on session end
│   └── init-data.ts                # Creates example data if missing
├── src/
│   ├── components/
│   │   ├── cards/                   # Entity cards (8 card types)
│   │   │   ├── AgentCard.tsx
│   │   │   ├── ClaudeToolCard.tsx
│   │   │   ├── CronJobCard.tsx
│   │   │   ├── MarketplacePluginCard.tsx
│   │   │   ├── McpCard.tsx
│   │   │   ├── ProjectDetailCard.tsx
│   │   │   ├── RepoCard.tsx
│   │   │   ├── SchedulerCard.tsx
│   │   │   └── ScriptCard.tsx
│   │   ├── layout/                  # Shell components
│   │   │   ├── CardGrid.tsx
│   │   │   ├── Header.tsx
│   │   │   ├── SearchBar.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── SidebarItem.tsx
│   │   ├── overview/                # Overview tab components
│   │   │   ├── OverviewTab.tsx
│   │   │   ├── ProjectGrid.tsx
│   │   │   ├── ProjectSummaryCard.tsx
│   │   │   ├── RelationshipMap.tsx  # Force-directed SVG graph
│   │   │   └── StatsBar.tsx
│   │   ├── shared/                  # Reusable UI primitives
│   │   │   ├── FilterBar.tsx
│   │   │   ├── InfoRow.tsx
│   │   │   ├── IntegrationTree.tsx
│   │   │   ├── SectionBlock.tsx
│   │   │   ├── StatusBadge.tsx
│   │   │   ├── TagPill.tsx
│   │   │   └── TechBadge.tsx
│   │   └── tabs/                    # Tab views (5 tabs)
│   │       ├── AutomationsTab.tsx
│   │       ├── ClaudeEcosystemTab.tsx
│   │       ├── GitHubReposTab.tsx
│   │       ├── ProjectDetailTab.tsx
│   │       └── ProjectsTab.tsx
│   ├── config/
│   │   ├── icons.ts                 # Icon registry
│   │   └── loader.ts               # Config file loader
│   ├── data/                        # 11 JSON data files + examples
│   │   ├── agents.json
│   │   ├── schedulers.json
│   │   ├── cron-jobs.json
│   │   ├── repos.json
│   │   ├── infrastructure.json
│   │   ├── marketplace-plugins.json
│   │   ├── projects.json
│   │   ├── claude-tools.json
│   │   ├── archived.json
│   │   ├── relationships.json
│   │   └── descriptions.json
│   ├── hooks/
│   │   └── useDashboardData.ts      # Central data hook
│   ├── layout/
│   │   └── forceLayout.ts           # Force-directed graph physics
│   ├── types/
│   │   ├── agents.ts
│   │   ├── config.ts
│   │   └── dashboard.ts
│   ├── utils/
│   │   └── formatters.ts
│   ├── App.tsx                      # Root component
│   ├── main.tsx                     # Entry point
│   └── index.css                    # Tailwind styles
├── daav.config.json                 # Dashboard layout config
├── daav.config.example.json
├── vite.config.ts
├── tsconfig.json
└── package.json
```

---

## Architecture

```
                         daav.config.json
                              |
11 JSON data files ──> useDashboardData hook ──> App.tsx
                                                   |
                              +--------------------+--------------------+
                              |                    |                    |
                           Sidebar              Header              Tab Views
                        (config-driven)       (search bar)             |
                                                        +--------------+--------------+
                                                        |              |              |
                                                   OverviewTab    ProjectTab    AutomationsTab
                                                        |              |              |
                                                   StatsBar      IntegTree      FilterBar
                                                   ProjGrid      CardGrid       CardGrid
                                                   RelMap            |              |
                                                                  [Cards]       [Cards]
```

### Data Flow

1. `/setup-daav` scans your system and writes 11 JSON files to `src/data/`
2. `useDashboardData` loads all JSON + `daav.config.json` into a single state object
3. `App.tsx` reads config to build sidebar tabs and routes content
4. Each tab renders cards, grids, and trees from the shared data
5. `RelationshipMap` computes a force-directed layout from `relationships.json`

---

## Configuration

`daav.config.json` controls the dashboard layout:

```json
{
  "title": "My Command Center",
  "projectTabs": [
    { "projectId": "my-project", "label": "My Project", "icon": "bot" }
  ],
  "centerNode": "my-project"
}
```

### Available Icons

`overview`, `projects`, `github`, `automations`, `claude`, `bot`, `chart`, `dollar`, `sun`, `server`, `database`, `wrench`, `globe`

### Project-Specific Config

```json
{
  "projects": [
    {
      "projectId": "my-project",
      "infrastructure": [
        { "label": "Runtime", "value": "Python 3.12" }
      ],
      "agentCategories": [
        { "key": "analysis", "title": "Analysis Agents" }
      ]
    }
  ]
}
```

---

## Data Files

| File | Contents |
|------|----------|
| `agents.json` | AI agent definitions |
| `schedulers.json` | Cron/daemon scheduler configs |
| `cron-jobs.json` | Cron job registry |
| `repos.json` | GitHub repositories |
| `infrastructure.json` | MCP servers, hooks, scripts |
| `marketplace-plugins.json` | Marketplace plugins |
| `projects.json` | Project metadata |
| `claude-tools.json` | CLI tools |
| `archived.json` | Historical project snapshots |
| `relationships.json` | Project relationship graph edges |
| `descriptions.json` | Section descriptions |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | React 19 |
| Language | TypeScript 5.9 (strict) |
| Styling | Tailwind CSS 4.2 (dark theme) |
| Bundler | Vite 8 |
| Graph | Custom force-directed SVG layout |
| Backend | None — all data in local JSON |

---

## License

MIT

# DAAV — Developer, Automation & Agent Visualizer

A self-configuring dashboard that auto-discovers your developer tools, AI agents, MCP servers, cron jobs, and Claude ecosystem plugins — then visualizes everything in one place.

## Quick Start

```bash
git clone https://github.com/seang1121/developer-automation-agent-visualizer.git
cd developer-automation-agent-visualizer
npm install
npm run dev
```

Opens at [http://localhost:3100](http://localhost:3100) with sample "Acme Labs" data.

## Auto-Discovery

DAAV isn't a template you manually fill in. It scans your system automatically.

### With Claude Code

```
/setup-daav
```

This slash command scans your local system for:
- Claude Code commands, agents, and skills
- MCP servers and hooks from `~/.claude/settings.json`
- Git repos in your home directory
- Project metadata from `CLAUDE.md`, `package.json`, `pyproject.toml`
- Cron jobs, schedulers, and automation scripts
- Cross-project relationships

All discovered data is written to `src/data/*.json` and a `daav.config.json` is generated.

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

## Architecture

```
11 JSON files --> useDashboardData hook --> App (config-driven tabs) --> Tab views
                                                                    --> Integration trees
                                                                    --> Relationship map (force-directed)
```

### Data Files

| File | Contents |
|------|----------|
| `agents.json` | AI agent definitions |
| `schedulers.json` | Cron/daemon scheduler configs |
| `cron-jobs.json` | Cron job registry |
| `repos.json` | GitHub repositories |
| `infrastructure.json` | MCP servers, hooks, scripts |
| `marketplace-plugins.json` | Claude marketplace plugins |
| `projects.json` | Project metadata |
| `claude-tools.json` | Claude CLI tools |
| `archived.json` | Historical project snapshots |
| `relationships.json` | Project relationship graph edges |
| `descriptions.json` | Section descriptions |

### Tabs

- **Overview** — Stats, project grid, force-directed relationship map
- **Project Tabs** — Config-driven, one per project with integration tree
- **Projects** — All projects by category
- **GitHub Repos** — Git-tracked projects with remote URLs
- **All Automations** — Agents, schedulers, cron jobs, scripts with filters
- **Claude Ecosystem** — Commands, agents, skills, MCP servers, plugins, hooks

## Tech Stack

- React 19 + TypeScript 5.9 (strict mode)
- Tailwind CSS 4.2 (dark theme)
- Vite 8
- No backend — all data in local JSON

## License

MIT

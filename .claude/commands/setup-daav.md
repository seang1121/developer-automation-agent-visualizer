# /setup-daav — Auto-Discovery Scanner

Scan this system to discover and populate all DAAV dashboard data. Follow these steps exactly:

## Step 1: Discover Claude Tools
Scan `~/.claude/commands/`, `~/.claude/agents/`, `~/.claude/skills/` for custom Claude Code tools.
For each file found, create an entry in `src/data/claude-tools.json`:
```json
{ "name": "<filename without extension>", "type": "<command|agent|skill>", "filePath": "<relative path>", "description": "<first line of file content>" }
```

## Step 2: Discover MCP Servers & Hooks
Read `~/.claude/settings.json` to find configured MCP servers and hooks.
Write MCP servers to `src/data/infrastructure.json` under `mcpServers`.
Write hooks to `src/data/infrastructure.json` under `hooks`.

## Step 3: Discover Marketplace Plugins
Check `~/.claude/plugins/` or the Claude Code marketplace settings for installed plugins.
Write to `src/data/marketplace-plugins.json`.

## Step 4: Discover Projects
Scan the home directory for top-level directories containing `.git/`.
For each project found:
1. Read `CLAUDE.md` if present for project description
2. Read `package.json` or `pyproject.toml` for tech stack
3. Check for GitHub remote URL with `git remote get-url origin`
4. Create entry in `src/data/projects.json`

## Step 5: Discover Automations
For each discovered project, scan for:
- **Agents**: Files matching `*agent*.py`, `*agent*.ts` in `src/` directories
- **Schedulers**: Files matching `*scheduler*`, `*cron*` patterns
- **Scripts**: `.bat`, `.sh`, `.py` files in `scripts/` directories
- **Cron jobs**: Look for crontab entries, PM2 configs, GitHub Actions workflows

Write agents to `src/data/agents.json`, schedulers to `src/data/schedulers.json`,
cron jobs to `src/data/cron-jobs.json`, scripts to `infrastructure.json` under `scripts`.

## Step 6: Discover Relationships
Analyze project cross-references:
- Check `relatedProjects` in CLAUDE.md files
- Check import statements that reference other projects
- Check API calls between projects
Write to `src/data/relationships.json`.

## Step 7: Discover Repos
For projects with GitHub remotes, create entries in `src/data/repos.json`.

## Step 8: Generate Config
Create `daav.config.json` with:
- `title`: "Developer Command Center" (or from user preference)
- `projectTabs`: one entry per active project with >2 automations
- `centerNode`: project with most relationships

## Step 9: Generate Archived
Check for `~/repos/` directory with old project snapshots.
Write to `src/data/archived.json`.

## Step 10: Write Descriptions
Generate `src/data/descriptions.json` with section descriptions based on discovered data.

After completing all steps, report:
- Number of projects found
- Number of agents, schedulers, cron jobs, scripts discovered
- Number of MCP servers and hooks detected
- Number of relationships mapped
- Confirm `daav.config.json` was generated

Then instruct the user to run `npm run dev` to see their dashboard.

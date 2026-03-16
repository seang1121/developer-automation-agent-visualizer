"""Dashboard Auto-Sync Script

Scans filesystem for Claude tools, plugins, hooks, repos, agents, schedulers,
scripts, and cron jobs. Compares against DAAV JSON data files and auto-updates
any that have drifted. Designed to run fast (<5s) as a Stop hook.

Exit codes:
  0 = no changes or changes applied successfully
  1 = error during sync
"""

import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime

HOME = Path(os.path.expanduser("~"))
DASH_DATA = HOME / "developer-automation-agent-visualizer" / "src" / "data"
CLAUDE_DIR = HOME / ".claude"
OPENCLAW_DIR = HOME / ".openclaw"
LOG_FILE = CLAUDE_DIR / "logs" / "dashboard-sync.log"

PLUGINS_BASE = CLAUDE_DIR / "plugins" / "marketplaces" / "claude-plugins-official"
IGNORED_PLUGINS = {
    "clangd-lsp", "claude-code-setup", "csharp-lsp", "example-plugin",
    "explanatory-output-style", "gopls-lsp", "hookify", "jdtls-lsp",
    "kotlin-lsp", "learning-output-style", "lua-lsp", "php-lsp",
    "playground", "plugin-dev", "ralph-loop", "ruby-lsp",
    "rust-analyzer-lsp", "skill-creator", "swift-lsp",
}

# Known project dirs to scan for agents/schedulers/scripts
AGENT_SCAN_PATHS = [
    (HOME / "betting-analyzer" / "src" / "agents", "betting-analyzer"),
    (OPENCLAW_DIR / "workspace", "openclaw"),
]
SCRIPT_SCAN_PATTERNS = [
    (HOME / "betting-analyzer", "*.bat", "betting-analyzer"),
    (OPENCLAW_DIR, "*.bat", "openclaw"),
    (OPENCLAW_DIR / "workspace", "*.py", "openclaw"),
]


def log(msg: str) -> None:
    """Append to sync log file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S EST")
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {msg}\n")
    except OSError:
        pass


def load_json(path: Path) -> list | dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_json(path: Path, data: list | dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def read_frontmatter(filepath: Path) -> dict:
    """Extract YAML-ish frontmatter from .md files."""
    result = {}
    try:
        text = filepath.read_text(encoding="utf-8", errors="ignore")
        match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
        if match:
            for line in match.group(1).splitlines():
                if ":" in line:
                    key, val = line.split(":", 1)
                    result[key.strip()] = val.strip()
        elif text.strip():
            result["description"] = text.strip().splitlines()[0][:120]
    except OSError:
        pass
    return result


def first_line_description(filepath: Path) -> str:
    """Get first meaningful line from a file as description."""
    try:
        text = filepath.read_text(encoding="utf-8", errors="ignore")
        for line in text.splitlines():
            stripped = line.strip().lstrip("#").lstrip("\"'").strip()
            if stripped and not stripped.startswith("---") and not stripped.startswith("import"):
                return stripped[:120]
    except OSError:
        pass
    return f"Auto-detected: {filepath.name}"


# ---------------------------------------------------------------------------
# Sync: Claude Tools (commands + agents)
# ---------------------------------------------------------------------------
def sync_claude_tools() -> list[str]:
    changes = []
    json_path = DASH_DATA / "claude-tools.json"
    tools = load_json(json_path)
    if not isinstance(tools, list):
        return changes

    existing = {(t["name"], t["type"]) for t in tools}

    # Built-in agents (always present)
    builtins = {"general-purpose", "Explore", "Plan", "claude-code-guide"}

    for tool_type in ["command", "agent"]:
        dir_path = CLAUDE_DIR / f"{tool_type}s"
        if not dir_path.exists():
            continue
        for f in dir_path.glob("*.md"):
            name = f.stem
            if (name, tool_type) not in existing and name not in builtins:
                fm = read_frontmatter(f)
                entry = {
                    "name": name,
                    "type": tool_type,
                    "filePath": f"~/.claude/{tool_type}s/{f.name}",
                    "description": fm.get("description", first_line_description(f)),
                }
                tools.append(entry)
                changes.append(f"+ claude-tools: added {tool_type} '{name}'")

    # Check for removed items
    on_disk_commands = set()
    cmd_dir = CLAUDE_DIR / "commands"
    if cmd_dir.exists():
        on_disk_commands = {f.stem for f in cmd_dir.glob("*.md")}

    on_disk_agents = set()
    agent_dir = CLAUDE_DIR / "agents"
    if agent_dir.exists():
        on_disk_agents = {f.stem for f in agent_dir.glob("*.md")}

    to_remove = []
    for i, t in enumerate(tools):
        if t.get("filePath") == "built-in":
            continue
        if t["type"] == "command" and t["name"] not in on_disk_commands:
            to_remove.append(i)
            changes.append(f"- claude-tools: removed command '{t['name']}'")
        elif t["type"] == "agent" and t["name"] not in on_disk_agents and t["name"] not in builtins:
            to_remove.append(i)
            changes.append(f"- claude-tools: removed agent '{t['name']}'")

    for i in reversed(to_remove):
        tools.pop(i)

    if changes:
        save_json(json_path, tools)
    return changes


# ---------------------------------------------------------------------------
# Sync: Infrastructure hooks
# ---------------------------------------------------------------------------
def sync_infrastructure_hooks() -> list[str]:
    changes = []
    json_path = DASH_DATA / "infrastructure.json"
    infra = load_json(json_path)
    if not isinstance(infra, dict):
        return changes

    hooks_list = infra.get("hooks", [])
    existing_hook_names = {h["name"] for h in hooks_list}

    # Build disk hooks from TWO sources:
    # 1. Hook files on disk (~/.claude/hooks/*.sh, *.py)
    # 2. settings.json for event/matcher metadata
    disk_hook_names: set[str] = set()
    hooks_dir = CLAUDE_DIR / "hooks"
    if hooks_dir.exists():
        for f in hooks_dir.iterdir():
            if f.suffix in (".sh", ".py") and not f.name.startswith("."):
                disk_hook_names.add(f.stem)

    # Read settings.json for event/matcher info on registered hooks
    settings_hooks_meta: dict[str, dict] = {}
    settings_path = CLAUDE_DIR / "settings.json"
    try:
        with open(settings_path, "r", encoding="utf-8") as f:
            settings = json.load(f)
        for event, hook_groups in settings.get("hooks", {}).items():
            for group in hook_groups:
                matcher = group.get("matcher", "")
                for hook_def in group.get("hooks", []):
                    cmd = hook_def.get("command", "")
                    name_match = re.search(r"hooks/([^.]+)\.\w+", cmd)
                    if name_match:
                        name = name_match.group(1)
                        settings_hooks_meta[name] = {
                            "event": event,
                            "matcher": matcher,
                            "command": cmd,
                        }
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    # Add new hooks found on disk
    for name in sorted(disk_hook_names - existing_hook_names):
        meta = settings_hooks_meta.get(name, {})
        # Detect file extension for command
        hook_file = hooks_dir / f"{name}.sh"
        if not hook_file.exists():
            hook_file = hooks_dir / f"{name}.py"
        runner = "bash" if hook_file.suffix == ".sh" else "python3"
        entry = {
            "name": name,
            "event": meta.get("event", "Unknown"),
            "command": meta.get("command", f"{runner} ~/.claude/hooks/{hook_file.name}"),
            "description": f"Auto-detected hook: {name}",
            "project": "system",
        }
        if meta.get("matcher"):
            entry["matcher"] = meta["matcher"]
        hooks_list.append(entry)
        changes.append(f"+ infrastructure.hooks: added '{name}'")

    # Remove hooks no longer on disk
    to_remove = []
    for i, h in enumerate(hooks_list):
        if h["name"] not in disk_hook_names:
            to_remove.append(i)
            changes.append(f"- infrastructure.hooks: removed '{h['name']}'")

    for i in reversed(to_remove):
        hooks_list.pop(i)

    if changes:
        infra["hooks"] = hooks_list
        save_json(json_path, infra)
    return changes


# ---------------------------------------------------------------------------
# Sync: Git repos
# ---------------------------------------------------------------------------
def sync_repos() -> list[str]:
    changes = []
    json_path = DASH_DATA / "repos.json"
    repos = load_json(json_path)
    if not isinstance(repos, list):
        return changes

    existing_names = {r["name"] for r in repos}

    disk_repos = set()
    for entry in HOME.iterdir():
        try:
            if entry.is_dir() and (entry / ".git").exists():
                disk_repos.add(entry.name)
        except PermissionError:
            continue

    # Add new repos
    for name in sorted(disk_repos - existing_names):
        entry = {
            "name": name,
            "url": "",
            "visibility": "private",
            "description": f"Auto-detected repository: {name}",
            "agentCount": 0,
            "automationCount": 0,
            "project": "unknown",
        }
        repos.append(entry)
        changes.append(f"+ repos: added '{name}'")

    # Remove repos no longer on disk
    to_remove = []
    for i, r in enumerate(repos):
        if r["name"] not in disk_repos:
            to_remove.append(i)
            changes.append(f"- repos: removed '{r['name']}'")

    for i in reversed(to_remove):
        repos.pop(i)

    if changes:
        save_json(json_path, repos)
    return changes


# ---------------------------------------------------------------------------
# Sync: Marketplace plugins
# ---------------------------------------------------------------------------
def sync_plugins() -> list[str]:
    changes = []
    json_path = DASH_DATA / "marketplace-plugins.json"
    plugins = load_json(json_path)
    if not isinstance(plugins, list):
        return changes

    existing_names = {p["name"].lower().replace(" ", "-") for p in plugins}

    # Scan filesystem plugins
    disk_plugins: set[str] = set()
    for subdir in ["external_plugins", "plugins"]:
        plugins_dir = PLUGINS_BASE / subdir
        if plugins_dir.exists():
            for entry in plugins_dir.iterdir():
                if entry.is_dir() and not entry.name.startswith("."):
                    name = entry.name.lower()
                    if name not in IGNORED_PLUGINS:
                        disk_plugins.add(name)

    # Also check enabledPlugins in settings.json
    settings_path = CLAUDE_DIR / "settings.json"
    try:
        with open(settings_path, "r", encoding="utf-8") as f:
            settings = json.load(f)
        for key, enabled in settings.get("enabledPlugins", {}).items():
            if enabled:
                name = key.split("@")[0].lower()
                if name not in IGNORED_PLUGINS:
                    disk_plugins.add(name)
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    # Add new plugins
    for name in sorted(disk_plugins - existing_names):
        display_name = name.replace("-", " ").title()
        entry = {
            "name": display_name,
            "kind": "skill",
            "installed": True,
            "installs": 0,
            "description": f"Auto-detected plugin: {display_name}",
        }
        plugins.append(entry)
        changes.append(f"+ marketplace-plugins: added '{display_name}'")

    if changes:
        save_json(json_path, plugins)
    return changes


# ---------------------------------------------------------------------------
# Sync: Cron jobs (from OpenClaw jobs.json)
# ---------------------------------------------------------------------------
def sync_cron_jobs() -> list[str]:
    changes = []
    json_path = DASH_DATA / "cron-jobs.json"
    cron_jobs = load_json(json_path)
    if not isinstance(cron_jobs, list):
        return changes

    existing_ids = {j.get("id") for j in cron_jobs}
    existing_names = {j.get("name") for j in cron_jobs}

    # Read OpenClaw jobs
    openclaw_jobs_path = OPENCLAW_DIR / "cron" / "jobs.json"
    openclaw_data = load_json(openclaw_jobs_path)
    if isinstance(openclaw_data, dict):
        openclaw_jobs = openclaw_data.get("jobs", [])
    else:
        openclaw_jobs = openclaw_data

    disk_job_ids = set()
    disk_job_names = set()
    for job in openclaw_jobs:
        if not job.get("enabled", False):
            continue
        job_id = job.get("id", "")
        job_name = job.get("name", "")
        disk_job_ids.add(job_id)
        disk_job_names.add(job_name)

        if job_id not in existing_ids and job_name not in existing_names:
            schedule = job.get("schedule", {})
            entry = {
                "id": job_id,
                "name": job_name,
                "enabled": True,
                "cron": schedule.get("expr", ""),
                "timezone": schedule.get("tz", "America/New_York"),
                "delivery": "",
                "status": "active",
                "errorCount": 0,
                "project": job.get("project", "openclaw"),
                "category": job.get("category", "unknown"),
                "description": job.get("payload", {}).get("message", "")[:120] or f"Auto-detected cron job: {job_name}",
            }
            # Build delivery string
            delivery = job.get("delivery", {})
            if delivery.get("channel") == "discord":
                entry["delivery"] = f"Discord ch.{delivery.get('to', '')}"
            elif delivery.get("mode") == "silent":
                entry["delivery"] = "Silent"
            cron_jobs.append(entry)
            changes.append(f"+ cron-jobs: added '{job_name}'")

    # Remove jobs no longer in OpenClaw — but only auto-detected ones
    # (OpenClaw IDs are UUIDs with dashes; hand-curated entries like "icc-weekly"
    # are short slugs and should never be auto-removed)
    to_remove = []
    for i, j in enumerate(cron_jobs):
        jid = j.get("id", "")
        jname = j.get("name", "")
        # Only remove if it looks like an OpenClaw UUID and is no longer there
        is_uuid = len(jid) > 20 and "-" in jid
        if is_uuid and jid not in disk_job_ids and jname not in disk_job_names:
            to_remove.append(i)
            changes.append(f"- cron-jobs: removed '{jname}'")

    for i in reversed(to_remove):
        cron_jobs.pop(i)

    if changes:
        save_json(json_path, cron_jobs)
    return changes


# ---------------------------------------------------------------------------
# Sync: Agents (from known project dirs)
# ---------------------------------------------------------------------------
def sync_agents() -> list[str]:
    changes = []
    json_path = DASH_DATA / "agents.json"
    agents = load_json(json_path)
    if not isinstance(agents, list):
        return changes

    existing_modules = {a.get("module", "") for a in agents}

    # Skip base classes and __init__ files
    agent_skip_patterns = {"base_agent", "__init__", "agent_utils", "agent_config"}

    for scan_dir, project in AGENT_SCAN_PATHS:
        if not scan_dir.exists():
            continue
        for f in scan_dir.glob("*agent*.py"):
            if f.stem in agent_skip_patterns:
                continue
            # Build relative module path
            try:
                rel = f.relative_to(HOME)
                module = str(rel).replace("\\", "/")
            except ValueError:
                module = f.name

            # Check against existing modules (normalize slashes)
            module_normalized = module.replace("\\", "/")
            if any(module_normalized.endswith(m.replace("\\", "/")) or m.replace("\\", "/").endswith(module_normalized) for m in existing_modules):
                continue

            # New agent found
            name = f.stem.replace("_", " ").title().replace(" ", "")
            desc = first_line_description(f)
            entry = {
                "name": name,
                "type": "sequential",
                "purpose": desc,
                "weight": None,
                "scoreRange": None,
                "dataSources": [],
                "module": module,
                "status": "active",
                "project": project,
                "category": "auto-detected",
            }
            agents.append(entry)
            changes.append(f"+ agents: added '{name}' from {module}")

    if changes:
        save_json(json_path, agents)
    return changes


# ---------------------------------------------------------------------------
# Sync: Schedulers
# ---------------------------------------------------------------------------
# Note: schedulers.json entries are hand-curated with detailed schedules,
# descriptions, and categories. The scheduler Python files on disk are the
# implementation files for these entries. We don't auto-detect new schedulers
# from filesystem because they'd duplicate existing curated entries under
# different names. New schedulers should be added via /scan-dashboard.


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    all_changes: list[str] = []
    try:
        all_changes.extend(sync_claude_tools())
        all_changes.extend(sync_infrastructure_hooks())
        all_changes.extend(sync_repos())
        all_changes.extend(sync_plugins())
        all_changes.extend(sync_cron_jobs())
        all_changes.extend(sync_agents())
    except Exception as e:
        log(f"ERROR: {e}")
        print(f"dashboard-auto-sync error: {e}", file=sys.stderr)
        return 1

    if all_changes:
        log(f"Applied {len(all_changes)} changes:")
        for c in all_changes:
            log(f"  {c}")
        print(f"dashboard-auto-sync: {len(all_changes)} changes applied")
        for c in all_changes:
            print(f"  {c}")
    else:
        log("No drift detected")

    return 0


if __name__ == "__main__":
    sys.exit(main())

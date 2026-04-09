"""Scan skill directories and extract graph data."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class Skill:
    name: str
    description: str
    content: str
    path: Path
    calls: list[str] = field(default_factory=list)
    services: list[str] = field(default_factory=list)


@dataclass
class ServicePattern:
    name: str
    patterns: list[str]


# Well-known MCP server name fragments -> friendly display name
_MCP_NAME_MAP = {
    "slack": "Slack",
    "jira": "Jira",
    "atlassian": "Jira",
    "google-calendar": "Google Calendar",
    "gcal": "Google Calendar",
    "notion": "Notion",
    "incident": "incident.io",
    "gitlab": "GitLab",
    "github": "GitHub",
    "linear": "Linear",
    "sentry": "Sentry",
    "datadog": "Datadog",
    "pagerduty": "PagerDuty",
    "opsgenie": "OpsGenie",
    "confluence": "Confluence",
    "asana": "Asana",
    "monday": "Monday",
    "discord": "Discord",
    "teams": "Microsoft Teams",
    "gmail": "Gmail",
    "drive": "Google Drive",
    "sheets": "Google Sheets",
    "postgres": "PostgreSQL",
    "mysql": "MySQL",
    "redis": "Redis",
    "firebase": "Firebase",
    "supabase": "Supabase",
    "aws": "AWS",
    "gcp": "GCP",
    "azure": "Azure",
    "vercel": "Vercel",
    "netlify": "Netlify",
    "stripe": "Stripe",
    "twilio": "Twilio",
}


def discover_mcp_servers(claude_dir: Path | None = None) -> dict[str, str]:
    """Discover MCP servers from Claude settings files.

    Returns a dict of server_key -> friendly_name.
    """
    if claude_dir is None:
        claude_dir = Path.home() / ".claude"

    servers: dict[str, str] = {}
    candidates = [
        claude_dir / "settings.json",
        claude_dir / "settings.local.json",
        Path.home() / ".claude.json",
    ]

    for path in candidates:
        if not path.exists():
            continue
        try:
            with open(path) as f:
                cfg = json.load(f)
            for key in cfg.get("mcpServers", {}):
                # Try to map to a friendly name
                key_lower = key.lower().replace("_", "-")
                friendly = None
                for fragment, name in _MCP_NAME_MAP.items():
                    if fragment in key_lower:
                        friendly = name
                        break
                servers[key] = friendly or key
        except (json.JSONDecodeError, KeyError):
            continue

    return servers


def load_service_patterns(
    config_path: Path | None = None,
    claude_dir: Path | None = None,
) -> list[ServicePattern]:
    """Load service detection patterns.

    Merges three sources (in priority order):
    1. User config YAML (if provided)
    2. Auto-detected MCP server names from Claude settings
    3. Built-in defaults for common tools
    """
    patterns = _default_service_patterns()
    known_names = {p.name for p in patterns}

    # Add MCP-derived patterns
    mcp_servers = discover_mcp_servers(claude_dir)
    for server_key, friendly_name in mcp_servers.items():
        if friendly_name not in known_names:
            # Create a pattern from the server key
            patterns.append(
                ServicePattern(
                    name=friendly_name,
                    patterns=[server_key.lower(), friendly_name.lower()],
                )
            )
            known_names.add(friendly_name)

    # Override with user config if provided
    if config_path and config_path.exists():
        with open(config_path) as f:
            cfg = yaml.safe_load(f)
        for svc in cfg.get("services", []):
            name = svc["name"]
            if name in known_names:
                # Replace existing
                patterns = [p for p in patterns if p.name != name]
            patterns.append(ServicePattern(name=name, patterns=svc["patterns"]))
            known_names.add(name)

    return patterns


def _default_service_patterns() -> list[ServicePattern]:
    return [
        ServicePattern(
            "Slack",
            [
                "slack mcp",
                "slack_",
                "slack channel",
                "slack search",
                "slack_send_message",
                "slack_read_channel",
            ],
        ),
        ServicePattern("Jira", ["jira mcp", "jira ticket", "jira search", "atlassian"]),
        ServicePattern(
            "Google Calendar",
            ["google calendar", "gcal_", "calendar events", "list_gcal"],
        ),
        ServicePattern(
            "Notion",
            [
                "notion mcp",
                "notion search",
                "notion-search",
                "notion page",
                "notion calendar",
                "notion-fetch",
                "notion.so",
            ],
        ),
        ServicePattern("incident.io", ["incident.io", "on-call schedule", "incident_"]),
        ServicePattern("GitLab", ["glab ", "gitlab", "merge request", "glab mr"]),
        ServicePattern("GitHub", ["github", "gh pr", "gh issue"]),
        ServicePattern(
            "Obsidian CLI",
            ["obsidian cli", "obsidian create", "obsidian append", "obsidian read"],
        ),
    ]


def discover_skills(skills_dir: Path) -> list[Skill]:
    """Find and parse all SKILL.md files in the skills directory."""
    skills = []
    if not skills_dir.is_dir():
        return skills

    for entry in sorted(skills_dir.iterdir()):
        if not entry.is_dir():
            continue
        skill_file = entry / "SKILL.md"
        if not skill_file.exists():
            skill_file = entry / "skill.md"
        if not skill_file.exists():
            continue

        content = skill_file.read_text()
        name, description = _parse_frontmatter(content)
        if not name:
            name = entry.name

        skills.append(
            Skill(
                name=name,
                description=description,
                content=content,
                path=skill_file,
            )
        )

    return skills


def _parse_frontmatter(content: str) -> tuple[str, str]:
    """Extract name and description from YAML frontmatter."""
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return "", ""
    try:
        fm = yaml.safe_load(match.group(1))
        return fm.get("name", ""), fm.get("description", "")
    except yaml.YAMLError:
        return "", ""


def extract_calls(skill: Skill, all_skill_names: set[str]) -> list[str]:
    """Find cross-skill references in a skill's content."""
    calls = set()
    # Match /skill-name patterns
    for match in re.finditer(r"/([a-z][a-z0-9-]+)", skill.content):
        target = match.group(1)
        if target in all_skill_names and target != skill.name:
            calls.add(target)
    return sorted(calls)


def extract_services(skill: Skill, patterns: list[ServicePattern]) -> list[str]:
    """Detect which services a skill uses based on content patterns."""
    content_lower = skill.content.lower()
    matched = []
    for sp in patterns:
        if any(p.lower() in content_lower for p in sp.patterns):
            matched.append(sp.name)
    return matched


def build_graph(
    skills_dir: Path,
    config_path: Path | None = None,
    claude_dir: Path | None = None,
) -> tuple[list[Skill], list[ServicePattern]]:
    """Full pipeline: discover skills, extract calls and services."""
    service_patterns = load_service_patterns(config_path, claude_dir)
    skills = discover_skills(skills_dir)
    all_names = {s.name for s in skills}

    for skill in skills:
        skill.calls = extract_calls(skill, all_names)
        skill.services = extract_services(skill, service_patterns)

    return skills, service_patterns

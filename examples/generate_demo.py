"""Generate demo graph files for the README."""

from pathlib import Path

from skillviz.scanner import Skill
from skillviz.graph import render
from skillviz.html_renderer import render_html

EXAMPLES_DIR = Path(__file__).parent

SKILLS = [
    Skill(
        "morning-standup",
        "Gather updates and prep standup notes",
        "",
        Path("fake"),
        calls=["sync-calendar", "check-tickets"],
        services=["Slack", "Google Calendar"],
    ),
    Skill(
        "sync-calendar",
        "Pull today's meetings and prep context",
        "",
        Path("fake"),
        calls=[],
        services=["Google Calendar", "Notion"],
    ),
    Skill(
        "check-tickets",
        "Review assigned tickets and blockers",
        "",
        Path("fake"),
        calls=[],
        services=["Jira", "Slack"],
    ),
    Skill(
        "draft-pr",
        "Create a pull request from the current branch",
        "",
        Path("fake"),
        calls=["run-tests"],
        services=["GitHub"],
    ),
    Skill(
        "run-tests",
        "Execute test suite and report results",
        "",
        Path("fake"),
        calls=[],
        services=["GitHub"],
    ),
    Skill(
        "review-code",
        "Review a pull request and leave comments",
        "",
        Path("fake"),
        calls=[],
        services=["GitHub", "Slack"],
    ),
    Skill(
        "write-docs",
        "Generate or update documentation",
        "",
        Path("fake"),
        calls=[],
        services=["Notion"],
    ),
    Skill(
        "deploy",
        "Deploy the current release to staging or prod",
        "",
        Path("fake"),
        calls=["run-tests"],
        services=["GitHub", "Slack"],
    ),
    Skill(
        "incident-response",
        "Triage and coordinate during an incident",
        "",
        Path("fake"),
        calls=["check-tickets"],
        services=["Slack", "PagerDuty", "Jira"],
    ),
    Skill(
        "weekly-retro",
        "Compile notes and action items for the retro",
        "",
        Path("fake"),
        calls=["check-tickets", "sync-calendar"],
        services=["Notion", "Slack"],
    ),
    Skill(
        "brainstorm",
        "Facilitate a design discussion",
        "",
        Path("fake"),
        calls=[],
        services=["Notion"],
    ),
    Skill(
        "onboard-teammate",
        "Walk a new team member through the codebase",
        "",
        Path("fake"),
        calls=["write-docs"],
        services=["Slack", "Notion"],
    ),
]

CLUSTERS = {
    "Daily workflow": [
        "morning-standup",
        "sync-calendar",
        "check-tickets",
    ],
    "Engineering": ["draft-pr", "run-tests", "review-code", "deploy"],
    "Documentation": ["write-docs", "brainstorm"],
    "Team": ["weekly-retro", "onboard-teammate"],
    "Incident": ["incident-response"],
}


if __name__ == "__main__":
    # Graphviz SVG
    svg_path = render(SKILLS, EXAMPLES_DIR / "demo-graph", "svg", clusters=CLUSTERS)
    print(f"SVG: {svg_path}")

    # Interactive HTML
    html_path = render_html(SKILLS, EXAMPLES_DIR / "demo-graph.html", clusters=CLUSTERS)
    print(f"HTML: {html_path}")

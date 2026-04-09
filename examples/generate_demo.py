"""Generate demo graph files for the README."""

from pathlib import Path

from skillviz.scanner import Skill
from skillviz.graph import render
from skillviz.html_renderer import render_html

EXAMPLES_DIR = Path(__file__).parent

SKILLS = [
    Skill(
        "start-my-day",
        "Morning planning routine",
        "",
        Path("fake"),
        calls=["sync-meetings", "personal-assistant"],
        services=["Google Calendar", "Slack", "Jira"],
    ),
    Skill(
        "end-my-day",
        "End of day wrap-up",
        "",
        Path("fake"),
        calls=["sync-meetings", "braindump"],
        services=["Notion", "Slack", "Obsidian CLI"],
    ),
    Skill(
        "sync-meetings",
        "Pull meeting notes from Notion",
        "",
        Path("fake"),
        calls=[],
        services=["Notion", "Google Calendar"],
    ),
    Skill(
        "personal-assistant",
        "Calendar and action item tracking",
        "",
        Path("fake"),
        calls=[],
        services=["Google Calendar", "Slack"],
    ),
    Skill(
        "braindump",
        "Quick thought capture",
        "",
        Path("fake"),
        calls=[],
        services=["Obsidian CLI"],
    ),
    Skill(
        "tdd",
        "Test-driven development loop",
        "",
        Path("fake"),
        calls=[],
        services=["GitHub"],
    ),
    Skill(
        "create-mr",
        "Create a GitLab merge request",
        "",
        Path("fake"),
        calls=[],
        services=["GitLab"],
    ),
    Skill(
        "review-rfc",
        "Review an RFC from Notion",
        "",
        Path("fake"),
        calls=[],
        services=["Notion", "Slack"],
    ),
    Skill(
        "grill-me",
        "Stress-test a plan or design",
        "",
        Path("fake"),
        calls=[],
        services=[],
    ),
    Skill(
        "create-jira",
        "Turn ideas into Jira tickets",
        "",
        Path("fake"),
        calls=["grill-me"],
        services=["Jira"],
    ),
    Skill(
        "write-post-mortem",
        "Draft incident post-mortems",
        "",
        Path("fake"),
        calls=[],
        services=["Notion", "Slack", "incident.io"],
    ),
    Skill(
        "growth",
        "Track accomplishments against competency matrix",
        "",
        Path("fake"),
        calls=[],
        services=["Obsidian CLI"],
    ),
]

CLUSTERS = {
    "Daily routine": [
        "start-my-day",
        "end-my-day",
        "sync-meetings",
        "personal-assistant",
        "braindump",
    ],
    "Engineering": ["tdd", "create-mr", "review-rfc"],
    "Planning": ["grill-me", "create-jira"],
    "Incident": ["write-post-mortem"],
    "Growth": ["growth"],
}


if __name__ == "__main__":
    # Graphviz SVG
    svg_path = render(SKILLS, EXAMPLES_DIR / "demo-graph", "svg", clusters=CLUSTERS)
    print(f"SVG: {svg_path}")

    # Interactive HTML
    html_path = render_html(SKILLS, EXAMPLES_DIR / "demo-graph.html", clusters=CLUSTERS)
    print(f"HTML: {html_path}")

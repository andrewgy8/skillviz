"""Build and render a graphviz graph from scanned skill data."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

import graphviz

from .scanner import Skill


def _svc_id(name: str) -> str:
    """Create a graphviz-safe node ID for a service name."""
    return "svc_" + name.lower().replace(" ", "_").replace(".", "_").replace("-", "_")


def _compute_weights(skills: list[Skill]) -> dict[str, int]:
    """Compute connection weight per skill (in-degree + out-degree of cross-skill calls)."""
    counts: Counter[str] = Counter()
    for skill in skills:
        counts[skill.name] += len(skill.calls)
        for target in skill.calls:
            counts[target] += 1
    return dict(counts)


def _compute_edge_weight(skills: list[Skill]) -> dict[tuple[str, str], int]:
    """Count how many skills use each service (for edge thickness)."""
    svc_usage: Counter[str] = Counter()
    for skill in skills:
        for svc in skill.services:
            svc_usage[svc] += 1
    # Edge weight for service edges = how popular the service is
    weights = {}
    for skill in skills:
        for svc in skill.services:
            weights[(skill.name, svc)] = svc_usage[svc]
    return weights


def _penwidth(
    weight: int, min_w: float = 1.0, max_w: float = 5.0, max_count: int = 10
) -> str:
    """Scale a weight to a penwidth value."""
    if max_count <= 1:
        return str(min_w)
    scaled = min_w + (max_w - min_w) * min(weight, max_count) / max_count
    return f"{scaled:.1f}"


# Cluster colors (graphviz color names / hex)
CLUSTER_COLORS = {
    "Daily routine": "#E8B4B8",
    "Engineering": "#B8D4B8",
    "Planning & design": "#C4B8D4",
    "Incident": "#D4C4A8",
    "Utility": "#A8C8D4",
    "Meta": "#D4D4A8",
    "Uncategorized": "#D0D0D0",
}


def render(
    skills: list[Skill],
    output_path: Path,
    fmt: str = "svg",
    clusters: dict[str, list[str]] | None = None,
) -> Path:
    """Render the skill graph to a file.

    Args:
        skills: List of parsed skills with calls and services populated.
        output_path: Where to write the output (without extension).
        fmt: Output format (svg, png, pdf).
        clusters: Mapping of cluster name -> list of skill names.
            Skills not in any cluster go to "Uncategorized".

    Returns:
        Path to the rendered file.
    """
    skill_map = {s.name: s for s in skills}
    weights = _compute_weights(skills)
    edge_weights = _compute_edge_weight(skills)
    max_weight = max(weights.values()) if weights else 1

    # Collect all services that are actually used
    all_services = sorted({svc for s in skills for svc in s.services})

    dot = graphviz.Digraph(
        "skills",
        format=fmt,
        engine="dot",
    )
    dot.attr(
        rankdir="TB",
        bgcolor="white",
        fontname="Helvetica",
        pad="1.0",
        nodesep="0.6",
        ranksep="1.2",
        label="Claude Code Skills Graph",
        labelloc="t",
        fontsize="24",
    )

    # Default node style
    dot.attr(
        "node", shape="box", style="rounded,filled", fontname="Helvetica", fontsize="11"
    )
    dot.attr("edge", fontname="Helvetica", fontsize="9")

    # Build cluster membership lookup
    if clusters is None:
        clusters = {"Uncategorized": [s.name for s in skills]}

    skill_to_cluster = {}
    for cname, members in clusters.items():
        for m in members:
            skill_to_cluster[m] = cname

    # Add uncategorized for any skill not in a cluster
    uncategorized = [s.name for s in skills if s.name not in skill_to_cluster]
    if uncategorized:
        clusters["Uncategorized"] = clusters.get("Uncategorized", []) + uncategorized
        for m in uncategorized:
            skill_to_cluster[m] = "Uncategorized"

    # Render clustered skill nodes
    for cname, members in clusters.items():
        color = CLUSTER_COLORS.get(cname, "#D0D0D0")
        with dot.subgraph(name=f"cluster_{cname.replace(' ', '_')}") as sub:
            sub.attr(
                label=cname,
                style="rounded,filled",
                color=color,
                fillcolor=f"{color}40",
                fontsize="14",
                fontname="Helvetica Bold",
            )
            for sname in members:
                if sname not in skill_map:
                    continue
                w = weights.get(sname, 0)
                pw = _penwidth(w, 1.5, 4.0, max_weight)
                sub.node(
                    sname,
                    label=f"/{sname}",
                    fillcolor=color,
                    penwidth=pw,
                    tooltip=skill_map[sname].description[:120],
                )

    # Service nodes in their own cluster
    max_svc_weight = max(
        (sum(1 for s in skills if svc in s.services) for svc in all_services),
        default=1,
    )
    with dot.subgraph(name="cluster_services") as sub:
        sub.attr(
            label="Services & Integrations",
            style="rounded,dashed",
            color="#888888",
            fontsize="14",
            fontname="Helvetica Bold",
            rank="sink",
        )
        for svc in all_services:
            usage_count = sum(1 for s in skills if svc in s.services)
            pw = _penwidth(usage_count, 1.0, 4.0, max_svc_weight)
            sub.node(
                _svc_id(svc),
                label=svc,
                shape="ellipse",
                style="filled",
                fillcolor="#F0F0F0",
                penwidth=pw,
                fontsize="10",
            )

    # Cross-skill call edges
    for skill in skills:
        for target in skill.calls:
            if target in skill_map:
                dot.edge(
                    skill.name,
                    target,
                    label="calls",
                    color="#CC4444",
                    penwidth="2.0",
                    arrowsize="0.8",
                )

    # Service usage edges
    for skill in skills:
        for svc in skill.services:
            ew = edge_weights.get((skill.name, svc), 1)
            pw = _penwidth(ew, 0.5, 2.5, max_svc_weight)
            dot.edge(
                skill.name,
                _svc_id(svc),
                color="#888888",
                style="dashed",
                penwidth=pw,
                arrowsize="0.5",
            )

    # Render
    output_str = str(output_path)
    # graphviz appends the format extension automatically
    dot.render(output_str, cleanup=True)
    return Path(f"{output_str}.{fmt}")

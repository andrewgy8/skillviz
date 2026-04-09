"""CLI entry point for skillviz."""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

import yaml

from .scanner import build_graph
from .graph import render


def _load_clusters(config_path: Path | None) -> dict[str, list[str]] | None:
    """Load cluster config from YAML if present."""
    if config_path and config_path.exists():
        with open(config_path) as f:
            cfg = yaml.safe_load(f)
        clusters_cfg = cfg.get("clusters", {})
        if clusters_cfg:
            return {name: members for name, members in clusters_cfg.items()}
    return None


def _print_summary(skills, all_services):
    """Print a text summary of the graph."""
    n_skills = len(skills)
    call_edges = [(s.name, t) for s in skills for t in s.calls]
    n_calls = len(call_edges)

    # Busiest skill
    outgoing = {s.name: len(s.calls) for s in skills}
    busiest = max(outgoing, key=lambda k: outgoing[k]) if outgoing else "none"
    busiest_n = outgoing.get(busiest, 0)

    # Most connected service
    svc_counts: Counter[str] = Counter()
    for s in skills:
        for svc in s.services:
            svc_counts[svc] += 1
    top_svc = svc_counts.most_common(1)[0] if svc_counts else ("none", 0)

    # Orphans
    called_by = {t for s in skills for t in s.calls}
    callers = {s.name for s in skills if s.calls}
    orphans = [
        s.name for s in skills if s.name not in called_by and s.name not in callers
    ]

    print(f"\nSkills: {n_skills}")
    print(f"Services detected: {len(all_services)}")
    print(f"Cross-skill calls: {n_calls}")
    if busiest_n > 0:
        print(f"Busiest skill: {busiest} (calls {busiest_n} others)")
    if top_svc != ("none", 0):
        print(f"Most connected service: {top_svc[0]} (used by {top_svc[1]} skills)")
    if orphans:
        print(f"Standalone skills: {', '.join(orphans)}")


def main(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(
        prog="skillviz",
        description="Visualize Claude Code skills as a graph",
    )
    parser.add_argument(
        "--skills-dir",
        type=Path,
        default=Path.home() / ".claude" / "skills",
        help="Path to the skills directory (default: ~/.claude/skills)",
    )
    parser.add_argument(
        "--claude-dir",
        type=Path,
        default=Path.home() / ".claude",
        help="Path to Claude config directory for MCP server detection (default: ~/.claude)",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Optional config YAML to override service patterns or clusters",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("skill-graph"),
        help="Output file path without extension (default: ./skill-graph)",
    )
    parser.add_argument(
        "--format",
        "-f",
        choices=["svg", "png", "pdf"],
        default="svg",
        help="Output format (default: svg)",
    )

    args = parser.parse_args(argv)

    # Build graph (auto-detects MCP servers from Claude settings)
    skills, service_patterns = build_graph(
        args.skills_dir,
        args.config,
        args.claude_dir,
    )
    if not skills:
        print(f"No skills found in {args.skills_dir}", file=sys.stderr)
        sys.exit(1)

    # Load clusters from config (optional)
    clusters = _load_clusters(args.config)

    # Collect all services
    all_services = sorted({svc for s in skills for svc in s.services})

    # Render
    out = render(skills, args.output, args.format, clusters)
    print(f"Graph written to {out}")

    # Summary
    _print_summary(skills, all_services)


if __name__ == "__main__":
    main()

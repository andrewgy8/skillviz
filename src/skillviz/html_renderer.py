"""Render skill graph as a self-contained interactive HTML file using vis.js."""

from __future__ import annotations

import json
from pathlib import Path

from .graph import _compute_weights, _compute_edge_weight
from .scanner import Skill


_VIS_JS_PATH = Path(__file__).parent / "vis-network.min.js"


def _load_vis_js() -> str:
    return _VIS_JS_PATH.read_text()


def render_html(
    skills: list[Skill],
    output_path: Path,
    clusters: dict[str, list[str]] | None = None,
) -> Path:
    """Render the skill graph to an interactive HTML file.

    Args:
        skills: List of parsed skills with calls and services populated.
        output_path: Where to write the HTML file.
        clusters: Optional mapping of cluster name -> list of skill names.

    Returns:
        Path to the rendered HTML file.
    """
    nodes, edges = _build_graph_data(skills, clusters)
    vis_js = _load_vis_js()

    html = _HTML_TEMPLATE.format(
        vis_js=vis_js,
        nodes_json=json.dumps(nodes),
        edges_json=json.dumps(edges),
    )
    output_path.write_text(html)
    return output_path


def _build_graph_data(
    skills: list[Skill],
    clusters: dict[str, list[str]] | None = None,
) -> tuple[list[dict], list[dict]]:
    """Build vis.js nodes and edges from skill data."""
    skill_map = {s.name: s for s in skills}
    weights = _compute_weights(skills)
    edge_weights = _compute_edge_weight(skills)
    max_weight = max(weights.values()) if weights else 1

    # Build cluster lookup
    if clusters is None:
        clusters = {"Uncategorized": [s.name for s in skills]}
    skill_to_cluster: dict[str, str] = {}
    for cname, members in clusters.items():
        for m in members:
            skill_to_cluster[m] = cname
    for s in skills:
        if s.name not in skill_to_cluster:
            skill_to_cluster[s.name] = "Uncategorized"

    # Skill nodes
    nodes = []
    for skill in skills:
        w = weights.get(skill.name, 0)
        size = _scale(w, 20, 50, max_weight)
        nodes.append(
            {
                "id": skill.name,
                "label": skill.name,
                "title": skill.description,
                "group": skill_to_cluster.get(skill.name, "Uncategorized"),
                "size": size,
                "shape": "box",
            }
        )

    # Service nodes
    all_services = sorted({svc for s in skills for svc in s.services})
    for svc in all_services:
        nodes.append(
            {
                "id": f"svc_{svc}",
                "label": svc,
                "group": "Services",
                "shape": "ellipse",
                "size": 15,
            }
        )

    # Cross-skill call edges
    edges = []
    for skill in skills:
        for target in skill.calls:
            if target in skill_map:
                edges.append(
                    {
                        "from": skill.name,
                        "to": target,
                        "label": "calls",
                        "color": {"color": "#CC4444"},
                        "width": 2,
                        "arrows": "to",
                    }
                )

    # Service usage edges
    all_svc_max = max(edge_weights.values()) if edge_weights else 1
    for skill in skills:
        for svc in skill.services:
            ew = edge_weights.get((skill.name, svc), 1)
            width = _scale(ew, 0.5, 2.5, all_svc_max)
            edges.append(
                {
                    "from": skill.name,
                    "to": f"svc_{svc}",
                    "dashes": True,
                    "color": {"color": "#888888"},
                    "width": width,
                    "arrows": "to",
                }
            )

    return nodes, edges


def _scale(value: int, min_v: float, max_v: float, max_count: int) -> float:
    if max_count <= 0:
        return min_v
    return round(min_v + (max_v - min_v) * min(value, max_count) / max(max_count, 1), 1)


_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Claude Code Skills Graph</title>
<style>
  body {{ margin: 0; padding: 0; font-family: Helvetica, Arial, sans-serif; }}
  #graph {{ width: 100vw; height: 100vh; }}
</style>
<script type="text/javascript">
{vis_js}
</script>
</head>
<body>
<div id="graph"></div>
<script type="text/javascript">
  var nodes = new vis.DataSet({nodes_json});
  var edges = new vis.DataSet({edges_json});
  var container = document.getElementById("graph");
  var data = {{ nodes: nodes, edges: edges }};
  var options = {{
    physics: {{
      enabled: true,
      barnesHut: {{ gravitationalConstant: -3000, springLength: 150 }}
    }},
    interaction: {{
      hover: true,
      tooltipDelay: 200,
      zoomView: true,
      dragView: true
    }},
    groups: {{
      Services: {{
        shape: "ellipse",
        color: {{ background: "#F0F0F0", border: "#888888" }}
      }}
    }}
  }};
  var network = new vis.Network(container, data, options);
</script>
</body>
</html>
"""

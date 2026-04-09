"""Tests for the HTML renderer module."""

from pathlib import Path

from skillviz.scanner import Skill
from skillviz.html_renderer import render_html


def _make_skill(name, calls=None, services=None):
    return Skill(
        name=name,
        description=f"{name} skill",
        content="",
        path=Path("fake"),
        calls=calls or [],
        services=services or [],
    )


def test_render_html_produces_file(tmp_path):
    skills = [
        _make_skill("alpha", calls=["beta"], services=["Slack"]),
        _make_skill("beta", services=["Slack"]),
    ]
    out = render_html(skills, tmp_path / "skill-graph.html")
    assert out.exists()
    assert out.suffix == ".html"


def test_html_is_self_contained(tmp_path):
    skills = [_make_skill("alpha")]
    out = render_html(skills, tmp_path / "graph.html")
    content = out.read_text()
    # vis.js must be embedded inline, not loaded from CDN
    assert "vis-network" in content.lower() or "vis.Network" in content
    # No external script src references
    assert 'src="http' not in content


def test_skill_nodes_in_js_data(tmp_path):
    skills = [
        _make_skill("alpha", calls=["beta"]),
        _make_skill("beta"),
    ]
    out = render_html(skills, tmp_path / "graph.html")
    content = out.read_text()
    assert '"label": "alpha"' in content
    assert '"label": "beta"' in content


def test_service_nodes_distinct_group(tmp_path):
    skills = [_make_skill("alpha", services=["Slack"])]
    out = render_html(skills, tmp_path / "graph.html")
    content = out.read_text()
    # Service node exists with label
    assert '"label": "Slack"' in content
    # Service node is in "Services" group, skill node is not
    assert '"group": "Services"' in content
    # Skill node should NOT be in Services group
    # Parse the nodes JSON to verify
    import json
    import re

    match = re.search(r"var nodes = new vis\.DataSet\((\[.*?\])\);", content, re.DOTALL)
    assert match, "Could not find nodes DataSet"
    nodes = json.loads(match.group(1))
    service_nodes = [n for n in nodes if n["group"] == "Services"]
    skill_nodes = [n for n in nodes if n["group"] != "Services"]
    assert len(service_nodes) == 1
    assert service_nodes[0]["label"] == "Slack"
    assert len(skill_nodes) == 1
    assert skill_nodes[0]["label"] == "alpha"


def _parse_edges(html_content):
    import json
    import re

    match = re.search(
        r"var edges = new vis\.DataSet\((\[.*?\])\);", html_content, re.DOTALL
    )
    assert match, "Could not find edges DataSet"
    return json.loads(match.group(1))


def test_cross_skill_call_edges(tmp_path):
    skills = [
        _make_skill("alpha", calls=["beta"]),
        _make_skill("beta"),
    ]
    out = render_html(skills, tmp_path / "graph.html")
    edges = _parse_edges(out.read_text())
    call_edges = [e for e in edges if e.get("label") == "calls"]
    assert len(call_edges) == 1
    assert call_edges[0]["from"] == "alpha"
    assert call_edges[0]["to"] == "beta"


def test_service_edges_are_dashed(tmp_path):
    skills = [_make_skill("alpha", services=["Slack"])]
    out = render_html(skills, tmp_path / "graph.html")
    edges = _parse_edges(out.read_text())
    svc_edges = [e for e in edges if e["to"].startswith("svc_")]
    assert len(svc_edges) == 1
    assert svc_edges[0]["dashes"] is True
    assert svc_edges[0]["from"] == "alpha"
    assert svc_edges[0]["to"] == "svc_Slack"


def _parse_nodes(html_content):
    import json
    import re

    match = re.search(
        r"var nodes = new vis\.DataSet\((\[.*?\])\);", html_content, re.DOTALL
    )
    assert match, "Could not find nodes DataSet"
    return json.loads(match.group(1))


def test_cluster_grouping(tmp_path):
    skills = [
        _make_skill("alpha"),
        _make_skill("beta"),
        _make_skill("gamma"),
    ]
    clusters = {
        "Daily routine": ["alpha"],
        "Engineering": ["beta", "gamma"],
    }
    out = render_html(skills, tmp_path / "graph.html", clusters=clusters)
    nodes = _parse_nodes(out.read_text())
    skill_nodes = {n["label"]: n["group"] for n in nodes if n["group"] != "Services"}
    assert skill_nodes["alpha"] == "Daily routine"
    assert skill_nodes["beta"] == "Engineering"
    assert skill_nodes["gamma"] == "Engineering"


def test_node_weights_affect_size(tmp_path):
    # alpha calls beta and gamma -> weight 2; beta called by alpha -> weight 1; gamma -> weight 1
    skills = [
        _make_skill("alpha", calls=["beta", "gamma"]),
        _make_skill("beta"),
        _make_skill("gamma"),
    ]
    out = render_html(skills, tmp_path / "graph.html")
    nodes = _parse_nodes(out.read_text())
    sizes = {n["label"]: n["size"] for n in nodes if n["group"] != "Services"}
    # alpha has highest weight (2 outgoing), beta and gamma have 1 each
    assert sizes["alpha"] > sizes["beta"]
    assert sizes["beta"] == sizes["gamma"]


def test_edge_weights_affect_width(tmp_path):
    # Slack used by 2 skills, Jira by 1 -> Slack edges should be wider
    skills = [
        _make_skill("alpha", services=["Slack", "Jira"]),
        _make_skill("beta", services=["Slack"]),
    ]
    out = render_html(skills, tmp_path / "graph.html")
    edges = _parse_edges(out.read_text())
    svc_edges = {
        (e["from"], e["to"]): e["width"] for e in edges if e["to"].startswith("svc_")
    }
    slack_width = svc_edges[("alpha", "svc_Slack")]
    jira_width = svc_edges[("alpha", "svc_Jira")]
    assert slack_width > jira_width


def test_hover_tooltips_show_descriptions(tmp_path):
    skills = [
        Skill(
            name="alpha",
            description="Manages daily routines",
            content="",
            path=Path("fake"),
            calls=[],
            services=[],
        )
    ]
    out = render_html(skills, tmp_path / "graph.html")
    nodes = _parse_nodes(out.read_text())
    alpha_node = [n for n in nodes if n["label"] == "alpha"][0]
    assert alpha_node["title"] == "Manages daily routines"

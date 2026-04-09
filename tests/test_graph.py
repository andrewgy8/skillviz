"""Tests for the graph module."""

from pathlib import Path

from skillviz.scanner import Skill
from skillviz.graph import _compute_weights, _compute_edge_weight, _penwidth, render


def _make_skill(name, calls=None, services=None):
    return Skill(
        name=name,
        description=f"{name} skill",
        content="",
        path=Path("fake"),
        calls=calls or [],
        services=services or [],
    )


def test_compute_weights():
    skills = [
        _make_skill("a", calls=["b", "c"]),
        _make_skill("b", calls=["c"]),
        _make_skill("c"),
    ]
    weights = _compute_weights(skills)
    assert weights["a"] == 2  # 2 outgoing
    assert weights["b"] == 2  # 1 outgoing + 1 incoming
    assert weights["c"] == 2  # 0 outgoing + 2 incoming


def test_compute_edge_weight():
    skills = [
        _make_skill("a", services=["Slack", "Jira"]),
        _make_skill("b", services=["Slack"]),
    ]
    weights = _compute_edge_weight(skills)
    assert weights[("a", "Slack")] == 2
    assert weights[("b", "Slack")] == 2
    assert weights[("a", "Jira")] == 1


def test_penwidth_bounds():
    assert _penwidth(0) == "1.0"
    assert _penwidth(10) == "5.0"
    assert _penwidth(100) == "5.0"  # clamped


def test_render_produces_file(tmp_path):
    skills = [
        _make_skill("alpha", calls=["beta"], services=["Slack"]),
        _make_skill("beta", services=["Slack"]),
    ]
    out = render(skills, tmp_path / "test-graph", "svg")
    assert out.exists()
    assert out.suffix == ".svg"
    content = out.read_text()
    assert "alpha" in content
    assert "beta" in content

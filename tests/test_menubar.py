"""Tests for the menu bar app module."""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

pytestmark = pytest.mark.skipif(
    sys.platform != "darwin", reason="menubar requires macOS"
)

from skillviz.menubar import SkillVizApp  # noqa: E402
from skillviz.scanner import Skill  # noqa: E402


def _make_skill(name):
    return Skill(
        name=name,
        description=f"{name} skill",
        content="",
        path=Path("fake"),
        calls=[],
        services=[],
    )


def test_app_has_correct_menu_items():
    app = SkillVizApp()
    menu_keys = list(app.menu.keys())
    assert "Open Graph" in menu_keys
    assert "Refresh" in menu_keys


def test_open_graph_scans_renders_opens_browser(tmp_path):
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    output = tmp_path / "graph.html"

    with (
        patch("skillviz.menubar.build_graph") as mock_build,
        patch("skillviz.menubar.webbrowser") as mock_browser,
    ):
        mock_build.return_value = ([_make_skill("alpha")], [])
        app = SkillVizApp(skills_dir=skills_dir, output_path=output)
        app.open_graph(None)

        mock_build.assert_called_once_with(skills_dir)
        assert output.exists()
        mock_browser.open.assert_called_once()
        assert str(output) in mock_browser.open.call_args[0][0]


def test_refresh_regenerates_without_browser(tmp_path):
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    output = tmp_path / "graph.html"

    with (
        patch("skillviz.menubar.build_graph") as mock_build,
        patch("skillviz.menubar.webbrowser") as mock_browser,
        patch("skillviz.menubar.rumps"),
    ):
        mock_build.return_value = ([_make_skill("alpha")], [])
        app = SkillVizApp(skills_dir=skills_dir, output_path=output)
        app.refresh(None)

        mock_build.assert_called_once_with(skills_dir)
        assert output.exists()
        mock_browser.open.assert_not_called()

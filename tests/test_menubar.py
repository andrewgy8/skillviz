"""Tests for the menu bar app module."""

from pathlib import Path
from unittest.mock import patch, MagicMock

from skillviz.menubar import SkillVizApp
from skillviz.scanner import Skill


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
    with patch("skillviz.menubar.rumps") as mock_rumps:
        mock_rumps.App = MagicMock()
        mock_rumps.MenuItem = MagicMock(
            side_effect=lambda title: MagicMock(title=title)
        )
        app = SkillVizApp()
        menu_titles = [item.title for item in app.menu_items]
        assert "Open Graph" in menu_titles
        assert "Refresh" in menu_titles


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
        app._open_graph()

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
    ):
        mock_build.return_value = ([_make_skill("alpha")], [])
        app = SkillVizApp(skills_dir=skills_dir, output_path=output)
        app._refresh()

        mock_build.assert_called_once_with(skills_dir)
        assert output.exists()
        mock_browser.open.assert_not_called()

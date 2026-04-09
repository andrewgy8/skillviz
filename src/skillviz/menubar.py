"""macOS menu bar app for SkillViz using rumps."""

from __future__ import annotations

import webbrowser
from pathlib import Path

import rumps

from .scanner import build_graph
from .html_renderer import render_html


_DEFAULT_SKILLS_DIR = Path.home() / ".claude" / "skills"
_DEFAULT_OUTPUT = Path.home() / ".claude" / "skill-graph.html"


class SkillVizApp:
    def __init__(
        self,
        skills_dir: Path = _DEFAULT_SKILLS_DIR,
        output_path: Path = _DEFAULT_OUTPUT,
    ):
        self.skills_dir = skills_dir
        self.output_path = output_path
        self.menu_items = [
            rumps.MenuItem("Open Graph"),
            rumps.MenuItem("Refresh"),
        ]
        self.app = rumps.App(
            "\U0001f990",
            menu=[*self.menu_items, None],  # None = separator before Quit
        )
        self.app.menu["Open Graph"].set_callback(self._open_graph)
        self.app.menu["Refresh"].set_callback(self._refresh)

    def _generate(self) -> Path:
        skills, _ = build_graph(self.skills_dir)
        return render_html(skills, self.output_path)

    def _open_graph(self, _sender=None):
        path = self._generate()
        webbrowser.open(f"file://{path}")

    def _refresh(self, _sender=None):
        self._generate()

    def run(self):
        self.app.run()


def main():
    app = SkillVizApp()
    app.run()


if __name__ == "__main__":
    main()

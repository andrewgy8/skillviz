"""macOS menu bar app for SkillViz using rumps."""

from __future__ import annotations

import webbrowser
from pathlib import Path

import rumps

from .scanner import build_graph
from .html_renderer import render_html


_DEFAULT_SKILLS_DIR = Path.home() / ".claude" / "skills"
_DEFAULT_OUTPUT = Path.home() / ".claude" / "skill-graph.html"


class SkillVizApp(rumps.App):
    def __init__(
        self,
        skills_dir: Path = _DEFAULT_SKILLS_DIR,
        output_path: Path = _DEFAULT_OUTPUT,
    ):
        super().__init__(
            "\U0001f990", menu=["Open Graph", "Refresh"], quit_button="Quit"
        )
        self.skills_dir = skills_dir
        self.output_path = output_path

    def _generate(self) -> Path:
        skills, _ = build_graph(self.skills_dir)
        if not skills:
            rumps.notification("SkillViz", "", f"No skills found in {self.skills_dir}")
            return self.output_path
        return render_html(skills, self.output_path)

    @rumps.clicked("Open Graph")
    def open_graph(self, _):
        path = self._generate()
        if path.exists():
            webbrowser.open(f"file://{path}")

    @rumps.clicked("Refresh")
    def refresh(self, _):
        self._generate()
        rumps.notification("SkillViz", "", "Graph refreshed")


def main():
    SkillVizApp().run()


if __name__ == "__main__":
    main()

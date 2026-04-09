<p align="center">
  <img src="logo.svg" alt="SkillViz logo" width="300"/>
</p>

<h1 align="center">SkillViz</h1>

<p align="center">Visualize your Claude Code skills as a dependency graph.</p>

---

## Why?

Claude Code skills are a lot like functions: they do a specific thing, and they can call other skills to get their job done. Once you have a dozen or more installed, the dependency chain gets hard to keep in your head. Which skills call which? What services does each one touch? You end up scanning through SKILL.md files trying to piece it together.

SkillViz makes this visible. It scans your `~/.claude/skills/` directory, finds cross-skill calls and service usage, and renders the whole thing as a graph. It also helps with discoverability, since it's surprisingly easy to forget what skills you have installed and how they relate to each other.

<p align="center">
  <img src="examples/demo.gif" alt="Interactive skill graph demo" width="100%"/>
</p>

<p align="center"><em>Red edges are skill-to-skill calls, gray dashed edges are service integrations. <a href="https://andrewgy8.github.io/skillviz/demo-graph.html">Try the interactive version.</a></em></p>

## Install

```bash
pip install skillviz
```

## Usage

### Interactive HTML graph

The default and recommended way to use SkillViz. Generates a self-contained HTML file with zoom, pan, hover tooltips, and physics-based layout. No browser extensions or JS dependencies needed -- just open the file.

```python
from pathlib import Path
from skillviz.scanner import build_graph
from skillviz.html_renderer import render_html

skills, _ = build_graph(Path.home() / ".claude" / "skills")
render_html(skills, Path.home() / ".claude" / "skill-graph.html")
```

Then open `~/.claude/skill-graph.html` in any browser. See the [live demo](https://andrewgy8.github.io/skillviz/demo-graph.html) for what this looks like.

### Static image output (SVG/PNG/PDF)

If you need a static image instead, the CLI renders via Graphviz. This requires the `dot` binary:

```bash
# macOS
brew install graphviz

# Debian/Ubuntu
apt install graphviz
```

Then:

```bash
# Defaults: reads ~/.claude/skills/, writes ./skill-graph.svg
skillviz

# PNG output with a custom name
skillviz -o my-graph -f png

# Custom skills directory
skillviz --skills-dir /path/to/skills
```

## What it detects

Skill-to-skill calls are found by matching `/skill-name` patterns in each `SKILL.md` file against all discovered skill names. Service usage is detected from content patterns (Slack, Jira, Notion, etc.) and MCP server names pulled from `~/.claude/settings.json`.

## Graph output

Nodes are skills and services. Red solid edges connect skills that call each other. Gray dashed edges connect skills to the services they use. Node and edge thickness scale with connection count.

If you pass a `--config` YAML, skills can be grouped into named clusters with color-coded subgraphs.

## Development

```bash
git clone https://github.com/andrewgy8/skillviz.git
cd skillviz
uv run pytest tests/ -v
uv run skillviz && open skill-graph.svg
```

## Releasing

Versions are derived from git tags via `hatch-vcs`, so there's no version to update manually. To publish a new release:

```bash
git tag v0.2.0
git push origin v0.2.0
```

The `publish` workflow will run lints, tests across Python 3.10-3.13, then build and publish to PyPI with the tag as the version.

## License

MIT

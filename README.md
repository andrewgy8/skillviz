<p align="center">
  <img src="logo.svg" alt="SkillViz logo" width="300"/>
</p>

<h1 align="center">SkillViz</h1>

<p align="center">Visualize your Claude Code skills as a dependency graph.</p>

---

SkillViz scans your `~/.claude/skills/` directory, finds cross-skill calls and service usage, and renders the whole thing as a graph via Graphviz.

## Install

```bash
pip install skillviz
```

You also need the Graphviz system binary:

```bash
# macOS
brew install graphviz

# Debian/Ubuntu
apt install graphviz
```

## Usage

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
uv run skillviz && open skill-graph.svg
```

## License

MIT

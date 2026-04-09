# SkillViz

Visualize Claude Code skills as a dependency graph.

## Project structure

```
src/skillviz/
  cli.py       - argparse CLI entry point
  scanner.py   - skill discovery, frontmatter parsing, cross-skill call extraction, service detection
  graph.py     - graphviz rendering with weighted nodes/edges and cluster grouping
```

## How it works

1. **Scanner** reads all `SKILL.md` files from `~/.claude/skills/`
2. Extracts cross-skill calls by regex-matching `/skill-name` patterns against discovered skill names
3. Detects service usage by matching content against patterns (built-in defaults + auto-detected MCP servers from `~/.claude/settings.json`)
4. **Graph** renders to SVG/PNG/PDF via graphviz with:
   - Skill nodes grouped into optional clusters
   - Service nodes as a separate cluster
   - Node thickness weighted by connection count (in-degree + out-degree)
   - Edge thickness weighted by service popularity
   - Red solid edges for skill-to-skill calls, gray dashed for service usage

## Running

```bash
uv run skillviz                          # defaults: ~/.claude/skills -> ./skill-graph.svg
uv run skillviz -o my-graph -f png       # PNG output
uv run skillviz --skills-dir /path/to/skills
```

## Key design decisions

- **Zero config by default.** Everything is auto-detected: skills from the directory, services from content patterns + MCP server names in Claude settings. The optional `--config` YAML is for overrides only.
- **Service patterns are layered.** Built-in defaults -> MCP auto-detection -> user config (highest priority).
- **MCP server names** are mapped to friendly display names via `_MCP_NAME_MAP` in `scanner.py`. Unknown servers use their raw key as the label.
- **Clusters are optional.** Without a config, all skills go into one "Uncategorized" group. With a config, skills map to named clusters with color-coded subgraphs.

## Dependencies

- `graphviz` Python package (pip) AND the system `dot` binary (`brew install graphviz` / `apt install graphviz`)
- `pyyaml` for frontmatter and config parsing

## Testing

Run the test suite:

```bash
uv run pytest tests/ -v
```

# Changelog

## 0.1.0 (unreleased)

Initial release.

- Scan `~/.claude/skills/` for SKILL.md files
- Extract cross-skill calls via `/skill-name` pattern matching
- Detect service usage from content patterns and MCP server names in `~/.claude/settings.json`
- Render dependency graph to SVG, PNG, or PDF via Graphviz
- Optional cluster grouping and color-coded subgraphs via `--config` YAML
- Node and edge thickness weighted by connection count

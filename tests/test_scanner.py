"""Tests for the scanner module."""

from pathlib import Path

from skillviz.scanner import (
    Skill,
    ServicePattern,
    _parse_frontmatter,
    extract_calls,
    extract_services,
    discover_skills,
    discover_mcp_servers,
)


def test_parse_frontmatter():
    content = "---\nname: my-skill\ndescription: Does things\n---\nBody here"
    name, desc = _parse_frontmatter(content)
    assert name == "my-skill"
    assert desc == "Does things"


def test_parse_frontmatter_missing():
    name, desc = _parse_frontmatter("No frontmatter here")
    assert name == ""
    assert desc == ""


def test_extract_calls():
    skill = Skill(
        name="builder",
        description="",
        content="This skill calls /deploy and /notify but not /builder",
        path=Path("fake"),
    )
    all_names = {"builder", "deploy", "notify", "unused"}
    calls = extract_calls(skill, all_names)
    assert calls == ["deploy", "notify"]


def test_extract_calls_no_self_reference():
    skill = Skill(
        name="deploy",
        description="",
        content="Run /deploy again",
        path=Path("fake"),
    )
    assert extract_calls(skill, {"deploy"}) == []


def test_extract_services():
    skill = Skill(
        name="test",
        description="",
        content="Send a slack_send_message and check jira ticket",
        path=Path("fake"),
    )
    patterns = [
        ServicePattern("Slack", ["slack_send_message"]),
        ServicePattern("Jira", ["jira ticket"]),
        ServicePattern("Notion", ["notion search"]),
    ]
    services = extract_services(skill, patterns)
    assert "Slack" in services
    assert "Jira" in services
    assert "Notion" not in services


def test_discover_skills(tmp_path):
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "---\nname: my-skill\ndescription: A test skill\n---\nContent"
    )

    skills = discover_skills(tmp_path)
    assert len(skills) == 1
    assert skills[0].name == "my-skill"
    assert skills[0].description == "A test skill"


def test_discover_skills_uses_dir_name_as_fallback(tmp_path):
    skill_dir = tmp_path / "fallback-name"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("No frontmatter")

    skills = discover_skills(tmp_path)
    assert skills[0].name == "fallback-name"


def test_discover_skills_empty_dir(tmp_path):
    assert discover_skills(tmp_path) == []


def test_discover_mcp_servers(tmp_path):
    settings = tmp_path / "settings.json"
    settings.write_text('{"mcpServers": {"my-slack-bot": {}, "custom-tool": {}}}')

    servers = discover_mcp_servers(tmp_path)
    assert servers["my-slack-bot"] == "Slack"
    assert servers["custom-tool"] == "custom-tool"


def test_discover_mcp_servers_no_file(tmp_path, monkeypatch):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    assert discover_mcp_servers(tmp_path) == {}

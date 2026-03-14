"""Tests for SkillPointer."""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from setup import (
    Config,
    get_category_for_skill,
    main,
    parse_args,
    setup_directories,
)


class TestGetCategoryForSkill:
    """Tests for get_category_for_skill function."""

    def test_substring_match_python(self) -> None:
        assert get_category_for_skill("python-pro") == "programming"

    def test_substring_match_security(self) -> None:
        assert get_category_for_skill("security-scanner") == "security"

    def test_substring_match_debug(self) -> None:
        assert get_category_for_skill("bug-hunter") == "debug"

    def test_substring_match_wordpress(self) -> None:
        assert get_category_for_skill("generateblocks-expert") == "wordpress"

    def test_substring_match_documentation(self) -> None:
        assert get_category_for_skill("code-documenter") == "documentation"

    def test_exact_match_quoted(self) -> None:
        assert get_category_for_skill('"python"') == "programming"

    def test_exact_match_no_match(self) -> None:
        assert get_category_for_skill('"xyz-nonexistent"') == "_uncategorized"

    def test_uncategorized_random_name(self) -> None:
        assert get_category_for_skill("xyz-abc-123") == "_uncategorized"

    def test_pr_review_special_case(self) -> None:
        assert get_category_for_skill("pr-review-agent") == "code-review"

    def test_pull_request_special_case(self) -> None:
        # Note: "pull-request" also matches "git" category, so this returns "git"
        # The special handling only applies when "review" is also in the name
        result = get_category_for_skill("pull-request-helper")
        assert result == "git"

    def test_merge_request_special_case(self) -> None:
        # Note: "merge-request" also matches "git" category
        result = get_category_for_skill("merge-request-bot")
        assert result == "git"

    def test_review_without_pr_not_code_review(self) -> None:
        result = get_category_for_skill("code-review-tool")
        assert result == "code-review"

    def test_underscore_to_dash_conversion(self) -> None:
        assert get_category_for_skill("python_pro") == "programming"

    def test_case_insensitive(self) -> None:
        assert get_category_for_skill("PYTHON-PRO") == "programming"

    def test_empty_string(self) -> None:
        assert get_category_for_skill("") == "_uncategorized"

    def test_web_dev_match(self) -> None:
        assert get_category_for_skill("react-components") == "web-dev"

    def test_database_match(self) -> None:
        assert get_category_for_skill("postgres-pro") == "database"

    def test_devops_match(self) -> None:
        assert get_category_for_skill("docker-helper") == "devops"

    def test_ai_ml_match(self) -> None:
        assert get_category_for_skill("llm-tools") == "ai-ml"


class TestConfig:
    """Tests for Config dataclass."""

    def test_default_config(self) -> None:
        config = Config()
        assert config.agent_name == "OpenCode"
        assert ".config/opencode/skills" in str(config.active_skills_dir)
        assert ".opencode-skill-libraries" in str(config.hidden_library_dir)
        assert config.dry_run is False

    def test_custom_config(self) -> None:
        config = Config(
            agent_name="Claude Code",
            active_skills_dir=Path("/custom/skills"),
            hidden_library_dir=Path("/custom/vault"),
            dry_run=True,
        )
        assert config.agent_name == "Claude Code"
        assert config.active_skills_dir == Path("/custom/skills")
        assert config.hidden_library_dir == Path("/custom/vault")
        assert config.dry_run is True


class TestSetupDirectories:
    """Tests for setup_directories function."""

    def test_nonexistent_skills_dir(self) -> None:
        config = Config(
            active_skills_dir=Path("/nonexistent/path/skills"),
        )
        assert setup_directories(config) is False

    def test_creates_vault_dir(self, tmp_path: Path) -> None:
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        vault_dir = tmp_path / "vault"

        config = Config(
            active_skills_dir=skills_dir,
            hidden_library_dir=vault_dir,
        )

        assert setup_directories(config) is True
        assert vault_dir.exists()

    def test_existing_vault_dir(self, tmp_path: Path) -> None:
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        vault_dir = tmp_path / "vault"
        vault_dir.mkdir()

        config = Config(
            active_skills_dir=skills_dir,
            hidden_library_dir=vault_dir,
        )

        assert setup_directories(config) is True


class TestParseArgs:
    """Tests for parse_args function."""

    def test_default_args(self) -> None:
        config, unknown = parse_args([])
        assert config.agent_name == "OpenCode"
        assert config.dry_run is False

    def test_claude_agent(self) -> None:
        config, unknown = parse_args(["--agent", "claude"])
        assert config.agent_name == "Claude Code"
        assert ".claude/skills" in str(config.active_skills_dir)

    def test_custom_skill_dir(self, tmp_path: Path) -> None:
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()

        config, unknown = parse_args(["--skill-dir", str(skills_dir)])
        assert config.active_skills_dir == skills_dir.resolve()

    def test_custom_vault_dir(self, tmp_path: Path) -> None:
        vault_dir = tmp_path / "vault"

        config, unknown = parse_args(["--vault-dir", str(vault_dir)])
        assert config.hidden_library_dir == vault_dir.resolve()

    def test_dry_run_flag(self) -> None:
        config, unknown = parse_args(["--dry-run"])
        assert config.dry_run is True

    def test_skill_dir_expands_home(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            skills_dir = Path(tmpdir) / "skills"
            skills_dir.mkdir()

            with patch.dict("os.environ", {"HOME": tmpdir}):
                config, unknown = parse_args(["--skill-dir", "~/skills"])
                assert "skills" in str(config.active_skills_dir)

    def test_nonexistent_skill_dir_exits(self, capsys: pytest.CaptureFixture) -> None:
        with pytest.raises(SystemExit) as exc_info:
            parse_args(["--skill-dir", "/nonexistent/path"])
        assert exc_info.value.code == 1

    def test_install_arg_compatibility(self) -> None:
        config, unknown = parse_args(["install"])
        assert "install" in unknown

    def test_combined_args(self, tmp_path: Path) -> None:
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        vault_dir = tmp_path / "vault"

        config, unknown = parse_args(
            [
                "--agent",
                "claude",
                "--skill-dir",
                str(skills_dir),
                "--vault-dir",
                str(vault_dir),
                "--dry-run",
            ]
        )

        assert config.agent_name == "Claude Code"
        assert config.active_skills_dir == skills_dir.resolve()
        assert config.hidden_library_dir == vault_dir.resolve()
        assert config.dry_run is True


class TestMain:
    """Tests for main function."""

    def test_dry_run_no_changes(self, tmp_path: Path) -> None:
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        (skills_dir / "test-skill").mkdir()
        (skills_dir / "test-skill" / "SKILL.md").write_text("---\nname: test\n---\n")

        vault_dir = tmp_path / "vault"

        result = main(
            [
                "--skill-dir",
                str(skills_dir),
                "--vault-dir",
                str(vault_dir),
                "--dry-run",
            ]
        )

        assert result == 0
        # Skills should NOT be moved in dry-run mode
        assert (skills_dir / "test-skill").exists()
        # Vault is created by setup_directories, but skills shouldn't be inside
        assert not (vault_dir / "testing" / "test-skill").exists()

    def test_full_migration(self, tmp_path: Path) -> None:
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        (skills_dir / "python-pro").mkdir()
        (skills_dir / "python-pro" / "SKILL.md").write_text("---\nname: python-pro\n---\n")

        vault_dir = tmp_path / "vault"

        result = main(
            [
                "--skill-dir",
                str(skills_dir),
                "--vault-dir",
                str(vault_dir),
            ]
        )

        assert result == 0
        assert not (skills_dir / "python-pro").exists()
        assert (vault_dir / "programming" / "python-pro").exists()
        assert (skills_dir / "programming-category-pointer").exists()

    def test_handles_existing_pointers(self, tmp_path: Path) -> None:
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        pointer_dir = skills_dir / "test-category-pointer"
        pointer_dir.mkdir()
        (pointer_dir / "SKILL.md").write_text("---\nname: test-pointer\n---\n")

        vault_dir = tmp_path / "vault"

        result = main(
            [
                "--skill-dir",
                str(skills_dir),
                "--vault-dir",
                str(vault_dir),
            ]
        )

        assert result == 0
        assert pointer_dir.exists()

    def test_handles_empty_folders(self, tmp_path: Path) -> None:
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        (skills_dir / "empty-folder").mkdir()

        vault_dir = tmp_path / "vault"

        result = main(
            [
                "--skill-dir",
                str(skills_dir),
                "--vault-dir",
                str(vault_dir),
            ]
        )

        assert result == 0
        assert (skills_dir / "empty-folder").exists()


class TestIntegration:
    """Integration tests for complete workflows."""

    def test_full_workflow_with_multiple_skills(self, tmp_path: Path) -> None:
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()

        # Note: Use names that won't accidentally match keywords
        # (e.g., "random-tool" contains "dom" which matches web-dev's "dom")
        skills = [
            ("python-pro", "programming"),
            ("postgres-pro", "database"),
            ("react-components", "web-dev"),
            ("security-scanner", "security"),
            ("xyz-abc-123", "_uncategorized"),
        ]

        for skill_name, _ in skills:
            skill_dir = skills_dir / skill_name
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text(f"---\nname: {skill_name}\n---\n")

        vault_dir = tmp_path / "vault"

        result = main(
            [
                "--skill-dir",
                str(skills_dir),
                "--vault-dir",
                str(vault_dir),
            ]
        )

        assert result == 0

        for skill_name, expected_category in skills:
            assert not (skills_dir / skill_name).exists(), f"{skill_name} not moved"
            assert (vault_dir / expected_category / skill_name).exists(), (
                f"{skill_name} not in {expected_category}"
            )

        for expected_category in set(cat for _, cat in skills):
            pointer_dir = skills_dir / f"{expected_category}-category-pointer"
            assert pointer_dir.exists(), f"Pointer for {expected_category} not created"

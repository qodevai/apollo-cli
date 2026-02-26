"""Tests for install command."""

from __future__ import annotations

from pathlib import Path

from apollo_cli.commands.install import _install_skills


class TestInstall:
    def test_install_skills(self, tmp_path: Path) -> None:
        """Test that skill files are installed to correct location."""
        dest = _install_skills(target_root=tmp_path)

        assert dest.exists()
        assert (dest / "SKILL.md").exists()
        assert (dest / "references").exists()
        assert (dest / "references" / "contact-workflows.md").exists()
        assert (dest / "references" / "deal-workflows.md").exists()
        assert (dest / "references" / "account-workflows.md").exists()

        # Verify no __pycache__ or __init__.py copied
        pycache_dirs = list(dest.rglob("__pycache__"))
        assert len(pycache_dirs) == 0

        init_files = list(dest.rglob("__init__.py"))
        assert len(init_files) == 0

        # Verify SKILL.md content
        skill_content = (dest / "SKILL.md").read_text()
        assert "qodev-apollo-cli" in skill_content
        assert "APOLLO_API_KEY" in skill_content
        assert "contacts search" in skill_content

    def test_install_skills_replaces_existing(self, tmp_path: Path) -> None:
        """Test that installing skills replaces existing installation."""
        dest = tmp_path / ".claude" / "skills" / "apollo"
        dest.mkdir(parents=True)
        old_file = dest / "old_file.txt"
        old_file.write_text("old content")

        # Install skills
        result_dest = _install_skills(target_root=tmp_path)

        assert result_dest == dest
        assert not old_file.exists()  # Old file should be removed
        assert (dest / "SKILL.md").exists()

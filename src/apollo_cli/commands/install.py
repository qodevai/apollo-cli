"""Install CLI resources (skills for AI agents)."""

from __future__ import annotations

import shutil
from importlib.abc import Traversable
from importlib.resources import files
from pathlib import Path
from typing import Annotated

from cyclopts import App, Parameter

from apollo_cli.output import console

install_app = App(name="install", help="Install CLI resources.")


def _install_skills(target_root: Path | None = None) -> Path:
    """Copy bundled skill files to .claude/skills/apollo/."""
    root = target_root or Path.cwd()
    dest = root / ".claude" / "skills" / "apollo"

    source = files("apollo_cli") / "skills"

    if dest.exists():
        console.print(f"Replacing existing skills at {dest}")
        shutil.rmtree(dest)
    dest.mkdir(parents=True)

    _copy_traversable(source, dest)
    return dest


def _copy_traversable(source: Traversable, dest: Path) -> None:
    """Recursively copy from a Traversable (importlib.resources) to a Path."""
    for item in source.iterdir():
        if item.name.startswith("__"):
            continue
        target = dest / item.name
        if item.is_file():
            target.write_bytes(item.read_bytes())
        elif item.is_dir():
            target.mkdir(exist_ok=True)
            _copy_traversable(item, target)


@install_app.default
def install(
    *,
    skills: Annotated[bool, Parameter(name="--skills", help="Install AI agent skill files", negative="")] = False,
) -> None:
    """Install CLI resources into the current workspace."""
    if not skills:
        from apollo_cli.output import error

        error("No install target specified. Use: qodev-apollo-cli install --skills", code="validation", exit_code=83)

    dest = _install_skills()
    console.print(f"[green]Installed skills to {dest}[/green]")

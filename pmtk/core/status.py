"""
Core functions for operations concerning units of work.

:copyright:
    2025, Conor A. Bacon
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

import pathlib

import typer
import yaml

from pmtk.utils import find_project_root, PROJECT_STRUCTURE


def check_tree(base: pathlib.Path, tree: dict, prefix: str | None = None) -> list[str]:
    """
    Return a list of missing paths (relative).

    """

    missing = []

    for name, subtree in tree.items():
        path = base / name
        rel = f"{prefix}{name}"
        if not path.exists():
            missing.append(rel + "/")
        elif subtree:
            missing.extend(check_tree(path, subtree, prefix=rel + "/"))

    return missing


def status() -> None:
    """
    Output information about the local project, if managed by PMTK.

    """

    project_root = find_project_root()
    if project_root is None:
        typer.echo("Error: Not in a pmtk project. No .pmtk-lock file found.", err=True)
        raise typer.Exit(code=1)

    typer.echo(f"pmtk project detected: {project_root.name}")
    typer.echo("")

    lockfile = project_root / ".pmtk-lock"
    if lockfile.exists():
        typer.echo("Lockfile: present")
        typer.echo(lockfile.read_text().strip())
    else:
        typer.echo("  Lockfile: missing")

    typer.echo("")

    project_yaml = project_root / "config" / "project.yaml"
    if project_yaml.exists():
        typer.echo("Project metadata:")
        data = yaml.safe_load(project_yaml.read_text()) or {}

        name = data.get("project_name", "<unknown>")
        created = data.get("created", "<unknown>")
        tags = data.get("tags", [])

        typer.echo(f"  Name: {name}")
        typer.echo(f"  Created: {created}")

        if tags:
            typer.echo(f"  Tags: {', '.join(tags)}")
        else:
            typer.echo("  Tags: (none)")
    else:
        typer.echo("  Project metadata missing (config/project.yaml)")

    typer.echo("")

    typer.echo("Directory structure:")

    missing = check_tree(project_root, PROJECT_STRUCTURE)
    if not missing:
        typer.echo("  Directory structure complete")
    else:
        typer.echo("  Missing directories:")
        for m in missing:
            typer.echo(f"    - {m}")

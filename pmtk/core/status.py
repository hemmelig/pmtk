"""
Core functions for operations concerning units of work.

:copyright:
    2025, Conor A. Bacon
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

import pathlib
import yaml
import typer

from pmtk.utils import find_project_root


REQUIRED_DIRS = [
    "config",
    "data",
    "docs",
    "environments",
    "logs",
    "results",
    "workspace",
    "archive",
]

def status() -> None:
    """
    Output information about the local project, if managed by PMTK.

    """

    project_root = find_project_root()

    if not project_root:
        typer.echo("Not inside a pmtk project (no .pmtk-lock found).")
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
        typer.echo(project_yaml.read_text().strip())
    else:
        typer.echo("  Project metadata missing (config/project.yaml)")

    typer.echo("")

    typer.echo("Directory structure:")

    for d in REQUIRED_DIRS:
        path = project_root / d
        if path.exists():
            typer.echo(f"  {d}/")
        else:
            typer.echo(f"  {d}/ (missing)")

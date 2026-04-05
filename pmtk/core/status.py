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
from .metadata import load_data_registry, load_project_metadata


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

    typer.echo(f"pmtk project detected: {project_root.name}")
    typer.echo("")

    try:
        project = load_project_metadata(project_root)
    except FileNotFoundError:
        typer.echo("  Missing .config/project.yaml\n")
        project = {}

    typer.echo("Project:")

    name = project.get("project_name", "<unknown>")
    status_ = project.get("status", "<unknown>")
    tags = project.get("tags", [])
    contacts = project.get("contacts", {})

    typer.echo(f"  Name: {name}")
    typer.echo(f"  Status: {status_}")

    if tags:
        typer.echo(f"  Tags: {', '.join(tags)}")
    else:
        typer.echo("  Tags: (none)")

    owner = contacts.get("owner")
    if owner:
        typer.echo(f"  Owner: {owner}")
    typer.echo("")

    registry = load_data_registry(project_root)
    datasets = registry.get("datasets", [])

    typer.echo("Data:")
    typer.echo(f"  Registered datasets: {len(datasets)}")
    typer.echo("")

    workspace = project_root / "workspace"
    archive = project_root / "archive"

    active_units = (
        len([p for p in workspace.iterdir() if p.is_dir()]) if workspace.exists() else 0
    )
    archived_units = (
        len([p for p in archive.iterdir() if p.is_dir()]) if archive.exists() else 0
    )

    typer.echo("Work units:")
    typer.echo(f"  Active: {active_units}")
    typer.echo(f"  Archived: {archived_units}")
    typer.echo("")

    typer.echo("Directory structure:")

    missing = check_tree(project_root, PROJECT_STRUCTURE)
    if not missing:
        typer.echo("  Directory structure complete")
    else:
        typer.echo("  Missing directories:")
        for m in missing:
            typer.echo(f"    - {m}")
    typer.echo("")

    lockfile = project_root / ".pmtk-lock"
    if lockfile.exists():
        typer.echo("Lockfile: present")
        try:
            lock = yaml.safe_load(lockfile.read_text()) or {}
        except Exception:
            typer.echo("    Could not read .pmtk-lock")
            return

        typer.echo(f"  pmtk version: {lock.get('pmtk_version', '<unknown>')}")
        typer.echo(f"  Schema version: {lock.get('schema_version', '<unknown>')}")
    else:
        typer.echo("  Lockfile: missing")

    typer.echo("")

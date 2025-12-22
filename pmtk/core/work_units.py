"""
Core functions for operations concerning units of work.

:copyright:
    2025, Conor A. Bacon
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

import pathlib
import shutil
from datetime import datetime as dt, UTC

import typer

from pmtk.utils import find_project_root
from .metadata import load_unit_registry, save_unit_registry


def _work_unit_exists(project_root: pathlib.Path, unit_name: str) -> bool:
    """
    Check if a work unit exists in workspace or archive.

    Parameters
    ----------
    project_root:
        Path to the project root directory.
    unit_name:
        Name of the work unit to check.

    Returns
    -------
     :
        True if the unit exists in either 'workspace' or 'archive', otherwise False.

    """

    workspace_path = project_root / "workspace" / unit_name
    archive_path = project_root / "archive" / unit_name

    return workspace_path.exists() or archive_path.exists()


def register_work_unit(
    unit_name: str, description: str | None = None, tags: list[str] = None
) -> None:
    """
    Register a new unit of work in the workspace.

    Creates a directory in workspace/ and adds an entry to config/registry.yaml.

    Parameters
    ----------
    unit_name:
        Name/identifier for the work unit.
    description:
        Optional description of the work unit.
    tags:
        Optional list of tags for categorization.

    """

    project_root = find_project_root()
    if project_root is None:
        typer.echo("Error: Not in a pmtk project. No .pmtk-lock file found.", err=True)
        raise typer.Exit(code=1)

    workspace_dir = project_root / "workspace"
    if not workspace_dir.exists():
        typer.echo(f"Error: Workspace directory not found at {workspace_dir}", err=True)
        raise typer.Exit(code=1)

    if _work_unit_exists(project_root, unit_name):
        typer.echo(f"Error: Work unit '{unit_name}' already exists.", err=True)
        raise typer.Exit(code=1)

    unit_path = workspace_dir / unit_name
    unit_path.mkdir(parents=True, exist_ok=True)

    description = description or ""
    readme = unit_path / "README.md"
    readme.write_text(f"# {unit_name}\n\n{description}\n")

    registry = load_unit_registry(project_root)

    if unit_name in registry["work_units"]:
        typer.echo(
            f"Error: Work unit '{unit_name}' already registered in registry.",
            err=True,
        )
        raise typer.Exit(code=1)

    registry["work_units"][unit_name] = {
        "created": dt.now(UTC).isoformat(),
        "status": "active",
        "path": f"workspace/{unit_name}",
        "description": description,
        "tags": tags or [],
    }
    save_unit_registry(project_root, registry)

    typer.echo(f"Work unit '{unit_name}' registered successfully at {unit_path}")


def archive_work_unit(unit_name: str) -> None:
    """
    Archive a work unit by moving it from workspace/ to archive/.

    Updates the registry to mark the unit as archived and records the archive timestamp.

    Parameters
    ----------
    unit_name:
        Name/identifier of the work unit to archive.

    """

    project_root = find_project_root()
    if project_root is None:
        typer.echo("Error: Not in a pmtk project. No .pmtk-lock file found.", err=True)
        raise typer.Exit(code=1)

    unit_path = project_root / "workspace" / unit_name
    archive_path = project_root / "archive" / unit_name

    if not unit_path.exists():
        typer.echo(f"Error: Work unit '{unit_name}' not found in workspace.", err=True)
        raise typer.Exit(code=1)

    registry = load_unit_registry(project_root)

    work_unit = registry["work_units"].get(unit_name)
    if not work_unit:
        typer.echo(f"Error: Work unit '{unit_name}' not found in registry.", err=True)
        raise typer.Exit(code=1)

    shutil.move(str(unit_path), str(archive_path))

    work_unit.update(
        {
            "status": "archived",
            "archived_at": dt.now(UTC).isoformat(),
            "path": f"archive/{unit_name}",
        }
    )

    save_unit_registry(project_root, registry)

    typer.echo(f"Work unit '{unit_name}' archived successfully to {archive_path}")


def restore_work_unit(unit_name: str) -> None:
    """
    Restore a work unit by moving it from archive/ back to workspace/.

    Updates the registry to mark the unit as active and removes the archive timestamp.

    Parameters
    ----------
    unit_name:
        Locally unique work unit identifier.

    """

    project_root = find_project_root()
    if project_root is None:
        typer.echo("Error: Not in a pmtk project. No .pmtk-lock file found.", err=True)
        raise typer.Exit(code=1)

    unit_path = project_root / "workspace" / unit_name
    archive_path = project_root / "archive" / unit_name

    if not archive_path.exists():
        typer.echo(f"Error: Work unit '{unit_name}' not found in archive.", err=True)
        raise typer.Exit(code=1)

    registry = load_unit_registry(project_root)

    work_unit = registry["work_units"].get(unit_name)
    if not work_unit:
        typer.echo(f"Error: Work unit '{unit_name}' not found in registry.", err=True)
        raise typer.Exit(code=1)

    shutil.move(str(archive_path), str(unit_path))

    work_unit.update(
        {
            "status": "active",
            "path": f"workspace/{unit_name}",
        }
    )
    if "archived_at" in work_unit:
        del work_unit["archived_at"]

    save_unit_registry(project_root, registry)

    typer.echo(f"Work unit '{unit_name}' unarchived successfully to {unit_path}")

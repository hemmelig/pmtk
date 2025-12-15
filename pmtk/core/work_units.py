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
import yaml

from pmtk.utils import find_project_root


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

    readme = unit_path / "README.md"
    description = "" if description is None else description
    readme.write_text(f"# {unit_name}\n\n{description}\n")

    registry_path = project_root / "config" / "registry.yaml"
    if registry_path.exists() and registry_path.stat().st_size > 0:
        with open(registry_path, "r") as f:
            registry = yaml.safe_load(f) or {}
    else:
        registry = {}

    if "work_units" not in registry:
        registry["work_units"] = []

    entry = {
        "name": unit_name,
        "created": dt.now(UTC).isoformat(),
        "status": "active",
        "description": description,
        "tags": tags or [],
    }
    registry["work_units"].append(entry)

    with open(registry_path, "w") as f:
        yaml.dump(registry, f, default_flow_style=False, sort_keys=False)

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
    registry_path = project_root / "config" / "registry.yaml"

    if not unit_path.exists():
        typer.echo(f"Error: Work unit '{unit_name}' not found in workspace.", err=True)
        raise typer.Exit(code=1)

    if not registry_path.exists():
        typer.echo("Error: Registry not found.", err=True)
        raise typer.Exit(code=1)

    with open(registry_path, "r") as f:
        registry = yaml.safe_load(f) or {}

    if "work_units" not in registry:
        typer.echo("Error: No work units found in registry.", err=True)
        raise typer.Exit(code=1)

    work_unit = None
    for unit in registry["work_units"]:
        if unit["name"] == unit_name:
            work_unit = unit
            break

    if work_unit is None:
        typer.echo(f"Error: Work unit '{unit_name}' not found in registry.", err=True)
        raise typer.Exit(code=1)

    shutil.move(str(unit_path), str(archive_path))

    work_unit["status"] = "archived"
    work_unit["archived"] = dt.now(UTC).isoformat()
    with open(registry_path, "w") as f:
        yaml.dump(registry, f, default_flow_style=False, sort_keys=False)

    typer.echo(f"Work unit '{unit_name}' archived successfully to {archive_path}")


def unarchive_work_unit(unit_name: str) -> None:
    """
    Unarchive a work unit by moving it from archive/ back to workspace/.

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
    registry_path = project_root / "config" / "registry.yaml"

    if not archive_path.exists():
        typer.echo(f"Error: Work unit '{unit_name}' not found in archive.", err=True)
        raise typer.Exit(code=1)

    if not registry_path.exists():
        typer.echo("Error: Registry not found.", err=True)
        raise typer.Exit(code=1)

    with open(registry_path, "r") as f:
        registry = yaml.safe_load(f) or {}

    if "work_units" not in registry:
        typer.echo("Error: No work units found in registry.", err=True)
        raise typer.Exit(code=1)

    work_unit = None
    for unit in registry["work_units"]:
        if unit["name"] == unit_name:
            work_unit = unit
            break

    if work_unit is None:
        typer.echo(f"Error: Work unit '{unit_name}' not found in registry.", err=True)
        raise typer.Exit(code=1)

    shutil.move(str(archive_path), str(unit_path))

    work_unit["status"] = "active"
    if "archived" in work_unit:
        del work_unit["archived"]

    with open(registry_path, "w") as f:
        yaml.dump(registry, f, default_flow_style=False, sort_keys=False)

    typer.echo(f"Work unit '{unit_name}' unarchived successfully to {unit_path}")

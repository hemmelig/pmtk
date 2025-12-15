"""
Modular CLI application for operations concerning units of work.

:copyright:
    2025, Conor A. Bacon
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

import typer

from pmtk.core.work_units import (
    register_work_unit,
    archive_work_unit,
    unarchive_work_unit,
)


app = typer.Typer(help="Utilities for operating on work units.")


@app.command("register")
def register(
    unit_name: str = typer.Argument(..., help="Name of the work unit"),
    description: str = typer.Option(
        "", "--description", "-d", help="Description of the work unit"
    ),
    tags: list[str] = typer.Option(
        None, "--tag", "-t", help="Tags for categorisation (can be used multiple times)"
    ),
) -> None:
    """
    Register a new unit of work in the workspace.

    Must be run from within a pmtk project directory.

    Parameters
    ----------
    unit_name:
        Locally unique work unit identifier.
    description:
        Optional description of the work unit.
    tags:
        Optional tags for the work unit, which can be used to filter work units.

    """

    register_work_unit(unit_name, description=description, tags=tags)


@app.command("archive")
def archive(
    unit_name: str = typer.Argument(..., help="Name of the work unit to archive"),
) -> None:
    """
    Archive a work unit by moving it from workspace/ to archive/.

    Updates the registry to mark the unit as archived.

    Parameters
    ----------
    unit_name:
        Locally unique work unit identifier.

    """

    archive_work_unit(unit_name)


@app.command("unarchive")
def unarchive(
    unit_name: str = typer.Argument(..., help="Name of the work unit to unarchive"),
) -> None:
    """
    Unarchive a work unit by moving it from archive/ back to workspace/.

    Updates the registry to mark the unit as active.

    Parameters
    ----------
    unit_name:
        Locally unique work unit identifier.

    """

    unarchive_work_unit(unit_name)

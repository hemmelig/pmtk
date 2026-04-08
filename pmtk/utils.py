"""
General utilities for the pmtk package.

:copyright:
    2025, Conor A. Bacon
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

import pathlib
from datetime import datetime as dt, UTC


PROJECT_STRUCTURE = {
    "archive": {},
    ".config": {},
    "data": {
        "external": {},
        "internal": {},
        "metadata": {},
        "processed": {},
    },
    "docs": {
        "budget": {},
        "notes": {},
        "proposal": {},
        "publications": {},
        "reports": {
            "drafts": {},
            "final": {},
        },
        "workplan": {},
    },
    "results": {
        "figures": {},
        "models": {},
        "tables": {},
    },
    "tools": {},
    "workspace": {},
}


def find_project_root(start_path: pathlib.Path | None = None) -> pathlib.Path:
    """
    Find the project root by looking for .pmtk-lock file.

    Searches from the current directory upwards through parent directories.

    Parameters
    ----------
    start_path:
        Starting directory for search. Defaults to current working directory.

    Returns
    -------
    pathlib.Path or None:
        Path to project root if found, None otherwise.

    Raises
    ------
    FileNotFoundError
        If no .pmtk-lock file is found, i.e., not in a PMTK-managed project.

    """

    path = (start_path or pathlib.Path.cwd()).resolve()
    for parent in [path, *path.parents]:
        if (parent / ".pmtk-lock").exists():
            return parent

    raise FileNotFoundError("not in a pmtk project. No .pmtk-lock file found.")


def get_work_unit_path(project_root: pathlib.Path, unit_name: str) -> pathlib.Path:
    """
    Resolve the absolute path to a work unit using the unit registry.

    Parameters
    ----------
    project_root:
        Path to the root of the PMTK project.
    unit_name:
        Key of the work unit (e.g., "array-design").

    Returns
    -------
    unit_path:
        Absolute path to the work unit.

    Raises
    ------
    KeyError
        If the unit is not found.

    """
    
    from pmtk.core.metadata import load_unit_registry

    unit_registry = load_unit_registry()

    try:
        unit_path = unit_registry["work_units"][unit_name]["path"]
    except KeyError as e:
        raise KeyError(f"Work unit '{unit_name}' not found in registry") from e

    return project_root / unit_path


def utc_now_iso() -> str:
    """Utility to return an ISO-formatted datetime string for now."""

    return dt.now(UTC).isoformat() + "Z"

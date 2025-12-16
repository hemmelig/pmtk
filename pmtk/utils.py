"""
General utilities for the pmtk package.

:copyright:
    2025, Conor A. Bacon
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

import pathlib


PROJECT_STRUCTURE = {
    "archive": {},
    "config": {},
    "data": {
        "external": {},
        "internal": {},
        "processed": {},
        "metadata": {},
    },
    "docs": {
        "proposal-and-contract": {},
        "budget": {},
        "publications-and-outreach": {},
        "risks": {},
        "status": {},
        "workplan": {},
    },
    "environments": {},
    "logs": {
        "pmtk": {},
        "pipeline": {},
    },
    "maps": {},
    "notes": {},
    "reports": {
        "drafts": {},
        "final": {},
    },
    "results": {
        "figures": {},
        "tables": {},
        "models": {},
    },
    "tools": {},
    "workspace": {},
}


def find_project_root(start_path: pathlib.Path | None = None) -> pathlib.Path | None:
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

    """

    path = (start_path or pathlib.Path.cwd()).resolve()
    for parent in [path, *path.parents]:
        if (parent / ".pmtk-lock").exists():
            return parent

    return None

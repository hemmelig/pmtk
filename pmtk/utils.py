"""
General utilities for the pmtk package.

:copyright:
    2025, Conor A. Bacon
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

import pathlib


def find_project_root(start_path: pathlib.Path = None) -> pathlib.Path | None:
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

    if start_path is None:
        start_path = pathlib.Path.cwd()

    current = start_path.resolve()
    for parent in [current] + list(current.parents):
        lock_file = parent / ".pmtk-lock"
        if lock_file.exists():
            return parent

    return None

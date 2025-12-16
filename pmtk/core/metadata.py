"""
Utilities for handling project metadata.

:copyright:
    2025, Conor A. Bacon
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

import pathlib

import yaml


def load_project_metadata(project_root: pathlib.Path) -> dict:
    """
    Read project metadata.

    Parameters
    ----------
    project_root:
        Root path for the project.

    Returns
    -------
     :
        Project metadata.

    """

    path = project_root / "config" / "project.yaml"
    if not path.exists():
        raise FileNotFoundError("Missing config/project.yaml")

    return yaml.safe_load(path.read_text()) or {}


def save_project_metadata(project_root: pathlib.Path, data: dict) -> None:
    """
    Read project metadata.

    Parameters
    ----------
    project_root:
        Root path for the project.
    data:
        Project metadata to save.

    """

    path = project_root / "config" / "project.yaml"
    path.write_text(yaml.safe_dump(data, sort_keys=False))

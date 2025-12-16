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


def load_data_registry(project_root: pathlib.Path) -> dict:
    """
    Read registry of datasets from project config file.

    Parameters
    ----------
    project_root:
        Root path for the project.

    Returns
    -------
     :
        Project dataset registry.

    """

    registry_path = project_root / "config" / "data_registry.yaml"
    if not registry_path.exists():
        return {"datasets": []}

    return yaml.safe_load(registry_path.read_text()) or {"datasets": []}


def save_data_registry(project_root: pathlib.Path, data: dict) -> None:
    """
    Write registry of datasets to file.

    Parameters
    ----------
    project_root:
        Root path for the project.
    data:
        Project dataset registry to save.

    """

    registry_path = project_root / "config" / "data_registry.yaml"
    registry_path.write_text(yaml.safe_dump(data, sort_keys=False))


def load_unit_registry(project_root: pathlib.Path) -> dict:
    """
    Read registry of work units from file.

    Parameters
    ----------
    project_root:
        Root path for the project.

    Returns
    -------
     :
        Work unit registry.

    """

    registry_path = project_root / "config" / "unit_registry.yaml"
    if not registry_path.exists():
        return {"units": {}}

    return yaml.safe_load(registry_path.read_text()) or {"units": {}}


def save_unit_registry(project_root: pathlib.Path, data: dict) -> None:
    """
    Write registry of work units to file.

    Parameters
    ----------
    project_root:
        Root path for the project.
    data:
        Work unit registry to save.

    """

    registry_path = project_root / "config" / "unit_registry.yaml"
    registry_path.write_text(yaml.safe_dump(data, sort_keys=False))

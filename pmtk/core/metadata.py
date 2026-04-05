"""
Utilities for handling project metadata.

:copyright:
    2025, Conor A. Bacon
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

import pathlib
from typing import Any, Mapping

import typer
import yaml

from pmtk.utils import find_project_root


def config_path(*parts: str) -> pathlib.Path:
    return find_project_root() / ".config" / pathlib.Path(*parts)


def project_metadata_path() -> pathlib.Path:
    return config_path("project.yaml")


def data_registry_path() -> pathlib.Path:
    return config_path("data_registry.yaml")


def work_unit_registry_path() -> pathlib.Path:
    return config_path("unit_registry.yaml")


def save_yaml(path: pathlib.Path, data: Mapping[str, Any]) -> None:
    """
    Utility for writing out a keyed dataset to a YAML file.

    Parameters
    ----------
    path:
        Directory to which to write the YAML file.
    data:
        Keyed dataset to be written to the YAML file.

    """

    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True))


def load_yaml(file: pathlib.Path) -> dict:
    """
    Utility for loading a keyed dataset from a YAML file.

    Parameters
    ----------
    file:
        YAML file to be read.

    """

    if not file.exists():
        typer.echo(f"Error: Missing file: {file}", err=True)
        raise typer.Exit(code=1)

    return yaml.safe_load(file.read_text()) or {}


def load_project_metadata() -> dict:
    """
    Read project metadata.

    Returns
    -------
    project_metadata:
        Project metadata.

    Raises
    ------
    FileNotFoundError
        If the user has decided to delete the project metadata file.

    """

    if not project_metadata_path().exists():
        raise FileNotFoundError("Missing .config/project.yaml")

    return yaml.safe_load(project_metadata_path().read_text()) or {}


def load_data_registry() -> dict:
    """
    Read registry of datasets from config file.

    Returns
    -------
    data_registry:
        Project dataset registry.

    """

    if not data_registry_path().exists():
        return {"datasets": {}}

    return yaml.safe_load(data_registry_path().read_text()) or {"datasets": {}}


def load_unit_registry() -> dict:
    """
    Read registry of work units from file.

    Returns
    -------
    work_unit_registry:
        Work unit registry.

    """

    if not work_unit_registry_path().exists():
        return {"work_units": {}}

    return yaml.safe_load(work_unit_registry_path().read_text()) or {"work_units": {}}

"""
Utilities for operations on datasets.

:copyright:
    2025, Conor A. Bacon
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

import pathlib
import yaml


def load_registry(registry_path: pathlib.Path) -> dict:
    """
    Read registry of datasets from project config file.

    Parameters
    ----------
    registry_path:
        Path to registry file to read in.

    Returns
    -------
     :
        Project dataset registry.

    """

    if registry_path.exists():
        return yaml.safe_load(registry_path.read_text()) or {}
    return {"datasets": {}}


def save_registry(registry_path: pathlib.Path, registry: dict) -> None:
    """

    Parameters
    ----------
    registry_path:
        Path to registry file to which to write dataset registry.
    registry:
        Project dataset registry to save.

    """

    registry_path.write_text(yaml.safe_dump(registry, sort_keys=False))

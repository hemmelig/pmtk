"""
Top-level CLI for pmtk.

:copyright:
    2025, Conor A. Bacon
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

import pathlib
from datetime import datetime as dt, UTC

import typer
import yaml

from pmtk.core.datasets import load_registry, save_registry
from pmtk.utils import find_project_root


app = typer.Typer(help="Utilities for operating on dataset.")


@app.command("add")
def add(
    dataset_id: str = typer.Argument(..., help="Dataset identifier"),
    title: str = typer.Option(..., help="Human-readable title"),
    path: pathlib.Path | None = typer.Option(
        None, "--path", help="Optional local file or directory"
    ),
    remote: str | None = typer.Option(
        None, "--remote", help="Remote dataset URI (e.g., Zenodo DOI)"
    ),
    source: str | None = typer.Option(None),
    url: str | None = typer.Option(None),
    license: str | None = typer.Option(None),
) -> None:
    """
    Register a new dataset to project.

    Must be run from within a pmtk project directory.

    Parameters
    ----------
    dataset_id:
        A unique identifier for the dataset.
    title:
        A human-readable title for the dataset.
    path:
        Optional path to a file or directory containing the dataset.
    remote:
        Optional URI for remote dataset.
    source:
        Optional description of the source of the data.
    url:
        Optional URL pointing to source of dataset.
    license:
        Optional description of dataset license.

    """

    project_root = find_project_root()
    if project_root is None:
        typer.echo("Error: Not in a pmtk project. No .pmtk-lock file found.", err=True)
        raise typer.Exit(code=1)

    now = dt.now(UTC).isoformat() + "Z"

    metadata_dir = project_root / "data" / "metadata"
    metadata_dir.mkdir(parents=True, exist_ok=True)

    metadata_path = metadata_dir / f"{dataset_id}.yaml"

    metadata = {
        "id": dataset_id,
        "title": title,
        "type": "external",
        "provenance": {
            "source": source,
            "url": url,
            "accessed": now,
        },
        "ownership": {
            "license": license,
        },
        "storage": {
            "local": str(path) if path else None,
            "remote": remote,
        },
    }

    metadata_path.write_text(yaml.safe_dump(metadata, sort_keys=False))

    registry_path = project_root / "config" / "data_registry.yaml"
    registry = load_registry(registry_path)

    registry.setdefault("datasets", {})[dataset_id] = {
        "title": title,
        "type": "external",
        "status": "active",
        "storage": {
            "local": str(path) if path else None,
            "remote": remote,
        },
        "metadata": str(metadata_path.relative_to(project_root)),
        "added": now,
    }

    save_registry(registry_path, registry)

    typer.echo(f"  Dataset '{dataset_id}' registered.")

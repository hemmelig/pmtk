"""
Core functions for operations concerning datasets.

:copyright:
    2025, Conor A. Bacon
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

import pathlib
from datetime import datetime as dt, UTC

import pooch
import requests
import typer
import yaml

from pmtk.utils import find_project_root
from .fetch import get_processor
from .metadata import load_data_registry, save_data_registry


def add_dataset(
    dataset_id: str,
    title: str,
    dtype: str | None,
    local_path: pathlib.Path | None,
    remote_provider: str | None,
    remote_id: str | None,
    inspect_remote: bool | None,
    license: str | None,
    owner: str | None,
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
    dtype:
    local_path:
        Optional path to a file or directory containing the dataset.
    remote_provider:
    remote_id:
        Optional URI for remote dataset.
    license:
        Optional description of dataset license.
    owner:

    """

    project_root = find_project_root()
    if project_root is None:
        typer.echo("Error: Not in a pmtk project. No .pmtk-lock file found.", err=True)
        raise typer.Exit(code=1)

    now = dt.now(UTC).isoformat() + "Z"

    files = []

    if remote_provider == "zenodo" and remote_id and inspect_remote:
        record_id = remote_id.split(".")[-1]
        try:
            files = get_zenodo_files(record_id)
        except Exception as exc:
            typer.echo(f"Warning: Failed to inspect Zenodo record: {exc}", err=True)


    metadata_path = project_root / "data" / "metadata" / f"{dataset_id}.yaml"
    metadata = {
        "id": dataset_id,
        "title": title,
        "description": "",
        "dtype": dtype,
        "ownership": {
            "owner": owner,
            "license": license,
        },
        "storage": {
            "local": {
                "path": str(local_path) if local_path else None,
            },
            "remote": {
                "provider": remote_provider,
                "identifier": remote_id,
                "url": (
                    f"https://zenodo.org/record/{remote_id.split('.')[-1]}"
                    if remote_provider == "zenodo" and remote_id
                    else None
                ),
            },
        },
        "files": files,
    }
    metadata_path.write_text(yaml.safe_dump(metadata, sort_keys=False))

    registry = load_data_registry(project_root)
    registry.setdefault("datasets", {})[dataset_id] = {
        "title": title,
        "type": dtype,
        "storage": {
            "local": str(local_path) if local_path else None,
            "remote": remote_id,
        },
        "metadata": str(metadata_path.relative_to(project_root)),
        "added": now,
    }
    save_data_registry(project_root, registry)

    typer.echo(f"  Dataset '{dataset_id}' registered.")


def report_dataset(dataset_id: str) -> None:
    project_root = find_project_root()
    if project_root is None:
        typer.echo("  Not inside a pmtk project.")
        raise typer.Exit(1)

    metadata_path = project_root / "data" / "metadata" / f"{dataset_id}.yaml"

    if not metadata_path.exists():
        typer.echo(f"  Dataset '{dataset_id}' not found.")
        raise typer.Exit(1)

    data = yaml.safe_load(metadata_path.read_text())

    def fmt(value):
        return value if value not in (None, "", []) else "(not set)"

    typer.echo(f"\nDataset: {data['id']}")
    typer.echo(f"Title:   {data['title']}")
    typer.echo(f"Type:    {data.get('dtype')}")

    typer.echo("Description:")
    typer.echo(f"  {fmt(data.get('description'))}\n")

    typer.echo("Ownership:")
    typer.echo(f"  Owner:   {fmt(data.get('ownership', {}).get('owner'))}")
    typer.echo(f"  License: {fmt(data.get('ownership', {}).get('license'))}\n")

    typer.echo("Storage:")
    storage = data.get("storage", {})
    local = storage.get("local", {})
    remote = storage.get("remote", {})

    typer.echo(
        f"  Local:  {fmt(local.get('path'))}"
    )
    if remote and remote.get("identifier"):
        typer.echo(f"  Remote: {remote.get('provider')}:{remote.get('identifier')}")
    else:
        typer.echo("  Remote: (none)")
    typer.echo("")

    typer.echo("Files:")
    files = data.get("files", [])
    if not files:
        typer.echo("  (none registered)\n")
    else:
        for f in files:
            typer.echo(f"  - {f.get('name')}")
            cs = f.get("checksum", {})
            typer.echo(f"      checksum: {cs.get('algorithm')}:{cs.get('value')}")
            archive = f.get("archive", {})
            if archive:
                typer.echo(
                    f"      archive: {archive.get('format')} "
                    f"(unpack={archive.get('unpack')})"
                )
        typer.echo("")

    typer.echo("Notes:")
    notes = data.get("notes", [])
    if not notes:
        typer.echo("  (none)")
    else:
        for n in notes:
            typer.echo(f"  - {n}")


def fetch_dataset(dataset_id: str, dry_run: bool, force: bool, no_unpack: bool):

    project_root = find_project_root()
    if project_root is None:
        typer.echo("Error: Not in a pmtk project. No .pmtk-lock file found.", err=True)
        raise typer.Exit(code=1)

    metadata_path = project_root / "data" / "metadata" / f"{dataset_id}.yaml"
    if not metadata_path.exists():
        typer.echo(f"  Dataset '{dataset_id}' not found.")
        raise typer.Exit(1)
    metadata = yaml.safe_load(metadata_path.read_text())

    remote = metadata.get("storage", {}).get("remote")
    local = metadata.get("storage", {}).get("local", {})

    if not remote or not remote.get("identifier"):
        typer.echo("  Dataset has no remote storage defined.")
        raise typer.Exit(1)

    files = metadata.get("files", [])
    if not files:
        typer.echo("  Dataset defines no remote files to fetch.")
        raise typer.Exit(1)

    local_path = local.get("path")
    if not local_path:
        typer.echo("  Dataset has no local storage path defined.")
        raise typer.Exit(1)

    target_dir = project_root / local_path
    target_dir.mkdir(parents=True, exist_ok=True)

    typer.echo(f"\nFetching dataset: {dataset_id}\n")

    for f in files:
        name = f["name"]
        checksum = f.get("checksum", {})
        archive = f.get("archive", {})

        if not checksum.get("value"):
            typer.echo(f"  File '{name}' has no checksum.")
            raise typer.Exit(1)

        url = f"doi:{remote['identifier']}/{name}"
        known_hash = f"{checksum['algorithm']}:{checksum['value']}"

        processor = None
        if archive and not no_unpack:
            processor = get_processor(archive, target_dir)

        typer.echo(f"- {name}")
        typer.echo(f"    Source: {remote['provider']}:{remote['identifier']}")
        typer.echo(f"    Checksum: {known_hash}")

        if dry_run:
            typer.echo("    Action: would fetch")
            if archive.get("unpack"):
                typer.echo(f"    Action: would unpack to {target_dir}")
            continue

        pooch.retrieve(
            url=url,
            known_hash=known_hash,
            path=target_dir,
            processor=processor,
            progressbar=True,
        )

        typer.echo("      fetched")

    typer.echo("\n  Dataset materialised successfully")


def get_zenodo_files(record_id: str) -> list[dict]:
    """
    Return list of files from a Zenodo record.
    """
    url = f"https://zenodo.org/api/records/{record_id}"
    r = requests.get(url, timeout=30)
    r.raise_for_status()

    data = r.json()
    files = []

    for f in data.get("files", []):
        algo, value = f["checksum"].split(":", 1)

        files.append(
            {
                "name": f["key"],
                "size_bytes": f["size"],
                "checksum": {
                    "algorithm": algo,
                    "value": value,
                },
            }
        )

    return files

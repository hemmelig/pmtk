"""
Core functions for operations concerning dataset records.

:copyright:
    2026, Conor A. Bacon
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

import pathlib
import shutil
from typing import Any, Mapping

import pooch
import typer

from pmtk.core.metadata import (
    data_registry_path,
    load_data_registry,
    load_yaml,
    save_yaml,
)
from pmtk.utils import find_project_root, utc_now_iso


def _safe_load_dataset_metadata(
    project_root: pathlib.Path,
    data_registry: Mapping[str, Any],
    dataset_id: str,
) -> tuple[pathlib.Path, dict[str, Any]]:
    """
    Load metadata for a registered dataset record and validate that it exists.

    Parameters
    ----------
    project_root:
        Root directory of the PMTK project.
    data_registry:
        Parsed project data registry.
    dataset_id:
        Identifier for the dataset record.

    Returns
    -------
    dataset_metadata_file, dataset_metadata:
        Path to the dataset metadata file and the parsed metadata.

    Raises
    ------
    typer.Exit
        If the dataset is not registered or its metadata file cannot be found.

    """

    dataset_entry = data_registry.get("datasets", {}).get(dataset_id)
    if not dataset_entry:
        typer.echo(f"Error: Dataset '{dataset_id}' not found in registry.", err=True)
        raise typer.Exit(code=1)

    dataset_metadata_relative_path = dataset_entry.get("metadata")
    if not dataset_metadata_relative_path:
        typer.echo(
            f"Error: Dataset '{dataset_id}' has no metadata path in registry.",
            err=True,
        )
        raise typer.Exit(code=1)

    dataset_metadata_file = project_root / dataset_metadata_relative_path
    if not dataset_metadata_file.exists():
        typer.echo(
            (
                f"Error: Metadata file for dataset '{dataset_id}' not found: "
                f"{dataset_metadata_relative_path}"
            ),
            err=True,
        )
        raise typer.Exit(code=1)

    dataset_metadata = load_yaml(dataset_metadata_file)

    return dataset_metadata_file, dataset_metadata


def _project_path(project_root: pathlib.Path, value: str | None) -> pathlib.Path:
    """
    Return a path from stored metadata as an absolute project path.

    Parameters
    ----------
    project_root:
        Root directory of the PMTK project.
    value:
        Stored path string, either relative to the project root or absolute.

    Returns
    -------
    path:
        Resolved path, or None if no value was provided.

    """

    path = pathlib.Path(value)

    return path if path.is_absolute() else project_root / path


def _build_processor(
    file_config: Mapping[str, Any] | None,
    target_path: pathlib.Path,
) -> pooch.processors.ExtractorProcessor | None:
    """
    Construct a Pooch processor from file metadata.

    Parameters
    ----------
    file_cfg:
        File metadata from the dataset record.
    target_path:
        Final target path for the fetched output. For ``unzip`` this is the extraction
        directory.

    Returns
    -------
    pooch.processors.ExtractorProcessor | None
        Configured processor, or None if the file is fetched as-is.

    Raises
    ------
    typer.Exit
        If the processor kind is not supported.

    """

    processor_config = file_config.get("processor") or {}
    if kind := processor_config.get("kind", "none") == "none":
        return None
    elif kind == "unzip":
        target_path.mkdir(parents=True, exist_ok=True)
        return pooch.Unzip(extract_dir=str(target_path))
    else:
        typer.echo(f"Error: Unsupported processor kind '{kind}'.", err=True)
        raise typer.Exit(code=1)


def _pooch_for_dataset(
    dataset_metadata: Mapping[str, Any],
    cache_dir: pathlib.Path,
) -> pooch.Pooch:
    """
    Build a Pooch instance for a dataset record.

    Parameters
    ----------
    dataset_metadata:
        Parsed metadata for the dataset record.
    cache_dir:
        Cache directory to use for remote downloads.

    Returns
    -------
    fido:
        Configured Pooch instance.

    Raises
    ------
    typer.Exit
        If required Pooch metadata are missing.

    """

    pooch_config = dataset_metadata.get("pooch") or {}
    base_url = pooch_config.get("base_url")
    if not base_url:
        typer.echo("Error: Dataset metadata is missing pooch.base_url.", err=True)
        raise typer.Exit(code=1)

    registry = {}
    for file_config in dataset_metadata.get("files", {}).values():
        file_name = file_config.get("file_name")
        known_hash = file_config.get("known_hash")
        if not file_name or not known_hash:
            continue
        registry[file_name] = known_hash

    fido = pooch.create(
        path=cache_dir,
        base_url=base_url,
        registry=registry,
    )

    return fido


def _fetch_one(
    project_root: pathlib.Path,
    dataset_id: str,
    dataset_meta: Mapping[str, Any],
    file_id: str,
    force: bool = False,
) -> pathlib.Path:
    """
    Fetch one registered file from a dataset record.

    Parameters
    ----------
    project_root:
        Root directory of the PMTK project.
    dataset_id:
        Identifier for the dataset record.
    dataset_meta:
        Parsed metadata for the dataset record.
    file_id:
        Identifier of the file to fetch.
    force:
        If True, remove any existing fetched output before fetching.

    Returns
    -------
    target_path:
        Path to the fetched output in the project.

    Raises
    ------
    typer.Exit
        If the file is not registered or required metadata are missing.

    """

    file_config = dataset_meta.get("files", {}).get(file_id)
    if not file_config:
        typer.echo(
            f"Error: File '{file_id}' is not registered under dataset '{dataset_id}'.",
            err=True,
        )
        raise typer.Exit(code=1)

    file_name = file_config.get("file_name")
    if not file_name:
        typer.echo(f"Error: File '{file_id}' has no file_name.", err=True)
        raise typer.Exit(code=1)

    target_path_str = file_config.get("target_path")
    if not target_path_str:
        typer.echo(f"Error: File '{file_id}' has no target_path.", err=True)
        raise typer.Exit(code=1)

    target_path = _project_path(project_root, target_path_str)

    cache_path = (
        pathlib.Path(pooch.os_cache("pmtk"))
        / project_root.name
        / "datasets"
        / dataset_id
    )
    cache_path.mkdir(parents=True, exist_ok=True)

    fido = _pooch_for_dataset(dataset_meta, cache_path)
    processor = _build_processor(file_config, target_path)

    if force and target_path.exists():
        if target_path.is_dir():
            shutil.rmtree(target_path)
        else:
            target_path.unlink()

    result = fido.fetch(file_name, processor=processor, progressbar=True)

    processor_kind = (file_config.get("processor") or {}).get("kind", "none")
    if processor_kind == "none":
        fetched_file = pathlib.Path(result)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        if fetched_file.resolve() != target_path.resolve():
            shutil.copy2(fetched_file, target_path)
        return target_path
    elif processor_kind == "unzip":
        if not isinstance(result, list):
            typer.echo(
                (
                    f"Error: Expected unzip processor to return a list of extracted "
                    f"files for '{file_id}', got {type(result).__name__}."
                ),
                err=True,
            )
            raise typer.Exit(code=1)

        return target_path
    else:
        typer.echo(f"Error: Unsupported processor kind '{processor_kind}'.", err=True)
        raise typer.Exit(code=1)


def register_dataset_record(
    dataset_id: str,
    title: str,
    doi: str,
    record_url: str,
    source: str,
    license: str | None,
) -> None:
    """
    Register a new dataset record in the project.

    Creates a directory in data/external/ and an entry in .config/data_registry.yaml

    Parameters
    ----------
    dataset_id:
        Identifier for the dataset record.
    title:
        Human-readable name for the dataset record.
    doi:
        Digital Object Identifier for the dataset record.
    record_url:
        URL pointing to where the dataset record is stored.
    source:
        Source of the record, e.g., Zenodo.
    license:
        Optional license indicator.

    """

    project_root = find_project_root()

    now = utc_now_iso()

    metadata_dir = project_root / "data" / "metadata"
    metadata_dir.mkdir(parents=True, exist_ok=True)
    dataset_metadata_file = metadata_dir / f"{dataset_id}.yaml"

    data_registry = load_data_registry()
    if dataset_id in data_registry["datasets"]:
        typer.echo(f"Error: Dataset '{dataset_id}' already exists.", err=True)
        raise typer.Exit(code=1)

    dataset_dir = project_root / "data" / "external" / dataset_id

    dataset_metadata = {
        "id": dataset_id,
        "title": title,
        "type": "external",
        "provenance": {
            "source": source,
            "url": record_url,
            "doi": doi,
            "accessed": now,
        },
        "ownership": {
            "license": license,
        },
        "storage": {
            "local": str(dataset_dir.relative_to(project_root)),
            "remote": record_url,
        },
        "pooch": {
            "base_url": f"doi:{doi}/",
            "registry_mode": "doi",
        },
        "files": {},
    }
    save_yaml(dataset_metadata_file, dataset_metadata)

    data_registry["datasets"][dataset_id] = {
        "title": title,
        "type": "external",
        "status": "active",
        "metadata": str(dataset_metadata_file.relative_to(project_root)),
        "added": now,
        "storage": {
            "local": str(dataset_dir.relative_to(project_root)),
            "remote": record_url,
        },
        "retrieval": {
            "backend": "pooch",
            "mode": "zenodo-record",
        },
    }
    save_yaml(data_registry_path(), data_registry)

    typer.echo(
        f"Dataset record '{dataset_id}' registered successfully at {dataset_dir}."
    )


def scan_dataset_record(
    dataset_id: str,
    overwrite: bool = False,
) -> None:
    """
    Discover files in a DOI-backed dataset record and store them in metadata.

    Parameters
    ----------
    dataset_id:
        Identifier for the dataset record.
    overwrite:
        If True, overwrite existing discovered file entries.

    """

    project_root = find_project_root()

    now = utc_now_iso()

    data_registry = load_data_registry()
    dataset_metadata_file, dataset_metadata = _safe_load_dataset_metadata(
        project_root, data_registry, dataset_id
    )

    pooch_cfg = dataset_metadata.get("pooch", {})
    if pooch_cfg.get("registry_mode") != "doi":
        typer.echo(
            (
                f"Error: Dataset '{dataset_id}' is not configured for "
                "DOI registry discovery."
            ),
            err=True,
        )
        raise typer.Exit(code=1)

    cache_path = (
        pathlib.Path(pooch.os_cache("pmtk"))
        / project_root.name
        / "datasets"
        / dataset_id
    )
    cache_path.mkdir(parents=True, exist_ok=True)

    fido = pooch.create(
        path=cache_path,
        base_url=pooch_cfg["base_url"],
        registry=None,
    )
    fido.load_registry_from_doi()

    files = dataset_metadata.setdefault("files", {})
    dataset_dir = project_root / dataset_metadata["storage"]["local"]

    added, skipped = 0, 0
    for file_name, known_hash in fido.registry.items():
        if file_name in files and not overwrite:
            skipped += 1
            continue

        files[file_name] = {
            "title": pathlib.Path(file_name).name,
            "file_name": file_name,
            "known_hash": known_hash,
            "processor": {"kind": "none"},
            "target_path": str((dataset_dir / file_name).relative_to(project_root)),
            "discovered": True,
            "status": "active",
            "added": now,
        }
        added += 1

    dataset_metadata["provenance"]["accessed"] = now
    save_yaml(dataset_metadata_file, dataset_metadata)

    typer.echo(
        f"Scanned dataset record '{dataset_id}': added {added}, skipped {skipped}."
    )


def fetch_record_files(
    dataset_id: str,
    file_id: str | None = None,
    all_files: bool = False,
    force: bool = False,
) -> None:
    """
    Fetch one registered file or all files for a dataset.

    Parameters
    ----------
    dataset_id:
        Identifier for the dataset record.
    file_id:
        Identifier of file to be fetched.
    all_files:
        If True, fetch all files in record.
    force:
        If True, force overwrite existing data files.

    """

    project_root = find_project_root()

    now = utc_now_iso()

    data_registry = load_data_registry()
    dataset_metadata_file, dataset_metadata = _safe_load_dataset_metadata(
        project_root, data_registry, dataset_id
    )

    files = dataset_metadata.get("files", {})
    if not files:
        typer.echo(f"Error: Dataset '{dataset_id}' has no registered files.", err=True)
        raise typer.Exit(code=1)

    if all_files and file_id is not None:
        typer.echo("Error: Provide either a file_id or --all, not both.", err=True)
        raise typer.Exit(code=1)

    if not all_files and file_id is None:
        typer.echo("Error: Provide a file_id or use --all.", err=True)
        raise typer.Exit(code=1)

    selected = list(files.keys()) if all_files else [file_id]

    for selected_file_id in selected:
        assert selected_file_id is not None
        result_path = _fetch_one(
            project_root=project_root,
            dataset_id=dataset_id,
            dataset_meta=dataset_metadata,
            file_id=selected_file_id,
            force=force,
        )
        typer.echo(f"Fetched '{selected_file_id}' -> {result_path}")

    dataset_metadata.setdefault("provenance", {})["accessed"] = now
    save_yaml(dataset_metadata_file, dataset_metadata)

    dataset_entry = data_registry["datasets"][dataset_id]
    dataset_entry.setdefault("storage", {})
    dataset_entry["storage"]["local"] = dataset_metadata.get("storage", {}).get("local")
    save_yaml(data_registry_path(), data_registry)

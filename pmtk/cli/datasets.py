"""
Modular CLI application for operations concerning datasets.

:copyright:
    2026, Conor A. Bacon
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

import typer

from pmtk.core.datasets import (
    fetch_record_files,
    register_dataset_record,
    scan_dataset_record,
)


app = typer.Typer(help="Utilities for operating on datasets.")


@app.command("add-record")
def add_record(
    dataset_id: str = typer.Argument(..., help="Dataset identifier"),
    title: str = typer.Option(..., help="Human-readable title"),
    doi: str = typer.Option(
        ..., "--doi", help="Zenodo DOI, e.g., 10.5281/zenodo.19350669"
    ),
    record_url: str = typer.Option(..., "--record-url", help="Zenodo record URL"),
    source: str = typer.Option("Zenodo", "--source", help="Dataset source description"),
    license: str | None = typer.Option(None, "--license", help="Dataset license"),
) -> None:
    """
    Register a Zenodo record as a PMTK dataset.

    Must be run from within a pmtk project directory.

    Parameters
    ----------
    dataset_id:
        Name/identifier for the dataset record.
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

    register_dataset_record(dataset_id, title, doi, record_url, source, license)


@app.command("fetch")
def fetch(
    dataset_id: str = typer.Argument(..., help="Dataset identifier"),
    file_id: str | None = typer.Argument(None, help="Optional file identifier"),
    all_files: bool = typer.Option(False, "--all", help="Fetch all registered files"),
    force: bool = typer.Option(False, "--force", help="Overwrite project data"),
) -> None:
    """
    Fetch one registered file or all files for a dataset.

    Parameters
    ----------
    dataset_id:
        Name/identifier for the dataset record.
    file_id:
        Name/identifier of file to be fetched.
    all_files:
        Optional toggle to fetch all files in record.
    force:
        Toggle to force overwrite existing data files.

    """

    fetch_record_files(dataset_id, file_id, all_files, force)


@app.command("scan-record")
def scan_record(
    dataset_id: str = typer.Argument(..., help="Dataset identifier"),
    overwrite: bool = typer.Option(
        False,
        "--overwrite",
        help="Overwrite existing discovered file entries",
    ),
) -> None:
    """
    Discover files in a DOI-backed Zenodo record using pooch and store them in dataset
    metadata.

    Parameters
    ----------
    dataset_id:
        Name/identifier for the dataset record.
    overwrite:
        If True, overwrite existing discovered file entries.

    """

    scan_dataset_record(dataset_id, overwrite)

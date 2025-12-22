"""
Modular CLI application for operations concerning datasets.

:copyright:
    2025, Conor A. Bacon
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

import pathlib

import typer

from pmtk.core.datasets import add_dataset, fetch_dataset, report_dataset


app = typer.Typer(help="Utilities for operating on dataset.")


@app.command("add")
def add(
    dataset_id: str = typer.Argument(..., help="Dataset identifier"),
    title: str = typer.Option(..., help="Human-readable title"),
    dtype: str = typer.Option(
        "external", "--type", help="external | internal | processed"
    ),
    local_path: pathlib.Path | None = typer.Option(
        None, "--local-path", help="Optional local file or directory"
    ),
    inspect_remote: bool = typer.Option(
        False, "--inspect-remote", help="Query Zenodo to list dataset files"
    ),
    remote_provider: str | None = typer.Option(None, "--remote-provider"),
    remote_id: str | None = typer.Option(None, "--remote-id"),
    license: str | None = typer.Option(None),
    owner: str | None = typer.Option(None, "--owner"),
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

    add_dataset(
        dataset_id,
        title=title,
        dtype=dtype,
        local_path=local_path,
        remote_provider=remote_provider,
        remote_id=remote_id,
        inspect_remote=inspect_remote,
        license=license,
        owner=owner,
    )


@app.command("show")
def data_show(dataset_id: str = typer.Argument(...)):
    """
    Show detailed metadata for a registered dataset.
    """

    report_dataset(dataset_id)


@app.command("fetch")
def data_fetch(
    dataset_id: str = typer.Argument(..., help="Dataset identifier"),
    dry_run: bool = typer.Option(False, "--dry-run"),
    force: bool = typer.Option(False, "--force"),
    no_unpack: bool = typer.Option(False, "--no-unpack"),
):
    """
    Fetch remote dataset files and materialise them locally.
    """

    fetch_dataset(dataset_id, dry_run, force, no_unpack)

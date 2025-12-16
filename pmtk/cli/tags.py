"""
Modular CLI application for operations concerning project tags.

:copyright:
    2025, Conor A. Bacon
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

import typer

from pmtk.core.tags import add_tag, remove_tag, list_tags


app = typer.Typer(help="Manage project tags")


@app.command("add")
def tag_add(
    tag: str = typer.Argument(..., help="Unique tag."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Validate only"),
):
    """
    Add a new project tag.

    Must be run from within a pmtk project directory.

    Parameters
    ----------
    tag:
        Tag string to be added to project tags.
    dry_run:
        Toggle to run in preliminary test mode.

    """

    add_tag(tag, dry_run=dry_run)


@app.command("remove")
def tag_remove(tag: str = typer.Argument(..., help="Unique tag.")) -> None:
    """
    Remove an existing project tag.

    Must be run from within a pmtk project directory.

    Parameters
    ----------
    tag:
        Tag string to be removed from project tags.

    """

    remove_tag(tag)


@app.command("list")
def tag_list() -> None:
    """
    Print out all project tags.

    Must be run from within a pmtk project directory.

    """

    list_tags()

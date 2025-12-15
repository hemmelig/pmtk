"""
Top-level CLI for pmtk.

:copyright:
    2025, Conor A. Bacon
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

import typer

from pmtk.core.init import init_project
from .work_units import app as work_unit_app


app = typer.Typer(help="Project Management Toolkit (pmtk)")

app.add_typer(work_unit_app, name="work_units")


@app.command("init")
def init(
    project_name: str = typer.Argument(..., help="Name of the project"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing directory"),
    git: bool = typer.Option(False, "--git", help="Initialise git repository"),
) -> None:
    """
    Create a new project with a standard structure.

    Parameters
    ----------
    project_name:
        A (locally) unique identifier for the project.
    force:
        Toggle to overwrite an existing local directory with the same name.
    git:
        Toggle to initialise a git repository at the same time.

    """

    init_project(project_name, force=force, git=git)


def entrypoint():
    app()

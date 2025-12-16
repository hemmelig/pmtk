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
from pmtk.core.status import status as status_cmd
from .datasets import app as datasets_app
from .tags import app as tag_app
from .work_units import app as work_unit_app


app = typer.Typer(help="Project Management Toolkit (pmtk)")

app.add_typer(work_unit_app, name="unit")
app.add_typer(datasets_app, name="data")
app.add_typer(tag_app, name="tag")


@app.command("init")
def init(
    project_name: str = typer.Argument(..., help="Name of the project"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing directory"),
    git: bool = typer.Option(False, "--git", help="Initialise git repository"),
    tag: list[str] = typer.Option(
        None,
        "--tag",
        help="Project tag (can be repeated)",
    ),
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

    init_project(project_name, force=force, git=git, tags=tag)


@app.command("status")
def status():
    """
    Show project status and basic health checks.

    """

    status_cmd()


def entrypoint():
    app()

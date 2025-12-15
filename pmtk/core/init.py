"""
Utilities for the initialisation of a new project.

:copyright:
    2025, Conor A. Bacon
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

from datetime import datetime as dt, UTC
import pathlib
import subprocess

import typer


PROJECT_DIRS = [
    "archive",
    "config",
    "data",
    "docs",
    "environment",
    "logs",
    "maps",
    "notes",
    "reports",
    "results",
    "tools",
    "workspace"
]

CONFIG_FILES = {
    "project.yaml": "project_name: {}\ncreated: {}\n",
    "data_registry.yaml": "",
    "environment.yaml": "",
    "contacts.yaml": "",
    "tasks.yaml": "",
    "registry.yaml": ""
}

def init_project(name: str, force: bool = False, git: bool = False) -> None:
    """
    Initialise a new project using a standard structure, with optional toggle to also
    initialise a git repository.

    Parameters
    ----------
    project_name:
        A (locally) unique identifier for the project.
    force:
        Toggle to overwrite an existing local directory with the same name.
    git:
        Toggle to initialise a git repository at the same time.

    """

    project_path = pathlib.Path(name)

    if project_path.exists() and not force:
        typer.echo(
            f"Error: Directory '{name}' already exists. Use --force to overwrite."
        )
        raise typer.Exit(code=1)

    # Create main directory tree
    project_path.mkdir(parents=True, exist_ok=True)
    for subdir in PROJECT_DIRS:
        (project_path / subdir).mkdir(parents=True, exist_ok=True)

    # Initialise configuration files
    config_dir = project_path / "config"
    now = dt.now(UTC).isoformat()
    for filename, template in CONFIG_FILES.items():
        content = template.format(name, now) if "{}" in template else template
        (config_dir / filename).write_text(content)

    readme = project_path / "README.md"
    readme.write_text(f"# {name}\n\nProject initialised by pmtk on {now}\n")

    lock = project_path / ".pmtk-lock"
    lock.write_text(f"pmtk_version: 0.1.0\ncreated: {now}\n")

    pmignore = project_path / ".pmignore"
    pmignore.write_text("# Add internal or private files here\n")

    if git:
        subprocess.run(["git", "init", str(project_path)])

    typer.echo(f"Project '{name}' created successfully.")

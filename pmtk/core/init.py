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
import yaml

from pmtk.templates import get_template
from pmtk.utils import PROJECT_STRUCTURE


CONFIG_FILES = {
    "project.yaml": "project_name: {}\ncreated: {}\n",
    "data_registry.yaml": "",
    "environment.yaml": "",
    "contacts.yaml": "",
    "tasks.yaml": "",
    "registry.yaml": "",
}


def create_tree(base: pathlib.Path, tree: dict) -> None:
    for name, subtree in tree.items():
        path = base / name
        path.mkdir(parents=True, exist_ok=True)
        if subtree:
            create_tree(path, subtree)


def init_project(
    name: str, force: bool = False, git: bool = False, tags: list[str] | None = None
) -> None:
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
    tags:
        Optional project tags.

    """

    typer.echo(f"Initialising '{name}' project...")

    project_path = pathlib.Path(name)
    if project_path.exists() and not force:
        typer.echo(
            f"Error: Directory '{name}' already exists. Use --force to overwrite."
        )
        raise typer.Exit(code=1)

    typer.echo("  ...creating main directory tree...", nl=False)
    project_path.mkdir(parents=True, exist_ok=True)
    create_tree(project_path, PROJECT_STRUCTURE)
    typer.echo(typer.style("success!", fg=typer.colors.GREEN, bold=True))

    typer.echo("  ...initialising config files...", nl=False)
    config_dir = project_path / "config"
    now = dt.now(UTC).isoformat()
    for filename, template in CONFIG_FILES.items():
        content = template.format(name, now) if "{}" in template else template
        (config_dir / filename).write_text(content)
    project_metadata = {
        "project_name": name,
        "created": now,
        "tags": tags or [],
    }

    project_yaml = config_dir / "project.yaml"
    project_yaml.write_text(yaml.safe_dump(project_metadata, sort_keys=False))
    typer.echo(typer.style("success!", fg=typer.colors.GREEN, bold=True))

    typer.echo("  ...creating PMTK project files...", nl=False)
    readme = project_path / "README.md"
    readme.write_text(f"# {name}\n\nProject initialised by pmtk on {now}\n")

    lock = project_path / ".pmtk-lock"
    lock.write_text(f"pmtk_version: 0.1.0\ncreated: {now}\n")

    pmignore = project_path / ".pmignore"
    pmignore.write_text("# Add internal or private files here\n")

    pre_commit = project_path / ".pre-commit-config.yaml"
    pre_commit.write_text(get_template("pre-commit-config.yaml"))
    typer.echo(typer.style("success!", fg=typer.colors.GREEN, bold=True))

    if git:
        typer.echo("  ...initialising git repository...", nl=False)
        result = subprocess.run(
            ["git", "init", str(project_path)],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            typer.echo(
                f"Warning: Failed to initialise git repository: {result.stderr}",
                err=True,
            )
        else:
            pre_commit_result = subprocess.run(
                ["pre-commit", "install"],
                cwd=str(project_path),
                capture_output=True,
                text=True,
            )

            if pre_commit_result.returncode == 0:
                typer.echo("repository initialised with pre-commit hooks.")
            else:
                typer.echo("repository initialised without pre-commit hooks.")

    typer.echo(
        f"Project '{name}' creation "
        + typer.style("successful.", fg=typer.colors.GREEN, bold=True)
    )

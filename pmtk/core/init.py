"""
Utilities for the initialisation of a new project.

:copyright:
    2025, Conor A. Bacon
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

import pathlib
import subprocess

import typer
import yaml

from pmtk.templates import get_template
from pmtk.utils import PROJECT_STRUCTURE, utc_now_iso


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
    config_dir = project_path / ".config"
    now = utc_now_iso()
    project_metadata = {
        "project_name": name,
        "created": now,
        "tags": [],
        "status": "active",
        "contacts": {
            "owner": "",
            "collaborators": [],
        },
    }

    (config_dir / "project.yaml").write_text(
        yaml.safe_dump(project_metadata, sort_keys=False)
    )
    typer.echo(typer.style("success!", fg=typer.colors.GREEN, bold=True))

    (config_dir / "data_registry.yaml").write_text(
        yaml.safe_dump({"datasets": {}}, sort_keys=False)
    )
    (config_dir / "unit_registry.yaml").write_text(
        yaml.safe_dump({"work_units": {}}, sort_keys=False)
    )

    typer.echo("  ...creating PMTK project files...", nl=False)
    (project_path / "README.md").write_text(
        f"# {name}\n\n## Project Management\n\nThis project is managed using the "
        "[Project Management ToolKit](https://github.com/hemmelig/pmtk).\n\n"
        f"Project initialised by pmtk on {now}\n"
    )

    (project_path / ".pmtk-lock").write_text(
        yaml.safe_dump(
            {
                "pmtk_version": "0.1.0",
                "schema_version": 1,
                "created": now,
            },
            sort_keys=False,
        )
    )

    (project_path / ".pmignore").write_text("# Add internal or private files here\n")
    (project_path / ".gitignore").write_text(
        "data/external/\ndata/processed/\n.DS_Store\n.venv/\n"
    )

    (project_path / ".pre-commit-config.yaml").write_text(
        get_template("pre-commit-config.yaml")
    )
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

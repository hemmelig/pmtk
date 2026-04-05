"""
Utilities for operating on project tags.

:copyright:
    2025, Conor A. Bacon
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

import re

import typer

from pmtk.utils import find_project_root
from .metadata import load_project_metadata, project_metadata_path, save_yaml


def add_tag(tag: str, dry_run: bool = False):
    """
    Add a new tag to a pmtk project.

    Parameters
    ----------
    tag:
        Tag string to be added to project tags.
    dry_run:
        Toggle to run in preliminary test mode.

    """

    project_root = find_project_root()

    data = load_project_metadata(project_root)
    tags = data.get("tags", [])

    new_tag = normalise_tag(tag)

    if new_tag in tags:
        typer.echo(f"  Tag '{new_tag}' already present.")
        return

    typer.echo(f"  Adding tag: {new_tag}")

    if not dry_run:
        tags.append(new_tag)
        data["tags"] = sorted(tags)
        save_yaml(project_metadata_path(), data)


def remove_tag(tag: str):
    """
    Remove an existing project tag.

    Parameters
    ----------
    tag:
        Tag string to be removed from project tags.

    """

    project_root = find_project_root()

    data = load_project_metadata(project_root)
    tags = data.get("tags", [])

    norm = normalise_tag(tag)

    if norm not in tags:
        typer.echo(f"  Tag '{norm}' not found.")
        return

    tags.remove(norm)
    data["tags"] = tags
    save_yaml(project_metadata_path(), data)

    typer.echo(f"  Removed tag: {norm}")


def list_tags():
    """
    Print out all project tags.

    """

    project_root = find_project_root()

    data = load_project_metadata(project_root)
    tags = data.get("tags", [])

    if not tags:
        typer.echo("(no tags)")
        return

    for tag in tags:
        typer.echo(f"- {tag}")


TAG_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{0,62}$")


def normalise_tag(raw: str) -> str:
    """
    Normalise a project tag.

    Parameters
    ----------
    raw:
        The raw tag string to be normalised.

    Returns
    -------
    tag:
        The normalised tag string.

    """

    tag = raw.strip().lower()
    tag = re.sub(r"[ _]+", "-", tag)
    tag = re.sub(r"-{2,}", "-", tag)

    if not tag:
        raise ValueError("Tag is empty after normalisation")

    if not TAG_PATTERN.match(tag):
        raise ValueError(f"Invalid tag '{raw}' → '{tag}'")

    return tag


def normalise_tags(raw_tags: list[str]) -> list[str]:
    """
    Normalise multiple project tags.

    Parameters
    ----------
    raw_tags:
        Raw tag strings to be normalised.

    Returns
    -------
    tags:
        The normalised tag strings.

    """

    seen = set()
    tags = []

    for raw_tag in raw_tags:
        tag = normalise_tag(raw_tag)
        if tag not in seen:
            seen.add(tag)
            tags.append(tag)

    return tags

"""
Module with some basic templates used across the toolkit.

:copyright:
    2025, Conor A. Bacon
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

import pathlib


TEMPLATES_DIR = pathlib.Path(__file__).parent


def get_template(filename: str) -> str:
    """
    Load a template file by name.

    Parameters
    ----------
    filename:
        Name of the template file to load.

    Returns
    -------
     :
        Contents of the template file.

    """

    template_path = TEMPLATES_DIR / filename
    if not template_path.exists():
        raise FileNotFoundError(f"Template file '{filename}' not found")

    return template_path.read_text()

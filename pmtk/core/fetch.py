from pathlib import Path
import subprocess
import pooch


def get_processor(archive: dict, target_dir: Path):
    """
    Return a Pooch processor based on archive metadata.
    """
    if not archive or not archive.get("unpack", False):
        return None

    fmt = archive.get("format")

    if fmt in ("tar", "tar.gz"):
        return pooch.Untar(extract_dir=target_dir)

    if fmt == "zip":
        return pooch.Unzip(extract_dir=target_dir)

    if fmt == "7z":
        return Un7z(target_dir)

    raise ValueError(f"Unsupported archive format: {fmt}")


class Un7z:
    """
    Custom Pooch processor for 7z archives.
    Requires either `7z` binary or py7zr.
    """

    def __init__(self, extract_dir: Path):
        self.extract_dir = extract_dir

    def __call__(self, fname, action, pooch_):
        if action != "download":
            return fname

        self.extract_dir.mkdir(parents=True, exist_ok=True)

        try:
            subprocess.run(
                ["7z", "x", fname, f"-o{self.extract_dir}"],
                check=True,
            )
        except FileNotFoundError as exc:
            raise RuntimeError(
                "7z archive detected but '7z' binary not found."
            ) from exc

        return self.extract_dir

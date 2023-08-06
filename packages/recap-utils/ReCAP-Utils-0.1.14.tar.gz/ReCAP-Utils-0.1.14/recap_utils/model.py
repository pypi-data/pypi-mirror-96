from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import typing as t


@dataclass
class PathPair:
    """A pair of paths for modification of files."""

    source: Path
    target: Path

    @classmethod
    def create(
        cls, folder_in: Path, folder_out: Path, suffix_in: str, suffix_out: str,
    ) -> t.List[PathPair]:
        files_in = sorted(folder_in.rglob(f"*{suffix_in}"))
        files_out = []

        for file_in in files_in:
            file_out = folder_out / file_in.relative_to(folder_in)
            file_out = file_out.with_suffix(suffix_out)
            file_out.parent.mkdir(parents=True, exist_ok=True)

            files_out.append(file_out)

        return [
            cls(file_in, file_out) for file_in, file_out in zip(files_in, files_out)
        ]

    @staticmethod
    def label(path_pair: t.Optional[PathPair]) -> str:
        """Generate a string for representing a path pair.

        Args:
            path_pair: The item that should be represented.

        Returns:
            A label for use in UI contexts.
        """

        if path_pair:
            return path_pair.source.name
        return ""

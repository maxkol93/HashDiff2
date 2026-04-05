from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal


@dataclass
class FileEntry:
    path: Path
    name: str  # filename only, no directory
    size: int
    md5: str | None = None
    status: Literal['pending', 'hashing', 'done', 'error'] = 'pending'
    error_msg: str | None = None

    @classmethod
    def from_path(cls, path: Path) -> 'FileEntry':
        path = Path(path)
        return cls(
            path=path,
            name=path.name,
            size=path.stat().st_size if path.exists() else 0,
        )


@dataclass
class FilePair:
    left: FileEntry | None
    right: FileEntry | None

    @property
    def match_status(self) -> Literal['match', 'diff', 'unpaired', 'pending']:
        if self.left is None or self.right is None:
            return 'unpaired'
        if self.left.status in ('pending', 'hashing') or self.right.status in ('pending', 'hashing'):
            return 'pending'
        if self.left.status == 'error' or self.right.status == 'error':
            return 'unpaired'
        if self.left.md5 and self.right.md5:
            return 'match' if self.left.md5 == self.right.md5 else 'diff'
        return 'pending'


@dataclass
class AppState:
    left_files: list[FileEntry] = field(default_factory=list)
    right_files: list[FileEntry] = field(default_factory=list)
    pairs: list[FilePair] = field(default_factory=list)

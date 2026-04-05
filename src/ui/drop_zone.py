from __future__ import annotations
import tkinter as tk
from pathlib import Path
from typing import Callable

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    _DND_AVAILABLE = True
except ImportError:
    _DND_AVAILABLE = False


def _parse_dnd_paths(data: str) -> list[Path]:
    """Parse the raw DnD event.data string into a list of Paths.

    tkinterdnd2 returns paths space-separated; paths with spaces are wrapped in {}.
    """
    paths: list[Path] = []
    data = data.strip()
    i = 0
    while i < len(data):
        if data[i] == '{':
            end = data.index('}', i)
            paths.append(Path(data[i + 1:end]))
            i = end + 2  # skip } and trailing space
        else:
            j = data.find(' ', i)
            if j == -1:
                paths.append(Path(data[i:]))
                break
            paths.append(Path(data[i:j]))
            i = j + 1
    return paths


class DropZone(tk.Frame):
    """Drag-and-drop target. Calls on_files_dropped(paths) when files are dropped."""

    def __init__(
        self,
        parent: tk.Widget,
        label: str,
        on_files_dropped: Callable[[list[Path]], None],
        **kwargs,
    ) -> None:
        super().__init__(parent, **kwargs)
        self._on_files_dropped = on_files_dropped

        self.configure(
            relief='groove', borderwidth=2,
            bg='#f0f4f8',
        )

        self._label = tk.Label(
            self,
            text=label,
            font=('Segoe UI', 10),
            fg='#6c757d',
            bg='#f0f4f8',
        )
        self._label.pack(expand=True, pady=12)

        if _DND_AVAILABLE:
            self.drop_target_register(DND_FILES)
            self.dnd_bind('<<Drop>>', self._on_drop)
            self._label.drop_target_register(DND_FILES)
            self._label.dnd_bind('<<Drop>>', self._on_drop)

    def _on_drop(self, event: tk.Event) -> None:
        paths = _parse_dnd_paths(event.data)
        files = []
        dirs = []
        for p in paths:
            if p.is_dir():
                dirs.append(p)
            else:
                files.append(p)

        if dirs:
            self._show_dirs_warning()
        if files:
            self._on_files_dropped(files)

    def _show_dirs_warning(self) -> None:
        import tkinter.messagebox as mb
        mb.showwarning(
            'HashDiff',
            'Папки не поддерживаются. Перетащите файлы.',
            parent=self,
        )

from __future__ import annotations
import tkinter as tk
from models import FileEntry, FilePair

COLORS = {
    'match':    '#d4edda',
    'diff':     '#f8d7da',
    'unpaired': '#e2e3e5',
    'pending':  '#ffffff',
}

STATUS_TEXT = {
    'match':    '✓ Идентичны',
    'diff':     '✗ Отличаются',
    'unpaired': '— Нет пары',
    'pending':  '⏳ Вычисляется...',
}

MAX_NAME_LEN = 30


class PairRow(tk.Frame):
    """One comparison row: [left file info] | [status] | [right file info]."""

    def __init__(self, parent: tk.Widget, **kwargs) -> None:
        super().__init__(parent, **kwargs)
        self.configure(relief='flat', borderwidth=0)

        self._left_label = tk.Label(
            self, anchor='w', justify='left',
            font=('Consolas', 9), wraplength=260,
        )
        self._status_label = tk.Label(
            self, anchor='center', justify='center',
            font=('Segoe UI', 9, 'bold'), width=16,
        )
        self._right_label = tk.Label(
            self, anchor='w', justify='left',
            font=('Consolas', 9), wraplength=260,
        )

        sep = tk.Frame(self, height=1, bg='#cccccc')

        self._left_label.pack(side='left', fill='both', expand=True, padx=(8, 4), pady=4)
        self._status_label.pack(side='left', padx=4, pady=4)
        self._right_label.pack(side='left', fill='both', expand=True, padx=(4, 8), pady=4)
        sep.pack(side='bottom', fill='x')

    def render(self, pair: FilePair) -> None:
        status = pair.match_status
        color = COLORS[status]
        self.configure(bg=color)
        self._left_label.configure(text=self._format_entry(pair.left), bg=color)
        self._status_label.configure(text=STATUS_TEXT[status], bg=color)
        self._right_label.configure(text=self._format_entry(pair.right), bg=color)

    def _format_entry(self, entry: FileEntry | None) -> str:
        if entry is None:
            return ''
        name = entry.name
        if len(name) > MAX_NAME_LEN:
            name = name[:MAX_NAME_LEN - 1] + '…'
        if entry.status == 'error':
            return f'{name}\n⚠ {entry.error_msg}'
        if entry.md5:
            size_str = self._fmt_size(entry.size)
            return f'{name}\n{entry.md5}  ({size_str})'
        return f'{name}\n...'

    @staticmethod
    def _fmt_size(size: int) -> str:
        for unit in ('B', 'KB', 'MB', 'GB'):
            if size < 1024:
                return f'{size:.0f} {unit}'
            size /= 1024
        return f'{size:.1f} TB'

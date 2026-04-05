from __future__ import annotations
import sys
import tkinter as tk
import tkinter.filedialog as fd
from pathlib import Path

# DPI awareness on Windows (must be called before any Tk window is created)
try:
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

try:
    from tkinterdnd2 import TkinterDnD
    _ROOT_CLASS = TkinterDnD.Tk
except ImportError:
    _ROOT_CLASS = tk.Tk

from models import AppState, FileEntry, FilePair
from hasher import hash_file_async
from matcher import compute_pairs
from ui.drop_zone import DropZone
from ui.pair_row import PairRow
from ui.scrollable import ScrollableFrame

APP_TITLE = 'HashDiff'
WIN_MIN_W = 900
WIN_MIN_H = 600
HEADER_BG = '#2c3e50'
HEADER_FG = '#ffffff'
PANEL_BG = '#f8f9fa'
BTN_BG = '#3498db'
BTN_FG = '#ffffff'
BTN_ACTIVE = '#2980b9'


class HashDiffApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.state = AppState()
        self._setup_window()
        self._build_ui()

    # ------------------------------------------------------------------
    # Window setup
    # ------------------------------------------------------------------

    def _setup_window(self) -> None:
        self.root.title(APP_TITLE)
        self.root.minsize(WIN_MIN_W, WIN_MIN_H)
        self.root.geometry(f'{WIN_MIN_W}x{WIN_MIN_H}')
        self.root.configure(bg=PANEL_BG)

        # Try to set window icon
        try:
            icon_path = Path(__file__).parent.parent / 'assets' / 'icon.ico'
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except Exception:
            pass

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        self._build_header()

        # Main area: two drop panels + pairs view
        main = tk.Frame(self.root, bg=PANEL_BG)
        main.pack(fill='both', expand=True, padx=8, pady=(0, 8))

        # Top half: side-by-side input panels
        panels_frame = tk.Frame(main, bg=PANEL_BG, height=220)
        panels_frame.pack(fill='x', pady=(8, 4))
        panels_frame.pack_propagate(False)

        left_panel = self._build_panel(panels_frame, 'left')
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 4))

        divider = tk.Frame(panels_frame, width=2, bg='#dee2e6')
        divider.pack(side='left', fill='y')

        right_panel = self._build_panel(panels_frame, 'right')
        right_panel.pack(side='left', fill='both', expand=True, padx=(4, 0))

        # Bottom half: scrollable pairs view
        pairs_label = tk.Label(main, text='Результаты сравнения', font=('Segoe UI', 10, 'bold'),
                               bg=PANEL_BG, fg='#495057', anchor='w')
        pairs_label.pack(fill='x', pady=(4, 2))

        self._pairs_frame = ScrollableFrame(main, bg='#ffffff', relief='groove', borderwidth=1)
        self._pairs_frame.pack(fill='both', expand=True)

        self._empty_label = tk.Label(
            self._pairs_frame.inner,
            text='Добавьте файлы в обе панели для сравнения',
            font=('Segoe UI', 10), fg='#adb5bd', bg='#ffffff',
        )
        self._empty_label.pack(pady=30)

    def _build_header(self) -> None:
        header = tk.Frame(self.root, bg=HEADER_BG, height=48)
        header.pack(fill='x')
        header.pack_propagate(False)

        tk.Label(
            header, text='HashDiff',
            font=('Segoe UI', 14, 'bold'),
            fg=HEADER_FG, bg=HEADER_BG,
        ).pack(side='left', padx=16, pady=8)

        tk.Label(
            header, text='Сравнение файлов по MD5',
            font=('Segoe UI', 10),
            fg='#95a5a6', bg=HEADER_BG,
        ).pack(side='left', pady=8)

    def _build_panel(self, parent: tk.Widget, side: str) -> tk.Frame:
        panel = tk.Frame(parent, bg=PANEL_BG)

        label_text = ('Левая панель' if side == 'left' else 'Правая панель')
        tk.Label(panel, text=label_text, font=('Segoe UI', 10, 'bold'),
                 bg=PANEL_BG, fg='#495057').pack(anchor='w', pady=(0, 4))

        # Drop zone
        drop_zone = DropZone(
            panel,
            label='Перетащите файлы сюда',
            on_files_dropped=lambda paths, s=side: self._on_files_added(paths, s),
            bg='#f0f4f8',
        )
        drop_zone.pack(fill='x', ipady=8)

        # Buttons
        btn_frame = tk.Frame(panel, bg=PANEL_BG)
        btn_frame.pack(fill='x', pady=(6, 0))

        add_btn = tk.Button(
            btn_frame, text='+ Добавить файл',
            font=('Segoe UI', 9),
            bg=BTN_BG, fg=BTN_FG, activebackground=BTN_ACTIVE,
            relief='flat', cursor='hand2', padx=8, pady=4,
            command=lambda s=side: self._open_file_dialog(s),
        )
        add_btn.pack(side='left', padx=(0, 6))

        clear_btn = tk.Button(
            btn_frame, text='Очистить',
            font=('Segoe UI', 9),
            bg='#e9ecef', fg='#495057', activebackground='#dee2e6',
            relief='flat', cursor='hand2', padx=8, pady=4,
            command=lambda s=side: self._clear_panel(s),
        )
        clear_btn.pack(side='left')

        # File list (small scrollable area inside the panel)
        list_frame = ScrollableFrame(panel, bg='#ffffff', relief='groove', borderwidth=1, height=80)
        list_frame.pack(fill='x', pady=(6, 0))
        list_frame.pack_propagate(False)

        if side == 'left':
            self._left_list = list_frame
        else:
            self._right_list = list_frame

        return panel

    # ------------------------------------------------------------------
    # File operations
    # ------------------------------------------------------------------

    def _open_file_dialog(self, side: str) -> None:
        paths = fd.askopenfilenames(
            title='Выберите файлы',
            parent=self.root,
        )
        if paths:
            self._on_files_added([Path(p) for p in paths], side)

    def _on_files_added(self, paths: list[Path], side: str) -> None:
        for path in paths:
            try:
                entry = FileEntry.from_path(path)
            except Exception:
                continue
            if side == 'left':
                self.state.left_files.append(entry)
            else:
                self.state.right_files.append(entry)
            hash_file_async(
                entry,
                on_complete=lambda e: self.root.after(0, lambda entry=e: self._on_hash_complete(entry)),
            )

        self._recompute_and_refresh()

    def _clear_panel(self, side: str) -> None:
        if side == 'left':
            self.state.left_files.clear()
            self._left_list.clear()
        else:
            self.state.right_files.clear()
            self._right_list.clear()
        self._recompute_and_refresh()

    def _on_hash_complete(self, _entry: FileEntry) -> None:
        """Called in main thread after a worker finishes hashing."""
        self._recompute_and_refresh()

    # ------------------------------------------------------------------
    # State + UI refresh
    # ------------------------------------------------------------------

    def _recompute_and_refresh(self) -> None:
        self.state.pairs = compute_pairs(self.state.left_files, self.state.right_files)
        self._refresh_file_lists()
        self._refresh_pairs_view()

    def _refresh_file_lists(self) -> None:
        for list_frame, files in (
            (self._left_list, self.state.left_files),
            (self._right_list, self.state.right_files),
        ):
            list_frame.clear()
            for entry in files:
                icon = {'pending': '⏳', 'hashing': '⏳', 'done': '✓', 'error': '⚠'}.get(entry.status, '')
                color = {'done': '#155724', 'error': '#721c24'}.get(entry.status, '#495057')
                tk.Label(
                    list_frame.inner,
                    text=f'{icon} {entry.name}',
                    font=('Segoe UI', 9), fg=color, bg='#ffffff',
                    anchor='w',
                ).pack(fill='x', padx=6, pady=1)

    def _refresh_pairs_view(self) -> None:
        self._pairs_frame.clear()

        if not self.state.pairs:
            tk.Label(
                self._pairs_frame.inner,
                text='Добавьте файлы в обе панели для сравнения',
                font=('Segoe UI', 10), fg='#adb5bd', bg='#ffffff',
            ).pack(pady=30)
            return

        for pair in self.state.pairs:
            row = PairRow(self._pairs_frame.inner, bg='#ffffff')
            row.pack(fill='x')
            row.render(pair)


def main() -> None:
    root = _ROOT_CLASS()
    app = HashDiffApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()

from __future__ import annotations
import tkinter as tk


class ScrollableFrame(tk.Frame):
    """A frame with a vertical scrollbar. Add child widgets to .inner."""

    def __init__(self, parent: tk.Widget, **kwargs) -> None:
        super().__init__(parent, **kwargs)

        self._canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        self._scrollbar = tk.Scrollbar(self, orient='vertical', command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=self._scrollbar.set)

        self._scrollbar.pack(side='right', fill='y')
        self._canvas.pack(side='left', fill='both', expand=True)

        self.inner = tk.Frame(self._canvas)
        self._window_id = self._canvas.create_window((0, 0), window=self.inner, anchor='nw')

        self.inner.bind('<Configure>', self._on_inner_configure)
        self._canvas.bind('<Configure>', self._on_canvas_configure)

        # Mouse wheel scrolling
        self._canvas.bind('<Enter>', self._bind_mousewheel)
        self._canvas.bind('<Leave>', self._unbind_mousewheel)

    def _on_inner_configure(self, _event: tk.Event) -> None:
        self._canvas.configure(scrollregion=self._canvas.bbox('all'))

    def _on_canvas_configure(self, event: tk.Event) -> None:
        self._canvas.itemconfig(self._window_id, width=event.width)

    def _bind_mousewheel(self, _event: tk.Event) -> None:
        self._canvas.bind_all('<MouseWheel>', self._on_mousewheel)

    def _unbind_mousewheel(self, _event: tk.Event) -> None:
        self._canvas.unbind_all('<MouseWheel>')

    def _on_mousewheel(self, event: tk.Event) -> None:
        self._canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units')

    def clear(self) -> None:
        """Destroy all child widgets in the inner frame."""
        for widget in self.inner.winfo_children():
            widget.destroy()

from __future__ import annotations
import hashlib
import threading
from pathlib import Path
from typing import Callable

from models import FileEntry


def compute_md5(path: Path, progress_callback: Callable[[float], None] | None = None) -> str:
    """Streaming MD5 — does not load the whole file into memory."""
    hasher = hashlib.md5()
    file_size = path.stat().st_size
    bytes_read = 0
    CHUNK_SIZE = 8192

    with open(path, 'rb') as f:
        while chunk := f.read(CHUNK_SIZE):
            hasher.update(chunk)
            bytes_read += len(chunk)
            if progress_callback and file_size > 0:
                progress_callback(bytes_read / file_size)

    return hasher.hexdigest()


def hash_file_async(
    entry: FileEntry,
    on_complete: Callable[[FileEntry], None],
    progress_callback: Callable[[FileEntry, float], None] | None = None,
) -> None:
    """Starts hashing in a daemon thread. on_complete is called from the worker thread —
    use root.after(0, callback) to re-enter the main thread."""

    def worker() -> None:
        entry.status = 'hashing'
        try:
            cb = (lambda p: progress_callback(entry, p)) if progress_callback else None
            entry.md5 = compute_md5(entry.path, progress_callback=cb)
            entry.status = 'done'
        except PermissionError:
            entry.status = 'error'
            entry.error_msg = 'Нет доступа'
        except FileNotFoundError:
            entry.status = 'error'
            entry.error_msg = 'Файл не найден'
        except Exception as e:
            entry.status = 'error'
            entry.error_msg = str(e)
        finally:
            on_complete(entry)

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()

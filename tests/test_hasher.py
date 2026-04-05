import hashlib
import sys
import threading
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from models import FileEntry
from hasher import compute_md5, hash_file_async


def make_entry(path: Path) -> FileEntry:
    return FileEntry(path=path, name=path.name, size=path.stat().st_size)


def test_md5_empty_file(tmp_path):
    f = tmp_path / 'empty.txt'
    f.write_bytes(b'')
    assert compute_md5(f) == 'd41d8cd98f00b204e9800998ecf8427e'


def test_md5_known_content(tmp_path):
    f = tmp_path / 'hello.txt'
    content = b'hello world'
    f.write_bytes(content)
    expected = hashlib.md5(content).hexdigest()
    assert compute_md5(f) == expected


def test_md5_streaming_matches_direct(tmp_path):
    """Streaming result must equal hashlib.md5(full_content)."""
    f = tmp_path / 'big.bin'
    content = b'x' * (1024 * 1024 * 10)  # 10 MB
    f.write_bytes(content)
    expected = hashlib.md5(content).hexdigest()
    assert compute_md5(f) == expected


def test_md5_progress_callback(tmp_path):
    f = tmp_path / 'data.bin'
    f.write_bytes(b'a' * (8192 * 4))
    progress_values = []
    compute_md5(f, progress_callback=lambda p: progress_values.append(p))
    assert progress_values
    assert progress_values[-1] == pytest.approx(1.0)


def test_hash_file_async_success(tmp_path):
    f = tmp_path / 'file.txt'
    f.write_bytes(b'test content')
    entry = make_entry(f)

    completed = threading.Event()
    result_entry = []

    def on_complete(e):
        result_entry.append(e)
        completed.set()

    hash_file_async(entry, on_complete)
    assert completed.wait(timeout=5)
    assert result_entry[0].status == 'done'
    assert result_entry[0].md5 == hashlib.md5(b'test content').hexdigest()


def test_hash_file_async_missing_file(tmp_path):
    path = tmp_path / 'nonexistent.txt'
    entry = FileEntry(path=path, name=path.name, size=0)

    completed = threading.Event()

    def on_complete(e):
        completed.set()

    hash_file_async(entry, on_complete)
    assert completed.wait(timeout=5)
    assert entry.status == 'error'
    assert entry.error_msg == 'Файл не найден'


def test_hash_file_async_sets_hashing_then_done(tmp_path):
    """status transitions: pending → hashing → done."""
    f = tmp_path / 'f.bin'
    f.write_bytes(b'data')
    entry = make_entry(f)

    assert entry.status == 'pending'
    completed = threading.Event()

    def on_complete(e):
        completed.set()

    hash_file_async(entry, on_complete)
    completed.wait(timeout=5)
    assert entry.status == 'done'

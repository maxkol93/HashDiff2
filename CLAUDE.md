# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Windows desktop utility for comparing files by MD5 hash. Drag & drop into two columns, green/red result. **`src/` does not exist yet — this project needs to be implemented.**

## Stack

- Python 3.11, customtkinter + tkinterdnd2, hashlib.md5 (streaming), threading.Thread (daemon)
- Build: PyInstaller --onefile --windowed → `dist/HashDiff.exe`

## Commands

```bat
# Install dependencies
pip install -r requirements.txt

# Run all tests (parallel)
pytest tests/ -n auto

# Run a single test
pytest tests/test_hasher.py::test_compute_md5 -v

# Build exe (Windows)
build.bat
```

## Architecture & Data Flow

Single-process desktop app. The central object is `AppState` (in `app.py`), which owns `left_files`, `right_files` (lists of `FileEntry`), and `pairs` (list of `FilePair`).

**Event flow when a file is dropped:**
1. `DropZone.on_drop` → parse paths → create `FileEntry` objects → add to `AppState`
2. `AppState` calls `compute_pairs()` (matcher.py) → rebuilds `pairs` list
3. UI calls `refresh_ui()` → recreates `PairRow` widgets from pairs
4. For each new entry: `hash_file_async(entry, on_hash_complete)` spawns a daemon thread
5. Worker thread computes MD5, sets `entry.md5 / entry.status`, then calls `on_complete(entry)`
6. `on_complete` must use `root.after(0, callback)` to re-enter main thread
7. Main thread calls `recompute_pairs()` + `refresh_ui()` again

**Matching algorithm** (`matcher.py`): Pass 1 — match by filename (no path). Pass 2 — remaining files matched by insertion order. Files without a pair get `status='unpaired'`.

## Threading (CRITICAL)

- MD5 is computed ONLY in worker threads
- UI is updated ONLY in main thread
- Worker → main transition: `root.after(0, callback)`
- Never call tkinter methods from a worker thread

## Key Implementation Rules

**File paths:** Always `pathlib.Path`, never bare `str`. Use `open(path, 'rb')` for hashing. Fixes Cyrillic and long paths.

**MD5 hashing** (streaming, don't load whole file into memory):
```python
hasher = hashlib.md5()
with open(path, 'rb') as f:
    while chunk := f.read(8192):
        hasher.update(chunk)
return hasher.hexdigest()
```

**Colors:**
```python
COLORS = {'match': '#d4edda', 'diff': '#f8d7da', 'unpaired': '#e2e3e5', 'pending': '#ffffff'}
```

## Common Issues

- DnD broken after PyInstaller → add `--collect-data tkinterdnd2`
- DPI blur on Windows → `ctypes.windll.shcore.SetProcessDpiAwareness(1)` in `app.py`
- Antivirus false positive → add `HashDiff.exe` to exclusions

## Documentation

Read before implementing: [Pseudocode](docs/Pseudocode.md) — exact algorithms, [Refinement](docs/Refinement.md) — edge cases, [test-scenarios](docs/test-scenarios.md) — BDD, [insights](docs/insights.md) — known gotchas/solutions.

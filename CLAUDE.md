# HashDiff — Claude Code Context

## Project
Windows desktop утилита для сравнения файлов по MD5 хешу. Drag & drop в два столбца, зелёный/красный результат.

## Stack
- **Language:** Python 3.11
- **GUI:** customtkinter + tkinterdnd2
- **Hashing:** hashlib.md5 (streaming)
- **Threading:** threading.Thread (daemon)
- **Build:** PyInstaller --onefile --windowed

## Key Rules

### Threading (CRITICAL)
- MD5 вычисляется ТОЛЬКО в worker threads
- UI обновляется ТОЛЬКО в main thread
- Переход из worker → main: `root.after(0, callback)`
- Никогда не вызывай tkinter методы из worker thread

### File Paths
- Всегда использовать `pathlib.Path`, никогда `str` для путей
- `open(path, 'rb')` для хеширования (бинарный режим)
- Это решает кириллику и длинные пути

### MD5 Hashing
```python
# Правильно — streaming
hasher = hashlib.md5()
with open(path, 'rb') as f:
    while chunk := f.read(8192):
        hasher.update(chunk)
return hasher.hexdigest()
```

### Matching Algorithm
1. Сначала match по `filename` (без пути)
2. Остаток — по порядку добавления
3. Файл без пары → status='unpaired'

### Colors
```python
COLORS = {
    'match':    '#d4edda',  # зелёный
    'diff':     '#f8d7da',  # красный
    'unpaired': '#e2e3e5',  # серый
    'pending':  '#ffffff',  # белый
}
```

## File Structure
```
src/
├── app.py          # Entry point, AppState, main window
├── models.py       # FileEntry, FilePair dataclasses
├── hasher.py       # compute_md5(), hash_file_async()
├── matcher.py      # compute_pairs()
└── ui/
    ├── drop_zone.py    # DropZone widget (tkinterdnd2)
    ├── pair_row.py     # PairRow widget
    └── scrollable.py   # ScrollableFrame helper
```

## Parallel Execution Strategy
- Запускать тесты параллельно: `pytest tests/ -n auto`
- Хеширование нескольких файлов — уже параллельно через threading
- Независимые задачи (hasher.py + matcher.py) можно реализовывать параллельно

## Documentation
- [PRD](docs/PRD.md) — что строим
- [Architecture](docs/Architecture.md) — как строим
- [Specification](docs/Specification.md) — user stories + AC
- [Pseudocode](docs/Pseudocode.md) — алгоритмы (ЧИТАЙ ПЕРЕД РЕАЛИЗАЦИЕЙ)
- [Refinement](docs/Refinement.md) — edge cases
- [test-scenarios](docs/test-scenarios.md) — BDD сценарии

## Build
```bat
build.bat
:: Output: dist/HashDiff.exe
```

## Common Issues
- DnD не работает → `--collect-data tkinterdnd2` в PyInstaller
- Кириллика → всегда pathlib.Path
- DPI размытость → `ctypes.windll.shcore.SetProcessDpiAwareness(1)` в app.py
- Антивирус → инструкция в README

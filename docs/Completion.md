# Completion: HashDiff

## Build & Distribution

### Prerequisites
```bash
# Python 3.11+ required
pip install customtkinter==5.2.2 tkinterdnd2==0.3.0 Pillow==10.3.0 pyinstaller==6.6.0
```

### Build Script (build.bat)
```bat
@echo off
echo Building HashDiff...
pyinstaller ^
  --onefile ^
  --windowed ^
  --name HashDiff ^
  --icon assets/icon.ico ^
  --hidden-import tkinterdnd2 ^
  --collect-data tkinterdnd2 ^
  --add-data "assets;assets" ^
  src/app.py

echo.
echo Build complete: dist/HashDiff.exe
pause
```

### CI Pipeline (GitHub Actions, опционально)
```yaml
name: Build HashDiff

on:
  push:
    tags: ['v*']

jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: python -m pytest tests/ -v
      - run: build.bat
      - uses: actions/upload-artifact@v4
        with:
          name: HashDiff-exe
          path: dist/HashDiff.exe
```

## Release Checklist

```
[ ] Все unit тесты проходят
[ ] Manual test checklist пройден
[ ] build.bat выполнен без ошибок
[ ] dist/HashDiff.exe запускается на чистой Windows
[ ] Кириллические пути работают
[ ] Файл > 100 MB хешируется без зависания
[ ] Размер exe < 30 MB
[ ] Обновлён CHANGELOG.md
[ ] Git tag: git tag v1.0.0 && git push origin v1.0.0
```

## Distribution

**Вариант 1: GitHub Releases**
- Загрузить `HashDiff.exe` в GitHub Release
- Приложить SHA256 хеш самого exe (ирония — используем нашу же утилиту)

**Вариант 2: Прямая передача**
- Передать `.exe` файл напрямую
- Никакой установки не требуется

## Versioning
```
v1.0.0 — MVP: dual panel, drag & drop, MD5, green/red
v1.1.0 — SHA256 опция, export report
v2.0.0 — Recursive folder comparison
```

## Troubleshooting Guide

| Проблема | Причина | Решение |
|----------|---------|---------|
| Антивирус блокирует exe | False positive PyInstaller | Добавить в исключения |
| Drag & drop не работает | DLL tkinterdnd2 не найдена | Пересобрать с `--collect-data tkinterdnd2` |
| Кириллика крякозябры | Encoding issue | Убедиться что используется pathlib.Path |
| Окно не открывается | DPI scaling | Добавить `ctypes.windll.shcore.SetProcessDpiAwareness(1)` |
| Медленное хеширование | HDD vs SSD | Нормально, прогресс-бар помогает |

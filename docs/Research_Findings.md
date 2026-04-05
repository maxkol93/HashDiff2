# Research Findings: HashDiff

## Executive Summary
Утилиты сравнения файлов — зрелый рынок с проверенными паттернами UX. Ключевой инсайт: пользователи ценят скорость и минимализм. Python + Tkinter — оптимальный выбор для single-file Windows exe без внешних зависимостей.

## Technology Assessment

### GUI Framework Options
| Framework | Pros | Cons | Verdict |
|-----------|------|------|---------|
| Tkinter | Встроен в Python, нет зависимостей, PyInstaller-friendly | Устаревший вид | ✅ Выбран |
| PyQt6 | Современный вид | Лицензия, размер exe | ❌ |
| wxPython | Нативный вид | Сложная упаковка | ❌ |
| CustomTkinter | Современный Tkinter | Зависимость | ⚠️ Опционально |

**Решение:** Использовать `customtkinter` для современного вида при минимальных зависимостях. PyInstaller справляется с упаковкой.

### MD5 Hashing
- Python встроенный `hashlib.md5()` — достаточно
- Streaming (чтение по чанкам 8192 bytes) — обязательно для больших файлов
- Производительность: ~500 MB/s на современном CPU

### Drag & Drop на Windows
- Tkinter не имеет нативного DnD на Windows
- Решение: библиотека `tkinterdnd2` — проверенное решение, совместимо с PyInstaller
- Альтернатива: кнопка «Открыть файл» через `tkinter.filedialog`

### Архивы
- `.zip`: встроенный `zipfile` (не нужен)
- Хешируем сам файл архива как binary — самый простой и предсказуемый подход
- Не нужно распаковывать — хеш файла = хеш содержимого для integrity check

### PyInstaller
- `pyinstaller --onefile --windowed app.py` — стандартная команда
- `--icon=icon.ico` для иконки
- Размер exe: ~15-25 MB (с customtkinter)
- Антивирусные ложные срабатывания — известная проблема, решается UPX или подписью

## Competitive Landscape
| Tool | Approach | Gap |
|------|----------|-----|
| WinMerge | Text diff, сложный | Нет MD5 panel view |
| HashCheck Shell Extension | Только хеш, нет сравнения | Нет visual comparison |
| MD5summer | Устаревший UI | Нет drag & drop, нет dual panel |
| Beyond Compare | Платный, тяжёлый | Избыточен для задачи |

**Наша ниша:** простой, бесплатный, single-exe, drag & drop, visual dual panel.

## Confidence Assessment
- **High:** Python + tkinterdnd2 решает DnD на Windows
- **High:** hashlib.md5 streaming — оптимальное решение
- **Medium:** customtkinter — хороший компромисс между видом и размером exe

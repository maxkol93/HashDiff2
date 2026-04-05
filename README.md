# HashDiff

Простая Windows утилита для сравнения файлов и архивов по MD5 хешу.

## Quick Start

```
1. unzip hashdiff.zip
2. cd hashdiff
3. claude
4. /init
```

## Что делает

- Перетащи файлы в левую и правую панели
- 🟢 Зелёный = файлы идентичны (MD5 совпадает)
- 🔴 Красный = файлы отличаются
- ⚪ Серый = нет пары для сравнения

## Поддерживаемые форматы

Любые файлы: `.zip`, `.rar`, `.7z`, `.tar.gz`, `.exe`, `.pdf`, `.docx`, и т.д.
Архивы хешируются как единое целое (не содержимое).

## Сборка exe

```bat
pip install -r requirements.txt
build.bat
# Output: dist/HashDiff.exe
```

## Документация

- [PRD](docs/PRD.md) — что строим
- [Architecture](docs/Architecture.md) — как строим
- [Specification](docs/Specification.md) — детальные требования

## Стек

- Python 3.11 + customtkinter + tkinterdnd2
- hashlib.md5 (streaming, не блокирует UI)
- PyInstaller (single exe, без установки)

## Антивирус

PyInstaller exe могут вызывать false positive. Добавьте `HashDiff.exe` в исключения антивируса.

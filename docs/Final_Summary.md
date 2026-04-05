# HashDiff — Executive Summary

## Overview
HashDiff — минималистичная Windows desktop утилита для сравнения файлов и архивов по MD5 хешу. Перетащи файлы в два столбца — мгновенно увидишь: зелёный = одинаковые, красный = разные.

## Problem & Solution
**Problem:** Сравнение файлов по хешу требует консоли, команд и ручного сравнения строк.  
**Solution:** Drag & drop в dual-panel UI с автоматическим выравниванием и цветовой подсветкой.

## Target Users
Разработчики, системные администраторы, технические пользователи Windows.

## Key Features (MVP)
1. **Drag & Drop** — перетащи файлы в левую или правую панель
2. **MD5 Hashing** — streaming вычисление, не блокирует UI
3. **Visual Comparison** — зелёный/красный/серый, текст статуса
4. **Smart Matching** — выравнивание по имени файла, fallback по порядку
5. **Multi-file** — несколько файлов в каждой панели

## Technical Approach
- **Stack:** Python 3.11 + customtkinter + tkinterdnd2 + hashlib
- **Distribution:** Single `.exe` через PyInstaller, без установки
- **Threading:** MD5 вычисляется в фоне, UI не зависает
- **Archives:** .zip/.rar/.7z хешируются как binary (файл целиком)

## Success Metrics
| Metric | Target |
|--------|--------|
| Время хеша 100 MB | < 500ms |
| Размер exe | < 30 MB |
| Запуск без установки | ✓ |
| Поддержка кириллики | ✓ |

## Timeline
| Phase | Features | Est. Time |
|-------|----------|-----------|
| MVP v1.0 | Dual panel, DnD, MD5, colors | 1-2 дня |
| v1.1 | SHA256, export, tooltip | +1 день |
| v2.0 | Folder comparison | +2-3 дня |

## Immediate Next Steps
1. Настроить virtualenv, установить зависимости
2. Реализовать `hasher.py` + тесты
3. Реализовать `matcher.py` + тесты
4. Собрать базовый UI (без DnD)
5. Добавить tkinterdnd2 drag & drop
6. Build exe через PyInstaller

## Documentation Package
- [PRD.md](PRD.md) — что строим
- [Architecture.md](Architecture.md) — как строим
- [Specification.md](Specification.md) — user stories + acceptance criteria
- [Pseudocode.md](Pseudocode.md) — алгоритмы
- [Refinement.md](Refinement.md) — edge cases + тесты
- [Completion.md](Completion.md) — build + distribution

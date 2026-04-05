# Development Guide: HashDiff

## Обзор инструментов

| Инструмент | Тип | Назначение |
|------------|-----|------------|
| `/init` | command | Первый запуск, читает контекст, git init |
| `/feature [name]` | command | Полный lifecycle новой фичи |
| `/myinsights [title]` | command | Захват нетривиального решения |
| `@planner` | agent | Планирование задач |
| `@code-reviewer` | agent | Code review перед мержем |

## Этапы разработки

### 🚀 Этап 1: Старт
```
/init
```

### 🏗️ Этап 2: Реализация ядра (рекомендуемый порядок)
1. `src/models.py` — FileEntry, FilePair dataclasses
2. `src/hasher.py` — compute_md5() + hash_file_async()
3. `src/matcher.py` — compute_pairs()
4. Тесты: `pytest tests/ -v`

### 💻 Этап 3: UI
1. `src/ui/scrollable.py` — ScrollableFrame helper
2. `src/ui/pair_row.py` — PairRow widget
3. `src/ui/drop_zone.py` — DropZone с tkinterdnd2
4. `src/app.py` — главное окно, AppState, сборка всего вместе

### 🧪 Этап 4: Тестирование
- Unit тесты: `pytest tests/ -v`
- Manual: пройди чеклист из `docs/Refinement.md`
- BDD: проверь сценарии из `docs/test-scenarios.md`

### 🔨 Этап 5: Сборка exe
```bat
build.bat
# dist/HashDiff.exe
```

### 🆕 Этап 6: Новые фичи
```
/feature sha256-support
/feature export-report
/feature folder-comparison
```

### 💡 Этап 7: Захват инсайтов (постоянно)
```
/myinsights "tkinterdnd2 не работает после PyInstaller"
```
Проверяй `docs/insights.md` ПЕРЕД дебагом — решение может уже быть там.

## Git Workflow

```
feat | fix | refactor | test | docs | chore
1 логическое изменение = 1 коммит

feat(hasher): streaming MD5 for files >100MB
fix(ui): prevent crash on read-only files
test(matcher): add duplicate filename test
```

## Swarm Agents: когда использовать

| Сценарий | Подход |
|----------|--------|
| hasher.py + matcher.py | Реализовывать параллельно (независимы) |
| UI + тесты | Параллельно через Task tool |
| Новая фича | `@planner` для декомпозиции |
| Перед мержем | `@code-reviewer` |

## Known Gotchas

1. **tkinterdnd2 + PyInstaller:** нужен флаг `--collect-data tkinterdnd2`
2. **UI из worker thread:** НИКОГДА не обновляй tkinter из worker — только `root.after(0, fn)`
3. **Кириллика:** только `pathlib.Path`, никогда голых строк для путей
4. **DPI на Windows:** добавь `ctypes.windll.shcore.SetProcessDpiAwareness(1)` в `app.py`

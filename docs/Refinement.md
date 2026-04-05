# Refinement: HashDiff

## Edge Cases

### Файловые ситуации
| Сценарий | Поведение |
|----------|-----------|
| Файл удалён во время хеширования | status='error', msg='Файл не найден' |
| Файл заблокирован (locked) | status='error', msg='Нет доступа' |
| Файл 0 байт | MD5 вычисляется (d41d8cd98f00b204...), сравниваем нормально |
| Файл > 4 GB | Streaming работает, время ~2-4 мин для HDD |
| Одинаковый файл в обе панели | match=True, зелёный — корректно |
| Один и тот же файл дважды в одну панель | Разрешено, оба показываются |
| Путь с кириллицей | pathlib.Path + open(path, 'rb') — работает |
| Очень длинное имя файла | Truncate в UI, полный путь в tooltip |
| Символические ссылки | Хешируем содержимое target-файла |

### UI ситуации
| Сценарий | Поведение |
|----------|-----------|
| Drop во время хеширования | Добавляем новый файл, продолжаем хешировать старые |
| Clear во время хеширования | Очищаем state, worker threads завершатся сами (daemon=True) |
| Resize окна | Скроллируемые панели адаптируются |
| Много файлов (50+) | Scroll работает, производительность нормальная |
| Одна панель пустая | Вторая работает нормально, результаты серые |

### Архивы
| Формат | Поведение |
|--------|-----------|
| .zip | Хешируем как binary file — корректно |
| .rar | Хешируем как binary file — корректно |
| .7z | Хешируем как binary file — корректно |
| .tar.gz | Хешируем как binary file — корректно |
| Повреждённый архив | Хеш вычислится (от битых байт) — это ожидаемо |

## Testing Strategy

### Unit Tests

```python
# tests/test_hasher.py
def test_md5_known_value():
    """hashlib.md5(b'') == 'd41d8cd98f00b204e9800998ecf8427e'"""
    entry = FileEntry(path=Path('empty.txt'), ...)
    # create temp file, hash it, check known value

def test_md5_streaming_matches_direct():
    """Streaming hash должен давать тот же результат что и hashlib"""
    # create 10MB temp file
    # compare streaming vs hashlib.md5(content)

def test_hash_error_on_missing_file():
    entry = FileEntry(path=Path('/nonexistent/file.txt'), ...)
    # expect status='error'
```

```python
# tests/test_matcher.py
def test_match_by_name():
    left = [FileEntry(name='a.txt'), FileEntry(name='b.txt')]
    right = [FileEntry(name='b.txt'), FileEntry(name='a.txt')]
    pairs = compute_pairs(left, right)
    assert pairs[0].left.name == pairs[0].right.name

def test_fallback_by_order():
    left = [FileEntry(name='x.txt')]
    right = [FileEntry(name='y.txt')]
    pairs = compute_pairs(left, right)
    assert pairs[0].left.name == 'x.txt'
    assert pairs[0].right.name == 'y.txt'

def test_unpaired_files():
    left = [FileEntry(name='a.txt'), FileEntry(name='b.txt')]
    right = [FileEntry(name='a.txt')]
    pairs = compute_pairs(left, right)
    unpaired = [p for p in pairs if p.match_status == 'unpaired']
    assert len(unpaired) == 1
```

### Manual Test Checklist

```
[ ] Drag & Drop одного файла в левую панель
[ ] Drag & Drop одного файла в правую панель
[ ] Одинаковые файлы → зелёный
[ ] Разные файлы → красный
[ ] Drag & Drop нескольких файлов
[ ] Одинаковые имена → правильное выравнивание
[ ] Кнопка "Добавить файл" — диалог открывается
[ ] Кнопка "Очистить" — панель очищается
[ ] Кириллические имена файлов
[ ] Файл > 100 MB — UI не зависает
[ ] Файл .zip — хешируется как файл
[ ] Файл в другой панели отсутствует → серый
[ ] Много файлов (20+) — scroll работает
```

## Performance Benchmarks (targets)

| File Size | Expected Hash Time |
|-----------|-------------------|
| < 1 MB | < 100ms |
| 100 MB | < 500ms |
| 1 GB | < 5s (SSD) |
| 4 GB | < 20s (SSD) |

## Known Limitations

1. **Антивирус:** PyInstaller exe может вызывать false positive. Решение: добавить в исключения или подписать exe.
2. **RAR архивы:** Для RAR нужна внешняя библиотека `rarfile` (требует WinRAR). В MVP хешируем как binary — достаточно для integrity check.
3. **Одинаковые имена:** Если в одной панели два файла с одинаковым именем (из разных папок), matching может быть неоднозначным. Используем первый найденный.

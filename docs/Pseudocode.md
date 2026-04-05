# Pseudocode: HashDiff

## Data Models

```python
@dataclass
class FileEntry:
    path: Path
    name: str           # filename only
    size: int
    md5: str | None = None
    status: Literal['pending', 'hashing', 'done', 'error'] = 'pending'
    error_msg: str | None = None

@dataclass  
class FilePair:
    left: FileEntry | None
    right: FileEntry | None
    
    @property
    def match_status(self) -> Literal['match', 'diff', 'unpaired', 'pending']:
        if self.left is None or self.right is None:
            return 'unpaired'
        if self.left.status == 'pending' or self.right.status == 'pending':
            return 'pending'
        if self.left.md5 and self.right.md5:
            return 'match' if self.left.md5 == self.right.md5 else 'diff'
        return 'pending'

class AppState:
    left_files: list[FileEntry]
    right_files: list[FileEntry]
    pairs: list[FilePair]  # computed
```

## Algorithm: File Matching

```python
def compute_pairs(left: list[FileEntry], right: list[FileEntry]) -> list[FilePair]:
    pairs = []
    right_by_name = {f.name: f for f in right}
    right_used = set()
    left_unmatched = []
    
    # Pass 1: match by filename
    for lf in left:
        if lf.name in right_by_name:
            rf = right_by_name[lf.name]
            pairs.append(FilePair(left=lf, right=rf))
            right_used.add(rf.name)
        else:
            left_unmatched.append(lf)
    
    # Pass 2: remaining by order
    right_unmatched = [f for f in right if f.name not in right_used]
    max_len = max(len(left_unmatched), len(right_unmatched))
    for i in range(max_len):
        lf = left_unmatched[i] if i < len(left_unmatched) else None
        rf = right_unmatched[i] if i < len(right_unmatched) else None
        pairs.append(FilePair(left=lf, right=rf))
    
    return pairs
```

## Algorithm: MD5 Streaming Hash

```python
def compute_md5(path: Path, progress_callback=None) -> str:
    """Streaming MD5 — не загружает файл в память целиком"""
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
```

## Algorithm: Background Hashing

```python
def hash_file_async(entry: FileEntry, on_complete: Callable):
    """Запускает хеширование в отдельном потоке"""
    def worker():
        entry.status = 'hashing'
        try:
            entry.md5 = compute_md5(entry.path)
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
            on_complete(entry)  # вызывается в worker thread → нужен root.after()
    
    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
```

## UI Component: PairRow

```python
class PairRow(tk.Frame):
    """Одна строка сравнения: [левый файл] | [правый файл]"""
    
    COLOR_MAP = {
        'match':    '#d4edda',  # зелёный
        'diff':     '#f8d7da',  # красный
        'unpaired': '#e2e3e5',  # серый
        'pending':  '#ffffff',  # белый
    }
    
    STATUS_TEXT = {
        'match':    '✓ Идентичны',
        'diff':     '✗ Отличаются',
        'unpaired': '— Нет пары',
        'pending':  '⏳ Вычисляется...',
    }
    
    def render(self, pair: FilePair):
        color = self.COLOR_MAP[pair.match_status]
        self.configure(bg=color)
        self.left_label.configure(text=self._format_entry(pair.left), bg=color)
        self.right_label.configure(text=self._format_entry(pair.right), bg=color)
        self.status_label.configure(text=self.STATUS_TEXT[pair.match_status], bg=color)
    
    def _format_entry(self, entry: FileEntry | None) -> str:
        if entry is None:
            return ''
        if entry.status == 'error':
            return f'{entry.name}\n⚠ {entry.error_msg}'
        if entry.md5:
            return f'{entry.name}\n{entry.md5}'
        return f'{entry.name}\n...'
```

## Event Flow

```
User drops file onto LeftPanel
  → on_drop(event) → parse paths from event.data
  → for each path: create FileEntry, add to state.left_files
  → recompute_pairs() → update state.pairs
  → refresh_ui()
  → for each new entry: hash_file_async(entry, on_hash_complete)

on_hash_complete(entry)  [called from worker thread]
  → root.after(0, lambda: handle_hash_result(entry))  [schedule in main thread]
  
handle_hash_result(entry)  [main thread]
  → recompute_pairs()
  → refresh_ui()
```

## App Structure

```python
class HashDiffApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.state = AppState()
        self._build_ui()
    
    def _build_ui(self):
        # Header bar
        # Main content: two panels side by side
        # Left panel: DropZone + FileList + buttons (Add, Clear)
        # Divider
        # Right panel: same
        # Pairs view: scrollable list of PairRow widgets
        pass
    
    def _build_panel(self, side: Literal['left', 'right']) -> DropZone:
        ...
    
    def _build_pairs_view(self) -> ScrollableFrame:
        ...
```

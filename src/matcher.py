from __future__ import annotations
from models import FileEntry, FilePair


def compute_pairs(left: list[FileEntry], right: list[FileEntry]) -> list[FilePair]:
    """
    Match files between left and right panels.
    Pass 1: match by filename (basename only).
    Pass 2: remaining files matched by insertion order.
    Files without a pair become unpaired (None on the missing side).
    """
    pairs: list[FilePair] = []
    right_by_name: dict[str, FileEntry] = {}
    right_used: set[str] = set()

    # Build name index — first occurrence wins for duplicate names
    for f in right:
        if f.name not in right_by_name:
            right_by_name[f.name] = f

    left_unmatched: list[FileEntry] = []

    # Pass 1: match by filename
    for lf in left:
        if lf.name in right_by_name and lf.name not in right_used:
            rf = right_by_name[lf.name]
            pairs.append(FilePair(left=lf, right=rf))
            right_used.add(rf.name)
        else:
            left_unmatched.append(lf)

    # Pass 2: remaining by order
    right_unmatched = [f for f in right if f.name not in right_used]
    max_len = max(len(left_unmatched), len(right_unmatched), 0)
    for i in range(max_len):
        lf = left_unmatched[i] if i < len(left_unmatched) else None
        rf = right_unmatched[i] if i < len(right_unmatched) else None
        pairs.append(FilePair(left=lf, right=rf))

    return pairs

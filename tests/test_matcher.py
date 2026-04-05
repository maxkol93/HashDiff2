import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from models import FileEntry, FilePair
from matcher import compute_pairs


def make_entry(name: str, md5: str | None = None, status: str = 'done') -> FileEntry:
    return FileEntry(path=Path(name), name=name, size=0, md5=md5, status=status)


# ------------------------------------------------------------------
# Basic matching
# ------------------------------------------------------------------

def test_match_by_name():
    left = [make_entry('a.txt'), make_entry('b.txt')]
    right = [make_entry('b.txt'), make_entry('a.txt')]
    pairs = compute_pairs(left, right)
    names = {(p.left.name, p.right.name) for p in pairs}
    assert ('a.txt', 'a.txt') in names
    assert ('b.txt', 'b.txt') in names


def test_fallback_by_order():
    left = [make_entry('x.txt')]
    right = [make_entry('y.txt')]
    pairs = compute_pairs(left, right)
    assert len(pairs) == 1
    assert pairs[0].left.name == 'x.txt'
    assert pairs[0].right.name == 'y.txt'


def test_unpaired_left_extra():
    left = [make_entry('a.txt'), make_entry('b.txt')]
    right = [make_entry('a.txt')]
    pairs = compute_pairs(left, right)
    unpaired = [p for p in pairs if p.match_status == 'unpaired']
    assert len(unpaired) == 1
    assert unpaired[0].right is None


def test_unpaired_right_extra():
    left = [make_entry('a.txt')]
    right = [make_entry('a.txt'), make_entry('c.txt')]
    pairs = compute_pairs(left, right)
    unpaired = [p for p in pairs if p.match_status == 'unpaired']
    assert len(unpaired) == 1
    assert unpaired[0].left is None


def test_empty_both():
    assert compute_pairs([], []) == []


def test_empty_left():
    right = [make_entry('a.txt')]
    pairs = compute_pairs([], right)
    assert len(pairs) == 1
    assert pairs[0].left is None


def test_empty_right():
    left = [make_entry('a.txt')]
    pairs = compute_pairs(left, [])
    assert len(pairs) == 1
    assert pairs[0].right is None


def test_mixed_name_and_order():
    """alpha+beta match by name, gamma+delta match by order."""
    left = [make_entry('alpha.txt'), make_entry('gamma.txt')]
    right = [make_entry('delta.txt'), make_entry('alpha.txt')]
    pairs = compute_pairs(left, right)
    by_left = {p.left.name: p.right.name for p in pairs if p.left and p.right}
    assert by_left['alpha.txt'] == 'alpha.txt'
    assert by_left['gamma.txt'] == 'delta.txt'


# ------------------------------------------------------------------
# FilePair.match_status
# ------------------------------------------------------------------

def test_pair_match_status_match():
    lf = make_entry('a.txt', md5='abc123')
    rf = make_entry('a.txt', md5='abc123')
    pair = FilePair(left=lf, right=rf)
    assert pair.match_status == 'match'


def test_pair_match_status_diff():
    lf = make_entry('a.txt', md5='aaa')
    rf = make_entry('a.txt', md5='bbb')
    pair = FilePair(left=lf, right=rf)
    assert pair.match_status == 'diff'


def test_pair_match_status_pending():
    lf = make_entry('a.txt', status='hashing')
    rf = make_entry('a.txt', md5='bbb')
    pair = FilePair(left=lf, right=rf)
    assert pair.match_status == 'pending'


def test_pair_match_status_unpaired_none():
    pair = FilePair(left=make_entry('a.txt', md5='x'), right=None)
    assert pair.match_status == 'unpaired'


def test_pair_match_status_error_treated_as_unpaired():
    lf = make_entry('a.txt', status='error')
    rf = make_entry('a.txt', md5='abc')
    pair = FilePair(left=lf, right=rf)
    assert pair.match_status == 'unpaired'

"""Fast duplicate file finder using progressive hashing (size -> chunk -> full)."""

import hashlib
import os
import sys
from collections import defaultdict
from pathlib import Path


def hash_file(filepath: Path, chunk_only: bool = False) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        if chunk_only:
            hasher.update(f.read(4096))
        else:
            while chunk := f.read(65536):
                hasher.update(chunk)
    return hasher.hexdigest()


def find_duplicates(root_dir: str | Path) -> dict[str, list[Path]]:
    size_map: dict[int, list[Path]] = defaultdict(list)
    for path in Path(root_dir).rglob("*"):
        if path.is_file() and not path.is_symlink():
            try:
                size_map[path.stat().st_size].append(path)
            except OSError:
                continue

    partial_map: dict[str, list[Path]] = defaultdict(list)
    for paths in (g for g in size_map.values() if len(g) > 1):
        for p in paths:
            try:
                partial_map[f"{p.stat().st_size}_{hash_file(p, True)}"].append(p)
            except OSError:
                continue

    duplicates: dict[str, list[Path]] = defaultdict(list)
    for paths in (g for g in partial_map.values() if len(g) > 1):
        for p in paths:
            try:
                duplicates[hash_file(p)].append(p)
            except OSError:
                continue

    return {k: v for k, v in duplicates.items() if len(v) > 1}


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    print(f"Scanning for duplicates in: {os.path.abspath(target)}")
    results = find_duplicates(target)
    if not results:
        print("No duplicate files found.")
    else:
        for digest, files in results.items():
            print(f"\nMatch [{digest[:12]}...] ({len(files)} files):")
            for f in files:
                print(f"  {f}")

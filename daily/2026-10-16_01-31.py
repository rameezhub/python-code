"""Analyze and display disk space usage of a directory as a terminal bar chart."""

import os
import sys
from pathlib import Path


def get_path_size(path: Path) -> int:
    """Calculate total byte size of a path (file or directory)."""
    if path.is_symlink() or not path.exists():
        return 0
    if path.is_file():
        return path.stat().st_size
    total = 0
    for root, _, files in os.walk(path):
        for file in files:
            p = Path(root) / file
            try:
                if not p.is_symlink():
                    total += p.stat().st_size
            except OSError:
                continue
    return total


def format_size(num_bytes: int) -> str:
    """Format bytes into a human-readable string."""
    val = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(val) < 1024.0:
            return f"{val:6.1f} {unit}"
        val /= 1024.0
    return f"{val:6.1f} PB"


def display_usage(target_path: Path, bar_width: int = 30) -> None:
    """Scan target directory and print an ASCII bar chart of its contents."""
    print(f"Scanning: {target_path.resolve()}\n")
    try:
        entries = list(target_path.iterdir())
    except OSError as err:
        sys.exit(f"Error accessing path: {err}")

    items = [(e.name + ("/" if e.is_dir() else ""), get_path_size(e)) for e in entries]
    items.sort(key=lambda x: x[1], reverse=True)

    max_size = items[0][1] if items else 1
    total_size = sum(size for _, size in items)
    max_label = min(max((len(name) for name, _ in items), default=10), 30)

    for name, size in items[:20]:
        label = (name[: max_label - 3] + "...") if len(name) > max_label else name
        bar = "█" * int((size / max_size) * bar_width) if max_size else ""
        print(f"{label:<{max_label}} | {format_size(size)} | {bar}")

    print("-" * (max_label + bar_width + 13))
    print(f"{'Total':<{max_label}} | {format_size(total_size)}")


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    if not target.is_dir():
        sys.exit(f"Target '{target}' is not a directory.")
    display_usage(target)

"""Analyze and display disk space usage by file extension in a given directory."""

import os
import sys
from collections import defaultdict
from pathlib import Path


def format_size(bytes_val: int) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if bytes_val < 1024.0:
            return f"{bytes_val:6.1f} {unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:6.1f} PB"


def analyze_directory(target_path: Path):
    stats = defaultdict(lambda: {"count": 0, "size": 0})
    total_size = 0
    for root, _, files in os.walk(target_path):
        for file in files:
            try:
                size = (Path(root) / file).stat().st_size
            except (OSError, PermissionError):
                continue
            ext = Path(file).suffix.lower() or "[no ext]"
            stats[ext]["count"] += 1
            stats[ext]["size"] += size
            total_size += size
    return stats, total_size


def print_report(stats: dict, total_size: int, top_n: int = 10):
    if not stats or total_size == 0:
        print("No files found or directory is empty.")
        return
    sorted_exts = sorted(stats.items(), key=lambda x: x[1]["size"], reverse=True)[:top_n]
    print(f"\n{'Extension':<12} {'Count':>7} {'Size':>10} {'Share':>7}  Distribution")
    print("-" * 60)
    for ext, data in sorted_exts:
        pct = (data["size"] / total_size) * 100
        bar = "#" * int(pct / 5)
        print(f"{ext:<12} {data['count']:>7d} {format_size(data['size']):>10} {pct:6.1f}%  {bar}")
    print("-" * 60)
    print(f"Total analyzed: {format_size(total_size).strip()}\n")


if __name__ == "__main__":
    scan_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    if not scan_dir.is_dir():
        sys.exit(f"Error: '{scan_dir}' is not a directory.")
    print(f"Scanning: {scan_dir.resolve()}")
    data, total = analyze_directory(scan_dir)
    print_report(data, total)

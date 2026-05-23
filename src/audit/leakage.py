from __future__ import annotations

from pathlib import Path
from typing import Iterable


def scan_text_for_forbidden_patterns(
    text: str,
    forbidden_patterns: Iterable[str],
) -> list[str]:
    patterns = tuple(forbidden_patterns)
    return [pattern for pattern in patterns if pattern in text]


def scan_file_for_forbidden_patterns(
    path: str | Path,
    forbidden_patterns: Iterable[str],
) -> list[str]:
    file_path = Path(path)
    text = file_path.read_text(encoding="utf-8")
    return scan_text_for_forbidden_patterns(text, forbidden_patterns)


def scan_directory_for_forbidden_patterns(
    directory: str | Path,
    forbidden_patterns: Iterable[str],
    *,
    suffixes: tuple[str, ...] = (".py", ".md", ".txt", ".yml", ".yaml"),
    ignore_dirs: tuple[str, ...] = (".git", "__pycache__"),
) -> dict[str, list[str]]:
    root = Path(directory)
    patterns = tuple(forbidden_patterns)
    findings: dict[str, list[str]] = {}

    for path in root.rglob("*"):
        if any(part in ignore_dirs for part in path.parts):
            continue
        if path.is_file() and path.suffix in suffixes:
            matches = scan_file_for_forbidden_patterns(path, patterns)
            if matches:
                findings[str(path)] = matches

    return findings

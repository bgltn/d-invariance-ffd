from pathlib import Path

from audit.leakage import (
    scan_directory_for_forbidden_patterns,
    scan_file_for_forbidden_patterns,
    scan_text_for_forbidden_patterns,
)


def test_scan_text_finds_forbidden_pattern():
    text = "this file contains SECRET_TOKEN"

    result = scan_text_for_forbidden_patterns(
        text,
        forbidden_patterns=["SECRET_TOKEN"],
    )

    assert result == ["SECRET_TOKEN"]


def test_scan_file_finds_forbidden_pattern(tmp_path: Path):
    file_path = tmp_path / "example.py"
    file_path.write_text("value = 'SECRET_TOKEN'", encoding="utf-8")

    result = scan_file_for_forbidden_patterns(
        file_path,
        forbidden_patterns=["SECRET_TOKEN"],
    )

    assert result == ["SECRET_TOKEN"]


def test_scan_directory_ignores_clean_files(tmp_path: Path):
    file_path = tmp_path / "clean.py"
    file_path.write_text("value = 'PUBLIC_VALUE'", encoding="utf-8")

    result = scan_directory_for_forbidden_patterns(
        tmp_path,
        forbidden_patterns=["SECRET_TOKEN"],
    )

    assert result == {}


def test_scan_directory_reports_matches(tmp_path: Path):
    file_path = tmp_path / "leaky.py"
    file_path.write_text("value = 'SECRET_TOKEN'", encoding="utf-8")

    result = scan_directory_for_forbidden_patterns(
        tmp_path,
        forbidden_patterns=["SECRET_TOKEN"],
    )

    assert str(file_path) in result
    assert result[str(file_path)] == ["SECRET_TOKEN"]

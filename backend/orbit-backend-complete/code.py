"""Small helper to export a readable project tree + source dump for review."""
from __future__ import annotations

import argparse
from pathlib import Path

EXCLUDED_DIRS = {".git", ".venv", "venv", "__pycache__", ".pytest_cache"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo", ".zip", ".png", ".jpg", ".jpeg", ".gif"}
EXCLUDED_FILES = {".env"}


def included_files(root: Path):
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if any(part in EXCLUDED_DIRS for part in rel.parts):
            continue
        if path.name in EXCLUDED_FILES or path.suffix.lower() in EXCLUDED_SUFFIXES:
            continue
        yield path, rel


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("project_dir", nargs="?", default=".")
    parser.add_argument("output_file", nargs="?", default="combined_backend_code.txt")
    args = parser.parse_args()
    root = Path(args.project_dir).resolve()
    out = Path(args.output_file).resolve()
    with out.open("w", encoding="utf-8") as handle:
        handle.write("PROJECT FILES:\n==============\n")
        files = list(included_files(root))
        for _, rel in files:
            handle.write(f"{rel.as_posix()}\n")
        handle.write("\nFILE CONTENTS:\n==============\n")
        for path, rel in files:
            handle.write(f"\n--- START OF FILE: {rel.as_posix()} ---\n\n")
            handle.write(path.read_text(encoding="utf-8", errors="ignore"))
            handle.write(f"\n\n--- END OF FILE: {rel.as_posix()} ---\n")
    print(out)


if __name__ == "__main__":
    main()

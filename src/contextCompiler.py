# Copyright (c) 2026 Daniel Bueno
# SPDX-License-Identifier: MIT
# See LICENSE for the full license text.

import argparse
import json
import uuid
from pathlib import Path
from typing import Any

import yaml


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_FILE = PROJECT_ROOT / "output" / "contextIndex.json"


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def ensure_problem_uuid(problem: dict[str, Any]) -> dict[str, Any]:
    """
    If problem_uuid is missing or blank, assign a generated UUID.
    """
    normalized_problem = dict(problem)

    if not normalized_problem.get("problem_uuid"):
        normalized_problem["problem_uuid"] = str(uuid.uuid4())

    return normalized_problem


def flatten_entry(
    entry: dict[str, Any],
    parent_uuid: str | None = None,
    depth: int = 0,
    path: list[str] | None = None,
) -> list[dict[str, Any]]:
    """
    Recursively flatten one YAML entry and its nested children.
    """
    if path is None:
        path = []

    title = entry.get("title")
    entry_uuid = entry.get("uuid")

    if not title:
        raise ValueError("Entry is missing required field: title")

    if not entry_uuid:
        raise ValueError(f"Entry '{title}' is missing required field: uuid")

    current_path = path + [title]

    flat_entry = {
        "uuid": entry_uuid,
        "title": title,
        "parent_uuid": parent_uuid,
        "depth": depth,
        "path": current_path,
        "text": entry.get("text", ""),
        "problems": [
            ensure_problem_uuid(problem)
            for problem in entry.get("problems", [])
        ],
    }

    flattened = [flat_entry]

    for child in entry.get("entries", []):
        flattened.extend(
            flatten_entry(
                child,
                parent_uuid=entry_uuid,
                depth=depth + 1,
                path=current_path,
            )
        )

    return flattened


def add_source_order(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Annotate each flattened entry with its original order in the YAML traversal.
    """
    for index, entry in enumerate(entries):
        entry["source_order"] = index

    return entries


def compile_context(input_file: Path, output_file: Path) -> None:
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with input_file.open("r", encoding="utf-8") as file_handle:
        root = yaml.safe_load(file_handle)

    flat_index = add_source_order(flatten_entry(root))

    with output_file.open("w", encoding="utf-8") as file_handle:
        json.dump(flat_index, file_handle, indent=2)

    print(f"Compiled {len(flat_index)} entries to {display_path(output_file)}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compile a context YAML file into a flattened JSON index."
    )
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Input YAML-like file to compile.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_FILE,
        help=f"Output JSON file. Default: {DEFAULT_OUTPUT_FILE}",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    compile_context(args.input, args.output)


if __name__ == "__main__":
    main()

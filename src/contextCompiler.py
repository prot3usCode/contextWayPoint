# Copyright (c) 2026 Daniel Bueno
# SPDX-License-Identifier: MIT
# See LICENSE for the full license text.

import argparse
import json
import uuid
from pathlib import Path
from typing import Any

import yaml
from contextValidator import (
    load_yaml,
    print_validation_errors,
    validate_context_tree,
)


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


def is_blank(value: Any) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def collect_existing_problem_uuids(entry: Any, seen_problem_uuids: set[str]) -> None:
    if not isinstance(entry, dict):
        return

    problems = entry.get("problems", [])
    if isinstance(problems, list):
        for problem in problems:
            if not isinstance(problem, dict):
                continue
            problem_uuid = problem.get("problem_uuid")
            if not is_blank(problem_uuid):
                seen_problem_uuids.add(problem_uuid)

    children = entry.get("entries", [])
    if isinstance(children, list):
        for child in children:
            collect_existing_problem_uuids(child, seen_problem_uuids)


def assign_missing_problem_uuids(entry: Any, seen_problem_uuids: set[str]) -> bool:
    if not isinstance(entry, dict):
        return False

    changed = False

    problems = entry.get("problems", [])
    if isinstance(problems, list):
        for problem in problems:
            if not isinstance(problem, dict):
                continue
            if not is_blank(problem.get("problem_uuid")):
                continue

            generated_uuid = str(uuid.uuid4())
            while generated_uuid in seen_problem_uuids:
                generated_uuid = str(uuid.uuid4())

            problem["problem_uuid"] = generated_uuid
            seen_problem_uuids.add(generated_uuid)
            changed = True

    children = entry.get("entries", [])
    if isinstance(children, list):
        for child in children:
            changed = assign_missing_problem_uuids(child, seen_problem_uuids) or changed

    return changed


def fill_missing_problem_uuids(root: dict[str, Any]) -> bool:
    seen_problem_uuids: set[str] = set()
    collect_existing_problem_uuids(root, seen_problem_uuids)
    return assign_missing_problem_uuids(root, seen_problem_uuids)


def default_filled_yaml_path(input_file: Path) -> Path:
    return input_file.with_name(f"{input_file.stem}.filled.yaml")


def write_yaml(output_file: Path, root: dict[str, Any]) -> None:
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open("w", encoding="utf-8") as file_handle:
        yaml.safe_dump(root, file_handle, sort_keys=False, allow_unicode=True)


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


def compile_context(
    input_file: Path,
    output_file: Path,
    fill_uuids: bool = False,
    output_yaml: Path | None = None,
    in_place: bool = False,
) -> None:
    output_file.parent.mkdir(parents=True, exist_ok=True)

    root = load_yaml(input_file)

    if fill_uuids:
        fill_missing_problem_uuids(root)

        filled_yaml_target = input_file if in_place else output_yaml
        if filled_yaml_target is None:
            filled_yaml_target = default_filled_yaml_path(input_file)

        write_yaml(filled_yaml_target, root)
        print(f"Wrote filled YAML to {display_path(filled_yaml_target)}")

    validation_errors = validate_context_tree(root)
    if validation_errors:
        print_validation_errors(validation_errors)
        raise SystemExit(1)

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
    parser.add_argument(
        "--fill-uuids",
        action="store_true",
        help="Fill blank problem_uuid values before compiling.",
    )
    parser.add_argument(
        "--output-yaml",
        type=Path,
        help="Write the filled YAML to a separate file.",
    )
    parser.add_argument(
        "--in-place",
        action="store_true",
        help="Write filled problem_uuid values back to the input file.",
    )
    args = parser.parse_args()

    if args.output_yaml and not args.fill_uuids:
        parser.error("--output-yaml requires --fill-uuids")

    if args.in_place and not args.fill_uuids:
        parser.error("--in-place requires --fill-uuids")

    if args.output_yaml and args.in_place:
        parser.error("Use either --output-yaml or --in-place, not both")

    return args


def main() -> None:
    args = parse_args()
    compile_context(
        args.input,
        args.output,
        fill_uuids=args.fill_uuids,
        output_yaml=args.output_yaml,
        in_place=args.in_place,
    )


if __name__ == "__main__":
    main()

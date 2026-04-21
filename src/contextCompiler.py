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
    discover_yaml_files,
    load_yaml,
    print_validation_errors,
    validate_context_documents,
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


def load_documents(
    input_file: Path | None = None,
    input_dir: Path | None = None,
) -> list[tuple[Path, dict[str, Any]]]:
    if input_file is not None:
        return [(input_file, load_yaml(input_file))]

    if input_dir is None:
        raise ValueError("Either input_file or input_dir is required")

    input_files = discover_yaml_files(input_dir)
    return [(context_file, load_yaml(context_file)) for context_file in input_files]


def flatten_entry(
    entry: dict[str, Any],
    source_file: str,
    source_root: str,
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
        "source_file": source_file,
        "source_root": source_root,
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
                source_file=source_file,
                source_root=source_root,
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


def flatten_documents(
    documents: list[tuple[Path, dict[str, Any]]],
) -> list[dict[str, Any]]:
    flattened: list[dict[str, Any]] = []

    for input_path, root in documents:
        source_file = display_path(input_path)
        source_root = root.get("title", "")
        flattened.extend(
            flatten_entry(
                root,
                source_file=source_file,
                source_root=source_root,
            )
        )

    return flattened


def compiled_entry_location(entry: dict[str, Any], index: int) -> str:
    source_file = entry.get("source_file") or "<missing source_file>"
    path = entry.get("path", [])

    if isinstance(path, list) and path:
        return f"compiled[{index}] {source_file} :: {' > '.join(str(part) for part in path)}"

    title = entry.get("title") or "<missing title>"
    return f"compiled[{index}] {source_file} :: {title}"


def validate_compiled_problem(
    problem: Any,
    errors: list[str],
    location: str,
    problem_index: int,
    seen_problem_uuids: set[str],
) -> None:
    prefix = f"{location} / problems[{problem_index}]"

    if not isinstance(problem, dict):
        errors.append(f"{prefix}: problem must be a mapping/object")
        return

    if is_blank(problem.get("problem_name")):
        errors.append(f"{prefix}: missing problem_name")

    problem_uuid = problem.get("problem_uuid")
    if is_blank(problem_uuid):
        errors.append(f"{prefix}: missing problem_uuid")
    elif problem_uuid in seen_problem_uuids:
        errors.append(f"{prefix}: duplicate problem_uuid '{problem_uuid}'")
    else:
        seen_problem_uuids.add(problem_uuid)

    step_number = problem.get("step_number")
    if step_number is None:
        errors.append(f"{prefix}: missing step_number")
    elif not isinstance(step_number, int):
        errors.append(f"{prefix}: step_number must be an integer")
    elif step_number < 1:
        errors.append(f"{prefix}: step_number must be greater than 0")

    weight = problem.get("weight")
    if weight is None:
        errors.append(f"{prefix}: missing weight")
    elif not isinstance(weight, (int, float)):
        errors.append(f"{prefix}: weight must be a number")
    elif weight < 0:
        errors.append(f"{prefix}: weight cannot be negative")

    keywords = problem.get("keywords", [])
    if keywords is None:
        return

    if not isinstance(keywords, list):
        errors.append(f"{prefix}: keywords must be a list")
        return

    for keyword_index, keyword in enumerate(keywords):
        if is_blank(keyword):
            errors.append(f"{prefix}: keywords[{keyword_index}] is blank")


def validate_compiled_index(entries: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    seen_uuids: set[str] = set()
    seen_problem_uuids: set[str] = set()

    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            errors.append(f"compiled[{index}]: entry must be a mapping/object")
            continue

        location = compiled_entry_location(entry, index)

        title = entry.get("title")
        if is_blank(title):
            errors.append(f"{location}: missing title")

        entry_uuid = entry.get("uuid")
        if is_blank(entry_uuid):
            errors.append(f"{location}: missing uuid")
        elif entry_uuid in seen_uuids:
            errors.append(f"{location}: duplicate uuid '{entry_uuid}'")
        else:
            seen_uuids.add(entry_uuid)

        source_file = entry.get("source_file")
        if is_blank(source_file):
            errors.append(f"{location}: missing source_file")

        source_root = entry.get("source_root")
        if is_blank(source_root):
            errors.append(f"{location}: missing source_root")

        text = entry.get("text")
        if is_blank(text):
            errors.append(f"{location}: blank text")

        path = entry.get("path", [])
        if not isinstance(path, list):
            errors.append(f"{location}: path must be a list")

        problems = entry.get("problems", [])
        if problems is None:
            problems = []

        if not isinstance(problems, list):
            errors.append(f"{location}: problems must be a list")
            continue

        for problem_index, problem in enumerate(problems):
            validate_compiled_problem(
                problem,
                errors,
                location,
                problem_index,
                seen_problem_uuids,
            )

    return errors


def compile_context(
    input_file: Path | None,
    input_dir: Path | None,
    output_file: Path,
    fill_uuids: bool = False,
    output_yaml: Path | None = None,
    in_place: bool = False,
) -> None:
    output_file.parent.mkdir(parents=True, exist_ok=True)

    documents = load_documents(input_file=input_file, input_dir=input_dir)

    if fill_uuids:
        if len(documents) != 1:
            raise ValueError("--fill-uuids only supports a single input file")

        input_file, root = documents[0]
        fill_missing_problem_uuids(root)

        filled_yaml_target = input_file if in_place else output_yaml
        if filled_yaml_target is None:
            filled_yaml_target = default_filled_yaml_path(input_file)

        write_yaml(filled_yaml_target, root)
        print(f"Wrote filled YAML to {display_path(filled_yaml_target)}")

    validation_errors = validate_context_documents(documents)
    if validation_errors:
        print_validation_errors(validation_errors)
        raise SystemExit(1)

    flat_index = add_source_order(flatten_documents(documents))
    compiled_index_errors = validate_compiled_index(flat_index)
    if compiled_index_errors:
        print_validation_errors(compiled_index_errors)
        raise SystemExit(1)

    with output_file.open("w", encoding="utf-8") as file_handle:
        json.dump(flat_index, file_handle, indent=2)

    if input_file is not None:
        input_label = display_path(input_file)
    else:
        input_label = f"{len(documents)} files from {display_path(input_dir)}"

    print(
        f"Compiled {len(flat_index)} entries from {input_label} to {display_path(output_file)}"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compile a context YAML file into a flattened JSON index."
    )
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--input",
        type=Path,
        help="Input YAML-like file to compile.",
    )
    input_group.add_argument(
        "--input-dir",
        type=Path,
        help="Directory of YAML-like files to compile into one global index.",
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

    if args.input_dir and args.fill_uuids:
        parser.error("--fill-uuids currently supports only --input, not --input-dir")

    return args


def main() -> None:
    args = parse_args()
    try:
        compile_context(
            args.input,
            args.input_dir,
            args.output,
            fill_uuids=args.fill_uuids,
            output_yaml=args.output_yaml,
            in_place=args.in_place,
        )
    except ValueError as error:
        print("Compilation failed:")
        print(f"- {error}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()

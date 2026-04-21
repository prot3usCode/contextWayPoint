# Copyright (c) 2026 Daniel Bueno
# SPDX-License-Identifier: MIT
# See LICENSE for the full license text.

import argparse
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import yaml

from contextwaypoint.common import (
    ContextValidationError,
    YAML_SUFFIXES,
    display_path,
)


ValidationErrorList = list[str]


def discover_yaml_files(input_dir: Path) -> list[Path]:
    if not input_dir.exists():
        raise ValueError(f"{input_dir} does not exist")

    if not input_dir.is_dir():
        raise ValueError(f"{input_dir} is not a directory")

    yaml_files = sorted(
        [
            path
            for path in input_dir.rglob("*")
            if path.is_file() and path.suffix.lower() in YAML_SUFFIXES
        ]
    )

    if not yaml_files:
        raise ValueError(f"{input_dir} does not contain any YAML files")

    return yaml_files


def format_location(path: list[str]) -> str:
    if not path:
        return "root"
    return " > ".join(path)


def is_blank(value: Any) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def qualify_location(document_label: str | None, location: str) -> str:
    if is_blank(document_label):
        return location
    return f"{document_label} :: {location}"


def validate_problem(
    problem: dict[str, Any],
    errors: ValidationErrorList,
    location: str,
    problem_index: int,
    seen_problem_uuids: set[str],
    document_label: str | None = None,
) -> None:
    prefix = qualify_location(document_label, f"{location} / problems[{problem_index}]")

    if not isinstance(problem, dict):
        errors.append(f"{prefix}: problem must be a mapping/object")
        return

    if is_blank(problem.get("problem_name")):
        errors.append(f"{prefix}: missing problem_name")

    problem_uuid = problem.get("problem_uuid")
    if not is_blank(problem_uuid):
        if problem_uuid in seen_problem_uuids:
            errors.append(f"{prefix}: duplicate problem_uuid '{problem_uuid}'")
        else:
            seen_problem_uuids.add(problem_uuid)

    step_number = problem.get("step_number")
    if step_number is None:
        errors.append(f"{prefix}: missing step_number")
    elif not isinstance(step_number, int):
        errors.append(f"{prefix}: step_number must be an integer")

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


def validate_entry(
    entry: dict[str, Any],
    errors: ValidationErrorList,
    seen_uuids: set[str],
    seen_problem_uuids: set[str],
    path: list[str] | None = None,
    document_label: str | None = None,
) -> None:
    if path is None:
        path = []

    if not isinstance(entry, dict):
        errors.append(
            f"{qualify_location(document_label, format_location(path))}: entry must be a mapping/object"
        )
        return

    title = entry.get("title")
    entry_uuid = entry.get("uuid")

    display_title = title if not is_blank(title) else "<missing title>"
    current_path = path + [str(display_title)]
    location = format_location(current_path)
    qualified_location = qualify_location(document_label, location)

    if is_blank(title):
        errors.append(f"{qualified_location}: missing title")

    if is_blank(entry_uuid):
        errors.append(f"{qualified_location}: missing uuid")
    elif entry_uuid in seen_uuids:
        errors.append(f"{qualified_location}: duplicate uuid '{entry_uuid}'")
    else:
        seen_uuids.add(entry_uuid)

    text = entry.get("text")
    if is_blank(text):
        errors.append(f"{qualified_location}: blank text")

    problems = entry.get("problems", [])
    if problems is None:
        problems = []

    if not isinstance(problems, list):
        errors.append(f"{qualified_location}: problems must be a list")
    else:
        for problem_index, problem in enumerate(problems):
            validate_problem(
                problem,
                errors,
                location,
                problem_index,
                seen_problem_uuids,
                document_label=document_label,
            )

    children = entry.get("entries", [])
    if children is None:
        children = []

    if not isinstance(children, list):
        errors.append(f"{qualified_location}: entries must be a list")
        return

    for child in children:
        validate_entry(
            child,
            errors,
            seen_uuids,
            seen_problem_uuids,
            current_path,
            document_label=document_label,
        )


def validate_context_tree(
    root: dict[str, Any],
    document_label: str | None = None,
    seen_uuids: set[str] | None = None,
    seen_problem_uuids: set[str] | None = None,
) -> ValidationErrorList:
    errors: ValidationErrorList = []

    if seen_uuids is None:
        seen_uuids = set()

    if seen_problem_uuids is None:
        seen_problem_uuids = set()

    validate_entry(
        root,
        errors,
        seen_uuids,
        seen_problem_uuids,
        document_label=document_label,
    )

    return errors


def validate_context_documents(
    documents: list[tuple[Path, dict[str, Any]]],
) -> ValidationErrorList:
    errors: ValidationErrorList = []
    seen_uuids: set[str] = set()
    seen_problem_uuids: set[str] = set()

    for input_file, root in documents:
        document_label = display_path(input_file)
        errors.extend(
            validate_context_tree(
                root,
                document_label=document_label,
                seen_uuids=seen_uuids,
                seen_problem_uuids=seen_problem_uuids,
            )
        )

    return errors


def load_yaml(input_file: Path) -> dict[str, Any]:
    with input_file.open("r", encoding="utf-8") as file_handle:
        loaded = yaml.safe_load(file_handle)

    if loaded is None:
        raise ValueError(f"{input_file} is empty")

    if not isinstance(loaded, dict):
        raise ValueError(f"{input_file} must contain a YAML mapping/object at the root")

    return loaded


def validate_file(input_file: Path) -> ValidationErrorList:
    root = load_yaml(input_file)
    return validate_context_tree(root, document_label=display_path(input_file))


def validate_input_dir(input_dir: Path) -> tuple[list[Path], ValidationErrorList]:
    input_files = discover_yaml_files(input_dir)
    documents = [(input_file, load_yaml(input_file)) for input_file in input_files]
    return input_files, validate_context_documents(documents)


def validate_source(source: Path) -> str:
    if not source.exists():
        raise ValueError(f"{source} does not exist")

    if source.is_dir():
        input_files, errors = validate_input_dir(source)
        if errors:
            raise ContextValidationError(errors)
        return f"{len(input_files)} files from {display_path(source)}"

    errors = validate_file(source)
    if errors:
        raise ContextValidationError(errors)
    return display_path(source)


def print_validation_errors(errors: ValidationErrorList) -> None:
    print("Validation failed:")
    for error in errors:
        print(f"- {error}")


def build_legacy_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate a contextWayPoint YAML file."
    )
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--input",
        type=Path,
        help="Input YAML-like context file to validate.",
    )
    input_group.add_argument(
        "--input-dir",
        type=Path,
        help="Directory of YAML-like context files to validate together.",
    )
    return parser


def legacy_main(argv: Sequence[str] | None = None) -> None:
    args = build_legacy_parser().parse_args(argv)

    try:
        if args.input is not None:
            label = validate_source(args.input)
        else:
            label = validate_source(args.input_dir)
    except ContextValidationError as error:
        print_validation_errors(error.errors)
        raise SystemExit(1)
    except ValueError as error:
        print("Validation failed:")
        print(f"- {error}")
        raise SystemExit(1)

    print(f"Validation passed: {label}")

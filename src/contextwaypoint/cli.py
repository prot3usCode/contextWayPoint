# Copyright (c) 2026 Daniel Bueno
# SPDX-License-Identifier: MIT
# See LICENSE for the full license text.

import argparse
from pathlib import Path

from contextwaypoint.common import (
    ContextValidationError,
    DEFAULT_DEMO_OUTPUT_DIR,
    DEFAULT_GENERATED_YAML_DIR,
    DEFAULT_INDEX_FILE,
    DEFAULT_PACKET_DIR,
    display_path,
)
from contextwaypoint.compiler import compile_source, fill_uuid_source
from contextwaypoint.demo import available_demo_names, demo_summary, run_demo
from contextwaypoint.project_export import (
    build_project_outputs,
    render_project_yaml_from_file,
    slugify,
)
from contextwaypoint.runtime_execution import preview_macro_execution_from_file
from contextwaypoint.router import route_and_write
from contextwaypoint.validation import print_validation_errors, validate_source


def print_error(message: str) -> None:
    print(message)


def command_validate(args: argparse.Namespace) -> int:
    label = validate_source(args.source)
    print(f"Validation passed: {label}")
    return 0


def command_compile(args: argparse.Namespace) -> int:
    message = compile_source(args.source, args.out)
    print(message)
    return 0


def command_fill_uuids(args: argparse.Namespace) -> int:
    written_files = fill_uuid_source(
        args.source,
        output_path=args.out,
        in_place=args.in_place,
    )

    for path in written_files:
        print(f"Wrote filled YAML to {display_path(path)}")

    return 0


def command_route(args: argparse.Namespace) -> int:
    rendered_output, output_path, audit_path = route_and_write(
        args.problem_name,
        args.mode,
        args.format,
        route_only=False,
        index_file=args.index_file,
        output_dir=args.output_dir,
        keywords=args.keywords,
    )
    print(rendered_output)
    print(f"\nWrote context packet to: {display_path(output_path)}")
    if audit_path is not None:
        print(f"Wrote audit packet to: {display_path(audit_path)}")
    return 0


def command_route_map(args: argparse.Namespace) -> int:
    rendered_output, output_path, _ = route_and_write(
        args.problem_name,
        args.mode,
        args.format,
        route_only=True,
        index_file=args.index_file,
        output_dir=args.output_dir,
        keywords=args.keywords,
    )
    print(rendered_output)
    print(f"\nWrote route map to: {display_path(output_path)}")
    return 0


def command_demo(args: argparse.Namespace) -> int:
    report, output_path = run_demo(
        args.name,
        output_dir=args.output_dir,
    )
    print(report)
    print(f"\n{demo_summary(output_path)}")
    return 0


def command_project_render(args: argparse.Namespace) -> int:
    rendered_documents = render_project_yaml_from_file(args.project_file)

    if args.problem is not None:
        file_name = f"{slugify(args.problem)}.generated.yaml"
        matched_name = next(
            (
                candidate_name
                for candidate_name in rendered_documents
                if candidate_name == file_name
            ),
            None,
        )
        if matched_name is None:
            raise ValueError(f"Problem '{args.problem}' was not found in the project file")
        print(rendered_documents[matched_name].rstrip())
        return 0

    for index, (file_name, contents) in enumerate(rendered_documents.items(), start=1):
        if index > 1:
            print("\n---\n")
        print(f"# {file_name}\n")
        print(contents.rstrip())

    return 0


def command_project_build(args: argparse.Namespace) -> int:
    message = build_project_outputs(
        args.project_file,
        yaml_output_dir=args.yaml_out,
        json_output_file=args.json_out,
    )
    print(message)
    return 0


def command_macro_preview(args: argparse.Namespace) -> int:
    preview = preview_macro_execution_from_file(
        workspace_file=args.workspace_file,
        macro_id=args.macro_id,
        prompt_text=args.prompt or "",
    )
    print(preview)
    return 0


def add_route_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "problem_name",
        help='Problem name, for example: "Order Fulfillment Investigation"',
    )
    parser.add_argument(
        "--mode",
        choices=("step", "weight", "yaml", "keyword"),
        default="step",
        help="Sort by step, weight, raw authored order, or keyword overlap.",
    )
    parser.add_argument(
        "--keywords",
        nargs="+",
        help="Keywords to score during keyword mode.",
    )
    parser.add_argument(
        "--format",
        choices=("txt", "md", "json"),
        default="md",
        help="Render the routed output as plain text, Markdown, or JSON.",
    )
    parser.add_argument(
        "--index-file",
        type=Path,
        default=DEFAULT_INDEX_FILE,
        help=f"Compiled context index to read. Default: {DEFAULT_INDEX_FILE}",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_PACKET_DIR,
        help=f"Directory for generated packets. Default: {DEFAULT_PACKET_DIR}",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="contextwaypoint",
        description="Compile and route authored context for LLMs and agents.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate one YAML file or a directory of YAML files.",
    )
    validate_parser.add_argument(
        "source",
        type=Path,
        help="YAML file or directory of YAML files to validate.",
    )
    validate_parser.set_defaults(func=command_validate)

    compile_parser = subparsers.add_parser(
        "compile",
        help="Compile one YAML file or a directory into a flattened JSON index.",
    )
    compile_parser.add_argument(
        "source",
        type=Path,
        help="YAML file or directory of YAML files to compile.",
    )
    compile_parser.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_INDEX_FILE,
        help=f"Output JSON file. Default: {DEFAULT_INDEX_FILE}",
    )
    compile_parser.set_defaults(func=command_compile)

    route_parser = subparsers.add_parser(
        "route",
        help="Route a context packet for one problem.",
    )
    add_route_arguments(route_parser)
    route_parser.set_defaults(func=command_route)

    route_map_parser = subparsers.add_parser(
        "route-map",
        help="Render only the route map for one problem.",
    )
    add_route_arguments(route_map_parser)
    route_map_parser.set_defaults(func=command_route_map)

    fill_parser = subparsers.add_parser(
        "fill-uuids",
        help="Fill blank problem_uuid values in one file or a directory tree.",
    )
    fill_parser.add_argument(
        "source",
        type=Path,
        help="YAML file or directory of YAML files to fill.",
    )
    fill_parser.add_argument(
        "--out",
        type=Path,
        help="Output file or directory for filled YAML content.",
    )
    fill_parser.add_argument(
        "--in-place",
        action="store_true",
        help="Write filled UUIDs back into the source file or directory.",
    )
    fill_parser.set_defaults(func=command_fill_uuids)

    demo_parser = subparsers.add_parser(
        "demo",
        help="Run a one-command demo that compares unordered retrieval to an authored route.",
    )
    demo_parser.add_argument(
        "name",
        choices=available_demo_names(),
        help="Demo name to run.",
    )
    demo_parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_DEMO_OUTPUT_DIR,
        help=f"Directory for generated demo output. Default: {DEFAULT_DEMO_OUTPUT_DIR}",
    )
    demo_parser.set_defaults(func=command_demo)

    project_render_parser = subparsers.add_parser(
        "project-render",
        help="Render generated YAML from an authoring project JSON file.",
    )
    project_render_parser.add_argument(
        "project_file",
        type=Path,
        help="Project JSON file to render into generated YAML.",
    )
    project_render_parser.add_argument(
        "--problem",
        help="Optional single problem to render.",
    )
    project_render_parser.set_defaults(func=command_project_render)

    project_build_parser = subparsers.add_parser(
        "project-build",
        help="Export project JSON to generated YAML and compile it to JSON.",
    )
    project_build_parser.add_argument(
        "project_file",
        type=Path,
        help="Project JSON file to export.",
    )
    project_build_parser.add_argument(
        "--yaml-out",
        type=Path,
        default=DEFAULT_GENERATED_YAML_DIR,
        help=f"Directory for generated YAML. Default: {DEFAULT_GENERATED_YAML_DIR}",
    )
    project_build_parser.add_argument(
        "--json-out",
        type=Path,
        default=DEFAULT_INDEX_FILE,
        help=f"Compiled JSON output file. Default: {DEFAULT_INDEX_FILE}",
    )
    project_build_parser.set_defaults(func=command_project_build)

    macro_preview_parser = subparsers.add_parser(
        "macro-preview",
        help="Preview one macro by resolving linked problems through the routing engine.",
    )
    macro_preview_parser.add_argument(
        "workspace_file",
        type=Path,
        help="Macro workspace JSON file.",
    )
    macro_preview_parser.add_argument(
        "--macro",
        dest="macro_id",
        required=True,
        help="Macro ID to preview.",
    )
    macro_preview_parser.add_argument(
        "--prompt",
        default="",
        help="Prompt text used for branch evaluation during the preview.",
    )
    macro_preview_parser.set_defaults(func=command_macro_preview)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if getattr(args, "mode", None) == "keyword" and not getattr(args, "keywords", None):
        parser.error("--keywords is required when --mode keyword is used")

    if getattr(args, "mode", None) != "keyword" and getattr(args, "keywords", None):
        parser.error("--keywords can only be used with --mode keyword")

    if getattr(args, "in_place", False) and getattr(args, "out", None):
        parser.error("Use either --out or --in-place, not both")

    try:
        return int(args.func(args))
    except ContextValidationError as error:
        print_validation_errors(error.errors)
        return 1
    except ValueError as error:
        print_error(f"Error: {error}")
        return 1

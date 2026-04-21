# Copyright (c) 2026 Daniel Bueno
# SPDX-License-Identifier: MIT
# See LICENSE for the full license text.

import argparse
import json
import re
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from contextwaypoint.common import (
    DEFAULT_INDEX_FILE,
    DEFAULT_PACKET_DIR,
    display_path,
)


def load_index(index_file: Path = DEFAULT_INDEX_FILE) -> list[dict[str, Any]]:
    with index_file.open("r", encoding="utf-8") as file_handle:
        return json.load(file_handle)


def find_matching_problem(
    entry: dict[str, Any], problem_name: str
) -> dict[str, Any] | None:
    for problem in entry.get("problems", []):
        if problem.get("problem_name", "").lower() == problem_name.lower():
            return problem
    return None


def normalize_tokens(values: list[str]) -> set[str]:
    tokens: set[str] = set()

    for value in values:
        for token in re.split(r"[^A-Za-z0-9]+", value.lower()):
            if token:
                tokens.add(token)

    return tokens


def problem_keywords(problem: dict[str, Any]) -> list[str]:
    keywords = problem.get("keywords", [])
    if not isinstance(keywords, list):
        return []
    return [str(keyword) for keyword in keywords if keyword is not None]


def score_keyword_overlap(item: dict[str, Any], query_keywords: list[str]) -> int:
    query_tokens = normalize_tokens(query_keywords)
    if not query_tokens:
        return 0

    searchable_values = [
        item.get("title", ""),
        item.get("text", ""),
        item.get("source_root", ""),
    ]
    searchable_values.extend(str(part) for part in item.get("path", []))
    searchable_values.extend(problem_keywords(item["matched_problem"]))

    searchable_tokens = normalize_tokens(searchable_values)
    return len(query_tokens & searchable_tokens)


def query_by_problem(
    problem_name: str,
    index_file: Path = DEFAULT_INDEX_FILE,
) -> list[dict[str, Any]]:
    index = load_index(index_file)
    results: list[dict[str, Any]] = []

    for fallback_order, entry in enumerate(index):
        matched_problem = find_matching_problem(entry, problem_name)
        if not matched_problem:
            continue

        path = entry.get("path", [])
        source_root = entry.get("source_root")
        if not source_root and isinstance(path, list) and path:
            source_root = path[0]

        results.append(
            {
                "uuid": entry["uuid"],
                "title": entry["title"],
                "parent_uuid": entry.get("parent_uuid"),
                "depth": entry.get("depth", 0),
                "path": path,
                "text": entry.get("text", "").strip(),
                "source_order": entry.get("source_order", fallback_order),
                "source_file": entry.get("source_file", "<unknown source>"),
                "source_root": source_root or entry.get("title", ""),
                "matched_problem": matched_problem,
            }
        )

    return results


def annotate_keyword_scores(
    results: list[dict[str, Any]],
    query_keywords: list[str] | None,
) -> list[dict[str, Any]]:
    keywords = query_keywords or []
    annotated_results: list[dict[str, Any]] = []

    for item in results:
        annotated_item = dict(item)
        annotated_item["keyword_score"] = score_keyword_overlap(item, keywords)
        annotated_results.append(annotated_item)

    return annotated_results


def step_sort_value(item: dict[str, Any]) -> int:
    step_number = item["matched_problem"].get("step_number")
    if isinstance(step_number, int):
        return step_number
    return 999999


def weight_sort_value(item: dict[str, Any]) -> float:
    weight = item["matched_problem"].get("weight")
    if isinstance(weight, (int, float)):
        return float(weight)
    return 0


def sort_results(results: list[dict[str, Any]], mode: str) -> list[dict[str, Any]]:
    if mode == "step":
        return sorted(
            results,
            key=lambda item: (
                step_sort_value(item),
                -weight_sort_value(item),
                item.get("depth", 0),
                item.get("source_order", 999999),
            ),
        )

    if mode == "weight":
        return sorted(
            results,
            key=lambda item: (
                -weight_sort_value(item),
                step_sort_value(item),
                item.get("depth", 0),
                item.get("source_order", 999999),
            ),
        )

    if mode == "yaml":
        return sorted(results, key=lambda item: item.get("source_order", 999999))

    if mode == "keyword":
        return sorted(
            results,
            key=lambda item: (
                -item.get("keyword_score", 0),
                step_sort_value(item),
                -weight_sort_value(item),
                item.get("depth", 0),
                item.get("source_order", 999999),
            ),
        )

    raise ValueError(f"Unsupported mode: {mode}")


def route_problem(
    problem_name: str,
    mode: str = "step",
    index_file: Path = DEFAULT_INDEX_FILE,
    keywords: list[str] | None = None,
) -> list[dict[str, Any]]:
    results = query_by_problem(problem_name, index_file=index_file)

    if mode == "keyword":
        results = annotate_keyword_scores(results, keywords)

    return sort_results(results, mode)


def to_camel_case(text: str) -> str:
    parts = re.split(r"[^A-Za-z0-9]+", text.strip())
    words = [part for part in parts if part]

    if not words:
        return "contextPacket"

    return words[0].lower() + "".join(word[:1].upper() + word[1:] for word in words[1:])


def build_intro_lines(
    problem_name: str,
    mode: str,
    route_only: bool,
    query_keywords: list[str] | None = None,
) -> list[str]:
    lines = [
        f"{'Route Map' if route_only else 'Context Packet'}: {problem_name}",
        f"Mode: {mode}",
    ]

    if mode == "keyword" and query_keywords:
        lines.append(f"Keywords: {', '.join(query_keywords)}")

    return lines + [""]


def entry_path_text(item: dict[str, Any]) -> str:
    return " > ".join(str(part) for part in item.get("path", []))


def text_route_label(item: dict[str, Any], route_position: int) -> str:
    return f"{route_position}. {item['title']}"


def step_heading(item: dict[str, Any]) -> str:
    step_number = item["matched_problem"].get("step_number")
    if step_number is None:
        return item["title"]
    return f"Step {step_number} - {item['title']}"


def entry_keywords_text(item: dict[str, Any]) -> str:
    keywords = problem_keywords(item["matched_problem"])
    return ", ".join(keywords)


def append_audit_metadata_lines(
    lines: list[str],
    item: dict[str, Any],
    mode: str,
    route_position: int,
) -> None:
    lines.append(f"Route Position: {route_position}")
    lines.append(f"Entry UUID: {item['uuid']}")
    lines.append(f"Source: {item['source_file']}")
    lines.append(f"Path: {entry_path_text(item)}")
    lines.append(f"Weight: {item['matched_problem'].get('weight')}")
    lines.append(f"Problem UUID: {item['matched_problem'].get('problem_uuid')}")

    keywords_text = entry_keywords_text(item)
    if keywords_text:
        lines.append(f"Keywords: {keywords_text}")

    if mode == "keyword":
        lines.append(f"Keyword Score: {item.get('keyword_score', 0)}")


def append_route_metadata_lines(
    lines: list[str],
    item: dict[str, Any],
    route_position: int,
    mode: str,
) -> None:
    lines.append(text_route_label(item, route_position))

    step_number = item["matched_problem"].get("step_number")
    if step_number is not None:
        lines.append(f"   Step: {step_number}")

    lines.append(f"   Source: {item['source_file']}")
    lines.append(f"   Path: {entry_path_text(item)}")

    if mode == "keyword":
        lines.append(f"   Keyword Score: {item.get('keyword_score', 0)}")


def format_results_as_text(
    results: list[dict[str, Any]],
    problem_name: str,
    mode: str,
    route_only: bool = False,
    query_keywords: list[str] | None = None,
) -> str:
    if route_only:
        lines = build_intro_lines(problem_name, mode, route_only, query_keywords)

        if not results:
            lines.append("No route found.")
            return "\n".join(lines).strip()

        for route_position, item in enumerate(results, start=1):
            append_route_metadata_lines(lines, item, route_position, mode)
            lines.append("")

        return "\n".join(lines).strip()

    if not results:
        return f"No context found for problem: {problem_name}"

    text_blocks = [item.get("text", "") for item in results if item.get("text", "")]
    if not text_blocks:
        return f"No context found for problem: {problem_name}"

    return "\n\n".join(text_blocks).strip()


def format_results_as_audit_text(
    results: list[dict[str, Any]],
    problem_name: str,
    mode: str,
    query_keywords: list[str] | None = None,
) -> str:
    lines = build_intro_lines(problem_name, mode, route_only=False, query_keywords=query_keywords)

    if not results:
        lines.append(f"No context found for problem: {problem_name}")
        return "\n".join(lines).strip()

    for route_position, item in enumerate(results, start=1):
        lines.append(step_heading(item))
        append_audit_metadata_lines(lines, item, mode, route_position)
        lines.extend(["", item.get("text", ""), ""])

    return "\n".join(lines).strip()


def format_results_as_markdown(
    results: list[dict[str, Any]],
    problem_name: str,
    mode: str,
    route_only: bool = False,
    query_keywords: list[str] | None = None,
) -> str:
    lines = [
        f"# {'Route Map' if route_only else 'Context Packet'}: {problem_name}",
        "",
        f"Mode: `{mode}`",
        "",
    ]

    if mode == "keyword" and query_keywords:
        lines.extend([f"Keywords: `{', '.join(query_keywords)}`", ""])

    if not results:
        lines.append(f"No {'route' if route_only else 'context'} found.")
        return "\n".join(lines)

    for route_position, item in enumerate(results, start=1):
        if route_only:
            lines.extend(
                [
                    f"{route_position}. **{item['title']}**",
                    "",
                ]
            )

            step_number = item["matched_problem"].get("step_number")
            if step_number is not None:
                lines.append(f"Step: `{step_number}`  ")

            lines.extend(
                [
                    f"Source: `{item['source_file']}`  ",
                    f"Path: `{entry_path_text(item)}`",
                ]
            )

            if mode == "keyword":
                lines.append(f"Keyword Score: `{item.get('keyword_score', 0)}`")

            lines.append("")
            continue

        lines.extend(
            [
                f"## {step_heading(item)}",
                "",
                f"Source: `{item['source_file']}`  ",
                f"Path: `{entry_path_text(item)}`  ",
                f"Weight: `{item['matched_problem'].get('weight')}`",
            ]
        )

        if mode == "keyword":
            lines.append(f"Keyword Score: `{item.get('keyword_score', 0)}`")

        lines.extend(["", item.get("text", ""), ""])

    return "\n".join(lines).strip()


def build_json_payload(
    results: list[dict[str, Any]],
    problem_name: str,
    mode: str,
    route_only: bool = False,
    query_keywords: list[str] | None = None,
) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []

    for route_position, item in enumerate(results, start=1):
        problem = item["matched_problem"]
        entry_payload = {
            "route_position": route_position,
            "title": item["title"],
            "uuid": item["uuid"],
            "parent_uuid": item.get("parent_uuid"),
            "depth": item.get("depth", 0),
            "path": item.get("path", []),
            "source_file": item.get("source_file"),
            "source_root": item.get("source_root"),
            "step_number": problem.get("step_number"),
            "weight": problem.get("weight"),
            "problem_uuid": problem.get("problem_uuid"),
            "keywords": problem_keywords(problem),
        }

        if mode == "keyword":
            entry_payload["keyword_score"] = item.get("keyword_score", 0)

        if not route_only:
            entry_payload["text"] = item.get("text", "")

        entries.append(entry_payload)

    return {
        "problem_name": problem_name,
        "mode": mode,
        "route_only": route_only,
        "keywords_used": query_keywords or [],
        "entry_count": len(entries),
        "entries": entries,
    }


def format_results_as_json(
    results: list[dict[str, Any]],
    problem_name: str,
    mode: str,
    route_only: bool = False,
    query_keywords: list[str] | None = None,
) -> str:
    return json.dumps(
        build_json_payload(
            results,
            problem_name,
            mode,
            route_only=route_only,
            query_keywords=query_keywords,
        ),
        indent=2,
    )


def render_results(
    results: list[dict[str, Any]],
    problem_name: str,
    mode: str,
    output_format: str,
    route_only: bool = False,
    query_keywords: list[str] | None = None,
) -> str:
    if output_format == "txt":
        return format_results_as_text(
            results,
            problem_name,
            mode,
            route_only=route_only,
            query_keywords=query_keywords,
        )

    if output_format == "md":
        return format_results_as_markdown(
            results,
            problem_name,
            mode,
            route_only=route_only,
            query_keywords=query_keywords,
        )

    if output_format == "json":
        return format_results_as_json(
            results,
            problem_name,
            mode,
            route_only=route_only,
            query_keywords=query_keywords,
        )

    raise ValueError(f"Unsupported format: {output_format}")


def write_results_to_file(
    results: list[dict[str, Any]],
    problem_name: str,
    mode: str,
    output_format: str,
    route_only: bool = False,
    query_keywords: list[str] | None = None,
    output_dir: Path = DEFAULT_PACKET_DIR,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)

    extension_by_format = {
        "txt": "txt",
        "md": "md",
        "json": "json",
    }
    extension = extension_by_format[output_format]
    suffix = "Route" if route_only else ""
    file_name = (
        f"{to_camel_case(problem_name)}{mode[:1].upper() + mode[1:]}{suffix}.{extension}"
    )
    output_path = output_dir / file_name

    output_text = render_results(
        results,
        problem_name,
        mode,
        output_format,
        route_only=route_only,
        query_keywords=query_keywords,
    )

    with output_path.open("w", encoding="utf-8") as file_handle:
        file_handle.write(output_text)

    return output_path


def write_audit_results_to_file(
    results: list[dict[str, Any]],
    problem_name: str,
    mode: str,
    query_keywords: list[str] | None = None,
    output_dir: Path = DEFAULT_PACKET_DIR,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)

    file_name = f"{to_camel_case(problem_name)}{mode[:1].upper() + mode[1:]}Audit.txt"
    output_path = output_dir / file_name
    output_text = format_results_as_audit_text(
        results,
        problem_name,
        mode,
        query_keywords=query_keywords,
    )

    with output_path.open("w", encoding="utf-8") as file_handle:
        file_handle.write(output_text)

    return output_path


def route_and_write(
    problem_name: str,
    mode: str,
    output_format: str,
    route_only: bool = False,
    index_file: Path = DEFAULT_INDEX_FILE,
    output_dir: Path = DEFAULT_PACKET_DIR,
    keywords: list[str] | None = None,
) -> tuple[str, Path, Path | None]:
    results = route_problem(
        problem_name,
        mode=mode,
        index_file=index_file,
        keywords=keywords,
    )
    rendered_output = render_results(
        results,
        problem_name,
        mode,
        output_format,
        route_only=route_only,
        query_keywords=keywords,
    )
    output_path = write_results_to_file(
        results,
        problem_name,
        mode,
        output_format,
        route_only=route_only,
        query_keywords=keywords,
        output_dir=output_dir,
    )

    audit_path = None
    if output_format == "txt" and not route_only:
        audit_path = write_audit_results_to_file(
            results,
            problem_name,
            mode,
            query_keywords=keywords,
            output_dir=output_dir,
        )

    return rendered_output, output_path, audit_path


def build_legacy_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Query the flattened context index and write a context packet."
    )
    parser.add_argument(
        "problem_name",
        help='Problem name, for example: "Order Flow Issue Triage"',
    )
    parser.add_argument(
        "--mode",
        choices=("step", "weight", "yaml", "keyword"),
        default="step",
        help="Sort by step, weight, raw YAML traversal order, or keyword overlap.",
    )
    parser.add_argument(
        "--keywords",
        nargs="+",
        help="Keywords to score during keyword mode.",
    )
    parser.add_argument(
        "--format",
        choices=("txt", "md", "json"),
        default="txt",
        help="Render the routed packet as plain text, Markdown, or JSON.",
    )
    parser.add_argument(
        "--route-only",
        action="store_true",
        help="Render only the route map without the full context text.",
    )
    parser.add_argument(
        "--index-file",
        type=Path,
        default=DEFAULT_INDEX_FILE,
        help=f"Path to the compiled context index. Default: {DEFAULT_INDEX_FILE}",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_PACKET_DIR,
        help=f"Directory for generated context packets. Default: {DEFAULT_PACKET_DIR}",
    )
    return parser


def legacy_main(argv: Sequence[str] | None = None) -> None:
    parser = build_legacy_parser()
    args = parser.parse_args(argv)

    if args.mode == "keyword" and not args.keywords:
        parser.error("--keywords is required when --mode keyword is used")

    if args.mode != "keyword" and args.keywords:
        parser.error("--keywords can only be used with --mode keyword")

    rendered_output, output_path, audit_path = route_and_write(
        args.problem_name,
        args.mode,
        args.format,
        route_only=args.route_only,
        index_file=args.index_file,
        output_dir=args.output_dir,
        keywords=args.keywords,
    )

    print(rendered_output)
    output_label = "route map" if args.route_only else "context packet"
    print(f"\nWrote {output_label} to: {display_path(output_path)}")
    if audit_path is not None:
        print(f"Wrote audit packet to: {display_path(audit_path)}")

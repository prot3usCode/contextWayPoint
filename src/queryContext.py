# Copyright (c) 2026 Daniel Bueno
# SPDX-License-Identifier: MIT
# See LICENSE for the full license text.

import argparse
import json
import re
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent
INDEX_FILE = PROJECT_ROOT / "output" / "contextIndex.json"
OUTPUT_DIR = PROJECT_ROOT / "output" / "contextPackets"


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def load_index(index_file: Path = INDEX_FILE) -> list[dict[str, Any]]:
    with index_file.open("r", encoding="utf-8") as file_handle:
        return json.load(file_handle)


def find_matching_problem(
    entry: dict[str, Any], problem_name: str
) -> dict[str, Any] | None:
    for problem in entry.get("problems", []):
        if problem.get("problem_name", "").lower() == problem_name.lower():
            return problem
    return None


def query_by_problem(
    problem_name: str,
    index_file: Path = INDEX_FILE,
) -> list[dict[str, Any]]:
    index = load_index(index_file)
    results: list[dict[str, Any]] = []

    for fallback_order, entry in enumerate(index):
        matched_problem = find_matching_problem(entry, problem_name)

        if matched_problem:
            results.append(
                {
                    "uuid": entry["uuid"],
                    "title": entry["title"],
                    "parent_uuid": entry.get("parent_uuid"),
                    "depth": entry.get("depth", 0),
                    "path": entry.get("path", []),
                    "text": entry.get("text", "").strip(),
                    "source_order": entry.get("source_order", fallback_order),
                    "matched_problem": matched_problem,
                }
            )

    return results


def sort_results(results: list[dict[str, Any]], mode: str) -> list[dict[str, Any]]:
    if mode == "step":
        return sorted(
            results,
            key=lambda item: (
                item["matched_problem"].get("step_number", 999999),
                -item["matched_problem"].get("weight", 0),
                item.get("depth", 0),
                item.get("source_order", 999999),
            ),
        )

    if mode == "weight":
        return sorted(
            results,
            key=lambda item: (
                -item["matched_problem"].get("weight", 0),
                item["matched_problem"].get("step_number", 999999),
                item.get("depth", 0),
                item.get("source_order", 999999),
            ),
        )

    if mode == "yaml":
        return sorted(results, key=lambda item: item.get("source_order", 999999))

    raise ValueError(f"Unsupported mode: {mode}")


def to_camel_case(text: str) -> str:
    parts = re.split(r"[^A-Za-z0-9]+", text.strip())
    words = [part for part in parts if part]

    if not words:
        return "contextPacket"

    return words[0].lower() + "".join(word[:1].upper() + word[1:] for word in words[1:])


def format_results_as_text(results: list[dict[str, Any]]) -> str:
    if not results:
        return ""

    text_blocks = [item["text"] for item in results if item.get("text")]
    return "\n\n".join(text_blocks)


def format_results_as_markdown(
    results: list[dict[str, Any]],
    problem_name: str,
    mode: str,
) -> str:
    lines = [
        f"# Context Packet: {problem_name}",
        "",
        f"Mode: `{mode}`",
        "",
    ]

    if not results:
        lines.append("No context found.")
        return "\n".join(lines)

    for item in results:
        problem = item["matched_problem"]
        step_number = problem.get("step_number")
        weight = problem.get("weight")
        path = " > ".join(item.get("path", []))
        keywords = problem.get("keywords", [])

        lines.extend(
            [
                f"## Step {step_number} - {item['title']}",
                "",
                f"**Weight:** {weight}",
                "",
            ]
        )

        if path:
            lines.extend([f"**Path:** `{path}`", ""])

        if keywords:
            lines.extend([f"**Keywords:** {', '.join(keywords)}", ""])

        lines.extend([item.get("text", ""), ""])

    return "\n".join(lines).strip()


def build_json_payload(
    results: list[dict[str, Any]],
    problem_name: str,
    mode: str,
) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []

    for item in results:
        problem = item["matched_problem"]
        entries.append(
            {
                "title": item["title"],
                "uuid": item["uuid"],
                "parent_uuid": item.get("parent_uuid"),
                "depth": item.get("depth", 0),
                "path": item.get("path", []),
                "step_number": problem.get("step_number"),
                "weight": problem.get("weight"),
                "problem_uuid": problem.get("problem_uuid"),
                "keywords": problem.get("keywords", []),
                "text": item.get("text", ""),
            }
        )

    return {
        "problem_name": problem_name,
        "mode": mode,
        "entry_count": len(entries),
        "entries": entries,
    }


def format_results_as_json(
    results: list[dict[str, Any]],
    problem_name: str,
    mode: str,
) -> str:
    return json.dumps(
        build_json_payload(results, problem_name, mode),
        indent=2,
    )


def render_results(
    results: list[dict[str, Any]],
    problem_name: str,
    mode: str,
    output_format: str,
) -> str:
    if output_format == "txt":
        if not results:
            return f"No context found for problem: {problem_name}"
        return format_results_as_text(results)

    if output_format == "md":
        return format_results_as_markdown(results, problem_name, mode)

    if output_format == "json":
        return format_results_as_json(results, problem_name, mode)

    raise ValueError(f"Unsupported format: {output_format}")


def write_results_to_file(
    results: list[dict[str, Any]],
    problem_name: str,
    mode: str,
    output_format: str,
    output_dir: Path = OUTPUT_DIR,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)

    extension_by_format = {
        "txt": "txt",
        "md": "md",
        "json": "json",
    }
    extension = extension_by_format[output_format]
    file_name = (
        f"{to_camel_case(problem_name)}{mode[:1].upper() + mode[1:]}.{extension}"
    )
    output_path = output_dir / file_name

    output_text = render_results(results, problem_name, mode, output_format)

    with output_path.open("w", encoding="utf-8") as file_handle:
        file_handle.write(output_text)

    return output_path


def print_results(
    results: list[dict[str, Any]],
    problem_name: str,
    mode: str,
    output_format: str,
) -> None:
    print(render_results(results, problem_name, mode, output_format))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Query the flattened context index and write a context packet."
    )
    parser.add_argument(
        "problem_name",
        help='Problem name, for example: "Order Flow Issue Triage"',
    )
    parser.add_argument(
        "--mode",
        choices=("step", "weight", "yaml"),
        default="step",
        help="Sort by step, weight, or raw YAML traversal order.",
    )
    parser.add_argument(
        "--format",
        choices=("txt", "md", "json"),
        default="txt",
        help="Render the routed packet as plain text, Markdown, or JSON.",
    )
    parser.add_argument(
        "--index-file",
        type=Path,
        default=INDEX_FILE,
        help=f"Path to the compiled context index. Default: {INDEX_FILE}",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=OUTPUT_DIR,
        help=f"Directory for generated context packets. Default: {OUTPUT_DIR}",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    results = query_by_problem(
        problem_name=args.problem_name,
        index_file=args.index_file,
    )
    sorted_results = sort_results(results, args.mode)

    print_results(sorted_results, args.problem_name, args.mode, args.format)

    output_path = write_results_to_file(
        sorted_results,
        args.problem_name,
        args.mode,
        args.format,
        output_dir=args.output_dir,
    )
    print(f"\nWrote context packet to: {display_path(output_path)}")


if __name__ == "__main__":
    main()

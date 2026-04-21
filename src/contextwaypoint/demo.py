# Copyright (c) 2026 Daniel Bueno
# SPDX-License-Identifier: MIT
# See LICENSE for the full license text.

from dataclasses import dataclass
from pathlib import Path

from contextwaypoint.common import (
    DEFAULT_DEMO_OUTPUT_DIR,
    DEMO_ROOT,
    FORMATS_DIR,
    display_path,
)
from contextwaypoint.compiler import compile_source
from contextwaypoint.router import render_results, route_problem


@dataclass(frozen=True)
class DemoSpec:
    name: str
    problem_name: str
    source: Path
    route_mode: str
    route_format: str
    problem_file: Path
    unordered_context_file: Path
    explanation_file: Path


DEMO_SPECS = {
    "order-4-not-shipped": DemoSpec(
        name="order-4-not-shipped",
        problem_name="Order Fulfillment Investigation",
        source=FORMATS_DIR,
        route_mode="step",
        route_format="md",
        problem_file=DEMO_ROOT / "problem.md",
        unordered_context_file=DEMO_ROOT / "unordered_retrieved_context.md",
        explanation_file=DEMO_ROOT / "explanation.md",
    )
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def available_demo_names() -> list[str]:
    return sorted(DEMO_SPECS)


def build_demo_report(spec: DemoSpec, route_map: str, routed_packet: str) -> str:
    return "\n\n".join(
        [
            f"# Demo: {spec.name}",
            "## Problem",
            read_text(spec.problem_file),
            "## Unordered Retrieved Context",
            read_text(spec.unordered_context_file),
            "## Generated Route Map",
            route_map.strip(),
            "## Generated Routed Context Packet",
            routed_packet.strip(),
            "## Thesis",
            read_text(spec.explanation_file),
        ]
    ).strip()


def run_demo(
    name: str,
    output_dir: Path = DEFAULT_DEMO_OUTPUT_DIR,
) -> tuple[str, Path]:
    if name not in DEMO_SPECS:
        raise ValueError(
            f"Unknown demo '{name}'. Available demos: {', '.join(available_demo_names())}"
        )

    spec = DEMO_SPECS[name]
    demo_output_dir = output_dir / spec.name
    demo_output_dir.mkdir(parents=True, exist_ok=True)

    index_file = demo_output_dir / "contextIndex.json"
    compile_source(spec.source, index_file)

    routed_results = route_problem(
        spec.problem_name,
        mode=spec.route_mode,
        index_file=index_file,
    )
    route_map = render_results(
        routed_results,
        spec.problem_name,
        spec.route_mode,
        "md",
        route_only=True,
    )
    routed_packet = render_results(
        routed_results,
        spec.problem_name,
        spec.route_mode,
        spec.route_format,
        route_only=False,
    )

    report = build_demo_report(spec, route_map, routed_packet)

    output_path = demo_output_dir / f"{spec.name}.md"
    output_path.write_text(report, encoding="utf-8")

    route_map_path = demo_output_dir / "routeMap.md"
    route_map_path.write_text(route_map, encoding="utf-8")

    packet_path = demo_output_dir / "routedContextPacket.md"
    packet_path.write_text(routed_packet, encoding="utf-8")

    return report, output_path


def demo_summary(output_path: Path) -> str:
    return f"Wrote demo report to: {display_path(output_path)}"

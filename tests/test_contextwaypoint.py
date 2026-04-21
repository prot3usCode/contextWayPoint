# Copyright (c) 2026 Daniel Bueno
# SPDX-License-Identifier: MIT
# See LICENSE for the full license text.

import json
import tempfile
import textwrap
import unittest
from pathlib import Path

from contextwaypoint.compiler import compile_source, fill_uuid_source
from contextwaypoint.router import route_problem


def write_text(path: Path, contents: str) -> None:
    path.write_text(textwrap.dedent(contents).lstrip(), encoding="utf-8")


class ContextWayPointTests(unittest.TestCase):
    def test_compile_preserves_hierarchy_and_source_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            contexts_dir = base / "contexts"
            contexts_dir.mkdir()

            write_text(
                contexts_dir / "domain.yaml",
                """
                title: Domain
                uuid: domain_root
                text: Root domain context.
                problems:
                  - problem_name: Demo Problem
                    problem_uuid:
                    step_number: 1
                    weight: 100
                    keywords:
                      - domain
                entries:
                  - title: Overview
                    uuid: overview_section
                    text: Start with the overview.
                    problems:
                      - problem_name: Demo Problem
                        problem_uuid:
                        step_number: 2
                        weight: 80
                        keywords:
                          - overview
                """,
            )

            write_text(
                contexts_dir / "rules.yaml",
                """
                title: Rules
                uuid: rules_root
                text: Rule set.
                entries:
                  - title: Payment Check
                    uuid: payment_check
                    text: Check payment.
                    problems:
                      - problem_name: Demo Problem
                        problem_uuid:
                        step_number: 3
                        weight: 90
                        keywords:
                          - payment
                """,
            )

            output_file = base / "contextIndex.json"
            compile_source(contexts_dir, output_file)
            compiled_entries = json.loads(output_file.read_text(encoding="utf-8"))

            overview_entry = next(
                entry for entry in compiled_entries if entry["uuid"] == "overview_section"
            )
            payment_entry = next(
                entry for entry in compiled_entries if entry["uuid"] == "payment_check"
            )

            self.assertEqual(overview_entry["parent_uuid"], "domain_root")
            self.assertEqual(overview_entry["depth"], 1)
            self.assertEqual(overview_entry["path"], ["Domain", "Overview"])
            self.assertTrue(overview_entry["source_file"].endswith("domain.yaml"))
            self.assertTrue(payment_entry["source_file"].endswith("rules.yaml"))

    def test_step_mode_routes_in_step_order(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            context_file = base / "demo.yaml"

            write_text(
                context_file,
                """
                title: Demo Root
                uuid: demo_root
                text: Root.
                problems:
                  - problem_name: Demo Problem
                    problem_uuid:
                    step_number: 1
                    weight: 10
                    keywords:
                      - root
                entries:
                  - title: Later Step
                    uuid: later_step
                    text: Later.
                    problems:
                      - problem_name: Demo Problem
                        problem_uuid:
                        step_number: 3
                        weight: 30
                        keywords:
                          - later
                  - title: Earlier Step
                    uuid: earlier_step
                    text: Earlier.
                    problems:
                      - problem_name: Demo Problem
                        problem_uuid:
                        step_number: 2
                        weight: 20
                        keywords:
                          - earlier
                """,
            )

            output_file = base / "contextIndex.json"
            compile_source(context_file, output_file)
            routed_titles = [
                item["title"]
                for item in route_problem(
                    "Demo Problem",
                    mode="step",
                    index_file=output_file,
                )
            ]

            self.assertEqual(
                routed_titles,
                ["Demo Root", "Earlier Step", "Later Step"],
            )

    def test_weight_mode_prioritizes_heavier_entries(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            context_file = base / "demo.yaml"

            write_text(
                context_file,
                """
                title: Demo Root
                uuid: demo_root
                text: Root.
                problems:
                  - problem_name: Demo Problem
                    problem_uuid:
                    step_number: 3
                    weight: 10
                    keywords:
                      - root
                entries:
                  - title: Heavy Check
                    uuid: heavy_check
                    text: Heavy.
                    problems:
                      - problem_name: Demo Problem
                        problem_uuid:
                        step_number: 2
                        weight: 95
                        keywords:
                          - heavy
                  - title: Medium Check
                    uuid: medium_check
                    text: Medium.
                    problems:
                      - problem_name: Demo Problem
                        problem_uuid:
                        step_number: 1
                        weight: 50
                        keywords:
                          - medium
                """,
            )

            output_file = base / "contextIndex.json"
            compile_source(context_file, output_file)
            routed_titles = [
                item["title"]
                for item in route_problem(
                    "Demo Problem",
                    mode="weight",
                    index_file=output_file,
                )
            ]

            self.assertEqual(
                routed_titles,
                ["Heavy Check", "Medium Check", "Demo Root"],
            )

    def test_keyword_mode_scores_and_sorts_results(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            context_file = base / "demo.yaml"

            write_text(
                context_file,
                """
                title: Demo Root
                uuid: demo_root
                text: Root context.
                problems:
                  - problem_name: Demo Problem
                    problem_uuid:
                    step_number: 1
                    weight: 5
                    keywords:
                      - overview
                entries:
                  - title: Payment Check
                    uuid: payment_check
                    text: Payment failed and payment declined.
                    problems:
                      - problem_name: Demo Problem
                        problem_uuid:
                        step_number: 3
                        weight: 50
                        keywords:
                          - payment
                          - failed
                  - title: Shipment Check
                    uuid: shipment_check
                    text: Shipment delayed.
                    problems:
                      - problem_name: Demo Problem
                        problem_uuid:
                        step_number: 2
                        weight: 40
                        keywords:
                          - shipment
                """,
            )

            output_file = base / "contextIndex.json"
            compile_source(context_file, output_file)
            routed_results = route_problem(
                "Demo Problem",
                mode="keyword",
                index_file=output_file,
                keywords=["payment", "failed"],
            )

            self.assertEqual(routed_results[0]["title"], "Payment Check")
            self.assertGreater(routed_results[0]["keyword_score"], routed_results[1]["keyword_score"])

    def test_fill_uuid_source_writes_nonblank_problem_uuids_for_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            source_dir = base / "source"
            output_dir = base / "filled"
            source_dir.mkdir()

            write_text(
                source_dir / "one.yaml",
                """
                title: First
                uuid: first_root
                text: First file.
                problems:
                  - problem_name: Shared Problem
                    problem_uuid:
                    step_number: 1
                    weight: 10
                    keywords:
                      - first
                """,
            )

            write_text(
                source_dir / "two.yaml",
                """
                title: Second
                uuid: second_root
                text: Second file.
                problems:
                  - problem_name: Shared Problem
                    problem_uuid:
                    step_number: 2
                    weight: 20
                    keywords:
                      - second
                """,
            )

            written_files = fill_uuid_source(source_dir, output_path=output_dir)
            written_values = []

            for written_file in written_files:
                payload = written_file.read_text(encoding="utf-8")
                self.assertIn("problem_uuid:", payload)
                for line in payload.splitlines():
                    if line.strip().startswith("problem_uuid:"):
                        written_values.append(line.split(":", 1)[1].strip())

            self.assertEqual(len(written_files), 2)
            self.assertEqual(len(written_values), 2)
            self.assertTrue(all(value for value in written_values))
            self.assertEqual(len(set(written_values)), 2)


if __name__ == "__main__":
    unittest.main()

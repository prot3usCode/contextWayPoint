# Copyright (c) 2026 Daniel Bueno
# SPDX-License-Identifier: MIT
# See LICENSE for the full license text.

import json
import tempfile
import textwrap
import unittest
from pathlib import Path

from contextwaypoint.compiler import compile_source, fill_uuid_source
from contextwaypoint.project_export import (
    build_project_outputs,
    render_project_yaml_from_file,
)
from contextwaypoint.router import route_and_write, route_problem


def write_text(path: Path, contents: str) -> None:
    path.write_text(textwrap.dedent(contents).lstrip(), encoding="utf-8")


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


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

    def test_compile_directory_uses_sorted_files_and_global_source_order(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            contexts_dir = base / "contexts"
            contexts_dir.mkdir()

            write_text(
                contexts_dir / "b_rules.yaml",
                """
                title: Rules
                uuid: rules_root
                text: Rule set.
                problems:
                  - problem_name: Demo Problem
                    problem_uuid:
                    step_number: 2
                    weight: 20
                    keywords:
                      - rules
                """,
            )

            write_text(
                contexts_dir / "a_domain.yaml",
                """
                title: Domain
                uuid: domain_root
                text: Root domain context.
                problems:
                  - problem_name: Demo Problem
                    problem_uuid:
                    step_number: 1
                    weight: 30
                    keywords:
                      - domain
                entries:
                  - title: Overview
                    uuid: overview_section
                    text: Start with the overview.
                    problems:
                      - problem_name: Demo Problem
                        problem_uuid:
                        step_number: 3
                        weight: 10
                        keywords:
                          - overview
                """,
            )

            output_file = base / "contextIndex.json"
            compile_source(contexts_dir, output_file)
            compiled_entries = json.loads(output_file.read_text(encoding="utf-8"))

            self.assertEqual(
                [entry["source_order"] for entry in compiled_entries],
                [0, 1, 2],
            )
            self.assertTrue(compiled_entries[0]["source_file"].endswith("a_domain.yaml"))
            self.assertTrue(compiled_entries[1]["source_file"].endswith("a_domain.yaml"))
            self.assertTrue(compiled_entries[2]["source_file"].endswith("b_rules.yaml"))

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

    def test_txt_route_writes_context_only_and_companion_audit_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            context_file = base / "demo.yaml"
            output_file = base / "contextIndex.json"
            packet_dir = base / "packets"

            write_text(
                context_file,
                """
                title: Demo Root
                uuid: demo_root
                text: Root context block.
                problems:
                  - problem_name: Demo Problem
                    problem_uuid:
                    step_number: 1
                    weight: 25
                    keywords:
                      - root
                      - overview
                entries:
                  - title: Payment Check
                    uuid: payment_check
                    text: Payment context block.
                    problems:
                      - problem_name: Demo Problem
                        problem_uuid:
                        step_number: 2
                        weight: 80
                        keywords:
                          - payment
                          - failed
                """,
            )

            compile_source(context_file, output_file)

            rendered_output, output_path, audit_path = route_and_write(
                "Demo Problem",
                mode="step",
                output_format="txt",
                route_only=False,
                index_file=output_file,
                output_dir=packet_dir,
            )

            self.assertEqual(
                rendered_output,
                "Root context block.\n\nPayment context block.",
            )
            self.assertEqual(output_path.read_text(encoding="utf-8"), rendered_output)
            self.assertIsNotNone(audit_path)

            assert audit_path is not None
            audit_text = audit_path.read_text(encoding="utf-8")

            self.assertNotIn("Step 1 - Demo Root", rendered_output)
            self.assertNotIn("Source:", rendered_output)
            self.assertIn("Step 1 - Demo Root", audit_text)
            self.assertIn("Source:", audit_text)
            self.assertIn("Keywords: root, overview", audit_text)
            self.assertIn("Keywords: payment, failed", audit_text)

    def test_route_map_txt_output_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            context_file = base / "demo.yaml"
            output_file = base / "contextIndex.json"
            packet_dir = base / "packets"

            write_text(
                context_file,
                """
                title: Demo Root
                uuid: demo_root
                text: Root context block.
                problems:
                  - problem_name: Demo Problem
                    problem_uuid:
                    step_number: 1
                    weight: 25
                    keywords:
                      - root
                entries:
                  - title: Payment Check
                    uuid: payment_check
                    text: Payment context block.
                    problems:
                      - problem_name: Demo Problem
                        problem_uuid:
                        step_number: 2
                        weight: 80
                        keywords:
                          - payment
                """,
            )

            compile_source(context_file, output_file)

            rendered_output, output_path, audit_path = route_and_write(
                "Demo Problem",
                mode="step",
                output_format="txt",
                route_only=True,
                index_file=output_file,
                output_dir=packet_dir,
            )

            expected_output = (
                "Route Map: Demo Problem\n"
                "Mode: step\n\n"
                "1. Demo Root\n"
                "   Step: 1\n"
                f"   Source: {context_file}\n"
                "   Path: Demo Root\n\n"
                "2. Payment Check\n"
                "   Step: 2\n"
                f"   Source: {context_file}\n"
                "   Path: Demo Root > Payment Check"
            )

            self.assertEqual(rendered_output, expected_output)
            self.assertEqual(output_path.read_text(encoding="utf-8"), expected_output)
            self.assertIsNone(audit_path)

    def test_project_render_outputs_deterministic_generated_yaml(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            project_file = base / "project.json"

            write_json(
                project_file,
                {
                    "version": "0.1",
                    "project_name": "Authoring Demo",
                    "documents": [
                        {
                            "document_id": "doc_a",
                            "display_name": "paymentRules.yaml",
                            "source_path": "/tmp/paymentRules.yaml",
                            "file_type": "yaml",
                            "status": "available",
                        }
                    ],
                    "anchors": [
                        {
                            "anchor_id": "anchor_payment",
                            "document_id": "doc_a",
                            "selected_text": "Check the latest payment.",
                            "char_start": 10,
                            "char_end": 35,
                            "context_before": "Before",
                            "context_after": "After",
                            "capture_method": "text_selection",
                        }
                    ],
                    "nodes": [
                        {
                            "node_id": "node_payment",
                            "title": "Payment Check",
                            "anchor_id": "anchor_payment",
                            "body_text": "Check the latest payment.",
                            "problem_assignments": [
                                {
                                    "problem_name": "Order Investigation",
                                    "step_number": 2,
                                    "weight": 95,
                                    "keywords": ["payment", "failed"],
                                }
                            ],
                        }
                    ],
                    "problems": [
                        {
                            "problem_name": "Order Investigation",
                            "description": "Investigate the order state.",
                            "entry_node_id": "node_payment",
                            "node_ids": ["node_payment"],
                            "status": "draft",
                        }
                    ],
                    "export_preferences": {
                        "target_format": "yaml",
                        "preserve_source_path": True,
                    },
                },
            )

            rendered_documents = render_project_yaml_from_file(project_file)
            self.assertEqual(
                list(rendered_documents.keys()),
                ["order_investigation.generated.yaml"],
            )

            rendered_yaml = rendered_documents["order_investigation.generated.yaml"]
            self.assertIn("title: Order Investigation", rendered_yaml)
            self.assertIn("uuid: problem_order_investigation", rendered_yaml)
            self.assertIn("title: Payment Check", rendered_yaml)
            self.assertIn("source_path: /tmp/paymentRules.yaml", rendered_yaml)
            self.assertIn("problem_name: Order Investigation", rendered_yaml)
            self.assertIn("step_number: 2", rendered_yaml)

    def test_project_build_writes_yaml_and_compiled_json_with_origin(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            project_file = base / "project.json"
            yaml_dir = base / "generated"
            json_out = base / "contextIndex.json"

            write_json(
                project_file,
                {
                    "version": "0.1",
                    "project_name": "Authoring Demo",
                    "documents": [
                        {
                            "document_id": "doc_a",
                            "display_name": "orderRules.md",
                            "source_path": "/tmp/orderRules.md",
                            "file_type": "md",
                            "status": "available",
                        }
                    ],
                    "anchors": [
                        {
                            "anchor_id": "anchor_overview",
                            "document_id": "doc_a",
                            "selected_text": "Start with the overview.",
                            "char_start": 0,
                            "char_end": 24,
                            "capture_method": "text_selection",
                        },
                        {
                            "anchor_id": "anchor_payment",
                            "document_id": "doc_a",
                            "selected_text": "Check the payment state.",
                            "char_start": 30,
                            "char_end": 54,
                            "capture_method": "text_selection",
                        },
                    ],
                    "nodes": [
                        {
                            "node_id": "node_overview",
                            "title": "Overview",
                            "anchor_id": "anchor_overview",
                            "body_text": "Start with the overview.",
                            "problem_assignments": [
                                {
                                    "problem_name": "Order Investigation",
                                    "step_number": 1,
                                    "weight": 100,
                                    "keywords": ["overview"],
                                }
                            ],
                        },
                        {
                            "node_id": "node_payment",
                            "title": "Payment Check",
                            "anchor_id": "anchor_payment",
                            "body_text": "Check the payment state.",
                            "problem_assignments": [
                                {
                                    "problem_name": "Order Investigation",
                                    "step_number": 2,
                                    "weight": 90,
                                    "keywords": ["payment"],
                                }
                            ],
                        },
                    ],
                    "problems": [
                        {
                            "problem_name": "Order Investigation",
                            "description": "Investigate the order state.",
                            "entry_node_id": "node_overview",
                            "node_ids": ["node_overview", "node_payment"],
                            "status": "draft",
                        }
                    ],
                    "export_preferences": {
                        "target_format": "yaml",
                        "preserve_source_path": True,
                    },
                },
            )

            message = build_project_outputs(project_file, yaml_dir, json_out)

            self.assertIn("Generated 1 YAML document(s)", message)
            self.assertTrue((yaml_dir / "order_investigation.generated.yaml").exists())
            self.assertTrue(json_out.exists())

            compiled_entries = json.loads(json_out.read_text(encoding="utf-8"))
            routed_titles = [
                item["title"]
                for item in route_problem(
                    "Order Investigation",
                    mode="step",
                    index_file=json_out,
                )
            ]

            self.assertEqual(routed_titles, ["Overview", "Payment Check"])
            self.assertEqual(
                compiled_entries[1]["origin"]["source_path"],
                "/tmp/orderRules.md",
            )
            self.assertTrue(
                compiled_entries[1]["source_file"].endswith(
                    "order_investigation.generated.yaml"
                )
            )

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

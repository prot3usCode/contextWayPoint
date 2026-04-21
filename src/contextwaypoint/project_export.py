# Copyright (c) 2026 Daniel Bueno
# SPDX-License-Identifier: MIT
# See LICENSE for the full license text.

import re
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from contextwaypoint.common import DEFAULT_INDEX_FILE, display_path
from contextwaypoint.compiler import compile_source
from contextwaypoint.project import (
    ProblemAssignment,
    ProblemDefinition,
    ProjectState,
    RouteNode,
    SelectionAnchor,
    SourceDocument,
    load_project,
)


@dataclass(frozen=True)
class GeneratedYamlDocument:
    problem_name: str
    file_name: str
    root: dict[str, Any]


def slugify(text: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9]+", "_", text.strip().lower()).strip("_")
    return normalized or "project"


def generated_problem_uuid(
    project_name: str,
    problem_name: str,
    node_id: str,
    assignment: ProblemAssignment,
) -> str:
    stable_key = (
        f"{project_name}|{problem_name}|{node_id}|"
        f"{assignment.step_number}|{assignment.weight}"
    )
    return str(uuid.uuid5(uuid.NAMESPACE_URL, stable_key))


def problem_root_uuid(problem_name: str) -> str:
    return f"problem_{slugify(problem_name)}"


def root_text(problem: ProblemDefinition) -> str:
    if problem.description.strip():
        return problem.description.strip()
    return f"Authored route for {problem.problem_name}."


def node_origin(
    document: SourceDocument,
    anchor: SelectionAnchor,
    preserve_source_path: bool,
) -> dict[str, Any]:
    origin = {
        "document_id": document.document_id,
        "display_name": document.display_name,
        "file_type": document.file_type,
        "anchor_id": anchor.anchor_id,
        "selected_text": anchor.selected_text,
        "capture_method": anchor.capture_method,
    }

    if preserve_source_path:
        origin["source_path"] = document.source_path

    if anchor.char_start is not None:
        origin["char_start"] = anchor.char_start

    if anchor.char_end is not None:
        origin["char_end"] = anchor.char_end

    if anchor.page_number is not None:
        origin["page_number"] = anchor.page_number

    if anchor.context_before:
        origin["context_before"] = anchor.context_before

    if anchor.context_after:
        origin["context_after"] = anchor.context_after

    return origin


def export_assignment(
    project: ProjectState,
    node: RouteNode,
    assignment: ProblemAssignment,
    document: SourceDocument,
    anchor: SelectionAnchor,
) -> dict[str, Any]:
    return {
        "title": node.title,
        "uuid": node.node_id,
        "text": node.body_text,
        "origin": node_origin(
            document,
            anchor,
            preserve_source_path=project.export_preferences.preserve_source_path,
        ),
        "problems": [
            {
                "problem_name": assignment.problem_name,
                "problem_uuid": generated_problem_uuid(
                    project.project_name,
                    assignment.problem_name,
                    node.node_id,
                    assignment,
                ),
                "step_number": assignment.step_number,
                "weight": assignment.weight,
                "keywords": assignment.keywords,
            }
        ],
    }


def exported_entries_for_problem(
    project: ProjectState,
    problem: ProblemDefinition,
) -> list[dict[str, Any]]:
    documents = project.document_by_id()
    anchors = project.anchor_by_id()
    entries: list[tuple[int, float, str, dict[str, Any]]] = []

    for node in project.nodes:
        anchor = anchors[node.anchor_id]
        document = documents[anchor.document_id]

        for assignment in node.problem_assignments:
            if assignment.problem_name != problem.problem_name:
                continue

            entries.append(
                (
                    assignment.step_number,
                    -assignment.weight,
                    node.node_id,
                    export_assignment(
                        project,
                        node,
                        assignment,
                        document,
                        anchor,
                    ),
                )
            )

    entries.sort(key=lambda item: (item[0], item[1], item[2]))
    return [entry for _, _, _, entry in entries]


def export_problem_document(
    project: ProjectState,
    problem: ProblemDefinition,
) -> GeneratedYamlDocument:
    file_name = f"{slugify(problem.problem_name)}.generated.yaml"
    root = {
        "title": problem.problem_name,
        "uuid": problem_root_uuid(problem.problem_name),
        "text": root_text(problem),
        "entries": exported_entries_for_problem(project, problem),
    }

    return GeneratedYamlDocument(
        problem_name=problem.problem_name,
        file_name=file_name,
        root=root,
    )


def export_project_documents(project: ProjectState) -> list[GeneratedYamlDocument]:
    return [
        export_problem_document(project, problem)
        for problem in project.problems
    ]


def render_generated_yaml(document: GeneratedYamlDocument) -> str:
    return yaml.safe_dump(
        document.root,
        sort_keys=False,
        allow_unicode=True,
    )


def render_project_yaml(project: ProjectState) -> dict[str, str]:
    return {
        document.file_name: render_generated_yaml(document)
        for document in export_project_documents(project)
    }


def write_project_yaml(
    project: ProjectState,
    output_dir: Path,
) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    written_paths: list[Path] = []

    for document in export_project_documents(project):
        output_path = output_dir / document.file_name
        output_path.write_text(render_generated_yaml(document), encoding="utf-8")
        written_paths.append(output_path)

    return written_paths


def clear_generated_yaml_files(output_dir: Path) -> None:
    if not output_dir.exists():
        return

    for path in output_dir.glob("*.generated.yaml"):
        path.unlink()


def render_project_yaml_from_file(project_file: Path) -> dict[str, str]:
    return render_project_yaml(load_project(project_file))


def build_project_outputs(
    project_file: Path,
    yaml_output_dir: Path,
    json_output_file: Path = DEFAULT_INDEX_FILE,
) -> str:
    project = load_project(project_file)
    clear_generated_yaml_files(yaml_output_dir)
    written_paths = write_project_yaml(project, yaml_output_dir)
    compile_message = compile_source(yaml_output_dir, json_output_file)
    yaml_label = ", ".join(display_path(path) for path in written_paths)

    return (
        f"Generated {len(written_paths)} YAML document(s) from "
        f"{display_path(project_file)} to {yaml_label}\n"
        f"{compile_message}"
    )

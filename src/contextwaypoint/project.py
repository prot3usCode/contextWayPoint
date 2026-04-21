# Copyright (c) 2026 Daniel Bueno
# SPDX-License-Identifier: MIT
# See LICENSE for the full license text.

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class SourceDocument:
    document_id: str
    display_name: str
    source_path: str
    file_type: str
    sha256: str | None = None
    modified_at: str | None = None
    size_bytes: int | None = None
    status: str = "available"

    @classmethod
    def from_dict(cls, payload: dict) -> "SourceDocument":
        return cls(
            document_id=str(payload["document_id"]),
            display_name=str(payload["display_name"]),
            source_path=str(payload["source_path"]),
            file_type=str(payload["file_type"]),
            sha256=_optional_str(payload.get("sha256")),
            modified_at=_optional_str(payload.get("modified_at")),
            size_bytes=_optional_int(payload.get("size_bytes")),
            status=str(payload.get("status", "available")),
        )


@dataclass
class SelectionAnchor:
    anchor_id: str
    document_id: str
    selected_text: str
    char_start: int | None = None
    char_end: int | None = None
    page_number: int | None = None
    context_before: str = ""
    context_after: str = ""
    capture_method: str = "text_selection"

    @classmethod
    def from_dict(cls, payload: dict) -> "SelectionAnchor":
        return cls(
            anchor_id=str(payload["anchor_id"]),
            document_id=str(payload["document_id"]),
            selected_text=str(payload["selected_text"]),
            char_start=_optional_int(payload.get("char_start")),
            char_end=_optional_int(payload.get("char_end")),
            page_number=_optional_int(payload.get("page_number")),
            context_before=str(payload.get("context_before", "")),
            context_after=str(payload.get("context_after", "")),
            capture_method=str(payload.get("capture_method", "text_selection")),
        )


@dataclass
class ProblemAssignment:
    problem_name: str
    step_number: int
    weight: float
    keywords: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, payload: dict) -> "ProblemAssignment":
        return cls(
            problem_name=str(payload["problem_name"]),
            step_number=int(payload["step_number"]),
            weight=float(payload["weight"]),
            keywords=[str(keyword) for keyword in payload.get("keywords", [])],
        )


@dataclass
class RouteNode:
    node_id: str
    title: str
    anchor_id: str
    body_text: str
    notes: str = ""
    problem_assignments: list[ProblemAssignment] = field(default_factory=list)

    @classmethod
    def from_dict(cls, payload: dict) -> "RouteNode":
        return cls(
            node_id=str(payload["node_id"]),
            title=str(payload["title"]),
            anchor_id=str(payload["anchor_id"]),
            body_text=str(payload["body_text"]),
            notes=str(payload.get("notes", "")),
            problem_assignments=[
                ProblemAssignment.from_dict(assignment)
                for assignment in payload.get("problem_assignments", [])
            ],
        )


@dataclass
class RouteEdge:
    edge_id: str
    problem_name: str
    from_node_id: str
    to_node_id: str
    label: str = "next"

    @classmethod
    def from_dict(cls, payload: dict) -> "RouteEdge":
        return cls(
            edge_id=str(payload["edge_id"]),
            problem_name=str(payload["problem_name"]),
            from_node_id=str(payload["from_node_id"]),
            to_node_id=str(payload["to_node_id"]),
            label=str(payload.get("label", "next")),
        )


@dataclass
class ProblemDefinition:
    problem_name: str
    description: str
    entry_node_id: str | None = None
    node_ids: list[str] = field(default_factory=list)
    status: str = "draft"

    @classmethod
    def from_dict(cls, payload: dict) -> "ProblemDefinition":
        return cls(
            problem_name=str(payload["problem_name"]),
            description=str(payload.get("description", "")),
            entry_node_id=_optional_str(payload.get("entry_node_id")),
            node_ids=[str(node_id) for node_id in payload.get("node_ids", [])],
            status=str(payload.get("status", "draft")),
        )


@dataclass
class ExportPreferences:
    target_format: str = "yaml"
    preserve_source_path: bool = True

    @classmethod
    def from_dict(cls, payload: dict | None) -> "ExportPreferences":
        if payload is None:
            return cls()

        return cls(
            target_format=str(payload.get("target_format", "yaml")),
            preserve_source_path=bool(payload.get("preserve_source_path", True)),
        )


@dataclass
class ProjectState:
    version: str
    project_name: str
    created_at: str | None = None
    updated_at: str | None = None
    documents: list[SourceDocument] = field(default_factory=list)
    anchors: list[SelectionAnchor] = field(default_factory=list)
    nodes: list[RouteNode] = field(default_factory=list)
    edges: list[RouteEdge] = field(default_factory=list)
    problems: list[ProblemDefinition] = field(default_factory=list)
    export_preferences: ExportPreferences = field(default_factory=ExportPreferences)

    @classmethod
    def from_dict(cls, payload: dict) -> "ProjectState":
        return cls(
            version=str(payload.get("version", "0.1")),
            project_name=str(payload["project_name"]),
            created_at=_optional_str(payload.get("created_at")),
            updated_at=_optional_str(payload.get("updated_at")),
            documents=[
                SourceDocument.from_dict(document)
                for document in payload.get("documents", [])
            ],
            anchors=[
                SelectionAnchor.from_dict(anchor)
                for anchor in payload.get("anchors", [])
            ],
            nodes=[
                RouteNode.from_dict(node)
                for node in payload.get("nodes", [])
            ],
            edges=[
                RouteEdge.from_dict(edge)
                for edge in payload.get("edges", [])
            ],
            problems=[
                ProblemDefinition.from_dict(problem)
                for problem in payload.get("problems", [])
            ],
            export_preferences=ExportPreferences.from_dict(
                payload.get("export_preferences")
            ),
        )

    def document_by_id(self) -> dict[str, SourceDocument]:
        return {document.document_id: document for document in self.documents}

    def anchor_by_id(self) -> dict[str, SelectionAnchor]:
        return {anchor.anchor_id: anchor for anchor in self.anchors}

    def node_by_id(self) -> dict[str, RouteNode]:
        return {node.node_id: node for node in self.nodes}

    def problem_by_name(self) -> dict[str, ProblemDefinition]:
        return {problem.problem_name: problem for problem in self.problems}


def _optional_str(value: object) -> str | None:
    if value is None:
        return None
    return str(value)


def _optional_int(value: object) -> int | None:
    if value is None:
        return None
    return int(value)


def load_project(project_file: Path) -> ProjectState:
    with project_file.open("r", encoding="utf-8") as file_handle:
        payload = json.load(file_handle)

    if not isinstance(payload, dict):
        raise ValueError(f"{project_file} must contain a JSON object")

    project = ProjectState.from_dict(payload)
    validate_project(project)
    return project


def validate_project(project: ProjectState) -> None:
    document_ids = {document.document_id for document in project.documents}
    anchor_ids = {anchor.anchor_id for anchor in project.anchors}
    node_ids = {node.node_id for node in project.nodes}
    problem_names = {problem.problem_name for problem in project.problems}

    if len(document_ids) != len(project.documents):
        raise ValueError("Project contains duplicate document_id values")

    if len(anchor_ids) != len(project.anchors):
        raise ValueError("Project contains duplicate anchor_id values")

    if len(node_ids) != len(project.nodes):
        raise ValueError("Project contains duplicate node_id values")

    if len(problem_names) != len(project.problems):
        raise ValueError("Project contains duplicate problem_name values")

    for anchor in project.anchors:
        if anchor.document_id not in document_ids:
            raise ValueError(
                f"Anchor '{anchor.anchor_id}' references unknown document_id '{anchor.document_id}'"
            )

    for node in project.nodes:
        if node.anchor_id not in anchor_ids:
            raise ValueError(
                f"Node '{node.node_id}' references unknown anchor_id '{node.anchor_id}'"
            )

        for assignment in node.problem_assignments:
            if assignment.step_number < 1:
                raise ValueError(
                    f"Node '{node.node_id}' has a step_number less than 1 for '{assignment.problem_name}'"
                )

    for edge in project.edges:
        if edge.from_node_id not in node_ids:
            raise ValueError(
                f"Edge '{edge.edge_id}' references unknown from_node_id '{edge.from_node_id}'"
            )
        if edge.to_node_id not in node_ids:
            raise ValueError(
                f"Edge '{edge.edge_id}' references unknown to_node_id '{edge.to_node_id}'"
            )

    for problem in project.problems:
        if problem.entry_node_id is not None and problem.entry_node_id not in node_ids:
            raise ValueError(
                f"Problem '{problem.problem_name}' references unknown entry_node_id '{problem.entry_node_id}'"
            )

        for node_id in problem.node_ids:
            if node_id not in node_ids:
                raise ValueError(
                    f"Problem '{problem.problem_name}' references unknown node_id '{node_id}'"
                )

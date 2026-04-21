# Copyright (c) 2026 Daniel Bueno
# SPDX-License-Identifier: MIT
# See LICENSE for the full license text.

import json
from dataclasses import dataclass, field as dataclass_field
from pathlib import Path


@dataclass
class ProjectReference:
    project_id: str
    display_name: str
    project_file: str
    compiled_index_file: str | None = None
    status: str = "available"

    @classmethod
    def from_dict(cls, payload: dict) -> "ProjectReference":
        return cls(
            project_id=str(payload["project_id"]),
            display_name=str(payload.get("display_name", payload["project_id"])),
            project_file=str(payload["project_file"]),
            compiled_index_file=_optional_str(payload.get("compiled_index_file")),
            status=str(payload.get("status", "available")),
        )


@dataclass
class ProblemReference:
    project_id: str
    problem_name: str
    mode: str = "step"
    output_format: str = "txt"
    route_only: bool = False

    @classmethod
    def from_dict(cls, payload: dict) -> "ProblemReference":
        return cls(
            project_id=str(payload["project_id"]),
            problem_name=str(payload["problem_name"]),
            mode=str(payload.get("mode", "step")),
            output_format=str(payload.get("output_format", "txt")),
            route_only=bool(payload.get("route_only", False)),
        )


@dataclass
class MacroCondition:
    condition_id: str
    kind: str
    field: str = "prompt_text"
    operator: str = "contains_any"
    values: list[str] = dataclass_field(default_factory=list)
    description: str = ""

    @classmethod
    def from_dict(cls, payload: dict) -> "MacroCondition":
        return cls(
            condition_id=str(payload["condition_id"]),
            kind=str(payload["kind"]),
            field=str(payload.get("field", "prompt_text")),
            operator=str(payload.get("operator", "contains_any")),
            values=[str(value) for value in payload.get("values", [])],
            description=str(payload.get("description", "")),
        )


@dataclass
class MacroStep:
    step_id: str
    action: str
    problem_ref: ProblemReference | None = None
    macro_id: str | None = None
    condition_id: str | None = None
    next_step_id: str | None = None
    true_step_id: str | None = None
    false_step_id: str | None = None
    notes: str = ""

    @classmethod
    def from_dict(cls, payload: dict) -> "MacroStep":
        problem_ref_payload = payload.get("problem_ref")
        return cls(
            step_id=str(payload["step_id"]),
            action=str(payload["action"]),
            problem_ref=(
                ProblemReference.from_dict(problem_ref_payload)
                if isinstance(problem_ref_payload, dict)
                else None
            ),
            macro_id=_optional_str(payload.get("macro_id")),
            condition_id=_optional_str(payload.get("condition_id")),
            next_step_id=_optional_str(payload.get("next_step_id")),
            true_step_id=_optional_str(payload.get("true_step_id")),
            false_step_id=_optional_str(payload.get("false_step_id")),
            notes=str(payload.get("notes", "")),
        )


@dataclass
class MacroDefinition:
    macro_id: str
    name: str
    description: str
    entry_step_id: str
    steps: list[MacroStep] = dataclass_field(default_factory=list)
    conditions: list[MacroCondition] = dataclass_field(default_factory=list)
    tags: list[str] = dataclass_field(default_factory=list)
    status: str = "draft"

    @classmethod
    def from_dict(cls, payload: dict) -> "MacroDefinition":
        return cls(
            macro_id=str(payload["macro_id"]),
            name=str(payload["name"]),
            description=str(payload.get("description", "")),
            entry_step_id=str(payload["entry_step_id"]),
            steps=[MacroStep.from_dict(step) for step in payload.get("steps", [])],
            conditions=[
                MacroCondition.from_dict(condition)
                for condition in payload.get("conditions", [])
            ],
            tags=[str(tag) for tag in payload.get("tags", [])],
            status=str(payload.get("status", "draft")),
        )


@dataclass
class RuntimeDefaults:
    default_mode: str = "step"
    default_output_format: str = "txt"
    rollback_strategy: str = "snapshot"

    @classmethod
    def from_dict(cls, payload: dict | None) -> "RuntimeDefaults":
        if payload is None:
            return cls()

        return cls(
            default_mode=str(payload.get("default_mode", "step")),
            default_output_format=str(payload.get("default_output_format", "txt")),
            rollback_strategy=str(payload.get("rollback_strategy", "snapshot")),
        )


@dataclass
class MacroWorkspace:
    version: str
    workspace_name: str
    created_at: str | None = None
    updated_at: str | None = None
    projects: list[ProjectReference] = dataclass_field(default_factory=list)
    macros: list[MacroDefinition] = dataclass_field(default_factory=list)
    runtime_defaults: RuntimeDefaults = dataclass_field(default_factory=RuntimeDefaults)

    @classmethod
    def from_dict(cls, payload: dict) -> "MacroWorkspace":
        return cls(
            version=str(payload.get("version", "0.1")),
            workspace_name=str(payload["workspace_name"]),
            created_at=_optional_str(payload.get("created_at")),
            updated_at=_optional_str(payload.get("updated_at")),
            projects=[
                ProjectReference.from_dict(project)
                for project in payload.get("projects", [])
            ],
            macros=[MacroDefinition.from_dict(macro) for macro in payload.get("macros", [])],
            runtime_defaults=RuntimeDefaults.from_dict(payload.get("runtime_defaults")),
        )

    def project_by_id(self) -> dict[str, ProjectReference]:
        return {project.project_id: project for project in self.projects}

    def macro_by_id(self) -> dict[str, MacroDefinition]:
        return {macro.macro_id: macro for macro in self.macros}


@dataclass
class PromptEvent:
    timestamp: str
    prompt_text: str
    selected_macro_id: str | None = None
    notes: str = ""

    @classmethod
    def from_dict(cls, payload: dict) -> "PromptEvent":
        return cls(
            timestamp=str(payload["timestamp"]),
            prompt_text=str(payload["prompt_text"]),
            selected_macro_id=_optional_str(payload.get("selected_macro_id")),
            notes=str(payload.get("notes", "")),
        )


@dataclass
class ContextAdjustment:
    adjustment_id: str
    action: str
    created_at: str
    status: str = "active"
    macro_id: str | None = None
    problem_ref: ProblemReference | None = None
    output_mode: str = "step"
    output_format: str = "txt"
    output_file: str | None = None
    compiled_json_file: str | None = None
    notes: str = ""

    @classmethod
    def from_dict(cls, payload: dict) -> "ContextAdjustment":
        problem_ref_payload = payload.get("problem_ref")
        return cls(
            adjustment_id=str(payload["adjustment_id"]),
            action=str(payload["action"]),
            created_at=str(payload["created_at"]),
            status=str(payload.get("status", "active")),
            macro_id=_optional_str(payload.get("macro_id")),
            problem_ref=(
                ProblemReference.from_dict(problem_ref_payload)
                if isinstance(problem_ref_payload, dict)
                else None
            ),
            output_mode=str(payload.get("output_mode", "step")),
            output_format=str(payload.get("output_format", "txt")),
            output_file=_optional_str(payload.get("output_file")),
            compiled_json_file=_optional_str(payload.get("compiled_json_file")),
            notes=str(payload.get("notes", "")),
        )


@dataclass
class SessionSnapshot:
    snapshot_id: str
    label: str
    created_at: str
    active_adjustment_ids: list[str] = dataclass_field(default_factory=list)
    notes: str = ""

    @classmethod
    def from_dict(cls, payload: dict) -> "SessionSnapshot":
        return cls(
            snapshot_id=str(payload["snapshot_id"]),
            label=str(payload["label"]),
            created_at=str(payload["created_at"]),
            active_adjustment_ids=[
                str(adjustment_id)
                for adjustment_id in payload.get("active_adjustment_ids", [])
            ],
            notes=str(payload.get("notes", "")),
        )


@dataclass
class SessionContextState:
    version: str
    session_id: str
    session_name: str
    agent_name: str
    created_at: str
    updated_at: str
    prompt_history: list[PromptEvent] = dataclass_field(default_factory=list)
    adjustments: list[ContextAdjustment] = dataclass_field(default_factory=list)
    snapshots: list[SessionSnapshot] = dataclass_field(default_factory=list)
    active_adjustment_ids: list[str] = dataclass_field(default_factory=list)
    current_snapshot_id: str | None = None

    @classmethod
    def from_dict(cls, payload: dict) -> "SessionContextState":
        return cls(
            version=str(payload.get("version", "0.1")),
            session_id=str(payload["session_id"]),
            session_name=str(payload["session_name"]),
            agent_name=str(payload.get("agent_name", "unknown")),
            created_at=str(payload["created_at"]),
            updated_at=str(payload["updated_at"]),
            prompt_history=[
                PromptEvent.from_dict(event)
                for event in payload.get("prompt_history", [])
            ],
            adjustments=[
                ContextAdjustment.from_dict(adjustment)
                for adjustment in payload.get("adjustments", [])
            ],
            snapshots=[
                SessionSnapshot.from_dict(snapshot)
                for snapshot in payload.get("snapshots", [])
            ],
            active_adjustment_ids=[
                str(adjustment_id)
                for adjustment_id in payload.get("active_adjustment_ids", [])
            ],
            current_snapshot_id=_optional_str(payload.get("current_snapshot_id")),
        )


def _optional_str(value: object) -> str | None:
    if value is None:
        return None
    return str(value)


def _load_json_object(file_path: Path) -> dict:
    with file_path.open("r", encoding="utf-8") as file_handle:
        payload = json.load(file_handle)

    if not isinstance(payload, dict):
        raise ValueError(f"{file_path} must contain a JSON object")

    return payload


def load_macro_workspace(workspace_file: Path) -> MacroWorkspace:
    workspace = MacroWorkspace.from_dict(_load_json_object(workspace_file))
    validate_macro_workspace(workspace)
    return workspace


def load_session_context_state(session_file: Path) -> SessionContextState:
    session = SessionContextState.from_dict(_load_json_object(session_file))
    validate_session_context_state(session)
    return session


def validate_macro_workspace(workspace: MacroWorkspace) -> None:
    project_ids = {project.project_id for project in workspace.projects}
    macro_ids = {macro.macro_id for macro in workspace.macros}

    if len(project_ids) != len(workspace.projects):
        raise ValueError("Macro workspace contains duplicate project_id values")

    if len(macro_ids) != len(workspace.macros):
        raise ValueError("Macro workspace contains duplicate macro_id values")

    for macro in workspace.macros:
        step_ids = {step.step_id for step in macro.steps}
        condition_ids = {condition.condition_id for condition in macro.conditions}

        if len(step_ids) != len(macro.steps):
            raise ValueError(
                f"Macro '{macro.macro_id}' contains duplicate step_id values"
            )

        if len(condition_ids) != len(macro.conditions):
            raise ValueError(
                f"Macro '{macro.macro_id}' contains duplicate condition_id values"
            )

        if macro.entry_step_id not in step_ids:
            raise ValueError(
                f"Macro '{macro.macro_id}' entry_step_id '{macro.entry_step_id}' does not exist"
            )

        for condition in macro.conditions:
            if condition.kind != "always" and not condition.values:
                raise ValueError(
                    f"Condition '{condition.condition_id}' in macro '{macro.macro_id}' must define values"
                )

        for step in macro.steps:
            if step.next_step_id is not None and step.next_step_id not in step_ids:
                raise ValueError(
                    f"Macro step '{step.step_id}' references unknown next_step_id '{step.next_step_id}'"
                )

            if step.action == "include_problem":
                if step.problem_ref is None:
                    raise ValueError(
                        f"Macro step '{step.step_id}' must define problem_ref for include_problem"
                    )
                if step.problem_ref.project_id not in project_ids:
                    raise ValueError(
                        f"Macro step '{step.step_id}' references unknown project_id '{step.problem_ref.project_id}'"
                    )

            elif step.action == "include_macro":
                if not step.macro_id:
                    raise ValueError(
                        f"Macro step '{step.step_id}' must define macro_id for include_macro"
                    )
                if step.macro_id not in macro_ids:
                    raise ValueError(
                        f"Macro step '{step.step_id}' references unknown macro_id '{step.macro_id}'"
                    )
                if step.macro_id == macro.macro_id:
                    raise ValueError(
                        f"Macro '{macro.macro_id}' cannot include itself directly"
                    )

            elif step.action == "branch":
                if not step.condition_id:
                    raise ValueError(
                        f"Macro step '{step.step_id}' must define condition_id for branch"
                    )
                if step.condition_id not in condition_ids:
                    raise ValueError(
                        f"Macro step '{step.step_id}' references unknown condition_id '{step.condition_id}'"
                    )
                if not step.true_step_id or step.true_step_id not in step_ids:
                    raise ValueError(
                        f"Macro step '{step.step_id}' must define a valid true_step_id"
                    )
                if not step.false_step_id or step.false_step_id not in step_ids:
                    raise ValueError(
                        f"Macro step '{step.step_id}' must define a valid false_step_id"
                    )

            elif step.action == "stop":
                continue

            else:
                raise ValueError(
                    f"Macro step '{step.step_id}' uses unsupported action '{step.action}'"
                )


def validate_session_context_state(session: SessionContextState) -> None:
    adjustment_ids = {adjustment.adjustment_id for adjustment in session.adjustments}
    snapshot_ids = {snapshot.snapshot_id for snapshot in session.snapshots}

    if len(adjustment_ids) != len(session.adjustments):
        raise ValueError("Session state contains duplicate adjustment_id values")

    if len(snapshot_ids) != len(session.snapshots):
        raise ValueError("Session state contains duplicate snapshot_id values")

    for adjustment_id in session.active_adjustment_ids:
        if adjustment_id not in adjustment_ids:
            raise ValueError(
                f"Session state references unknown active adjustment_id '{adjustment_id}'"
            )

    if (
        session.current_snapshot_id is not None
        and session.current_snapshot_id not in snapshot_ids
    ):
        raise ValueError(
            f"Session state references unknown current_snapshot_id '{session.current_snapshot_id}'"
        )

    for adjustment in session.adjustments:
        if adjustment.action == "apply_macro" and not adjustment.macro_id:
            raise ValueError(
                f"Adjustment '{adjustment.adjustment_id}' must define macro_id for apply_macro"
            )

        if adjustment.action == "apply_problem" and adjustment.problem_ref is None:
            raise ValueError(
                f"Adjustment '{adjustment.adjustment_id}' must define problem_ref for apply_problem"
            )

    for snapshot in session.snapshots:
        for adjustment_id in snapshot.active_adjustment_ids:
            if adjustment_id not in adjustment_ids:
                raise ValueError(
                    f"Snapshot '{snapshot.snapshot_id}' references unknown adjustment_id '{adjustment_id}'"
                )

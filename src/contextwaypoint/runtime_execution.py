# Copyright (c) 2026 Daniel Bueno
# SPDX-License-Identifier: MIT
# See LICENSE for the full license text.

from contextlib import ExitStack
from pathlib import Path
from tempfile import TemporaryDirectory

from contextwaypoint.common import PROJECT_ROOT, display_path
from contextwaypoint.compiler import compile_source
from contextwaypoint.project_export import build_project_outputs, slugify
from contextwaypoint.router import format_results_as_text, route_problem
from contextwaypoint.runtime_model import (
    MacroCondition,
    MacroDefinition,
    MacroStep,
    MacroWorkspace,
    ProjectReference,
    load_macro_workspace,
)


def resolve_workspace_path(workspace_file: Path, target: str) -> Path:
    raw_path = Path(target)
    if raw_path.is_absolute():
        return raw_path

    candidate_paths = [
        workspace_file.parent / raw_path,
        PROJECT_ROOT / raw_path,
    ]

    for candidate in candidate_paths:
        if candidate.exists():
            return candidate

    return candidate_paths[0]


def evaluate_condition(condition: MacroCondition, prompt_text: str) -> bool:
    normalized_prompt = prompt_text.lower()

    if condition.kind == "always":
        return True

    if condition.kind == "prompt_contains_any":
        return any(value.lower() in normalized_prompt for value in condition.values)

    if condition.kind == "prompt_contains_all":
        return all(value.lower() in normalized_prompt for value in condition.values)

    raise ValueError(
        f"Unsupported condition kind '{condition.kind}' for condition '{condition.condition_id}'"
    )


def resolved_index_for_project(
    workspace: MacroWorkspace,
    workspace_file: Path,
    project_id: str,
    temp_root: Path,
    compiled_index_cache: dict[str, Path],
) -> Path:
    if project_id in compiled_index_cache:
        return compiled_index_cache[project_id]

    project = workspace.project_by_id().get(project_id)
    if project is None:
        raise ValueError(f"Unknown project_id '{project_id}'")

    index_file = _build_or_resolve_index_file(
        workspace_file,
        project,
        temp_root,
    )
    compiled_index_cache[project_id] = index_file
    return index_file


def _build_or_resolve_index_file(
    workspace_file: Path,
    project: ProjectReference,
    temp_root: Path,
) -> Path:
    compiled_index_path = None
    if project.compiled_index_file:
        compiled_index_path = resolve_workspace_path(
            workspace_file,
            project.compiled_index_file,
        )

    project_file_path = resolve_workspace_path(workspace_file, project.project_file)

    if project_file_path.exists():
        index_file = temp_root / f"{slugify(project.project_id)}.contextIndex.json"

        if project_file_path.suffix.lower() == ".json":
            yaml_dir = temp_root / f"{slugify(project.project_id)}_generated"
            build_project_outputs(
                project_file_path,
                yaml_output_dir=yaml_dir,
                json_output_file=index_file,
            )
        else:
            compile_source(project_file_path, index_file)

        return index_file

    if compiled_index_path is not None and compiled_index_path.exists():
        return compiled_index_path

    raise ValueError(
        f"Could not resolve a project file or compiled index for project '{project.project_id}'"
    )


def preview_macro_execution(
    workspace_file: Path,
    macro_id: str,
    prompt_text: str = "",
) -> str:
    workspace = load_macro_workspace(workspace_file)
    macro = workspace.macro_by_id().get(macro_id)
    if macro is None:
        raise ValueError(f"Macro '{macro_id}' was not found in {display_path(workspace_file)}")

    lines = [
        f"Macro Preview: {macro.name}",
        f"Workspace: {workspace.workspace_name}",
        f"Macro ID: {macro.macro_id}",
        f"Prompt: {prompt_text or '<empty prompt>'}",
        "",
    ]

    with ExitStack() as stack:
        temp_dir = Path(stack.enter_context(TemporaryDirectory(prefix="contextwaypoint-macro-")))
        compiled_index_cache: dict[str, Path] = {}
        _append_macro_preview(
            lines,
            workspace=workspace,
            workspace_file=workspace_file,
            macro=macro,
            prompt_text=prompt_text,
            temp_root=temp_dir,
            compiled_index_cache=compiled_index_cache,
            call_stack=[],
            indent_level=0,
        )

    return "\n".join(lines).strip()


def _append_macro_preview(
    lines: list[str],
    workspace: MacroWorkspace,
    workspace_file: Path,
    macro: MacroDefinition,
    prompt_text: str,
    temp_root: Path,
    compiled_index_cache: dict[str, Path],
    call_stack: list[str],
    indent_level: int,
) -> None:
    if macro.macro_id in call_stack:
        raise ValueError(
            f"Macro recursion detected: {' -> '.join([*call_stack, macro.macro_id])}"
        )

    step_by_id = {step.step_id: step for step in macro.steps}
    condition_by_id = {
        condition.condition_id: condition
        for condition in macro.conditions
    }
    visited_steps: set[str] = set()
    current_step_id = macro.entry_step_id
    indent = "  " * indent_level

    lines.append(f"{indent}Macro: {macro.name}")

    while current_step_id is not None:
        if current_step_id in visited_steps:
            raise ValueError(
                f"Macro '{macro.macro_id}' revisited step '{current_step_id}'."
            )

        visited_steps.add(current_step_id)
        step = step_by_id[current_step_id]
        lines.append(f"{indent}- Step `{step.step_id}` [{step.action}]")

        if step.notes:
            lines.append(f"{indent}  Notes: {step.notes}")

        if step.action == "include_problem":
            if step.problem_ref is None:
                raise ValueError(f"Macro step '{step.step_id}' is missing problem_ref")

            index_file = resolved_index_for_project(
                workspace,
                workspace_file,
                step.problem_ref.project_id,
                temp_root,
                compiled_index_cache,
            )
            routed_results = route_problem(
                step.problem_ref.problem_name,
                mode=step.problem_ref.mode,
                index_file=index_file,
            )
            route_titles = " -> ".join(item["title"] for item in routed_results) or "<no matches>"
            lines.append(
                f"{indent}  Problem: {step.problem_ref.problem_name} "
                f"({step.problem_ref.mode}, {step.problem_ref.output_format})"
            )
            lines.append(f"{indent}  Project: {step.problem_ref.project_id}")
            lines.append(f"{indent}  Route: {route_titles}")
            rendered = format_results_as_text(
                routed_results,
                step.problem_ref.problem_name,
                step.problem_ref.mode,
                route_only=step.problem_ref.route_only,
            )
            lines.append(f"{indent}  Output:")
            for rendered_line in rendered.splitlines() or ["<empty>"]:
                lines.append(f"{indent}    {rendered_line}")
            current_step_id = step.next_step_id
            continue

        if step.action == "include_macro":
            if not step.macro_id:
                raise ValueError(f"Macro step '{step.step_id}' is missing macro_id")

            nested_macro = workspace.macro_by_id().get(step.macro_id)
            if nested_macro is None:
                raise ValueError(
                    f"Macro step '{step.step_id}' references unknown macro '{step.macro_id}'"
                )

            _append_macro_preview(
                lines,
                workspace=workspace,
                workspace_file=workspace_file,
                macro=nested_macro,
                prompt_text=prompt_text,
                temp_root=temp_root,
                compiled_index_cache=compiled_index_cache,
                call_stack=[*call_stack, macro.macro_id],
                indent_level=indent_level + 1,
            )
            current_step_id = step.next_step_id
            continue

        if step.action == "branch":
            if not step.condition_id:
                raise ValueError(f"Macro step '{step.step_id}' is missing condition_id")

            condition = condition_by_id[step.condition_id]
            matched = evaluate_condition(condition, prompt_text)
            next_step_id = step.true_step_id if matched else step.false_step_id
            lines.append(
                f"{indent}  Condition `{condition.condition_id}` -> "
                f"{'true' if matched else 'false'}"
            )
            lines.append(
                f"{indent}  Match rule: {condition.kind} "
                f"({', '.join(condition.values) if condition.values else 'no values'})"
            )
            current_step_id = next_step_id
            continue

        if step.action == "stop":
            lines.append(f"{indent}  Macro complete.")
            break

        raise ValueError(f"Unsupported macro step action '{step.action}'")


def preview_macro_execution_from_file(
    workspace_file: Path,
    macro_id: str,
    prompt_text: str = "",
) -> str:
    return preview_macro_execution(
        workspace_file=workspace_file,
        macro_id=macro_id,
        prompt_text=prompt_text,
    )

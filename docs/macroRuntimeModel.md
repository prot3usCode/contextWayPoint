<!-- Copyright (c) 2026 Daniel Bueno -->
<!-- SPDX-License-Identifier: MIT -->
<!-- See LICENSE for the full license text. -->

# Macro and Runtime Model

This document defines the next layer above the authored problem model.

`contextWayPoint` now has three distinct concerns:

1. authored problem design
2. macro composition
3. runtime context delivery to an agent

That means the future desktop app should not behave like one giant editor. It
should separate those responsibilities cleanly.

## Product Split

### Tab 1: `Authoring Shell`

This tab owns the authored problem units.

It is responsible for:

- source documents
- anchors and selections
- authored nodes
- problem step order
- weights
- keywords
- provenance

This is the layer currently represented by:

- `ProjectState`
- `ProblemDefinition`
- `RouteNode`
- `SelectionAnchor`

The output of this tab is the authored problem layer that the existing
compiler/router can still consume.

### Tab 2: `Macro Creator`

This tab owns composition.

It is responsible for:

- combining multiple problems into one larger flow
- linking to problems from another project or folder
- defining if/else routing rules
- choosing route mode and output defaults
- creating reusable higher-order flows

This is where an operator builds a larger macro like:

- "Insurance application query"
- "Paid but not shipped investigation"
- "Multi-step order explanation"

The output of this tab should be a JSON macro catalog, not authored YAML.

### Runtime Layer

This does not need to be a visible tab in v1, but it needs a real model.

It is responsible for:

- receiving the prompt or selected macro
- resolving which problems/macros to apply
- generating the routed context packet
- tracking applied adjustments
- snapshotting state
- keep / delete / rollback behavior

This is the layer that eventually sits between `contextWayPoint` and Codex or
Claude Code.

## Core Models

### `Problem`

The atomic authored context unit.

In the current repo this maps to:

- `ProblemDefinition`
- its related nodes and anchors inside a `ProjectState`

Problems are created in the `Authoring Shell` and should remain source-backed.

### `MacroWorkspace`

The saved file for the `Macro Creator`.

Recommended ownership:

- known authored projects
- reusable macros
- runtime defaults

Suggested fields:

- `version`
- `workspace_name`
- `created_at`
- `updated_at`
- `projects`
- `macros`
- `runtime_defaults`

### `ProjectReference`

Lets a macro point to an authored project from another folder or repo location.

Suggested fields:

- `project_id`
- `display_name`
- `project_file`
- `compiled_index_file`
- `status`

The important part is that macros should not duplicate problems. They should
reference them.

### `ProblemReference`

Represents one included authored problem inside a macro step.

Suggested fields:

- `project_id`
- `problem_name`
- `mode`
- `output_format`
- `route_only`

This is how one macro pulls in one authored route.

### `MacroDefinition`

Represents one reusable macro.

Suggested fields:

- `macro_id`
- `name`
- `description`
- `entry_step_id`
- `steps`
- `conditions`
- `tags`
- `status`

Macros should be compositional and inspectable.

### `MacroCondition`

Represents a branch rule.

Suggested fields:

- `condition_id`
- `kind`
- `field`
- `operator`
- `values`
- `description`

For v1, conditions should stay simple and deterministic.

Examples:

- prompt contains `refund`
- prompt contains `shipment`
- user explicitly selected macro variant A
- always true

### `MacroStep`

Represents one executable unit inside a macro.

Suggested fields:

- `step_id`
- `action`
- `problem_ref`
- `macro_id`
- `condition_id`
- `next_step_id`
- `true_step_id`
- `false_step_id`
- `notes`

Recommended `action` values for v1:

- `include_problem`
- `include_macro`
- `branch`
- `stop`

This is enough to build real flow logic without inventing a full workflow
language too early.

### `SessionContextState`

Represents the runtime state of a context-adjusted agent session.

Suggested fields:

- `version`
- `session_id`
- `session_name`
- `agent_name`
- `created_at`
- `updated_at`
- `prompt_history`
- `adjustments`
- `snapshots`
- `active_adjustment_ids`
- `current_snapshot_id`

This is the model that makes keep / delete / rollback concrete.

### `ContextAdjustment`

Represents one runtime context change.

Suggested fields:

- `adjustment_id`
- `action`
- `created_at`
- `status`
- `macro_id`
- `problem_ref`
- `output_mode`
- `output_format`
- `output_file`
- `compiled_json_file`
- `notes`

Examples:

- apply a macro
- apply a single problem
- remove a prior adjustment

### `SessionSnapshot`

Represents one rollback point.

Suggested fields:

- `snapshot_id`
- `label`
- `created_at`
- `active_adjustment_ids`
- `notes`

This is the cleanest way to support:

- keep
- delete
- rollback

without losing the runtime history.

## Execute Macro Semantics

The phrase "execute a macro" should mean something very specific.

Recommended v1 semantics:

1. start from a selected macro or a suggested macro
2. evaluate branch conditions against the prompt and session metadata
3. resolve each `include_problem` step into a concrete routed query
4. run the existing router for those problems
5. combine the returned packets in macro order
6. record the application as a `ContextAdjustment`
7. optionally create a `SessionSnapshot`

That is enough to make `contextWayPoint` feel like a context engine rather than
just a compiler.

## Prompt-Time Behavior

The safest first runtime flow is:

1. user enters prompt
2. app suggests one or more macros
3. user confirms one
4. macro executes
5. resulting packet is passed to Codex or Claude

That is better than immediately auto-selecting a macro from freeform text.

The prompt should become macro metadata, not the only source of truth.

## Keep / Delete / Rollback

These actions should operate on runtime adjustments, not on authored problems.

Recommended behavior:

- `keep`
  Leave the current adjustment active in the session.

- `delete`
  Mark an adjustment inactive or removed and rebuild the active context set.

- `rollback`
  Restore the active adjustment list to a prior snapshot.

That model is much easier to reason about than mutating the authored route
state.

## Visuals Versus Structured Editing

Visuals are a good long-term goal, but they should not block the macro model.

Recommended sequence:

### v1

- structured step list
- condition editor
- cross-project references
- read-only route graph preview

### v2

- draggable shapes
- arrows
- nested macro groups
- richer canvas interactions

If the logic model is sound, visuals can be added later without changing the
underlying data contract.

## YAML Versus JSON

The authored problem layer can still export through generated YAML internally,
but the macro and runtime layers should be JSON-first.

That means:

- authored problems: source-backed project state, optionally bridged through
  YAML
- macro workspace: JSON
- session runtime state: JSON
- compiled routing index: JSON

The future app does not need to display the generated YAML pane if it is no
longer useful to the operator.

## Example Files

See:

- `docs/examples/orderFulfillmentProject.example.json`
- `docs/examples/orderFulfillmentMacroWorkspace.example.json`
- `docs/examples/orderFulfillmentSessionState.example.json`

<!-- Copyright (c) 2026 Daniel Bueno -->
<!-- SPDX-License-Identifier: MIT -->
<!-- See LICENSE for the full license text. -->

# contextWayPoint Project Model

This document defines the pre-authoring contract for a future visual authoring
branch.

The current YAML and CLI engine stays intact. The future GUI should sit on top
of a separate project model and export back into the current engine rather than
editing authored YAML directly.

## Intent

The visual authoring layer will eventually need to manage:

- source documents loaded from disk
- user-selected text spans from those documents
- provenance for each selection
- route nodes built from those selections
- route edges between nodes
- export of that authored route into the current YAML or compiled JSON flow

That means the GUI needs a richer source of truth than plain YAML.

## Design Goals

The project model should:

- preserve the current YAML workflow rather than replace it
- make source provenance explicit
- support a simple linear route first
- allow branching and nested macros later
- survive source file moves or edits with detectable failure states
- export deterministic data that can be compiled and routed by the current
  engine

## Proposed Top-Level Objects

### `Project`

The full saved authoring file.

Suggested fields:

- `version`
- `project_name`
- `created_at`
- `updated_at`
- `documents`
- `nodes`
- `edges`
- `problems`
- `export_preferences`

### `SourceDocument`

Represents a source file loaded into the authoring app.

Suggested fields:

- `document_id`
- `display_name`
- `source_path`
- `file_type`
- `sha256`
- `modified_at`
- `size_bytes`
- `status`

`status` is meant to support states like:

- `available`
- `moved`
- `modified`
- `missing`

### `SelectionAnchor`

Represents the exact text evidence selected from a source document.

Suggested fields:

- `anchor_id`
- `document_id`
- `selected_text`
- `char_start`
- `char_end`
- `page_number`
- `context_before`
- `context_after`
- `capture_method`

For text formats, character offsets are the main anchor.

For PDF, page-based anchoring is more realistic in v1, with richer geometry as
future work.

### `RouteNode`

Represents one routed context step created from a captured source selection.

Suggested fields:

- `node_id`
- `title`
- `anchor_id`
- `body_text`
- `notes`
- `problem_assignments`

The key idea is that the node stores the selected evidence and any cleaned
authoring text that should actually be exported.

### `ProblemAssignment`

Represents how one node participates in one problem flow.

Suggested fields:

- `problem_name`
- `step_number`
- `weight`
- `keywords`

This keeps routing metadata separate from the raw source selection.

### `RouteEdge`

Represents the pointer from one node to the next node in a route.

Suggested fields:

- `edge_id`
- `problem_name`
- `from_node_id`
- `to_node_id`
- `label`

For a linear route, this will usually just be one next node.

For later graph behavior, this can support branching.

### `ProblemDefinition`

Represents the route-level object the app is visualizing.

Suggested fields:

- `problem_name`
- `description`
- `entry_node_id`
- `node_ids`
- `status`

This gives the GUI something stable to open, list, and export.

## Relationship To Current YAML

The GUI project file should not replace the current authored YAML flow.

Instead:

1. the GUI project stores selections, nodes, edges, and provenance
2. an exporter generates the authored YAML-like context structure
3. the current compiler and router keep doing the engine work

That separation is important because it lets the current branch stay useful on
its own and keeps the future visual authoring work on a separate branch.

The important product distinction now is:

- `ProjectState` owns authored problems
- the future macro layer composes those problems
- the future runtime layer applies those composed packets to an agent session

That means `ProblemDefinition` should stay the atomic authored unit that the
later `Macro Creator` can reference instead of copying problem content around.

## Minimal Viable Export Contract

The future authoring app only needs to export enough for the current engine:

- `title`
- `uuid`
- `text`
- `problems`
- `entries`

The richer project-only fields stay in the project file and do not need to be
forced into the exported YAML if they are only useful to the GUI.

## First Practical Scope

The first version of the visual authoring branch should assume:

- one project file
- one or more source documents
- text selection into nodes
- one problem flow at a time
- mostly linear edges
- export to the current YAML/JSON engine

Not yet:

- collaborative editing
- nested macro flows
- complex branch logic
- fully generalized graph editing

## Example

See:

- `docs/examples/orderFulfillmentProject.example.json`

That example is deliberately small and is only meant to make the structure
concrete before any GUI code is written.

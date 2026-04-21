<!-- Copyright (c) 2026 Daniel Bueno -->
<!-- SPDX-License-Identifier: MIT -->
<!-- See LICENSE for the full license text. -->

# Layer Ownership

This document answers one practical question:

Which fields belong in the internal project state, which belong in generated
YAML, and which belong in compiled JSON?

That separation matters because the future visualizer should stay transparent
without forcing every GUI concern into the authored YAML.

## Recommended Layers

### 1. Internal Project State

This is the GUI-facing authoring model.

It should own:

- loaded documents
- source paths
- document hashes
- modified timestamps
- selection anchors
- selected text
- anchor offsets or page numbers
- canvas position
- node notes
- visual edges
- route editing state
- unresolved source warnings
- relink state
- UI-only flags

These are important to the visualizer, but most of them do not belong in the
exported routing YAML.

### 2. Generated YAML

This is the live authored artifact the user can inspect.

It should own:

- `title`
- `uuid`
- `text`
- `problems`
- `entries`
- optional exported `origin` block

The YAML should stay understandable to a human and close to the existing engine
contract.

The YAML should not try to store every GUI concern.

### 3. Compiled JSON

This is the queryable routing index.

It should own:

- flattened `uuid`
- `parent_uuid`
- `depth`
- `path`
- `source_order`
- compiled `source_file`
- compiled `source_root`
- copied `origin`
- normalized `problems`

This layer is for deterministic querying and routing, not editing.

## Field Recommendations

### Internal Project State Only

Recommended examples:

- `document_id`
- `source_path`
- `sha256`
- `modified_at`
- `size_bytes`
- `status`
- `anchor_id`
- `char_start`
- `char_end`
- `page_number`
- `context_before`
- `context_after`
- `capture_method`
- `edge_id`
- `from_node_id`
- `to_node_id`
- `notes`
- future canvas coordinates

### Generated YAML

Recommended examples:

- `title`
- `uuid`
- `text`
- `problems[*].problem_name`
- `problems[*].problem_uuid`
- `problems[*].step_number`
- `problems[*].weight`
- `problems[*].keywords`
- `entries`
- `origin.source_path`
- `origin.document_id`
- `origin.anchor_id`
- `origin.selected_text`

The `origin` block is where the YAML can stay transparent about where the
authored text came from without becoming a dump of every GUI field.

### Compiled JSON

Recommended examples:

- `uuid`
- `title`
- `parent_uuid`
- `depth`
- `path`
- `text`
- `source_order`
- `source_file`
- `source_root`
- `origin`
- `problems`

These are the fields the router and audit output should consume.

## Practical Rule

If a field is only useful to:

- file management
- source recovery
- visual layout
- GUI state

then it belongs in internal project state, not in authored YAML.

If a field is useful to:

- explain where the exported text came from
- route the context later
- inspect authored context outside the GUI

then it may belong in generated YAML.

If a field is only useful after compile for:

- sorting
- traversal
- querying
- route rendering

then it belongs in compiled JSON.

## Bottom Line

The future visualizer should edit the internal project state.

The YAML pane should be a live, generated authored artifact.

The JSON index should remain the compiled query layer.

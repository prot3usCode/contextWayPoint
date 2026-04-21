<!-- Copyright (c) 2026 Daniel Bueno -->
<!-- SPDX-License-Identifier: MIT -->
<!-- See LICENSE for the full license text. -->

# Source Anchoring Rules

This document defines how the future visual authoring branch should track text
selected from source documents.

The goal is to make the routed context traceable even after the authoring app
has been closed and reopened.

## Core Principle

A routed node should never only say:

- "this text came from somewhere in a file"

It should say:

- which file it came from
- what exact text was selected
- how that text was located
- whether the source file still matches the captured evidence

## Required Source Fields

Every loaded document should capture:

- absolute `source_path`
- `file_type`
- `sha256`
- `modified_at`
- `size_bytes`

These fields are the minimum needed to detect whether a source file:

- still exists
- moved
- changed content
- changed enough that the anchor should be treated as stale

## Required Anchor Fields

Every text selection should capture:

- `document_id`
- `selected_text`
- `context_before`
- `context_after`
- a file-type-specific location strategy

The surrounding context is important because pure offsets are brittle once a
document changes.

## File-Type Strategies

### Markdown and Plain Text

Primary fields:

- `char_start`
- `char_end`
- `selected_text`
- `context_before`
- `context_after`

This is the easiest and most reliable first target for the authoring app.

### PDF

Practical v1 fields:

- `page_number`
- `selected_text`
- optional `char_start` and `char_end` within extracted page text
- `context_before`
- `context_after`

Future fields can include bounding boxes, but v1 does not need them.

### JSON and YAML

If the viewer supports them later, treat them like text first.

Do not try to make AST-level anchors a v1 requirement.

### DOC and DOCX

These should be deferred until the document-viewer workflow already works well
for text and PDF.

## Document Status Rules

The GUI should surface document state explicitly.

Suggested statuses:

- `available`
- `missing`
- `modified`
- `moved`
- `stale_anchor`

### `available`

The file exists at the stored path and still matches the expected fingerprint.

### `missing`

The file no longer exists at the stored path.

### `modified`

The file exists but its fingerprint or modification metadata changed.

### `moved`

The file was manually relinked to a new path.

### `stale_anchor`

The file is present, but the exact selection cannot be rematched with enough
confidence.

## Relinking Rules

If a file moves, the app should not silently repair the project.

Instead it should:

1. mark the document as unresolved
2. let the user choose a replacement file
3. compare the replacement against the stored fingerprint and selected text
4. either relink the document or keep it unresolved

This is safer than pretending the original evidence is still valid.

## Recommended v1 File Types

The first authoring branch should focus on:

- `.md`
- `.txt`
- `.pdf`

These provide enough coverage to prove the workflow without dragging document
format support into the critical path too early.

Later candidates:

- `.json`
- `.yaml`
- `.doc`
- `.docx`

## Anchor Recovery

If a source file changes, the app can attempt a soft recovery strategy:

1. look for an exact `selected_text` match
2. if more than one match exists, compare `context_before` and `context_after`
3. if confidence is still poor, mark the anchor as stale instead of guessing

The app should prefer surfacing uncertainty over inventing a new anchor.

## Why This Matters

The future authoring app is not just a YAML generator.

It is a source-aware authoring tool.

That means provenance and anchor validity are part of the product, not an
optional extra.

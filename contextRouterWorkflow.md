<!-- Copyright (c) 2026 Daniel Bueno -->
<!-- SPDX-License-Identifier: MIT -->
<!-- See LICENSE for the full license text. -->

# contextWayPoint Workflow

This is the practical runbook for the current codebase. It covers both the
original single-file flow and the newer multi-document route flow.

## What the Project Does

`contextWayPoint` helps convert authored YAML context into problem-specific
packets for an LLM or agent.

Current workflow:

1. write one YAML file or several related YAML files
2. attach problem flows to sections
3. validate those files together
4. compile them into one flat JSON index
5. route the entries for one problem
6. render either a full packet or a route map

Current routing modes:

- `step`
- `weight`
- `yaml`
- `keyword`

Current output formats:

- `txt`
- `md`
- `json`

## Project Root

Run commands from:

`contextWaypoint`

## 1. Set Up Python

### macOS or Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install PyYAML
```

### Windows 11

```powershell
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install PyYAML
```

If PowerShell activation is blocked, run the venv Python directly:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install PyYAML
.\.venv\Scripts\python.exe .\src\contextValidator.py --input-dir .\Formats
.\.venv\Scripts\python.exe .\src\contextCompiler.py --input-dir .\Formats
.\.venv\Scripts\python.exe .\src\contextRouter.py "Order Fulfillment Investigation" --mode step --format md
```

What you need:

- Python 3.10+
- `PyYAML`

What you do not need:

- Docker
- Node
- Postgres
- an API key

## 2. Author the Source YAML

You can author one file or many files.

The repository includes:

- `Formats/sampleBuildFailureContext.yaml`
  Single-file example.
- `Formats/orderFulfillmentContext.yaml`
- `Formats/postgresPatterns.yaml`
- `Formats/paymentRules.yaml`
- `Formats/inventoryRules.yaml`
- `Formats/shipmentRules.yaml`
  Multi-document example.

Each entry can contain:

- `title`
- `uuid`
- `text`
- `problems`
- `entries`

Minimal shape:

```yaml
title: Root Title
uuid: root_uuid
problems:
  - problem_name: Example Investigation
    problem_uuid:
    step_number: 1
    weight: 80
    keywords:
      - payment

text: >
  Root context text.

entries:
  - title: Child Section
    uuid: child_uuid
    text: >
      Child context text.
```

Notes:

- every entry must have a `title`
- every entry must have a `uuid`
- every entry must have non-blank `text`
- blank `problem_uuid` values are allowed while drafting
- duplicate entry UUIDs and duplicate problem UUIDs are checked across documents

## 3. Validate the YAML

Single file:

```bash
python src/contextValidator.py --input Formats/sampleBuildFailureContext.yaml
```

Directory of files:

```bash
python src/contextValidator.py --input-dir Formats
```

Validation catches:

- missing entry `title`
- missing entry `uuid`
- blank entry `text`
- duplicate entry `uuid`
- missing problem `problem_name`
- missing or invalid `step_number`
- missing or invalid `weight`
- blank keywords
- duplicate `problem_uuid`
- malformed `problems` or `entries` lists

In directory mode, UUID collisions are checked across files, not only inside one
document.

## 4. Compile to the Flat JSON Index

Single file:

```bash
python src/contextCompiler.py --input Formats/sampleBuildFailureContext.yaml
```

Directory of files:

```bash
python src/contextCompiler.py --input-dir Formats
```

Both flows write:

`output/contextIndex.json`

The compiled entries include:

- `uuid`
- `title`
- `parent_uuid`
- `depth`
- `path`
- `text`
- `problems`
- `source_order`
- `source_file`
- `source_root`

The directory flow builds one global index, so a route can move from one YAML
document to another and later return to the original source file.

If you want a different output path:

```bash
python src/contextCompiler.py --input-dir Formats --output output/myIndex.json
```

## 5. Optionally Fill Blank Problem UUIDs

Blank `problem_uuid` values are fine while drafting, but stable UUIDs are better
for diffs and tests.

Use the existing single-file fill flow:

```bash
python src/contextCompiler.py --input Formats/sampleBuildFailureContext.yaml --fill-uuids --output-yaml output/sampleBuildFailureContextFilled.yaml
```

Or write directly into the source file:

```bash
python src/contextCompiler.py --input Formats/sampleBuildFailureContext.yaml --fill-uuids --in-place
```

`--fill-uuids` currently works with `--input`, not `--input-dir`.

## 6. Route a Context Packet

Step mode:

```bash
python src/contextRouter.py "Order Fulfillment Investigation" --mode step --format md
```

Weight mode:

```bash
python src/contextRouter.py "Order Fulfillment Investigation" --mode weight --format txt
```

Raw compiled order:

```bash
python src/contextRouter.py "Order Fulfillment Investigation" --mode yaml --format txt
```

Keyword mode:

```bash
python src/contextRouter.py "Order Fulfillment Investigation" --mode keyword --keywords payment failed shipment --format txt
```

Current behavior by mode:

- `step`: sort by `step_number`, then `weight`, then depth and source order
- `weight`: sort by `weight`, then `step_number`, then depth and source order
- `yaml`: preserve compiled traversal order
- `keyword`: sort by keyword overlap first, then `step_number`, then `weight`

Keyword mode only scores entries already matched to the selected problem.

## 7. Print Only the Route Map

If you want proof of the route without the full packet text:

```bash
python src/contextRouter.py "Order Fulfillment Investigation" --mode step --route-only --format txt
```

This prints the ordered route with:

- route position
- step number
- source file
- authored path

## 8. Output Formats

Supported formats:

- `txt`
- `md`
- `json`

Current behavior:

- `txt` writes a plain-text packet or route map with source metadata
- `md` writes headings plus source metadata for README/demo usage
- `json` writes a structured payload for downstream tools

The router always prints the result to the terminal and writes a file under:

`output/contextPackets/`

## 9. RAG Comparison Demo

The repository includes:

`demos/rag_vs_contextwaypoint/`

Files:

- `problem.md`
- `unordered_retrieved_context.md`
- `routed_context_packet.md`
- `explanation.md`

Use this when you need to explain the difference between:

- relevant but unordered retrieval
- an authored, traceable context route

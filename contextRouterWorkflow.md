<!-- Copyright (c) 2026 Daniel Bueno -->
<!-- SPDX-License-Identifier: MIT -->
<!-- See LICENSE for the full license text. -->

# contextWayPoint Workflow

This document is the practical runbook for the current codebase. It covers the
full path from authoring a context file to generating a routed context packet.

## What the Project Does

`contextWayPoint` exists to make authored context easier for an LLM or agent to
consume correctly.

Current workflow:

1. write a nested YAML context outline
2. attach problem flows to sections
3. validate the structure
4. compile it into flat JSON
5. route a packet for one problem
6. render that packet as `txt`, `md`, or `json`

Current routing modes:

- `step`
- `weight`
- `yaml`

Not implemented yet:

- keyword routing
- tests
- installable packaging
- evals

## Project Root

Run commands from the project root folder:

`contextWaypoint`

## 1. Set Up Python

### macOS or Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install PyYAML
```

### Windows 11

For a locked-down work machine, the safest path is still:

1. use an already-approved Python install if you have one
2. otherwise ask IT for Python 3.10+
3. avoid trying to bypass endpoint or execution policy controls

From PowerShell in the project root:

```powershell
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install PyYAML
```

If PowerShell activation is blocked, run the venv Python directly:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install PyYAML
.\.venv\Scripts\python.exe .\src\contextValidator.py --input .\Formats\sampleBuildFailureContext.yaml
.\.venv\Scripts\python.exe .\src\contextCompiler.py --input .\Formats\sampleBuildFailureContext.yaml
.\.venv\Scripts\python.exe .\src\contextRouter.py "Order Flow Issue Triage" --mode step --format txt
```

What you need installed:

- Python 3.10+
- `PyYAML`

What you do not need:

- Docker
- a VM
- Node
- Postgres
- an API key

## 2. Write the Source YAML

You can author a context file anywhere, but the repository includes one sample:

`Formats/sampleBuildFailureContext.yaml`

That sample currently models troubleshooting around an order workflow described in:

`Database/howToSetUpTestPostgres.md`

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
  - problem_name: Order Flow Issue Triage
    problem_uuid:
    step_number: 1
    weight: 80
    keywords:
      - orders

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
- blank `problem_uuid` values are allowed while drafting
- if you do not fill `problem_uuid` values permanently, compile will generate them

## 3. Validate the YAML

Run:

```bash
python src/contextValidator.py --input Formats/sampleBuildFailureContext.yaml
```

Validation currently checks:

- missing entry `title`
- missing entry `uuid`
- blank entry `text`
- duplicate entry `uuid`
- missing problem `problem_name`
- missing or invalid `step_number`
- missing or invalid `weight`
- duplicate `problem_uuid`

If validation fails, fix the YAML first.

## 4. Compile to the Flat JSON Index

Run:

```bash
python src/contextCompiler.py --input Formats/sampleBuildFailureContext.yaml
```

This writes:

`output/contextIndex.json`

What the compiler preserves:

- entry `uuid`
- title
- parent/child relationship
- depth
- full path
- text
- problem metadata
- authored traversal order as `source_order`

If you want a different output path:

```bash
python src/contextCompiler.py --input path/to/myFile.yaml --output output/myIndex.json
```

## 5. Optionally Fill Blank Problem UUIDs

Blank `problem_uuid` values are fine for early drafting, but they are not stable
identifiers until you save them somewhere.

If you want stable UUIDs across future compiles, use:

```bash
python src/contextCompiler.py --input Formats/sampleBuildFailureContext.yaml --fill-uuids --output-yaml output/sampleBuildFailureContextFilled.yaml
```

That flow:

1. loads the YAML
2. fills blank `problem_uuid` values
3. writes a filled YAML file
4. compiles the same structure to `output/contextIndex.json`

If you really want to modify the source file directly:

```bash
python src/contextCompiler.py --input Formats/sampleBuildFailureContext.yaml --fill-uuids --in-place
```

Use `--in-place` carefully.

Stable `problem_uuid` values help with:

- cleaner Git diffs
- comparing compiled outputs over time
- downstream references
- future tests

## 6. Route a Context Packet

Run:

```bash
python src/contextRouter.py "Order Flow Issue Triage" --mode step --format txt
```

Supported modes:

- `step`
- `weight`
- `yaml`

Current behavior by mode:

- `step` sorts by `step_number`, then `weight`, then depth, then source order
- `weight` sorts by `weight`, then `step_number`, then depth, then source order
- `yaml` preserves authored traversal order

Supported formats:

- `txt`
- `md`
- `json`

Current behavior by format:

- `txt` writes only the ordered text blocks
- `md` writes a richer packet with headings and metadata
- `json` writes a structured payload for another program to consume

## 7. Output Files

The router prints the routed packet to the terminal and writes a file under:

`output/contextPackets/`

Example outputs:

- `output/contextPackets/orderFlowIssueTriageStep.txt`
- `output/contextPackets/orderFlowIssueTriageStep.md`
- `output/contextPackets/orderFlowIssueTriageStep.json`

The compiler output is:

- `output/contextIndex.json`

## 8. Full End-to-End Example

From the project root:

```bash
source .venv/bin/activate
python src/contextValidator.py --input Formats/sampleBuildFailureContext.yaml
python src/contextCompiler.py --input Formats/sampleBuildFailureContext.yaml
python src/contextRouter.py "Order Flow Issue Triage" --mode step --format txt
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
python .\src\contextValidator.py --input .\Formats\sampleBuildFailureContext.yaml
python .\src\contextCompiler.py --input .\Formats\sampleBuildFailureContext.yaml
python .\src\contextRouter.py "Order Flow Issue Triage" --mode step --format txt
```

## 9. Current Demo Shape

The sample file is meant to show one context tree supporting multiple related
problem flows.

Included sample problems:

- `Order Flow Issue Triage`
- `Shipment Delay Investigation`
- `Payment Failure Investigation`
- `Inventory Shortage Investigation`

That lets the same authored tree produce different packets depending on the
problem name and routing mode.

## 10. Current Gaps and Next Steps

The most useful next steps for the repo are:

- add keyword routing
- add a small focused test suite
- improve packaging and CLI ergonomics
- add a stronger demo comparing broad prompts to routed packets
- add one real model integration later

Good first tests would be:

- compiler preserves hierarchy metadata
- router returns the expected step order
- weight mode sorts correctly
- blank UUIDs are generated or filled correctly
- packet output stays stable when source UUIDs are stable

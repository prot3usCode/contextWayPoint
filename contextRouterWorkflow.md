<!-- Copyright (c) 2026 Daniel Bueno -->
<!-- SPDX-License-Identifier: MIT -->
<!-- See LICENSE for the full license text. -->

# Context Router Workflow

This document describes the full process from writing the source YAML file to generating routed output text.

## Project Location

Run commands from the project root folder:

`contextWaypoint`

## 1. Set Up the Environment

### macOS or Linux

From the project root, create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install PyYAML
```

### Windows 11

If this is a corporate Windows 11 machine, the safest path is:

1. Use an already-approved Python install if your company provides one.
2. If Python is not already installed, request an approved install of Python 3.10+ from IT.
3. Avoid trying to bypass local admin, endpoint protection, or software policy controls.

From PowerShell in the project root:

```powershell
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install PyYAML
```

If PowerShell blocks script activation because of execution policy, you can run the venv Python directly without activating it:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install PyYAML
.\.venv\Scripts\python.exe .\src\contextCompiler.py
.\.venv\Scripts\python.exe .\src\contextRouter.py "Order Flow Issue Triage" --mode step --format txt
```

What this installs:

- Python 3.10+
- `PyYAML`

### If `pip install` Is Blocked at Work

Common corporate environments block direct package downloads. If that happens, use one of these approved paths:

1. Ask IT whether Python packages can be installed from an internal package mirror.
2. Ask IT to provide or approve the `PyYAML` wheel file for your Python version.
3. Install from a locally approved wheel instead of the public internet.

Example local wheel install:

```powershell
python -m pip install .\wheels\PyYAML-6.0.3-cp314-cp314-win_amd64.whl
```

Important:

- Once Python is installed, creating `.venv` usually does not require admin rights.
- This project does not require Docker, a VM, Node, Postgres, or an API key.
- The only non-stdlib dependency right now is `PyYAML`.

## 2. Write the Source YAML File

Write your own local context source file anywhere you want. It does not need to live in the repository.

Included example file:

`Formats/sampleBuildFailureContext.yaml`

Each entry can contain:

- `title`
- `uuid`
- `text`
- `problems`
- `entries`

Minimal example:

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

- Every entry must have a `title`.
- Every entry must have a `uuid`.
- If `problem_uuid` is blank, the compiler can still compile, but it will generate a UUID at compile time unless you fill and save one permanently.

## 3. Validate the YAML File

Run:

```bash
python src/contextValidator.py --input Formats/sampleBuildFailureContext.yaml
```

What validation checks today:

- missing entry `title`
- missing entry `uuid`
- blank entry `text`
- duplicate entry `uuid`
- missing problem `problem_name`
- missing or invalid `step_number`
- missing or invalid `weight`
- duplicate `problem_uuid`

If validation fails, fix the YAML first before compiling.

## 4. Compile the YAML into the Queryable JSON Index

Run:

```bash
python src/contextCompiler.py --input Formats/sampleBuildFailureContext.yaml
```

This writes:

`output/contextIndex.json`

If you want to compile a different input file:

```bash
python src/contextCompiler.py --input path/to/myFile.yaml
```

## 5. Optionally Fill Blank Problem UUIDs Permanently

If you are still drafting, blank `problem_uuid` values are okay. The compiler will generate them during compile.

If you want stable UUIDs that do not change between compiles, fill them into YAML permanently.

Recommended safe option:

```bash
python src/contextCompiler.py --input Formats/sampleBuildFailureContext.yaml --fill-uuids --output-yaml output/sampleBuildFailureContextFilled.yaml
```

This does four things:

1. loads the source YAML
2. fills blank `problem_uuid` values
3. writes a filled YAML copy
4. compiles the same content into `output/contextIndex.json`

You can also write UUIDs back into the source file directly:

```bash
python src/contextCompiler.py --input Formats/sampleBuildFailureContext.yaml --fill-uuids --in-place
```

Use `--in-place` carefully, since it changes the original file.

Stable UUIDs are useful for:

- cleaner Git diffs
- comparing compiled JSON between runs
- tests
- later references to the same problem mapping

## 6. Run the Router Script

Run:

```bash
python src/contextRouter.py "Order Flow Issue Triage" --mode step --format txt
```

Supported modes:

- `step`: sort by step first
- `weight`: sort by weight first
- `yaml`: preserve raw YAML order

Supported formats:

- `txt`: plain text context only
- `md`: Markdown with headings and metadata
- `json`: machine-readable structured output

## 7. Get the Output

The router prints the routed result to the terminal and writes it to a file in `output/contextPackets/`.

It does two things:

- prints the routed output to the terminal
- writes the same routed output to a file in `output/contextPackets/`

Example output file:

`output/contextPackets/orderFlowIssueTriageStep.txt`

Examples:

```bash
python src/contextRouter.py "Order Flow Issue Triage" --mode step --format txt
python src/contextRouter.py "Order Flow Issue Triage" --mode step --format md
python src/contextRouter.py "Order Flow Issue Triage" --mode step --format json
```

## Full End-to-End Command Flow

From the project root:

```bash
source .venv/bin/activate
python src/contextValidator.py --input Formats/sampleBuildFailureContext.yaml
python src/contextCompiler.py --input Formats/sampleBuildFailureContext.yaml
python src/contextRouter.py "Order Flow Issue Triage" --mode step --format txt
```

Windows PowerShell version:

```powershell
.venv\Scripts\Activate.ps1
python .\src\contextValidator.py --input .\Formats\sampleBuildFailureContext.yaml
python .\src\contextCompiler.py --input .\Formats\sampleBuildFailureContext.yaml
python .\src\contextRouter.py "Order Flow Issue Triage" --mode step --format txt
```

## Output Files

Compiled JSON index:

`output/contextIndex.json`

Routed text packet:

`output/contextPackets/orderFlowIssueTriageStep.txt`

## Important Behavior Notes

- `step` mode does not guarantee strict YAML source order if multiple items share the same step and have different weights.
- If you want exact authored order, use:

```bash
python src/contextRouter.py "Order Flow Issue Triage" --mode yaml
```

- If `problem_uuid` fields remain blank in the source YAML, new UUIDs are generated each time you recompile.
- If you want stable `problem_uuid` values, use `--fill-uuids` and save the filled YAML output.
- Duplicate `problem_uuid` values are now treated as validation errors.

<!-- Copyright (c) 2026 Daniel Bueno -->
<!-- SPDX-License-Identifier: MIT -->
<!-- See LICENSE for the full license text. -->

# contextWayPoint Workflow

This document is the practical runbook for the current packaged version of
`contextWayPoint`.

## Main Path

The simplest current path is:

1. install the package in editable mode
2. validate a file or directory of YAML
3. compile the flattened JSON index
4. route a context packet or route map
5. run the demo when you want to show the project claim clearly

## 1. Install the CLI

### macOS or Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

### Windows 11

```powershell
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e .
```

If PowerShell activation is blocked:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\contextwaypoint.exe --help
```

What this installs:

- Python 3.10+
- `PyYAML`
- the `contextwaypoint` CLI entrypoint

## 2. Validate Authored Context

Validate one file:

```bash
contextwaypoint validate Formats/sampleBuildFailureContext.yaml
```

Validate a directory together:

```bash
contextwaypoint validate Formats
```

Validation checks:

- missing entry `title`
- missing entry `uuid`
- blank entry `text`
- duplicate entry `uuid`
- missing problem `problem_name`
- missing or invalid `step_number`
- missing or invalid `weight`
- duplicate `problem_uuid`

## 3. Compile the JSON Index

Compile one file:

```bash
contextwaypoint compile Formats/sampleBuildFailureContext.yaml --out output/contextIndex.json
```

Compile a directory of YAML files into one global index:

```bash
contextwaypoint compile Formats --out output/contextIndex.json
```

The compiled output is:

- `output/contextIndex.json`

The compiled index preserves:

- entry `uuid`
- parent/child relationship
- depth
- full path
- authored traversal order as `source_order`
- `source_file`
- `source_root`

## 4. Fill Blank Problem UUIDs

Fill one file to a new output file:

```bash
contextwaypoint fill-uuids Formats/sampleBuildFailureContext.yaml --out output/sampleBuildFailureContextFilled.yaml
```

Fill a whole directory to a new directory:

```bash
contextwaypoint fill-uuids Formats --out filledFormats
```

Or write back in place:

```bash
contextwaypoint fill-uuids Formats --in-place
```

Stable `problem_uuid` values help with:

- cleaner Git diffs
- deterministic comparisons across compiles
- later references to the same route
- stronger tests

## 5. Route a Context Packet

Render a full packet:

```bash
contextwaypoint route "Order Fulfillment Investigation" --mode step --format md
```

Render only the route map:

```bash
contextwaypoint route-map "Order Fulfillment Investigation"
```

Supported modes:

- `step`
- `weight`
- `yaml`
- `keyword`

Keyword mode requires explicit keywords:

```bash
contextwaypoint route "Order Fulfillment Investigation" --mode keyword --keywords payment shipment inventory --format txt
```

Supported formats:

- `txt`
- `md`
- `json`

Output files are written under:

- `output/contextPackets/`

## 6. Run the Demo

The best current one-command explanation of the repository is:

```bash
contextwaypoint demo order-4-not-shipped
```

This compiles the multi-document order-fulfillment context, generates a route
map, generates a routed packet, and writes a demo report under:

- `output/demos/order-4-not-shipped/`

## 7. Run the Tests

Run the engine test suite with:

```bash
python -m unittest discover -s tests
```

## 8. Legacy Script Entry Points

The old script commands still work:

```bash
python src/contextValidator.py --input-dir Formats
python src/contextCompiler.py --input-dir Formats
python src/contextRouter.py "Order Fulfillment Investigation" --mode step --format md
```

Those wrappers now call the packaged implementation under `src/contextwaypoint/`.

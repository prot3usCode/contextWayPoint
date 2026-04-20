<!-- Copyright (c) 2026 Daniel Bueno -->
<!-- SPDX-License-Identifier: MIT -->
<!-- See LICENSE for the full license text. -->

# contextWayPoint

`contextWayPoint` is a lightweight compiler and router for authored LLM context.

The project is built around a simple idea: LLMs often fail not because they cannot
reason, but because they receive context that is too broad, unordered, or
semantically fuzzy. `contextWayPoint` lets you author context as a nested outline,
map sections to specific problem flows, compile that structure into flat JSON, and
route smaller context packets in a deterministic order.

## The Problem

When a model is given too much raw documentation, it tends to:

- pull in irrelevant details
- miss the intended workflow order
- blend unrelated concepts together
- produce weaker SQL, analysis, or troubleshooting steps

`contextWayPoint` is meant to narrow that gap by turning authored context into
problem-specific packets that are easier for an LLM or agent to use correctly.

## The Approach

The current workflow is:

1. Author context as a nested YAML outline.
2. Attach one or more `problems` to each section.
3. Validate the file for missing fields and duplicate UUIDs.
4. Compile the outline into a flattened JSON index.
5. Route a context packet for a single problem in a chosen order.
6. Render that packet as `txt`, `md`, or `json`.

## Current Feature Set

What the code supports today:

- validate YAML-shaped context files before compile
- compile nested context into flat JSON while preserving hierarchy metadata
- fill blank `problem_uuid` values and write a filled YAML copy
- route context by `step`, `weight`, or authored YAML traversal order
- render routed packets as plain text, Markdown, or JSON
- support multiple problem paths through the same context tree

What is not implemented yet:

- keyword routing mode
- automated tests
- Python packaging and installable CLI entry points
- evals or output quality benchmarking
- model API integration

## Why I Built It

I work as a data engineer and noticed that LLMs often fail not because they
cannot reason, but because they receive the wrong context. I built
`contextWayPoint` as a lightweight compiler/router for authored context. It lets
teams define problem-specific context outlines and produce context packets
ordered by step, weight, or authored traversal order.

## Included Demo

The repository currently ships with a sample troubleshooting workflow built
around an order, payment, inventory, and shipment data model.

Relevant files:

- `Formats/sampleBuildFailureContext.yaml`
- `Database/howToSetUpTestPostgres.md`

The sample filename is older than the current demo content, but the example
itself is about order-flow issue triage rather than build failures.

Example problem names in the sample:

- `Order Flow Issue Triage`
- `Shipment Delay Investigation`
- `Payment Failure Investigation`
- `Inventory Shortage Investigation`

## Quick Start

From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install PyYAML
python src/contextValidator.py --input Formats/sampleBuildFailureContext.yaml
python src/contextCompiler.py --input Formats/sampleBuildFailureContext.yaml
python src/contextRouter.py "Order Flow Issue Triage" --mode step --format txt
```

This produces:

- `output/contextIndex.json`
- `output/contextPackets/orderFlowIssueTriageStep.txt`

## Example Output

Running:

```bash
python src/contextRouter.py "Order Flow Issue Triage" --mode step --format txt
```

produces a text packet shaped like:

```text
This context covers how to troubleshoot issues in the sample order data flow...

Start with a single order and build a joined view across orders, customers,
payments, and shipments...

Check payments next...
```

The same routed packet can also be written as:

- `--format txt` for copy/paste and simple prompts
- `--format md` for docs and richer prompt structure
- `--format json` for programmatic consumers

## Main Scripts

- `src/contextValidator.py`
- `src/contextCompiler.py`
- `src/contextRouter.py`
- `src/queryContext.py`

## Current Routing Modes

- `step`: sort by `step_number`, then `weight`, then depth and source order
- `weight`: sort by `weight`, then `step_number`, then depth and source order
- `yaml`: preserve raw authored traversal order

If you want stable `problem_uuid` values across compiles, use
`--fill-uuids` and save a filled YAML file. Otherwise blank `problem_uuid`
values are generated during compile.

## Roadmap

The next useful improvements are:

- add keyword-based routing
- add 3 to 5 focused tests for compiler and router behavior
- improve CLI ergonomics and packaging
- add simple evals for packet quality
- add one downstream integration with a model API
- build a stronger end-to-end demo showing baseline prompts versus routed context

The test cases worth adding first are:

- compiler preserves hierarchy metadata
- step mode returns the expected order
- weight mode sorts correctly
- blank UUIDs are generated or filled correctly
- packet output is stable when source UUIDs are stable

## Documentation

- `contextRouterWorkflow.md` walks through the setup and execution flow in more detail.

## License

MIT. See `LICENSE`.

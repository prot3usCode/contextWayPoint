<!-- Copyright (c) 2026 Daniel Bueno -->
<!-- SPDX-License-Identifier: MIT -->
<!-- See LICENSE for the full license text. -->

# contextWayPoint

`contextWayPoint` is a lightweight compiler and router for authored LLM context.

The core idea is simple:

- RAG retrieves relevant chunks.
- `contextWayPoint` defines and executes an authored route through context.

That route can now span multiple YAML documents, preserve source traceability,
and render either a full packet or a route map.

## Why It Exists

LLMs often underperform because the context they receive is:

- too broad
- out of order
- mixed across unrelated workflows
- hard to trace back to a source

`contextWayPoint` narrows that problem by turning authored context into
problem-specific packets with explicit step order, source metadata, and optional
keyword scoring.

## Current Feature Set

What the code supports today:

- validate one YAML file or a directory of YAML files together
- catch duplicate entry UUIDs across documents
- catch duplicate `problem_uuid` values across documents
- compile one file or many files into one global `output/contextIndex.json`
- preserve hierarchy metadata, traversal order, `source_file`, and `source_root`
- fill blank `problem_uuid` values for a single input file and write a filled YAML copy
- route context by `step`, `weight`, raw authored order, or `keyword`
- render source-aware packets as `txt`, `md`, or `json`
- render `--route-only` output to show the problem path without full text
- support routes that leave one document and return to it later

Still missing:

- automated tests
- installable packaging / CLI entry points
- evals and packet quality benchmarking
- downstream model API integration

## Included Examples

The repository includes two example shapes:

- `Formats/sampleBuildFailureContext.yaml`
  Single-file sample for legacy order-flow issue triage.
- `Formats/orderFulfillmentContext.yaml`
- `Formats/postgresPatterns.yaml`
- `Formats/paymentRules.yaml`
- `Formats/inventoryRules.yaml`
- `Formats/shipmentRules.yaml`
  Multi-document sample for `Order Fulfillment Investigation`.

The multi-document example is the clearest demonstration of the current thesis:
one route can move through several authored files and then return to the first
document for the final explanation step.

There is also a comparison demo under:

- `demos/rag_vs_contextwaypoint/`

## Quick Start

From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install PyYAML
python src/contextValidator.py --input-dir Formats
python src/contextCompiler.py --input-dir Formats
python src/contextRouter.py "Order Fulfillment Investigation" --mode step --format md
python src/contextRouter.py "Order Fulfillment Investigation" --mode step --route-only --format txt
python src/contextRouter.py "Order Fulfillment Investigation" --mode keyword --keywords payment failed shipment --format txt
```

This produces:

- `output/contextIndex.json`
- `output/contextPackets/orderFulfillmentInvestigationStep.md`
- `output/contextPackets/orderFulfillmentInvestigationStepRoute.txt`
- `output/contextPackets/orderFulfillmentInvestigationKeyword.txt`

If you want the original single-file workflow instead:

```bash
python src/contextValidator.py --input Formats/sampleBuildFailureContext.yaml
python src/contextCompiler.py --input Formats/sampleBuildFailureContext.yaml
python src/contextRouter.py "Order Flow Issue Triage" --mode step --format txt
```

## Routing Modes

- `step`: sort by `step_number`, then `weight`, then depth and source order
- `weight`: sort by `weight`, then `step_number`, then depth and source order
- `yaml`: preserve compiled traversal order
- `keyword`: sort by keyword overlap first, then `step_number`, then `weight`

Keyword mode is intentionally simple:

- it only considers entries already matched to the selected `problem_name`
- it scores token overlap against routed entry keywords, path, title, and text
- it does not replace authored routes; it adds a search-like ordering option

## Output Shapes

`contextWayPoint` now renders source-aware packets. A routed Markdown packet looks
like:

```md
## Step 3 - Payment Check

Source: `Formats/paymentRules.yaml`
Path: `Payment Rules > Payment Check`
Weight: `95`

Check the latest payment for the order...
```

If you only want the route map:

```bash
python src/contextRouter.py "Order Fulfillment Investigation" --mode step --route-only
```

That prints the ordered path without the full context body.

For machine consumers, `--format json` includes:

- route position
- source metadata
- path
- problem metadata
- text when `--route-only` is not used

## Stable UUIDs

Blank `problem_uuid` values are allowed while drafting. If you want stable values
saved back to a YAML file, use the existing single-file fill flow:

```bash
python src/contextCompiler.py --input Formats/sampleBuildFailureContext.yaml --fill-uuids --output-yaml output/sampleBuildFailureContextFilled.yaml
```

Or write them directly into the source file:

```bash
python src/contextCompiler.py --input Formats/sampleBuildFailureContext.yaml --fill-uuids --in-place
```

`--fill-uuids` currently applies only to `--input`, not `--input-dir`.

## RAG Comparison Demo

Use the demo folder to explain the difference between unordered retrieval and an
authored route:

- `demos/rag_vs_contextwaypoint/problem.md`
- `demos/rag_vs_contextwaypoint/unordered_retrieved_context.md`
- `demos/rag_vs_contextwaypoint/routed_context_packet.md`
- `demos/rag_vs_contextwaypoint/explanation.md`

The point is not that retrieval is bad. The point is that retrieval alone does
not define the intended sequence through domain context.

## Main Scripts

- `src/contextValidator.py`
- `src/contextCompiler.py`
- `src/contextRouter.py`
- `src/queryContext.py`

## Documentation

- `contextRouterWorkflow.md` is the practical runbook.
- `projectRepoExplanation.txt` is the plain-text repo overview.

## License

MIT. See `LICENSE`.

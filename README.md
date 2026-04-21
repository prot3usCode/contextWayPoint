<!-- Copyright (c) 2026 Daniel Bueno -->
<!-- SPDX-License-Identifier: MIT -->
<!-- See LICENSE for the full license text. -->

# contextWayPoint

`contextWayPoint` is a lightweight compiler and router for authored LLM context.

The claim is simple:

- RAG retrieves relevant chunks.
- `contextWayPoint` defines and executes an authored route through context.

That route can span multiple YAML documents, preserve source traceability, and
render either a full context packet or only the route map.

## Why It Exists

LLMs often fail because the context they receive is:

- too broad
- out of order
- mixed across unrelated workflows
- hard to trace back to a source

`contextWayPoint` is for problems where the missing piece is not just
retrieval. The missing piece is the intended path through the context.

## What It Does Today

- validate one YAML file or a directory of YAML files together
- catch duplicate entry UUIDs across documents
- catch duplicate `problem_uuid` values across documents
- compile one file or many files into one flattened JSON index
- preserve hierarchy metadata, traversal order, `source_file`, and `source_root`
- fill blank `problem_uuid` values for one file or a directory tree
- route context by `step`, `weight`, raw authored order, or `keyword`
- render source-aware packets as `txt`, `md`, or `json`
- render `route-map` output without the full context body
- run a one-command demo that compares unordered retrieval to an authored route

## Install

From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

After that, use the installable CLI:

```bash
contextwaypoint --help
```

## One-Command Demo

The main milestone for the repo right now is:

```bash
contextwaypoint demo order-4-not-shipped
```

That command:

1. compiles the multi-document order-fulfillment example
2. generates a route map
3. generates a routed context packet
4. prints a side-by-side demo showing why ordered authored context is different
   from unordered retrieval

It also writes output under:

- `output/demos/order-4-not-shipped/`

## CLI Commands

Validate one file or a directory:

```bash
contextwaypoint validate Formats
```

Compile a global index:

```bash
contextwaypoint compile Formats --out output/contextIndex.json
```

Route a full context packet:

```bash
contextwaypoint route "Order Fulfillment Investigation" --mode step --format md
```

Render only the route map:

```bash
contextwaypoint route-map "Order Fulfillment Investigation"
```

Fill blank UUIDs to a new directory:

```bash
contextwaypoint fill-uuids Formats --out filledFormats
```

## Demo Context

The clearest multi-document example uses:

- `Formats/orderFulfillmentContext.yaml`
- `Formats/postgresPatterns.yaml`
- `Formats/paymentRules.yaml`
- `Formats/inventoryRules.yaml`
- `Formats/shipmentRules.yaml`

This route is used for:

- `Order Fulfillment Investigation`

The demo assets that explain the RAG comparison live under:

- `demos/rag_vs_contextwaypoint/`

## Tests

The repository now includes a focused engine test suite.

Run it with:

```bash
python -m unittest discover -s tests
```

The current tests cover:

- compile preserves hierarchy and `source_file`
- step routing order
- weight routing order
- keyword scoring behavior
- directory UUID filling

## Thesis and Evals

The concise project framing lives in:

- `docs/thesis.md`

The lightweight evaluation scaffold lives in:

- `evals/README.md`
- `evals/tasks/orderNotShipped.yaml`
- `evals/tasks/inventoryShortage.yaml`
- `evals/tasks/paymentFailure.yaml`

## Package Layout

The repo now has an installable package:

- `pyproject.toml`
- `src/contextwaypoint/`
- `tests/`
- `docs/`
- `evals/`
- `SECURITY.md`

The original script entry points still exist for compatibility:

- `src/contextValidator.py`
- `src/contextCompiler.py`
- `src/contextRouter.py`

## Security

Security reporting guidance lives in:

- `SECURITY.md`

## License

MIT. See `LICENSE`.

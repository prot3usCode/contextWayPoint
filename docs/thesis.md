<!-- Copyright (c) 2026 Daniel Bueno -->
<!-- SPDX-License-Identifier: MIT -->
<!-- See LICENSE for the full license text. -->

# contextWayPoint Thesis

## Core Claim

LLM context failures are often not retrieval failures. They are ordering
failures.

RAG is good at retrieving relevant chunks.

`contextWayPoint` is for a different job:

- define the intended route through context
- preserve the authored order of reasoning
- mix domain rules and reusable patterns deliberately
- produce deterministic context packets for a specific problem

## Why That Matters

A model can receive six relevant chunks and still fail the task if those chunks
arrive in the wrong order.

That failure usually looks like:

- jumping into a specific rule too early
- skipping the domain overview
- mixing explanation steps with evidence-gathering steps
- answering from partially relevant context without a coherent path

The missing piece is often not more retrieval. The missing piece is an authored
route.

## What contextWayPoint Does

`contextWayPoint` lets a human author that route explicitly.

The workflow is:

1. write context as a nested outline
2. tag entries with one or more problem flows
3. compile the outline into a flat JSON index
4. route a context packet by step, weight, authored order, or keyword overlap
5. return either the full packet or only the route map

This makes the route inspectable, testable, and repeatable.

## Difference From RAG

RAG answer:

- here are the chunks that seem relevant

`contextWayPoint` answer:

- here is the intended path through the relevant context

Those are related, but not identical.

RAG solves relevance.

`contextWayPoint` solves route definition.

## Practical Thesis

Many real data and operations questions are not just asking:

- what information matters?

They are also asking:

- what should come first?
- what evidence depends on that first step?
- what explanation rules should come last?

That is why an authored route can outperform unordered retrieval even when both
contain roughly the same facts.

## Repository Milestone

The project becomes compelling when a new person can:

1. clone the repo
2. install it locally
3. run one command
4. see an unordered retrieval example beside an authored route
5. immediately understand why ordered context is different from RAG

That is the standard this repository is now building toward.

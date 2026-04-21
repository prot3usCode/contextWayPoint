<!-- Copyright (c) 2026 Daniel Bueno -->
<!-- SPDX-License-Identifier: MIT -->
<!-- See LICENSE for the full license text. -->

# Evaluation Harness

This directory is a lightweight evaluation scaffold for `contextWayPoint`.

The goal is not to build a large benchmark yet. The goal is to create a small,
repeatable set of tasks that make the project claim testable.

Each task stores:

- the user question
- a baseline prompt
- an unordered-context prompt
- a `contextWayPoint` packet prompt
- the expected answer shape

The current tasks are:

- `orderNotShipped.yaml`
- `inventoryShortage.yaml`
- `paymentFailure.yaml`

These are intended for manual comparison now and can later feed a more
automated eval runner.

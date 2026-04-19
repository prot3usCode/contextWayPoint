# contextWayPoint

`contextWayPoint` is a lightweight context compiler and router for structured LLM or agent context.

It takes a YAML-shaped source file, compiles it into a flattened JSON index, and then routes ordered text packets for a given problem name.

## What It Does

- Compiles nested context entries into a queryable JSON index
- Matches entries by `problem_name`
- Sorts routed output by `step`, `weight`, or raw YAML order
- Produces plain text packets with only the context text in the selected order

## Main Scripts

- `src/contextCompiler.py`
- `src/contextRouter.py`

## Typical Workflow

```bash
python src/contextCompiler.py --input Formats/sampleBuildFailureContext.yaml
python src/contextRouter.py "Build Failure Triage" --mode step
```

## Output

- Compiled index: `output/contextIndex.json`
- Routed packet: `output/contextPackets/<problem><mode>.txt`

## Included Example

- `Formats/sampleBuildFailureContext.yaml`

## License

MIT. See `LICENSE`.

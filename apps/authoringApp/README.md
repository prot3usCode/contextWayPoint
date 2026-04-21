# contextWayPoint Authoring App

This is the first thin authoring shell for the future visualizer branch.

It is intentionally minimal.

What it does right now:

- loads a project JSON file
- lists problems and nodes
- lets you edit node title, body text, step, weight, keywords, and notes
- shows the generated YAML for the selected problem
- builds generated YAML and compiled JSON through the existing Python bridge

What it does not do yet:

- source-document viewing
- text highlighting
- drag-and-drop route editing
- PDF support
- undo / redo
- packaging for distribution

## Run

From this folder:

```bash
npm install
npm start
```

The app expects the repo-level Python environment to exist and the
`contextwaypoint` package to be installed in editable mode:

```bash
cd /path/to/contextWaypoint
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

The app loads this example project by default:

- `../../docs/examples/orderFulfillmentProject.example.json`

## Architecture

The shell is deliberately thin:

- renderer edits internal project-state
- preload exposes safe IPC methods
- main process calls the Python CLI bridge
- the Python bridge generates YAML and compiled JSON

That keeps the app transparent and lets the existing YAML/JSON engine stay the
real backend.

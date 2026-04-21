# contextWayPoint Authoring App

This is the first thin desktop shell for the future visualizer branch.

It is intentionally minimal.

What it does right now:

- has two tabs:
  - `Authoring Shell`
  - `Macro Creator`
- loads a project JSON file for authored problems
- loads `.md` and `.txt` source documents into a viewer
- lets you select text from the source viewer
- creates new nodes from the current selection
- applies the current selection to the selected node
- lists problems and nodes
- lets you edit node title, body text, step, weight, keywords, and notes
- loads a macro workspace JSON file
- lets you define linked projects, macros, macro steps, and conditions
- runs a backend macro preview through the existing Python bridge
- builds compiled JSON through the existing Python bridge

What it does not do yet:

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

- `../../docs/examples/authoringShellProject.example.json`

And this example macro workspace:

- `../../docs/examples/orderFulfillmentMacroWorkspace.example.json`

## Architecture

The shell is deliberately thin:

- renderer edits internal project-state for authored problems
- renderer also edits a separate macro workspace model
- renderer reads source selections from the document viewer
- preload exposes safe IPC methods
- preload runs through `preload.cjs` for a stable Electron bridge
- main process calls the Python CLI bridge
- main process also reads source documents from disk for `.md` and `.txt`
- the Python bridge generates internal support files, compiled JSON, and macro previews

That keeps the app transparent and lets the existing YAML/JSON engine stay the
real backend.

const state = {
  currentFilePath: null,
  project: null,
  selectedProblemName: null,
  selectedNodeId: null,
  yamlPreview: "Loading…",
  buildOutput: "No build has been run yet.",
  statusMessage: "Starting…",
  isDirty: false,
  renderTimerId: null,
};

const refs = {
  projectFilePath: document.querySelector("#project-file-path"),
  projectName: document.querySelector("#project-name"),
  projectStatus: document.querySelector("#project-status"),
  problemSelect: document.querySelector("#problem-select"),
  nodeList: document.querySelector("#node-list"),
  nodeTitleInput: document.querySelector("#node-title-input"),
  nodeBodyInput: document.querySelector("#node-body-input"),
  nodeStepInput: document.querySelector("#node-step-input"),
  nodeWeightInput: document.querySelector("#node-weight-input"),
  nodeKeywordsInput: document.querySelector("#node-keywords-input"),
  nodeNotesInput: document.querySelector("#node-notes-input"),
  anchorDisplayName: document.querySelector("#anchor-display-name"),
  anchorSourcePath: document.querySelector("#anchor-source-path"),
  anchorSelectedText: document.querySelector("#anchor-selected-text"),
  yamlPreview: document.querySelector("#yaml-preview"),
  buildOutput: document.querySelector("#build-output"),
  openProjectButton: document.querySelector("#open-project-button"),
  saveProjectButton: document.querySelector("#save-project-button"),
  saveProjectAsButton: document.querySelector("#save-project-as-button"),
  addNodeButton: document.querySelector("#add-node-button"),
  buildProjectButton: document.querySelector("#build-project-button"),
};

function problemDefinitions() {
  return state.project?.problems ?? [];
}

function nodes() {
  return state.project?.nodes ?? [];
}

function anchorsById() {
  return new Map((state.project?.anchors ?? []).map((anchor) => [anchor.anchor_id, anchor]));
}

function documentsById() {
  return new Map(
    (state.project?.documents ?? []).map((document) => [document.document_id, document])
  );
}

function selectedProblem() {
  return problemDefinitions().find(
    (problem) => problem.problem_name === state.selectedProblemName
  ) ?? null;
}

function assignmentForNode(node) {
  if (!node || !state.selectedProblemName) {
    return null;
  }

  return (
    node.problem_assignments?.find(
      (assignment) => assignment.problem_name === state.selectedProblemName
    ) ?? null
  );
}

function sortedNodesForSelectedProblem() {
  return nodes()
    .filter((node) => assignmentForNode(node))
    .slice()
    .sort((left, right) => {
      const leftAssignment = assignmentForNode(left);
      const rightAssignment = assignmentForNode(right);

      const leftStep = leftAssignment?.step_number ?? Number.MAX_SAFE_INTEGER;
      const rightStep = rightAssignment?.step_number ?? Number.MAX_SAFE_INTEGER;

      if (leftStep !== rightStep) {
        return leftStep - rightStep;
      }

      const leftWeight = Number(leftAssignment?.weight ?? 0);
      const rightWeight = Number(rightAssignment?.weight ?? 0);

      if (leftWeight !== rightWeight) {
        return rightWeight - leftWeight;
      }

      return left.title.localeCompare(right.title);
    });
}

function selectedNode() {
  return nodes().find((node) => node.node_id === state.selectedNodeId) ?? null;
}

function setStatus(message, dirty = state.isDirty) {
  state.statusMessage = message;
  state.isDirty = dirty;
  renderHeader();
}

function renderHeader() {
  refs.projectFilePath.textContent = state.currentFilePath ?? "Not loaded";
  refs.projectName.textContent = state.project?.project_name ?? "-";
  refs.projectStatus.textContent = state.isDirty
    ? `${state.statusMessage} • unsaved changes`
    : state.statusMessage;
}

function renderProblemOptions() {
  refs.problemSelect.innerHTML = "";

  for (const problem of problemDefinitions()) {
    const option = document.createElement("option");
    option.value = problem.problem_name;
    option.textContent = problem.problem_name;
    refs.problemSelect.append(option);
  }

  if (!state.selectedProblemName && problemDefinitions().length > 0) {
    state.selectedProblemName = problemDefinitions()[0].problem_name;
  }

  refs.problemSelect.value = state.selectedProblemName ?? "";
}

function renderNodeList() {
  refs.nodeList.innerHTML = "";

  const visibleNodes = sortedNodesForSelectedProblem();

  if (visibleNodes.length === 0) {
    const emptyState = document.createElement("p");
    emptyState.textContent = "No nodes yet for this problem.";
    refs.nodeList.append(emptyState);
    return;
  }

  for (const node of visibleNodes) {
    const assignment = assignmentForNode(node);
    const button = document.createElement("button");
    button.type = "button";
    button.className = "node-card";

    if (node.node_id === state.selectedNodeId) {
      button.classList.add("is-selected");
    }

    button.innerHTML = `
      <span class="node-card__step">Step ${assignment?.step_number ?? "?"}</span>
      <span class="node-card__title">${escapeHtml(node.title)}</span>
      <span class="node-card__meta">Weight ${assignment?.weight ?? 0}</span>
    `;

    button.addEventListener("click", () => {
      state.selectedNodeId = node.node_id;
      render();
    });

    refs.nodeList.append(button);
  }
}

function renderEditor() {
  const node = selectedNode();
  const assignment = assignmentForNode(node);
  const anchor = node ? anchorsById().get(node.anchor_id) : null;
  const document = anchor ? documentsById().get(anchor.document_id) : null;

  refs.nodeTitleInput.disabled = !node;
  refs.nodeBodyInput.disabled = !node;
  refs.nodeStepInput.disabled = !assignment;
  refs.nodeWeightInput.disabled = !assignment;
  refs.nodeKeywordsInput.disabled = !assignment;
  refs.nodeNotesInput.disabled = !node;

  refs.nodeTitleInput.value = node?.title ?? "";
  refs.nodeBodyInput.value = node?.body_text ?? "";
  refs.nodeStepInput.value = assignment?.step_number ?? "";
  refs.nodeWeightInput.value = assignment?.weight ?? "";
  refs.nodeKeywordsInput.value = assignment?.keywords?.join(", ") ?? "";
  refs.nodeNotesInput.value = node?.notes ?? "";

  refs.anchorDisplayName.textContent = document?.display_name ?? "No source anchor selected";
  refs.anchorSourcePath.textContent = document?.source_path ?? "-";
  refs.anchorSelectedText.textContent = anchor?.selected_text ?? "-";
}

function renderYamlPreview() {
  refs.yamlPreview.textContent = state.yamlPreview;
}

function renderBuildOutput() {
  refs.buildOutput.textContent = state.buildOutput;
}

function render() {
  renderHeader();
  renderProblemOptions();
  renderNodeList();
  renderEditor();
  renderYamlPreview();
  renderBuildOutput();
}

function normalizeKeywords(value) {
  return value
    .split(",")
    .map((token) => token.trim())
    .filter(Boolean);
}

function updateSelectedNode(mutator) {
  const node = selectedNode();
  if (!node) {
    return;
  }

  mutator(node);
  setStatus("Project updated", true);
  render();
  scheduleYamlRefresh();
}

function ensureSelectedNodeExists() {
  const visibleNodes = sortedNodesForSelectedProblem();
  if (visibleNodes.length === 0) {
    state.selectedNodeId = null;
    return;
  }

  if (!visibleNodes.some((node) => node.node_id === state.selectedNodeId)) {
    state.selectedNodeId = visibleNodes[0].node_id;
  }
}

function scheduleYamlRefresh() {
  window.clearTimeout(state.renderTimerId);
  state.renderTimerId = window.setTimeout(() => {
    refreshYamlPreview().catch((error) => {
      state.yamlPreview = `YAML render failed:\n${error.message}`;
      renderYamlPreview();
    });
  }, 220);
}

async function refreshYamlPreview() {
  if (!state.project) {
    return;
  }

  const rendered = await window.contextWayPointApp.renderYaml(
    state.project,
    state.selectedProblemName
  );
  state.yamlPreview = rendered || "# No YAML generated";
  renderYamlPreview();
}

function createNodeId() {
  return `node_${globalThis.crypto.randomUUID().slice(0, 8)}`;
}

function createAnchorId() {
  return `anchor_${globalThis.crypto.randomUUID().slice(0, 8)}`;
}

function currentProblemMaxStep() {
  return sortedNodesForSelectedProblem().reduce((maxStep, node) => {
    const assignment = assignmentForNode(node);
    return Math.max(maxStep, Number(assignment?.step_number ?? 0));
  }, 0);
}

function addNode() {
  if (!state.project || !state.selectedProblemName) {
    return;
  }

  const document = state.project.documents?.[0];
  if (!document) {
    setStatus("Add a source document to the project before creating nodes", state.isDirty);
    return;
  }

  const anchorId = createAnchorId();
  const nodeId = createNodeId();
  const nextStep = currentProblemMaxStep() + 1;

  state.project.anchors.push({
    anchor_id: anchorId,
    document_id: document.document_id,
    selected_text: "Add selected source text here.",
    char_start: null,
    char_end: null,
    page_number: null,
    context_before: "",
    context_after: "",
    capture_method: "manual_placeholder",
  });

  state.project.nodes.push({
    node_id: nodeId,
    title: `New Step ${nextStep}`,
    anchor_id: anchorId,
    body_text: "Add node text here.",
    notes: "",
    problem_assignments: [
      {
        problem_name: state.selectedProblemName,
        step_number: nextStep,
        weight: 50,
        keywords: [],
      },
    ],
  });

  const problem = selectedProblem();
  if (problem) {
    problem.node_ids = Array.from(new Set([...(problem.node_ids ?? []), nodeId]));
    if (!problem.entry_node_id) {
      problem.entry_node_id = nodeId;
    }
  }

  state.selectedNodeId = nodeId;
  setStatus("Added node", true);
  render();
  scheduleYamlRefresh();
}

async function openProject() {
  const loaded = await window.contextWayPointApp.openProjectDialog();
  if (!loaded) {
    return;
  }

  setLoadedProject(loaded.filePath, loaded.project);
  setStatus("Project loaded", false);
}

async function saveProject() {
  if (!state.project) {
    return;
  }

  if (!state.currentFilePath) {
    await saveProjectAs();
    return;
  }

  await window.contextWayPointApp.saveProject(state.currentFilePath, state.project);
  setStatus("Project saved", false);
}

async function saveProjectAs() {
  if (!state.project) {
    return;
  }

  const saved = await window.contextWayPointApp.saveProjectAs(state.project);
  if (!saved) {
    return;
  }

  state.currentFilePath = saved.filePath;
  setStatus("Project saved", false);
}

async function buildProject() {
  if (!state.project) {
    return;
  }

  setStatus("Building generated YAML and compiled JSON…", state.isDirty);
  const result = await window.contextWayPointApp.buildProject(state.project);
  state.buildOutput = [
    result.stdout,
    "",
    `Generated YAML: ${result.generatedYamlDir}`,
    `Compiled JSON: ${result.compiledJsonFile}`,
  ].join("\n");
  renderBuildOutput();
  setStatus("Build complete", state.isDirty);
}

function setLoadedProject(filePath, project) {
  state.currentFilePath = filePath;
  state.project = project;
  state.selectedProblemName =
    project.problems?.[0]?.problem_name ?? null;
  ensureSelectedNodeExists();
  state.buildOutput = "No build has been run yet.";
  render();
  scheduleYamlRefresh();
}

function escapeHtml(text) {
  return text
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

refs.problemSelect.addEventListener("change", (event) => {
  state.selectedProblemName = event.target.value;
  ensureSelectedNodeExists();
  render();
  scheduleYamlRefresh();
});

refs.nodeTitleInput.addEventListener("input", (event) => {
  updateSelectedNode((node) => {
    node.title = event.target.value;
  });
});

refs.nodeBodyInput.addEventListener("input", (event) => {
  updateSelectedNode((node) => {
    node.body_text = event.target.value;
  });
});

refs.nodeStepInput.addEventListener("input", (event) => {
  updateSelectedNode((node) => {
    const assignment = assignmentForNode(node);
    if (assignment) {
      assignment.step_number = Number(event.target.value || 1);
    }
  });
});

refs.nodeWeightInput.addEventListener("input", (event) => {
  updateSelectedNode((node) => {
    const assignment = assignmentForNode(node);
    if (assignment) {
      assignment.weight = Number(event.target.value || 0);
    }
  });
});

refs.nodeKeywordsInput.addEventListener("input", (event) => {
  updateSelectedNode((node) => {
    const assignment = assignmentForNode(node);
    if (assignment) {
      assignment.keywords = normalizeKeywords(event.target.value);
    }
  });
});

refs.nodeNotesInput.addEventListener("input", (event) => {
  updateSelectedNode((node) => {
    node.notes = event.target.value;
  });
});

refs.openProjectButton.addEventListener("click", () => {
  openProject().catch((error) => {
    setStatus(`Open failed: ${error.message}`, state.isDirty);
  });
});

refs.saveProjectButton.addEventListener("click", () => {
  saveProject().catch((error) => {
    setStatus(`Save failed: ${error.message}`, state.isDirty);
  });
});

refs.saveProjectAsButton.addEventListener("click", () => {
  saveProjectAs().catch((error) => {
    setStatus(`Save As failed: ${error.message}`, state.isDirty);
  });
});

refs.addNodeButton.addEventListener("click", () => addNode());

refs.buildProjectButton.addEventListener("click", () => {
  buildProject().catch((error) => {
    state.buildOutput = `Build failed:\n${error.message}`;
    renderBuildOutput();
    setStatus("Build failed", state.isDirty);
  });
});

async function initialize() {
  try {
    const loaded = await window.contextWayPointApp.loadDefaultProject();
    setLoadedProject(loaded.filePath, loaded.project);
    setStatus("Loaded default example project", false);
  } catch (error) {
    state.yamlPreview = `Failed to initialize:\n${error.message}`;
    setStatus("Initialization failed", false);
    render();
  }
}

initialize();

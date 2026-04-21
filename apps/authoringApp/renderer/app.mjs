const state = {
  activeTab: "authoring",
  currentFilePath: null,
  project: null,
  selectedProblemName: null,
  selectedNodeId: null,
  selectedDocumentId: null,
  documentCache: new Map(),
  linkedProjectCache: new Map(),
  currentSelection: null,
  buildOutput: "No build has been run yet.",
  statusMessage: "Starting…",
  isDirty: false,
  macroWorkspaceFilePath: null,
  macroWorkspace: null,
  selectedWorkspaceProjectId: null,
  selectedLinkedProblemName: null,
  selectedLinkedProblemStepNodeId: null,
  selectedMacroId: null,
  selectedMacroStepId: null,
  selectedMacroConditionId: null,
  macroPreviewOutput: "No macro preview has been run yet.",
  macroPromptText: "Why has order 4 not shipped?",
  macroStatusMessage: "Starting…",
  isMacroDirty: false,
  selectedTarget: null,
  dragTarget: null,
  contextMenu: {
    visible: false,
    x: 0,
    y: 0,
    target: null,
  },
};

const refs = {
  tabAuthoringButton: document.querySelector("#tab-authoring-button"),
  tabMacroButton: document.querySelector("#tab-macro-button"),
  authoringView: document.querySelector("#authoring-view"),
  macroView: document.querySelector("#macro-view"),
  projectFilePath: document.querySelector("#project-file-path"),
  projectName: document.querySelector("#project-name"),
  projectStatus: document.querySelector("#project-status"),
  problemSelect: document.querySelector("#problem-select"),
  documentList: document.querySelector("#document-list"),
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
  viewerDocumentName: document.querySelector("#viewer-document-name"),
  viewerDocumentPath: document.querySelector("#viewer-document-path"),
  documentViewer: document.querySelector("#document-viewer"),
  selectionSummary: document.querySelector("#selection-summary"),
  createNodeFromSelectionButton: document.querySelector(
    "#create-node-from-selection-button"
  ),
  applySelectionToNodeButton: document.querySelector(
    "#apply-selection-to-node-button"
  ),
  buildOutput: document.querySelector("#build-output"),
  newProjectButton: document.querySelector("#new-project-button"),
  openProjectButton: document.querySelector("#open-project-button"),
  addDocumentButton: document.querySelector("#add-document-button"),
  saveProjectButton: document.querySelector("#save-project-button"),
  saveProjectAsButton: document.querySelector("#save-project-as-button"),
  addNodeButton: document.querySelector("#add-node-button"),
  buildProjectButton: document.querySelector("#build-project-button"),
  macroWorkspaceFilePath: document.querySelector("#macro-workspace-file-path"),
  macroWorkspaceName: document.querySelector("#macro-workspace-name"),
  macroWorkspaceStatus: document.querySelector("#macro-workspace-status"),
  workspaceProjectSelect: document.querySelector("#workspace-project-select"),
  workspaceProjectDisplayNameInput: document.querySelector(
    "#workspace-project-display-name-input"
  ),
  workspaceProjectFileInput: document.querySelector("#workspace-project-file-input"),
  workspaceProjectIndexInput: document.querySelector(
    "#workspace-project-index-input"
  ),
  workspaceProjectStatusInput: document.querySelector(
    "#workspace-project-status-input"
  ),
  macroList: document.querySelector("#macro-list"),
  macroNameInput: document.querySelector("#macro-name-input"),
  macroDescriptionInput: document.querySelector("#macro-description-input"),
  macroEntryStepSelect: document.querySelector("#macro-entry-step-select"),
  macroStatusInput: document.querySelector("#macro-status-input"),
  macroTagsInput: document.querySelector("#macro-tags-input"),
  linkedProblemList: document.querySelector("#linked-problem-list"),
  linkedProblemName: document.querySelector("#linked-problem-name"),
  linkedProblemDescription: document.querySelector("#linked-problem-description"),
  linkedProblemStatus: document.querySelector("#linked-problem-status"),
  linkedProblemStepList: document.querySelector("#linked-problem-step-list"),
  linkedStepTitleInput: document.querySelector("#linked-step-title-input"),
  linkedStepBodyInput: document.querySelector("#linked-step-body-input"),
  linkedStepNumberInput: document.querySelector("#linked-step-number-input"),
  linkedStepWeightInput: document.querySelector("#linked-step-weight-input"),
  linkedStepKeywordsInput: document.querySelector("#linked-step-keywords-input"),
  linkedStepNotesInput: document.querySelector("#linked-step-notes-input"),
  macroStepList: document.querySelector("#macro-step-list"),
  macroStepIdInput: document.querySelector("#macro-step-id-input"),
  macroStepActionSelect: document.querySelector("#macro-step-action-select"),
  macroStepProjectSelect: document.querySelector("#macro-step-project-select"),
  macroStepProblemInput: document.querySelector("#macro-step-problem-input"),
  macroStepModeSelect: document.querySelector("#macro-step-mode-select"),
  macroStepFormatSelect: document.querySelector("#macro-step-format-select"),
  macroStepRouteOnlyInput: document.querySelector("#macro-step-route-only-input"),
  macroStepNestedMacroSelect: document.querySelector(
    "#macro-step-nested-macro-select"
  ),
  macroStepConditionSelect: document.querySelector("#macro-step-condition-select"),
  macroStepNextSelect: document.querySelector("#macro-step-next-select"),
  macroStepTrueSelect: document.querySelector("#macro-step-true-select"),
  macroStepFalseSelect: document.querySelector("#macro-step-false-select"),
  macroStepNotesInput: document.querySelector("#macro-step-notes-input"),
  macroConditionList: document.querySelector("#macro-condition-list"),
  macroConditionIdInput: document.querySelector("#macro-condition-id-input"),
  macroConditionKindSelect: document.querySelector("#macro-condition-kind-select"),
  macroConditionFieldInput: document.querySelector("#macro-condition-field-input"),
  macroConditionOperatorInput: document.querySelector(
    "#macro-condition-operator-input"
  ),
  macroConditionValuesInput: document.querySelector("#macro-condition-values-input"),
  macroConditionDescriptionInput: document.querySelector(
    "#macro-condition-description-input"
  ),
  macroPromptInput: document.querySelector("#macro-prompt-input"),
  macroPreviewOutput: document.querySelector("#macro-preview-output"),
  openMacroWorkspaceButton: document.querySelector("#open-macro-workspace-button"),
  saveMacroWorkspaceButton: document.querySelector("#save-macro-workspace-button"),
  saveMacroWorkspaceAsButton: document.querySelector(
    "#save-macro-workspace-as-button"
  ),
  addWorkspaceProjectButton: document.querySelector(
    "#add-workspace-project-button"
  ),
  addMacroButton: document.querySelector("#add-macro-button"),
  addProblemStepButton: document.querySelector("#add-problem-step-button"),
  addBranchStepButton: document.querySelector("#add-branch-step-button"),
  addStopStepButton: document.querySelector("#add-stop-step-button"),
  addConditionButton: document.querySelector("#add-condition-button"),
  previewMacroButton: document.querySelector("#preview-macro-button"),
  contextMenu: document.querySelector("#context-menu"),
  contextMenuCopy: document.querySelector("#context-menu-copy"),
  contextMenuCut: document.querySelector("#context-menu-cut"),
  contextMenuDelete: document.querySelector("#context-menu-delete"),
};

function problemDefinitions() {
  return state.project?.problems ?? [];
}

function documents() {
  return state.project?.documents ?? [];
}

function nodes() {
  return state.project?.nodes ?? [];
}

function anchors() {
  return state.project?.anchors ?? [];
}

function edges() {
  return state.project?.edges ?? [];
}

function anchorsById() {
  return new Map(anchors().map((anchor) => [anchor.anchor_id, anchor]));
}

function documentsById() {
  return new Map(
    documents().map((documentEntry) => [documentEntry.document_id, documentEntry])
  );
}

function selectedProblem() {
  return (
    problemDefinitions().find(
      (problem) => problem.problem_name === state.selectedProblemName
    ) ?? null
  );
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
      const leftStep = Number(leftAssignment?.step_number ?? Number.MAX_SAFE_INTEGER);
      const rightStep = Number(
        rightAssignment?.step_number ?? Number.MAX_SAFE_INTEGER
      );

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

function selectedDocument() {
  return (
    documents().find(
      (documentEntry) => documentEntry.document_id === state.selectedDocumentId
    ) ?? null
  );
}

function selectedDocumentCacheEntry() {
  if (!state.selectedDocumentId) {
    return null;
  }

  return state.documentCache.get(state.selectedDocumentId) ?? null;
}

function workspaceProjects() {
  return state.macroWorkspace?.projects ?? [];
}

function macroDefinitions() {
  return state.macroWorkspace?.macros ?? [];
}

function selectedWorkspaceProject() {
  return (
    workspaceProjects().find(
      (project) => project.project_id === state.selectedWorkspaceProjectId
    ) ?? null
  );
}

function selectedLinkedProjectData() {
  if (!state.selectedWorkspaceProjectId) {
    return null;
  }

  return state.linkedProjectCache.get(state.selectedWorkspaceProjectId) ?? null;
}

function linkedProblemDefinitions() {
  return selectedLinkedProjectData()?.project?.problems ?? [];
}

function linkedNodes() {
  return selectedLinkedProjectData()?.project?.nodes ?? [];
}

function linkedProblemAssignmentsForNode(node) {
  if (!node || !state.selectedLinkedProblemName) {
    return null;
  }

  return (
    node.problem_assignments?.find(
      (assignment) => assignment.problem_name === state.selectedLinkedProblemName
    ) ?? null
  );
}

function linkedProblemNodes() {
  return linkedNodes()
    .filter((node) => linkedProblemAssignmentsForNode(node))
    .slice()
    .sort((left, right) => {
      const leftAssignment = linkedProblemAssignmentsForNode(left);
      const rightAssignment = linkedProblemAssignmentsForNode(right);
      const leftStep = Number(leftAssignment?.step_number ?? Number.MAX_SAFE_INTEGER);
      const rightStep = Number(
        rightAssignment?.step_number ?? Number.MAX_SAFE_INTEGER
      );

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

function selectedLinkedProblem() {
  return (
    linkedProblemDefinitions().find(
      (problem) => problem.problem_name === state.selectedLinkedProblemName
    ) ?? null
  );
}

function selectedLinkedProblemStep() {
  return (
    linkedProblemNodes().find(
      (node) => node.node_id === state.selectedLinkedProblemStepNodeId
    ) ?? null
  );
}

function selectedMacro() {
  return (
    macroDefinitions().find((macro) => macro.macro_id === state.selectedMacroId) ??
    null
  );
}

function macroSteps() {
  return selectedMacro()?.steps ?? [];
}

function macroConditions() {
  return selectedMacro()?.conditions ?? [];
}

function selectedMacroStep() {
  return (
    macroSteps().find((step) => step.step_id === state.selectedMacroStepId) ?? null
  );
}

function selectedMacroCondition() {
  return (
    macroConditions().find(
      (condition) => condition.condition_id === state.selectedMacroConditionId
    ) ?? null
  );
}

function setStatus(message, dirty = state.isDirty) {
  state.statusMessage = message;
  state.isDirty = dirty;
  renderAuthoringHeader();
}

function setMacroStatus(message, dirty = state.isMacroDirty) {
  state.macroStatusMessage = message;
  state.isMacroDirty = dirty;
  renderMacroWorkspaceHeader();
}

function normalizeProject(project) {
  return {
    ...project,
    documents: Array.isArray(project.documents) ? project.documents : [],
    anchors: Array.isArray(project.anchors) ? project.anchors : [],
    nodes: Array.isArray(project.nodes) ? project.nodes : [],
    edges: Array.isArray(project.edges) ? project.edges : [],
    problems: Array.isArray(project.problems) ? project.problems : [],
    export_preferences:
      project.export_preferences ?? {
        target_format: "yaml",
        preserve_source_path: true,
      },
  };
}

function normalizeMacroWorkspace(workspace) {
  return {
    ...workspace,
    projects: Array.isArray(workspace.projects) ? workspace.projects : [],
    macros: Array.isArray(workspace.macros) ? workspace.macros : [],
    runtime_defaults: workspace.runtime_defaults ?? {
      default_mode: "step",
      default_output_format: "txt",
      rollback_strategy: "snapshot",
    },
  };
}

function createNodeId() {
  return `node_${globalThis.crypto.randomUUID().slice(0, 8)}`;
}

function createAnchorId() {
  return `anchor_${globalThis.crypto.randomUUID().slice(0, 8)}`;
}

function createDocumentId() {
  return `doc_${globalThis.crypto.randomUUID().slice(0, 8)}`;
}

function createEdgeId() {
  return `edge_${globalThis.crypto.randomUUID().slice(0, 8)}`;
}

function createWorkspaceProjectId() {
  return `project_${globalThis.crypto.randomUUID().slice(0, 8)}`;
}

function createMacroId() {
  return `macro_${globalThis.crypto.randomUUID().slice(0, 8)}`;
}

function createMacroStepId(prefix = "step") {
  return `${prefix}_${globalThis.crypto.randomUUID().slice(0, 6)}`;
}

function createConditionId() {
  return `cond_${globalThis.crypto.randomUUID().slice(0, 8)}`;
}

function currentProblemMaxStep() {
  return sortedNodesForSelectedProblem().reduce((maxStep, node) => {
    const assignment = assignmentForNode(node);
    return Math.max(maxStep, Number(assignment?.step_number ?? 0));
  }, 0);
}

function deriveTitleFromSelection(text) {
  const collapsed = text.replace(/^#+\s*/, "").replace(/\s+/g, " ").trim();

  if (!collapsed) {
    return "New Node";
  }

  if (collapsed.length <= 48) {
    return collapsed;
  }

  return `${collapsed.slice(0, 45).trim()}...`;
}

function escapeHtml(text) {
  return String(text)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function normalizeFreeTextList(value) {
  return value
    .split(",")
    .map((token) => token.trim())
    .filter((token) => token.length > 0);
}

function setSelectedTarget(target) {
  state.selectedTarget = target;
}

function hideContextMenu() {
  state.contextMenu = {
    visible: false,
    x: 0,
    y: 0,
    target: null,
  };
  refs.contextMenu.hidden = true;
}

function showContextMenu(event, target) {
  event.preventDefault();
  state.contextMenu = {
    visible: true,
    x: event.clientX,
    y: event.clientY,
    target,
  };
  refs.contextMenu.hidden = false;
  refs.contextMenu.style.left = `${event.clientX}px`;
  refs.contextMenu.style.top = `${event.clientY}px`;
}

function isEditableElement(element) {
  if (!element) {
    return false;
  }

  const tagName = element.tagName?.toLowerCase();
  return (
    element.isContentEditable ||
    tagName === "input" ||
    tagName === "textarea" ||
    tagName === "select"
  );
}

function isSameTarget(left, right) {
  return Boolean(left && right && left.kind === right.kind && left.id === right.id);
}

function reorderArrayById(items, fromId, toId, idField) {
  const nextItems = items.slice();
  const fromIndex = nextItems.findIndex((item) => item[idField] === fromId);
  const toIndex = nextItems.findIndex((item) => item[idField] === toId);

  if (fromIndex === -1 || toIndex === -1 || fromIndex === toIndex) {
    return items;
  }

  const [movedItem] = nextItems.splice(fromIndex, 1);
  nextItems.splice(toIndex, 0, movedItem);
  return nextItems;
}

function deleteAuthoringNode(nodeId) {
  const node = nodes().find((candidateNode) => candidateNode.node_id === nodeId);
  if (!node) {
    return false;
  }

  state.project.nodes = nodes().filter((candidateNode) => candidateNode.node_id !== nodeId);
  state.project.anchors = anchors().filter(
    (anchor) => anchor.anchor_id !== node.anchor_id
  );
  state.project.edges = edges().filter(
    (edge) => edge.from_node_id !== nodeId && edge.to_node_id !== nodeId
  );

  for (const problem of problemDefinitions()) {
    problem.node_ids = (problem.node_ids ?? []).filter(
      (problemNodeId) => problemNodeId !== nodeId
    );
    if (problem.entry_node_id === nodeId) {
      problem.entry_node_id = problem.node_ids[0] ?? null;
    }
  }

  ensureSelectedNodeExists();
  setStatus("Deleted route step", true);
  render();
  return true;
}

function deleteAuthoringDocument(documentId) {
  const affectedAnchors = anchors()
    .filter((anchor) => anchor.document_id === documentId)
    .map((anchor) => anchor.anchor_id);
  const affectedNodeIds = nodes()
    .filter((node) => affectedAnchors.includes(node.anchor_id))
    .map((node) => node.node_id);

  state.project.documents = documents().filter(
    (documentEntry) => documentEntry.document_id !== documentId
  );
  state.documentCache.delete(documentId);

  for (const nodeId of affectedNodeIds) {
    deleteAuthoringNode(nodeId);
  }

  state.project.anchors = anchors().filter(
    (anchor) => anchor.document_id !== documentId
  );
  ensureSelectedDocumentExists();
  setStatus("Deleted source document", true);
  render();
  return true;
}

function pruneUnusedLinkedProjectArtifacts(project) {
  const activeNodes = (project.nodes ?? []).filter(
    (node) => (node.problem_assignments ?? []).length > 0
  );
  const activeNodeIds = new Set(activeNodes.map((node) => node.node_id));
  const activeAnchorIds = new Set(
    activeNodes
      .map((node) => node.anchor_id)
      .filter((anchorId) => Boolean(anchorId))
  );

  project.nodes = activeNodes;
  project.anchors = (project.anchors ?? []).filter((anchor) =>
    activeAnchorIds.has(anchor.anchor_id)
  );
  project.edges = (project.edges ?? []).filter(
    (edge) =>
      activeNodeIds.has(edge.from_node_id) && activeNodeIds.has(edge.to_node_id)
  );

  for (const problem of project.problems ?? []) {
    problem.node_ids = (problem.node_ids ?? []).filter((nodeId) =>
      activeNodeIds.has(nodeId)
    );
    if (!activeNodeIds.has(problem.entry_node_id)) {
      problem.entry_node_id = problem.node_ids[0] ?? null;
    }
  }
}

function persistSelectedLinkedProject(successMessage) {
  const linkedProjectData = selectedLinkedProjectData();

  if (!linkedProjectData?.project || !linkedProjectData.filePath) {
    setMacroStatus(successMessage, true);
    render();
    return;
  }

  window.contextWayPointApp
    .saveProject(linkedProjectData.filePath, linkedProjectData.project)
    .then(() => {
      setMacroStatus(successMessage, true);
      render();
    })
    .catch((error) => {
      setMacroStatus(
        `Linked project save failed: ${error.message}`,
        state.isMacroDirty
      );
      render();
    });
}

function deleteLinkedProblemStep(nodeId) {
  const linkedProjectData = selectedLinkedProjectData();
  const problemName = state.selectedLinkedProblemName;
  if (!linkedProjectData?.project || !problemName) {
    return false;
  }

  const node = linkedProjectData.project.nodes.find(
    (candidateNode) => candidateNode.node_id === nodeId
  );
  if (!node) {
    return false;
  }

  node.problem_assignments = (node.problem_assignments ?? []).filter(
    (assignment) => assignment.problem_name !== problemName
  );

  for (const problem of linkedProjectData.project.problems ?? []) {
    if (problem.problem_name !== problemName) {
      continue;
    }

    problem.node_ids = (problem.node_ids ?? []).filter(
      (problemNodeId) => problemNodeId !== nodeId
    );
    if (problem.entry_node_id === nodeId) {
      problem.entry_node_id = problem.node_ids[0] ?? null;
    }
  }

  pruneUnusedLinkedProjectArtifacts(linkedProjectData.project);
  ensureSelectedLinkedProblemStepExists();
  persistSelectedLinkedProject("Removed linked problem step");
  render();
  return true;
}

function deleteLinkedProblem(problemName) {
  const linkedProjectData = selectedLinkedProjectData();
  if (!linkedProjectData?.project) {
    return false;
  }

  linkedProjectData.project.problems = linkedProjectData.project.problems.filter(
    (problem) => problem.problem_name !== problemName
  );
  for (const node of linkedProjectData.project.nodes ?? []) {
    node.problem_assignments = (node.problem_assignments ?? []).filter(
      (assignment) => assignment.problem_name !== problemName
    );
  }

  pruneUnusedLinkedProjectArtifacts(linkedProjectData.project);
  ensureSelectedLinkedProblemExists();
  ensureSelectedLinkedProblemStepExists();
  persistSelectedLinkedProject("Removed linked problem");
  render();
  return true;
}

function reorderLinkedProblems(fromProblemName, toProblemName) {
  const linkedProjectData = selectedLinkedProjectData();
  if (!linkedProjectData?.project) {
    return;
  }

  linkedProjectData.project.problems = reorderArrayById(
    linkedProjectData.project.problems ?? [],
    fromProblemName,
    toProblemName,
    "problem_name"
  );

  persistSelectedLinkedProject("Reordered linked problems");
  render();
}

function reorderLinkedProblemSteps(fromNodeId, toNodeId) {
  const linkedProjectData = selectedLinkedProjectData();
  const problem = selectedLinkedProblem();
  if (!linkedProjectData?.project || !problem) {
    return;
  }

  const orderedNodes = reorderArrayById(
    linkedProblemNodes(),
    fromNodeId,
    toNodeId,
    "node_id"
  );

  orderedNodes.forEach((node, index) => {
    const assignment = (node.problem_assignments ?? []).find(
      (candidateAssignment) =>
        candidateAssignment.problem_name === state.selectedLinkedProblemName
    );
    if (assignment) {
      assignment.step_number = index + 1;
    }
  });

  problem.node_ids = orderedNodes.map((node) => node.node_id);
  problem.entry_node_id = orderedNodes[0]?.node_id ?? null;
  persistSelectedLinkedProject("Reordered linked problem steps");
  render();
}

function deleteMacro(macroId) {
  state.macroWorkspace.macros = macroDefinitions().filter(
    (macro) => macro.macro_id !== macroId
  );

  for (const macro of macroDefinitions()) {
    for (const step of macro.steps ?? []) {
      if (step.macro_id === macroId) {
        step.macro_id = null;
      }
    }
  }

  ensureSelectedMacroExists();
  ensureSelectedMacroStepExists();
  ensureSelectedMacroConditionExists();
  setMacroStatus("Deleted macro", true);
  render();
  return true;
}

function deleteMacroStep(stepId) {
  const macro = selectedMacro();
  if (!macro) {
    return false;
  }

  macro.steps = macro.steps.filter((step) => step.step_id !== stepId);

  for (const step of macro.steps) {
    if (step.next_step_id === stepId) {
      step.next_step_id = null;
    }
    if (step.true_step_id === stepId) {
      step.true_step_id = null;
    }
    if (step.false_step_id === stepId) {
      step.false_step_id = null;
    }
  }

  synchronizeMacroLinearSequence(macro);
  ensureSelectedMacroStepExists();
  setMacroStatus("Deleted macro step", true);
  render();
  return true;
}

function deleteMacroCondition(conditionId) {
  const macro = selectedMacro();
  if (!macro) {
    return false;
  }

  macro.conditions = macro.conditions.filter(
    (condition) => condition.condition_id !== conditionId
  );

  for (const step of macro.steps ?? []) {
    if (step.condition_id === conditionId) {
      step.condition_id = "";
    }
  }

  ensureSelectedMacroConditionExists();
  setMacroStatus("Deleted condition", true);
  render();
  return true;
}

function getTargetPayload(target) {
  if (!target) {
    return null;
  }

  switch (target.kind) {
    case "authoring_document":
      return documents().find(
        (documentEntry) => documentEntry.document_id === target.id
      );
    case "authoring_node":
      return nodes().find((node) => node.node_id === target.id);
    case "macro":
      return macroDefinitions().find((macro) => macro.macro_id === target.id);
    case "macro_step":
      return macroSteps().find((step) => step.step_id === target.id);
    case "macro_condition":
      return macroConditions().find(
        (condition) => condition.condition_id === target.id
      );
    case "linked_problem":
      return linkedProblemDefinitions().find(
        (problem) => problem.problem_name === target.id
      );
    case "linked_problem_step":
      return linkedProblemNodes().find((node) => node.node_id === target.id);
    default:
      return null;
  }
}

async function copyTarget(target) {
  const payload = getTargetPayload(target);
  if (!payload) {
    return;
  }

  window.contextWayPointApp.writeClipboardText(JSON.stringify(payload, null, 2));
  if (state.activeTab === "authoring") {
    setStatus("Copied selection", state.isDirty);
  } else {
    setMacroStatus("Copied selection", state.isMacroDirty);
  }
}

function deleteTarget(target) {
  if (!target) {
    return false;
  }

  hideContextMenu();

  switch (target.kind) {
    case "authoring_document":
      return deleteAuthoringDocument(target.id);
    case "authoring_node":
      return deleteAuthoringNode(target.id);
    case "macro":
      return deleteMacro(target.id);
    case "macro_step":
      return deleteMacroStep(target.id);
    case "macro_condition":
      return deleteMacroCondition(target.id);
    case "linked_problem":
      return deleteLinkedProblem(target.id);
    case "linked_problem_step":
      return deleteLinkedProblemStep(target.id);
    default:
      return false;
  }
}

async function cutTarget(target) {
  await copyTarget(target);
  deleteTarget(target);
}

function populateSelect(select, options, selectedValue, placeholder = "Not set") {
  select.innerHTML = "";
  const blankOption = document.createElement("option");
  blankOption.value = "";
  blankOption.textContent = placeholder;
  select.append(blankOption);

  for (const option of options) {
    const optionElement = document.createElement("option");
    optionElement.value = option.value;
    optionElement.textContent = option.label;
    select.append(optionElement);
  }

  select.value = selectedValue ?? "";
}

function ensureSelectedProblemExists() {
  const problems = problemDefinitions();
  if (problems.length === 0) {
    state.selectedProblemName = null;
    return;
  }

  if (!problems.some((problem) => problem.problem_name === state.selectedProblemName)) {
    state.selectedProblemName = problems[0].problem_name;
  }
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

function ensureSelectedDocumentExists() {
  const availableDocuments = documents();
  if (availableDocuments.length === 0) {
    state.selectedDocumentId = null;
    return;
  }

  if (
    !availableDocuments.some(
      (documentEntry) => documentEntry.document_id === state.selectedDocumentId
    )
  ) {
    state.selectedDocumentId = availableDocuments[0].document_id;
  }
}

function ensureSelectedWorkspaceProjectExists() {
  const projects = workspaceProjects();
  if (projects.length === 0) {
    state.selectedWorkspaceProjectId = null;
    return;
  }

  if (
    !projects.some((project) => project.project_id === state.selectedWorkspaceProjectId)
  ) {
    state.selectedWorkspaceProjectId = projects[0].project_id;
  }
}

function ensureSelectedLinkedProblemExists() {
  const problems = linkedProblemDefinitions();
  if (problems.length === 0) {
    state.selectedLinkedProblemName = null;
    return;
  }

  if (
    !problems.some(
      (problem) => problem.problem_name === state.selectedLinkedProblemName
    )
  ) {
    state.selectedLinkedProblemName = problems[0].problem_name;
  }
}

function ensureSelectedLinkedProblemStepExists() {
  const problemNodes = linkedProblemNodes();
  if (problemNodes.length === 0) {
    state.selectedLinkedProblemStepNodeId = null;
    return;
  }

  if (
    !problemNodes.some(
      (node) => node.node_id === state.selectedLinkedProblemStepNodeId
    )
  ) {
    state.selectedLinkedProblemStepNodeId = problemNodes[0].node_id;
  }
}

function ensureSelectedMacroExists() {
  const macros = macroDefinitions();
  if (macros.length === 0) {
    state.selectedMacroId = null;
    return;
  }

  if (!macros.some((macro) => macro.macro_id === state.selectedMacroId)) {
    state.selectedMacroId = macros[0].macro_id;
  }
}

function ensureSelectedMacroStepExists() {
  const steps = macroSteps();
  if (steps.length === 0) {
    state.selectedMacroStepId = null;
    return;
  }

  if (!steps.some((step) => step.step_id === state.selectedMacroStepId)) {
    state.selectedMacroStepId = steps[0].step_id;
  }
}

function ensureSelectedMacroConditionExists() {
  const conditions = macroConditions();
  if (conditions.length === 0) {
    state.selectedMacroConditionId = null;
    return;
  }

  if (
    !conditions.some(
      (condition) => condition.condition_id === state.selectedMacroConditionId
    )
  ) {
    state.selectedMacroConditionId = conditions[0].condition_id;
  }
}

function resetCurrentSelection() {
  state.currentSelection = null;
  renderSelectionSummary();
}

function updateSelectedNode(mutator) {
  const node = selectedNode();
  if (!node) {
    return;
  }

  mutator(node);
  setStatus("Project updated", true);
  render();
}

function updateSelectedWorkspaceProject(mutator) {
  const project = selectedWorkspaceProject();
  if (!project) {
    return;
  }

  mutator(project);
  setMacroStatus("Macro workspace updated", true);
  render();
}

function updateSelectedMacro(mutator) {
  const macro = selectedMacro();
  if (!macro) {
    return;
  }

  mutator(macro);
  setMacroStatus("Macro workspace updated", true);
  render();
}

function updateSelectedMacroStep(mutator) {
  const step = selectedMacroStep();
  if (!step) {
    return;
  }

  mutator(step);
  setMacroStatus("Macro workspace updated", true);
  render();
}

function updateSelectedMacroCondition(mutator) {
  const condition = selectedMacroCondition();
  if (!condition) {
    return;
  }

  mutator(condition);
  setMacroStatus("Macro workspace updated", true);
  render();
}

function buildSelectionAnchorPayload() {
  const documentEntry = selectedDocument();
  const cacheEntry = selectedDocumentCacheEntry();

  if (!state.currentSelection || !documentEntry || !cacheEntry?.supportedText) {
    return null;
  }

  return {
    document_id: documentEntry.document_id,
    selected_text: state.currentSelection.selectedText,
    char_start: state.currentSelection.charStart,
    char_end: state.currentSelection.charEnd,
    page_number: null,
    context_before: state.currentSelection.contextBefore,
    context_after: state.currentSelection.contextAfter,
    capture_method: "text_selection",
  };
}

function renderTabs() {
  const isAuthoring = state.activeTab === "authoring";
  refs.tabAuthoringButton.classList.toggle("is-active", isAuthoring);
  refs.tabMacroButton.classList.toggle("is-active", !isAuthoring);
  refs.tabAuthoringButton.setAttribute("aria-selected", String(isAuthoring));
  refs.tabMacroButton.setAttribute("aria-selected", String(!isAuthoring));
  refs.authoringView.classList.toggle("is-active", isAuthoring);
  refs.macroView.classList.toggle("is-active", !isAuthoring);
}

function renderAuthoringHeader() {
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

  refs.problemSelect.value = state.selectedProblemName ?? "";
}

function renderStackButton(
  container,
  {
    eyebrow,
    title,
    meta,
    selected,
    onClick,
    target = null,
    draggable = false,
    onDrop = null,
  }
) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = "stack-card";

  if (selected) {
    button.classList.add("is-selected");
  }

  button.draggable = draggable;

  button.innerHTML = `
    <span class="stack-card__eyebrow">${escapeHtml(eyebrow)}</span>
    <span class="stack-card__title">${escapeHtml(title)}</span>
    <span class="stack-card__meta">${escapeHtml(meta)}</span>
  `;

  button.addEventListener("click", (event) => {
    if (target) {
      setSelectedTarget(target);
    }
    hideContextMenu();
    onClick?.(event);
  });

  if (target) {
    button.addEventListener("contextmenu", (event) => {
      setSelectedTarget(target);
      onClick?.(event);
      showContextMenu(event, target);
    });
  }

  if (draggable && target) {
    button.addEventListener("dragstart", () => {
      state.dragTarget = target;
      setSelectedTarget(target);
      hideContextMenu();
    });
    button.addEventListener("dragend", () => {
      state.dragTarget = null;
      button.classList.remove("is-drag-over");
    });
    button.addEventListener("dragover", (event) => {
      if (!state.dragTarget || isSameTarget(state.dragTarget, target)) {
        return;
      }

      event.preventDefault();
      button.classList.add("is-drag-over");
    });
    button.addEventListener("dragleave", () => {
      button.classList.remove("is-drag-over");
    });
    button.addEventListener("drop", (event) => {
      if (!state.dragTarget || isSameTarget(state.dragTarget, target)) {
        return;
      }

      event.preventDefault();
      button.classList.remove("is-drag-over");
      onDrop?.(state.dragTarget, target);
      state.dragTarget = null;
    });
  }

  container.append(button);
}

function renderDocumentList() {
  refs.documentList.innerHTML = "";

  if (documents().length === 0) {
    const emptyState = document.createElement("p");
    emptyState.textContent = "No source documents in this project yet.";
    refs.documentList.append(emptyState);
    return;
  }

  for (const documentEntry of documents()) {
    const cacheEntry = state.documentCache.get(documentEntry.document_id);
    const statusLabel = cacheEntry?.error
      ? "missing"
      : cacheEntry?.supportedText
        ? "ready"
        : documentEntry.status ?? "loaded";

    renderStackButton(refs.documentList, {
      eyebrow: statusLabel,
      title: documentEntry.display_name ?? documentEntry.source_path,
      meta: cacheEntry?.resolvedPath ?? documentEntry.source_path ?? "-",
      selected: documentEntry.document_id === state.selectedDocumentId,
      target: { kind: "authoring_document", id: documentEntry.document_id },
      draggable: true,
      onClick: async () => {
        state.selectedDocumentId = documentEntry.document_id;
        resetCurrentSelection();
        render();
        await ensureSelectedDocumentLoaded();
        render();
      },
      onDrop: (dragTarget, dropTarget) => {
        if (
          dragTarget.kind !== "authoring_document" ||
          dropTarget.kind !== "authoring_document"
        ) {
          return;
        }

        state.project.documents = reorderArrayById(
          documents(),
          dragTarget.id,
          dropTarget.id,
          "document_id"
        );
        setStatus("Reordered source documents", true);
        render();
      },
    });
  }
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
    renderStackButton(refs.nodeList, {
      eyebrow: `Step ${assignment?.step_number ?? "?"}`,
      title: node.title,
      meta: `Weight ${assignment?.weight ?? 0}`,
      selected: node.node_id === state.selectedNodeId,
      target: { kind: "authoring_node", id: node.node_id },
      draggable: true,
      onClick: async () => {
        state.selectedNodeId = node.node_id;
        setSelectedTarget({ kind: "authoring_node", id: node.node_id });
        const anchor = anchorsById().get(node.anchor_id);
        if (anchor) {
          state.selectedDocumentId = anchor.document_id;
        }
        resetCurrentSelection();
        render();
        await ensureSelectedDocumentLoaded();
        render();
      },
      onDrop: (dragTarget, dropTarget) => {
        if (
          dragTarget.kind !== "authoring_node" ||
          dropTarget.kind !== "authoring_node"
        ) {
          return;
        }

        reorderAuthoringNodes(dragTarget.id, dropTarget.id);
      },
    });
  }
}

function renderEditor() {
  const node = selectedNode();
  const assignment = assignmentForNode(node);
  const anchor = node ? anchorsById().get(node.anchor_id) : null;
  const documentEntry = anchor ? documentsById().get(anchor.document_id) : null;
  const cacheEntry = anchor ? state.documentCache.get(anchor.document_id) : null;

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

  refs.anchorDisplayName.textContent =
    documentEntry?.display_name ?? "No source anchor selected";
  refs.anchorSourcePath.textContent =
    cacheEntry?.resolvedPath ?? documentEntry?.source_path ?? "-";
  refs.anchorSelectedText.textContent = anchor?.selected_text ?? "-";
}

function renderDocumentViewer() {
  const documentEntry = selectedDocument();
  const cacheEntry = selectedDocumentCacheEntry();

  refs.viewerDocumentName.textContent =
    documentEntry?.display_name ?? "No document selected";
  refs.viewerDocumentPath.textContent =
    cacheEntry?.resolvedPath ?? documentEntry?.source_path ?? "-";

  refs.documentViewer.classList.remove("is-empty");

  if (!documentEntry) {
    refs.documentViewer.textContent = "Add or select a source document to begin.";
    refs.documentViewer.classList.add("is-empty");
    return;
  }

  if (cacheEntry?.error) {
    refs.documentViewer.textContent = `Could not load source file:\n${cacheEntry.error}`;
    refs.documentViewer.classList.add("is-empty");
    return;
  }

  if (!cacheEntry) {
    refs.documentViewer.textContent = "Loading source document…";
    refs.documentViewer.classList.add("is-empty");
    return;
  }

  if (!cacheEntry.supportedText) {
    refs.documentViewer.textContent =
      "This file type is not selectable yet. Start with .md or .txt.";
    refs.documentViewer.classList.add("is-empty");
    return;
  }

  refs.documentViewer.textContent = cacheEntry.content;
}

function renderSelectionSummary() {
  if (!state.currentSelection) {
    refs.selectionSummary.textContent =
      "Select text in the viewer to create or update an anchor.";
  } else {
    refs.selectionSummary.textContent =
      `${state.currentSelection.selectedText.length} chars • ` +
      `offsets ${state.currentSelection.charStart}-${state.currentSelection.charEnd}`;
  }

  refs.createNodeFromSelectionButton.disabled = !state.currentSelection;
  refs.applySelectionToNodeButton.disabled = !state.currentSelection || !selectedNode();
}

function renderBuildOutput() {
  refs.buildOutput.textContent = state.buildOutput;
}

function renderContextMenu() {
  if (!state.contextMenu.visible) {
    refs.contextMenu.hidden = true;
    return;
  }

  refs.contextMenu.hidden = false;
  refs.contextMenu.style.left = `${state.contextMenu.x}px`;
  refs.contextMenu.style.top = `${state.contextMenu.y}px`;
}

function renderMacroWorkspaceHeader() {
  refs.macroWorkspaceFilePath.value = state.macroWorkspaceFilePath ?? "";
  refs.macroWorkspaceName.value = state.macroWorkspace?.workspace_name ?? "";
  refs.macroWorkspaceStatus.value = state.isMacroDirty
    ? `${state.macroStatusMessage} • unsaved changes`
    : state.macroStatusMessage;
}

function renderWorkspaceProjectEditor() {
  const project = selectedWorkspaceProject();
  populateSelect(
    refs.workspaceProjectSelect,
    workspaceProjects().map((workspaceProject) => ({
      value: workspaceProject.project_id,
      label: workspaceProject.display_name ?? workspaceProject.project_id,
    })),
    state.selectedWorkspaceProjectId ?? "",
    "Select linked project"
  );

  const inputs = [
    refs.workspaceProjectSelect,
    refs.workspaceProjectDisplayNameInput,
    refs.workspaceProjectFileInput,
    refs.workspaceProjectIndexInput,
    refs.workspaceProjectStatusInput,
  ];

  for (const input of inputs) {
    input.disabled = !project;
  }

  refs.workspaceProjectDisplayNameInput.value = project?.display_name ?? "";
  refs.workspaceProjectFileInput.value = project?.project_file ?? "";
  refs.workspaceProjectIndexInput.value = project?.compiled_index_file ?? "";
  refs.workspaceProjectStatusInput.value = project?.status ?? "";
}

function renderMacroList() {
  refs.macroList.innerHTML = "";

  if (macroDefinitions().length === 0) {
    const emptyState = document.createElement("p");
    emptyState.textContent = "No macros yet.";
    refs.macroList.append(emptyState);
    return;
  }

  for (const macro of macroDefinitions()) {
    renderStackButton(refs.macroList, {
      eyebrow: macro.status ?? "draft",
      title: macro.name,
      meta: `${macro.steps?.length ?? 0} steps`,
      selected: macro.macro_id === state.selectedMacroId,
      target: { kind: "macro", id: macro.macro_id },
      draggable: true,
      onClick: () => {
        state.selectedMacroId = macro.macro_id;
        ensureSelectedMacroStepExists();
        ensureSelectedMacroConditionExists();
        render();
      },
      onDrop: (dragTarget, dropTarget) => {
        if (dragTarget.kind !== "macro" || dropTarget.kind !== "macro") {
          return;
        }

        state.macroWorkspace.macros = reorderArrayById(
          macroDefinitions(),
          dragTarget.id,
          dropTarget.id,
          "macro_id"
        );
        setMacroStatus("Reordered macros", true);
        render();
      },
    });
  }
}

function renderLinkedProblemList() {
  refs.linkedProblemList.innerHTML = "";
  const linkedProjectData = selectedLinkedProjectData();

  if (linkedProjectData?.error) {
    const errorState = document.createElement("p");
    errorState.textContent = `Could not load linked project: ${linkedProjectData.error}`;
    refs.linkedProblemList.append(errorState);
    return;
  }

  if (linkedProblemDefinitions().length === 0) {
    const emptyState = document.createElement("p");
    emptyState.textContent = "No authored problems are available from this linked project yet.";
    refs.linkedProblemList.append(emptyState);
    return;
  }

  for (const problem of linkedProblemDefinitions()) {
    renderStackButton(refs.linkedProblemList, {
      eyebrow: problem.status ?? "draft",
      title: problem.problem_name,
      meta: `${problem.node_ids?.length ?? 0} steps`,
      selected: problem.problem_name === state.selectedLinkedProblemName,
      target: { kind: "linked_problem", id: problem.problem_name },
      draggable: true,
      onClick: () => {
        state.selectedLinkedProblemName = problem.problem_name;
        ensureSelectedLinkedProblemStepExists();
        render();
      },
      onDrop: (dragTarget, dropTarget) => {
        if (
          dragTarget.kind !== "linked_problem" ||
          dropTarget.kind !== "linked_problem"
        ) {
          return;
        }

        reorderLinkedProblems(dragTarget.id, dropTarget.id);
      },
    });
  }
}

function renderLinkedProblemDetails() {
  const linkedProjectData = selectedLinkedProjectData();
  const problem = selectedLinkedProblem();

  refs.linkedProblemName.textContent =
    problem?.problem_name ?? "No problem selected";
  refs.linkedProblemDescription.textContent = problem?.description ?? "-";
  refs.linkedProblemStatus.textContent = linkedProjectData?.error
    ? "project load failed"
    : problem?.status ?? "-";
}

function renderLinkedProblemStepList() {
  refs.linkedProblemStepList.innerHTML = "";

  if (linkedProblemNodes().length === 0) {
    const emptyState = document.createElement("p");
    emptyState.textContent = "No authored steps available for this problem.";
    refs.linkedProblemStepList.append(emptyState);
    return;
  }

  for (const node of linkedProblemNodes()) {
    const assignment = linkedProblemAssignmentsForNode(node);
    renderStackButton(refs.linkedProblemStepList, {
      eyebrow: `Step ${assignment?.step_number ?? "?"}`,
      title: node.title,
      meta: `Weight ${assignment?.weight ?? 0}`,
      selected: node.node_id === state.selectedLinkedProblemStepNodeId,
      target: { kind: "linked_problem_step", id: node.node_id },
      draggable: true,
      onClick: () => {
        state.selectedLinkedProblemStepNodeId = node.node_id;
        render();
      },
      onDrop: (dragTarget, dropTarget) => {
        if (
          dragTarget.kind !== "linked_problem_step" ||
          dropTarget.kind !== "linked_problem_step"
        ) {
          return;
        }

        reorderLinkedProblemSteps(dragTarget.id, dropTarget.id);
      },
    });
  }
}

function renderLinkedProblemStepEditor() {
  const node = selectedLinkedProblemStep();
  const assignment = linkedProblemAssignmentsForNode(node);

  refs.linkedStepTitleInput.value = node?.title ?? "";
  refs.linkedStepBodyInput.value = node?.body_text ?? "";
  refs.linkedStepNumberInput.value = assignment?.step_number ?? "";
  refs.linkedStepWeightInput.value = assignment?.weight ?? "";
  refs.linkedStepKeywordsInput.value = assignment?.keywords?.join(", ") ?? "";
  refs.linkedStepNotesInput.value = node?.notes ?? "";
}

function renderMacroEditor() {
  const macro = selectedMacro();
  const steps = macroSteps();
  const inputs = [
    refs.macroNameInput,
    refs.macroDescriptionInput,
    refs.macroEntryStepSelect,
    refs.macroStatusInput,
    refs.macroTagsInput,
  ];

  for (const input of inputs) {
    input.disabled = !macro;
  }

  refs.macroNameInput.value = macro?.name ?? "";
  refs.macroDescriptionInput.value = macro?.description ?? "";
  populateSelect(
    refs.macroEntryStepSelect,
    steps.map((step) => ({ value: step.step_id, label: step.step_id })),
    macro?.entry_step_id ?? "",
    "Select entry step"
  );
  refs.macroStatusInput.value = macro?.status ?? "";
  refs.macroTagsInput.value = macro?.tags?.join(", ") ?? "";
}

function renderMacroStepList() {
  refs.macroStepList.innerHTML = "";

  if (macroSteps().length === 0) {
    const emptyState = document.createElement("p");
    emptyState.textContent = "No steps yet for this macro.";
    refs.macroStepList.append(emptyState);
    return;
  }

  for (const step of macroSteps()) {
    const meta =
      step.action === "include_problem"
        ? step.problem_ref?.problem_name ?? "Problem not set"
        : step.action === "include_macro"
          ? step.macro_id ?? "Nested macro not set"
          : step.action === "branch"
            ? step.condition_id ?? "Condition not set"
            : "Stop";

    renderStackButton(refs.macroStepList, {
      eyebrow: step.action,
      title: step.step_id,
      meta,
      selected: step.step_id === state.selectedMacroStepId,
      target: { kind: "macro_step", id: step.step_id },
      draggable: true,
      onClick: () => {
        state.selectedMacroStepId = step.step_id;
        render();
      },
      onDrop: (dragTarget, dropTarget) => {
        if (
          dragTarget.kind !== "macro_step" ||
          dropTarget.kind !== "macro_step" ||
          !selectedMacro()
        ) {
          return;
        }

        selectedMacro().steps = reorderArrayById(
          macroSteps(),
          dragTarget.id,
          dropTarget.id,
          "step_id"
        );
        synchronizeMacroLinearSequence(selectedMacro());
        setMacroStatus("Reordered macro steps", true);
        render();
      },
    });
  }
}

function ensureProblemRef(step) {
  if (!step.problem_ref) {
    step.problem_ref = {
      project_id: workspaceProjects()[0]?.project_id ?? "",
      problem_name: "",
      mode: state.macroWorkspace?.runtime_defaults?.default_mode ?? "step",
      output_format:
        state.macroWorkspace?.runtime_defaults?.default_output_format ?? "txt",
      route_only: false,
    };
  }

  return step.problem_ref;
}

function renderMacroStepEditor() {
  const step = selectedMacroStep();
  const macro = selectedMacro();
  const stepInputs = [
    refs.macroStepIdInput,
    refs.macroStepActionSelect,
    refs.macroStepProjectSelect,
    refs.macroStepProblemInput,
    refs.macroStepModeSelect,
    refs.macroStepFormatSelect,
    refs.macroStepRouteOnlyInput,
    refs.macroStepNestedMacroSelect,
    refs.macroStepConditionSelect,
    refs.macroStepNextSelect,
    refs.macroStepTrueSelect,
    refs.macroStepFalseSelect,
    refs.macroStepNotesInput,
  ];

  for (const input of stepInputs) {
    input.disabled = !step;
  }

  if (!step || !macro) {
    refs.macroStepIdInput.value = "";
    refs.macroStepProblemInput.value = "";
    refs.macroStepNotesInput.value = "";
    refs.macroStepRouteOnlyInput.checked = false;
    populateSelect(refs.macroStepProjectSelect, [], "", "Select project");
    populateSelect(refs.macroStepNestedMacroSelect, [], "", "Select nested macro");
    populateSelect(refs.macroStepConditionSelect, [], "", "Select condition");
    populateSelect(refs.macroStepNextSelect, [], "", "Not set");
    populateSelect(refs.macroStepTrueSelect, [], "", "Not set");
    populateSelect(refs.macroStepFalseSelect, [], "", "Not set");
    return;
  }

  const problemRef = ensureProblemRef(step);
  const stepOptions = macroSteps().map((macroStep) => ({
    value: macroStep.step_id,
    label: macroStep.step_id,
  }));
  const projectOptions = workspaceProjects().map((project) => ({
    value: project.project_id,
    label: project.display_name ?? project.project_id,
  }));
  const nestedMacroOptions = macroDefinitions()
    .filter((candidateMacro) => candidateMacro.macro_id !== macro.macro_id)
    .map((candidateMacro) => ({
      value: candidateMacro.macro_id,
      label: candidateMacro.name,
    }));
  const conditionOptions = macroConditions().map((condition) => ({
    value: condition.condition_id,
    label: condition.condition_id,
  }));

  refs.macroStepIdInput.value = step.step_id ?? "";
  refs.macroStepActionSelect.value = step.action ?? "include_problem";
  refs.macroStepProblemInput.value = problemRef.problem_name ?? "";
  refs.macroStepModeSelect.value = problemRef.mode ?? "step";
  refs.macroStepFormatSelect.value = problemRef.output_format ?? "txt";
  refs.macroStepRouteOnlyInput.checked = Boolean(problemRef.route_only);
  refs.macroStepNotesInput.value = step.notes ?? "";

  populateSelect(
    refs.macroStepProjectSelect,
    projectOptions,
    problemRef.project_id ?? "",
    "Select project"
  );
  populateSelect(
    refs.macroStepNestedMacroSelect,
    nestedMacroOptions,
    step.macro_id ?? "",
    "Select nested macro"
  );
  populateSelect(
    refs.macroStepConditionSelect,
    conditionOptions,
    step.condition_id ?? "",
    "Select condition"
  );
  populateSelect(refs.macroStepNextSelect, stepOptions, step.next_step_id ?? "");
  populateSelect(refs.macroStepTrueSelect, stepOptions, step.true_step_id ?? "");
  populateSelect(refs.macroStepFalseSelect, stepOptions, step.false_step_id ?? "");

  const isProblemStep = step.action === "include_problem";
  const isNestedMacroStep = step.action === "include_macro";
  const isBranchStep = step.action === "branch";

  refs.macroStepProjectSelect.disabled = !isProblemStep;
  refs.macroStepProblemInput.disabled = !isProblemStep;
  refs.macroStepModeSelect.disabled = !isProblemStep;
  refs.macroStepFormatSelect.disabled = !isProblemStep;
  refs.macroStepRouteOnlyInput.disabled = !isProblemStep;
  refs.macroStepNestedMacroSelect.disabled = !isNestedMacroStep;
  refs.macroStepConditionSelect.disabled = !isBranchStep;
  refs.macroStepTrueSelect.disabled = !isBranchStep;
  refs.macroStepFalseSelect.disabled = !isBranchStep;
  refs.macroStepNextSelect.disabled = step.action === "stop" || isBranchStep;
}

function renderMacroConditionList() {
  refs.macroConditionList.innerHTML = "";

  if (macroConditions().length === 0) {
    const emptyState = document.createElement("p");
    emptyState.textContent = "No conditions yet for this macro.";
    refs.macroConditionList.append(emptyState);
    return;
  }

  for (const condition of macroConditions()) {
    renderStackButton(refs.macroConditionList, {
      eyebrow: condition.kind,
      title: condition.condition_id,
      meta: condition.values?.join(", ") || "No values",
      selected: condition.condition_id === state.selectedMacroConditionId,
      target: { kind: "macro_condition", id: condition.condition_id },
      draggable: true,
      onClick: () => {
        state.selectedMacroConditionId = condition.condition_id;
        render();
      },
      onDrop: (dragTarget, dropTarget) => {
        if (
          dragTarget.kind !== "macro_condition" ||
          dropTarget.kind !== "macro_condition" ||
          !selectedMacro()
        ) {
          return;
        }

        selectedMacro().conditions = reorderArrayById(
          macroConditions(),
          dragTarget.id,
          dropTarget.id,
          "condition_id"
        );
        setMacroStatus("Reordered conditions", true);
        render();
      },
    });
  }
}

function renderMacroConditionEditor() {
  const condition = selectedMacroCondition();
  const inputs = [
    refs.macroConditionIdInput,
    refs.macroConditionKindSelect,
    refs.macroConditionFieldInput,
    refs.macroConditionOperatorInput,
    refs.macroConditionValuesInput,
    refs.macroConditionDescriptionInput,
  ];

  for (const input of inputs) {
    input.disabled = !condition;
  }

  refs.macroConditionIdInput.value = condition?.condition_id ?? "";
  refs.macroConditionKindSelect.value =
    condition?.kind ?? "prompt_contains_any";
  refs.macroConditionFieldInput.value = condition?.field ?? "";
  refs.macroConditionOperatorInput.value = condition?.operator ?? "";
  refs.macroConditionValuesInput.value = condition?.values?.join(", ") ?? "";
  refs.macroConditionDescriptionInput.value = condition?.description ?? "";
}

function renderMacroPreview() {
  refs.macroPromptInput.value = state.macroPromptText;
  refs.macroPreviewOutput.textContent = state.macroPreviewOutput;
}

function renderAuthoring() {
  renderAuthoringHeader();
  renderProblemOptions();
  renderDocumentList();
  renderNodeList();
  renderDocumentViewer();
  renderEditor();
  renderSelectionSummary();
  renderBuildOutput();
}

function renderMacroCreator() {
  renderMacroWorkspaceHeader();
  renderWorkspaceProjectEditor();
  renderLinkedProblemList();
  renderLinkedProblemDetails();
  renderLinkedProblemStepList();
  renderLinkedProblemStepEditor();
  renderMacroList();
  renderMacroEditor();
  renderMacroStepList();
  renderMacroStepEditor();
  renderMacroConditionList();
  renderMacroConditionEditor();
  renderMacroPreview();
}

function render() {
  renderTabs();
  renderAuthoring();
  renderMacroCreator();
  renderContextMenu();
}

function selectionOffsetsForContainer(container) {
  const selection = window.getSelection();
  if (!selection || selection.rangeCount === 0 || selection.isCollapsed) {
    return null;
  }

  const range = selection.getRangeAt(0);
  if (!container.contains(range.commonAncestorContainer)) {
    return null;
  }

  const preSelectionRange = range.cloneRange();
  preSelectionRange.selectNodeContents(container);
  preSelectionRange.setEnd(range.startContainer, range.startOffset);

  const charStart = preSelectionRange.toString().length;
  const selectedText = range.toString();
  const charEnd = charStart + selectedText.length;

  if (!selectedText.trim()) {
    return null;
  }

  return {
    selectedText,
    charStart,
    charEnd,
  };
}

function updateSelectionFromViewer() {
  const documentEntry = selectedDocument();
  const cacheEntry = selectedDocumentCacheEntry();

  if (!documentEntry || !cacheEntry?.supportedText) {
    resetCurrentSelection();
    return;
  }

  const offsets = selectionOffsetsForContainer(refs.documentViewer);
  if (!offsets) {
    resetCurrentSelection();
    return;
  }

  const contextBefore = cacheEntry.content.slice(
    Math.max(0, offsets.charStart - 80),
    offsets.charStart
  );
  const contextAfter = cacheEntry.content.slice(
    offsets.charEnd,
    Math.min(cacheEntry.content.length, offsets.charEnd + 80)
  );

  state.currentSelection = {
    documentId: documentEntry.document_id,
    selectedText: offsets.selectedText,
    charStart: offsets.charStart,
    charEnd: offsets.charEnd,
    contextBefore,
    contextAfter,
  };
  renderSelectionSummary();
}

function createNodeFromSelection() {
  if (!state.project || !state.selectedProblemName) {
    return;
  }

  const anchorPayload = buildSelectionAnchorPayload();
  if (!anchorPayload) {
    setStatus("Select text in a .md or .txt document first", state.isDirty);
    return;
  }

  const previousLastNode = sortedNodesForSelectedProblem().at(-1) ?? null;
  const anchorId = createAnchorId();
  const nodeId = createNodeId();
  const nextStep = currentProblemMaxStep() + 1;

  state.project.anchors.push({
    anchor_id: anchorId,
    ...anchorPayload,
  });

  state.project.nodes.push({
    node_id: nodeId,
    title: deriveTitleFromSelection(anchorPayload.selected_text),
    anchor_id: anchorId,
    body_text: anchorPayload.selected_text,
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

  if (previousLastNode && previousLastNode.node_id !== nodeId) {
    edges().push({
      edge_id: createEdgeId(),
      problem_name: state.selectedProblemName,
      from_node_id: previousLastNode.node_id,
      to_node_id: nodeId,
      label: "next",
    });
  }

  state.selectedNodeId = nodeId;
  setStatus("Created node from selection", true);
  render();
}

function createBlankNode() {
  if (!state.project || !state.selectedProblemName) {
    return;
  }

  const documentEntry = selectedDocument() ?? documents()[0];
  if (!documentEntry) {
    setStatus("Add a source document before creating a blank node", state.isDirty);
    return;
  }

  const previousLastNode = sortedNodesForSelectedProblem().at(-1) ?? null;
  const anchorId = createAnchorId();
  const nodeId = createNodeId();
  const nextStep = currentProblemMaxStep() + 1;

  state.project.anchors.push({
    anchor_id: anchorId,
    document_id: documentEntry.document_id,
    selected_text: "Select source text later.",
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
    body_text: "",
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

  if (previousLastNode && previousLastNode.node_id !== nodeId) {
    edges().push({
      edge_id: createEdgeId(),
      problem_name: state.selectedProblemName,
      from_node_id: previousLastNode.node_id,
      to_node_id: nodeId,
      label: "next",
    });
  }

  state.selectedNodeId = nodeId;
  state.selectedDocumentId = documentEntry.document_id;
  resetCurrentSelection();
  setStatus("Added blank node", true);
  render();
}

function applySelectionToSelectedNode() {
  const node = selectedNode();
  const anchorPayload = buildSelectionAnchorPayload();

  if (!node || !anchorPayload) {
    setStatus("Select text and choose a node first", state.isDirty);
    return;
  }

  const anchor = anchorsById().get(node.anchor_id);
  if (!anchor) {
    return;
  }

  anchor.document_id = anchorPayload.document_id;
  anchor.selected_text = anchorPayload.selected_text;
  anchor.char_start = anchorPayload.char_start;
  anchor.char_end = anchorPayload.char_end;
  anchor.page_number = anchorPayload.page_number;
  anchor.context_before = anchorPayload.context_before;
  anchor.context_after = anchorPayload.context_after;
  anchor.capture_method = anchorPayload.capture_method;
  node.body_text = anchorPayload.selected_text;

  if (!node.title.trim() || /^New Step/.test(node.title)) {
    node.title = deriveTitleFromSelection(anchorPayload.selected_text);
  }

  setStatus("Applied source selection to node", true);
  render();
}

async function loadDocumentIntoCache(documentEntry) {
  try {
    const payload = await window.contextWayPointApp.readSourceDocument(
      documentEntry.source_path
    );
    state.documentCache.set(documentEntry.document_id, payload);
    documentEntry.display_name = documentEntry.display_name || payload.displayName;
    documentEntry.file_type = documentEntry.file_type || payload.fileType;
    documentEntry.sha256 = documentEntry.sha256 || payload.sha256;
    documentEntry.modified_at = documentEntry.modified_at || payload.modifiedAt;
    documentEntry.size_bytes = documentEntry.size_bytes || payload.sizeBytes;
    documentEntry.status = "available";
  } catch (error) {
    state.documentCache.set(documentEntry.document_id, {
      error: error.message,
      supportedText: false,
      content: "",
      resolvedPath: documentEntry.source_path,
    });
    documentEntry.status = "missing";
  }
}

async function hydrateProjectDocuments() {
  state.documentCache = new Map();
  await Promise.all(
    documents().map((documentEntry) => loadDocumentIntoCache(documentEntry))
  );
}

async function ensureSelectedDocumentLoaded() {
  const documentEntry = selectedDocument();
  if (!documentEntry) {
    return;
  }

  if (!state.documentCache.has(documentEntry.document_id)) {
    await loadDocumentIntoCache(documentEntry);
  }
}

async function loadSelectedWorkspaceProjectReference() {
  const workspaceProject = selectedWorkspaceProject();
  if (!workspaceProject) {
    return;
  }

  try {
    const baseDir = state.macroWorkspaceFilePath
      ? state.macroWorkspaceFilePath.replace(/[/\\][^/\\]+$/, "")
      : null;
    const loaded = await window.contextWayPointApp.loadReferencedProjectFile(
      workspaceProject.project_file,
      baseDir
    );
    state.linkedProjectCache.set(workspaceProject.project_id, {
      project: normalizeProject(loaded.project),
      filePath: loaded.filePath,
      error: null,
    });
  } catch (error) {
    state.linkedProjectCache.set(workspaceProject.project_id, {
      project: null,
      filePath: workspaceProject.project_file,
      error: error.message,
    });
  }

  ensureSelectedLinkedProblemExists();
  ensureSelectedLinkedProblemStepExists();
}

function synchronizeMacroLinearSequence(macro) {
  if (!macro || !Array.isArray(macro.steps) || macro.steps.length === 0) {
    return;
  }

  macro.entry_step_id = macro.steps[0].step_id;

  for (let index = 0; index < macro.steps.length; index += 1) {
    const step = macro.steps[index];
    const nextStep = macro.steps[index + 1] ?? null;

    if (step.action === "branch") {
      if (!step.true_step_id) {
        step.true_step_id = nextStep?.step_id ?? null;
      }
      if (!step.false_step_id) {
        step.false_step_id = nextStep?.step_id ?? null;
      }
      step.next_step_id = null;
      continue;
    }

    if (step.action === "stop") {
      step.next_step_id = null;
      continue;
    }

    step.next_step_id = nextStep?.step_id ?? null;
  }
}

async function setLoadedProject(filePath, project) {
  state.currentFilePath = filePath;
  state.project = normalizeProject(project);
  ensureSelectedProblemExists();
  state.selectedDocumentId = state.project.documents?.[0]?.document_id ?? null;
  await hydrateProjectDocuments();
  ensureSelectedDocumentExists();
  ensureSelectedNodeExists();

  const node = selectedNode();
  if (node) {
    const anchor = anchorsById().get(node.anchor_id);
    if (anchor) {
      state.selectedDocumentId = anchor.document_id;
    }
  }

  state.buildOutput = "No build has been run yet.";
  resetCurrentSelection();
  render();
}

async function setLoadedMacroWorkspace(filePath, workspace) {
  state.macroWorkspaceFilePath = filePath;
  state.macroWorkspace = normalizeMacroWorkspace(workspace);
  state.linkedProjectCache = new Map();
  ensureSelectedWorkspaceProjectExists();
  await loadSelectedWorkspaceProjectReference();
  ensureSelectedMacroExists();
  ensureSelectedMacroStepExists();
  ensureSelectedMacroConditionExists();
  state.macroPreviewOutput = "No macro preview has been run yet.";
  render();
}

async function openProject() {
  const loaded = await window.contextWayPointApp.openProjectDialog();
  if (!loaded) {
    return;
  }

  await setLoadedProject(loaded.filePath, loaded.project);
  setStatus("Project loaded", false);
}

async function newProject() {
  const created = await window.contextWayPointApp.newProjectDialog();
  if (!created) {
    return;
  }

  await setLoadedProject(created.filePath, created.project);
  setStatus("Created new project", false);
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

  setStatus("Building project outputs…", state.isDirty);
  const result = await window.contextWayPointApp.buildProject(state.project);
  state.buildOutput = [
    "Project outputs ready.",
    `Compiled JSON: ${result.compiledJsonFile}`,
    `Internal generated files: ${result.generatedYamlDir}`,
  ].join("\n");
  renderBuildOutput();
  setStatus("Build complete", state.isDirty);
}

async function addSourceDocument() {
  if (!state.project) {
    return;
  }

  const selectedDocumentPayload =
    await window.contextWayPointApp.openSourceDocumentDialog();
  if (!selectedDocumentPayload) {
    return;
  }

  const existingDocument = documents().find(
    (documentEntry) => documentEntry.source_path === selectedDocumentPayload.resolvedPath
  );

  if (existingDocument) {
    state.selectedDocumentId = existingDocument.document_id;
    state.documentCache.set(existingDocument.document_id, selectedDocumentPayload);
    setStatus("Source document already exists in this project", state.isDirty);
    render();
    return;
  }

  const documentId = createDocumentId();
  state.project.documents.push({
    document_id: documentId,
    display_name: selectedDocumentPayload.displayName,
    source_path: selectedDocumentPayload.resolvedPath,
    file_type: selectedDocumentPayload.fileType,
    sha256: selectedDocumentPayload.sha256,
    modified_at: selectedDocumentPayload.modifiedAt,
    size_bytes: selectedDocumentPayload.sizeBytes,
    status: "available",
  });
  state.documentCache.set(documentId, selectedDocumentPayload);
  state.selectedDocumentId = documentId;
  resetCurrentSelection();
  setStatus("Added source document", true);
  render();
}

function reorderAuthoringNodes(fromNodeId, toNodeId) {
  const orderedNodes = reorderArrayById(
    sortedNodesForSelectedProblem(),
    fromNodeId,
    toNodeId,
    "node_id"
  );

  orderedNodes.forEach((node, index) => {
    const assignment = assignmentForNode(node);
    if (assignment) {
      assignment.step_number = index + 1;
    }
  });

  setStatus("Reordered route steps", true);
  render();
}

function wirePreviousLinearStep(macro, newStepId) {
  const previousStep = macro.steps.at(-1);
  if (
    previousStep &&
    (previousStep.action === "include_problem" ||
      previousStep.action === "include_macro") &&
    !previousStep.next_step_id
  ) {
    previousStep.next_step_id = newStepId;
  }
}

function addWorkspaceProject() {
  if (!state.macroWorkspace) {
    return;
  }

  const projectId = createWorkspaceProjectId();
  state.macroWorkspace.projects.push({
    project_id: projectId,
    display_name: `Linked Project ${workspaceProjects().length + 1}`,
    project_file: "",
    compiled_index_file: "",
    status: "draft",
  });
  state.selectedWorkspaceProjectId = projectId;
  setMacroStatus("Added linked project", true);
  render();
}

function addMacro() {
  if (!state.macroWorkspace) {
    return;
  }

  const macroId = createMacroId();
  const stopStepId = createMacroStepId("step_stop");
  state.macroWorkspace.macros.push({
    macro_id: macroId,
    name: `New Macro ${macroDefinitions().length + 1}`,
    description: "",
    entry_step_id: stopStepId,
    steps: [
      {
        step_id: stopStepId,
        action: "stop",
        notes: "Macro complete.",
      },
    ],
    conditions: [],
    tags: [],
    status: "draft",
  });
  state.selectedMacroId = macroId;
  state.selectedMacroStepId = stopStepId;
  state.selectedMacroConditionId = null;
  setMacroStatus("Added macro", true);
  render();
}

function addProblemStep() {
  const macro = selectedMacro();
  if (!macro) {
    return;
  }

  const stepId = createMacroStepId("step_problem");
  wirePreviousLinearStep(macro, stepId);
  macro.steps.push({
    step_id: stepId,
    action: "include_problem",
    problem_ref: {
      project_id: workspaceProjects()[0]?.project_id ?? "",
      problem_name: "",
      mode: state.macroWorkspace?.runtime_defaults?.default_mode ?? "step",
      output_format:
        state.macroWorkspace?.runtime_defaults?.default_output_format ?? "txt",
      route_only: false,
    },
    next_step_id: null,
    notes: "",
  });
  if (!macro.entry_step_id) {
    macro.entry_step_id = stepId;
  }
  state.selectedMacroStepId = stepId;
  setMacroStatus("Added problem step", true);
  render();
}

function addBranchStep() {
  const macro = selectedMacro();
  if (!macro) {
    return;
  }

  if (macro.conditions.length === 0) {
    const conditionId = createConditionId();
    macro.conditions.push({
      condition_id: conditionId,
      kind: "prompt_contains_any",
      field: "prompt_text",
      operator: "contains_any",
      values: ["shipment"],
      description: "",
    });
    state.selectedMacroConditionId = conditionId;
  }

  const stepId = createMacroStepId("step_branch");
  macro.steps.push({
    step_id: stepId,
    action: "branch",
    condition_id: macro.conditions[0].condition_id,
    true_step_id: "",
    false_step_id: "",
    notes: "",
  });
  if (!macro.entry_step_id) {
    macro.entry_step_id = stepId;
  }
  state.selectedMacroStepId = stepId;
  setMacroStatus("Added branch step", true);
  render();
}

function addStopStep() {
  const macro = selectedMacro();
  if (!macro) {
    return;
  }

  const stepId = createMacroStepId("step_stop");
  wirePreviousLinearStep(macro, stepId);
  macro.steps.push({
    step_id: stepId,
    action: "stop",
    notes: "Macro complete.",
  });
  if (!macro.entry_step_id) {
    macro.entry_step_id = stepId;
  }
  state.selectedMacroStepId = stepId;
  setMacroStatus("Added stop step", true);
  render();
}

function addCondition() {
  const macro = selectedMacro();
  if (!macro) {
    return;
  }

  const conditionId = createConditionId();
  macro.conditions.push({
    condition_id: conditionId,
    kind: "prompt_contains_any",
    field: "prompt_text",
    operator: "contains_any",
    values: ["keyword"],
    description: "",
  });
  state.selectedMacroConditionId = conditionId;
  setMacroStatus("Added condition", true);
  render();
}

async function openMacroWorkspace() {
  const loaded = await window.contextWayPointApp.openMacroWorkspaceDialog();
  if (!loaded) {
    return;
  }

  await setLoadedMacroWorkspace(loaded.filePath, loaded.workspace);
  setMacroStatus("Macro workspace loaded", false);
}

async function saveMacroWorkspace() {
  if (!state.macroWorkspace) {
    return;
  }

  if (!state.macroWorkspaceFilePath) {
    await saveMacroWorkspaceAs();
    return;
  }

  await window.contextWayPointApp.saveMacroWorkspace(
    state.macroWorkspaceFilePath,
    state.macroWorkspace
  );
  setMacroStatus("Macro workspace saved", false);
}

async function saveMacroWorkspaceAs() {
  if (!state.macroWorkspace) {
    return;
  }

  const saved = await window.contextWayPointApp.saveMacroWorkspaceAs(
    state.macroWorkspace
  );
  if (!saved) {
    return;
  }

  state.macroWorkspaceFilePath = saved.filePath;
  setMacroStatus("Macro workspace saved", false);
}

async function previewSelectedMacro() {
  if (!state.macroWorkspace || !state.selectedMacroId) {
    setMacroStatus("Select a macro first", state.isMacroDirty);
    return;
  }

  setMacroStatus("Running macro preview…", state.isMacroDirty);
  const result = await window.contextWayPointApp.previewMacroWorkspace(
    state.macroWorkspace,
    state.selectedMacroId,
    state.macroPromptText
  );
  state.macroPreviewOutput = result.stdout || result.stderr || "No preview output.";
  renderMacroPreview();
  setMacroStatus("Macro preview complete", state.isMacroDirty);
}

refs.tabAuthoringButton.addEventListener("click", () => {
  state.activeTab = "authoring";
  renderTabs();
});

refs.tabMacroButton.addEventListener("click", () => {
  state.activeTab = "macro";
  renderTabs();
});

refs.problemSelect.addEventListener("change", async (event) => {
  state.selectedProblemName = event.target.value;
  ensureSelectedNodeExists();
  const node = selectedNode();
  if (node) {
    const anchor = anchorsById().get(node.anchor_id);
    if (anchor) {
      state.selectedDocumentId = anchor.document_id;
    }
  }
  resetCurrentSelection();
  render();
  await ensureSelectedDocumentLoaded();
  render();
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
      assignment.keywords = normalizeFreeTextList(event.target.value);
    }
  });
});

refs.nodeNotesInput.addEventListener("input", (event) => {
  updateSelectedNode((node) => {
    node.notes = event.target.value;
  });
});

refs.documentViewer.addEventListener("mouseup", () => updateSelectionFromViewer());
refs.documentViewer.addEventListener("keyup", () => updateSelectionFromViewer());

refs.openProjectButton.addEventListener("click", () => {
  openProject().catch((error) => {
    setStatus(`Open failed: ${error.message}`, state.isDirty);
  });
});

refs.newProjectButton.addEventListener("click", () => {
  newProject().catch((error) => {
    setStatus(`New project failed: ${error.message}`, state.isDirty);
  });
});

refs.addDocumentButton.addEventListener("click", () => {
  addSourceDocument().catch((error) => {
    setStatus(`Add document failed: ${error.message}`, state.isDirty);
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

refs.addNodeButton.addEventListener("click", () => {
  createBlankNode();
});

refs.createNodeFromSelectionButton.addEventListener("click", () => {
  createNodeFromSelection();
});

refs.applySelectionToNodeButton.addEventListener("click", () => {
  applySelectionToSelectedNode();
});

refs.buildProjectButton.addEventListener("click", () => {
  buildProject().catch((error) => {
    state.buildOutput = `Build failed:\n${error.message}`;
    renderBuildOutput();
    setStatus("Build failed", state.isDirty);
  });
});

refs.openMacroWorkspaceButton.addEventListener("click", () => {
  openMacroWorkspace().catch((error) => {
    setMacroStatus(`Open failed: ${error.message}`, state.isMacroDirty);
  });
});

refs.saveMacroWorkspaceButton.addEventListener("click", () => {
  saveMacroWorkspace().catch((error) => {
    setMacroStatus(`Save failed: ${error.message}`, state.isMacroDirty);
  });
});

refs.saveMacroWorkspaceAsButton.addEventListener("click", () => {
  saveMacroWorkspaceAs().catch((error) => {
    setMacroStatus(`Save As failed: ${error.message}`, state.isMacroDirty);
  });
});

refs.addWorkspaceProjectButton.addEventListener("click", () => addWorkspaceProject());
refs.addMacroButton.addEventListener("click", () => addMacro());
refs.addProblemStepButton.addEventListener("click", () => addProblemStep());
refs.addBranchStepButton.addEventListener("click", () => addBranchStep());
refs.addStopStepButton.addEventListener("click", () => addStopStep());
refs.addConditionButton.addEventListener("click", () => addCondition());
refs.previewMacroButton.addEventListener("click", () => {
  previewSelectedMacro().catch((error) => {
    state.macroPreviewOutput = `Macro preview failed:\n${error.message}`;
    renderMacroPreview();
    setMacroStatus("Macro preview failed", state.isMacroDirty);
  });
});

refs.workspaceProjectDisplayNameInput.addEventListener("input", (event) => {
  updateSelectedWorkspaceProject((project) => {
    project.display_name = event.target.value;
  });
});

refs.workspaceProjectSelect.addEventListener("change", () => {
  state.selectedWorkspaceProjectId = refs.workspaceProjectSelect.value || null;
  loadSelectedWorkspaceProjectReference()
    .then(() => {
      render();
    })
    .catch((error) => {
      setMacroStatus(
        `Linked project load failed: ${error.message}`,
        state.isMacroDirty
      );
    });
});

refs.workspaceProjectFileInput.addEventListener("input", (event) => {
  updateSelectedWorkspaceProject((project) => {
    project.project_file = event.target.value;
  });
});

refs.workspaceProjectFileInput.addEventListener("change", () => {
  state.linkedProjectCache.delete(state.selectedWorkspaceProjectId);
  loadSelectedWorkspaceProjectReference()
    .then(() => {
      render();
    })
    .catch((error) => {
      setMacroStatus(
        `Linked project load failed: ${error.message}`,
        state.isMacroDirty
      );
    });
});

refs.workspaceProjectIndexInput.addEventListener("input", (event) => {
  updateSelectedWorkspaceProject((project) => {
    project.compiled_index_file = event.target.value;
  });
});

refs.workspaceProjectStatusInput.addEventListener("input", (event) => {
  updateSelectedWorkspaceProject((project) => {
    project.status = event.target.value;
  });
});

refs.macroNameInput.addEventListener("input", (event) => {
  updateSelectedMacro((macro) => {
    macro.name = event.target.value;
  });
});

refs.macroDescriptionInput.addEventListener("input", (event) => {
  updateSelectedMacro((macro) => {
    macro.description = event.target.value;
  });
});

refs.macroEntryStepSelect.addEventListener("change", (event) => {
  updateSelectedMacro((macro) => {
    macro.entry_step_id = event.target.value;
  });
});

refs.macroStatusInput.addEventListener("input", (event) => {
  updateSelectedMacro((macro) => {
    macro.status = event.target.value;
  });
});

refs.macroTagsInput.addEventListener("input", (event) => {
  updateSelectedMacro((macro) => {
    macro.tags = normalizeFreeTextList(event.target.value);
  });
});

refs.macroStepIdInput.addEventListener("input", (event) => {
  const previousStepId = state.selectedMacroStepId;
  updateSelectedMacroStep((step) => {
    step.step_id = event.target.value;
  });
  if (previousStepId) {
    state.selectedMacroStepId = refs.macroStepIdInput.value || previousStepId;
  }
});

refs.macroStepActionSelect.addEventListener("change", (event) => {
  updateSelectedMacroStep((step) => {
    step.action = event.target.value;
    if (step.action === "include_problem") {
      step.problem_ref = ensureProblemRef(step);
      step.macro_id = null;
      step.condition_id = null;
      step.true_step_id = null;
      step.false_step_id = null;
    } else if (step.action === "include_macro") {
      step.problem_ref = null;
      step.condition_id = null;
      step.true_step_id = null;
      step.false_step_id = null;
      step.next_step_id = step.next_step_id ?? "";
    } else if (step.action === "branch") {
      step.problem_ref = null;
      step.macro_id = null;
      step.next_step_id = null;
      step.condition_id = macroConditions()[0]?.condition_id ?? "";
      step.true_step_id = step.true_step_id ?? "";
      step.false_step_id = step.false_step_id ?? "";
    } else if (step.action === "stop") {
      step.problem_ref = null;
      step.macro_id = null;
      step.condition_id = null;
      step.next_step_id = null;
      step.true_step_id = null;
      step.false_step_id = null;
    }
  });
});

refs.macroStepProjectSelect.addEventListener("change", (event) => {
  updateSelectedMacroStep((step) => {
    ensureProblemRef(step).project_id = event.target.value;
  });
});

refs.macroStepProblemInput.addEventListener("input", (event) => {
  updateSelectedMacroStep((step) => {
    ensureProblemRef(step).problem_name = event.target.value;
  });
});

refs.macroStepModeSelect.addEventListener("change", (event) => {
  updateSelectedMacroStep((step) => {
    ensureProblemRef(step).mode = event.target.value;
  });
});

refs.macroStepFormatSelect.addEventListener("change", (event) => {
  updateSelectedMacroStep((step) => {
    ensureProblemRef(step).output_format = event.target.value;
  });
});

refs.macroStepRouteOnlyInput.addEventListener("change", (event) => {
  updateSelectedMacroStep((step) => {
    ensureProblemRef(step).route_only = event.target.checked;
  });
});

refs.macroStepNestedMacroSelect.addEventListener("change", (event) => {
  updateSelectedMacroStep((step) => {
    step.macro_id = event.target.value;
  });
});

refs.macroStepConditionSelect.addEventListener("change", (event) => {
  updateSelectedMacroStep((step) => {
    step.condition_id = event.target.value;
  });
});

refs.macroStepNextSelect.addEventListener("change", (event) => {
  updateSelectedMacroStep((step) => {
    step.next_step_id = event.target.value || null;
  });
});

refs.macroStepTrueSelect.addEventListener("change", (event) => {
  updateSelectedMacroStep((step) => {
    step.true_step_id = event.target.value || null;
  });
});

refs.macroStepFalseSelect.addEventListener("change", (event) => {
  updateSelectedMacroStep((step) => {
    step.false_step_id = event.target.value || null;
  });
});

refs.macroStepNotesInput.addEventListener("input", (event) => {
  updateSelectedMacroStep((step) => {
    step.notes = event.target.value;
  });
});

refs.macroConditionIdInput.addEventListener("input", (event) => {
  const previousConditionId = state.selectedMacroConditionId;
  updateSelectedMacroCondition((condition) => {
    condition.condition_id = event.target.value;
  });
  if (previousConditionId) {
    state.selectedMacroConditionId =
      refs.macroConditionIdInput.value || previousConditionId;
  }
});

refs.macroConditionKindSelect.addEventListener("change", (event) => {
  updateSelectedMacroCondition((condition) => {
    condition.kind = event.target.value;
  });
});

refs.macroConditionFieldInput.addEventListener("input", (event) => {
  updateSelectedMacroCondition((condition) => {
    condition.field = event.target.value;
  });
});

refs.macroConditionOperatorInput.addEventListener("input", (event) => {
  updateSelectedMacroCondition((condition) => {
    condition.operator = event.target.value;
  });
});

refs.macroConditionValuesInput.addEventListener("input", (event) => {
  updateSelectedMacroCondition((condition) => {
    condition.values = normalizeFreeTextList(event.target.value);
  });
});

refs.macroConditionDescriptionInput.addEventListener("input", (event) => {
  updateSelectedMacroCondition((condition) => {
    condition.description = event.target.value;
  });
});

refs.macroPromptInput.addEventListener("input", (event) => {
  state.macroPromptText = event.target.value;
});

refs.contextMenuCopy.addEventListener("click", () => {
  copyTarget(state.contextMenu.target ?? state.selectedTarget).catch((error) => {
    if (state.activeTab === "authoring") {
      setStatus(`Copy failed: ${error.message}`, state.isDirty);
    } else {
      setMacroStatus(`Copy failed: ${error.message}`, state.isMacroDirty);
    }
  });
  hideContextMenu();
});

refs.contextMenuCut.addEventListener("click", () => {
  cutTarget(state.contextMenu.target ?? state.selectedTarget).catch((error) => {
    if (state.activeTab === "authoring") {
      setStatus(`Cut failed: ${error.message}`, state.isDirty);
    } else {
      setMacroStatus(`Cut failed: ${error.message}`, state.isMacroDirty);
    }
  });
});

refs.contextMenuDelete.addEventListener("click", () => {
  deleteTarget(state.contextMenu.target ?? state.selectedTarget);
});

document.addEventListener("click", (event) => {
  if (!refs.contextMenu.contains(event.target)) {
    hideContextMenu();
  }
});

document.addEventListener("contextmenu", (event) => {
  const targetElement = event.target;
  if (!targetElement.closest(".stack-card")) {
    hideContextMenu();
  }
});

document.addEventListener("keydown", (event) => {
  if (isEditableElement(document.activeElement)) {
    return;
  }

  if (event.key === "Delete" || event.key === "Backspace") {
    if (deleteTarget(state.selectedTarget)) {
      event.preventDefault();
    }
  }
});

async function initialize() {
  try {
    const [loadedProject, loadedWorkspace] = await Promise.all([
      window.contextWayPointApp.loadDefaultProject(),
      window.contextWayPointApp.loadDefaultMacroWorkspace(),
    ]);

    await setLoadedProject(loadedProject.filePath, loadedProject.project);
    setStatus("Loaded default example project", false);
    await setLoadedMacroWorkspace(loadedWorkspace.filePath, loadedWorkspace.workspace);
    setMacroStatus("Loaded default macro workspace", false);
  } catch (error) {
    state.buildOutput = `Initialization failed:\n${error.message}`;
    state.macroPreviewOutput = `Initialization failed:\n${error.message}`;
    setStatus("Initialization failed", false);
    setMacroStatus("Initialization failed", false);
    render();
  }
}

initialize();

import { app, BrowserWindow, dialog, ipcMain } from "electron";
import { promises as fs } from "node:fs";
import path from "node:path";
import os from "node:os";
import { createHash } from "node:crypto";
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { fileURLToPath } from "node:url";

const execFileAsync = promisify(execFile);

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const REPO_ROOT = path.resolve(__dirname, "..", "..");
const DEFAULT_PROJECT_FILE = path.join(
  REPO_ROOT,
  "docs",
  "examples",
  "authoringShellProject.example.json"
);
const DEFAULT_MACRO_WORKSPACE_FILE = path.join(
  REPO_ROOT,
  "docs",
  "examples",
  "orderFulfillmentMacroWorkspace.example.json"
);
const GENERATED_YAML_DIR = path.join(REPO_ROOT, "output", "generatedYaml");
const COMPILED_JSON_FILE = path.join(REPO_ROOT, "output", "contextIndex.json");
const SUPPORTED_TEXT_FILE_TYPES = new Set([".md", ".txt"]);

function nowIso() {
  return new Date().toISOString();
}

function defaultEmptyProject(projectName) {
  const timestamp = nowIso();
  return {
    version: "0.1",
    project_name: projectName,
    created_at: timestamp,
    updated_at: timestamp,
    documents: [],
    anchors: [],
    nodes: [],
    edges: [],
    problems: [
      {
        problem_name: "New Problem",
        description: "",
        entry_node_id: null,
        node_ids: [],
        status: "draft",
      },
    ],
    export_preferences: {
      target_format: "yaml",
      preserve_source_path: true,
    },
  };
}

function createWindow() {
  const window = new BrowserWindow({
    width: 1500,
    height: 980,
    minWidth: 1180,
    minHeight: 760,
    backgroundColor: "#f5efe4",
    webPreferences: {
      preload: path.join(__dirname, "preload.cjs"),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  window.loadFile(path.join(__dirname, "renderer", "index.html"));
}

async function pathExists(targetPath) {
  try {
    await fs.access(targetPath);
    return true;
  } catch {
    return false;
  }
}

async function detectPythonExecutable() {
  const candidates = [
    path.join(REPO_ROOT, ".venv", "bin", "python"),
    path.join(REPO_ROOT, ".venv", "Scripts", "python.exe"),
    "python3",
    "python",
  ];

  for (const candidate of candidates) {
    if (candidate === "python3" || candidate === "python") {
      return candidate;
    }

    if (await pathExists(candidate)) {
      return candidate;
    }
  }

  throw new Error("Could not locate a Python interpreter for contextWayPoint");
}

async function writeTemporaryProject(projectPayload) {
  return writeTemporaryJsonPayload(
    projectPayload,
    "contextwaypoint-authoring-",
    "project.json"
  );
}

async function writeTemporaryMacroWorkspace(workspacePayload) {
  return writeTemporaryJsonPayload(
    workspacePayload,
    "contextwaypoint-macro-",
    "macroWorkspace.json"
  );
}

async function writeTemporaryJsonPayload(payload, tempPrefix, fileName) {
  const tempDir = await fs.mkdtemp(
    path.join(os.tmpdir(), tempPrefix)
  );
  const filePath = path.join(tempDir, fileName);
  await fs.writeFile(
    filePath,
    JSON.stringify(payload, null, 2),
    "utf-8"
  );

  return {
    tempDir,
    filePath,
  };
}

function resolveSourcePath(sourcePath) {
  if (path.isAbsolute(sourcePath)) {
    return sourcePath;
  }

  return path.join(REPO_ROOT, sourcePath);
}

async function resolveJsonReferencePath(targetPath, baseDir = null) {
  if (path.isAbsolute(targetPath)) {
    return targetPath;
  }

  const candidatePaths = [];
  if (baseDir) {
    candidatePaths.push(path.join(baseDir, targetPath));
  }
  candidatePaths.push(path.join(REPO_ROOT, targetPath));

  for (const candidate of candidatePaths) {
    if (await pathExists(candidate)) {
      return candidate;
    }
  }

  return candidatePaths[0] ?? targetPath;
}

async function readSourceDocument(sourcePath) {
  const resolvedPath = resolveSourcePath(sourcePath);
  const extension = path.extname(resolvedPath).toLowerCase();
  const supportedText = SUPPORTED_TEXT_FILE_TYPES.has(extension);
  const fileBuffer = await fs.readFile(resolvedPath);
  const fileStats = await fs.stat(resolvedPath);

  return {
    sourcePath,
    resolvedPath,
    displayName: path.basename(resolvedPath),
    fileType: extension.replace(".", "") || "text",
    supportedText,
    content: supportedText ? fileBuffer.toString("utf-8") : "",
    sha256: createHash("sha256").update(fileBuffer).digest("hex"),
    modifiedAt: fileStats.mtime.toISOString(),
    sizeBytes: fileStats.size,
  };
}

async function runContextwaypoint(args) {
  const pythonExecutable = await detectPythonExecutable();
  const { stdout, stderr } = await execFileAsync(
    pythonExecutable,
    ["-m", "contextwaypoint", ...args],
    {
      cwd: REPO_ROOT,
      maxBuffer: 1024 * 1024 * 8,
    }
  );

  return {
    stdout: stdout.trimEnd(),
    stderr: stderr.trimEnd(),
  };
}

async function withTemporaryProject(projectPayload, callback) {
  const { tempDir, filePath } = await writeTemporaryProject(projectPayload);

  try {
    return await callback(filePath);
  } finally {
    await fs.rm(tempDir, { recursive: true, force: true });
  }
}

async function withTemporaryMacroWorkspace(workspacePayload, callback) {
  const { tempDir, filePath } = await writeTemporaryMacroWorkspace(workspacePayload);

  try {
    return await callback(filePath);
  } finally {
    await fs.rm(tempDir, { recursive: true, force: true });
  }
}

async function loadJsonFile(filePath) {
  const contents = await fs.readFile(filePath, "utf-8");
  return {
    filePath,
    project: JSON.parse(contents),
  };
}

async function loadProjectFile(projectFile) {
  return loadJsonFile(projectFile);
}

async function loadMacroWorkspaceFile(workspaceFile) {
  const loaded = await loadJsonFile(workspaceFile);
  return {
    filePath: loaded.filePath,
    workspace: loaded.project,
  };
}

ipcMain.handle("app:get-default-project-path", async () => {
  return DEFAULT_PROJECT_FILE;
});

ipcMain.handle("app:get-default-macro-workspace-path", async () => {
  return DEFAULT_MACRO_WORKSPACE_FILE;
});

ipcMain.handle("project:open-dialog", async () => {
  const result = await dialog.showOpenDialog({
    title: "Open contextWayPoint project",
    defaultPath: DEFAULT_PROJECT_FILE,
    filters: [{ name: "Project JSON", extensions: ["json"] }],
    properties: ["openFile"],
  });

  if (result.canceled || result.filePaths.length === 0) {
    return null;
  }

  return loadProjectFile(result.filePaths[0]);
});

ipcMain.handle("project:new-dialog", async () => {
  const documentsDir = app.getPath("documents");
  const defaultName = "New Context Project";
  const result = await dialog.showSaveDialog({
    title: "Create contextWayPoint project",
    defaultPath: path.join(documentsDir, `${defaultName}.project.json`),
    filters: [{ name: "Project JSON", extensions: ["json"] }],
  });

  if (result.canceled || !result.filePath) {
    return null;
  }

  const rawSelectedPath = result.filePath;
  const selectedDirectory = path.dirname(rawSelectedPath);
  const selectedFileName = path.basename(rawSelectedPath);
  const projectBaseName = path
    .basename(selectedFileName, path.extname(selectedFileName))
    .replace(/\.project$/i, "")
    .trim() || defaultName;
  const projectFolder = path.join(selectedDirectory, projectBaseName);
  const projectFile = path.join(
    projectFolder,
    `${projectBaseName}.project.json`
  );
  const project = defaultEmptyProject(projectBaseName);

  await fs.mkdir(projectFolder, { recursive: true });
  await fs.writeFile(projectFile, JSON.stringify(project, null, 2), "utf-8");

  return {
    filePath: projectFile,
    project,
  };
});

ipcMain.handle("project:load-default", async () => {
  return loadProjectFile(DEFAULT_PROJECT_FILE);
});

ipcMain.handle("project:load-file", async (_event, filePath) => {
  return loadProjectFile(filePath);
});

ipcMain.handle("project:load-reference-file", async (_event, payload) => {
  const { filePath, baseDir } = payload;
  const resolvedPath = await resolveJsonReferencePath(filePath, baseDir);
  return loadProjectFile(resolvedPath);
});

ipcMain.handle("project:save", async (_event, payload) => {
  const { filePath, project } = payload;
  if (!filePath) {
    throw new Error("project:save requires a filePath");
  }

  await fs.writeFile(filePath, JSON.stringify(project, null, 2), "utf-8");
  return { filePath };
});

ipcMain.handle("project:save-as", async (_event, project) => {
  const result = await dialog.showSaveDialog({
    title: "Save contextWayPoint project",
    defaultPath: DEFAULT_PROJECT_FILE,
    filters: [{ name: "Project JSON", extensions: ["json"] }],
  });

  if (result.canceled || !result.filePath) {
    return null;
  }

  await fs.writeFile(
    result.filePath,
    JSON.stringify(project, null, 2),
    "utf-8"
  );

  return { filePath: result.filePath };
});

ipcMain.handle("macro:open-dialog", async () => {
  const result = await dialog.showOpenDialog({
    title: "Open contextWayPoint macro workspace",
    defaultPath: DEFAULT_MACRO_WORKSPACE_FILE,
    filters: [{ name: "Macro Workspace JSON", extensions: ["json"] }],
    properties: ["openFile"],
  });

  if (result.canceled || result.filePaths.length === 0) {
    return null;
  }

  return loadMacroWorkspaceFile(result.filePaths[0]);
});

ipcMain.handle("macro:load-default", async () => {
  return loadMacroWorkspaceFile(DEFAULT_MACRO_WORKSPACE_FILE);
});

ipcMain.handle("macro:load-file", async (_event, filePath) => {
  return loadMacroWorkspaceFile(filePath);
});

ipcMain.handle("macro:save", async (_event, payload) => {
  const { filePath, workspace } = payload;
  if (!filePath) {
    throw new Error("macro:save requires a filePath");
  }

  await fs.writeFile(filePath, JSON.stringify(workspace, null, 2), "utf-8");
  return { filePath };
});

ipcMain.handle("macro:save-as", async (_event, workspace) => {
  const result = await dialog.showSaveDialog({
    title: "Save contextWayPoint macro workspace",
    defaultPath: DEFAULT_MACRO_WORKSPACE_FILE,
    filters: [{ name: "Macro Workspace JSON", extensions: ["json"] }],
  });

  if (result.canceled || !result.filePath) {
    return null;
  }

  await fs.writeFile(
    result.filePath,
    JSON.stringify(workspace, null, 2),
    "utf-8"
  );

  return { filePath: result.filePath };
});

ipcMain.handle("project:render-yaml", async (_event, payload) => {
  const { project, problemName } = payload;

  return withTemporaryProject(project, async (projectFile) => {
    const args = ["project-render", projectFile];

    if (problemName) {
      args.push("--problem", problemName);
    }

    const { stdout } = await runContextwaypoint(args);
    return stdout;
  });
});

ipcMain.handle("project:build", async (_event, payload) => {
  const { project } = payload;

  return withTemporaryProject(project, async (projectFile) => {
    const { stdout, stderr } = await runContextwaypoint([
      "project-build",
      projectFile,
      "--yaml-out",
      GENERATED_YAML_DIR,
      "--json-out",
      COMPILED_JSON_FILE,
    ]);

    return {
      stdout,
      stderr,
      generatedYamlDir: GENERATED_YAML_DIR,
      compiledJsonFile: COMPILED_JSON_FILE,
    };
  });
});

ipcMain.handle("macro:preview", async (_event, payload) => {
  const { workspace, macroId, promptText } = payload;

  return withTemporaryMacroWorkspace(workspace, async (workspaceFile) => {
    const { stdout, stderr } = await runContextwaypoint([
      "macro-preview",
      workspaceFile,
      "--macro",
      macroId,
      "--prompt",
      promptText ?? "",
    ]);

    return {
      stdout,
      stderr,
      workspaceFile,
    };
  });
});

ipcMain.handle("document:open-dialog", async () => {
  const result = await dialog.showOpenDialog({
    title: "Add source document",
    defaultPath: REPO_ROOT,
    filters: [
      { name: "Text and Markdown", extensions: ["md", "txt"] },
    ],
    properties: ["openFile"],
  });

  if (result.canceled || result.filePaths.length === 0) {
    return null;
  }

  return readSourceDocument(result.filePaths[0]);
});

ipcMain.handle("document:read", async (_event, sourcePath) => {
  return readSourceDocument(sourcePath);
});

app.whenReady().then(() => {
  createWindow();

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});

import { app, BrowserWindow, dialog, ipcMain } from "electron";
import { promises as fs } from "node:fs";
import path from "node:path";
import os from "node:os";
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
  "orderFulfillmentProject.example.json"
);
const GENERATED_YAML_DIR = path.join(REPO_ROOT, "output", "generatedYaml");
const COMPILED_JSON_FILE = path.join(REPO_ROOT, "output", "contextIndex.json");

function createWindow() {
  const window = new BrowserWindow({
    width: 1500,
    height: 980,
    minWidth: 1180,
    minHeight: 760,
    backgroundColor: "#f5efe4",
    webPreferences: {
      preload: path.join(__dirname, "preload.mjs"),
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
  const tempDir = await fs.mkdtemp(
    path.join(os.tmpdir(), "contextwaypoint-authoring-")
  );
  const projectFile = path.join(tempDir, "project.json");
  await fs.writeFile(
    projectFile,
    JSON.stringify(projectPayload, null, 2),
    "utf-8"
  );

  return {
    tempDir,
    projectFile,
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
  const { tempDir, projectFile } = await writeTemporaryProject(projectPayload);

  try {
    return await callback(projectFile);
  } finally {
    await fs.rm(tempDir, { recursive: true, force: true });
  }
}

async function loadProjectFile(projectFile) {
  const contents = await fs.readFile(projectFile, "utf-8");
  return {
    filePath: projectFile,
    project: JSON.parse(contents),
  };
}

ipcMain.handle("app:get-default-project-path", async () => {
  return DEFAULT_PROJECT_FILE;
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

ipcMain.handle("project:load-default", async () => {
  return loadProjectFile(DEFAULT_PROJECT_FILE);
});

ipcMain.handle("project:load-file", async (_event, filePath) => {
  return loadProjectFile(filePath);
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

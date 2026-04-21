const { clipboard, contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("contextWayPointApp", {
  getDefaultProjectPath: () => ipcRenderer.invoke("app:get-default-project-path"),
  getDefaultMacroWorkspacePath: () =>
    ipcRenderer.invoke("app:get-default-macro-workspace-path"),
  openProjectDialog: () => ipcRenderer.invoke("project:open-dialog"),
  newProjectDialog: () => ipcRenderer.invoke("project:new-dialog"),
  loadDefaultProject: () => ipcRenderer.invoke("project:load-default"),
  loadProjectFile: (filePath) => ipcRenderer.invoke("project:load-file", filePath),
  loadReferencedProjectFile: (filePath, baseDir) =>
    ipcRenderer.invoke("project:load-reference-file", { filePath, baseDir }),
  saveProject: (filePath, project) =>
    ipcRenderer.invoke("project:save", { filePath, project }),
  saveProjectAs: (project) => ipcRenderer.invoke("project:save-as", project),
  renderYaml: (project, problemName) =>
    ipcRenderer.invoke("project:render-yaml", { project, problemName }),
  buildProject: (project) => ipcRenderer.invoke("project:build", { project }),
  openMacroWorkspaceDialog: () => ipcRenderer.invoke("macro:open-dialog"),
  loadDefaultMacroWorkspace: () => ipcRenderer.invoke("macro:load-default"),
  loadMacroWorkspaceFile: (filePath) => ipcRenderer.invoke("macro:load-file", filePath),
  saveMacroWorkspace: (filePath, workspace) =>
    ipcRenderer.invoke("macro:save", { filePath, workspace }),
  saveMacroWorkspaceAs: (workspace) => ipcRenderer.invoke("macro:save-as", workspace),
  previewMacroWorkspace: (workspace, macroId, promptText) =>
    ipcRenderer.invoke("macro:preview", { workspace, macroId, promptText }),
  openSourceDocumentDialog: () => ipcRenderer.invoke("document:open-dialog"),
  readSourceDocument: (sourcePath) => ipcRenderer.invoke("document:read", sourcePath),
  writeClipboardText: (text) => clipboard.writeText(text),
});

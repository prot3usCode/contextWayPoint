import { contextBridge, ipcRenderer } from "electron";

contextBridge.exposeInMainWorld("contextWayPointApp", {
  getDefaultProjectPath: () => ipcRenderer.invoke("app:get-default-project-path"),
  openProjectDialog: () => ipcRenderer.invoke("project:open-dialog"),
  loadDefaultProject: () => ipcRenderer.invoke("project:load-default"),
  loadProjectFile: (filePath) => ipcRenderer.invoke("project:load-file", filePath),
  saveProject: (filePath, project) =>
    ipcRenderer.invoke("project:save", { filePath, project }),
  saveProjectAs: (project) => ipcRenderer.invoke("project:save-as", project),
  renderYaml: (project, problemName) =>
    ipcRenderer.invoke("project:render-yaml", { project, problemName }),
  buildProject: (project) => ipcRenderer.invoke("project:build", { project }),
});

'use strict'
const { contextBridge, ipcRenderer } = require('electron')
// A small capability surface. Never expose ipcRenderer, Node, paths, or a shell.
contextBridge.exposeInMainWorld('bidoytu', {
  request: (method, params = {}) => ipcRenderer.invoke('backend:request', method, params),
  onEvent: (callback) => {
    const listener = (_event, data) => callback(data)
    ipcRenderer.on('backend:event', listener)
    return () => ipcRenderer.removeListener('backend:event', listener)
  },
  exportCertificate: () => ipcRenderer.invoke('certificate:export'),
  listBrowsers: () => ipcRenderer.invoke('browser:list'),
  openBrowser: (id) => ipcRenderer.invoke('browser:open', id),
  copyText: (text) => ipcRenderer.invoke('clipboard:write', text),
  window: (action) => ipcRenderer.send('window:action', action),
  listSessions: () => ipcRenderer.invoke('session:list'),
  createSession: (name) => ipcRenderer.invoke('session:create', name),
  deleteSession: (id) => ipcRenderer.invoke('session:delete', id),
  openSession: (id) => ipcRenderer.invoke('session:open', id),
  onAppCloseRequest: (callback) => {
    const listener = () => callback()
    ipcRenderer.on('app:close-request', listener)
    return () => ipcRenderer.removeListener('app:close-request', listener)
  },
  onSessionOpened: (callback) => {
    const listener = (_event, session) => callback(session)
    ipcRenderer.on('session:opened', listener)
    return () => ipcRenderer.removeListener('session:opened', listener)
  },
  closeDecision: (decision) => ipcRenderer.invoke('app:close-decision', decision),
})

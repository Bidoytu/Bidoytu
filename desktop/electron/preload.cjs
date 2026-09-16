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
  copyText: (text) => ipcRenderer.invoke('clipboard:write', text),
  window: (action) => ipcRenderer.send('window:action', action),
})

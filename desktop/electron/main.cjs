'use strict'
const { app, BrowserWindow, Menu, ipcMain, dialog, session, clipboard } = require('electron')
const { join, resolve } = require('node:path')
const { existsSync } = require('node:fs')
const { writeFile } = require('node:fs/promises')
const { pathToFileURL } = require('node:url')
const { Backend, METHODS } = require('./backend.cjs')

let window,
  backend,
  closing = false
const root = resolve(__dirname, '../..')
const development = !app.isPackaged && process.env.BIDOYTU_DEV === '1'
const entry = development
  ? 'http://127.0.0.1:5173/'
  : pathToFileURL(join(__dirname, '../dist/index.html')).href

function trusted(event) {
  if (
    !window ||
    event.sender !== window.webContents ||
    event.senderFrame !== window.webContents.mainFrame ||
    event.senderFrame.url !== entry
  )
    throw new Error('Untrusted IPC sender')
}

function configureMenu() {
  // The default menu binds Ctrl+R/F5 to "Reload", which would swallow the
  // renderer's Ctrl+R "Send to Repeater" shortcut. Keep editing/window roles
  // but omit the reload accelerators so key events reach the page.
  const template = [
    ...(process.platform === 'darwin' ? [{ role: 'appMenu' }] : []),
    { role: 'editMenu' },
    {
      label: 'View',
      submenu: [
        { role: 'toggleDevTools' },
        { type: 'separator' },
        { role: 'resetZoom' },
        { role: 'zoomIn' },
        { role: 'zoomOut' },
      ],
    },
    { role: 'windowMenu' },
  ]
  Menu.setApplicationMenu(Menu.buildFromTemplate(template))
}

function startBackend() {
  const executable = process.platform === 'win32' ? 'python.exe' : 'python'
  const candidates = [
    join(root, '.venv', process.platform === 'win32' ? 'Scripts' : 'bin', executable),
    join(root, 'venv', process.platform === 'win32' ? 'Scripts' : 'bin', executable),
  ]
  const command = app.isPackaged
    ? join(
        process.resourcesPath,
        'backend',
        process.platform === 'win32' ? 'bidoytu-backend.exe' : 'bidoytu-backend',
      )
    : process.env.BIDOYTU_PYTHON ||
      candidates.find(existsSync) ||
      (process.platform === 'win32' ? 'python' : 'python3')
  const args = app.isPackaged ? [] : ['-u', '-m', 'bidoytu.backend']
  // Electron workspaces have their own directory; old Qt databases are preserved.
  args.push(
    '--data-dir',
    process.env.BIDOYTU_DATA_DIR || join(app.getPath('userData'), 'workspaces', 'default'),
  )
  backend = new Backend(command, args, {
    cwd: app.isPackaged ? process.resourcesPath : root,
    env: { ...process.env, PYTHONPATH: join(root, 'src'), PYTHONUTF8: '1' },
  })
  backend.on('changed', (data) => {
    if (window && !window.isDestroyed())
      window.webContents.send('backend:event', { type: 'changed', data })
  })
  backend.on('failure', (error) => {
    if (!closing && window && !window.isDestroyed())
      window.webContents.send('backend:event', { type: 'offline', message: error.message })
  })
  backend.ready.catch(() => {})
}

function createWindow() {
  window = new BrowserWindow({
    width: 1480,
    height: 940,
    minWidth: 1000,
    minHeight: 680,
    backgroundColor: '#101215',
    frame: false,
    show: false,
    title: 'Bidoytu',
    icon: app.isPackaged
      ? join(process.resourcesPath, 'logo.png')
      : join(root, 'src/bidoytu/assets/logo.png'),
    webPreferences: {
      preload: join(__dirname, 'preload.cjs'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
      webSecurity: true,
      spellcheck: false,
      backgroundThrottling: false,
      offscreen: process.env.BIDOYTU_TEST === '1',
    },
  })
  window.webContents.setWindowOpenHandler(() => ({ action: 'deny' }))
  window.webContents.on('will-navigate', (event, url) => {
    if (url !== entry) event.preventDefault()
  })
  window.webContents.on('will-attach-webview', (event) => event.preventDefault())
  window.once('ready-to-show', () => {
    if (process.env.BIDOYTU_TEST !== '1') window.show()
  })
  window.loadURL(entry)
}

if (!app.requestSingleInstanceLock()) app.quit()
else {
  app.on('second-instance', () => {
    if (window) {
      if (window.isMinimized()) window.restore()
      window.focus()
    }
  })
  app.whenReady().then(() => {
    configureMenu()
    session.defaultSession.setPermissionRequestHandler((_contents, _permission, callback) =>
      callback(false),
    )
    session.defaultSession.setPermissionCheckHandler(() => false)
    ipcMain.handle('backend:request', async (event, method, params) => {
      trusted(event)
      if (!METHODS.has(method) || !params || typeof params !== 'object' || Array.isArray(params))
        throw new Error('Invalid desktop command')
      await backend.ready
      return backend.request(method, params)
    })
    ipcMain.handle('certificate:export', async (event) => {
      trusted(event)
      await backend.ready
      const certificate = await backend.request('certificate.read')
      const result = await dialog.showSaveDialog(window, {
        title: 'Export public proxy CA',
        defaultPath: 'bidoytu-ca-cert.pem',
        filters: [{ name: 'Public certificate', extensions: ['pem'] }],
      })
      if (result.canceled || !result.filePath) return false
      await writeFile(result.filePath, certificate, 'utf8')
      return true
    })
    ipcMain.handle('browser:list', async (event) => {
      trusted(event)
      await backend.ready
      return backend.request('browser.list')
    })
    ipcMain.handle('browser:open', async (event, id) => {
      trusted(event)
      if (!Number.isInteger(id) || id < 0) throw new Error('Invalid browser selection')
      await backend.ready
      return backend.request('browser.open', { id })
    })
    ipcMain.handle('clipboard:write', (event, text) => {
      trusted(event)
      if (typeof text !== 'string' || Buffer.byteLength(text) > 2 * 1024 * 1024)
        throw new Error('Clipboard text exceeds 2 MiB')
      clipboard.writeText(text)
      return true
    })
    ipcMain.on('window:action', (event, action) => {
      trusted(event)
      if (action === 'minimize') window.minimize()
      if (action === 'maximize') window.isMaximized() ? window.unmaximize() : window.maximize()
      if (action === 'close') window.close()
    })
    startBackend()
    createWindow()
  })
  app.on('window-all-closed', () => app.quit())
  app.on('before-quit', (event) => {
    if (!closing && backend) {
      event.preventDefault()
      closing = true
      backend.stop().finally(() => app.quit())
    }
  })
}

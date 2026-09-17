'use strict'
const { app, BrowserWindow, Menu, ipcMain, dialog, session, clipboard } = require('electron')
const { join, resolve } = require('node:path')
const { existsSync } = require('node:fs')
const { writeFile, readFile, mkdir, rm } = require('node:fs/promises')
const { pathToFileURL } = require('node:url')
const { Backend, METHODS } = require('./backend.cjs')

let window, backend, closing = false, closePromptPending = false, activeSession
const root = resolve(__dirname, '../..')
const appData = join(app.getPath('userData'), 'workspaces')
const sessionsDir = join(appData, 'sessions')
const registryPath = join(appData, 'sessions.json')
const caDir = join(app.getPath('userData'), 'ca')
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

async function readSessions() {
  let entries = []
  try { entries = JSON.parse(await readFile(registryPath, 'utf8')) } catch {}
  if (!Array.isArray(entries)) entries = []
  return entries.filter((item) => item && typeof item.id === 'string' && typeof item.name === 'string' && existsSync(join(sessionsDir, item.id)))
}

async function writeSessions(entries) {
  await mkdir(appData, { recursive: true })
  await writeFile(`${registryPath}.tmp`, JSON.stringify(entries, null, 2))
  const { rename } = require('node:fs/promises')
  await rename(`${registryPath}.tmp`, registryPath)
}

async function startBackend(sessionPath) {
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
  args.push('--data-dir', sessionPath, '--ca-dir', caDir)
  const instance = new Backend(command, args, {
    cwd: app.isPackaged ? process.resourcesPath : root,
    env: { ...process.env, PYTHONPATH: join(root, 'src'), PYTHONUTF8: '1' },
  })
  backend = instance
  instance.on('changed', (data) => {
    if (window && !window.isDestroyed())
      window.webContents.send('backend:event', { type: 'changed', data })
  })
  instance.on('ready', (data) => {
    if (window && !window.isDestroyed()) window.webContents.send('backend:event', { type: 'ready', data })
  })
  instance.on('failure', (error) => {
    if (!closing && backend === instance && window && !window.isDestroyed())
      window.webContents.send('backend:event', { type: 'offline', message: error.message })
  })
  try {
    await instance.ready
    return instance
  } catch (error) {
    if (backend === instance) backend = undefined
    throw error
  }
}

// Terminate any browsers the current session launched and wait for them to
// exit before the backend goes away. Called on every shutdown path so a
// launched browser is always closed before the app quits, and so its profile
// files are released before a session directory is removed on Windows.
async function stopBrowsers() {
  if (!backend) return
  try {
    await backend.request('browser.stop')
  } catch {
    // Best effort: the backend may already be gone or never opened a browser.
  }
}

async function stopBackend() {
  if (!backend) return
  const current = backend
  backend = undefined
  await current.stop()
}

async function removeWithRetry(path) {
  for (let attempt = 0; ; attempt += 1) {
    try {
      await rm(path, { recursive: true, force: true })
      return
    } catch (error) {
      const retryable = process.platform === 'win32' &&
        (error.code === 'EBUSY' || error.code === 'EPERM' || error.code === 'ENOTEMPTY')
      // ~15s of retries: browser child processes can hold profile SQLite files
      // for several seconds after taskkill returns before Windows releases them.
      if (!retryable || attempt >= 60) throw error
      await new Promise((resolve) => setTimeout(resolve, 250))
    }
  }
}

function maximizeWindow() {
  if (window && !window.isDestroyed() && !window.isMaximized()) window.maximize()
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
      // The renderer probes state and polls read-only data while the startup
      // session picker is visible, and briefly during a session switch/close
      // window before it observes the backend going offline. A missing backend
      // is expected for these, so resolve quietly instead of throwing (which
      // Electron would log as a handler error).
      if (!backend) {
        const idleSafe = new Set([
          'state',
          'history.list',
          'history.detail',
          'intruder.results',
          'audit.list',
          'workspace.load',
        ])
        if (idleSafe.has(method)) return null
        throw new Error('Open a session before using the workspace.')
      }
      await backend.ready
      return backend.request(method, params)
    })
    ipcMain.handle('session:list', async (event) => { trusted(event); return readSessions() })
    ipcMain.handle('session:create', async (event, name) => {
      trusted(event)
      if (typeof name !== 'string' || !name.trim() || name.length > 120) throw new Error('Enter a session name up to 120 characters.')
      const now = new Date().toISOString()
      const item = { id: require('node:crypto').randomUUID(), name: name.trim(), created_at: now, updated_at: now }
      await mkdir(sessionsDir, { recursive: true })
      await mkdir(join(sessionsDir, item.id), { recursive: false })
      await writeSessions([...(await readSessions()), item])
      await stopBackend()
      activeSession = item
      await startBackend(join(sessionsDir, item.id))
      maximizeWindow()
      event.sender.send('session:opened', item)
      return item
    })
    ipcMain.handle('session:delete', async (event, id) => {
      trusted(event)
      const entries = await readSessions()
      const item = entries.find((entry) => entry.id === id)
      if (!item || item.protected) throw new Error('That session cannot be deleted.')
      if (activeSession && activeSession.id === id) throw new Error('Close the active session before deleting it.')
      await rm(join(sessionsDir, id), { recursive: true, force: true })
      await writeSessions(entries.filter((entry) => entry.id !== id))
      return true
    })
    ipcMain.handle('session:open', async (event, id) => {
      trusted(event)
      const item = (await readSessions()).find((entry) => entry.id === id)
      if (!item) throw new Error('That session no longer exists.')
      await stopBackend()
      activeSession = item
      await startBackend(join(sessionsDir, item.id))
      maximizeWindow()
      event.sender.send('session:opened', item)
      return item
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
    createWindow()
  })
  app.on('window-all-closed', () => app.quit())
  app.on('browser-window-created', (_event, created) => {
    created.on('close', (event) => {
      if (closing || !activeSession || closePromptPending) return
      event.preventDefault()
      closePromptPending = true
      created.webContents.send('app:close-request')
    })
  })
  ipcMain.handle('app:close-decision', async (event, decision) => {
    trusted(event)
    if (!closePromptPending) return false
    closePromptPending = false
    if (decision === 'cancel') return
    // Release SQLite/WAL and other session files before discard tries to remove
    // the directory. This is especially important on Windows, where an open
    // database handle prevents recursive removal.
    closing = true
    try {
      // Terminate any browsers this session launched before stopping the
      // backend, so their profile files are released ahead of directory
      // removal (avoids Windows EBUSY on locked SQLite files).
      await stopBrowsers()
      await stopBackend()
      if (decision === 'save' && activeSession) {
        activeSession.updated_at = new Date().toISOString()
        await writeSessions((await readSessions()).map((entry) => entry.id === activeSession.id ? activeSession : entry))
      }
      if (decision === 'discard' && activeSession && !activeSession.protected) {
        await removeWithRetry(join(sessionsDir, activeSession.id))
        await writeSessions((await readSessions()).filter((entry) => entry.id !== activeSession.id))
      }
      window.destroy()
      return true
    } catch (error) {
      closing = false
      closePromptPending = true
      throw error
    }
  })
  app.on('before-quit', (event) => {
    if (!closing && backend) {
      event.preventDefault()
      closing = true
      // Close the launched browser(s) first, then stop the engine, then quit.
      stopBrowsers()
        .then(stopBackend)
        .finally(() => app.quit())
    }
  })
}

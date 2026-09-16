import {
  Activity,
  ArrowRight,
  Check,
  ChevronRight,
  CircleHelp,
  Globe2,
  Fingerprint,
  Folder,
  Layers3,
  LoaderCircle,
  LockKeyhole,
  Maximize2,
  Minus,
  Play,
  Radio,
  Settings2,
  Square,
  X,
} from 'lucide-react'
import { api } from './api'
import { Button } from './components'

import { icons, useWorkspace, type View } from './hooks/useWorkspace'
import { AuditView } from './views/AuditView'
import { DecoderView } from './views/DecoderView'
import { IntruderView } from './views/IntruderView'
import { ProxyView } from './views/ProxyView'
import { RepeaterView } from './views/RepeaterView'
import { ScopeView } from './views/ScopeView'
import { SettingsView } from './views/SettingsView'
import type { BrowserInfo } from './types'
import type { WorkspaceSession } from './types'
import { useEffect, useState } from 'react'
import type { IconDefinition } from '@fortawesome/free-brands-svg-icons'
import {
  faBrave,
  faChrome,
  faEdge,
  faFirefoxBrowser,
  faOpera,
} from '@fortawesome/free-brands-svg-icons'
import brandImage from '../../bidoytu-long.png'

const browserBrandIcons: Record<string, IconDefinition> = {
  'Google Chrome': faChrome,
  Chromium: faChrome,
  Firefox: faFirefoxBrowser,
  'Microsoft Edge': faEdge,
  Brave: faBrave,
  Opera: faOpera,
}

function BrowserLogo({ browser }: { browser: BrowserInfo }) {
  if (browser.name === 'Vivaldi') {
    return <img className="browser-logo" src="/browser-logos/vivaldi.svg" alt="" />
  }
  const icon = browserBrandIcons[browser.name]
  if (!icon) return <Globe2 className="browser-logo-fallback" size={22} aria-hidden="true" />
  const [width, height, , , paths] = icon.icon
  const pathList = Array.isArray(paths) ? paths : [paths]
  return (
    <svg className="browser-logo" viewBox={`0 0 ${width} ${height}`} aria-hidden="true">
      {pathList.map((path, index) => (
        <path key={index} d={path} />
      ))}
    </svg>
  )
}

function SessionPicker({
  sessions,
  onOpen,
  onCreate,
  onDelete,
  onClose,
}: {
  sessions: WorkspaceSession[]
  onOpen: (session: WorkspaceSession) => void
  onCreate: (name: string) => void
  onDelete: (session: WorkspaceSession) => void
  onClose: () => void
}) {
  const [creating, setCreating] = useState(false)
  const [name, setName] = useState('New session')
  return (
    <div className="session-picker">
      <div className="session-picker-card">
        <button className="session-picker-close" aria-label="Close" onClick={onClose}><X size={17} /></button>
        <div className="empty-icon"><Layers3 size={26} /></div>
        <h1>Choose a session</h1>
        <p>History, requests, scope, and tool state are saved per session. The proxy CA is shared globally.</p>
        <div className="session-list">
          {sessions.map((session) => (
            <div className="session-row" key={session.id}>
              <div className="session-row-info">
                <strong>{session.name}</strong>
                <small>Updated {new Date(session.updated_at).toLocaleString()}</small>
              </div>
              <Button className="primary" onClick={() => onOpen(session)}>Open</Button>
              {!session.protected && <Button className="subtle" onClick={() => onDelete(session)}>Delete</Button>}
            </div>
          ))}
          {!sessions.length && <p className="muted">No saved sessions yet.</p>}
        </div>
        {!creating ? <Button className="primary session-create" onClick={() => setCreating(true)}><Layers3 size={14} /> Create session</Button> : (
          <form className="session-create-form" onSubmit={(event) => { event.preventDefault(); if (name.trim()) onCreate(name.trim()) }}>
            <input autoFocus aria-label="Session name" value={name} maxLength={120} onChange={(event) => setName(event.target.value)} />
            <Button className="subtle" type="button" onClick={() => setCreating(false)}>Cancel</Button>
            <Button className="primary" type="submit" disabled={!name.trim()}>Create</Button>
          </form>
        )}
      </div>
    </div>
  )
}

export function App() {
  const workspace = useWorkspace()
  const {
    view,
    setView,
    state,
    setState,
    online,
    connecting,
    error,
    setError,
    notice,
    setNotice,
    busy,
    page,
    port,
    findings,
    showHelp,
    setShowHelp,
    pending,
    toggleProxy,
  } = workspace
  const [showBrowsers, setShowBrowsers] = useState(false)
  const [browsers, setBrowsers] = useState<BrowserInfo[]>([])
  const [browserBusy, setBrowserBusy] = useState(false)
  const [browserError, setBrowserError] = useState('')
  const [sessions, setSessions] = useState<WorkspaceSession[]>([])
  const [activeSession, setActiveSession] = useState<WorkspaceSession | null>(null)
  const [sessionError, setSessionError] = useState('')
  const [closeRequested, setCloseRequested] = useState(false)
  const [closing, setClosing] = useState(false)

  useEffect(() => {
    api.listSessions().then(setSessions).catch((e) => setSessionError(e.message))
    const unsubscribeClose = api.onAppCloseRequest(() => setCloseRequested(true))
    const unsubscribeSession = api.onSessionOpened((session) => setActiveSession(session))
    return () => { unsubscribeClose(); unsubscribeSession() }
  }, [])

  async function createSession(name: string) {
    try {
      const created = await api.createSession(name)
      setSessions((current) => [created, ...current])
      await api.openSession(created.id)
      setActiveSession(created)
    } catch (e) { setSessionError(e instanceof Error ? e.message : String(e)) }
  }

  async function openSession(session: WorkspaceSession) {
    try { await api.openSession(session.id); setActiveSession(session); setSessionError('') }
    catch (e) { setSessionError(e instanceof Error ? e.message : String(e)) }
  }

  async function deleteSession(session: WorkspaceSession) {
    if (!window.confirm(`Delete "${session.name}" and all of its history?`)) return
    try { await api.deleteSession(session.id); setSessions((current) => current.filter((item) => item.id !== session.id)) }
    catch (e) { setSessionError(e instanceof Error ? e.message : String(e)) }
  }

  if (!activeSession) return <>
    <SessionPicker sessions={sessions} onOpen={openSession} onCreate={createSession} onDelete={deleteSession} onClose={() => api.window('close')} />
    {sessionError && <div className="session-error">{sessionError}</div>}
  </>

  async function openBrowserPicker() {
    setShowBrowsers(true)
    setBrowserError('')
    try {
      setBrowsers(await api.listBrowsers())
    } catch (e) {
      setBrowserError(e instanceof Error ? e.message : String(e))
    }
  }

  async function launchBrowser(id: number) {
    setBrowserBusy(true)
    setBrowserError('')
    try {
      const result = await api.openBrowser(id)
      setNotice(`${result.name} opened with the Bidoytu proxy and CA configured.`)
      setShowBrowsers(false)
    } catch (e) {
      setBrowserError(e instanceof Error ? e.message : String(e))
    } finally {
      setBrowserBusy(false)
    }
  }
  return (
    <div className="app">
      <header className="titlebar">
        <img className="brand-logo" src={brandImage} alt="bidoytu" />
        <span className="title-divider" />
        <span className="title-context">Security workspace</span>
        <div className="title-project">
          <Folder size={12} />
          {activeSession.name}<span className="local-pill">LOCAL</span>
        </div>
        <div className="window-controls">
          <button aria-label="Minimize" onClick={() => api.window('minimize')}>
            <Minus size={14} />
          </button>
          <button aria-label="Maximize" onClick={() => api.window('maximize')}>
            <Maximize2 size={12} />
          </button>
          <button aria-label="Close" onClick={() => api.window('close')}>
            <X size={15} />
          </button>
        </div>
      </header>
      <aside className="sidebar">
        <div className="nav-label">WORKSPACE</div>
        <nav>
          {(['Proxy', 'Repeater', 'Intruder'] as View[]).map((item) => {
            const NavIcon = icons[item]
            return (
              <button
                key={item}
                className={`nav-item ${view === item ? 'active' : ''}`}
                onClick={() => setView(item)}
              >
                <NavIcon size={17} />
                <span>{item}</span>
                {item === 'Proxy' && state.pending.length > 0 ? (
                  <b className="nav-badge">{state.pending.length}</b>
                ) : item === 'Proxy' ? (
                  <kbd>⌘ 1</kbd>
                ) : null}
              </button>
            )
          })}
        </nav>
        <div className="nav-label tools-label">TOOLS</div>
        <nav>
          {(['Scope', 'Live audit', 'Decoder'] as View[]).map((item) => {
            const NavIcon = icons[item]
            return (
              <button
                key={item}
                className={`nav-item ${view === item ? 'active' : ''}`}
                onClick={() => setView(item)}
              >
                <NavIcon size={17} />
                <span>{item === 'Scope' ? 'Target scope' : item}</span>
                {item === 'Live audit' && state.findings > 0 && (
                  <b className="nav-badge">{state.findings}</b>
                )}
              </button>
            )
          })}
        </nav>
        <div className="sidebar-bottom">
          <div className="engine-card">
            <div className="inline">
              <span className={`dot ${online ? 'green' : ''}`} />
              <strong>Python engine</strong>
              <span className="engine-tag">ASYNC</span>
            </div>
            <span>
              {connecting ? 'Connecting…' : online ? 'Connected via private IPC' : 'Engine offline'}
            </span>
            <div className="engine-activity">
              <i />
              <i />
              <i />
              <i />
              <i />
              <i />
              <i />
              <i />
              <i />
              <i />
              <i />
              <i />
            </div>
          </div>
          <button
            className={`nav-item ${view === 'Settings' ? 'active' : ''}`}
            onClick={() => setView('Settings')}
          >
            <Settings2 size={17} />
            <span>Settings</span>
          </button>
          <button className="nav-item" onClick={() => setShowHelp(true)}>
            <CircleHelp size={17} />
            <span>Quick start</span>
            <ArrowRight size={13} />
          </button>
          <div className="sidebar-signature">
            <Fingerprint size={15} />
            <span>Built for the curious.</span>
          </div>
        </div>
      </aside>
      <main className="main">
        <div className="workspace-topbar">
          <div className="breadcrumbs">
            <Folder size={14} />
            <span>{activeSession.name}</span>
            <ChevronRight size={12} />
            <strong>{view}</strong>
          </div>
          <div className="inline">
            <span className={`connection-label ${state.running ? 'connected' : ''}`}>
              <span className={`dot ${state.running ? 'green' : ''}`} />
              {state.running ? `Listening on ${state.host}:${state.port}` : 'Proxy stopped'}
            </span>
            <Button
              className={state.running ? 'subtle' : 'primary'}
              disabled={!online || busy}
              onClick={toggleProxy}
            >
              {busy ? (
                <LoaderCircle className="spin" size={13} />
              ) : state.running ? (
                <Square size={11} />
              ) : (
                <Play size={13} />
              )}{' '}
              {state.running ? 'Stop proxy' : 'Start proxy'}
            </Button>
            <Button
              className="subtle"
              disabled={!online || !state.running || browserBusy}
              onClick={openBrowserPicker}
            >
              <Globe2 size={13} /> Open browser
            </Button>
          </div>
        </div>
        {(error || state.error) && (
          <div className="error-banner" role="alert">
            <Activity size={15} />
            <span>{error || state.error}</span>
            <button
              aria-label="Dismiss error"
              onClick={() => {
                setError('')
                setState((s) => ({ ...s, error: '' }))
              }}
            >
              <X size={14} />
            </button>
          </div>
        )}
        {notice && (
          <div className="notice" role="status">
            <Check size={15} />
            {notice}
          </div>
        )}
        {view === 'Proxy' && <ProxyView workspace={workspace} />}
        {view === 'Repeater' && <RepeaterView workspace={workspace} />}
        {view === 'Intruder' && <IntruderView workspace={workspace} />}
        {view === 'Scope' && <ScopeView workspace={workspace} />}
        {view === 'Live audit' && <AuditView workspace={workspace} />}
        {view === 'Decoder' && <DecoderView workspace={workspace} />}
        {view === 'Settings' && <SettingsView workspace={workspace} />}{' '}
      </main>
      <footer className="statusbar">
        <span>
          <span className={`dot ${online ? 'green' : ''}`} />
          {online ? 'Engine connected' : connecting ? 'Connecting to engine' : 'Engine offline'}
        </span>
        <span className="status-divider" />
        <span>
          <LockKeyhole size={11} />
          Local workspace
        </span>
        <span className="grow" />
        {state.dropped > 0 && (
          <span className="warning-text">{state.dropped} capture updates dropped</span>
        )}
        <button
          onClick={() => {
            setView('Proxy')
            workspace.setProxyView('Intercept')
          }}
        >
          <span className={`dot ${state.intercept ? 'amber' : ''}`} />
          Intercept {state.intercept ? 'on' : 'off'}
        </button>
        <span className="status-divider" />
        <span>Bidoytu 2.0.0</span>
      </footer>
      {showHelp && (
        <div className="modal-backdrop" onClick={() => setShowHelp(false)}>
          <section
            className="modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="help-title"
            onClick={(e) => e.stopPropagation()}
          >
            <button
              className="modal-close icon-button"
              aria-label="Close quick start"
              autoFocus
              onClick={() => setShowHelp(false)}
            >
              <X size={18} />
            </button>
            <div className="empty-icon">
              <Radio size={26} />
            </div>
            <h2 id="help-title">Connect. Capture. Explore.</h2>
            <p>Set up a dedicated browser profile for your testing workspace.</p>
            <ol>
              <li>
                <strong>Start the proxy</strong>
                <span>
                  Use the button in the top right. The default listener is 127.0.0.1:8080.
                </span>
              </li>
              <li>
                <strong>Configure your browser</strong>
                <span>
                  Set its HTTP and HTTPS proxy to 127.0.0.1 and the listener port. Disable proxy
                  bypass for local test hosts if needed.
                </span>
              </li>
              <li>
                <strong>Set up HTTPS</strong>
                <span>
                  Export the public CA from Settings and import it into your testing browser’s
                  certificate authorities.
                </span>
              </li>
              <li>
                <strong>Make your first request</strong>
                <span>
                  Browse your target. Select a captured request and send it to Repeater to start
                  exploring.
                </span>
              </li>
            </ol>
            <Button
              className="primary"
              onClick={() => {
                setShowHelp(false)
                setView('Settings')
              }}
            >
              Open settings <ArrowRight size={14} />
            </Button>
          </section>
        </div>
      )}
      {showBrowsers && (
        <div className="modal-backdrop" onClick={() => setShowBrowsers(false)}>
          <section
            className="modal browser-modal"
            role="dialog"
            aria-modal="true"
            aria-label="Open browser"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="modal-head">
              <div>
                <h2>Open browser through Bidoytu</h2>
                <p>A dedicated profile will use the active proxy and trust its public CA.</p>
              </div>
              <button aria-label="Close" onClick={() => setShowBrowsers(false)}>
                <X size={15} />
              </button>
            </div>
            {browserError && (
              <div className="error-banner" role="alert">
                {browserError}
              </div>
            )}
            <div className="browser-list">
              {browsers.map((browser) => (
                <div className="browser-row" key={browser.id}>
                  <BrowserLogo browser={browser} />
                  <div className="grow">
                    <strong>{browser.name}</strong>
                    <small>Fresh isolated profile</small>
                  </div>
                  <Button
                    className="primary"
                    disabled={browserBusy}
                    onClick={() => launchBrowser(browser.id)}
                  >
                    Open
                  </Button>
                </div>
              ))}
              {!browsers.length && !browserError && (
                <p className="muted">No supported browsers were found on this device.</p>
              )}
            </div>
            <small className="browser-note">
              Browsers opened here are closed automatically when Bidoytu exits.
            </small>
          </section>
        </div>
      )}
      {closeRequested && (
        <div className="modal-backdrop">
          <section className="modal" role="dialog" aria-modal="true" aria-labelledby="close-title">
            <h2 id="close-title">Close session?</h2>
            <p>Save this session to keep its history and workspace details for next time, or discard it permanently.</p>
            <div className="close-actions">
              <Button className="subtle" disabled={closing} onClick={() => { setCloseRequested(false); void api.closeDecision('cancel') }}>Cancel</Button>
              <Button className="subtle" disabled={closing} onClick={async () => { setClosing(true); try { await api.closeDecision('discard') } catch (e) { setClosing(false); setCloseRequested(true); setError(e instanceof Error ? e.message : String(e)) } }}>Discard session</Button>
              <Button className="primary" disabled={closing} onClick={async () => { setClosing(true); try { await api.closeDecision('save') } catch (e) { setClosing(false); setCloseRequested(true); setError(e instanceof Error ? e.message : String(e)) } }}>Save session</Button>
            </div>
            {closing && <p className="close-progress">Closing session…</p>}
          </section>
        </div>
      )}
    </div>
  )
}

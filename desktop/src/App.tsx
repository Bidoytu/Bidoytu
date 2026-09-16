import {
  Activity,
  ArrowRight,
  Check,
  ChevronRight,
  CircleHelp,
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

import { descriptions, icons, useWorkspace, type View } from './hooks/useWorkspace'
import { AuditView } from './views/AuditView'
import { DecoderView } from './views/DecoderView'
import { HistoryView } from './views/HistoryView'
import { InterceptView } from './views/InterceptView'
import { IntruderView } from './views/IntruderView'
import { RepeaterView } from './views/RepeaterView'
import { ScopeView } from './views/ScopeView'
import { SettingsView } from './views/SettingsView'

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
    busy,
    page,
    port,
    findings,
    showHelp,
    setShowHelp,
    pending,
    Icon,
    toggleProxy,
  } = workspace
  return (
    <div className="app">
      <header className="titlebar">
        <div className="brand-mark">
          <Layers3 size={18} />
        </div>
        <strong>
          bidoytu<span className="version">2.0</span>
        </strong>
        <span className="title-divider" />
        <span className="title-context">Security workspace</span>
        <div className="title-project">
          <Folder size={12} />
          Default workspace<span className="local-pill">LOCAL</span>
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
        <div className="workspace-card">
          <div className="workspace-avatar">B</div>
          <div>
            <strong>Default workspace</strong>
            <span>Local project</span>
          </div>
          <LockKeyhole size={13} />
        </div>
        <div className="nav-label">WORKSPACE</div>
        <nav>
          {(['History', 'Intercept', 'Repeater', 'Intruder'] as View[]).map((item) => {
            const NavIcon = icons[item]
            return (
              <button
                key={item}
                className={`nav-item ${view === item ? 'active' : ''}`}
                onClick={() => setView(item)}
              >
                <NavIcon size={17} />
                <span>{item === 'History' ? 'HTTP history' : item}</span>
                {item === 'Intercept' && state.pending.length > 0 ? (
                  <b className="nav-badge">{state.pending.length}</b>
                ) : item === 'History' ? (
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
            <span>Default workspace</span>
            <ChevronRight size={12} />
            <strong>{view === 'History' ? 'HTTP history' : view}</strong>
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
          </div>
        </div>
        <div className="page-heading">
          <div>
            <div className="eyebrow">
              {view === 'History' || view === 'Intercept' ? 'PROXY' : 'WORKSPACE'}
            </div>
            <h1>
              {view === 'History' ? 'HTTP history' : view === 'Scope' ? 'Target scope' : view}
            </h1>
            <p>{descriptions[view]}</p>
          </div>
          <div className="page-heading-icon">
            <Icon size={30} />
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
        {view === 'History' && <HistoryView workspace={workspace} />}
        {view === 'Intercept' && <InterceptView workspace={workspace} />}
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
        <button onClick={() => setView('Intercept')}>
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
    </div>
  )
}

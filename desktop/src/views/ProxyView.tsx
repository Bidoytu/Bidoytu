import { ArrowLeftRight, Globe2, List, LoaderCircle, Play, Square } from 'lucide-react'
import type { WorkspaceController } from '../hooks/useWorkspace'
import { Button } from '../components'
import { HistoryView } from './HistoryView'
import { InterceptView } from './InterceptView'

export function ProxyView({
  workspace,
  browserBusy,
  onOpenBrowser,
}: {
  workspace: WorkspaceController
  browserBusy: boolean
  onOpenBrowser: () => void
}) {
  const { proxyView, setProxyView, state, online, busy, toggleProxy } = workspace

  return (
    <div className="proxy-workspace">
      <div className="proxy-tabs" role="tablist" aria-label="Proxy views">
        <button
          className={proxyView === 'History' ? 'active' : ''}
          role="tab"
          aria-selected={proxyView === 'History'}
          onClick={() => setProxyView('History')}
        >
          <List size={14} />
          HTTP history
        </button>
        <button
          className={proxyView === 'Intercept' ? 'active' : ''}
          role="tab"
          aria-selected={proxyView === 'Intercept'}
          onClick={() => setProxyView('Intercept')}
        >
          <ArrowLeftRight size={14} />
          Intercept
          {state.pending.length > 0 && <b className="nav-badge">{state.pending.length}</b>}
        </button>
        <span className="grow" />
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
          onClick={onOpenBrowser}
        >
          <Globe2 size={13} /> Open browser
        </Button>
      </div>
      {proxyView === 'History' ? (
        <HistoryView workspace={workspace} />
      ) : (
        <InterceptView workspace={workspace} />
      )}
    </div>
  )
}

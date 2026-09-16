import { ArrowLeftRight, List } from 'lucide-react'
import type { WorkspaceController } from '../hooks/useWorkspace'
import { HistoryView } from './HistoryView'
import { InterceptView } from './InterceptView'

export function ProxyView({ workspace }: { workspace: WorkspaceController }) {
  const { proxyView, setProxyView, state } = workspace

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
      </div>
      {proxyView === 'History' ? (
        <HistoryView workspace={workspace} />
      ) : (
        <InterceptView workspace={workspace} />
      )}
    </div>
  )
}

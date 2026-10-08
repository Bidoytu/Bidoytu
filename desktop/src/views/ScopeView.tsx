import { Check, Crosshair } from 'lucide-react'
import { api } from '../api'
import { Button } from '../components'
import type { EngineState } from '../types'

import type { WorkspaceController } from '../hooks/useWorkspace'

export function ScopeView({ workspace }: { workspace: WorkspaceController }) {
  const {
    online,
    setNotice,
    include,
    setInclude,
    exclude,
    setExclude,
    dropOutOfScope,
    setDropOutOfScope,
    split,
    run,
    refresh,
  } = workspace
  return (
    <div className="settings-workspace">
      <div className="info-card">
        <Crosshair size={23} />
        <div>
          <strong>A focused investigation</strong>
          <p>
            Scope controls which hosts are intercepted, passively audited, and shown by the default
            History view. The quickest way to build it: right-click any request in HTTP history and
            choose <em>Add to scope</em> — no need to type hosts here. An empty include list matches
            all hosts, and History always captures everything so you can review it later.
          </p>
        </div>
      </div>
      <div className="scope-grid">
        <section className="settings-card">
          <h2>
            <span className="dot green" />
            Include hosts
          </h2>
          <p>One host per line. A domain also includes its subdomains.</p>
          <textarea
            aria-label="Included hosts"
            placeholder={'example.com\napi.example.com'}
            value={include}
            onChange={(e) => setInclude(e.target.value)}
          />
        </section>
        <section className="settings-card">
          <h2>
            <span className="dot red" />
            Exclude hosts
          </h2>
          <p>Excluded hosts take precedence over the include list.</p>
          <textarea
            aria-label="Excluded hosts"
            placeholder={'analytics.example.com\ncdn.example.com'}
            value={exclude}
            onChange={(e) => setExclude(e.target.value)}
          />
        </section>
      </div>
      <section className="settings-card">
        <h2>
          <span className="dot amber" />
          Out-of-scope traffic
        </h2>
        <label className="check-row">
          <input
            type="checkbox"
            checked={dropOutOfScope}
            onChange={(e) => setDropOutOfScope(e.target.checked)}
          />
          <span>
            <strong>Drop all out-of-scope traffic</strong>
            <small>
              Out-of-scope requests are still proxied so pages keep loading, but they are never
              recorded to History or intercepted. Set an include host above first, or everything
              counts as in scope.
            </small>
          </span>
        </label>
      </section>
      <div className="inline">
        <Button
          className="primary"
          disabled={!online}
          onClick={() =>
            void run(async () => {
              refresh(
                await api.request<EngineState>('scope.save', {
                  include: include
                    .split('\n')
                    .map((v) => v.trim())
                    .filter(Boolean),
                  exclude: exclude
                    .split('\n')
                    .map((v) => v.trim())
                    .filter(Boolean),
                  drop_out_of_scope: dropOutOfScope,
                }),
              )
              setNotice('Target scope saved. New traffic uses these rules.')
            })
          }
        >
          <Check size={14} />
          Save scope
        </Button>
        <span className="muted">Applies immediately to new traffic.</span>
      </div>
    </div>
  )
}

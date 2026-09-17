import { Check, Crosshair } from 'lucide-react'
import { api } from '../api'
import { Button } from '../components'
import type { EngineState } from '../types'

import type { WorkspaceController } from '../hooks/useWorkspace'

export function ScopeView({ workspace }: { workspace: WorkspaceController }) {
  const { online, setNotice, include, setInclude, exclude, setExclude, split, run, refresh } =
    workspace
  return (
    <div className="settings-workspace">
      <div className="info-card">
        <Crosshair size={23} />
        <div>
          <strong>A focused investigation</strong>
          <p>
            Scope controls which hosts can be intercepted and passively audited. History still
            captures all traffic. An empty include list matches all hosts.
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

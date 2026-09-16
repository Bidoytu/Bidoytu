import { ArrowRight, Shield, ShieldCheck } from 'lucide-react'
import { api } from '../api'
import { Button, Empty, Toggle } from '../components'
import type { EngineState } from '../types'

import type { WorkspaceController } from '../hooks/useWorkspace'

export function AuditView({ workspace }: { workspace: WorkspaceController }) {
  const { setView, state, online, include, findings, run, refresh, selectFlow } = workspace
  return (
    <div className="tool-workspace">
      <div className="tool-toolbar">
        <Toggle
          label="Enable passive audit"
          enabled={state.audit}
          disabled={!online}
          onChange={() =>
            void run(async () =>
              refresh(await api.request<EngineState>('audit.toggle', { enabled: !state.audit })),
            )
          }
        />
        <strong>Passive audit {state.audit ? 'enabled' : 'disabled'}</strong>
        <span className="muted">In-scope responses only · no additional requests</span>
        <span className="grow" />
        <span className="count-chip">{findings.length} findings</span>
      </div>
      <div className="findings-scroll">
        {findings.length ? (
          findings.map((finding) => (
            <article className="finding" key={finding.id}>
              <div className="inline">
                <span className={`severity severity-${finding.severity.toLowerCase()}`}>
                  {finding.severity}
                </span>
                <h3>{finding.title}</h3>
                <span className="grow" />
                <Button
                  className="subtle"
                  onClick={() => {
                    setView('History')
                    void selectFlow(finding.flow_id)
                  }}
                >
                  View evidence <ArrowRight size={12} />
                </Button>
              </div>
              <div className="finding-url mono">{finding.url}</div>
              <p>{finding.detail}</p>
              {finding.evidence.map((e, i) => (
                <pre key={i}>{e.text}</pre>
              ))}
              <p className="remediation">
                <Shield size={13} />
                {finding.remediation}
              </p>
            </article>
          ))
        ) : (
          <Empty icon={<ShieldCheck size={30} />} title="Let the traffic tell its story">
            Enable passive audit and browse an in-scope target. Findings include captured evidence
            and remediation guidance.
          </Empty>
        )}
      </div>
    </div>
  )
}

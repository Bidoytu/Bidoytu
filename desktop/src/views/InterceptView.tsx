import { ArrowLeftRight, ArrowRight, X } from 'lucide-react'
import { Button, ContextMenu, Editor, Empty, Toggle, useContextMenu } from '../components'

import type { WorkspaceController } from '../hooks/useWorkspace'

export function InterceptView({ workspace }: { workspace: WorkspaceController }) {
  const {
    state,
    online,
    busy,
    flows,
    port,
    interceptText,
    setInterceptText,
    interceptOriginal,
    setInterceptId,
    interceptDetail,
    split,
    pending,
    interceptToggle,
    resolveIntercept,
    toRepeater,
    toIntruder,
  } = workspace
  const ctx = useContextMenu()
  return (
    <div className="tool-workspace">
      <div className="tool-toolbar">
        <div className="inline">
          <Toggle
            label="Intercept traffic"
            enabled={state.intercept}
            disabled={!online}
            onChange={() => void interceptToggle()}
          />
          <strong>Intercept is {state.intercept ? 'on' : 'off'}</strong>
          <span className="muted">{state.pending.length} waiting</span>
        </div>
        <label className="check-label">
          <input
            type="checkbox"
            checked={state.responses}
            onChange={(e) => void interceptToggle(state.intercept, e.target.checked)}
          />
          Intercept responses
        </label>
        <span className="grow" />
        <Button
          disabled={
            !pending ||
            busy ||
            !interceptDetail ||
            (interceptDetail.truncated && interceptText !== interceptOriginal)
          }
          className="primary"
          onClick={() => void resolveIntercept(false)}
        >
          <ArrowRight size={14} />
          Forward
        </Button>
        <Button
          disabled={!pending || busy}
          className="danger"
          onClick={() => void resolveIntercept(true)}
        >
          <X size={14} />
          Drop
        </Button>
      </div>
      {pending ? (
        <>
          <div className="pending-strip">
            {state.pending.map((item) => (
              <button
                className={
                  item.flow_id === pending.flow_id ? 'pending-item active' : 'pending-item'
                }
                key={item.flow_id}
                onClick={() => setInterceptId(item.flow_id)}
              >
                <span className="method">{item.method}</span>
                {item.host}
                <span className="muted">{item.phase}</span>
              </button>
            ))}
          </div>
          {interceptDetail?.truncated && (
            <div className="warning-banner">
              Body preview is truncated. Forwarding without edits preserves the original bytes.
            </div>
          )}
          <div
            className="editor-split full"
            onContextMenu={(e) => {
              if (!interceptDetail) return
              ctx.open(e, [
                {
                  label: 'Send to Repeater',
                  shortcut: 'Ctrl+R',
                  disabled: !interceptDetail || interceptDetail.truncated || interceptDetail.binary,
                  onClick: () => interceptDetail && toRepeater(interceptDetail),
                },
                {
                  label: 'Send to Intruder',
                  shortcut: 'Ctrl+I',
                  disabled: !interceptDetail || interceptDetail.truncated || interceptDetail.binary,
                  onClick: () => interceptDetail && toIntruder(interceptDetail),
                },
              ])
            }}
          >
            <Editor
              title={pending.phase === 'request' ? 'Request' : 'Response'}
              value={interceptText}
              onChange={
                interceptDetail?.truncated || interceptDetail?.binary ? undefined : setInterceptText
              }
              hint="Paused in Python engine"
            />
            <div className="intercept-guide">
              <div className="empty-icon">
                <ArrowLeftRight size={25} />
              </div>
              <h3>You control the next step.</h3>
              <p>
                Edit the raw {pending.phase}, then forward it to continue. Drop closes this
                exchange.
              </p>
              <dl>
                <dt>Destination</dt>
                <dd>
                  {pending.host}:{pending.port}
                </dd>
                <dt>Phase</dt>
                <dd>{pending.phase}</dd>
                <dt>Scope</dt>
                <dd>In scope</dd>
              </dl>
            </div>
          </div>
        </>
      ) : (
        <Empty
          icon={<ArrowLeftRight size={30} />}
          title={state.intercept ? 'Waiting for in-scope traffic' : 'Traffic flows uninterrupted'}
        >
          {state.intercept
            ? 'Incoming requests will pause here while interception is enabled.'
            : 'Enable interception to pause requests before they reach the server.'}
        </Empty>
      )}
      <ContextMenu menu={ctx.menu} onClose={ctx.close} />
    </div>
  )
}

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
    pending,
    interceptToggle,
    resolveIntercept,
    resolveAllIntercept,
    interceptSplit,
    setInterceptSplit,
    interceptRef,
    resizeIntercept,
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
          disabled={state.pending.length === 0 || busy}
          onClick={() => void resolveAllIntercept(false)}
        >
          <ArrowRight size={14} />
          Forward all
        </Button>
        <Button
          disabled={!pending || busy}
          className="danger"
          onClick={() => void resolveIntercept(true)}
        >
          <X size={14} />
          Drop
        </Button>
        <Button
          disabled={state.pending.length === 0 || busy}
          className="danger"
          onClick={() => void resolveAllIntercept(true)}
        >
          <X size={14} />
          Drop all
        </Button>
      </div>
      {pending ? (
        <div
          className="intercept-content"
          ref={interceptRef}
          style={{ gridTemplateRows: `${interceptSplit}% 7px minmax(0, 1fr)` }}
        >
          <div className="pending-strip" aria-label="Intercept queue">
            <div className="intercept-table-row intercept-table-header">
              <span>Type</span>
              <span>Method</span>
              <span>Host</span>
              <span>Path</span>
              <span>State</span>
            </div>
            {state.pending.map((item) => (
              <button
                className={`intercept-table-row pending-item ${item.flow_id === pending.flow_id ? 'active' : ''}`}
                key={item.flow_id}
                onClick={() => setInterceptId(item.flow_id)}
              >
                <span className="muted">{item.phase === 'request' ? 'Request' : 'Response'}</span>
                <span className={`method method-${item.method.toLowerCase()}`}>{item.method}</span>
                <span className="host-cell">
                  <span>{item.host}</span>
                </span>
                <span className="mono path-cell" title={item.path}>
                  {item.path}
                </span>
                <span className="muted mono">{item.status_code ?? '—'}</span>
              </button>
            ))}
          </div>
          <div
            className="split-handle intercept-split-handle"
            role="separator"
            aria-label="Resize intercept queue and message inspector"
            aria-valuenow={interceptSplit}
            aria-valuemin={22}
            aria-valuemax={78}
            tabIndex={0}
            onPointerDown={resizeIntercept}
            onKeyDown={(e) => {
              if (e.key === 'ArrowUp') setInterceptSplit((v) => Math.max(22, v - 3))
              if (e.key === 'ArrowDown') setInterceptSplit((v) => Math.min(78, v + 3))
            }}
          >
            <span />
          </div>
          <div className="intercept-main">
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
                    disabled:
                      !interceptDetail || interceptDetail.truncated || interceptDetail.binary,
                    onClick: () => interceptDetail && toRepeater(interceptDetail),
                  },
                  {
                    label: 'Send to Intruder',
                    shortcut: 'Ctrl+I',
                    disabled:
                      !interceptDetail || interceptDetail.truncated || interceptDetail.binary,
                    onClick: () => interceptDetail && toIntruder(interceptDetail),
                  },
                ])
              }}
            >
              <Editor
                title="Request"
                value={
                  pending.phase === 'response' ? (interceptDetail?.request ?? '') : interceptText
                }
                onChange={
                  pending.phase === 'request' &&
                  !interceptDetail?.truncated &&
                  !interceptDetail?.binary
                    ? setInterceptText
                    : undefined
                }
                hint={pending.phase === 'response' ? 'Original request' : 'Paused in Python engine'}
              />
              {pending.phase === 'response' ? (
                <Editor
                  title="Response"
                  value={interceptText}
                  onChange={
                    interceptDetail?.truncated || interceptDetail?.binary
                      ? undefined
                      : setInterceptText
                  }
                  hint="Paused before returning to the client"
                />
              ) : (
                <div className="intercept-guide">
                  <div className="empty-icon">
                    <ArrowLeftRight size={25} />
                  </div>
                  <h3>Request paused</h3>
                  <p>
                    Edit the request, then forward it to the target. Enable response interception to
                    pause the matching response on the right.
                  </p>
                  <dl>
                    <dt>Destination</dt>
                    <dd>
                      {pending.host}:{pending.port}
                    </dd>
                    <dt>Phase</dt>
                    <dd>Request</dd>
                    <dt>Scope</dt>
                    <dd>In scope</dd>
                  </dl>
                </div>
              )}
            </div>
          </div>
        </div>
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

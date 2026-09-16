import { Activity, ArrowRight, Globe2, Layers3, Play, Square, Zap } from 'lucide-react'
import { api } from '../api'
import { Button, Editor, Empty, Status, bytes, duration } from '../components'
import type { Detail } from '../types'

import type { WorkspaceController } from '../hooks/useWorkspace'

export function IntruderView({ workspace }: { workspace: WorkspaceController }) {
  const {
    state,
    setState,
    online,
    error,
    verifyTLS,
    attackRequest,
    setAttackRequest,
    attackUrl,
    setAttackUrl,
    payloads,
    setPayloads,
    results,
    setResults,
    split,
    run,
    toRepeater,
  } = workspace
  return (
    <div className="tool-workspace">
      <div className="tool-toolbar">
        <label className="target-input">
          <Globe2 size={15} />
          <input
            aria-label="Intruder target URL"
            value={attackUrl}
            disabled={state.job_state === 'running'}
            onChange={(e) => setAttackUrl(e.target.value)}
          />
        </label>
        <span className="muted">{state.job_state}</span>
        {state.job_state === 'running' ? (
          <Button className="danger" onClick={() => void run(() => api.request('intruder.cancel'))}>
            <Square size={12} />
            Cancel run
          </Button>
        ) : (
          <Button
            className="primary"
            disabled={!online}
            onClick={() =>
              void run(async () => {
                await api.request('intruder.start', {
                  url: attackUrl,
                  request: attackRequest,
                  payloads: payloads.split('\n').filter(Boolean),
                  verify_tls: verifyTLS,
                })
                setState((s) => ({ ...s, job_state: 'running' }))
                setResults([])
              })
            }
          >
            <Play size={13} />
            Start run
          </Button>
        )}
      </div>
      <div className="attack-top">
        <Editor
          title="Request template"
          value={attackRequest}
          onChange={setAttackRequest}
          disabled={state.job_state === 'running'}
        />
        <section className="payload-panel">
          <div className="panel-title">
            <span>
              <Layers3 size={14} />
              Payloads
            </span>
            <small>{payloads.split('\n').filter(Boolean).length} values</small>
          </div>
          <p>
            Place <code>§payload§</code> in the request. Enter one replacement per line.
          </p>
          <textarea
            aria-label="Intruder payloads"
            placeholder="One payload per line…"
            value={payloads}
            disabled={state.job_state === 'running'}
            onChange={(e) => setPayloads(e.target.value)}
          />
          <small>Sequential requests · 100 ms interval · up to 1,000 payloads</small>
        </section>
      </div>
      <div className="results-panel">
        <div className="panel-title">
          <span>
            <Activity size={14} />
            Results
          </span>
          <small>{results.length} completed</small>
        </div>
        {results.length ? (
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>Payload</th>
                <th>Status</th>
                <th>Size</th>
                <th>Time</th>
                <th>Result</th>
              </tr>
            </thead>
            <tbody>
              {results.map((result) => (
                <tr key={result.index}>
                  <td>{result.index}</td>
                  <td className="mono">{result.payload}</td>
                  <td>
                    <Status value={result.status_code} />
                  </td>
                  <td>
                    {result.response_body_size != null ? bytes(result.response_body_size) : '—'}
                  </td>
                  <td>{duration(result.duration_ms)}</td>
                  <td>
                    {result.error || (
                      <button
                        className="text-button"
                        onClick={() =>
                          void run(async () =>
                            toRepeater(
                              await api.request<Detail>('history.detail', {
                                flow_id: result.flow_id,
                              }),
                            ),
                          )
                        }
                      >
                        Open in Repeater <ArrowRight size={12} />
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <Empty icon={<Zap size={24} />} title="Ready when you are">
            Add your payloads and start a controlled run.
          </Empty>
        )}
      </div>
    </div>
  )
}

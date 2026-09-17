import { useMemo, useRef, useState } from 'react'
import {
  ArrowDown,
  ArrowRight,
  ArrowUp,
  ArrowUpDown,
  LoaderCircle,
  Square,
  X,
  Zap,
} from 'lucide-react'
import { api } from '../api'
import { Button, Editor, Empty, Status, bytes, duration } from '../components'
import type { JobResult } from '../types'

import type { WorkspaceController } from '../hooks/useWorkspace'

type SortKey = 'index' | 'payload' | 'status' | 'size' | 'time'
type SortState = { key: SortKey; direction: 'asc' | 'desc' }

// The Intruder run popup mirrors the HTTP history layout: a table of every
// request the run has sent, with a request/response inspector below that loads
// the selected row's detail on click. The split between the two is resizable
// and the table columns can be ordered ascending/descending.
export function IntruderRunModal({ workspace }: { workspace: WorkspaceController }) {
  const {
    state,
    results,
    intruderTab,
    showIntruderRun,
    setShowIntruderRun,
    runSelectedIndex,
    runDetail,
    runDetailLoading,
    selectRunResult,
    run,
    toRepeater,
  } = workspace
  const [split, setSplit] = useState(54)
  const [sort, setSort] = useState<SortState>({ key: 'index', direction: 'asc' })
  const bodyRef = useRef<HTMLDivElement>(null)

  const sorted = useMemo(() => {
    const rows = [...results]
    const dir = sort.direction === 'asc' ? 1 : -1
    const value = (r: JobResult): number | string => {
      switch (sort.key) {
        case 'payload':
          return r.payload ?? ''
        case 'status':
          return r.status_code ?? (r.error ? -1 : Number.MAX_SAFE_INTEGER)
        case 'size':
          return r.response_body_size ?? -1
        case 'time':
          return r.duration_ms ?? -1
        default:
          return r.index
      }
    }
    rows.sort((a, b) => {
      const av = value(a)
      const bv = value(b)
      if (typeof av === 'string' || typeof bv === 'string') {
        return String(av).localeCompare(String(bv)) * dir
      }
      return (av - bv) * dir
    })
    return rows
  }, [results, sort])

  const sortHeader = (key: SortKey, label: string) => {
    const active = sort.key === key
    const Icon = active ? (sort.direction === 'asc' ? ArrowUp : ArrowDown) : ArrowUpDown
    return (
      <button
        className={active ? 'sort-header active' : 'sort-header'}
        onClick={() =>
          setSort((current) => ({
            key,
            direction: current.key === key && current.direction === 'asc' ? 'desc' : 'asc',
          }))
        }
      >
        <span>{label}</span>
        <Icon size={11} />
      </button>
    )
  }

  const resize = (e: React.PointerEvent) => {
    const element = e.currentTarget as HTMLElement
    element.setPointerCapture(e.pointerId)
    const move = (event: PointerEvent) => {
      const rect = bodyRef.current!.getBoundingClientRect()
      setSplit(Math.min(80, Math.max(20, ((event.clientY - rect.top) / rect.height) * 100)))
    }
    const stop = () => {
      element.removeEventListener('pointermove', move)
      element.removeEventListener('pointerup', stop)
    }
    element.addEventListener('pointermove', move)
    element.addEventListener('pointerup', stop)
  }

  if (!showIntruderRun) return null
  const running = state.job_state === 'running'
  const completed = results.filter((r) => r.error || r.status_code != null).length
  return (
    <div className="modal-backdrop" onClick={() => setShowIntruderRun(false)}>
      <section
        className="intruder-run-modal"
        role="dialog"
        aria-modal="true"
        aria-label="Intruder run"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="intruder-run-head">
          <div className="inline">
            {running ? <LoaderCircle size={15} className="spin" /> : <Zap size={15} />}
            <strong>{intruderTab.name}</strong>
            <span className="muted">
              {completed} of {results.length || '…'} completed
            </span>
          </div>
          <div className="inline">
            {running && (
              <Button
                className="danger"
                onClick={() => void run(() => api.request('intruder.cancel'))}
              >
                <Square size={12} />
                Cancel run
              </Button>
            )}
            <button
              className="icon-button"
              aria-label="Close run"
              onClick={() => setShowIntruderRun(false)}
            >
              <X size={18} />
            </button>
          </div>
        </div>

        <div
          className="intruder-run-body"
          ref={bodyRef}
          style={{ gridTemplateRows: `${split}% 7px minmax(0, 1fr)` }}
        >
          <div className="intruder-run-table">
            <div className="traffic-header run-row">
              {sortHeader('index', '#')}
              {sortHeader('payload', 'Payload')}
              {sortHeader('status', 'Status')}
              {sortHeader('size', 'Size')}
              {sortHeader('time', 'Time')}
            </div>
            <div className="run-scroll">
              {sorted.length ? (
                sorted.map((result) => (
                  <button
                    key={result.index}
                    className={`traffic-row run-row ${
                      runSelectedIndex === result.index ? 'selected-row' : ''
                    }`}
                    onClick={() => void selectRunResult(result)}
                  >
                    <span className="muted mono">{result.index}</span>
                    <span className="mono path-cell" title={result.payload || '(empty)'}>
                      {result.payload || <span className="muted">(empty)</span>}
                    </span>
                    <span>
                      {result.error ? (
                        <span className="status-code bad">err</span>
                      ) : (
                        <Status value={result.status_code} />
                      )}
                    </span>
                    <span className="muted mono">
                      {result.response_body_size != null ? bytes(result.response_body_size) : '—'}
                    </span>
                    <span className="muted mono">{duration(result.duration_ms)}</span>
                  </button>
                ))
              ) : (
                <Empty icon={<Zap size={24} />} title="Waiting for the first response">
                  Requests will appear here as the run sends them.
                </Empty>
              )}
            </div>
          </div>

          <div
            className="split-handle"
            role="separator"
            aria-label="Resize results and inspector"
            aria-valuenow={split}
            aria-valuemin={20}
            aria-valuemax={80}
            tabIndex={0}
            onPointerDown={resize}
            onKeyDown={(e) => {
              if (e.key === 'ArrowUp') setSplit((v) => Math.max(20, v - 3))
              if (e.key === 'ArrowDown') setSplit((v) => Math.min(80, v + 3))
            }}
          >
            <span />
          </div>

          <div className="intruder-run-inspector">
            <div className="inspector-bar">
              <div className="inline">
                <span className="inspector-label">INSPECTOR</span>
                {runDetailLoading ? (
                  <LoaderCircle size={13} className="spin" />
                ) : runDetail ? (
                  <>
                    <span className={`method method-${runDetail.method.toLowerCase()}`}>
                      {runDetail.method}
                    </span>
                    <span className="mono ellipsis">
                      {runDetail.host}
                      {runDetail.path}
                    </span>
                  </>
                ) : (
                  <span className="muted">
                    {runSelectedIndex == null ? 'No request selected' : 'No response captured'}
                  </span>
                )}
              </div>
              <div className="inline">
                <Button
                  className="subtle"
                  disabled={!runDetail || runDetail.truncated || runDetail.binary}
                  onClick={() => {
                    if (runDetail) {
                      toRepeater(runDetail)
                      setShowIntruderRun(false)
                    }
                  }}
                >
                  Send to Repeater <ArrowRight size={13} />
                </Button>
              </div>
            </div>
            <div className="editor-split">
              <Editor title="Request" value={runDetail?.request ?? ''} />
              <Editor
                title="Response"
                value={runDetail?.response ?? ''}
                hint={
                  runDetail?.status_code
                    ? `${runDetail.status_code} · ${duration(runDetail.duration_ms)}`
                    : undefined
                }
              />
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}

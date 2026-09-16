import {
  ArrowRight,
  Bookmark,
  ChevronLeft,
  ChevronRight,
  Crosshair,
  Globe2,
  LoaderCircle,
  LockKeyhole,
  Radio,
  Search,
  SlidersHorizontal,
  X,
} from 'lucide-react'
import { api } from '../api'
import {
  Button,
  ContextMenu,
  Editor,
  Empty,
  Status,
  bytes,
  duration,
  useContextMenu,
} from '../components'
import { filterChips } from '../historyFilters'
import { HistoryFilterModal } from './HistoryFilterModal'

import type { WorkspaceController } from '../hooks/useWorkspace'

export function HistoryView({ workspace }: { workspace: WorkspaceController }) {
  const {
    state,
    setRevision,
    flows,
    total,
    unfilteredTotal,
    query,
    setQuery,
    filters,
    updateFilters,
    resetFilters,
    activeFilterCount,
    showFilters,
    setShowFilters,
    page,
    setPage,
    selected,
    setSelected,
    loadingDetail,
    selectedId,
    port,
    setShowHelp,
    searchRef,
    scrollRef,
    scrollTop,
    setScrollTop,
    split,
    setSplit,
    historyRef,
    run,
    trafficStart,
    visibleTraffic,
    selectFlow,
    toRepeater,
    toIntruder,
    resize,
  } = workspace
  const ctx = useContextMenu()
  const chips = filterChips(filters)
  return (
    <div
      className="history-workspace"
      ref={historyRef}
      style={{ gridTemplateRows: `${split}% 7px minmax(0, 1fr)` }}
    >
      <section className="traffic-panel">
        <div className="traffic-toolbar">
          <label className="search-box">
            <Search size={15} />
            <input
              ref={searchRef}
              aria-label="Search traffic"
              placeholder="Filter by host, path, method, or status…"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
            <kbd>Ctrl K</kbd>
          </label>
          <Button
            className={filters.inScopeOnly ? 'selected' : 'subtle'}
            aria-pressed={filters.inScopeOnly}
            onClick={() => updateFilters({ inScopeOnly: !filters.inScopeOnly })}
          >
            <Crosshair size={14} />
            In scope
          </Button>
          <Button
            title="Show bookmarked traffic"
            aria-label="Show bookmarked traffic"
            aria-pressed={filters.bookmarkedOnly}
            className={filters.bookmarkedOnly ? 'selected icon-only' : 'subtle icon-only'}
            onClick={() => updateFilters({ bookmarkedOnly: !filters.bookmarkedOnly })}
          >
            <Bookmark size={14} />
          </Button>
          <Button
            className={showFilters || activeFilterCount ? 'selected' : 'subtle'}
            aria-haspopup="dialog"
            aria-expanded={showFilters}
            onClick={() => setShowFilters((v) => !v)}
          >
            <SlidersHorizontal size={14} />
            Filters
            {activeFilterCount > 0 && <span className="filter-badge">{activeFilterCount}</span>}
          </Button>
        </div>
        {chips.length > 0 && (
          <div className="filter-chips">
            <span className="filter-chips-label">Active</span>
            {chips.map((chip) => (
              <button
                key={chip.id}
                className="filter-chip"
                title={`Remove filter: ${chip.label}`}
                onClick={() => updateFilters(chip.clear)}
              >
                {chip.label}
                <X size={11} />
              </button>
            ))}
            <button className="filter-chip-clear" onClick={resetFilters}>
              Clear all
            </button>
          </div>
        )}
        <div className="traffic-header traffic-row">
          <span>#</span>
          <span>Method</span>
          <span>Host</span>
          <span>Path</span>
          <span>Status</span>
          <span>Size</span>
          <span>Time</span>
          <span />
        </div>
        <div
          className="traffic-scroll"
          ref={scrollRef}
          onScroll={(e) => setScrollTop(e.currentTarget.scrollTop)}
        >
          {flows.length ? (
            <div style={{ height: flows.length * 35, position: 'relative' }}>
              <div style={{ position: 'absolute', top: trafficStart * 35, left: 0, right: 0 }}>
                {visibleTraffic.map((flow) => (
                  <button
                    className={`traffic-row ${selectedId === flow.flow_id ? 'selected-row' : ''}`}
                    key={flow.flow_id}
                    onClick={() => void selectFlow(flow.flow_id)}
                    onContextMenu={(e) => {
                      void selectFlow(flow.flow_id)
                      ctx.open(e, [
                        {
                          label: 'Send to Repeater',
                          shortcut: 'Ctrl+R',
                          onClick: async () => {
                            const detail = await api.request<import('../types').Detail>(
                              'history.detail',
                              { flow_id: flow.flow_id },
                            )
                            toRepeater(detail)
                          },
                        },
                        {
                          label: 'Send to Intruder',
                          shortcut: 'Ctrl+I',
                          onClick: async () => {
                            const detail = await api.request<import('../types').Detail>(
                              'history.detail',
                              { flow_id: flow.flow_id },
                            )
                            toIntruder(detail)
                          },
                        },
                      ])
                    }}
                  >
                    <span className="muted mono">{flow.id}</span>
                    <span className={`method method-${flow.method.toLowerCase()}`}>
                      {flow.method}
                    </span>
                    <span className="host-cell">
                      {flow.scheme === 'https' ? <LockKeyhole size={11} /> : <Globe2 size={11} />}
                      <span>{flow.host}</span>
                    </span>
                    <span className="mono path-cell" title={flow.path}>
                      {flow.path}
                    </span>
                    <span>
                      <Status value={flow.status_code} />
                    </span>
                    <span className="muted mono">{bytes(flow.response_body_size)}</span>
                    <span className="muted mono">{duration(flow.duration_ms)}</span>
                    <span className="row-mark">
                      {flow.bookmarked ? (
                        <Bookmark size={12} />
                      ) : flow.scope ? (
                        <span className="scope-dot" />
                      ) : null}
                    </span>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <Empty
              icon={<Radio size={28} />}
              title={
                query || activeFilterCount
                  ? 'No matching requests'
                  : 'Your next discovery starts here'
              }
            >
              {query || activeFilterCount ? (
                'Try another search or turn off the active filters.'
              ) : (
                <>
                  Start the proxy and route your browser through <code>127.0.0.1:{state.port}</code>
                  .<br />
                  Captured traffic will appear here in real time.
                  <button className="text-button" onClick={() => setShowHelp(true)}>
                    Set up your browser <ArrowRight size={13} />
                  </button>
                </>
              )}
            </Empty>
          )}
        </div>
        <div className="table-footer">
          <span>
            <span className={`dot ${state.running ? 'green' : ''}`} />
            {state.running ? 'Live capture' : 'Capture paused'}
            <span className="footer-separator">/</span>
            {total !== unfilteredTotal ? (
              <span>
                <strong>{total.toLocaleString()}</strong> of {unfilteredTotal.toLocaleString()}{' '}
                requests
              </span>
            ) : (
              <span>
                <strong>{total.toLocaleString()}</strong> requests
              </span>
            )}
          </span>
          <div className="inline">
            <span>
              {total ? `${page * 100 + 1}–${Math.min((page + 1) * 100, total)}` : '0'} of {total}
            </span>
            <button
              aria-label="Previous page"
              disabled={page === 0}
              onClick={() => setPage((p) => p - 1)}
            >
              <ChevronLeft size={14} />
            </button>
            <button
              aria-label="Next page"
              disabled={(page + 1) * 100 >= total}
              onClick={() => setPage((p) => p + 1)}
            >
              <ChevronRight size={14} />
            </button>
          </div>
        </div>
      </section>
      <div
        className="split-handle"
        role="separator"
        aria-label="Resize traffic and inspector"
        aria-valuenow={split}
        aria-valuemin={25}
        aria-valuemax={72}
        tabIndex={0}
        onPointerDown={resize}
        onKeyDown={(e) => {
          if (e.key === 'ArrowUp') setSplit((v) => Math.max(25, v - 3))
          if (e.key === 'ArrowDown') setSplit((v) => Math.min(72, v + 3))
        }}
      >
        <span />
      </div>
      <section className="inspector">
        <div className="inspector-bar">
          <div className="inline">
            <span className="inspector-label">INSPECTOR</span>
            {loadingDetail ? (
              <LoaderCircle size={13} className="spin" />
            ) : selected ? (
              <>
                <span className={`method method-${selected.method.toLowerCase()}`}>
                  {selected.method}
                </span>
                <span className="mono ellipsis">
                  {selected.host}
                  {selected.path}
                </span>
              </>
            ) : (
              <span className="muted">No request selected</span>
            )}
          </div>
          <div className="inline">
            {selected?.truncated && (
              <span className="warning-text">Preview limited to 256 KiB</span>
            )}
            <Button
              className="subtle icon-only"
              aria-label="Bookmark selected request"
              disabled={!selected}
              onClick={() =>
                void run(async () => {
                  if (!selected) return
                  await api.request('history.metadata', {
                    flow_id: selected.flow_id,
                    bookmarked: !selected.bookmarked,
                    notes: selected.notes,
                  })
                  setSelected({ ...selected, bookmarked: !selected.bookmarked })
                  setRevision((v) => v + 1)
                })
              }
            >
              <Bookmark size={13} fill={selected?.bookmarked ? 'currentColor' : 'none'} />
            </Button>
            <Button
              className="subtle"
              disabled={!selected || selected.truncated || selected.binary}
              onClick={() => selected && toRepeater(selected)}
            >
              Send to Repeater <ArrowRight size={13} />
            </Button>
          </div>
        </div>
        <div
          className="editor-split"
          onContextMenu={(e) => {
            if (!selected) return
            ctx.open(e, [
              {
                label: 'Send to Repeater',
                shortcut: 'Ctrl+R',
                disabled: !selected || selected.truncated || selected.binary,
                onClick: () => selected && toRepeater(selected),
              },
              {
                label: 'Send to Intruder',
                shortcut: 'Ctrl+I',
                disabled: !selected || selected.truncated || selected.binary,
                onClick: () => selected && toIntruder(selected),
              },
            ])
          }}
        >
          <Editor title="Request" value={selected?.request ?? ''} />
          <Editor
            title="Response"
            value={selected?.response ?? ''}
            hint={
              selected?.status_code
                ? `${selected.status_code} · ${duration(selected.duration_ms)}`
                : undefined
            }
          />
        </div>
      </section>
      <ContextMenu menu={ctx.menu} onClose={ctx.close} />
      {showFilters && (
        <HistoryFilterModal
          filters={filters}
          onChange={updateFilters}
          onReset={resetFilters}
          onClose={() => setShowFilters(false)}
          total={total}
          unfiltered={unfilteredTotal}
        />
      )}
    </div>
  )
}

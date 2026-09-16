import { Search, SlidersHorizontal, X } from 'lucide-react'
import { useEffect, type ReactNode } from 'react'
import { Button } from '../components'
import {
  MIME_OPTIONS,
  STATUS_OPTIONS,
  countActiveFilters,
  type HistoryFilters,
} from '../historyFilters'

type Props = {
  filters: HistoryFilters
  onChange: (patch: Partial<HistoryFilters>) => void
  onReset: () => void
  onClose: () => void
  total: number
  unfiltered: number
}

function FilterSection({
  title,
  action,
  children,
}: {
  title: string
  action?: ReactNode
  children: ReactNode
}) {
  return (
    <section className="filter-section">
      <div className="filter-section-head">
        <h4>{title}</h4>
        {action}
      </div>
      <div className="filter-section-body">{children}</div>
    </section>
  )
}

function SelectAll({ onAll, onNone }: { onAll: () => void; onNone: () => void }) {
  return (
    <div className="filter-section-actions">
      <button type="button" onClick={onAll}>
        All
      </button>
      <span aria-hidden="true">·</span>
      <button type="button" onClick={onNone}>
        None
      </button>
    </div>
  )
}

function CheckRow({
  label,
  hint,
  checked,
  onChange,
}: {
  label: string
  hint?: string
  checked: boolean
  onChange: (checked: boolean) => void
}) {
  return (
    <label className={`filter-check ${checked ? 'checked' : ''}`}>
      <input type="checkbox" checked={checked} onChange={(e) => onChange(e.target.checked)} />
      <span className="filter-check-text">
        {label}
        {hint && <small>{hint}</small>}
      </span>
    </label>
  )
}

export function HistoryFilterModal({
  filters,
  onChange,
  onReset,
  onClose,
  total,
  unfiltered,
}: Props) {
  useEffect(() => {
    const handler = (event: KeyboardEvent) => {
      if (event.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [onClose])

  const active = countActiveFilters(filters)
  const selectMime = (value: string, checked: boolean) =>
    onChange({
      mimeTypes: checked
        ? [...filters.mimeTypes, value]
        : filters.mimeTypes.filter((item) => item !== value),
    })
  const selectStatus = (value: string, checked: boolean) =>
    onChange({
      statusClasses: checked
        ? [...filters.statusClasses, value]
        : filters.statusClasses.filter((item) => item !== value),
    })

  return (
    <div className="modal-backdrop" onMouseDown={onClose}>
      <section
        className="filter-modal"
        role="dialog"
        aria-modal="true"
        aria-label="Advanced HTTP history filter"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <header className="filter-modal-head">
          <div className="filter-modal-title">
            <SlidersHorizontal size={15} />
            <strong>Advanced filter</strong>
            {active > 0 && <span className="filter-badge">{active}</span>}
          </div>
          <button className="icon-button" aria-label="Close advanced filter" onClick={onClose}>
            <X size={16} />
          </button>
        </header>

        <div className="filter-modal-body">
          <div className="filter-column">
            <FilterSection title="Request type">
              <CheckRow
                label="In-scope items only"
                checked={filters.inScopeOnly}
                onChange={(value) => onChange({ inScopeOnly: value })}
              />
              <CheckRow
                label="Hide items without responses"
                checked={filters.hideWithoutResponses}
                onChange={(value) => onChange({ hideWithoutResponses: value })}
              />
              <CheckRow
                label="Parameterized requests only"
                checked={filters.parameterizedOnly}
                onChange={(value) => onChange({ parameterizedOnly: value })}
              />
            </FilterSection>

            <FilterSection
              title="Status code"
              action={
                <SelectAll
                  onAll={() => onChange({ statusClasses: STATUS_OPTIONS.map((o) => o.value) })}
                  onNone={() => onChange({ statusClasses: [] })}
                />
              }
            >
              <div className="filter-grid two">
                {STATUS_OPTIONS.map((option) => (
                  <CheckRow
                    key={option.value}
                    label={option.label}
                    hint={option.hint}
                    checked={filters.statusClasses.includes(option.value)}
                    onChange={(value) => selectStatus(option.value, value)}
                  />
                ))}
              </div>
            </FilterSection>

            <FilterSection
              title="MIME type"
              action={
                <SelectAll
                  onAll={() => onChange({ mimeTypes: MIME_OPTIONS.map((o) => o.value) })}
                  onNone={() => onChange({ mimeTypes: [] })}
                />
              }
            >
              <div className="filter-grid two">
                {MIME_OPTIONS.map((option) => (
                  <CheckRow
                    key={option.value}
                    label={option.label}
                    checked={filters.mimeTypes.includes(option.value)}
                    onChange={(value) => selectMime(option.value, value)}
                  />
                ))}
              </div>
            </FilterSection>
          </div>

          <div className="filter-column">
            <FilterSection title="Request fields">
              <div className="filter-fields">
                <label>
                  <span>Host</span>
                  <input
                    value={filters.host}
                    placeholder="example.com"
                    onChange={(e) => onChange({ host: e.target.value })}
                  />
                </label>
                <label>
                  <span>Path</span>
                  <input
                    value={filters.path}
                    placeholder="/api/users"
                    onChange={(e) => onChange({ path: e.target.value })}
                  />
                </label>
                <label>
                  <span>Method</span>
                  <input
                    value={filters.method}
                    placeholder="GET"
                    onChange={(e) => onChange({ method: e.target.value })}
                  />
                </label>
                <label>
                  <span>Status</span>
                  <input
                    value={filters.status}
                    placeholder="200 or 2xx"
                    onChange={(e) => onChange({ status: e.target.value })}
                  />
                </label>
                <label>
                  <span>MIME</span>
                  <input
                    value={filters.mime}
                    placeholder="application/json"
                    onChange={(e) => onChange({ mime: e.target.value })}
                  />
                </label>
                <label>
                  <span>Size</span>
                  <input
                    value={filters.size}
                    placeholder="> 1024"
                    onChange={(e) => onChange({ size: e.target.value })}
                  />
                </label>
                <label>
                  <span>Time (epoch)</span>
                  <input
                    value={filters.time}
                    placeholder="> 1700000000"
                    onChange={(e) => onChange({ time: e.target.value })}
                  />
                </label>
                <label>
                  <span>Tool</span>
                  <input
                    value={filters.tool}
                    placeholder="Proxy"
                    onChange={(e) => onChange({ tool: e.target.value })}
                  />
                </label>
              </div>
            </FilterSection>

            <FilterSection title="File extension">
              <div className="filter-fields">
                <label>
                  <span>Show only</span>
                  <input
                    value={filters.showExtensions}
                    placeholder="php, aspx, jsp"
                    onChange={(e) => onChange({ showExtensions: e.target.value })}
                  />
                </label>
                <label>
                  <span>Hide</span>
                  <input
                    value={filters.hideExtensions}
                    placeholder="png, css, woff"
                    onChange={(e) => onChange({ hideExtensions: e.target.value })}
                  />
                </label>
              </div>
            </FilterSection>

            <FilterSection title="Annotation">
              <CheckRow
                label="Items with notes"
                checked={filters.notesOnly}
                onChange={(value) => onChange({ notesOnly: value })}
              />
              <CheckRow
                label="Highlighted items"
                checked={filters.highlightedOnly}
                onChange={(value) => onChange({ highlightedOnly: value })}
              />
              <CheckRow
                label="Bookmarked items"
                checked={filters.bookmarkedOnly}
                onChange={(value) => onChange({ bookmarkedOnly: value })}
              />
            </FilterSection>
          </div>

          <div className="filter-column">
            <FilterSection
              title="Search match"
              action={
                <span className="filter-section-note">
                  <Search size={11} /> toolbar search
                </span>
              }
            >
              <CheckRow
                label="Regex"
                checked={filters.regex}
                onChange={(value) => onChange({ regex: value })}
              />
              <CheckRow
                label="Case sensitive"
                checked={filters.caseSensitive}
                onChange={(value) => onChange({ caseSensitive: value })}
              />
              <CheckRow
                label="Negative search"
                checked={filters.negativeSearch}
                onChange={(value) => onChange({ negativeSearch: value })}
              />
              <p className="filter-hint">
                These options change how the search box in the toolbar matches captured traffic.
              </p>
            </FilterSection>

            <FilterSection title="Listener">
              <div className="filter-fields">
                <label>
                  <span>Port</span>
                  <input
                    value={filters.listenerPort}
                    placeholder="8080"
                    onChange={(e) => onChange({ listenerPort: e.target.value })}
                  />
                </label>
              </div>
              <p className="filter-hint">Limit results to a single listener port.</p>
            </FilterSection>
          </div>
        </div>

        <footer className="filter-modal-foot">
          <Button className="subtle" disabled={active === 0} onClick={onReset}>
            Reset all
          </Button>
          <span className="grow" />
          <span className="filter-summary">
            <strong>{total.toLocaleString()}</strong>
            {total === unfiltered ? ' requests' : ` of ${unfiltered.toLocaleString()} requests`}
          </span>
          <Button className="primary" onClick={onClose}>
            Done
          </Button>
        </footer>
      </section>
    </div>
  )
}

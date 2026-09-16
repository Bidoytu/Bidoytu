import { Braces, Copy, FileCode2 } from 'lucide-react'
import { api } from './api'
import { useCallback, useEffect, useMemo, useRef, useState, type ReactNode } from 'react'

export type ContextMenuItem = {
  label: string
  shortcut?: string
  disabled?: boolean
  onClick: () => void
}
export function useContextMenu() {
  const [menu, setMenu] = useState<{ x: number; y: number; items: ContextMenuItem[] } | null>(null)
  const open = useCallback(
    (e: React.MouseEvent, items: ContextMenuItem[]) => {
      e.preventDefault()
      e.stopPropagation()
      setMenu({ x: e.clientX, y: e.clientY, items })
    },
    [],
  )
  const close = useCallback(() => setMenu(null), [])
  return { menu, open, close }
}
export function ContextMenu({
  menu,
  onClose,
}: {
  menu: { x: number; y: number; items: ContextMenuItem[] } | null
  onClose: () => void
}) {
  if (!menu) return null
  return (
    <>
      <div className="context-menu-backdrop" onMouseDown={onClose} onContextMenu={(e) => { e.preventDefault(); onClose() }} />
      <div className="context-menu" style={{ left: menu.x, top: menu.y }}>
        {menu.items.map((item, i) => (
          <button
            key={i}
            disabled={item.disabled}
            onClick={() => {
              item.onClick()
              onClose()
            }}
          >
            <span>{item.label}</span>
            {item.shortcut && <span className="context-menu-shortcut">{item.shortcut}</span>}
          </button>
        ))}
      </div>
    </>
  )
}

export function Button({
  children,
  className = '',
  ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button className={`button ${className}`} {...props}>
      {children}
    </button>
  )
}
export function Empty({
  icon,
  title,
  children,
}: {
  icon: ReactNode
  title: string
  children: ReactNode
}) {
  return (
    <div className="empty">
      <div className="empty-icon">{icon}</div>
      <h3>{title}</h3>
      <p>{children}</p>
    </div>
  )
}
export function Toggle({
  enabled,
  onChange,
  label,
  disabled = false,
}: {
  enabled: boolean
  onChange: () => void
  label: string
  disabled?: boolean
}) {
  return (
    <button
      role="switch"
      aria-checked={enabled}
      aria-label={label}
      className={`toggle ${enabled ? 'on' : ''}`}
      disabled={disabled}
      onClick={onChange}
    >
      <span />
    </button>
  )
}
export function Editor({
  title,
  value,
  onChange,
  hint,
  actions,
  disabled = false,
}: {
  title: string
  value: string
  onChange?: (value: string) => void
  hint?: string
  actions?: ReactNode
  disabled?: boolean
}) {
  const [pretty, setPretty] = useState(false)
  const [copied, setCopied] = useState(false)
  const [copyFailed, setCopyFailed] = useState(false)
  const [scrollTop, setScrollTop] = useState(0)
  const [viewportHeight, setViewportHeight] = useState(900)
  const viewport = useRef<HTMLDivElement>(null)
  const displayed = useMemo(() => {
    if (!pretty) return value
    const separator = value.includes('\r\n\r\n') ? '\r\n\r\n' : '\n\n'
    const index = value.indexOf(separator)
    try {
      return index < 0
        ? JSON.stringify(JSON.parse(value), null, 2)
        : value.slice(0, index) +
            separator +
            JSON.stringify(JSON.parse(value.slice(index + separator.length)), null, 2)
    } catch {
      return value
    }
  }, [value, pretty])
  const lines = useMemo(() => displayed.split('\n'), [displayed])
  const firstLine = Math.max(0, Math.floor(scrollTop / 20) - 8)
  const visibleLines = lines.slice(firstLine, firstLine + Math.ceil(viewportHeight / 20) + 16)
  useEffect(() => {
    setScrollTop(0)
    if (viewport.current) viewport.current.scrollTop = 0
  }, [value, pretty])
  useEffect(() => {
    const element = viewport.current
    if (!element) return
    const observer = new ResizeObserver(() => setViewportHeight(element.clientHeight))
    observer.observe(element)
    return () => observer.disconnect()
  }, [pretty, !!onChange])
  return (
    <section className="editor">
      <div className="panel-title">
        <span>
          <FileCode2 size={14} />
          {title}
        </span>
        <div className="inline">
          {hint && <small>{hint}</small>}
          {actions}
        </div>
      </div>
      <div className="editor-toolbar">
        <button className={!pretty ? 'tab active' : 'tab'} onClick={() => setPretty(false)}>
          Raw
        </button>
        <button className={pretty ? 'tab active' : 'tab'} onClick={() => setPretty(true)}>
          <Braces size={12} />
          Pretty
        </button>
        <span className="grow" />
        <button
          className="icon-button"
          title={copied ? 'Copied' : 'Copy message'}
          aria-label="Copy message"
          onClick={async () => {
            try {
              await api.copyText(displayed)
              setCopied(true)
              setTimeout(() => setCopied(false), 1500)
            } catch {
              setCopyFailed(true)
              setTimeout(() => setCopyFailed(false), 2500)
            }
          }}
        >
          <Copy size={13} />
          {copied && <small>Copied</small>}
          {copyFailed && <small>Copy unavailable</small>}
        </button>
      </div>
      <div className="editor-body">
        {onChange && !pretty ? (
          <textarea
            aria-label={`${title} editor`}
            spellCheck={false}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            disabled={disabled}
          />
        ) : (
          <div
            ref={viewport}
            onScroll={(e) => setScrollTop(e.currentTarget.scrollTop)}
            className="code-view"
            tabIndex={0}
            role="region"
            aria-label={`${title} message`}
          >
            {value ? (
              <div style={{ height: lines.length * 20, position: 'relative' }}>
                <div style={{ position: 'absolute', top: firstLine * 20, minWidth: '100%' }}>
                  {visibleLines.map((line, index) => (
                    <div className="code-line" key={firstLine + index}>
                      <span className="line-number">{firstLine + index + 1}</span>
                      <span
                        className={
                          firstLine + index === 0
                            ? 'code-first'
                            : line.match(/^[\w-]+:/)
                              ? 'code-header'
                              : 'code-text'
                        }
                      >
                        {line || ' '}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="code-placeholder">
                {title === 'Response'
                  ? 'The response will appear here.'
                  : 'Select a request to inspect its contents.'}
              </div>
            )}
          </div>
        )}
      </div>
      <div className="editor-footer">
        <span>
          {onChange && !pretty
            ? 'Editable · UTF-8 text'
            : pretty
              ? 'Formatted view · original message preserved'
              : 'Read only · UTF-8 preview'}
        </span>
        <span>{value.length.toLocaleString()} characters</span>
      </div>
    </section>
  )
}
export function bytes(value: number) {
  return value < 1024
    ? `${value} B`
    : value < 1048576
      ? `${(value / 1024).toFixed(1)} KB`
      : `${(value / 1048576).toFixed(1)} MB`
}
export function duration(value?: number | null) {
  return value == null ? '—' : `${Math.round(value)} ms`
}
export function Status({ value }: { value?: number | null }) {
  return (
    <span
      className={`status-code ${value && value >= 400 ? 'bad' : value && value >= 300 ? 'redirect' : ''}`}
    >
      {value ?? '…'}
    </span>
  )
}

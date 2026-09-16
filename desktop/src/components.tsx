import { Binary, Braces, Copy, FileCode2 } from 'lucide-react'
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
  const open = useCallback((e: React.MouseEvent, items: ContextMenuItem[]) => {
    e.preventDefault()
    e.stopPropagation()
    setMenu({ x: e.clientX, y: e.clientY, items })
  }, [])
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
      <div
        className="context-menu-backdrop"
        onMouseDown={onClose}
        onContextMenu={(e) => {
          e.preventDefault()
          onClose()
        }}
      />
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
type EditorView = 'pretty' | 'raw' | 'hex'

function formatMessage(value: string): string {
  const separator = value.includes('\r\n\r\n') ? '\r\n\r\n' : '\n\n'
  const index = value.indexOf(separator)
  if (index < 0) return formatPayload(value, '')
  const headers = value.slice(0, index)
  const body = value.slice(index + separator.length)
  const contentType = headers.match(/^content-type\s*:\s*([^;\r\n]+)/im)?.[1] ?? ''
  return headers + separator + formatPayload(body, contentType)
}

function formatPayload(value: string, contentType: string): string {
  const text = value.trim()
  if (!text) return value
  const type = contentType.toLowerCase()
  if (type.includes('json') || /^[\[{]/.test(text)) {
    try {
      return JSON.stringify(JSON.parse(text), null, 2)
    } catch {
      // Continue with the content-type-specific formatter below.
    }
  }
  if (
    type.includes('html') ||
    type.includes('xml') ||
    /^<!doctype\s+html|^<(?:html|head|body|div|main|section|article|svg|\/?[a-z]+[\s>])/i.test(text)
  ) {
    return beautifyMarkup(text)
  }
  if (
    type.includes('javascript') ||
    type.includes('ecmascript') ||
    type.includes('typescript') ||
    /^(?:#!.*\n)?\s*(?:import\s|export\s|(?:const|let|var|function|class)\s|(?:if|for|while|switch|try)\s*\(|[\w$.]+\s*=>)/.test(
      text,
    )
  ) {
    return beautifyCode(text)
  }
  if (type.includes('css') || /^[^{]+\{\s*[\w-]+\s*:/m.test(text)) return beautifyCode(text)
  if (type.includes('x-www-form-urlencoded')) {
    return text
      .split('&')
      .map((part) => part.replace('=', ' = '))
      .join('\n')
  }
  return value
}

function beautifyMarkup(value: string): string {
  const tokens = value.replace(/>\s+</g, '><').match(/<!--[\s\S]*?-->|<![^>]*>|<[^>]+>|[^<]+/g) ?? [
    value,
  ]
  const lines: string[] = []
  let indent = 0
  const voidTag = /^(area|base|br|col|embed|hr|img|input|link|meta|param|source|track|wbr)\b/i
  for (const token of tokens) {
    const part = token.trim()
    if (!part) continue
    if (part.startsWith('</')) indent = Math.max(0, indent - 1)
    if (part.startsWith('<script') || part.startsWith('<style')) {
      lines.push(`${'  '.repeat(indent)}${part}`)
      indent += 1
    } else if (part.startsWith('</script') || part.startsWith('</style')) {
      indent = Math.max(0, indent - 1)
      lines.push(`${'  '.repeat(indent)}${part}`)
    } else {
      lines.push(`${'  '.repeat(indent)}${part}`)
      if (
        part.startsWith('<') &&
        !part.startsWith('</') &&
        !part.startsWith('<!') &&
        !part.startsWith('<?') &&
        !part.endsWith('/>') &&
        !voidTag.test(part.slice(1))
      )
        indent += 1
    }
  }
  return lines.join('\n')
}

function beautifyCode(value: string): string {
  const lines: string[] = []
  let current = ''
  let indent = 0
  let quote = ''
  let escaped = false
  const flush = () => {
    const line = current.trim()
    if (line) lines.push(`${'  '.repeat(indent)}${line}`)
    current = ''
  }
  for (const char of value) {
    if (quote) {
      current += char
      if (escaped) escaped = false
      else if (char === '\\') escaped = true
      else if (char === quote) quote = ''
      continue
    }
    if (char === '"' || char === "'" || char === '`') {
      quote = char
      current += char
      continue
    }
    if (char === '{') {
      current = current.trimEnd() + ' {'
      flush()
      indent += 1
      continue
    }
    if (char === '}') {
      flush()
      indent = Math.max(0, indent - 1)
      current = '}'
      continue
    }
    if (char === ';') {
      current = current.trimEnd() + ';'
      flush()
      continue
    }
    if (char === '\n' || char === '\r') {
      flush()
      continue
    }
    current += char
  }
  flush()
  return lines.join('\n')
}

function buildHexLines(value: string) {
  const bytes = new TextEncoder().encode(value)
  const lines: { offset: string; hex: string; ascii: string }[] = []
  for (let index = 0; index < bytes.length; index += 16) {
    const slice = bytes.subarray(index, index + 16)
    const parts: string[] = []
    for (let offset = 0; offset < 16; offset += 1) {
      parts.push(offset < slice.length ? slice[offset].toString(16).padStart(2, '0') : '  ')
    }
    const hex = `${parts.slice(0, 8).join(' ')}  ${parts.slice(8).join(' ')}`
    const ascii = Array.from(slice, (byte) =>
      byte >= 32 && byte < 127 ? String.fromCharCode(byte) : '.',
    ).join('')
    lines.push({ offset: index.toString(16).padStart(8, '0'), hex, ascii })
  }
  return { lines, bytes: bytes.length }
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
  const [view, setView] = useState<EditorView>('pretty')
  const [wrap, setWrap] = useState(true)
  const [copied, setCopied] = useState(false)
  const [copyFailed, setCopyFailed] = useState(false)
  const [scrollTop, setScrollTop] = useState(0)
  const [viewportHeight, setViewportHeight] = useState(900)
  const viewport = useRef<HTMLDivElement>(null)
  const prettyText = useMemo(
    () => (view === 'pretty' ? formatMessage(value) : value),
    [value, view],
  )
  const lines = useMemo(() => prettyText.split('\n'), [prettyText])
  const hex = useMemo(() => (view === 'hex' ? buildHexLines(value) : null), [value, view])
  const firstLine = Math.max(0, Math.floor(scrollTop / 20) - 8)
  const windowSize = Math.ceil(viewportHeight / 20) + 16
  const visibleLines = lines.slice(firstLine, firstLine + windowSize)
  const visibleHex = hex ? hex.lines.slice(firstLine, firstLine + windowSize) : []
  useEffect(() => {
    setScrollTop(0)
    if (viewport.current) viewport.current.scrollTop = 0
  }, [value, view])
  useEffect(() => {
    const element = viewport.current
    if (!element) return
    const observer = new ResizeObserver(() => setViewportHeight(element.clientHeight))
    observer.observe(element)
    return () => observer.disconnect()
  }, [view, !!onChange])
  const editable = Boolean(onChange) && (view === 'pretty' || view === 'raw')
  const editorValue = view === 'pretty' ? prettyText : value
  const copyValue =
    view === 'hex' && hex
      ? hex.lines.map((line) => `${line.offset}  ${line.hex}  ${line.ascii}`).join('\n')
      : view === 'pretty'
        ? prettyText
        : value
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
        <button
          className={view === 'pretty' ? 'tab active' : 'tab'}
          aria-pressed={view === 'pretty'}
          onClick={() => setView('pretty')}
        >
          <Braces size={12} />
          Pretty
        </button>
        <button
          className={view === 'raw' ? 'tab active' : 'tab'}
          aria-pressed={view === 'raw'}
          onClick={() => setView('raw')}
        >
          Raw
        </button>
        <button
          className={view === 'hex' ? 'tab active' : 'tab'}
          aria-pressed={view === 'hex'}
          onClick={() => setView('hex')}
        >
          <Binary size={12} />
          Hex
        </button>
        <label className="wrap-toggle">
          <input
            type="checkbox"
            checked={wrap}
            onChange={(e) => setWrap(e.target.checked)}
            aria-label={`Wrap ${title.toLowerCase()} text`}
          />
          Wrap
        </label>
        <span className="grow" />
        <button
          className="icon-button"
          title={copied ? 'Copied' : 'Copy message'}
          aria-label="Copy message"
          onClick={async () => {
            try {
              await api.copyText(copyValue)
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
        {editable ? (
          <textarea
            aria-label={`${title} editor`}
            spellCheck={false}
            className={wrap ? 'wrap-editor' : undefined}
            value={editorValue}
            onChange={(e) => onChange?.(e.target.value)}
            disabled={disabled}
          />
        ) : view === 'hex' ? (
          <div
            ref={viewport}
            onScroll={(e) => setScrollTop(e.currentTarget.scrollTop)}
            className="code-view hex-view"
            tabIndex={0}
            role="region"
            aria-label={`${title} hex view`}
          >
            {value && hex ? (
              <div style={{ height: hex.lines.length * 20, position: 'relative' }}>
                <div style={{ position: 'absolute', top: firstLine * 20, minWidth: '100%' }}>
                  {visibleHex.map((line, index) => (
                    <div className="hex-line" key={firstLine + index}>
                      <span className="hex-offset">{line.offset}</span>
                      <span className="hex-bytes">{line.hex}</span>
                      <span className="hex-ascii">{line.ascii}</span>
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
        ) : (
          <div
            ref={viewport}
            onScroll={(e) => setScrollTop(e.currentTarget.scrollTop)}
            className={wrap ? 'code-view wrap-view' : 'code-view'}
            tabIndex={0}
            role="region"
            aria-label={`${title} message`}
          >
            {value ? (
              wrap ? (
                <div>
                  {lines.map((line, index) => (
                    <div className="code-line wrap" key={index}>
                      <span className="line-number">{index + 1}</span>
                      <span
                        className={
                          index === 0
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
              ) : (
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
              )
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
          {editable
            ? 'Editable · UTF-8 text'
            : view === 'pretty'
              ? 'Formatted view · original message preserved'
              : view === 'hex'
                ? 'Hex view · UTF-8 bytes'
                : 'Read only · UTF-8 preview'}
        </span>
        <span>
          {view === 'hex' && hex
            ? `${hex.bytes.toLocaleString()} bytes`
            : `${value.length.toLocaleString()} characters`}
        </span>
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

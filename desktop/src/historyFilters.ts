export type HistoryFilters = {
  host: string
  path: string
  method: string
  status: string
  mime: string
  size: string
  time: string
  tool: string
  inScopeOnly: boolean
  bookmarkedOnly: boolean
  hideWithoutResponses: boolean
  parameterizedOnly: boolean
  notesOnly: boolean
  highlightedOnly: boolean
  hideBrowserNoise: boolean
  regex: boolean
  caseSensitive: boolean
  negativeSearch: boolean
  showExtensions: string
  hideExtensions: string
  listenerPort: string
  mimeTypes: string[]
  statusClasses: string[]
}

export const EMPTY_HISTORY_FILTERS: HistoryFilters = {
  host: '',
  path: '',
  method: '',
  status: '',
  mime: '',
  size: '',
  time: '',
  tool: '',
  inScopeOnly: false,
  bookmarkedOnly: false,
  hideWithoutResponses: false,
  parameterizedOnly: false,
  notesOnly: false,
  highlightedOnly: false,
  hideBrowserNoise: true,
  regex: false,
  caseSensitive: false,
  negativeSearch: false,
  showExtensions: '',
  hideExtensions: '',
  listenerPort: '',
  // Keep the history useful for application/API traffic by default. Resource
  // types can be restored from Advanced filter when needed.
  mimeTypes: ['html', 'xml', 'other text'],
  statusClasses: ['2xx', '3xx', '4xx', '5xx'],
}

export const MIME_OPTIONS: { value: string; label: string }[] = [
  { value: 'html', label: 'HTML' },
  { value: 'script', label: 'Script' },
  { value: 'xml', label: 'XML' },
  { value: 'css', label: 'CSS' },
  { value: 'other text', label: 'Other text' },
  { value: 'images', label: 'Images' },
  { value: 'flash', label: 'Flash' },
  { value: 'other binary', label: 'Other binary' },
]

export const STATUS_OPTIONS: { value: string; label: string; hint: string }[] = [
  { value: '2xx', label: '2xx', hint: 'Success' },
  { value: '3xx', label: '3xx', hint: 'Redirection' },
  { value: '4xx', label: '4xx', hint: 'Client error' },
  { value: '5xx', label: '5xx', hint: 'Server error' },
]

const STATUS_LABELS = Object.fromEntries(STATUS_OPTIONS.map((o) => [o.value, o.label]))
const MIME_LABELS = Object.fromEntries(MIME_OPTIONS.map((o) => [o.value, o.label]))

export type FilterChip = { id: string; label: string; clear: Partial<HistoryFilters> }

export function filterChips(filters: HistoryFilters): FilterChip[] {
  const chips: FilterChip[] = []
  const flag = (key: keyof HistoryFilters, condition: boolean, label: string) => {
    if (condition) chips.push({ id: key, label, clear: { [key]: false } })
  }
  flag('inScopeOnly', filters.inScopeOnly, 'In scope')
  flag('bookmarkedOnly', filters.bookmarkedOnly, 'Bookmarked')
  flag('hideWithoutResponses', filters.hideWithoutResponses, 'Has response')
  flag('parameterizedOnly', filters.parameterizedOnly, 'Parameterized')
  flag('notesOnly', filters.notesOnly, 'Notes')
  flag('highlightedOnly', filters.highlightedOnly, 'Highlighted')
  flag('hideBrowserNoise', filters.hideBrowserNoise, 'Hide browser noise')
  flag('regex', filters.regex, 'Regex')
  flag('caseSensitive', filters.caseSensitive, 'Case sensitive')
  flag('negativeSearch', filters.negativeSearch, 'Negative search')
  const text = (key: keyof HistoryFilters, value: string, prefix: string) => {
    if (value.trim()) {
      chips.push({ id: key, label: `${prefix} ${value.trim()}`, clear: { [key]: '' } })
    }
  }
  text('host', filters.host, 'Host')
  text('path', filters.path, 'Path')
  text('method', filters.method, 'Method')
  text('status', filters.status, 'Status')
  text('mime', filters.mime, 'MIME')
  text('size', filters.size, 'Size')
  text('time', filters.time, 'Time')
  text('tool', filters.tool, 'Tool')
  text('showExtensions', filters.showExtensions, 'Only')
  text('hideExtensions', filters.hideExtensions, 'Hide')
  text('listenerPort', filters.listenerPort, 'Port')
  if (filters.mimeTypes.length !== MIME_OPTIONS.length) {
    if (filters.mimeTypes.length === 0) {
      chips.push({
        id: 'mime:none',
        label: 'No MIME types',
        clear: { mimeTypes: EMPTY_HISTORY_FILTERS.mimeTypes },
      })
    } else {
      for (const value of filters.mimeTypes) {
        chips.push({
          id: `mime:${value}`,
          label: MIME_LABELS[value] ?? value,
          clear: { mimeTypes: filters.mimeTypes.filter((item) => item !== value) },
        })
      }
    }
  }
  if (filters.statusClasses.length !== STATUS_OPTIONS.length) {
    if (filters.statusClasses.length === 0) {
      chips.push({
        id: 'status:none',
        label: 'No status classes',
        clear: { statusClasses: EMPTY_HISTORY_FILTERS.statusClasses },
      })
    } else {
      for (const value of filters.statusClasses) {
        chips.push({
          id: `status:${value}`,
          label: STATUS_LABELS[value] ?? value,
          clear: { statusClasses: filters.statusClasses.filter((item) => item !== value) },
        })
      }
    }
  }
  return chips
}

export function countActiveFilters(filters: HistoryFilters): number {
  return filterChips(filters).length
}

export function historyFilterPayload(filters: HistoryFilters): Record<string, unknown> {
  return {
    host: filters.host,
    path: filters.path,
    method: filters.method,
    status: filters.status,
    mime: filters.mime,
    size: filters.size,
    time: filters.time,
    tool: filters.tool,
    in_scope_only: filters.inScopeOnly,
    bookmarked_only: filters.bookmarkedOnly,
    hide_without_responses: filters.hideWithoutResponses,
    parameterized_only: filters.parameterizedOnly,
    notes_only: filters.notesOnly,
    highlighted_only: filters.highlightedOnly,
    hide_browser_noise: filters.hideBrowserNoise,
    regex: filters.regex,
    case_sensitive: filters.caseSensitive,
    negative_search: filters.negativeSearch,
    show_extensions: filters.showExtensions,
    hide_extensions: filters.hideExtensions,
    listener_port: filters.listenerPort,
    mime_types: filters.mimeTypes,
    status_classes: filters.statusClasses,
  }
}

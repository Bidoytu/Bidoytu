import {
  ArrowLeftRight,
  Code2,
  Crosshair,
  Radio,
  Send,
  Settings2,
  ShieldCheck,
  Zap,
} from 'lucide-react'
import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { api } from '../api'
import {
  EMPTY_HISTORY_FILTERS,
  countActiveFilters,
  historyFilterPayload,
  type HistoryFilters,
} from '../historyFilters'
import type { Detail, EngineState, Finding, Flow, JobResult } from '../types'

export type View =
  'Proxy' | 'Repeater' | 'Intruder' | 'Scope' | 'Live audit' | 'Decoder' | 'Settings'
export type RepeaterTab = {
  id: number
  name: string
  url: string
  request: string
  response?: string
  result?: Detail
  busy: boolean
  error?: string
  history?: RepeaterRevision[]
  historyIndex?: number
}
export type RepeaterRevision = { request: string; result: Detail }
export type RepeaterGroup = {
  name: string
  color: string
  tabIds: number[]
  collapsed: boolean
}
export type IntruderTab = {
  id: number
  name: string
  url: string
  request: string
  payloads: string
  results: JobResult[]
}
export type ProxyView = 'History' | 'Intercept'
const initial: EngineState = {
  protocol: 1,
  running: false,
  port: 8080,
  host: '127.0.0.1',
  intercept: false,
  responses: false,
  pending: [],
  audit: false,
  findings: 0,
  dropped: 0,
  queue_depth: 0,
  error: '',
  data_dir: '',
  scope: { include: [], exclude: [] },
  job_state: 'idle',
}
export const icons = {
  Proxy: Radio,
  Repeater: Send,
  Intruder: Zap,
  Scope: Crosshair,
  'Live audit': ShieldCheck,
  Decoder: Code2,
  Settings: Settings2,
}
export const descriptions: Record<View, string> = {
  Proxy: 'Capture, inspect, and shape traffic in flight.',
  Repeater: 'Refine a request. Explore the response.',
  Intruder: 'Controlled payload testing, powered by Python.',
  Scope: 'Define the boundaries of your investigation.',
  'Live audit': 'Evidence from the traffic you already capture.',
  Decoder: 'Make encoded data readable.',
  Settings: 'Your engine. Your workspace.',
}
export const newTab = (id: number): RepeaterTab => ({
  id,
  name: `Request ${id}`,
  url: 'https://example.com',
  request: 'GET / HTTP/1.1\r\nHost: example.com\r\nAccept: */*\r\n\r\n',
  busy: false,
})

function nextRepeaterCopyName(name: string, tabs: RepeaterTab[]) {
  const stem = name.replace(/\s*\(\d+\)\s*$/, '').trim() || 'Request'
  const pattern = new RegExp(
    `^${stem.replace(/[.*+?^${}()|[\\]\\\\]/g, '\\\\$&')}\\s*\\((\\d+)\\)$`,
  )
  const used = new Set<number>()
  for (const tab of tabs) {
    const match = tab.name.trim().match(pattern)
    if (match) used.add(Number(match[1]))
  }
  let index = 1
  while (used.has(index)) index += 1
  return `${stem} (${index})`
}
export const newIntruderTab = (id: number): IntruderTab => ({
  id,
  name: `Attack ${id}`,
  url: 'https://example.com',
  request: 'GET /?q=§payload§ HTTP/1.1\r\nHost: example.com\r\n\r\n',
  payloads: '',
  results: [],
})

export function useWorkspace() {
  const [view, setView] = useState<View>('Proxy')
  const [proxyView, setProxyView] = useState<ProxyView>('History')
  const [state, setState] = useState(initial)
  const [online, setOnline] = useState(false)
  const [connecting, setConnecting] = useState(true)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [busy, setBusy] = useState(false)
  const [revision, setRevision] = useState(0)
  const [flows, setFlows] = useState<Flow[]>([])
  const [total, setTotal] = useState(0)
  const [unfilteredTotal, setUnfilteredTotal] = useState(0)
  const [query, setQuery] = useState('')
  const [debouncedQuery, setDebouncedQuery] = useState('')
  const [filters, setFilters] = useState<HistoryFilters>(EMPTY_HISTORY_FILTERS)
  const [debouncedFilters, setDebouncedFilters] = useState<HistoryFilters>(EMPTY_HISTORY_FILTERS)
  const [showFilters, setShowFilters] = useState(false)
  const [page, setPage] = useState(0)
  const [historySort, setHistorySort] = useState<{
    key: 'id' | 'method' | 'host' | 'path' | 'status' | 'size' | 'time'
    direction: 'asc' | 'desc'
  }>({ key: 'id', direction: 'desc' })
  const [selected, setSelected] = useState<Detail | null>(null)
  const [loadingDetail, setLoadingDetail] = useState(false)
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [port, setPort] = useState(8080)
  const [verifyTLS, setVerifyTLS] = useState(true)
  const [tabs, setTabs] = useState<RepeaterTab[]>([newTab(1)])
  const [groups, setGroups] = useState<RepeaterGroup[]>([])
  const [activeTab, setActiveTab] = useState(1)
  const tabSequence = useRef(1)
  const [interceptText, setInterceptText] = useState('')
  const [interceptOriginal, setInterceptOriginal] = useState('')
  const [interceptId, setInterceptId] = useState('')
  const [interceptDetail, setInterceptDetail] = useState<Detail | null>(null)
  const [include, setInclude] = useState('')
  const [exclude, setExclude] = useState('')
  const [findings, setFindings] = useState<Finding[]>([])
  const [decoderInput, setDecoderInput] = useState('')
  const [decoderOutput, setDecoderOutput] = useState('')
  const [operation, setOperation] = useState('base64.decode')
  const [intruderTabs, setIntruderTabs] = useState<IntruderTab[]>([newIntruderTab(1)])
  const [activeIntruderTab, setActiveIntruderTab] = useState(1)
  const intruderSequence = useRef(1)
  const [intruderRunningId, setIntruderRunningId] = useState<number | null>(null)
  const [showHelp, setShowHelp] = useState(false)
  const [theme, setTheme] = useState<'light' | 'dark'>(() =>
    typeof localStorage !== 'undefined' && localStorage.getItem('bidoytu.theme') === 'dark'
      ? 'dark'
      : 'light',
  )
  const searchRef = useRef<HTMLInputElement>(null)
  const detailSequence = useRef(0)
  const historyRequestSequence = useRef(0)
  const scrollRef = useRef<HTMLDivElement>(null)
  const [scrollTop, setScrollTop] = useState(0)
  const [split, setSplit] = useState(51)
  const [interceptSplit, setInterceptSplit] = useState(51)
  const [sessionLoaded, setSessionLoaded] = useState(false)
  const sendRun = useRef(0)
  const historyRef = useRef<HTMLDivElement>(null)
  const interceptRef = useRef<HTMLDivElement>(null)
  // Refs for values accessed by the stable keyboard listener (empty deps array).
  const viewRef = useRef(view)
  viewRef.current = view
  const selectedRef = useRef(selected)
  selectedRef.current = selected
  const interceptDetailRef = useRef(interceptDetail)
  interceptDetailRef.current = interceptDetail
  const requestTab = tabs.find((t) => t.id === activeTab) ?? tabs[0]
  const intruderTab = intruderTabs.find((t) => t.id === activeIntruderTab) ?? intruderTabs[0]
  const requestTabRef = useRef(requestTab)
  requestTabRef.current = requestTab
  const intruderTabRef = useRef(intruderTab)
  intruderTabRef.current = intruderTab
  const pending = state.pending.find((p) => p.flow_id === interceptId) ?? state.pending[0]

  const run = useCallback(async <T>(fn: () => Promise<T>): Promise<T | undefined> => {
    try {
      return await fn()
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
      return undefined
    }
  }, [])
  const refresh = useCallback((next: EngineState) => {
    setState(next)
    setRevision((v) => v + 1)
  }, [])
  const updateFilters = useCallback((patch: Partial<HistoryFilters>) => {
    setFilters((previous) => ({ ...previous, ...patch }))
  }, [])
  const resetFilters = useCallback(() => setFilters(EMPTY_HISTORY_FILTERS), [])
  const clearHistory = useCallback(
    () =>
      run(async () => {
        await api.request('history.clear')
        setSelected(null)
        setSelectedId(null)
        setRevision((v) => v + 1)
        setNotice('HTTP history cleared')
      }),
    [run],
  )
  const activeFilterCount = useMemo(() => countActiveFilters(filters), [filters])

  useEffect(() => {
    if (!online) return
    let alive = true
    api
      .request<{
        tabs?: RepeaterTab[]
        groups?: RepeaterGroup[]
        intruderTabs?: IntruderTab[]
        port?: number
        verifyTLS?: boolean
      }>('workspace.load')
      .then((saved) => {
        if (!alive) return
        if (
          Array.isArray(saved.tabs) &&
          saved.tabs.length &&
          saved.tabs.every(
            (tab) =>
              Number.isInteger(tab.id) &&
              typeof tab.request === 'string' &&
              typeof tab.url === 'string',
          )
        ) {
          setTabs(saved.tabs.map((tab) => ({ ...tab, busy: false })))
          setActiveTab(saved.tabs[0].id)
          tabSequence.current = Math.max(...saved.tabs.map((tab) => tab.id))
        }
        if (Array.isArray(saved.groups)) {
          setGroups(
            saved.groups
              .filter((group) => typeof group.name === 'string' && typeof group.color === 'string')
              .map((group) => ({
                name: group.name,
                color: group.color,
                tabIds: Array.isArray(group.tabIds) ? group.tabIds.filter(Number.isInteger) : [],
                collapsed: Boolean(group.collapsed),
              })),
          )
        }
        if (
          Array.isArray(saved.intruderTabs) &&
          saved.intruderTabs.length &&
          saved.intruderTabs.every(
            (tab) =>
              Number.isInteger(tab.id) &&
              typeof tab.request === 'string' &&
              typeof tab.url === 'string',
          )
        ) {
          setIntruderTabs(
            saved.intruderTabs.map((tab) => ({
              ...newIntruderTab(tab.id),
              ...tab,
              payloads: typeof tab.payloads === 'string' ? tab.payloads : '',
              results: [],
            })),
          )
          setActiveIntruderTab(saved.intruderTabs[0].id)
          intruderSequence.current = Math.max(...saved.intruderTabs.map((tab) => tab.id))
        }
        if (saved.port && saved.port >= 1024 && saved.port <= 65535) setPort(saved.port)
        if (typeof saved.verifyTLS === 'boolean') setVerifyTLS(saved.verifyTLS)
        setSessionLoaded(true)
      })
      .catch((e) => {
        if (alive) setError(e.message)
      })
    return () => {
      alive = false
    }
  }, [online])
  useEffect(() => {
    if (!sessionLoaded) return
    const timer = setTimeout(() => {
      void run(() =>
        api.request('workspace.save', {
          tabs: tabs.map(({ id, name, url, request, history, historyIndex }) => ({
            id,
            name,
            url,
            request,
            history,
            historyIndex,
          })),
          groups,
          intruderTabs: intruderTabs.map(({ id, name, url, request, payloads }) => ({
            id,
            name,
            url,
            request,
            payloads,
          })),
          port,
          verifyTLS,
        }),
      )
    }, 350)
    return () => clearTimeout(timer)
  }, [tabs, groups, intruderTabs, port, verifyTLS, sessionLoaded, run])
  useEffect(() => {
    let alive = true
    const unsubscribe = api.onEvent((event) => {
      if (event.type === 'changed' || event.type === 'ready') {
        setOnline(true)
        refresh(event.data)
      } else {
        setOnline(false)
        setError(event.message)
      }
    })
    api
      .request<EngineState | null>('state')
      .then((next) => {
        if (!alive) return
        if (!next) return
        setOnline(true)
        refresh(next)
        setPort(next.port)
        setInclude(next.scope.include.join('\n'))
        setExclude(next.scope.exclude.join('\n'))
      })
      .catch((e) => {
        if (alive) setError(e.message)
      })
      .finally(() => {
        if (alive) setConnecting(false)
      })
    return () => {
      alive = false
      unsubscribe()
    }
  }, [refresh])
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(query)
      setPage(0)
    }, 180)
    return () => clearTimeout(timer)
  }, [query])
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedFilters(filters)
      setPage(0)
    }, 200)
    return () => clearTimeout(timer)
  }, [filters])
  useEffect(() => {
    if (!online || view !== 'Proxy' || proxyView !== 'History') return
    let alive = true
    const requestSequence = ++historyRequestSequence.current
    api
      .request<{ items: Flow[]; total: number; unfiltered: number }>('history.list', {
        query: debouncedQuery,
        offset: page * 100,
        limit: 100,
        filter: historyFilterPayload(debouncedFilters),
        sort_by: historySort.key,
        sort_direction: historySort.direction,
      })
      .then((result) => {
        if (alive && requestSequence === historyRequestSequence.current) {
          setFlows(result.items)
          setTotal(result.total)
          setUnfilteredTotal(result.unfiltered)
          if (!result.items.length && page > 0) setPage(0)
        }
      })
      .catch((e) => {
        if (alive && requestSequence === historyRequestSequence.current) setError(e.message)
      })
    return () => {
      alive = false
    }
  }, [online, revision, view, proxyView, debouncedQuery, page, debouncedFilters, historySort])
  useEffect(() => {
    setScrollTop(0)
    if (scrollRef.current) scrollRef.current.scrollTop = 0
  }, [page, debouncedQuery, debouncedFilters])
  useEffect(() => {
    if (view !== 'Proxy' || proxyView !== 'History' || !selectedId) return
    let alive = true
    api
      .request<Detail>('history.detail', { flow_id: selectedId })
      .then((detail) => {
        if (alive) setSelected(detail)
      })
      .catch(() => {})
    return () => {
      alive = false
    }
  }, [revision, selectedId, view, proxyView])
  useEffect(() => {
    if (view !== 'Proxy' || proxyView !== 'Intercept' || !pending) {
      setInterceptDetail(null)
      return
    }
    let alive = true
    setInterceptDetail(null)
    setInterceptText('')
    api
      .request<Detail>('history.detail', { flow_id: pending.flow_id })
      .then((detail) => {
        if (alive) {
          const text = pending.phase === 'response' ? detail.response : detail.request
          setInterceptText(text)
          setInterceptOriginal(text)
          setInterceptDetail(detail)
        }
      })
      .catch((e) => {
        if (alive) setError(e.message)
      })
    return () => {
      alive = false
    }
  }, [view, proxyView, pending?.flow_id, pending?.phase])
  useEffect(() => {
    if (!online) return
    if (view === 'Live audit')
      void run(async () => setFindings(await api.request<Finding[]>('audit.list')))
    if (view === 'Intruder' && intruderRunningId != null)
      void run(async () => {
        const { items } = await api.request<{ items: JobResult[] }>('intruder.results')
        setIntruderTabs((prev) =>
          prev.map((tab) => (tab.id === intruderRunningId ? { ...tab, results: items } : tab)),
        )
      })
  }, [view, online, revision, run, intruderRunningId])
  useEffect(() => {
    if (!notice) return
    const timer = setTimeout(() => setNotice(''), 3500)
    return () => clearTimeout(timer)
  }, [notice])
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    try {
      localStorage.setItem('bidoytu.theme', theme)
    } catch {
      // Ignore storage failures; theme still applies for this session.
    }
  }, [theme])
  useEffect(() => {
    const listener = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault()
        setView('Proxy')
        setProxyView('History')
        setTimeout(() => searchRef.current?.focus(), 0)
      }
      if ((e.ctrlKey || e.metaKey) && ['1', '2', '3', '4'].includes(e.key)) {
        e.preventDefault()
        if (e.key === '1') {
          setView('Proxy')
          setProxyView('History')
        } else if (e.key === '2') {
          setView('Proxy')
          setProxyView('Intercept')
        } else if (e.key === '3') setView('Repeater')
        else if (e.key === '4') setView('Intruder')
      }
      // Ctrl+R -> Send to Repeater. Inside Repeater it duplicates the active
      // request into a new tab; inside Intruder it forwards the attack template.
      // Everywhere else it uses the selected history request or the paused
      // intercepted flow. Ctrl+I mirrors this for Intruder.
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'r' && !e.shiftKey) {
        e.preventDefault()
        if (viewRef.current === 'Repeater') duplicateRepeaterTab()
        else if (viewRef.current === 'Intruder') intruderToRepeater()
        else {
          const detail =
            viewRef.current === 'Proxy' && proxyView === 'Intercept'
              ? interceptDetailRef.current
              : selectedRef.current
          if (detail) toRepeater(detail)
        }
      }
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'i' && !e.shiftKey) {
        e.preventDefault()
        if (viewRef.current === 'Intruder') duplicateIntruderTab()
        else if (viewRef.current === 'Repeater') repeaterToIntruder()
        else {
          const detail =
            viewRef.current === 'Proxy' && proxyView === 'Intercept'
              ? interceptDetailRef.current
              : selectedRef.current
          if (detail) toIntruder(detail)
        }
      }
      if (e.key === 'Escape') {
        setShowHelp(false)
        setError('')
      }
    }
    window.addEventListener('keydown', listener)
    return () => window.removeEventListener('keydown', listener)
  }, [proxyView])

  async function selectFlow(flowId: string) {
    const sequence = ++detailSequence.current
    setSelectedId(flowId)
    setSelected(null)
    setLoadingDetail(true)
    await run(async () => {
      const detail = await api.request<Detail>('history.detail', { flow_id: flowId })
      if (sequence === detailSequence.current) setSelected(detail)
    })
    if (sequence === detailSequence.current) setLoadingDetail(false)
  }
  function toRepeater(detail: Detail) {
    if (detail.truncated || detail.binary) {
      setError(
        'Binary or truncated previews cannot be replayed as text. Create a new text request.',
      )
      return
    }
    const id = ++tabSequence.current
    setTabs((prev) => [
      ...prev,
      {
        id,
        name: detail.host,
        url: `${detail.scheme}://${detail.host}:${detail.port}`,
        request: detail.request,
        busy: false,
      },
    ])
    setActiveTab(id)
    setView('Repeater')
  }
  function addIntruderTab(seed: Partial<IntruderTab>) {
    const id = ++intruderSequence.current
    setIntruderTabs((prev) => [...prev, { ...newIntruderTab(id), ...seed, id, results: [] }])
    setActiveIntruderTab(id)
    setView('Intruder')
  }
  function toIntruder(detail: Detail) {
    if (detail.truncated || detail.binary) {
      setError('Binary or truncated previews cannot be sent to Intruder as text.')
      return
    }
    addIntruderTab({
      name: detail.host,
      url: `${detail.scheme}://${detail.host}:${detail.port}`,
      request: detail.request,
    })
  }
  // The shortcuts below only read refs and stable setters so the empty-deps
  // keyboard listener always sees the current tab.
  function duplicateRepeaterTab() {
    const current = requestTabRef.current
    if (!current) return
    const id = ++tabSequence.current
    setTabs((prev) => [
      ...prev,
      {
        ...current,
        id,
        name: nextRepeaterCopyName(current.name, prev),
        busy: false,
        result: undefined,
        error: undefined,
        history: [],
        historyIndex: undefined,
      },
    ])
    setActiveTab(id)
    setView('Repeater')
  }
  function duplicateIntruderTab() {
    const current = intruderTabRef.current
    if (!current) return
    const id = ++intruderSequence.current
    setIntruderTabs((prev) => [
      ...prev,
      { ...current, id, name: `${current.name} copy`, results: [] },
    ])
    setActiveIntruderTab(id)
    setView('Intruder')
  }
  function repeaterToIntruder() {
    const current = requestTabRef.current
    if (!current) return
    addIntruderTab({ name: current.name, url: current.url, request: current.request })
  }
  function intruderToRepeater() {
    const current = intruderTabRef.current
    if (!current) return
    const id = ++tabSequence.current
    setTabs((prev) => [
      ...prev,
      { id, name: current.name, url: current.url, request: current.request, busy: false },
    ])
    setActiveTab(id)
    setView('Repeater')
  }
  function updateTab(patch: Partial<RepeaterTab>, id = activeTab) {
    setTabs((prev) => prev.map((t) => (t.id === id ? { ...t, ...patch } : t)))
  }
  function updateIntruderTab(patch: Partial<IntruderTab>, id = activeIntruderTab) {
    setIntruderTabs((prev) => prev.map((t) => (t.id === id ? { ...t, ...patch } : t)))
  }
  async function sendRequestForTab(id: number, run = sendRun.current) {
    const tab = tabs.find((item) => item.id === id)
    if (!tab || tab.busy) return
    updateTab({ busy: true, error: undefined, result: undefined, response: undefined }, tab.id)
    try {
      const result = await api.request<Detail>('repeater.send', {
        url: tab.url,
        request: tab.request,
        verify_tls: verifyTLS,
      })
      if (run === sendRun.current) {
        setTabs((prev) =>
          prev.map((item) => {
            if (item.id !== tab.id) return item
            const history = item.history ?? []
            const index = item.historyIndex ?? history.length - 1
            const nextHistory = [...history.slice(0, index + 1), { request: tab.request, result }]
            return {
              ...item,
              response: result.response,
              result,
              history: nextHistory,
              historyIndex: nextHistory.length - 1,
            }
          }),
        )
      }
    } catch (e) {
      if (run === sendRun.current)
        updateTab({ error: e instanceof Error ? e.message : String(e) }, tab.id)
    } finally {
      if (run === sendRun.current) updateTab({ busy: false }, tab.id)
    }
  }
  async function sendRequest() {
    const tab = requestTab
    if (tab?.busy) return
    await sendRequestForTab(tab.id)
  }
  async function sendGroup(
    tabIds: number[],
    mode: 'sequence-single' | 'sequence-separate' | 'parallel',
  ) {
    const run = ++sendRun.current
    if (mode === 'parallel') {
      await Promise.all(tabIds.map((id) => sendRequestForTab(id, run)))
      return
    }
    for (const id of tabIds) {
      if (run !== sendRun.current) return
      await sendRequestForTab(id, run)
    }
  }
  function cancelRequest() {
    ++sendRun.current
    setTabs((prev) => prev.map((tab) => (tab.busy ? { ...tab, busy: false } : tab)))
  }
  function navigateRepeaterHistory(delta: -1 | 1) {
    const tab = requestTab
    const history = tab.history ?? []
    if (history.length < 2) return
    const currentIndex = tab.historyIndex ?? history.length - 1
    const nextIndex = Math.max(0, Math.min(history.length - 1, currentIndex + delta))
    if (nextIndex === currentIndex) return
    const revision = history[nextIndex]
    updateTab(
      {
        request: revision.request,
        response: revision.result.response,
        result: revision.result,
        historyIndex: nextIndex,
      },
      tab.id,
    )
  }
  function setAttackRequest(value: string) {
    updateIntruderTab({ request: value })
  }
  function setAttackUrl(value: string) {
    updateIntruderTab({ url: value })
  }
  function setPayloads(value: string) {
    updateIntruderTab({ payloads: value })
  }
  function setResults(value: JobResult[]) {
    updateIntruderTab({ results: value })
  }
  async function startIntruder() {
    const tab = intruderTab
    try {
      await api.request('intruder.start', {
        url: tab.url,
        request: tab.request,
        payloads: tab.payloads.split('\n').filter(Boolean),
        verify_tls: verifyTLS,
      })
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
      return
    }
    setIntruderRunningId(tab.id)
    updateIntruderTab({ results: [] }, tab.id)
    setState((s) => ({ ...s, job_state: 'running' }))
  }
  async function toggleProxy() {
    setBusy(true)
    await run(async () =>
      refresh(
        await api.request<EngineState>(state.running ? 'proxy.stop' : 'proxy.start', {
          port,
          verify_tls: verifyTLS,
        }),
      ),
    )
    setBusy(false)
  }
  async function interceptToggle(enabled = !state.intercept, responses = state.responses) {
    await run(async () =>
      refresh(await api.request<EngineState>('proxy.intercept', { enabled, responses })),
    )
  }
  async function resolveIntercept(drop: boolean) {
    if (!pending) return
    setBusy(true)
    await run(async () =>
      refresh(
        await api.request<EngineState>('proxy.resolve', {
          flow_id: pending.flow_id,
          drop,
          ...(interceptText !== interceptOriginal ? { edited_text: interceptText } : {}),
        }),
      ),
    )
    setBusy(false)
  }
  async function resolveAllIntercept(drop: boolean) {
    if (state.pending.length === 0) return
    setBusy(true)
    const waiting = [...state.pending]
    await run(async () => {
      let next = state
      for (const item of waiting) {
        next = await api.request<EngineState>('proxy.resolve', {
          flow_id: item.flow_id,
          drop,
          ...(item.flow_id === pending?.flow_id && interceptText !== interceptOriginal
            ? { edited_text: interceptText }
            : {}),
        })
        refresh(next)
      }
      return next
    })
    setBusy(false)
  }
  function resize(e: React.PointerEvent) {
    const element = e.currentTarget as HTMLElement
    element.setPointerCapture(e.pointerId)
    const move = (event: PointerEvent) => {
      const rect = historyRef.current!.getBoundingClientRect()
      setSplit(Math.min(72, Math.max(25, ((event.clientY - rect.top) / rect.height) * 100)))
    }
    const stop = () => {
      element.removeEventListener('pointermove', move)
      element.removeEventListener('pointerup', stop)
    }
    element.addEventListener('pointermove', move)
    element.addEventListener('pointerup', stop)
  }
  function resizeIntercept(e: React.PointerEvent) {
    const element = e.currentTarget as HTMLElement
    element.setPointerCapture(e.pointerId)
    const move = (event: PointerEvent) => {
      const rect = interceptRef.current!.getBoundingClientRect()
      setInterceptSplit(
        Math.min(78, Math.max(22, ((event.clientY - rect.top) / rect.height) * 100)),
      )
    }
    const stop = () => {
      element.removeEventListener('pointermove', move)
      element.removeEventListener('pointerup', stop)
    }
    element.addEventListener('pointermove', move)
    element.addEventListener('pointerup', stop)
  }

  const trafficStart = Math.max(0, Math.floor(scrollTop / 35) - 5)
  const visibleTraffic = flows.slice(trafficStart, trafficStart + 35)
  const Icon = icons[view]
  return {
    view,
    setView,
    proxyView,
    setProxyView,
    state,
    setState,
    online,
    setOnline,
    connecting,
    setConnecting,
    error,
    setError,
    notice,
    setNotice,
    busy,
    setBusy,
    revision,
    setRevision,
    flows,
    setFlows,
    total,
    setTotal,
    unfilteredTotal,
    query,
    setQuery,
    debouncedQuery,
    setDebouncedQuery,
    filters,
    setFilters,
    debouncedFilters,
    updateFilters,
    resetFilters,
    activeFilterCount,
    showFilters,
    setShowFilters,
    historySort,
    setHistorySort,
    clearHistory,
    page,
    setPage,
    selected,
    setSelected,
    loadingDetail,
    setLoadingDetail,
    selectedId,
    setSelectedId,
    port,
    setPort,
    verifyTLS,
    setVerifyTLS,
    tabs,
    setTabs,
    groups,
    setGroups,
    activeTab,
    setActiveTab,
    tabSequence,
    interceptText,
    setInterceptText,
    interceptOriginal,
    setInterceptOriginal,
    interceptId,
    setInterceptId,
    interceptDetail,
    setInterceptDetail,
    include,
    setInclude,
    exclude,
    setExclude,
    findings,
    setFindings,
    decoderInput,
    setDecoderInput,
    decoderOutput,
    setDecoderOutput,
    operation,
    setOperation,
    attackRequest: intruderTab.request,
    setAttackRequest,
    attackUrl: intruderTab.url,
    setAttackUrl,
    payloads: intruderTab.payloads,
    setPayloads,
    results: intruderTab.results,
    setResults,
    intruderTabs,
    setIntruderTabs,
    activeIntruderTab,
    setActiveIntruderTab,
    intruderSequence,
    intruderTab,
    intruderRunningId,
    updateIntruderTab,
    startIntruder,
    duplicateIntruderTab,
    repeaterToIntruder,
    showHelp,
    setShowHelp,
    theme,
    setTheme,
    searchRef,
    detailSequence,
    scrollRef,
    scrollTop,
    setScrollTop,
    split,
    setSplit,
    interceptSplit,
    setInterceptSplit,
    sessionLoaded,
    setSessionLoaded,
    historyRef,
    interceptRef,
    requestTab,
    pending,
    run,
    refresh,
    trafficStart,
    visibleTraffic,
    Icon,
    selectFlow,
    toRepeater,
    toIntruder,
    updateTab,
    duplicateRepeaterTab,
    intruderToRepeater,
    sendRequest,
    sendGroup,
    cancelRequest,
    navigateRepeaterHistory,
    toggleProxy,
    interceptToggle,
    resolveIntercept,
    resolveAllIntercept,
    resize,
    resizeIntercept,
  }
}
export type WorkspaceController = ReturnType<typeof useWorkspace>

import {
  ArrowLeftRight,
  Code2,
  Crosshair,
  History,
  Send,
  Settings2,
  ShieldCheck,
  Zap,
} from 'lucide-react'
import { useCallback, useEffect, useRef, useState } from 'react'
import { api } from '../api'
import type { Detail, EngineState, Finding, Flow, JobResult } from '../types'

export type View =
  | 'History'
  | 'Intercept'
  | 'Repeater'
  | 'Intruder'
  | 'Scope'
  | 'Live audit'
  | 'Decoder'
  | 'Settings'
export type RepeaterTab = {
  id: number
  name: string
  url: string
  request: string
  result?: Detail
  busy: boolean
  error?: string
}
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
  History,
  Intercept: ArrowLeftRight,
  Repeater: Send,
  Intruder: Zap,
  Scope: Crosshair,
  'Live audit': ShieldCheck,
  Decoder: Code2,
  Settings: Settings2,
}
export const descriptions: Record<View, string> = {
  History: 'Every request. The complete picture.',
  Intercept: 'Pause, inspect, and shape traffic in flight.',
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

export function useWorkspace() {
  const [view, setView] = useState<View>('History')
  const [state, setState] = useState(initial)
  const [online, setOnline] = useState(false)
  const [connecting, setConnecting] = useState(true)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [busy, setBusy] = useState(false)
  const [revision, setRevision] = useState(0)
  const [flows, setFlows] = useState<Flow[]>([])
  const [total, setTotal] = useState(0)
  const [query, setQuery] = useState('')
  const [debouncedQuery, setDebouncedQuery] = useState('')
  const [scopeOnly, setScopeOnly] = useState(false)
  const [bookmarked, setBookmarked] = useState(false)
  const [page, setPage] = useState(0)
  const [selected, setSelected] = useState<Detail | null>(null)
  const [loadingDetail, setLoadingDetail] = useState(false)
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [port, setPort] = useState(8080)
  const [verifyTLS, setVerifyTLS] = useState(true)
  const [tabs, setTabs] = useState<RepeaterTab[]>([newTab(1)])
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
  const [attackRequest, setAttackRequest] = useState(
    'GET /?q=§payload§ HTTP/1.1\r\nHost: example.com\r\n\r\n',
  )
  const [attackUrl, setAttackUrl] = useState('https://example.com')
  const [payloads, setPayloads] = useState('')
  const [results, setResults] = useState<JobResult[]>([])
  const [showHelp, setShowHelp] = useState(false)
  const searchRef = useRef<HTMLInputElement>(null)
  const detailSequence = useRef(0)
  const scrollRef = useRef<HTMLDivElement>(null)
  const [scrollTop, setScrollTop] = useState(0)
  const [split, setSplit] = useState(51)
  const [sessionLoaded, setSessionLoaded] = useState(false)
  const historyRef = useRef<HTMLDivElement>(null)
  // Refs for values accessed by the stable keyboard listener (empty deps array).
  const viewRef = useRef(view)
  viewRef.current = view
  const selectedRef = useRef(selected)
  selectedRef.current = selected
  const interceptDetailRef = useRef(interceptDetail)
  interceptDetailRef.current = interceptDetail
  const requestTab = tabs.find((t) => t.id === activeTab) ?? tabs[0]
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

  useEffect(() => {
    if (!online) return
    let alive = true
    api
      .request<{ tabs?: RepeaterTab[]; port?: number; verifyTLS?: boolean }>('workspace.load')
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
          tabs: tabs.map(({ id, name, url, request }) => ({ id, name, url, request })),
          port,
          verifyTLS,
        }),
      )
    }, 350)
    return () => clearTimeout(timer)
  }, [tabs, port, verifyTLS, sessionLoaded, run])
  useEffect(() => {
    let alive = true
    const unsubscribe = api.onEvent((event) => {
      if (event.type === 'changed') {
        setOnline(true)
        refresh(event.data)
      } else {
        setOnline(false)
        setError(event.message)
      }
    })
    api
      .request<EngineState>('state')
      .then((next) => {
        if (!alive) return
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
    if (!online || view !== 'History') return
    let alive = true
    api
      .request<{ items: Flow[]; total: number }>('history.list', {
        query: debouncedQuery,
        offset: page * 100,
        limit: 100,
        scope: scopeOnly,
        bookmarked,
      })
      .then((result) => {
        if (alive) {
          setFlows(result.items)
          setTotal(result.total)
          if (!result.items.length && page > 0) setPage(0)
        }
      })
      .catch((e) => {
        if (alive) setError(e.message)
      })
    return () => {
      alive = false
    }
  }, [online, revision, view, debouncedQuery, page, scopeOnly, bookmarked])
  useEffect(() => {
    setScrollTop(0)
    if (scrollRef.current) scrollRef.current.scrollTop = 0
  }, [page, debouncedQuery, scopeOnly, bookmarked])
  useEffect(() => {
    if (view !== 'History' || !selectedId) return
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
  }, [revision, selectedId, view])
  useEffect(() => {
    if (view !== 'Intercept' || !pending) {
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
  }, [view, pending?.flow_id, pending?.phase])
  useEffect(() => {
    if (!online) return
    if (view === 'Live audit')
      void run(async () => setFindings(await api.request<Finding[]>('audit.list')))
    if (view === 'Intruder')
      void run(async () =>
        setResults((await api.request<{ items: JobResult[] }>('intruder.results')).items),
      )
  }, [view, online, revision, run])
  useEffect(() => {
    if (!notice) return
    const timer = setTimeout(() => setNotice(''), 3500)
    return () => clearTimeout(timer)
  }, [notice])
  useEffect(() => {
    const listener = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault()
        setView('History')
        setTimeout(() => searchRef.current?.focus(), 0)
      }
      if ((e.ctrlKey || e.metaKey) && ['1', '2', '3', '4'].includes(e.key)) {
        e.preventDefault()
        setView((['History', 'Intercept', 'Repeater', 'Intruder'] as View[])[Number(e.key) - 1])
      }
      // Ctrl+R -> Send to Repeater, Ctrl+I -> Send to Intruder.
      // Uses the selected detail from History or the intercepted flow detail.
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'r' && !e.shiftKey) {
        e.preventDefault()
        const detail = viewRef.current === 'Intercept'
          ? interceptDetailRef.current
          : selectedRef.current
        if (detail) toRepeater(detail)
      }
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'i' && !e.shiftKey) {
        e.preventDefault()
        const detail = viewRef.current === 'Intercept'
          ? interceptDetailRef.current
          : selectedRef.current
        if (detail) toIntruder(detail)
      }
      if (e.key === 'Escape') {
        setShowHelp(false)
        setError('')
      }
    }
    window.addEventListener('keydown', listener)
    return () => window.removeEventListener('keydown', listener)
  }, [])

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
  function toIntruder(detail: Detail) {
    if (detail.truncated || detail.binary) {
      setError(
        'Binary or truncated previews cannot be sent to Intruder as text.',
      )
      return
    }
    setAttackUrl(`${detail.scheme}://${detail.host}:${detail.port}`)
    setAttackRequest(detail.request)
    setView('Intruder')
  }
  function updateTab(patch: Partial<RepeaterTab>, id = activeTab) {
    setTabs((prev) => prev.map((t) => (t.id === id ? { ...t, ...patch } : t)))
  }
  async function sendRequest() {
    const tab = requestTab
    if (tab.busy) return
    updateTab({ busy: true, error: undefined, result: undefined }, tab.id)
    try {
      updateTab(
        {
          result: await api.request<Detail>('repeater.send', {
            url: tab.url,
            request: tab.request,
            verify_tls: verifyTLS,
          }),
        },
        tab.id,
      )
    } catch (e) {
      updateTab({ error: e instanceof Error ? e.message : String(e) }, tab.id)
    } finally {
      updateTab({ busy: false }, tab.id)
    }
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

  const trafficStart = Math.max(0, Math.floor(scrollTop / 35) - 5)
  const visibleTraffic = flows.slice(trafficStart, trafficStart + 35)
  const Icon = icons[view]
  return {
    view,
    setView,
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
    query,
    setQuery,
    debouncedQuery,
    setDebouncedQuery,
    scopeOnly,
    setScopeOnly,
    bookmarked,
    setBookmarked,
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
    attackRequest,
    setAttackRequest,
    attackUrl,
    setAttackUrl,
    payloads,
    setPayloads,
    results,
    setResults,
    showHelp,
    setShowHelp,
    searchRef,
    detailSequence,
    scrollRef,
    scrollTop,
    setScrollTop,
    split,
    setSplit,
    sessionLoaded,
    setSessionLoaded,
    historyRef,
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
    sendRequest,
    toggleProxy,
    interceptToggle,
    resolveIntercept,
    resize,
  }
}
export type WorkspaceController = ReturnType<typeof useWorkspace>

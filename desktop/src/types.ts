export type Flow = {
  id: number
  flow_id: string
  method: string
  scheme: string
  host: string
  port: number
  path: string
  url: string
  status_code: number | null
  content_type: string
  response_body_size: number
  duration_ms: number | null
  started_at: number
  scope: boolean
  bookmarked: boolean
  notes: string
  tool: string
}
export type Detail = Flow & {
  request: string
  response: string
  truncated: boolean
  binary: boolean
}
export type Pending = Flow & { phase: 'request' | 'response' }
export type EngineState = {
  protocol: number
  running: boolean
  port: number
  host: string
  intercept: boolean
  responses: boolean
  pending: Pending[]
  audit: boolean
  findings: number
  dropped: number
  queue_depth: number
  error: string
  data_dir: string
  scope: { include: string[]; exclude: string[] }
  job_state: string
}
export type Finding = {
  id: string
  flow_id: string
  title: string
  severity: string
  detail: string
  remediation: string
  url: string
  evidence: { location: string; text: string }[]
}
export type JobResult = {
  index: number
  // Combined payloads joined for display (e.g. "admin | 42"); `payloads` holds
  // the individual per-position values.
  payload: string
  payloads?: string[]
  flow_id?: string
  status_code?: number
  duration_ms?: number
  response_body_size?: number
  error?: string
}
export type OastDomain = {
  id: number
  domain: string
  created_at: number
  hits: number
}
export type OastStatus = {
  active: boolean
  server: string
  domains: OastDomain[]
  interaction_count: number
  poll_interval: number
  last_poll: number | null
  error: string
}
export type OastInteraction = {
  protocol: string
  unique_id: string
  full_id: string
  remote_address: string
  timestamp: string
  q_type: string | null
  raw_request: string | null
  raw_response: string | null
  smtp_from: string | null
  received_at: number
}
export type EngineEvent =
  { type: 'changed'; data: EngineState } | { type: 'ready'; data: EngineState } | { type: 'offline'; message: string }
export type WorkspaceSession = {
  id: string
  name: string
  created_at: string
  updated_at: string
  protected?: boolean
}
export type BrowserInfo = { id: number; name: string; kind: 'firefox' | 'chromium' }
export interface DesktopBridge {
  request<T = unknown>(method: string, params?: Record<string, unknown>): Promise<T>
  onEvent(callback: (event: EngineEvent) => void): () => void
  exportCertificate(): Promise<boolean>
  listBrowsers(): Promise<BrowserInfo[]>
  openBrowser(id: number): Promise<{ name: string; trust_method: string }>
  copyText(text: string): Promise<unknown>
  window(action: 'minimize' | 'maximize' | 'close'): void
  listSessions(): Promise<WorkspaceSession[]>
  createSession(name: string): Promise<WorkspaceSession>
  deleteSession(id: string): Promise<boolean>
  openSession(id: string): Promise<WorkspaceSession>
  onAppCloseRequest(callback: () => void): () => void
  onSessionOpened(callback: (session: WorkspaceSession) => void): () => void
  closeDecision(decision: 'save' | 'discard' | 'cancel'): Promise<void>
}
declare global {
  interface Window {
    bidoytu?: DesktopBridge
  }
}

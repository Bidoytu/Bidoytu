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
  payload: string
  flow_id?: string
  status_code?: number
  duration_ms?: number
  response_body_size?: number
  error?: string
}
export type EngineEvent =
  { type: 'changed'; data: EngineState } | { type: 'offline'; message: string }
export interface DesktopBridge {
  request<T = unknown>(method: string, params?: Record<string, unknown>): Promise<T>
  onEvent(callback: (event: EngineEvent) => void): () => void
  exportCertificate(): Promise<boolean>
  copyText(text: string): Promise<unknown>
  window(action: 'minimize' | 'maximize' | 'close'): void
}
declare global {
  interface Window {
    bidoytu?: DesktopBridge
  }
}

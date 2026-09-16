import type { DesktopBridge } from './types'

export const api: DesktopBridge = window.bidoytu ?? {
  request: async () => {
    throw new Error('Open the desktop application with npm run dev to connect the Python engine.')
  },
  onEvent: () => () => {},
  exportCertificate: async () => false,
  listBrowsers: async () => [],
  openBrowser: async () => {
    throw new Error('Desktop browser integration is unavailable.')
  },
  copyText: (text) => navigator.clipboard.writeText(text),
  window: () => {},
  listSessions: async () => [],
  createSession: async () => { throw new Error('Session management is unavailable.') },
  deleteSession: async () => false,
  openSession: async () => { throw new Error('Session management is unavailable.') },
  onAppCloseRequest: () => () => {},
  onSessionOpened: () => () => {},
  closeDecision: async () => {},
}

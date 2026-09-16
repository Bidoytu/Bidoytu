import type { DesktopBridge } from './types'

export const api: DesktopBridge = window.bidoytu ?? {
  request: async () => {
    throw new Error('Open the desktop application with npm run dev to connect the Python engine.')
  },
  onEvent: () => () => {},
  exportCertificate: async () => false,
  copyText: (text) => navigator.clipboard.writeText(text),
  window: () => {},
}

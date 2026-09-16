import {
  ArrowDownToLine,
  ArrowLeftRight,
  Folder,
  Layers3,
  SlidersHorizontal,
  Terminal,
} from 'lucide-react'
import { api } from '../api'
import { Button, Toggle } from '../components'

import type { WorkspaceController } from '../hooks/useWorkspace'

export function SettingsView({ workspace }: { workspace: WorkspaceController }) {
  const { state, online, setNotice, port, setPort, verifyTLS, setVerifyTLS, run, theme, setTheme } =
    workspace
  return (
    <div className="settings-workspace">
      <section className="settings-card">
        <h2>
          <SlidersHorizontal size={18} />
          Network engine
        </h2>
        <div className="setting-row">
          <div>
            <strong>Proxy listener</strong>
            <p>Loopback interface · HTTP/HTTPS · HTTP/2 enabled</p>
          </div>
          <label className="port-field">
            <span>127.0.0.1 :</span>
            <input
              type="number"
              min={1024}
              max={65535}
              disabled={state.running}
              value={port}
              aria-label="Proxy port"
              onChange={(e) => setPort(Number(e.target.value))}
            />
          </label>
        </div>
        <div className="setting-row">
          <div>
            <strong>Verify upstream TLS certificates</strong>
            <p>Used for replay and the next proxy start.</p>
          </div>
          <Toggle
            label="Verify upstream TLS certificates"
            enabled={verifyTLS}
            onChange={() => setVerifyTLS((v) => !v)}
          />
        </div>
        <div className="setting-row">
          <div>
            <strong>HTTPS interception certificate</strong>
            <p>Export the public CA and trust it in your testing browser.</p>
          </div>
          <Button
            disabled={!online}
            onClick={() =>
              void run(async () => {
                if (await api.exportCertificate()) setNotice('Public CA certificate exported.')
              })
            }
          >
            <ArrowDownToLine size={14} />
            Export public CA
          </Button>
        </div>
      </section>
      <section className="settings-card">
        <h2>
          <Folder size={18} />
          Workspace storage
        </h2>
        <div className="setting-row">
          <div>
            <strong>Active session</strong>
            <p className="mono">{state.data_dir || 'Waiting for Python engine…'}</p>
          </div>
          <span className="count-chip">SQLite · WAL</span>
        </div>
        <div className="setting-row">
          <div>
            <strong>Capture health</strong>
            <p>Bounded storage queue with visible overload reporting.</p>
          </div>
          <span className="mono">
            {state.queue_depth} queued / {state.dropped} dropped
          </span>
        </div>
        <div className="setting-row">
          <div>
            <strong>Dark mode</strong>
            <p>Invert the workspace to a dark canvas. Saved on this device.</p>
          </div>
          <Toggle
            label="Dark mode"
            enabled={theme === 'dark'}
            onChange={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
          />
        </div>
      </section>
      <div className="architecture-card">
        <div>
          <Terminal size={21} />
          <strong>Python</strong>
          <span>Async networking · mitmproxy · SQLite</span>
        </div>
        <div className="architecture-pipe">
          <ArrowLeftRight size={20} />
          <span>Private IPC</span>
        </div>
        <div>
          <Layers3 size={21} />
          <strong>Electron</strong>
          <span>React · TypeScript · sandboxed renderer</span>
        </div>
      </div>
    </div>
  )
}

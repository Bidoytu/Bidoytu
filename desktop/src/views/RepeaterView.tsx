import { Globe2, LoaderCircle, Plus, Send, X, Zap } from 'lucide-react'
import { Button, Editor, bytes, duration } from '../components'

import type { WorkspaceController } from '../hooks/useWorkspace'
import { newTab } from '../hooks/useWorkspace'

export function RepeaterView({ workspace }: { workspace: WorkspaceController }) {
  const {
    setView,
    online,
    error,
    busy,
    tabs,
    setTabs,
    activeTab,
    setActiveTab,
    tabSequence,
    setAttackRequest,
    setAttackUrl,
    split,
    requestTab,
    updateTab,
    sendRequest,
  } = workspace
  return (
    <div
      className="tool-workspace"
      onKeyDown={(e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
          e.preventDefault()
          void sendRequest()
        }
      }}
    >
      <div className="request-tabs">
        {tabs.map((tab) => (
          <div className={`request-tab ${tab.id === activeTab ? 'active' : ''}`} key={tab.id}>
            <button onClick={() => setActiveTab(tab.id)}>
              {tab.busy ? <LoaderCircle size={13} className="spin" /> : <Send size={12} />}
              <span>{tab.name}</span>
            </button>
            {tabs.length > 1 && (
              <button
                aria-label={`Close ${tab.name}`}
                disabled={tab.busy}
                onClick={() => {
                  setTabs(tabs.filter((t) => t.id !== tab.id))
                  if (tab.id === activeTab) setActiveTab(tabs.find((t) => t.id !== tab.id)!.id)
                }}
              >
                <X size={12} />
              </button>
            )}
          </div>
        ))}
        <button
          className="icon-button"
          aria-label="New Repeater request"
          onClick={() => {
            const id = ++tabSequence.current
            setTabs((prev) => [...prev, newTab(id)])
            setActiveTab(id)
          }}
        >
          <Plus size={16} />
        </button>
      </div>
      <div className="tool-toolbar">
        <label className="target-input">
          <Globe2 size={15} />
          <input
            aria-label="Repeater target URL"
            value={requestTab.url}
            disabled={requestTab.busy}
            onChange={(e) => updateTab({ url: e.target.value })}
          />
        </label>
        <Button
          className="primary"
          disabled={!online || requestTab.busy}
          onClick={() => void sendRequest()}
        >
          {requestTab.busy ? <LoaderCircle size={14} className="spin" /> : <Send size={14} />}{' '}
          {requestTab.busy ? 'Sending…' : 'Send'}
          <kbd>Ctrl ↵</kbd>
        </Button>
        <Button
          className="subtle"
          onClick={() => {
            setAttackUrl(requestTab.url)
            setAttackRequest(requestTab.request)
            setView('Intruder')
          }}
        >
          <Zap size={14} />
          To Intruder
        </Button>
      </div>
      {requestTab.error && <div className="error-banner">{requestTab.error}</div>}
      <div className="editor-split full">
        <Editor
          title="Request"
          value={requestTab.request}
          onChange={(value) => updateTab({ request: value })}
          disabled={requestTab.busy}
        />
        <Editor
          title="Response"
          value={requestTab.result?.response ?? ''}
          hint={
            requestTab.result
              ? `${requestTab.result.status_code} · ${duration(requestTab.result.duration_ms)} · ${bytes(requestTab.result.response_body_size)}${requestTab.result.truncated ? ' · truncated' : ''}`
              : undefined
          }
        />
      </div>
    </div>
  )
}

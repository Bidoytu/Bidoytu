import {
  ChevronDown,
  ChevronRight,
  Copy,
  FolderPlus,
  Globe2,
  LoaderCircle,
  Plus,
  Send,
  X,
  Zap,
} from 'lucide-react'
import { useMemo, useState } from 'react'
import { Button, Editor, bytes, duration } from '../components'
import type { RepeaterGroup, WorkspaceController } from '../hooks/useWorkspace'
import { newTab } from '../hooks/useWorkspace'

const GROUP_COLORS = ['#d48a3a', '#6aa9e9', '#b67be8', '#5fbf91', '#e06b78', '#d7c45f']
type GroupSendMode = 'current' | 'sequence-single' | 'sequence-separate' | 'parallel'

export function RepeaterView({ workspace }: { workspace: WorkspaceController }) {
  const {
    online,
    tabs,
    setTabs,
    groups,
    setGroups,
    activeTab,
    setActiveTab,
    tabSequence,
    requestTab,
    updateTab,
    duplicateRepeaterTab,
    repeaterToIntruder,
    sendRequest,
    sendGroup,
    cancelRequest,
    navigateRepeaterHistory,
  } = workspace
  const [menu, setMenu] = useState<{
    x: number
    y: number
    tabId?: number
    groupName?: string
  } | null>(null)
  const [groupDialog, setGroupDialog] = useState<number | null>(null)
  const [sendMenuOpen, setSendMenuOpen] = useState(false)
  const [groupSendMode, setGroupSendMode] = useState<GroupSendMode>('current')
  const groupedIds = useMemo(() => new Set(groups.flatMap((group) => group.tabIds)), [groups])
  const orderedGroups = groups.map((group) => ({
    ...group,
    tabIds: group.tabIds.filter((id) => tabs.some((tab) => tab.id === id)),
  }))
  const ungrouped = tabs.filter((tab) => !groupedIds.has(tab.id))
  const activeGroup = groups.find((group) => group.tabIds.includes(activeTab))
  const groupBusy = Boolean(
    activeGroup?.tabIds.some((id) => tabs.find((tab) => tab.id === id)?.busy),
  )
  const requestHistory = requestTab.history ?? []
  const historyIndex = requestTab.historyIndex ?? requestHistory.length - 1

  function renderTab(tab: (typeof tabs)[number]) {
    return (
      <div className={`request-tab ${tab.id === activeTab ? 'active' : ''}`} key={tab.id}>
        <button
          onClick={() => setActiveTab(tab.id)}
          onContextMenu={(e) => {
            e.preventDefault()
            setMenu({ x: e.clientX, y: e.clientY, tabId: tab.id })
          }}
        >
          {tab.busy ? <LoaderCircle size={13} className="spin" /> : <Send size={12} />}
          <span>{tab.name}</span>
        </button>
        {tabs.length > 1 && (
          <button
            aria-label={`Close ${tab.name}`}
            disabled={tab.busy}
            onClick={() => {
              setTabs((prev) => prev.filter((item) => item.id !== tab.id))
              setGroups((prev) =>
                prev
                  .map((group) => ({
                    ...group,
                    tabIds: group.tabIds.filter((id) => id !== tab.id),
                  }))
                  .filter((group) => group.tabIds.length),
              )
              if (tab.id === activeTab) setActiveTab(tabs.find((item) => item.id !== tab.id)!.id)
            }}
          >
            <X size={12} />
          </button>
        )}
      </div>
    )
  }
  function createTab() {
    const id = ++tabSequence.current
    setTabs((prev) => [...prev, newTab(id)])
    setActiveTab(id)
  }
  function toggleGroup(name: string) {
    setGroups((prev) =>
      prev.map((group) =>
        group.name === name ? { ...group, collapsed: !group.collapsed } : group,
      ),
    )
  }
  function sendSelected() {
    if (activeGroup && groupSendMode !== 'current')
      void sendGroup(activeGroup.tabIds, groupSendMode)
    else void sendRequest()
  }

  return (
    <div
      className="tool-workspace repeater-workspace"
      onClick={() => menu && setMenu(null)}
      onKeyDown={(e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
          e.preventDefault()
          void sendRequest()
        }
      }}
    >
      <div className="request-tabs">
        {orderedGroups.map((group) => (
          <div className="request-group" key={group.name}>
            <button
              className="request-group-header"
              style={{ '--group-color': group.color } as React.CSSProperties}
              onClick={(e) => {
                e.stopPropagation()
                toggleGroup(group.name)
              }}
              onContextMenu={(e) => {
                e.preventDefault()
                e.stopPropagation()
                setMenu({ x: e.clientX, y: e.clientY, groupName: group.name })
              }}
            >
              {group.collapsed ? <ChevronRight size={13} /> : <ChevronDown size={13} />}
              <span>{group.name}</span>
              <small>{group.tabIds.length}</small>
            </button>
            {!group.collapsed &&
              group.tabIds.map((id) => {
                const tab = tabs.find((item) => item.id === id)
                return tab ? renderTab(tab) : null
              })}
          </div>
        ))}
        {ungrouped.map(renderTab)}
        <button
          className="icon-button"
          aria-label="New Repeater request"
          onClick={(e) => {
            e.stopPropagation()
            createTab()
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
        <div className="send-control">
          <Button className="primary" disabled={!online || requestTab.busy} onClick={sendSelected}>
            {requestTab.busy ? <LoaderCircle size={14} className="spin" /> : <Send size={14} />}{' '}
            {requestTab.busy ? 'Sending…' : 'Send'} <kbd>Ctrl ↵</kbd>
          </Button>
          {activeGroup && (
            <button
              className="send-menu-toggle"
              aria-label="Group send options"
              onClick={() => setSendMenuOpen((open) => !open)}
            >
              <ChevronDown size={15} />
            </button>
          )}
          {sendMenuOpen && activeGroup && (
            <div className="group-send-menu" onClick={(e) => e.stopPropagation()}>
              <div className="group-send-title">
                <strong>?</strong>
                <span>Group send options</span>
              </div>
              <button
                className={groupSendMode === 'current' ? 'selected' : ''}
                onClick={() => {
                  setSendMenuOpen(false)
                  setGroupSendMode('current')
                }}
              >
                ✓ <span>Send (current tab)</span>
                <kbd>Ctrl+Space</kbd>
              </button>
              <button
                className={groupSendMode === 'sequence-single' ? 'selected' : ''}
                onClick={() => {
                  setSendMenuOpen(false)
                  setGroupSendMode('sequence-single')
                }}
              >
                <span>Send group in sequence</span>
                <small>(single connection)</small>
              </button>
              <button
                className={groupSendMode === 'sequence-separate' ? 'selected' : ''}
                onClick={() => {
                  setSendMenuOpen(false)
                  setGroupSendMode('sequence-separate')
                }}
              >
                <span>Send group in sequence</span>
                <small>(separate connections)</small>
              </button>
              <button
                className={groupSendMode === 'parallel' ? 'selected' : ''}
                onClick={() => {
                  setSendMenuOpen(false)
                  setGroupSendMode('parallel')
                }}
              >
                <span>Send group in parallel</span>
              </button>
            </div>
          )}
        </div>
        {(requestTab.busy || groupBusy) && (
          <Button className="subtle cancel-request" onClick={cancelRequest}>
            Cancel
          </Button>
        )}
        <div className="request-navigation" aria-label="Navigate request tabs">
          <span className="request-history-count">
            {requestHistory.length ? `${historyIndex + 1}/${requestHistory.length}` : '0/0'}
          </span>
          <button
            disabled={historyIndex <= 0}
            aria-label="Previous request"
            onClick={() => navigateRepeaterHistory(-1)}
          >
            ‹
          </button>
          <button
            disabled={historyIndex < 0 || historyIndex >= requestHistory.length - 1}
            aria-label="Next request"
            onClick={() => navigateRepeaterHistory(1)}
          >
            ›
          </button>
        </div>
        <Button
          className="subtle"
          title="Duplicate request (Ctrl+R)"
          onClick={duplicateRepeaterTab}
        >
          <Copy size={14} /> Duplicate
        </Button>
        <Button className="subtle" title="Send to Intruder (Ctrl+I)" onClick={repeaterToIntruder}>
          <Zap size={14} /> To Intruder
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
      {menu && (
        <div
          className="repeater-context-menu"
          style={{ left: menu.x, top: menu.y }}
          onClick={(e) => e.stopPropagation()}
        >
          {menu.groupName && (
            <>
              <button
                onClick={() => {
                  setGroups((prev) => prev.filter((group) => group.name !== menu.groupName))
                  setMenu(null)
                }}
              >
                Delete group
              </button>
              <button
                className="danger-item"
                onClick={() => {
                  const group = groups.find((item) => item.name === menu.groupName)
                  if (
                    !group ||
                    !window.confirm(`Delete group and its ${group.tabIds.length} request tabs?`)
                  )
                    return
                  const removed = new Set(group.tabIds)
                  const remaining = tabs.filter((tab) => !removed.has(tab.id))
                  const fallback = remaining[0] ?? newTab(++tabSequence.current)
                  setTabs(remaining.length ? remaining : [fallback])
                  setGroups((prev) => prev.filter((item) => item.name !== group.name))
                  if (removed.has(activeTab)) setActiveTab(fallback.id)
                  setMenu(null)
                }}
              >
                Delete group and tabs
              </button>
            </>
          )}
          <button
            style={{ display: menu.tabId === undefined ? 'none' : undefined }}
            onClick={() => {
              if (menu.tabId !== undefined) setGroupDialog(menu.tabId)
              setMenu(null)
            }}
          >
            <FolderPlus size={14} /> Add to group…
          </button>
        </div>
      )}
      {groupDialog !== null && (
        <GroupModal
          tabId={groupDialog}
          tabs={tabs}
          groups={groups}
          onCancel={() => setGroupDialog(null)}
          onSave={(group) => {
            setGroups((prev) => {
              const selected = new Set(group.tabIds)
              const cleaned = prev
                .filter((item) => item.name !== group.name)
                .map((item) => ({ ...item, tabIds: item.tabIds.filter((id) => !selected.has(id)) }))
                .filter((item) => item.tabIds.length)
              return [...cleaned, group]
            })
            setGroupDialog(null)
          }}
        />
      )}
    </div>
  )
}

function GroupModal({
  tabId,
  tabs,
  groups,
  onCancel,
  onSave,
}: {
  tabId: number
  tabs: WorkspaceController['tabs']
  groups: RepeaterGroup[]
  onCancel: () => void
  onSave: (group: RepeaterGroup) => void
}) {
  const existing = groups.find((group) => group.tabIds.includes(tabId))
  const [name, setName] = useState(existing?.name ?? '')
  const [color, setColor] = useState(
    existing?.color ?? GROUP_COLORS[groups.length % GROUP_COLORS.length],
  )
  const [selected, setSelected] = useState<number[]>(existing?.tabIds ?? [tabId])
  const allSelected = selected.length === tabs.length
  function save() {
    const cleanName = name.trim()
    if (cleanName && selected.length)
      onSave({ name: cleanName, color, tabIds: selected, collapsed: existing?.collapsed ?? false })
  }
  return (
    <div className="modal-backdrop" onMouseDown={onCancel}>
      <div className="group-modal" onMouseDown={(e) => e.stopPropagation()}>
        <div className="modal-title">
          <div>
            <strong>Add requests to group</strong>
            <span>Select request tabs and choose a group color.</span>
          </div>
          <button onClick={onCancel}>
            <X size={16} />
          </button>
        </div>
        <label className="modal-field">
          <span>
            Group name <em>required</em>
          </span>
          <input
            autoFocus
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g. Authentication flow"
          />
        </label>
        <div className="modal-field">
          <span>Request tabs</span>
          <button
            className="select-all"
            onClick={() => setSelected(allSelected ? [] : tabs.map((tab) => tab.id))}
          >
            {allSelected ? 'Clear all' : 'Select all'}
          </button>
        </div>
        <div className="group-tab-list">
          {tabs.map((tab) => (
            <label key={tab.id}>
              <input
                type="checkbox"
                checked={selected.includes(tab.id)}
                onChange={() =>
                  setSelected((prev) =>
                    prev.includes(tab.id) ? prev.filter((id) => id !== tab.id) : [...prev, tab.id],
                  )
                }
              />
              <span>{tab.name}</span>
              <small>{tabHost(tab.url)}</small>
            </label>
          ))}
        </div>
        <div className="modal-field">
          <span>Group color</span>
          <div className="color-picker">
            {GROUP_COLORS.map((item) => (
              <button
                key={item}
                className={color === item ? 'selected' : ''}
                style={{ background: item }}
                aria-label={`Use ${item}`}
                onClick={() => setColor(item)}
              />
            ))}
          </div>
        </div>
        <div className="modal-actions">
          <Button className="subtle" onClick={onCancel}>
            Cancel
          </Button>
          <Button
            className="primary"
            disabled={!name.trim() || selected.length === 0}
            onClick={save}
          >
            Add to group
          </Button>
        </div>
      </div>
    </div>
  )
}

function tabHost(url: string) {
  try {
    return new URL(url).host || url
  } catch {
    return url || '—'
  }
}

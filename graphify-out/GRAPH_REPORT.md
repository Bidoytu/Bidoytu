# Graph Report - Bidoytu  (2026-09-15)

## Corpus Check
- 75 files · ~141,909 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 6 file(s) not represented in the graph (top: (none) 4, .spec 1, .ico 1)

## Summary
- 1394 nodes · 2635 edges · 89 communities (72 shown, 16 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 191 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `be419317`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- theme.py
- InterceptView
- MessageView
- CollaboratorTab
- HistoryView
- AppConfig
- IntruderSession
- InterceptActivityModel
- attack.py
- InteractshClient
- RepeaterSession
- IntruderResultsModel
- ProxyEngine
- CaptureAddon
- MainWindow
- FlowRepository
- What You Must Do When Invoked
- ProxyTab
- intruder_session.py
- FindBar
- collaborator_tab.py
- repeater_session.py
- body_format.py
- PayloadSetEditor
- InteractionsModel
- IntruderTab
- FlowRecord
- FlowTableModel
- smoke_test.py
- ._send
- FlowLayout
- AsyncHttpSender
- main_window.py
- QMenu
- AttackRunner
- GroupDialog
- iter_jobs
- _Chip
- RepeaterTab
- Storage Layer (storage/)
- CaCertDialog
- .restore_state
- intercept_response_live_test.py
- repeater_tab.py
- WorkspaceDialog
- intercept_live_test.py
- InteractionFilterProxy
- ResultFilterProxy
- graphify reference: extra exports and benchmark
- SendHandle
- Bidoytu
- attack_runner.py
- .closeEvent
- CLAUDE.md
- UI Layer (ui/)
- Building and releasing Bidoytu
- _GroupHeaderChip
- ProxyEngine (QThread)
- Security Policy
- .mousePressEvent
- Public CA Certificate Export
- Release CI/CD Workflow
- proxy_live_test.py
- WorkspaceManager
- WrappingTabBar
- Contributing to Bidoytu
- ui/__init__.py
- wrap_selection
- bidoytu
- ._update_group_send_menu
- httpx Async Client
- AGENTS.md
- Display vs. Wire Invariant
- graphify reference: query, path, explain
- Contributors Acknowledgement
- start_proxy_repro.py
- http_utils Raw HTTP Parsing
- Private Vulnerability Reporting
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native CLAUDE.md integration
- graphify reference: incremental update and cluster-only
- graphify reference: GitHub clone and cross-repo merge
- graphify reference: transcribe video and audio
- strip_markers
- extraction-spec.md
- wrapping_tab_bar.py
- config.py
- CONTRIBUTORS.md

## God Nodes (most connected - your core abstractions)
1. `FlowRecord` - 83 edges
2. `RepeaterSession` - 65 edges
3. `IntruderSession` - 60 edges
4. `MainWindow` - 50 edges
5. `CollaboratorTab` - 50 edges
6. `MessageView` - 45 edges
7. `InterceptView` - 41 edges
8. `RepeaterTab` - 41 edges
9. `AsyncHttpSender` - 34 edges
10. `InterceptActivityModel` - 29 edges

## Surprising Connections (you probably didn't know these)
- `Bundled App Icon Asset` --conceptually_related_to--> `UI Layer (ui/)`  [INFERRED]
  src/bidoytu/assets/logo.png → README.md
- `Bidoytu` --references--> `Bidoytu Banner Logo`  [EXTRACTED]
  README.md → bidoytu-long.png
- `Bidoytu` --references--> `Bidoytu Circular Icon Logo`  [INFERRED]
  README.md → logo.png
- `Bidoytu Banner Logo` --semantically_similar_to--> `Bidoytu Circular Icon Logo`  [INFERRED] [semantically similar]
  bidoytu-long.png → logo.png
- `Bidoytu Circular Icon Logo` --semantically_similar_to--> `Bundled App Icon Asset`  [INFERRED] [semantically similar]
  logo.png → src/bidoytu/assets/logo.png

## Import Cycles
- None detected.

## Communities (89 total, 16 thin omitted)

### Community 0 - "theme.py"
Cohesion: 0.08
Nodes (39): QColor, QPalette, QPixmap, QProxyStyle, QStyledItemDelegate, HistoryItemDelegate, Item delegate for the HTTP history table. This delegate paints every cell…, A soft, muted tint of the accent used to fill the selected row. Uses the shared… (+31 more)

### Community 1 - "InterceptView"
Cohesion: 0.07
Nodes (22): build_response_text(), Assemble a raw HTTP response string from parts., InterceptView, QWidget, Size the activity table so URL fills the leftover width, while every column…, Whenever a column is resized, compensate its immediate right neighbor (or left…, Reflow the URL column to absorb the viewport's leftover width. URL is the…, Forward every still-pending flow, then reset the panel. Called when… (+14 more)

### Community 2 - "MessageView"
Cohesion: 0.05
Nodes (27): QSyntaxHighlighter, QTextCharFormat, _fmt(), HttpHighlighter, Lightweight syntax highlighting for raw HTTP messages. Uses…, Highlights HTTP start-lines and headers., Re-color for a new theme mode and re-highlight the document., MarkerHighlighter (+19 more)

### Community 3 - "CollaboratorTab"
Cohesion: 0.09
Nodes (10): CollaboratorTab, QWidget, Slot, Build a titled pane (label + find bar + view), matching Repeater., Best-effort correlate an interaction back to a generated payload., Render a raw HTTP message, pretty-printing its body by content-type. Splits…, Attach a note (e.g. the target tab) to the most recent payload., Generate a payload, tag it with ``note``, and return the hostname. Used by… (+2 more)

### Community 4 - "HistoryView"
Cohesion: 0.10
Nodes (10): DetailView, QWidget, Two MessageViews (request | response) with a shared soft-wrap toggle., HistoryView, QWidget, Slot, Whenever a column is resized, compensate its immediate right neighbor (or left…, Reflow the Path column to absorb the viewport's leftover width. Path is the… (+2 more)

### Community 5 - "AppConfig"
Cohesion: 0.11
Nodes (13): AppConfig, Path, Top-level runtime configuration. Attributes: data_dir: Root directory for all…, JSON file holding persisted Repeater sessions across restarts., JSON file holding the last Intruder attack config across restarts., JSON file holding the Target scope for this workspace., JSON file holding Collaborator session state across restarts. Stores the active…, Directory where mitmproxy stores its generated CA and certs. We keep it under… (+5 more)

### Community 6 - "IntruderSession"
Cohesion: 0.08
Nodes (8): IntruderSession, QWidget, Slot, Grow/shrink the payload-set tabs to exactly ``n`` (min 1)., Return a JSON-serializable snapshot of this session., Restore this session from a snapshot produced by :meth:`to_state`., Build a FlowRecord from the template (payload markers removed)., One Intruder attack: template + positions + payload sets + results.

### Community 7 - "InterceptActivityModel"
Cohesion: 0.08
Nodes (14): ActivityRow, InterceptActivityModel, Orientation, QAbstractTableModel, QModelIndex, Log a paused (pending) request. Returns its row index., Log a paused (pending) response. Returns its row index., True if the row is a still-pending request or response. (+6 more)

### Community 8 - "attack.py"
Cohesion: 0.16
Nodes (20): PayloadSet, Intruder attack model: markers, attack types, and request building. Qt-free so…, A generator plus its processing rules (one Intruder payload set)., _apply_one(), apply_rules(), _brute(), build_generator(), describe_rule() (+12 more)

### Community 9 - "InteractshClient"
Cohesion: 0.10
Nodes (13): Exception, InteractshClient, _cb(), _cb(), InteractshError, Raised for registration / polling / crypto failures., Register with, generate payloads for, and poll an Interactsh server. The client…, Generate a keypair and register against the first working server. ``servers``… (+5 more)

### Community 10 - "RepeaterSession"
Cohesion: 0.16
Nodes (6): QHBoxLayout, QWidget, True if this is a pristine session: no request text and no history., Paint the Send button with the disabled cue when it has no request. Uses a…, One request/response pane with full Repeater controls., RepeaterSession

### Community 11 - "IntruderResultsModel"
Cohesion: 0.18
Nodes (7): One completed request in the results table., ResultRow, IntruderResultsModel, QAbstractTableModel, QModelIndex, Table model + filter proxy for Intruder attack results.…, status_color()

### Community 12 - "ProxyEngine"
Cohesion: 0.08
Nodes (11): QThread, ProxyEngine, Update target scope immediately, including while the proxy runs., Toggle the global 'intercept responses' behavior., Arm a one-shot response intercept for a single flow., Forward a paused request, optionally with edited raw request text., Drop a paused request., Forward a paused response, optionally with edited raw response text. (+3 more)

### Community 13 - "CaptureAddon"
Cohesion: 0.10
Nodes (15): FlowCallback, HTTPFlow, InterceptCallback, CaptureAddon, _PendingFlow, Arm a one-shot response intercept for a single flow (Burp's "Response to this…, Apply a UI decision to a paused request. Runs on the proxy loop., Apply a UI decision to a paused response. Runs on the proxy loop. (+7 more)

### Community 14 - "MainWindow"
Cohesion: 0.13
Nodes (5): QMainWindow, MainWindow, Slot, Return a fresh Collaborator payload host, or None if unavailable. Called by…, Load a file-backed request body inline so editors can show it.

### Community 15 - "FlowRepository"
Cohesion: 0.12
Nodes (10): Connection, Row, FlowRepository, Path, Move the corrupt database and SQLite sidecars to a safe backup., Insert a new flow and return its assigned primary key., Update an existing flow (matched by ``flow_id``)., Insert if new, otherwise update. Returns the row id. (+2 more)

### Community 16 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 17 - "ProxyTab"
Cohesion: 0.09
Nodes (11): ProxyTab, QWidget, Container widget for everything under the top-level "Proxy" tab., Collapse the Target panel to an arrow, or restore its full width., Use Qt's native arrow icon so the control does not depend on fonts., The Clear History button now lives in the Intercept control row. Exposed here…, First click arms the button; a second click within 3s confirms. This guards…, Surface a detailed transient message (e.g. "Starting...", errors) on the… (+3 more)

### Community 18 - "intruder_session.py"
Cohesion: 0.20
Nodes (5): Live test: RepeaterTab.load_from_record + Send performs a real request., Async HTTP sender for Repeater/Intruder. Runs an ``httpx.AsyncClient`` on a…, Networking helpers (async HTTP client for Repeater/Intruder)., A single Intruder session: one request template + its attack + results. This is…, Intruder tab: a container of independent attack sessions. Each "Send to…

### Community 19 - "FindBar"
Cohesion: 0.19
Nodes (8): FindFlags, QKeyEvent, FindBar, QPlainTextEdit, QWidget, A small find bar that searches within a QPlainTextEdit. Reusable over any…, Incremental find controls bound to a target text edit., Reveal the bar, seed it with any selected text, and focus input.

### Community 20 - "collaborator_tab.py"
Cohesion: 0.13
Nodes (16): _encode_xid(), generate_xid(), Interaction, _now_iso(), Interactsh (OAST) client for the Collaborator feature. This is a small, Qt-free…, A single out-of-band interaction reported by the server., Everything needed to resume / persist a registered session., Return a 20-char XID string. XID layout: 4-byte time, 3-byte machine id, 2-byte… (+8 more)

### Community 21 - "repeater_session.py"
Cohesion: 0.10
Nodes (20): absolute_url(), build_request_text(), ensure_host_header(), _headers_have(), host_from_headers_or_url(), parse_request_text(), parse_response_text(), ParsedRequest (+12 more)

### Community 22 - "body_format.py"
Cohesion: 0.11
Nodes (19): HTMLParser, format_body(), _format_c_like(), _format_css(), _format_form(), _format_html(), _format_js(), _format_json() (+11 more)

### Community 23 - "PayloadSetEditor"
Cohesion: 0.15
Nodes (7): QPushButton, PayloadSetEditor, ProcessingRuleDialog, QDialog, QWidget, Edit one payload set: a generator plus a processing-rule pipeline., Configure a single :class:`ProcessingRule`.

### Community 24 - "InteractionsModel"
Cohesion: 0.16
Nodes (9): InteractionRow, InteractionsModel, protocol_color(), QAbstractTableModel, QModelIndex, Render an ISO timestamp as HH:MM:SS, falling back to the raw string., Return a hex color for an interaction protocol., A received interaction plus the display metadata we derive from it. (+1 more)

### Community 25 - "IntruderTab"
Cohesion: 0.15
Nodes (8): IntruderTab, Path, QWidget, Close every Intruder tab., Open a new session tab populated from a captured flow., Write every open session to ``path`` as JSON (list of snapshots)., Recreate the sessions saved by :meth:`save_state`. Accepts both the multi-…, Holds multiple :class:`IntruderSession` instances in a tab strip.

### Community 26 - "FlowRecord"
Cohesion: 0.09
Nodes (15): mitmproxy addon: maps flows to FlowRecords and supports interception. Two…, Storage layer: SQLite persistence + on-disk body store., FlowRecord, Plain data structures passed between the proxy engine, storage, and UI. These…, A single captured HTTP request/response exchange. Body payloads are represented…, The response content type without parameters (e.g. ``text/html``)., File extension derived from the request path (without the dot). The query…, Cookie names sent/received for this flow, comma-separated. Collects request… (+7 more)

### Community 27 - "FlowTableModel"
Cohesion: 0.17
Nodes (6): FlowTableModel, Orientation, QAbstractTableModel, QModelIndex, Replace all rows (e.g. when loading history from the database)., Add a new record, or update an existing one in place. Called from the UI thread…

### Community 28 - "smoke_test.py"
Cohesion: 0.11
Nodes (22): QApplication, main(), Path, Import + wiring smoke test (no live proxy, no visible window). Verifies: - all…, test_body_format(), test_body_store(), test_http_utils(), test_intercept_view() (+14 more)

### Community 29 - "._send"
Cohesion: 0.16
Nodes (6): HistoryEntry, Slot, Set the status/target label, eliding to fit the current width. Stores the full…, Enable/disable the Send action while keeping the button visible. We…, Public entry point for the container to send this tab's request., A request that was sent and (optionally) the response it produced.

### Community 30 - "FlowLayout"
Cohesion: 0.15
Nodes (7): Orientations, QLayout, QLayoutItem, FlowLayout, QRect, QSize, QWidget

### Community 31 - "AsyncHttpSender"
Cohesion: 0.19
Nodes (5): ResultCallback, AsyncHttpSender, _schedule(), Schedule a request; ``callback`` is invoked on the sender thread. Returns a…, Owns a background event loop running httpx.AsyncClient instances.

### Community 32 - "main_window.py"
Cohesion: 0.14
Nodes (18): main(), Application entry point. Creates the Qt application, builds the main window,…, Give Windows an explicit AppUserModelID so the taskbar uses our icon. Without…, _set_windows_app_id(), Bidoytu - an intercepting HTTP proxy tool. Base architecture: - Proxy/MITM…, Enables ``python -m bidoytu``., asset_path(), _assets_dir() (+10 more)

### Community 33 - "QMenu"
Cohesion: 0.14
Nodes (6): QMenu, Install (or clear) the dropdown's group-send options. ``actions`` is a list of…, Record which send mode the split button runs, and show it on the button., Grey out the dropdown's options when there is no request to send., Ask the provider for a payload and insert it at the cursor., Build a FlowRecord from the current (edited) request text.

### Community 34 - "AttackRunner"
Cohesion: 0.20
Nodes (8): QObject, HttpResult, AttackJob, One request to send: the substituted text and the payloads used., AttackRunner, Slot, Launch requests until we hit the concurrency cap or run out., Runs one attack, emitting a :class:`ResultRow` per completed request.

### Community 35 - "GroupDialog"
Cohesion: 0.27
Nodes (3): GroupDialog, QDialog, Collect a group name, member tabs, and a color.

### Community 36 - "iter_jobs"
Cohesion: 0.21
Nodes (11): count_jobs(), find_markers(), iter_jobs(), Marker, Insert ``values`` into ``clean_text`` at each marker (right-to-left). Working…, Best-effort total request count for a configured attack., Yield an :class:`AttackJob` per request for the configured attack.…, A payload position: the span between a pair of ``§`` markers. ``start``/``end``… (+3 more)

### Community 37 - "_Chip"
Cohesion: 0.21
Nodes (6): current_mode(), Return the named color tokens for ``mode`` (falls back to dark)., Return the theme mode currently applied to the application., tokens(), _Chip, A single clickable tab chip with an optional close button.

### Community 38 - "RepeaterTab"
Cohesion: 0.14
Nodes (10): QWidget, Clone a session's request into a new tab, named ``base (n)``., Return ``base (n)`` with the smallest unused positive integer n., Delete a group along with all request tabs it contains., Close every request tab and remove all groups. Always leaves one fresh, empty…, Guarantee at least one (empty) session exists. Called on startup after…, Open a new session tab populated from a captured flow. If the only open session…, Return the sole session iff it is a single, empty, ungrouped tab. (+2 more)

### Community 39 - "Storage Layer (storage/)"
Cohesion: 0.25
Nodes (8): Body Store (file-backed bodies), Capture Addon, Decode Bodies with content not raw_content, FlowRecord Plain Dataclass, asyncio.Event Pause/Forward/Drop, Architecture Layering Invariant, Content-Addressed Body Storage, Storage Layer (storage/)

### Community 40 - "CaCertDialog"
Cohesion: 0.33
Nodes (5): CaCertDialog, Path, QDialog, Dialog for exporting and installing the proxy's CA certificate. To intercept…, Shows CA status, an export button, and install instructions.

### Community 41 - ".restore_state"
Cohesion: 0.20
Nodes (3): Path, Persist the session, generated payloads, and interactions to JSON., Restore a session saved by :meth:`save_state` and re-register it.

### Community 42 - "intercept_response_live_test.py"
Cohesion: 0.31
Nodes (7): check_done(), do_forward(), finish(), on_intercepted(), on_started(), Live: intercept a request via the real MainWindow, forward it, and confirm the…, send()

### Community 43 - "repeater_tab.py"
Cohesion: 0.15
Nodes (9): Dialog for adding Repeater request tabs to a named, colored group. Presents a…, Serializable snapshot of a session (for persistence)., SessionState, Group, Path, Repeater tab: a container of independent request/response sessions. Each "Send…, A named, colored, collapsible collection of member sessions., Write all open sessions and their groups to ``path`` as JSON. (+1 more)

### Community 44 - "WorkspaceDialog"
Cohesion: 0.29
Nodes (3): QDialog, Choose, create, import, or export local workspaces before app startup., WorkspaceDialog

### Community 45 - "intercept_live_test.py"
Cohesion: 0.36
Nodes (6): finish(), on_captured(), on_intercepted(), on_started(), Live test: interception pauses a request, and forward/drop resolve it.…, send()

### Community 46 - "InteractionFilterProxy"
Cohesion: 0.22
Nodes (5): CollaboratorConfig, Settings for the Collaborator (out-of-band interaction) feature. Attributes:…, InteractionFilterProxy, QSortFilterProxyModel, Filter interactions by protocol and a free-text needle.

### Community 47 - "ResultFilterProxy"
Cohesion: 0.25
Nodes (3): QSortFilterProxyModel, Filter results by status, min length, matched-only, and a text needle., ResultFilterProxy

### Community 48 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 49 - "SendHandle"
Cohesion: 0.25
Nodes (4): AbstractEventLoop, A cancellable handle to an in-flight request. The handle wraps the…, SendHandle, Task

### Community 50 - "Bidoytu"
Cohesion: 0.12
Nodes (16): Bidoytu Banner Logo, Bidoytu Circular Icon Logo, A note on the editor widget, Architecture, Bidoytu, Building, Contributing, Data flow (+8 more)

### Community 51 - "attack_runner.py"
Cohesion: 0.38
Nodes (5): Pattern, _compile(), GrepConfig, Drives an Intruder attack: iterate jobs, send them, collect results. The runner…, How to derive match/extract columns from each response.

### Community 53 - "CLAUDE.md"
Cohesion: 0.22
Nodes (7): Architecture and layering (respect this), Conventions, Gotchas learned the hard way, Tech stack, Verifying changes (always do this), What Bidoytu is, Where things live

### Community 54 - "UI Layer (ui/)"
Cohesion: 0.25
Nodes (8): QPlainTextEdit + QSyntaxHighlighter Editor, Headless Smoke Test, Default 127.0.0.1 Bind, HTTP History, Qt Isolation to ui/, SQLite History Store, UI Layer (ui/), Safe Default Localhost Bind

### Community 55 - "Building and releasing Bidoytu"
Cohesion: 0.14
Nodes (13): Build / check the package locally, Build (Windows or Linux), Building and releasing Bidoytu, Cutting version 1.0.0, How releases work (CI/CD), Local builds (optional), Notes, Nuitka (alternative compiler) (+5 more)

### Community 57 - "ProxyEngine (QThread)"
Cohesion: 0.22
Nodes (9): loop.call_soon_threadsafe Into Proxy Loop, Port Availability Pre-check, ProxyEngine (QThread), Qt Signals Cross-Thread Results, SystemExit Errorcheck Catch, Threading Model, mitmproxy Engine, Proxy Layer (proxy/) (+1 more)

### Community 58 - "Security Policy"
Cohesion: 0.22
Nodes (8): Handling the CA certificate, Reporting a vulnerability, Responsible and lawful use, Safe defaults and data handling, Scope, Security Policy, Supported versions, What to expect

### Community 60 - "Public CA Certificate Export"
Cohesion: 0.36
Nodes (8): CA Private Key Protection, Focused Live Test Scripts, Public CA Certificate Export, Request Interception, cryptography Dependency, CA Certificate Handling Policy, Public-Only CA Export Invariant, Untrusted Captured Traffic

### Community 61 - "Release CI/CD Workflow"
Cohesion: 0.22
Nodes (10): Staging-First Git Workflow, PyInstaller Build Step, Release CI/CD Workflow, Rolling latest Pre-Release, Versioned v* Tag Release, Nuitka Alternative Compiler, Desktop App Packaging, Qt Module Excludes (size reduction) (+2 more)

### Community 62 - "proxy_live_test.py"
Cohesion: 0.33
Nodes (3): on_started(), Live end-to-end test: start the ProxyEngine thread and route a real request…, send_request()

### Community 63 - "WorkspaceManager"
Cohesion: 0.15
Nodes (14): Startup picker for local Bidoytu workspaces., _now(), Path, Local, Burp-style workspace management. Each workspace owns its SQLite history,…, Remove every deletable workspace while keeping the legacy recovery one., Write every saved workspace to one portable ZIP archive., Merge all valid workspaces in a Bidoytu archive into this machine., Place a pre-workspace installation into one recoverable session. (+6 more)

### Community 64 - "WrappingTabBar"
Cohesion: 0.21
Nodes (6): QResizeEvent, QScrollArea, Group-aware, wrapping tab bar composed of chip widgets., Rebuild the whole bar from the container's model. Args: order: list of keys…, Grow the bar to fit its rows, capped at ``_max_rows`` (then scroll)., WrappingTabBar

### Community 65 - "Contributing to Bidoytu"
Cohesion: 0.25
Nodes (7): Coding conventions, Contributing to Bidoytu, Development setup, Ground rules, Reporting bugs / security issues, Running the checks, Submitting changes

### Community 70 - "httpx Async Client"
Cohesion: 0.40
Nodes (6): AsyncHttpSender, httpx Async Client, Intruder, Net Layer (net/), Repeater, httpx Dependency

### Community 73 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 75 - "start_proxy_repro.py"
Cohesion: 0.47
Nodes (4): after_start(), finish(), Reproduce the 'start proxy crashes' path using the real MainWindow. Builds the…, send()

### Community 78 - "graphify reference: add a URL and watch a folder"
Cohesion: 0.50
Nodes (3): For /graphify add, For --watch, graphify reference: add a URL and watch a folder

### Community 79 - "graphify reference: commit hook and native CLAUDE.md integration"
Cohesion: 0.50
Nodes (3): For git commit hook, For native CLAUDE.md integration, graphify reference: commit hook and native CLAUDE.md integration

### Community 80 - "graphify reference: incremental update and cluster-only"
Cohesion: 0.50
Nodes (3): For --cluster-only, For --update (incremental re-extraction), graphify reference: incremental update and cluster-only

### Community 83 - "strip_markers"
Cohesion: 0.33
Nodes (3): Return the template with all ``§`` markers removed (defaults kept)., strip_markers(), Wrap each ``name=value`` value (query + body) in markers.

### Community 86 - "wrapping_tab_bar.py"
Cohesion: 0.25
Nodes (5): A wrapping flow layout: children flow left-to-right and wrap to new rows. This…, _FlowHost, QWidget, A wrapping, group-aware tab bar built from individual chip widgets. Unlike…, Host widget whose height tracks its FlowLayout's height-for-width. A…

### Community 92 - "config.py"
Cohesion: 0.11
Nodes (13): finish(), poll_for_ca(), Verify the CA is generated in Bidoytu's confdir and can be exported. Starts the…, on_started(), Verify the capture addon stores DECODED bodies (gzip is undone). Routes a…, Verify starting the proxy on an occupied port produces a clean error signal…, _default_data_dir(), ProxyConfig (+5 more)

## Ambiguous Edges - Review These
- `Qt Isolation to ui/` → `Safe Default Localhost Bind`  [AMBIGUOUS]
  SECURITY.md · relation: conceptually_related_to
- `Public CA Certificate Export` → `CA Certificate Handling Policy`  [AMBIGUOUS]
  SECURITY.md · relation: references

## Knowledge Gaps
- **99 isolated node(s):** `bidoytu`, `For /graphify add and --watch`, `For /graphify query`, `For the commit hook and native CLAUDE.md integration`, `For --update and --cluster-only` (+94 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 577 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **16 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Qt Isolation to ui/` and `Safe Default Localhost Bind`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Public CA Certificate Export` and `CA Certificate Handling Policy`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **Why does `FlowRecord` connect `FlowRecord` to `InterceptView`, `HistoryView`, `IntruderSession`, `InterceptActivityModel`, `RepeaterSession`, `ProxyEngine`, `CaptureAddon`, `MainWindow`, `FlowRepository`, `intruder_session.py`, `repeater_session.py`, `IntruderTab`, `FlowTableModel`, `smoke_test.py`, `._send`, `AsyncHttpSender`, `main_window.py`, `QMenu`, `RepeaterTab`, `repeater_tab.py`, `config.py`?**
  _High betweenness centrality (0.201) - this node is a cross-community bridge._
- **Why does `IntruderSession` connect `IntruderSession` to `AttackRunner`, `wrap_selection`, `iter_jobs`, `MessageView`, `attack.py`, `IntruderResultsModel`, `ResultFilterProxy`, `intruder_session.py`, `attack_runner.py`, `FindBar`, `strip_markers`, `PayloadSetEditor`, `IntruderTab`, `FlowRecord`, `AsyncHttpSender`?**
  _High betweenness centrality (0.101) - this node is a cross-community bridge._
- **Why does `CollaboratorTab` connect `CollaboratorTab` to `main_window.py`, `MessageView`, `InteractshClient`, `.restore_state`, `InteractionFilterProxy`, `MainWindow`, `FindBar`, `collaborator_tab.py`, `InteractionsModel`, `AsyncHttpSender`?**
  _High betweenness centrality (0.091) - this node is a cross-community bridge._
- **Are the 17 inferred relationships involving `FlowRecord` (e.g. with `test_intercept_view()` and `test_qt_and_proxy_apis()`) actually correct?**
  _`FlowRecord` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `RepeaterSession` (e.g. with `AsyncHttpSender` and `HttpResult`) actually correct?**
  _`RepeaterSession` has 7 INFERRED edges - model-reasoned connections that need verification._
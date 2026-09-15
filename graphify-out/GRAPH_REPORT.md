# Graph Report - Bidoytu  (2026-09-15)

## Corpus Check
- 80 files · ~149,517 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 6 file(s) not represented in the graph (top: (none) 4, .spec 1, .ico 1)

## Summary
- 1557 nodes · 2970 edges · 111 communities (92 shown, 17 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 238 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `089ae12b`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- _chevron_icon
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
- intruder_session.py
- ProxyEngine
- CaptureAddon
- MainWindow
- strip_markers
- What You Must Do When Invoked
- ProxyTab
- FlowRecord
- AsyncHttpSender
- interactsh.py
- http_utils.py
- _HTMLPretty
- main_window.py
- InteractionsModel
- IntruderTab
- DetailView
- FlowTableModel
- ._set_has_request
- PayloadSetEditor
- FlowLayout
- WrappingTabBar
- smoke_test.py
- QMenu
- AttackRunner
- Bidoytu documentation
- collaborator_tab.py
- ui_icon
- RepeaterTab
- Storage Layer (storage/)
- SecListsDialog
- Path
- intercept_response_live_test.py
- .restore_state
- FlowRepository
- intercept_live_test.py
- InteractionFilterProxy
- .cookies
- graphify reference: extra exports and benchmark
- parse_request_text
- Bidoytu
- Feature guide
- BodyStore
- CLAUDE.md
- UI Layer (ui/)
- Building and releasing Bidoytu
- _GroupHeaderChip
- ProxyEngine (QThread)
- Security Policy
- _Chip
- Public CA Certificate Export
- Release CI/CD Workflow
- proxy_live_test.py
- WorkspaceManager
- FilterSpec
- Contributing to Bidoytu
- ui/__init__.py
- ca_export_test.py
- bidoytu
- app.py
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
- .restore_sessions
- extraction-spec.md
- _FlowHost
- SendHandle
- Publishing to PyPI (`pip install bidoytu`)
- ._update_group_send_menu
- body_format.py
- config.py
- iter_jobs
- Testing and development
- CONTRIBUTORS.md
- Getting started
- How the application is put together
- HttpHighlighter
- history_view.py
- theme.py
- history_delegate.py
- ._deregister
- QColor
- InteractshError
- _NoFocusRectStyle
- MarkerHighlighter
- ._show_raw
- _SavedFilterDelegate
- .__init__
- wrap_selection

## God Nodes (most connected - your core abstractions)
1. `FlowRecord` - 99 edges
2. `RepeaterSession` - 65 edges
3. `IntruderSession` - 60 edges
4. `MainWindow` - 54 edges
5. `CollaboratorTab` - 50 edges
6. `MessageView` - 45 edges
7. `InterceptView` - 41 edges
8. `RepeaterTab` - 41 edges
9. `HistoryView` - 36 edges
10. `AsyncHttpSender` - 34 edges

## Surprising Connections (you probably didn't know these)
- `Bidoytu Circular Icon Logo` --semantically_similar_to--> `Bundled App Icon Asset`  [INFERRED] [semantically similar]
  logo.png → src/bidoytu/assets/logo.png
- `Bundled App Icon Asset` --conceptually_related_to--> `UI Layer (ui/)`  [INFERRED]
  src/bidoytu/assets/logo.png → README.md
- `Bidoytu` --references--> `Bidoytu Banner Logo`  [EXTRACTED]
  README.md → bidoytu-long.png
- `Bidoytu` --references--> `Bidoytu Circular Icon Logo`  [INFERRED]
  README.md → logo.png
- `Bidoytu Banner Logo` --semantically_similar_to--> `Bidoytu Circular Icon Logo`  [INFERRED] [semantically similar]
  bidoytu-long.png → logo.png

## Import Cycles
- None detected.

## Communities (111 total, 17 thin omitted)

### Community 0 - "_chevron_icon"
Cohesion: 0.15
Nodes (19): QPainter, QPixmap, _blank_pixmap(), _build_qss(), _check_icon(), _chevron_down_icon(), _chevron_icon(), _chevron_up_icon() (+11 more)

### Community 1 - "InterceptView"
Cohesion: 0.07
Nodes (20): InterceptView, QWidget, Size the activity table so URL fills the leftover width, while every column…, Whenever a column is resized, compensate its immediate right neighbor (or left…, Reflow the URL column to absorb the viewport's leftover width. URL is the…, Forward every still-pending flow, then reset the panel. Called when…, A request was paused by the proxy; add it to the table., A response was paused by the proxy; add it to the table. (+12 more)

### Community 2 - "MessageView"
Cohesion: 0.08
Nodes (12): _LineNumberArea, MessageView, QPlainTextEdit, QRect, QSize, QWidget, Switch how the remembered body is rendered and re-display it., Return the full editor contents as text (for editable views). (+4 more)

### Community 3 - "CollaboratorTab"
Cohesion: 0.14
Nodes (6): CollaboratorTab, QWidget, Build a titled pane (label + find bar + view), matching Repeater., Attach a note (e.g. the target tab) to the most recent payload., Generate a payload, tag it with ``note``, and return the hostname. Used by…, Register with an Interactsh server, hand out payloads, show callbacks.

### Community 4 - "HistoryView"
Cohesion: 0.11
Nodes (8): HistoryView, QWidget, Slot, Size columns so Path fills the leftover width initially, while every column…, Whenever a column is resized, compensate its immediate right neighbor (or left…, Reflow the Path column to absorb the viewport's leftover width. Path is the…, Populate the saved-filter picker without coupling the widget to SQLite., Traffic table + detail, with send-to context actions.

### Community 5 - "AppConfig"
Cohesion: 0.11
Nodes (13): AppConfig, Path, Top-level runtime configuration. Attributes: data_dir: Root directory for all…, JSON file holding persisted Repeater sessions across restarts., JSON file holding the last Intruder attack config across restarts., JSON file holding the Target scope for this workspace., JSON file holding Collaborator session state across restarts. Stores the active…, Directory where mitmproxy stores its generated CA and certs. We keep it under… (+5 more)

### Community 6 - "IntruderSession"
Cohesion: 0.10
Nodes (7): IntruderSession, Slot, Grow/shrink the payload-set tabs to exactly ``n`` (min 1)., Return a JSON-serializable snapshot of this session., Restore this session from a snapshot produced by :meth:`to_state`., Build a FlowRecord from the template (payload markers removed)., One Intruder attack: template + positions + payload sets + results.

### Community 7 - "InterceptActivityModel"
Cohesion: 0.08
Nodes (15): ActivityRow, InterceptActivityModel, Orientation, QAbstractTableModel, QModelIndex, Table model for the Intercept tab's activity log. Each intercepted request…, Log a paused (pending) request. Returns its row index., Log a paused (pending) response. Returns its row index. (+7 more)

### Community 8 - "attack.py"
Cohesion: 0.16
Nodes (20): PayloadSet, Intruder attack model: markers, attack types, and request building. Qt-free so…, A generator plus its processing rules (one Intruder payload set)., _apply_one(), apply_rules(), _brute(), build_generator(), describe_rule() (+12 more)

### Community 9 - "InteractshClient"
Cohesion: 0.11
Nodes (10): InteractshClient, _cb(), _cb(), _now_iso(), Register with, generate payloads for, and poll an Interactsh server. The client…, Generate a keypair and register against the first working server. ``servers``…, Return (ok, done). ``done`` short-circuits trying more servers., Restore a persisted session and re-register to keep it alive. (+2 more)

### Community 10 - "RepeaterSession"
Cohesion: 0.11
Nodes (8): HistoryEntry, True if this is a pristine session: no request text and no history., Install (or clear) the dropdown's group-send options. ``actions`` is a list of…, Record which send mode the split button runs, and show it on the button., Grey out the dropdown's options when there is no request to send., A request that was sent and (optionally) the response it produced., One request/response pane with full Repeater controls., RepeaterSession

### Community 11 - "intruder_session.py"
Cohesion: 0.10
Nodes (11): One completed request in the results table., ResultRow, IntruderResultsModel, QAbstractTableModel, QModelIndex, QSortFilterProxyModel, Table model + filter proxy for Intruder attack results.…, Filter results by status, min length, matched-only, and a text needle. (+3 more)

### Community 12 - "ProxyEngine"
Cohesion: 0.08
Nodes (11): QThread, ProxyEngine, Update target scope immediately, including while the proxy runs., Toggle the global 'intercept responses' behavior., Arm a one-shot response intercept for a single flow., Forward a paused request, optionally with edited raw request text., Drop a paused request., Forward a paused response, optionally with edited raw response text. (+3 more)

### Community 13 - "CaptureAddon"
Cohesion: 0.10
Nodes (15): FlowCallback, HTTPFlow, InterceptCallback, CaptureAddon, _PendingFlow, Arm a one-shot response intercept for a single flow (Burp's "Response to this…, Apply a UI decision to a paused request. Runs on the proxy loop., Apply a UI decision to a paused response. Runs on the proxy loop. (+7 more)

### Community 14 - "MainWindow"
Cohesion: 0.07
Nodes (15): QMainWindow, CaCertDialog, Path, QDialog, Dialog for exporting and installing the proxy's CA certificate. To intercept…, Shows CA status, an export button, and install instructions., MainWindow, Slot (+7 more)

### Community 15 - "strip_markers"
Cohesion: 0.33
Nodes (3): Return the template with all ``§`` markers removed (defaults kept)., strip_markers(), Wrap each ``name=value`` value (query + body) in markers.

### Community 16 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 17 - "ProxyTab"
Cohesion: 0.05
Nodes (22): QComboBox, QHBoxLayout, QPushButton, QPlainTextEdit, GroupDialog, QDialog, Dialog for adding Repeater request tabs to a named, colored group. Presents a…, Collect a group name, member tabs, and a color. (+14 more)

### Community 18 - "FlowRecord"
Cohesion: 0.15
Nodes (21): _body(), _compare(), curl_command(), export_records(), _field(), fingerprint(), _headers(), matches() (+13 more)

### Community 19 - "AsyncHttpSender"
Cohesion: 0.15
Nodes (6): ResultCallback, AsyncHttpSender, _schedule(), Schedule a request; ``callback`` is invoked on the sender thread. Returns a…, Owns a background event loop running httpx.AsyncClient instances., Networking helpers (async HTTP client for Repeater/Intruder).

### Community 20 - "interactsh.py"
Cohesion: 0.22
Nodes (8): _encode_xid(), generate_xid(), Interactsh (OAST) client for the Collaborator feature. This is a small, Qt-free…, Everything needed to resume / persist a registered session., Return a 20-char XID string. XID layout: 4-byte time, 3-byte machine id, 2-byte…, Encode 12 raw bytes into the 20-char XID base32 representation., SessionInfo, _session_from_dict()

### Community 21 - "http_utils.py"
Cohesion: 0.11
Nodes (18): absolute_url(), build_request_text(), build_response_text(), ensure_host_header(), _headers_have(), parse_response_text(), ParsedResponse, Helpers for converting between raw HTTP text and structured parts. Used by… (+10 more)

### Community 22 - "_HTMLPretty"
Cohesion: 0.22
Nodes (4): HTMLParser, _HTMLPretty, Lenient HTML pretty-printer built on the stdlib parser. Emits nicely indented…, Close a preceding sibling with an optional end tag, if applicable.

### Community 23 - "main_window.py"
Cohesion: 0.16
Nodes (8): Live test: RepeaterTab.load_from_record + Send performs a real request., On-disk store for large request/response bodies. Rather than storing large…, Storage layer: SQLite persistence + on-disk body store., Plain data structures passed between the proxy engine, storage, and UI. These…, SQLite persistence for captured flows. Uses the stdlib ``sqlite3`` module…, Intruder tab: a container of independent attack sessions. Each "Send to…, Main application window. Top-level layout is a QTabWidget with four tabs: -…, Repeater tab: a container of independent request/response sessions. Each "Send…

### Community 24 - "InteractionsModel"
Cohesion: 0.14
Nodes (12): Interaction, A single out-of-band interaction reported by the server., InteractionRow, InteractionsModel, protocol_color(), QAbstractTableModel, QModelIndex, Table model + filter proxy for Collaborator (OAST) interactions.… (+4 more)

### Community 25 - "IntruderTab"
Cohesion: 0.15
Nodes (8): IntruderTab, Path, QWidget, Close every Intruder tab., Open a new session tab populated from a captured flow., Write every open session to ``path`` as JSON (list of snapshots)., Recreate the sessions saved by :meth:`save_state`. Accepts both the multi-…, Holds multiple :class:`IntruderSession` instances in a tab strip.

### Community 26 - "DetailView"
Cohesion: 0.31
Nodes (3): DetailView, QWidget, Two MessageViews (request | response) with a shared soft-wrap toggle.

### Community 27 - "FlowTableModel"
Cohesion: 0.11
Nodes (8): SortOrder, FlowTableModel, Orientation, QAbstractTableModel, QModelIndex, Replace all rows (e.g. when loading history from the database)., Sort the source rows while keeping the active History filter applied., Add a new record, or update an existing one in place. Called from the UI thread…

### Community 28 - "._set_has_request"
Cohesion: 0.25
Nodes (4): Enable/disable the Send action while keeping the button visible. We…, Paint the Send button with the disabled cue when it has no request. Uses a…, Serializable snapshot of a session (for persistence)., SessionState

### Community 29 - "PayloadSetEditor"
Cohesion: 0.14
Nodes (6): PayloadSetEditor, ProcessingRuleDialog, QDialog, QWidget, Edit one payload set: a generator plus a processing-rule pipeline., Configure a single :class:`ProcessingRule`.

### Community 30 - "FlowLayout"
Cohesion: 0.15
Nodes (7): Orientations, QLayout, QLayoutItem, FlowLayout, QRect, QSize, QWidget

### Community 31 - "WrappingTabBar"
Cohesion: 0.29
Nodes (4): Group-aware, wrapping tab bar composed of chip widgets., Rebuild the whole bar from the container's model. Args: order: list of keys…, Grow the bar to fit its rows, capped at ``_max_rows`` (then scroll)., WrappingTabBar

### Community 32 - "smoke_test.py"
Cohesion: 0.35
Nodes (11): QApplication, main(), Path, Import + wiring smoke test (no live proxy, no visible window). Verifies: - all…, test_body_format(), test_body_store(), test_http_utils(), test_intercept_view() (+3 more)

### Community 33 - "QMenu"
Cohesion: 0.29
Nodes (3): QMenu, Ask the provider for a payload and insert it at the cursor., Build a FlowRecord from the current (edited) request text.

### Community 34 - "AttackRunner"
Cohesion: 0.16
Nodes (10): QObject, HttpResult, Async HTTP sender for Repeater/Intruder. Runs an ``httpx.AsyncClient`` on a…, AttackJob, One request to send: the substituted text and the payloads used., AttackRunner, Slot, Drives an Intruder attack: iterate jobs, send them, collect results. The runner… (+2 more)

### Community 35 - "Bidoytu documentation"
Cohesion: 0.18
Nodes (11): At a glance, Bidoytu documentation, Configuration, Contents, Data and storage, First-run workflow, Packaging and releases, Repository map (+3 more)

### Community 36 - "collaborator_tab.py"
Cohesion: 0.13
Nodes (12): FindFlags, QKeyEvent, Collaborator tab: out-of-band (OAST) interaction listener. Bidoytu's equivalent…, FindBar, QWidget, A small find bar that searches within a QPlainTextEdit. Reusable over any…, Incremental find controls bound to a target text edit., Reveal the bar, seed it with any selected text, and focus input. (+4 more)

### Community 37 - "ui_icon"
Cohesion: 0.22
Nodes (9): QIcon, A wrapping flow layout: children flow left-to-right and wrap to new rows. This…, current_mode(), Return the named color tokens for ``mode`` (falls back to dark)., Return a font-independent icon for compact UI controls., Return the theme mode currently applied to the application., tokens(), ui_icon() (+1 more)

### Community 38 - "RepeaterTab"
Cohesion: 0.14
Nodes (10): QWidget, Clone a session's request into a new tab, named ``base (n)``., Return ``base (n)`` with the smallest unused positive integer n., Delete a group along with all request tabs it contains., Close every request tab and remove all groups. Always leaves one fresh, empty…, Guarantee at least one (empty) session exists. Called on startup after…, Open a new session tab populated from a captured flow. If the only open session…, Return the sole session iff it is a single, empty, ungrouped tab. (+2 more)

### Community 39 - "Storage Layer (storage/)"
Cohesion: 0.20
Nodes (10): Body Store (file-backed bodies), Capture Addon, Decode Bodies with content not raw_content, FlowRecord Plain Dataclass, asyncio.Event Pause/Forward/Drop, Architecture Layering Invariant, Content-Addressed Body Storage, HTTP History (+2 more)

### Community 40 - "SecListsDialog"
Cohesion: 0.07
Nodes (24): QTreeWidgetItem, default_cache_dir(), Path, Browse and fetch wordlists from the SecLists project on demand. `SecLists…, Where a given repository path is (or would be) cached locally., Whether the wordlist at *path* already exists in the local cache., Return repo-relative paths of every wordlist already cached locally., Download the wordlist at *path* into the cache and return its path. If the file… (+16 more)

### Community 41 - "Path"
Cohesion: 0.38
Nodes (3): Path, Persist the session, generated payloads, and interactions to JSON., _session_to_dict()

### Community 42 - "intercept_response_live_test.py"
Cohesion: 0.31
Nodes (7): check_done(), do_forward(), finish(), on_intercepted(), on_started(), Live: intercept a request via the real MainWindow, forward it, and confirm the…, send()

### Community 43 - ".restore_state"
Cohesion: 0.20
Nodes (3): Slot, Best-effort correlate an interaction back to a generated payload., Restore a session saved by :meth:`save_state` and re-register it.

### Community 44 - "FlowRepository"
Cohesion: 0.09
Nodes (12): Connection, Row, FlowRepository, Path, Move the corrupt database and SQLite sidecars to a safe backup., Insert a new flow and return its assigned primary key., Update an existing flow (matched by ``flow_id``)., Insert if new, otherwise update. Returns the row id. (+4 more)

### Community 45 - "intercept_live_test.py"
Cohesion: 0.36
Nodes (6): finish(), on_captured(), on_intercepted(), on_started(), Live test: interception pauses a request, and forward/drop resolve it.…, send()

### Community 46 - "InteractionFilterProxy"
Cohesion: 0.22
Nodes (5): CollaboratorConfig, Settings for the Collaborator (out-of-band interaction) feature. Attributes:…, InteractionFilterProxy, QSortFilterProxyModel, Filter interactions by protocol and a free-text needle.

### Community 48 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 49 - "parse_request_text"
Cohesion: 0.15
Nodes (8): host_from_headers_or_url(), parse_request_text(), ParsedRequest, Determine (scheme, host, port, path) for sending a parsed request. Prefers an…, Parse raw HTTP request text into a :class:`ParsedRequest`. Tolerant of both…, Slot, Set the status/target label, eliding to fit the current width. Stores the full…, Public entry point for the container to send this tab's request.

### Community 50 - "Bidoytu"
Cohesion: 0.14
Nodes (15): Bidoytu Banner Logo, Bidoytu Circular Icon Logo, A note on the editor widget, Architecture, Bidoytu, Building, Contributing, Data flow (+7 more)

### Community 51 - "Feature guide"
Cohesion: 0.25
Nodes (8): Collaborator, Display and themes, Feature guide, History, Intercept, Intruder, Proxy, Repeater

### Community 52 - "BodyStore"
Cohesion: 0.25
Nodes (5): BodyStore, Path, Content-addressed file store for body payloads. Files are sharded into…, Write ``data`` to the store and return its relative path. Identical content…, Read body content previously returned by :meth:`store`.

### Community 53 - "CLAUDE.md"
Cohesion: 0.22
Nodes (7): Architecture and layering (respect this), Conventions, Gotchas learned the hard way, Tech stack, Verifying changes (always do this), What Bidoytu is, Where things live

### Community 54 - "UI Layer (ui/)"
Cohesion: 0.22
Nodes (9): QPlainTextEdit + QSyntaxHighlighter Editor, Headless Smoke Test, Default 127.0.0.1 Bind, PySide6, Qt Isolation to ui/, UI Layer (ui/), PySide6 Dependency, Safe Default Localhost Bind (+1 more)

### Community 55 - "Building and releasing Bidoytu"
Cohesion: 0.22
Nodes (9): Build (Windows or Linux), Building and releasing Bidoytu, Cutting version 1.0.0, How releases work (CI/CD), Local builds (optional), Notes, Nuitka (alternative compiler), Prerequisites (+1 more)

### Community 57 - "ProxyEngine (QThread)"
Cohesion: 0.22
Nodes (9): loop.call_soon_threadsafe Into Proxy Loop, Port Availability Pre-check, ProxyEngine (QThread), Qt Signals Cross-Thread Results, SystemExit Errorcheck Catch, Threading Model, mitmproxy Engine, Proxy Layer (proxy/) (+1 more)

### Community 58 - "Security Policy"
Cohesion: 0.25
Nodes (8): Handling the CA certificate, Reporting a vulnerability, Responsible and lawful use, Safe defaults and data handling, Scope, Security Policy, Supported versions, What to expect

### Community 59 - "_Chip"
Cohesion: 0.26
Nodes (3): QMouseEvent, _Chip, A single clickable tab chip with an optional close button.

### Community 60 - "Public CA Certificate Export"
Cohesion: 0.36
Nodes (8): CA Private Key Protection, Focused Live Test Scripts, Public CA Certificate Export, Request Interception, cryptography Dependency, CA Certificate Handling Policy, Public-Only CA Export Invariant, Untrusted Captured Traffic

### Community 61 - "Release CI/CD Workflow"
Cohesion: 0.29
Nodes (8): Staging-First Git Workflow, PyInstaller Build Step, Release CI/CD Workflow, Rolling latest Pre-Release, Versioned v* Tag Release, Nuitka Alternative Compiler, Desktop App Packaging, Qt Module Excludes (size reduction)

### Community 62 - "proxy_live_test.py"
Cohesion: 0.33
Nodes (3): on_started(), Live end-to-end test: start the ProxyEngine thread and route a real request…, send_request()

### Community 63 - "WorkspaceManager"
Cohesion: 0.10
Nodes (17): QDialog, Startup picker for local Bidoytu workspaces., Choose, create, import, or export local workspaces before app startup., WorkspaceDialog, _now(), Path, Local, Burp-style workspace management. Each workspace owns its SQLite history,…, Remove every deletable workspace while keeping the legacy recovery one. (+9 more)

### Community 64 - "FilterSpec"
Cohesion: 0.19
Nodes (7): QGroupBox, QScrollArea, FilterSpec, HistoryFilterDialog, QDialog, Burp-style modal filter settings for HTTP History., Edit a :class:`FilterSpec` without changing the table until Apply.

### Community 65 - "Contributing to Bidoytu"
Cohesion: 0.29
Nodes (7): Coding conventions, Contributing to Bidoytu, Development setup, Ground rules, Reporting bugs / security issues, Running the checks, Submitting changes

### Community 67 - "ca_export_test.py"
Cohesion: 0.67
Nodes (3): finish(), poll_for_ca(), Verify the CA is generated in Bidoytu's confdir and can be exported. Starts the…

### Community 69 - "app.py"
Cohesion: 0.16
Nodes (15): main(), Application entry point. Creates the Qt application, builds the main window,…, Give Windows an explicit AppUserModelID so the taskbar uses our icon. Without…, _set_windows_app_id(), Bidoytu - an intercepting HTTP proxy tool. Base architecture: - Proxy/MITM…, Enables ``python -m bidoytu``., asset_path(), _assets_dir() (+7 more)

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

### Community 83 - ".restore_sessions"
Cohesion: 0.29
Nodes (5): Group, Path, A named, colored, collapsible collection of member sessions., Write all open sessions and their groups to ``path`` as JSON., Recreate sessions and groups saved by :meth:`save_sessions`.

### Community 86 - "_FlowHost"
Cohesion: 0.36
Nodes (4): QResizeEvent, _FlowHost, QWidget, Host widget whose height tracks its FlowLayout's height-for-width. A…

### Community 87 - "SendHandle"
Cohesion: 0.25
Nodes (4): AbstractEventLoop, A cancellable handle to an in-flight request. The handle wraps the…, SendHandle, Task

### Community 89 - "Publishing to PyPI (`pip install bidoytu`)"
Cohesion: 0.50
Nodes (4): Build / check the package locally, One-time setup on PyPI, Publishing to PyPI (`pip install bidoytu`), Releasing a new version to PyPI

### Community 91 - "body_format.py"
Cohesion: 0.20
Nodes (15): format_body(), _format_c_like(), _format_css(), _format_form(), _format_html(), _format_js(), _format_json(), _format_xml() (+7 more)

### Community 92 - "config.py"
Cohesion: 0.11
Nodes (16): on_started(), Verify the capture addon stores DECODED bodies (gzip is undone). Routes a…, Verify starting the proxy on an occupied port produces a clean error signal…, _default_data_dir(), host_matches_scope(), matches(), _normalise_scope_entry(), ProxyConfig (+8 more)

### Community 93 - "iter_jobs"
Cohesion: 0.17
Nodes (13): count_jobs(), find_markers(), iter_jobs(), Marker, Insert ``values`` into ``clean_text`` at each marker (right-to-left). Working…, Best-effort total request count for a configured attack., Yield an :class:`AttackJob` per request for the configured attack.…, A payload position: the span between a pair of ``§`` markers. ``start``/``end``… (+5 more)

### Community 94 - "Testing and development"
Cohesion: 0.67
Nodes (3): Contribution workflow, Fast verification, Testing and development

### Community 96 - "Getting started"
Cohesion: 0.67
Nodes (3): Getting started, Install from source, Requirements

### Community 97 - "How the application is put together"
Cohesion: 0.67
Nodes (3): How the application is put together, Startup sequence, Threading model

### Community 98 - "HttpHighlighter"
Cohesion: 0.23
Nodes (7): QSyntaxHighlighter, HttpHighlighter, Lightweight syntax highlighting for raw HTTP messages. Uses…, Highlights HTTP start-lines and headers., Re-color for a new theme mode and re-highlight the document., highlight_colors(), Return the highlighter color set for ``mode`` (falls back to dark).

### Community 99 - "history_view.py"
Cohesion: 0.20
Nodes (7): deserialize_filter_spec(), Persist the complete filter state in the saved-filter query column., Load a saved filter, accepting legacy plain HTTPQL values., serialize_filter_spec(), Custom QAbstractTableModel backing the traffic history view. We use a hand-…, HTTP history: the traffic table plus a request/response detail view. Emits a…, Proxy tab: Target scope, proxy controls, and HTTP History / Intercept tabs. The…

### Community 100 - "theme.py"
Cohesion: 0.36
Nodes (8): QPalette, apply_theme(), _dark_palette(), _light_palette(), _palette_from_tokens(), _qss_for(), Application theming: light and dark modes. Provides two things: -…, Apply ``mode`` ('light' or 'dark') to the whole application.

### Community 101 - "history_delegate.py"
Cohesion: 0.27
Nodes (8): HistoryItemDelegate, QStyledItemDelegate, Item delegate for the HTTP history table. This delegate paints every cell…, A soft, muted tint of the accent used to fill the selected row. Uses the shared…, Fully self-painted cells: soft row wash + slim accent bar, no style frame., _selection_fill(), highlight_bg(), selection_color()

### Community 103 - "QColor"
Cohesion: 0.47
Nodes (5): QColor, QTextCharFormat, _fmt(), _blend(), Blend ``fg`` over ``bg`` by ``alpha`` (0..1) and return a hex string. Used to…

### Community 104 - "InteractshError"
Cohesion: 0.40
Nodes (4): Exception, InteractshError, Raised for registration / polling / crypto failures., Return a fresh unique payload hostname for this session. Format:…

### Community 105 - "_NoFocusRectStyle"
Cohesion: 0.60
Nodes (3): QProxyStyle, _NoFocusRectStyle, Application style that suppresses the item-view focus rectangle globally. The…

### Community 106 - "MarkerHighlighter"
Cohesion: 0.50
Nodes (3): MarkerHighlighter, Highlighter for the Intruder request template. A…, HTTP highlighting plus a highlighted background for ``§payload§`` spans.

### Community 107 - "._show_raw"
Cohesion: 0.50
Nodes (3): Render a raw HTTP message, pretty-printing its body by content-type. Splits…, Split a raw HTTP message into (start_line, headers, body). Tolerant of both…, _split_http_message()

### Community 108 - "_SavedFilterDelegate"
Cohesion: 0.67
Nodes (3): QStyledItemDelegate, Paint saved-filter names with a compact delete affordance., _SavedFilterDelegate

## Ambiguous Edges - Review These
- `Qt Isolation to ui/` → `Safe Default Localhost Bind`  [AMBIGUOUS]
  SECURITY.md · relation: conceptually_related_to
- `Public CA Certificate Export` → `CA Certificate Handling Policy`  [AMBIGUOUS]
  SECURITY.md · relation: references

## Knowledge Gaps
- **121 isolated node(s):** `bidoytu`, `Usage`, `What graphify is for`, `Step 0 - GitHub repos and multi-path merge (only if a URL or several paths)`, `Step 1 - Ensure graphify is installed` (+116 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 635 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **17 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Qt Isolation to ui/` and `Safe Default Localhost Bind`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Public CA Certificate Export` and `CA Certificate Handling Policy`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **Why does `FlowRecord` connect `FlowRecord` to `InterceptView`, `HistoryView`, `IntruderSession`, `InterceptActivityModel`, `RepeaterSession`, `intruder_session.py`, `ProxyEngine`, `CaptureAddon`, `MainWindow`, `AsyncHttpSender`, `http_utils.py`, `main_window.py`, `IntruderTab`, `DetailView`, `FlowTableModel`, `smoke_test.py`, `QMenu`, `collaborator_tab.py`, `RepeaterTab`, `FlowRepository`, `.cookies`, `parse_request_text`, `config.py`, `history_view.py`?**
  _High betweenness centrality (0.202) - this node is a cross-community bridge._
- **Why does `CollaboratorTab` connect `CollaboratorTab` to `MessageView`, `collaborator_tab.py`, `._deregister`, `InteractshError`, `InteractshClient`, `Path`, `.restore_state`, `._show_raw`, `InteractionFilterProxy`, `MainWindow`, `AsyncHttpSender`, `main_window.py`, `InteractionsModel`?**
  _High betweenness centrality (0.071) - this node is a cross-community bridge._
- **Why does `IntruderSession` connect `IntruderSession` to `AttackRunner`, `MessageView`, `collaborator_tab.py`, `attack.py`, `MarkerHighlighter`, `intruder_session.py`, `wrap_selection`, `strip_markers`, `ProxyTab`, `FlowRecord`, `AsyncHttpSender`, `parse_request_text`, `PayloadSetEditor`, `main_window.py`, `IntruderTab`, `iter_jobs`?**
  _High betweenness centrality (0.070) - this node is a cross-community bridge._
- **Are the 28 inferred relationships involving `FlowRecord` (e.g. with `test_intercept_view()` and `test_qt_and_proxy_apis()`) actually correct?**
  _`FlowRecord` has 28 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `RepeaterSession` (e.g. with `AsyncHttpSender` and `HttpResult`) actually correct?**
  _`RepeaterSession` has 7 INFERRED edges - model-reasoned connections that need verification._
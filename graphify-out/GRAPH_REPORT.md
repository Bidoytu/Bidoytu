# Graph Report - Bidoytu  (2026-09-15)

## Corpus Check
- 75 files · ~141,291 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 6 file(s) not represented in the graph (top: (none) 4, .spec 1, .ico 1)

## Summary
- 1406 nodes · 2533 edges · 91 communities (71 shown, 19 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 172 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `68bdcede`
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
- intruder_session.py
- InteractshClient
- RepeaterSession
- IntruderResultsModel
- ProxyEngine
- CaptureAddon
- MainWindow
- FlowRecord
- What You Must Do When Invoked
- body_format.py
- PayloadSetEditor
- FindBar
- collaborator_tab.py
- parse_request_text
- _HTMLPretty
- AttackRunner
- InteractionsModel
- IntruderTab
- models.py
- FlowTableModel
- smoke_test.py
- content_type_from_headers
- FlowLayout
- AsyncHttpSender
- ._open_or_recover
- QMenu
- iter_jobs
- GroupDialog
- BodyStore
- WrappingTabBar
- RepeaterTab
- Storage Layer (storage/)
- ProxyTab
- .restore_state
- intercept_response_live_test.py
- repeater_tab.py
- intercept_view.py
- intercept_live_test.py
- InteractionFilterProxy
- _LineNumberArea
- graphify reference: extra exports and benchmark
- SendHandle
- Bidoytu
- config.py
- ._restore_attack
- CLAUDE.md
- UI Layer (ui/)
- Building and releasing Bidoytu
- .__init__
- ProxyEngine (QThread)
- Security Policy
- wrap_selection
- Public CA Certificate Export
- Release CI/CD Workflow
- proxy_live_test.py
- WorkspaceManager
- QSize
- Contributing to Bidoytu
- ui/__init__.py
- http_utils.py
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
- Path
- ca_export_test.py
- .__init__
- .cookies
- CONTRIBUTORS.md

## God Nodes (most connected - your core abstractions)
1. `FlowRecord` - 62 edges
2. `IntruderSession` - 60 edges
3. `RepeaterSession` - 59 edges
4. `CollaboratorTab` - 48 edges
5. `InterceptView` - 39 edges
6. `RepeaterTab` - 38 edges
7. `MainWindow` - 36 edges
8. `MessageView` - 36 edges
9. `InterceptActivityModel` - 29 edges
10. `ProxyEngine` - 25 edges

## Surprising Connections (you probably didn't know these)
- `Bundled App Icon Asset` --conceptually_related_to--> `UI Layer (ui/)`  [INFERRED]
  src/bidoytu/assets/logo.png → README.md
- `Bidoytu` --references--> `Bidoytu Banner Logo`  [EXTRACTED]
  README.md → bidoytu-long.png
- `Bidoytu` --references--> `Bidoytu Circular Icon Logo`  [INFERRED]
  README.md → logo.png
- `Design rules` --semantically_similar_to--> `Architecture Layering Invariant`  [INFERRED] [semantically similar]
  CONTRIBUTING.md → CLAUDE.md
- `Bidoytu Banner Logo` --semantically_similar_to--> `Bidoytu Circular Icon Logo`  [INFERRED] [semantically similar]
  bidoytu-long.png → logo.png

## Import Cycles
- None detected.

## Communities (91 total, 19 thin omitted)

### Community 0 - "theme.py"
Cohesion: 0.05
Nodes (54): Path, QPalette, QPixmap, QProxyStyle, main(), Application entry point. Creates the Qt application, builds the main window,…, Give Windows an explicit AppUserModelID so the taskbar uses our icon. Without…, _set_windows_app_id() (+46 more)

### Community 1 - "InterceptView"
Cohesion: 0.07
Nodes (21): InterceptView, FlowRecord, QWidget, Size the activity table so URL fills the leftover width, while every column…, Whenever a column is resized, compensate its immediate right neighbor (or left…, Reflow the URL column to absorb the viewport's leftover width. URL is the…, Forward every still-pending flow, then reset the panel. Called when…, A request was paused by the proxy; add it to the table. (+13 more)

### Community 2 - "MessageView"
Cohesion: 0.12
Nodes (7): MessageView, QPlainTextEdit, QRect, Return the full editor contents as text (for editable views)., Re-color the syntax highlighter for a new theme mode., Register an extra action shown in the right-click menu. The action is appended…, A monospace, syntax-highlighted view of a raw HTTP request/response.

### Community 3 - "CollaboratorTab"
Cohesion: 0.10
Nodes (7): CollaboratorTab, Slot, Render a raw HTTP message, pretty-printing its body by content-type. Splits…, Attach a note (e.g. the target tab) to the most recent payload., Generate a payload, tag it with ``note``, and return the hostname. Used by…, Register with an Interactsh server, hand out payloads, show callbacks., Stop polling and deregister on application close (best-effort).

### Community 4 - "HistoryView"
Cohesion: 0.07
Nodes (17): FlowTableModel, QStyledItemDelegate, DetailView, FlowRecord, QWidget, Reusable side-by-side request/response viewer. Used by the Proxy history, the…, Two MessageViews (request | response) with a shared soft-wrap toggle., HistoryItemDelegate (+9 more)

### Community 5 - "AppConfig"
Cohesion: 0.10
Nodes (15): AppConfig, _default_data_dir(), Path, Top-level runtime configuration. Attributes: data_dir: Root directory for all…, JSON file holding persisted Repeater sessions across restarts., JSON file holding the last Intruder attack config across restarts., Return a per-user, per-OS data directory for Bidoytu., JSON file holding the Target scope for this workspace. (+7 more)

### Community 6 - "IntruderSession"
Cohesion: 0.10
Nodes (7): QHBoxLayout, IntruderSession, QWidget, Slot, Return a JSON-serializable snapshot of this session., Build a FlowRecord from the template (payload markers removed)., One Intruder attack: template + positions + payload sets + results.

### Community 7 - "InterceptActivityModel"
Cohesion: 0.08
Nodes (14): ActivityRow, InterceptActivityModel, Orientation, QAbstractTableModel, QModelIndex, Log a paused (pending) request. Returns its row index., Log a paused (pending) response. Returns its row index., True if the row is a still-pending request or response. (+6 more)

### Community 8 - "intruder_session.py"
Cohesion: 0.15
Nodes (23): count_jobs(), PayloadSet, Intruder attack model: markers, attack types, and request building. Qt-free so…, Best-effort total request count for a configured attack., A generator plus its processing rules (one Intruder payload set)., _apply_one(), apply_rules(), _brute() (+15 more)

### Community 9 - "InteractshClient"
Cohesion: 0.11
Nodes (10): InteractshClient, _cb(), _cb(), _now_iso(), Register with, generate payloads for, and poll an Interactsh server. The client…, Generate a keypair and register against the first working server. ``servers``…, Return (ok, done). ``done`` short-circuits trying more servers., Return a fresh unique payload hostname for this session. Format:… (+2 more)

### Community 10 - "RepeaterSession"
Cohesion: 0.14
Nodes (8): FindBar, MessageView, AsyncHttpSender, QWidget, True if this is a pristine session: no request text and no history., Paint the Send button with the disabled cue when it has no request. Uses a…, One request/response pane with full Repeater controls., RepeaterSession

### Community 11 - "IntruderResultsModel"
Cohesion: 0.11
Nodes (10): One completed request in the results table., ResultRow, IntruderResultsModel, QAbstractTableModel, QModelIndex, QSortFilterProxyModel, Table model + filter proxy for Intruder attack results.…, Filter results by status, min length, matched-only, and a text needle. (+2 more)

### Community 12 - "ProxyEngine"
Cohesion: 0.07
Nodes (12): QThread, ProxyEngine, Update target scope immediately, including while the proxy runs., Toggle the global 'intercept responses' behavior., Arm a one-shot response intercept for a single flow., Forward a paused request, optionally with edited raw request text., Drop a paused request., Forward a paused response, optionally with edited raw response text. (+4 more)

### Community 13 - "CaptureAddon"
Cohesion: 0.12
Nodes (13): HTTPFlow, CaptureAddon, _PendingFlow, Arm a one-shot response intercept for a single flow (Burp's "Response to this…, Apply a UI decision to a paused request. Runs on the proxy loop., Apply a UI decision to a paused response. Runs on the proxy loop., Rewrite a flow's request from edited raw text before forwarding., Rewrite a flow's response from edited raw text before forwarding. (+5 more)

### Community 14 - "MainWindow"
Cohesion: 0.10
Nodes (11): AppConfig, QMainWindow, MainWindow, FlowRecord, Slot, Export every locally saved session to one portable archive., Flush state that lives in widgets rather than the flow repository., Return a fresh Collaborator payload host, or None if unavailable. Called by… (+3 more)

### Community 15 - "FlowRecord"
Cohesion: 0.14
Nodes (10): Row, FlowRecord, A single captured HTTP request/response exchange. Body payloads are represented…, The response content type without parameters (e.g. ``text/html``)., File extension derived from the request path (without the dot). The query…, FlowRepository, Insert a new flow and return its assigned primary key., Update an existing flow (matched by ``flow_id``). (+2 more)

### Community 16 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 17 - "body_format.py"
Cohesion: 0.20
Nodes (15): format_body(), _format_c_like(), _format_css(), _format_form(), _format_html(), _format_js(), _format_json(), _format_xml() (+7 more)

### Community 18 - "PayloadSetEditor"
Cohesion: 0.15
Nodes (6): PayloadSetEditor, ProcessingRuleDialog, QDialog, QWidget, Edit one payload set: a generator plus a processing-rule pipeline., Configure a single :class:`ProcessingRule`.

### Community 19 - "FindBar"
Cohesion: 0.14
Nodes (10): FindFlags, QKeyEvent, QWidget, Build a titled pane (label + find bar + view), matching Repeater., FindBar, QPlainTextEdit, QWidget, A small find bar that searches within a QPlainTextEdit. Reusable over any… (+2 more)

### Community 20 - "collaborator_tab.py"
Cohesion: 0.10
Nodes (18): Exception, Live test: RepeaterTab.load_from_record + Send performs a real request., Async HTTP sender for Repeater/Intruder. Runs an ``httpx.AsyncClient`` on a…, _encode_xid(), generate_xid(), InteractshError, Interactsh (OAST) client for the Collaborator feature. This is a small, Qt-free…, Everything needed to resume / persist a registered session. (+10 more)

### Community 21 - "parse_request_text"
Cohesion: 0.27
Nodes (6): host_from_headers_or_url(), parse_request_text(), ParsedRequest, Determine (scheme, host, port, path) for sending a parsed request. Prefers an…, Parse raw HTTP request text into a :class:`ParsedRequest`. Tolerant of both…, Drives an Intruder attack: iterate jobs, send them, collect results. The runner…

### Community 22 - "_HTMLPretty"
Cohesion: 0.22
Nodes (4): HTMLParser, _HTMLPretty, Lenient HTML pretty-printer built on the stdlib parser. Emits nicely indented…, Close a preceding sibling with an optional end tag, if applicable.

### Community 23 - "AttackRunner"
Cohesion: 0.20
Nodes (8): QObject, HttpResult, AttackJob, One request to send: the substituted text and the payloads used., AttackRunner, Slot, Launch requests until we hit the concurrency cap or run out., Runs one attack, emitting a :class:`ResultRow` per completed request.

### Community 24 - "InteractionsModel"
Cohesion: 0.13
Nodes (12): Interaction, A single out-of-band interaction reported by the server., InteractionRow, InteractionsModel, protocol_color(), QAbstractTableModel, QModelIndex, Table model + filter proxy for Collaborator (OAST) interactions.… (+4 more)

### Community 25 - "IntruderTab"
Cohesion: 0.15
Nodes (8): IntruderTab, Path, QWidget, Close every Intruder tab., Open a new session tab populated from a captured flow., Write every open session to ``path`` as JSON (list of snapshots)., Recreate the sessions saved by :meth:`save_state`. Accepts both the multi-…, Holds multiple :class:`IntruderSession` instances in a tab strip.

### Community 26 - "models.py"
Cohesion: 0.22
Nodes (5): Plain data structures passed between the proxy engine, storage, and UI. These…, Custom QAbstractTableModel backing the traffic history view. We use a hand-…, HTTP history: the traffic table plus a request/response detail view. Emits a…, Table model for the Intercept tab's activity log. Each intercepted request…, Intruder tab: a container of independent attack sessions. Each "Send to…

### Community 27 - "FlowTableModel"
Cohesion: 0.17
Nodes (6): FlowTableModel, Orientation, QAbstractTableModel, QModelIndex, Replace all rows (e.g. when loading history from the database)., Add a new record, or update an existing one in place. Called from the UI thread…

### Community 28 - "smoke_test.py"
Cohesion: 0.35
Nodes (11): QApplication, main(), Path, Import + wiring smoke test (no live proxy, no visible window). Verifies: - all…, test_body_format(), test_body_store(), test_http_utils(), test_intercept_view() (+3 more)

### Community 29 - "content_type_from_headers"
Cohesion: 0.16
Nodes (8): HttpResult, content_type_from_headers(), Extract the Content-Type value from a raw header block (case-insensitive)., FlowRecord, Slot, Set the status/target label, eliding to fit the current width. Stores the full…, Enable/disable the Send action while keeping the button visible. We…, Public entry point for the container to send this tab's request.

### Community 30 - "FlowLayout"
Cohesion: 0.13
Nodes (8): Orientations, QLayout, QLayoutItem, FlowLayout, QRect, QSize, QWidget, A wrapping flow layout: children flow left-to-right and wrap to new rows. This…

### Community 31 - "AsyncHttpSender"
Cohesion: 0.16
Nodes (6): ResultCallback, AsyncHttpSender, _schedule(), Schedule a request; ``callback`` is invoked on the sender thread. Returns a…, Owns a background event loop running httpx.AsyncClient instances., Networking helpers (async HTTP client for Repeater/Intruder).

### Community 32 - "._open_or_recover"
Cohesion: 0.29
Nodes (4): Connection, Path, Move the corrupt database and SQLite sidecars to a safe backup., Open and validate the database, recovering from SQLite corruption. A damaged…

### Community 33 - "QMenu"
Cohesion: 0.14
Nodes (6): QMenu, Install (or clear) the dropdown's group-send options. ``actions`` is a list of…, Record which send mode the split button runs, and show it on the button., Grey out the dropdown's options when there is no request to send., Ask the provider for a payload and insert it at the cursor., Build a FlowRecord from the current (edited) request text.

### Community 34 - "iter_jobs"
Cohesion: 0.19
Nodes (11): find_markers(), iter_jobs(), Marker, Insert ``values`` into ``clean_text`` at each marker (right-to-left). Working…, Yield an :class:`AttackJob` per request for the configured attack.…, A payload position: the span between a pair of ``§`` markers. ``start``/``end``…, Split a ``§``-marked template into (clean_text, markers). Markers come in…, _splice() (+3 more)

### Community 35 - "GroupDialog"
Cohesion: 0.09
Nodes (17): QColor, QSyntaxHighlighter, QTextCharFormat, GroupDialog, QDialog, Dialog for adding Repeater request tabs to a named, colored group. Presents a…, Collect a group name, member tabs, and a color., _fmt() (+9 more)

### Community 36 - "BodyStore"
Cohesion: 0.15
Nodes (8): BodyStore, Path, On-disk store for large request/response bodies. Rather than storing large…, Content-addressed file store for body payloads. Files are sharded into…, Write ``data`` to the store and return its relative path. Identical content…, Read body content previously returned by :meth:`store`., Storage layer: SQLite persistence + on-disk body store., SQLite persistence for captured flows. Uses the stdlib ``sqlite3`` module…

### Community 37 - "WrappingTabBar"
Cohesion: 0.07
Nodes (20): QMouseEvent, QResizeEvent, QScrollArea, AsyncHttpSender, current_mode(), Return the named color tokens for ``mode`` (falls back to dark)., Return the theme mode currently applied to the application., tokens() (+12 more)

### Community 38 - "RepeaterTab"
Cohesion: 0.11
Nodes (13): FlowRecord, QWidget, Clone a session's request into a new tab, named ``base (n)``., Return ``base (n)`` with the smallest unused positive integer n., Delete a group along with all request tabs it contains., Close every request tab and remove all groups. Always leaves one fresh, empty…, Guarantee at least one (empty) session exists. Called on startup after…, Open a new session tab populated from a captured flow. If the only open session… (+5 more)

### Community 39 - "Storage Layer (storage/)"
Cohesion: 0.18
Nodes (11): Body Store (file-backed bodies), Capture Addon, Decode Bodies with content not raw_content, FlowRecord Plain Dataclass, asyncio.Event Pause/Forward/Drop, Architecture Layering Invariant, Design rules, Content-Addressed Body Storage (+3 more)

### Community 40 - "ProxyTab"
Cohesion: 0.07
Nodes (18): QPushButton, CaCertDialog, Path, QDialog, Dialog for exporting and installing the proxy's CA certificate. To intercept…, Shows CA status, an export button, and install instructions., ProxyTab, QWidget (+10 more)

### Community 41 - ".restore_state"
Cohesion: 0.18
Nodes (4): Path, Best-effort correlate an interaction back to a generated payload., Persist the session, generated payloads, and interactions to JSON., Restore a session saved by :meth:`save_state` and re-register it.

### Community 42 - "intercept_response_live_test.py"
Cohesion: 0.31
Nodes (7): check_done(), do_forward(), finish(), on_intercepted(), on_started(), Live: intercept a request via the real MainWindow, forward it, and confirm the…, send()

### Community 43 - "repeater_tab.py"
Cohesion: 0.20
Nodes (8): HistoryEntry, A single Repeater session: one editable request + its response. Bundles the…, A request that was sent and (optionally) the response it produced., Serializable snapshot of a session (for persistence)., SessionState, Group, Repeater tab: a container of independent request/response sessions. Each "Send…, A named, colored, collapsible collection of member sessions.

### Community 44 - "intercept_view.py"
Cohesion: 0.20
Nodes (5): Intercept panel: pause, edit, and forward/drop in-flight requests. When…, hex_dump(), Raw HTTP message viewer/editor (headers + body) with highlighting. Soft wrap is…, Switch how the remembered body is rendered and re-display it., Return a classic offset / hex / ASCII hex dump of ``data``.

### Community 45 - "intercept_live_test.py"
Cohesion: 0.36
Nodes (6): finish(), on_captured(), on_intercepted(), on_started(), Live test: interception pauses a request, and forward/drop resolve it.…, send()

### Community 46 - "InteractionFilterProxy"
Cohesion: 0.24
Nodes (5): CollaboratorConfig, Settings for the Collaborator (out-of-band interaction) feature. Attributes:…, InteractionFilterProxy, QSortFilterProxyModel, Filter interactions by protocol and a free-text needle.

### Community 47 - "_LineNumberArea"
Cohesion: 0.29
Nodes (4): _LineNumberArea, QSize, QWidget, Gutter widget that paints line numbers for its owning MessageView.

### Community 48 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 49 - "SendHandle"
Cohesion: 0.25
Nodes (4): AbstractEventLoop, A cancellable handle to an in-flight request. The handle wraps the…, SendHandle, Task

### Community 50 - "Bidoytu"
Cohesion: 0.14
Nodes (14): Bidoytu Banner Logo, Bidoytu Circular Icon Logo, Architecture, Bidoytu, Development workflow, Highlights, License, Packaging and releases (+6 more)

### Community 51 - "config.py"
Cohesion: 0.13
Nodes (13): on_started(), Verify the capture addon stores DECODED bodies (gzip is undone). Routes a…, Verify starting the proxy on an occupied port produces a clean error signal…, host_matches_scope(), matches(), _normalise_scope_entry(), ProxyConfig, Application configuration and filesystem paths. Everything the app writes… (+5 more)

### Community 53 - "CLAUDE.md"
Cohesion: 0.20
Nodes (8): Architecture and layering (respect this), Conventions, Git workflow, Gotchas learned the hard way, Tech stack, Verifying changes (always do this), What Bidoytu is, Where things live

### Community 54 - "UI Layer (ui/)"
Cohesion: 0.25
Nodes (8): QPlainTextEdit + QSyntaxHighlighter Editor, Headless Smoke Test, Default 127.0.0.1 Bind, PySide6, Qt Isolation to ui/, UI Layer (ui/), PySide6 Dependency, Safe Default Localhost Bind

### Community 55 - "Building and releasing Bidoytu"
Cohesion: 0.20
Nodes (9): Build (Windows or Linux), Building and releasing Bidoytu, Cutting version 1.0.0, How releases work (CI/CD), Local builds (optional), Notes, Nuitka (alternative compiler), Prerequisites (+1 more)

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
Cohesion: 0.29
Nodes (8): Staging-First Git Workflow, PyInstaller Build Step, Release CI/CD Workflow, Rolling latest Pre-Release, Versioned v* Tag Release, Nuitka Alternative Compiler, Desktop App Packaging, Qt Module Excludes (size reduction)

### Community 62 - "proxy_live_test.py"
Cohesion: 0.33
Nodes (3): on_started(), Live end-to-end test: start the ProxyEngine thread and route a real request…, send_request()

### Community 63 - "WorkspaceManager"
Cohesion: 0.10
Nodes (17): QDialog, Startup picker for local Bidoytu workspaces., Choose, create, import, or export local workspaces before app startup., WorkspaceDialog, _now(), Path, Local, Burp-style workspace management. Each workspace owns its SQLite history,…, Remove every deletable workspace while keeping the legacy recovery one. (+9 more)

### Community 65 - "Contributing to Bidoytu"
Cohesion: 0.29
Nodes (6): Branches and pull requests, Checks, Contributing to Bidoytu, License, Local setup, Security issues

### Community 67 - "http_utils.py"
Cohesion: 0.15
Nodes (14): absolute_url(), build_request_text(), build_response_text(), ensure_host_header(), _headers_have(), parse_response_text(), ParsedResponse, Helpers for converting between raw HTTP text and structured parts. Used by… (+6 more)

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

### Community 92 - "ca_export_test.py"
Cohesion: 0.67
Nodes (3): finish(), poll_for_ca(), Verify the CA is generated in Bidoytu's confdir and can be exported. Starts the…

## Ambiguous Edges - Review These
- `Qt Isolation to ui/` → `Safe Default Localhost Bind`  [AMBIGUOUS]
  SECURITY.md · relation: conceptually_related_to
- `Public CA Certificate Export` → `CA Certificate Handling Policy`  [AMBIGUOUS]
  SECURITY.md · relation: references

## Knowledge Gaps
- **96 isolated node(s):** `Usage`, `What graphify is for`, `Step 0 - GitHub repos and multi-path merge (only if a URL or several paths)`, `Step 1 - Ensure graphify is installed`, `Step 2 - Detect files` (+91 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 582 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **19 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Qt Isolation to ui/` and `Safe Default Localhost Bind`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Public CA Certificate Export` and `CA Certificate Handling Policy`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **Why does `FlowRecord` connect `FlowRecord` to `InterceptView`, `BodyStore`, `HistoryView`, `IntruderSession`, `InterceptActivityModel`, `intruder_session.py`, `ProxyEngine`, `CaptureAddon`, `intercept_view.py`, `config.py`, `IntruderTab`, `models.py`, `FlowTableModel`, `smoke_test.py`, `.cookies`, `AsyncHttpSender`?**
  _High betweenness centrality (0.134) - this node is a cross-community bridge._
- **Why does `RepeaterTab` connect `RepeaterTab` to `theme.py`, `WrappingTabBar`, `._update_group_send_menu`, `RepeaterSession`, `repeater_tab.py`, `MainWindow`?**
  _High betweenness centrality (0.084) - this node is a cross-community bridge._
- **Why does `CollaboratorTab` connect `CollaboratorTab` to `MessageView`, `InteractshClient`, `.restore_state`, `InteractionFilterProxy`, `MainWindow`, `FindBar`, `collaborator_tab.py`, `InteractionsModel`, `AsyncHttpSender`?**
  _High betweenness centrality (0.083) - this node is a cross-community bridge._
- **Are the 13 inferred relationships involving `FlowRecord` (e.g. with `CaptureAddon` and `ProxyEngine`) actually correct?**
  _`FlowRecord` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `IntruderSession` (e.g. with `AsyncHttpSender` and `FlowRecord`) actually correct?**
  _`IntruderSession` has 15 INFERRED edges - model-reasoned connections that need verification._
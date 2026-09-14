# Graph Report - Bidoytu  (2026-09-14)

## Corpus Check
- 73 files · ~138,604 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 6 file(s) not represented in the graph (top: (none) 4, .spec 1, .ico 1)

## Summary
- 1262 nodes · 2419 edges · 92 communities (71 shown, 20 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 182 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `1351a4d4`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- IntruderSession
- InterceptView
- CollaboratorTab
- InterceptActivityModel
- repeater_session.py
- CaptureAddon
- intruder_session.py
- InteractshClient
- app.py
- IntruderResultsModel
- MessageView
- MainWindow
- ProxyEngine
- HistoryView
- AsyncHttpSender
- FlowRecord
- What You Must Do When Invoked
- IntruderTab
- parse_request_text
- body_format.py
- FlowLayout
- theme.py
- main_window.py
- RepeaterTab
- _HTMLPretty
- PayloadSetEditor
- interactsh.py
- InteractionsModel
- AttackRunner
- FlowTableModel
- iter_jobs
- SendHandle
- collaborator_tab.py
- strip_markers
- AppConfig
- _Chip
- ._deregister
- QMenu
- WrappingTabBar
- Storage Layer (storage/)
- ProxyTab
- ._open_or_recover
- Release CI/CD Workflow
- smoke_test.py
- .cookies
- HttpResult
- ProxyEngine (QThread)
- intercept_response_live_test.py
- graphify reference: extra exports and benchmark
- BodyStore
- ._set_has_request
- ._duplicate_session
- _GroupHeaderChip
- graphify reference: query, path, explain
- Bidoytu
- Public CA Certificate Export
- config.py
- intercept_live_test.py
- InteractionFilterProxy
- .restore_state
- wrapping_tab_bar.py
- InteractshError
- ._update_group_send_menu
- httpx Async Client
- logo_path
- proxy_live_test.py
- Path
- gzip_decode_test.py
- .mousePressEvent
- start_proxy_repro.py
- Qt Isolation to ui/
- RepeaterSession
- Display vs. Wire Invariant
- ui/__init__.py
- Contributors Acknowledgement
- bidoytu
- http_utils Raw HTTP Parsing
- Private Vulnerability Reporting
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native CLAUDE.md integration
- graphify reference: incremental update and cluster-only
- graphify reference: GitHub clone and cross-repo merge
- graphify reference: transcribe video and audio
- AGENTS.md
- extraction-spec.md
- ._restore_attack
- .restore_sessions
- MarkerHighlighter
- ._show_raw
- wrap_selection
- .is_empty

## God Nodes (most connected - your core abstractions)
1. `FlowRecord` - 83 edges
2. `RepeaterSession` - 65 edges
3. `IntruderSession` - 60 edges
4. `CollaboratorTab` - 50 edges
5. `MainWindow` - 46 edges
6. `MessageView` - 45 edges
7. `InterceptView` - 41 edges
8. `RepeaterTab` - 41 edges
9. `AsyncHttpSender` - 34 edges
10. `InterceptActivityModel` - 29 edges

## Surprising Connections (you probably didn't know these)
- `Bundled App Icon Asset` --conceptually_related_to--> `UI Layer (ui/)`  [INFERRED]
  src/bidoytu/assets/logo.png → README.md
- `Contributor Design Rules` --semantically_similar_to--> `Architecture Layering Invariant`  [INFERRED] [semantically similar]
  CONTRIBUTING.md → CLAUDE.md
- `Bidoytu Banner Logo` --references--> `Bidoytu`  [EXTRACTED]
  bidoytu-long.png → README.md
- `Bidoytu Circular Icon Logo` --references--> `Bidoytu`  [INFERRED]
  logo.png → README.md
- `Bidoytu Banner Logo` --semantically_similar_to--> `Bidoytu Circular Icon Logo`  [INFERRED] [semantically similar]
  bidoytu-long.png → logo.png

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Cross-Thread Flow Pipeline** — claude_proxy_engine, claude_flowrecord, claude_qt_signals, claude_async_sender [INFERRED 0.75]
- **CA Security Invariants** — security_public_only_export, claude_ca_private_key_protection, readme_ca_export [INFERRED 0.85]
- **Framework-Free Core Layers (proxy/net/storage)** — readme_proxy_layer, readme_net_layer, readme_storage_layer [INFERRED 0.85]

## Communities (92 total, 20 thin omitted)

### Community 0 - "IntruderSession"
Cohesion: 0.11
Nodes (5): IntruderSession, Slot, Return a JSON-serializable snapshot of this session., Build a FlowRecord from the template (payload markers removed)., One Intruder attack: template + positions + payload sets + results.

### Community 1 - "InterceptView"
Cohesion: 0.07
Nodes (19): InterceptView, QWidget, Size the activity table so URL fills the leftover width, while every column…, Whenever a column is resized, compensate its immediate right neighbor (or left…, Reflow the URL column to absorb the viewport's leftover width. URL is the…, Forward every still-pending flow, then reset the panel. Called when…, A request was paused by the proxy; add it to the table., A response was paused by the proxy; add it to the table. (+11 more)

### Community 2 - "CollaboratorTab"
Cohesion: 0.14
Nodes (6): CollaboratorTab, QWidget, Build a titled pane (label + find bar + view), matching Repeater., Attach a note (e.g. the target tab) to the most recent payload., Generate a payload, tag it with ``note``, and return the hostname. Used by…, Register with an Interactsh server, hand out payloads, show callbacks.

### Community 3 - "InterceptActivityModel"
Cohesion: 0.08
Nodes (14): ActivityRow, InterceptActivityModel, Orientation, QAbstractTableModel, QModelIndex, Log a paused (pending) request. Returns its row index., Log a paused (pending) response. Returns its row index., True if the row is a still-pending request or response. (+6 more)

### Community 4 - "repeater_session.py"
Cohesion: 0.10
Nodes (19): absolute_url(), build_request_text(), build_response_text(), ensure_host_header(), _headers_have(), parse_response_text(), ParsedRequest, ParsedResponse (+11 more)

### Community 5 - "CaptureAddon"
Cohesion: 0.11
Nodes (14): FlowCallback, HTTPFlow, InterceptCallback, CaptureAddon, _PendingFlow, Apply a UI decision to a paused response. Runs on the proxy loop., Rewrite a flow's request from edited raw text before forwarding., Rewrite a flow's response from edited raw text before forwarding. (+6 more)

### Community 6 - "intruder_session.py"
Cohesion: 0.15
Nodes (23): count_jobs(), PayloadSet, Intruder attack model: markers, attack types, and request building. Qt-free so…, Best-effort total request count for a configured attack., A generator plus its processing rules (one Intruder payload set)., _apply_one(), apply_rules(), _brute() (+15 more)

### Community 7 - "InteractshClient"
Cohesion: 0.15
Nodes (7): InteractshClient, _cb(), _cb(), Register with, generate payloads for, and poll an Interactsh server. The client…, Generate a keypair and register against the first working server. ``servers``…, Poll the server once. ``on_done(interactions, error)`` on sender thread., Deregister from the server. Best-effort; failures are ignored.

### Community 8 - "app.py"
Cohesion: 0.24
Nodes (8): main(), Application entry point. Creates the Qt application, builds the main window,…, Give Windows an explicit AppUserModelID so the taskbar uses our icon. Without…, _set_windows_app_id(), Bidoytu - an intercepting HTTP proxy tool. Base architecture: - Proxy/MITM…, Enables ``python -m bidoytu``., load_theme(), Return the persisted theme, defaulting to dark.

### Community 9 - "IntruderResultsModel"
Cohesion: 0.11
Nodes (10): One completed request in the results table., ResultRow, IntruderResultsModel, QAbstractTableModel, QModelIndex, QSortFilterProxyModel, Table model + filter proxy for Intruder attack results.…, Filter results by status, min length, matched-only, and a text needle. (+2 more)

### Community 10 - "MessageView"
Cohesion: 0.08
Nodes (14): hex_dump(), _LineNumberArea, MessageView, QPlainTextEdit, QRect, QSize, QWidget, Switch how the remembered body is rendered and re-display it. (+6 more)

### Community 11 - "MainWindow"
Cohesion: 0.08
Nodes (13): QMainWindow, CaCertDialog, Path, QDialog, Dialog for exporting and installing the proxy's CA certificate. To intercept…, Shows CA status, an export button, and install instructions., MainWindow, Slot (+5 more)

### Community 12 - "ProxyEngine"
Cohesion: 0.07
Nodes (14): QThread, ProxyConfig, Listen settings for the mitmproxy engine., ProxyEngine, Runs mitmproxy inside a dedicated QThread. Design: - mitmproxy is asyncio-…, Toggle the global 'intercept responses' behavior., Arm a one-shot response intercept for a single flow., Forward a paused request, optionally with edited raw request text. (+6 more)

### Community 13 - "HistoryView"
Cohesion: 0.09
Nodes (13): QStyledItemDelegate, DetailView, QWidget, Two MessageViews (request | response) with a shared soft-wrap toggle., HistoryItemDelegate, Fully self-painted cells: soft row wash + slim accent bar, no style frame., HistoryView, QWidget (+5 more)

### Community 14 - "AsyncHttpSender"
Cohesion: 0.15
Nodes (9): Pattern, host_from_headers_or_url(), Determine (scheme, host, port, path) for sending a parsed request. Prefers an…, AsyncHttpSender, Async HTTP sender for Repeater/Intruder. Runs an ``httpx.AsyncClient`` on a…, Owns a background event loop running httpx.AsyncClient instances., Networking helpers (async HTTP client for Repeater/Intruder)., _compile() (+1 more)

### Community 15 - "FlowRecord"
Cohesion: 0.14
Nodes (10): Row, FlowRecord, A single captured HTTP request/response exchange. Body payloads are represented…, The response content type without parameters (e.g. ``text/html``)., File extension derived from the request path (without the dot). The query…, FlowRepository, Insert a new flow and return its assigned primary key., Update an existing flow (matched by ``flow_id``). (+2 more)

### Community 16 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 17 - "IntruderTab"
Cohesion: 0.15
Nodes (8): IntruderTab, Path, QWidget, Close every Intruder tab., Open a new session tab populated from a captured flow., Write every open session to ``path`` as JSON (list of snapshots)., Recreate the sessions saved by :meth:`save_state`. Accepts both the multi-…, Holds multiple :class:`IntruderSession` instances in a tab strip.

### Community 18 - "parse_request_text"
Cohesion: 0.33
Nodes (4): parse_request_text(), Parse raw HTTP request text into a :class:`ParsedRequest`. Tolerant of both…, mitmproxy addon: maps flows to FlowRecords and supports interception. Two…, Build a FlowRecord from the (possibly edited) request in the editor. Uses the…

### Community 19 - "body_format.py"
Cohesion: 0.18
Nodes (16): format_body(), _format_c_like(), _format_css(), _format_form(), _format_html(), _format_js(), _format_json(), _format_xml() (+8 more)

### Community 20 - "FlowLayout"
Cohesion: 0.15
Nodes (7): Orientations, QLayout, QLayoutItem, FlowLayout, QRect, QSize, QWidget

### Community 21 - "theme.py"
Cohesion: 0.06
Nodes (45): QColor, QPalette, QPixmap, QProxyStyle, QSyntaxHighlighter, QTextCharFormat, _fmt(), HttpHighlighter (+37 more)

### Community 22 - "main_window.py"
Cohesion: 0.11
Nodes (13): Live test: RepeaterTab.load_from_record + Send performs a real request., On-disk store for large request/response bodies. Rather than storing large…, Storage layer: SQLite persistence + on-disk body store., Plain data structures passed between the proxy engine, storage, and UI. These…, SQLite persistence for captured flows. Uses the stdlib ``sqlite3`` module…, Custom QAbstractTableModel backing the traffic history view. We use a hand-…, HTTP history: the traffic table plus a request/response detail view. Emits a…, Table model for the Intercept tab's activity log. Each intercepted request… (+5 more)

### Community 23 - "RepeaterTab"
Cohesion: 0.16
Nodes (8): QWidget, Delete a group along with all request tabs it contains., Close every request tab and remove all groups. Always leaves one fresh, empty…, Guarantee at least one (empty) session exists. Called on startup after…, Open a new session tab populated from a captured flow. If the only open session…, Return the sole session iff it is a single, empty, ungrouped tab., Holds multiple :class:`RepeaterSession` instances with a wrapping bar., RepeaterTab

### Community 24 - "_HTMLPretty"
Cohesion: 0.22
Nodes (4): HTMLParser, _HTMLPretty, Lenient HTML pretty-printer built on the stdlib parser. Emits nicely indented…, Close a preceding sibling with an optional end tag, if applicable.

### Community 25 - "PayloadSetEditor"
Cohesion: 0.15
Nodes (6): PayloadSetEditor, ProcessingRuleDialog, QDialog, QWidget, Edit one payload set: a generator plus a processing-rule pipeline., Configure a single :class:`ProcessingRule`.

### Community 26 - "interactsh.py"
Cohesion: 0.29
Nodes (6): _encode_xid(), generate_xid(), _now_iso(), Interactsh (OAST) client for the Collaborator feature. This is a small, Qt-free…, Return a 20-char XID string. XID layout: 4-byte time, 3-byte machine id, 2-byte…, Encode 12 raw bytes into the 20-char XID base32 representation.

### Community 27 - "InteractionsModel"
Cohesion: 0.14
Nodes (12): Interaction, A single out-of-band interaction reported by the server., InteractionRow, InteractionsModel, protocol_color(), QAbstractTableModel, QModelIndex, Table model + filter proxy for Collaborator (OAST) interactions.… (+4 more)

### Community 28 - "AttackRunner"
Cohesion: 0.20
Nodes (7): QObject, AttackJob, One request to send: the substituted text and the payloads used., AttackRunner, Slot, Launch requests until we hit the concurrency cap or run out., Runs one attack, emitting a :class:`ResultRow` per completed request.

### Community 29 - "FlowTableModel"
Cohesion: 0.17
Nodes (6): FlowTableModel, Orientation, QAbstractTableModel, QModelIndex, Replace all rows (e.g. when loading history from the database)., Add a new record, or update an existing one in place. Called from the UI thread…

### Community 30 - "iter_jobs"
Cohesion: 0.19
Nodes (11): find_markers(), iter_jobs(), Marker, Insert ``values`` into ``clean_text`` at each marker (right-to-left). Working…, Yield an :class:`AttackJob` per request for the configured attack.…, A payload position: the span between a pair of ``§`` markers. ``start``/``end``…, Split a ``§``-marked template into (clean_text, markers). Markers come in…, _splice() (+3 more)

### Community 31 - "SendHandle"
Cohesion: 0.25
Nodes (4): AbstractEventLoop, A cancellable handle to an in-flight request. The handle wraps the…, SendHandle, Task

### Community 32 - "collaborator_tab.py"
Cohesion: 0.18
Nodes (8): FindFlags, QKeyEvent, Collaborator tab: out-of-band (OAST) interaction listener. Bidoytu's equivalent…, FindBar, QWidget, A small find bar that searches within a QPlainTextEdit. Reusable over any…, Incremental find controls bound to a target text edit., Reveal the bar, seed it with any selected text, and focus input.

### Community 33 - "strip_markers"
Cohesion: 0.33
Nodes (3): Return the template with all ``§`` markers removed (defaults kept)., strip_markers(), Wrap each ``name=value`` value (query + body) in markers.

### Community 34 - "AppConfig"
Cohesion: 0.15
Nodes (10): AppConfig, Path, JSON file holding Collaborator session state across restarts. Stores the active…, Directory where mitmproxy stores its generated CA and certs. We keep it under…, PEM-encoded CA certificate (for Firefox, curl, most Linux tools)., DER/.cer CA certificate (convenient for the Windows cert store)., Create the data, body, and CA directories if they do not exist., Top-level runtime configuration. Attributes: data_dir: Root directory for all… (+2 more)

### Community 35 - "_Chip"
Cohesion: 0.21
Nodes (6): current_mode(), Return the named color tokens for ``mode`` (falls back to dark)., Return the theme mode currently applied to the application., tokens(), _Chip, A single clickable tab chip with an optional close button.

### Community 37 - "QMenu"
Cohesion: 0.14
Nodes (6): QMenu, Install (or clear) the dropdown's group-send options. ``actions`` is a list of…, Record which send mode the split button runs, and show it on the button., Grey out the dropdown's options when there is no request to send., Ask the provider for a payload and insert it at the cursor., Build a FlowRecord from the current (edited) request text.

### Community 38 - "WrappingTabBar"
Cohesion: 0.21
Nodes (6): QResizeEvent, QScrollArea, Group-aware, wrapping tab bar composed of chip widgets., Rebuild the whole bar from the container's model. Args: order: list of keys…, Grow the bar to fit its rows, capped at ``_max_rows`` (then scroll)., WrappingTabBar

### Community 39 - "Storage Layer (storage/)"
Cohesion: 0.18
Nodes (11): Body Store (file-backed bodies), Capture Addon, Decode Bodies with content not raw_content, FlowRecord Plain Dataclass, asyncio.Event Pause/Forward/Drop, Architecture Layering Invariant, Contributor Design Rules, Content-Addressed Body Storage (+3 more)

### Community 40 - "ProxyTab"
Cohesion: 0.08
Nodes (15): QHBoxLayout, QPushButton, QPlainTextEdit, GroupDialog, QDialog, Dialog for adding Repeater request tabs to a named, colored group. Presents a…, Collect a group name, member tabs, and a color., QWidget (+7 more)

### Community 41 - "._open_or_recover"
Cohesion: 0.29
Nodes (4): Connection, Path, Move the corrupt database and SQLite sidecars to a safe backup., Open and validate the database, recovering from SQLite corruption. A damaged…

### Community 42 - "Release CI/CD Workflow"
Cohesion: 0.22
Nodes (10): Staging-First Git Workflow, PyInstaller Build Step, Release CI/CD Workflow, Rolling latest Pre-Release, Versioned v* Tag Release, Nuitka Alternative Compiler, Desktop App Packaging, Qt Module Excludes (size reduction) (+2 more)

### Community 43 - "smoke_test.py"
Cohesion: 0.36
Nodes (10): QApplication, main(), Path, Import + wiring smoke test (no live proxy, no visible window). Verifies: - all…, test_body_format(), test_body_store(), test_http_utils(), test_intercept_view() (+2 more)

### Community 45 - "HttpResult"
Cohesion: 0.24
Nodes (5): ResultCallback, _schedule(), HttpResult, Schedule a request; ``callback`` is invoked on the sender thread. Returns a…, Return (ok, done). ``done`` short-circuits trying more servers.

### Community 46 - "ProxyEngine (QThread)"
Cohesion: 0.22
Nodes (9): loop.call_soon_threadsafe Into Proxy Loop, Port Availability Pre-check, ProxyEngine (QThread), Qt Signals Cross-Thread Results, SystemExit Errorcheck Catch, Threading Model, mitmproxy Engine, Proxy Layer (proxy/) (+1 more)

### Community 47 - "intercept_response_live_test.py"
Cohesion: 0.31
Nodes (7): check_done(), do_forward(), finish(), on_intercepted(), on_started(), Live: intercept a request via the real MainWindow, forward it, and confirm the…, send()

### Community 48 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 49 - "BodyStore"
Cohesion: 0.25
Nodes (5): BodyStore, Path, Content-addressed file store for body payloads. Files are sharded into…, Write ``data`` to the store and return its relative path. Identical content…, Read body content previously returned by :meth:`store`.

### Community 50 - "._set_has_request"
Cohesion: 0.25
Nodes (4): Enable/disable the Send action while keeping the button visible. We…, Paint the Send button with the disabled cue when it has no request. Uses a…, Serializable snapshot of a session (for persistence)., SessionState

### Community 53 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 54 - "Bidoytu"
Cohesion: 0.32
Nodes (8): Bidoytu Banner Logo, QPlainTextEdit + QSyntaxHighlighter Editor, Headless Smoke Test, Bidoytu Circular Icon Logo, Bidoytu, UI Layer (ui/), Responsible and Lawful Use, Bundled App Icon Asset

### Community 55 - "Public CA Certificate Export"
Cohesion: 0.36
Nodes (8): CA Private Key Protection, Focused Live Test Scripts, Public CA Certificate Export, Request Interception, cryptography Dependency, CA Certificate Handling Policy, Public-Only CA Export Invariant, Untrusted Captured Traffic

### Community 56 - "config.py"
Cohesion: 0.22
Nodes (7): finish(), poll_for_ca(), Verify the CA is generated in Bidoytu's confdir and can be exported. Starts the…, Verify starting the proxy on an occupied port produces a clean error signal…, _default_data_dir(), Application configuration and filesystem paths. Everything the app writes…, Return a per-user, per-OS data directory for Bidoytu.

### Community 57 - "intercept_live_test.py"
Cohesion: 0.36
Nodes (6): finish(), on_captured(), on_intercepted(), on_started(), Live test: interception pauses a request, and forward/drop resolve it.…, send()

### Community 58 - "InteractionFilterProxy"
Cohesion: 0.22
Nodes (5): CollaboratorConfig, Settings for the Collaborator (out-of-band interaction) feature. Attributes:…, InteractionFilterProxy, QSortFilterProxyModel, Filter interactions by protocol and a free-text needle.

### Community 59 - ".restore_state"
Cohesion: 0.20
Nodes (3): Slot, Best-effort correlate an interaction back to a generated payload., Restore a session saved by :meth:`save_state` and re-register it.

### Community 60 - "wrapping_tab_bar.py"
Cohesion: 0.25
Nodes (5): A wrapping flow layout: children flow left-to-right and wrap to new rows. This…, _FlowHost, QWidget, A wrapping, group-aware tab bar built from individual chip widgets. Unlike…, Host widget whose height tracks its FlowLayout's height-for-width. A…

### Community 61 - "InteractshError"
Cohesion: 0.17
Nodes (8): Exception, InteractshError, Everything needed to resume / persist a registered session., Raised for registration / polling / crypto failures., Restore a persisted session and re-register to keep it alive., Return a fresh unique payload hostname for this session. Format:…, SessionInfo, _session_from_dict()

### Community 63 - "httpx Async Client"
Cohesion: 0.40
Nodes (6): AsyncHttpSender, httpx Async Client, Intruder, Net Layer (net/), Repeater, httpx Dependency

### Community 64 - "logo_path"
Cohesion: 0.39
Nodes (7): asset_path(), _assets_dir(), logo_path(), Path, Locators for bundled resources (icons, images). Resources live under…, Return the absolute path to a bundled asset by file name., Absolute path to the application logo.

### Community 65 - "proxy_live_test.py"
Cohesion: 0.33
Nodes (3): on_started(), Live end-to-end test: start the ProxyEngine thread and route a real request…, send_request()

### Community 66 - "Path"
Cohesion: 0.38
Nodes (3): Path, Persist the session, generated payloads, and interactions to JSON., _session_to_dict()

### Community 69 - "start_proxy_repro.py"
Cohesion: 0.47
Nodes (4): after_start(), finish(), Reproduce the 'start proxy crashes' path using the real MainWindow. Builds the…, send()

### Community 70 - "Qt Isolation to ui/"
Cohesion: 0.67
Nodes (3): Default 127.0.0.1 Bind, Qt Isolation to ui/, Safe Default Localhost Bind

### Community 71 - "RepeaterSession"
Cohesion: 0.13
Nodes (7): HistoryEntry, Slot, Set the status/target label, eliding to fit the current width. Stores the full…, Public entry point for the container to send this tab's request., A request that was sent and (optionally) the response it produced., One request/response pane with full Repeater controls., RepeaterSession

### Community 78 - "graphify reference: add a URL and watch a folder"
Cohesion: 0.50
Nodes (3): For /graphify add, For --watch, graphify reference: add a URL and watch a folder

### Community 79 - "graphify reference: commit hook and native CLAUDE.md integration"
Cohesion: 0.50
Nodes (3): For git commit hook, For native CLAUDE.md integration, graphify reference: commit hook and native CLAUDE.md integration

### Community 80 - "graphify reference: incremental update and cluster-only"
Cohesion: 0.50
Nodes (3): For --cluster-only, For --update (incremental re-extraction), graphify reference: incremental update and cluster-only

### Community 87 - ".restore_sessions"
Cohesion: 0.29
Nodes (5): Group, Path, A named, colored, collapsible collection of member sessions., Write all open sessions and their groups to ``path`` as JSON., Recreate sessions and groups saved by :meth:`save_sessions`.

### Community 88 - "MarkerHighlighter"
Cohesion: 0.50
Nodes (3): MarkerHighlighter, Highlighter for the Intruder request template. A…, HTTP highlighting plus a highlighted background for ``§payload§`` spans.

### Community 89 - "._show_raw"
Cohesion: 0.50
Nodes (3): Render a raw HTTP message, pretty-printing its body by content-type. Splits…, Split a raw HTTP message into (start_line, headers, body). Tolerant of both…, _split_http_message()

## Ambiguous Edges - Review These
- `Public CA Certificate Export` → `CA Certificate Handling Policy`  [AMBIGUOUS]
  SECURITY.md · relation: references
- `Qt Isolation to ui/` → `Safe Default Localhost Bind`  [AMBIGUOUS]
  SECURITY.md · relation: conceptually_related_to

## Knowledge Gaps
- **61 isolated node(s):** `bidoytu`, `Usage`, `What graphify is for`, `Step 0 - GitHub repos and multi-path merge (only if a URL or several paths)`, `Step 1 - Ensure graphify is installed` (+56 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 503 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **20 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Public CA Certificate Export` and `CA Certificate Handling Policy`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **What is the exact relationship between `Qt Isolation to ui/` and `Safe Default Localhost Bind`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `FlowRecord` connect `FlowRecord` to `IntruderSession`, `InterceptView`, `InterceptActivityModel`, `repeater_session.py`, `CaptureAddon`, `intruder_session.py`, `MainWindow`, `ProxyEngine`, `HistoryView`, `IntruderTab`, `parse_request_text`, `main_window.py`, `RepeaterTab`, `FlowTableModel`, `QMenu`, `smoke_test.py`, `.cookies`, `HttpResult`, `RepeaterSession`?**
  _High betweenness centrality (0.208) - this node is a cross-community bridge._
- **Why does `MessageView` connect `MessageView` to `collaborator_tab.py`, `InterceptView`, `CollaboratorTab`, `IntruderSession`, `repeater_session.py`, `intruder_session.py`, `RepeaterSession`, `ProxyTab`, `MainWindow`, `HistoryView`, `body_format.py`, `theme.py`, `main_window.py`, `._show_raw`?**
  _High betweenness centrality (0.111) - this node is a cross-community bridge._
- **Why does `IntruderSession` connect `IntruderSession` to `collaborator_tab.py`, `strip_markers`, `intruder_session.py`, `ProxyTab`, `IntruderResultsModel`, `MessageView`, `AsyncHttpSender`, `FlowRecord`, `IntruderTab`, `._restore_attack`, `main_window.py`, `MarkerHighlighter`, `PayloadSetEditor`, `wrap_selection`, `AttackRunner`, `iter_jobs`?**
  _High betweenness centrality (0.104) - this node is a cross-community bridge._
- **Are the 17 inferred relationships involving `FlowRecord` (e.g. with `test_intercept_view()` and `test_qt_and_proxy_apis()`) actually correct?**
  _`FlowRecord` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `RepeaterSession` (e.g. with `AsyncHttpSender` and `HttpResult`) actually correct?**
  _`RepeaterSession` has 7 INFERRED edges - model-reasoned connections that need verification._
# Graph Report - Bidoytu  (2026-09-15)

## Corpus Check
- 77 files · ~145,619 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 6 file(s) not represented in the graph (top: (none) 4, .spec 1, .ico 1)

## Summary
- 1476 nodes · 2847 edges · 93 communities (75 shown, 17 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 230 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `343ece05`
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
- strip_markers
- What You Must Do When Invoked
- ProxyTab
- advanced_history.py
- AsyncHttpSender
- main_window.py
- repeater_session.py
- _HTMLPretty
- history_view.py
- InteractionsModel
- IntruderTab
- ._open_or_recover
- FlowTableModel
- iter_jobs
- PayloadSetEditor
- FlowLayout
- WrappingTabBar
- .__init__
- QMenu
- AttackRunner
- QColor
- FindBar
- ui_icon
- RepeaterTab
- Storage Layer (storage/)
- GroupDialog
- parse_response_text
- intercept_response_live_test.py
- FlowRecord
- intercept_live_test.py
- InteractionFilterProxy
- .cookies
- graphify reference: extra exports and benchmark
- QHBoxLayout
- Bidoytu
- HttpHighlighter
- BodyStore
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
- gzip_decode_test.py
- Contributing to Bidoytu
- ui/__init__.py
- ca_export_test.py
- bidoytu
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
- SessionState
- extraction-spec.md
- SendHandle
- ._update_group_send_menu
- _ScopeList
- config.py
- _NoFocusRectStyle
- CONTRIBUTORS.md
- MarkerHighlighter
- ._set_target_toggle_icon
- .__init__

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

## Communities (93 total, 17 thin omitted)

### Community 0 - "theme.py"
Cohesion: 0.13
Nodes (27): QPainter, QPalette, QPixmap, apply_theme(), _blank_pixmap(), _build_qss(), _check_icon(), _chevron_down_icon() (+19 more)

### Community 1 - "InterceptView"
Cohesion: 0.07
Nodes (20): InterceptView, QWidget, Size the activity table so URL fills the leftover width, while every column…, Whenever a column is resized, compensate its immediate right neighbor (or left…, Reflow the URL column to absorb the viewport's leftover width. URL is the…, Forward every still-pending flow, then reset the panel. Called when…, A request was paused by the proxy; add it to the table., A response was paused by the proxy; add it to the table. (+12 more)

### Community 2 - "MessageView"
Cohesion: 0.06
Nodes (17): DetailView, QWidget, Two MessageViews (request | response) with a shared soft-wrap toggle., hex_dump(), _LineNumberArea, MessageView, QPlainTextEdit, QRect (+9 more)

### Community 3 - "CollaboratorTab"
Cohesion: 0.06
Nodes (18): CollaboratorConfig, Settings for the Collaborator (out-of-band interaction) feature. Attributes:…, CollaboratorTab, Path, QWidget, Slot, Build a titled pane (label + find bar + view), matching Repeater., Best-effort correlate an interaction back to a generated payload. (+10 more)

### Community 4 - "HistoryView"
Cohesion: 0.12
Nodes (7): HistoryView, QWidget, Slot, Whenever a column is resized, compensate its immediate right neighbor (or left…, Reflow the Path column to absorb the viewport's leftover width. Path is the…, Populate the saved-filter picker without coupling the widget to SQLite., Traffic table + detail, with send-to context actions.

### Community 5 - "AppConfig"
Cohesion: 0.10
Nodes (15): AppConfig, _default_data_dir(), Path, Top-level runtime configuration. Attributes: data_dir: Root directory for all…, JSON file holding persisted Repeater sessions across restarts., Return a per-user, per-OS data directory for Bidoytu., JSON file holding the last Intruder attack config across restarts., JSON file holding the Target scope for this workspace. (+7 more)

### Community 6 - "IntruderSession"
Cohesion: 0.08
Nodes (9): QComboBox, IntruderSession, QWidget, Slot, Grow/shrink the payload-set tabs to exactly ``n`` (min 1)., Return a JSON-serializable snapshot of this session., Restore this session from a snapshot produced by :meth:`to_state`., Build a FlowRecord from the template (payload markers removed). (+1 more)

### Community 7 - "InterceptActivityModel"
Cohesion: 0.08
Nodes (14): ActivityRow, InterceptActivityModel, Orientation, QAbstractTableModel, QModelIndex, Log a paused (pending) request. Returns its row index., Log a paused (pending) response. Returns its row index., True if the row is a still-pending request or response. (+6 more)

### Community 8 - "intruder_session.py"
Cohesion: 0.13
Nodes (25): count_jobs(), PayloadSet, Intruder attack model: markers, attack types, and request building. Qt-free so…, Wrap the ``[sel_start, sel_end)`` span of ``text`` in ``§`` markers. Used by…, Best-effort total request count for a configured attack., A generator plus its processing rules (one Intruder payload set)., wrap_selection(), _apply_one() (+17 more)

### Community 9 - "InteractshClient"
Cohesion: 0.10
Nodes (13): Exception, InteractshClient, _cb(), _cb(), InteractshError, Raised for registration / polling / crypto failures., Register with, generate payloads for, and poll an Interactsh server. The client…, Generate a keypair and register against the first working server. ``servers``… (+5 more)

### Community 10 - "RepeaterSession"
Cohesion: 0.11
Nodes (8): Slot, Set the status/target label, eliding to fit the current width. Stores the full…, True if this is a pristine session: no request text and no history., Enable/disable the Send action while keeping the button visible. We…, Paint the Send button with the disabled cue when it has no request. Uses a…, Public entry point for the container to send this tab's request., One request/response pane with full Repeater controls., RepeaterSession

### Community 11 - "IntruderResultsModel"
Cohesion: 0.11
Nodes (10): One completed request in the results table., ResultRow, IntruderResultsModel, QAbstractTableModel, QModelIndex, QSortFilterProxyModel, Table model + filter proxy for Intruder attack results.…, Filter results by status, min length, matched-only, and a text needle. (+2 more)

### Community 12 - "ProxyEngine"
Cohesion: 0.08
Nodes (11): QThread, ProxyEngine, Update target scope immediately, including while the proxy runs., Toggle the global 'intercept responses' behavior., Arm a one-shot response intercept for a single flow., Forward a paused request, optionally with edited raw request text., Drop a paused request., Forward a paused response, optionally with edited raw response text. (+3 more)

### Community 13 - "CaptureAddon"
Cohesion: 0.12
Nodes (13): HTTPFlow, CaptureAddon, _PendingFlow, Arm a one-shot response intercept for a single flow (Burp's "Response to this…, Apply a UI decision to a paused request. Runs on the proxy loop., Apply a UI decision to a paused response. Runs on the proxy loop., Rewrite a flow's request from edited raw text before forwarding., Rewrite a flow's response from edited raw text before forwarding. (+5 more)

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
Cohesion: 0.14
Nodes (5): ProxyTab, Container widget for everything under the top-level "Proxy" tab., The Clear History button now lives in the Intercept control row. Exposed here…, First click arms the button; a second click within 3s confirms. This guards…, Surface a detailed transient message (e.g. "Starting...", errors) on the…

### Community 18 - "advanced_history.py"
Cohesion: 0.20
Nodes (17): _body(), _compare(), curl_command(), export_records(), _field(), fingerprint(), _headers(), matches() (+9 more)

### Community 19 - "AsyncHttpSender"
Cohesion: 0.16
Nodes (6): ResultCallback, AsyncHttpSender, _schedule(), Schedule a request; ``callback`` is invoked on the sender thread. Returns a…, Owns a background event loop running httpx.AsyncClient instances., Networking helpers (async HTTP client for Repeater/Intruder).

### Community 20 - "main_window.py"
Cohesion: 0.12
Nodes (15): Live test: RepeaterTab.load_from_record + Send performs a real request., Async HTTP sender for Repeater/Intruder. Runs an ``httpx.AsyncClient`` on a…, _encode_xid(), generate_xid(), Interactsh (OAST) client for the Collaborator feature. This is a small, Qt-free…, Everything needed to resume / persist a registered session., Return a 20-char XID string. XID layout: 4-byte time, 3-byte machine id, 2-byte…, Encode 12 raw bytes into the 20-char XID base32 representation. (+7 more)

### Community 21 - "repeater_session.py"
Cohesion: 0.05
Nodes (52): QApplication, main(), Path, Import + wiring smoke test (no live proxy, no visible window). Verifies: - all…, test_body_format(), test_body_store(), test_http_utils(), test_intercept_view() (+44 more)

### Community 22 - "_HTMLPretty"
Cohesion: 0.22
Nodes (4): HTMLParser, _HTMLPretty, Lenient HTML pretty-printer built on the stdlib parser. Emits nicely indented…, Close a preceding sibling with an optional end tag, if applicable.

### Community 23 - "history_view.py"
Cohesion: 0.12
Nodes (14): QGroupBox, QScrollArea, deserialize_filter_spec(), FilterSpec, Persist the complete filter state in the saved-filter query column., Load a saved filter, accepting legacy plain HTTPQL values., serialize_filter_spec(), Custom QAbstractTableModel backing the traffic history view. We use a hand-… (+6 more)

### Community 24 - "InteractionsModel"
Cohesion: 0.12
Nodes (12): Interaction, _now_iso(), A single out-of-band interaction reported by the server., InteractionRow, InteractionsModel, protocol_color(), QAbstractTableModel, QModelIndex (+4 more)

### Community 25 - "IntruderTab"
Cohesion: 0.15
Nodes (8): IntruderTab, Path, QWidget, Close every Intruder tab., Open a new session tab populated from a captured flow., Write every open session to ``path`` as JSON (list of snapshots)., Recreate the sessions saved by :meth:`save_state`. Accepts both the multi-…, Holds multiple :class:`IntruderSession` instances in a tab strip.

### Community 26 - "._open_or_recover"
Cohesion: 0.29
Nodes (4): Connection, Path, Move the corrupt database and SQLite sidecars to a safe backup., Open and validate the database, recovering from SQLite corruption. A damaged…

### Community 27 - "FlowTableModel"
Cohesion: 0.11
Nodes (8): SortOrder, FlowTableModel, Orientation, QAbstractTableModel, QModelIndex, Replace all rows (e.g. when loading history from the database)., Sort the source rows while keeping the active History filter applied., Add a new record, or update an existing one in place. Called from the UI thread…

### Community 28 - "iter_jobs"
Cohesion: 0.19
Nodes (11): find_markers(), iter_jobs(), Marker, Insert ``values`` into ``clean_text`` at each marker (right-to-left). Working…, Yield an :class:`AttackJob` per request for the configured attack.…, A payload position: the span between a pair of ``§`` markers. ``start``/``end``…, Split a ``§``-marked template into (clean_text, markers). Markers come in…, _splice() (+3 more)

### Community 29 - "PayloadSetEditor"
Cohesion: 0.15
Nodes (6): PayloadSetEditor, ProcessingRuleDialog, QDialog, QWidget, Edit one payload set: a generator plus a processing-rule pipeline., Configure a single :class:`ProcessingRule`.

### Community 30 - "FlowLayout"
Cohesion: 0.13
Nodes (8): Orientations, QLayout, QLayoutItem, FlowLayout, QRect, QSize, QWidget, A wrapping flow layout: children flow left-to-right and wrap to new rows. This…

### Community 31 - "WrappingTabBar"
Cohesion: 0.23
Nodes (5): QResizeEvent, Group-aware, wrapping tab bar composed of chip widgets., Rebuild the whole bar from the container's model. Args: order: list of keys…, Grow the bar to fit its rows, capped at ``_max_rows`` (then scroll)., WrappingTabBar

### Community 32 - ".__init__"
Cohesion: 0.18
Nodes (8): HistoryItemDelegate, QStyledItemDelegate, Fully self-painted cells: soft row wash + slim accent bar, no style frame., QStyledItemDelegate, Size columns so Path fills the leftover width initially, while every column…, Paint saved-filter names with a compact delete affordance., _SavedFilterCombo, _SavedFilterDelegate

### Community 33 - "QMenu"
Cohesion: 0.14
Nodes (6): QMenu, Install (or clear) the dropdown's group-send options. ``actions`` is a list of…, Record which send mode the split button runs, and show it on the button., Grey out the dropdown's options when there is no request to send., Ask the provider for a payload and insert it at the cursor., Build a FlowRecord from the current (edited) request text.

### Community 34 - "AttackRunner"
Cohesion: 0.16
Nodes (11): Pattern, QObject, HttpResult, AttackJob, One request to send: the substituted text and the payloads used., AttackRunner, _compile(), Slot (+3 more)

### Community 35 - "QColor"
Cohesion: 0.22
Nodes (10): QColor, QTextCharFormat, _fmt(), Item delegate for the HTTP history table. This delegate paints every cell…, A soft, muted tint of the accent used to fill the selected row. Uses the shared…, _selection_fill(), _blend(), highlight_bg() (+2 more)

### Community 36 - "FindBar"
Cohesion: 0.23
Nodes (7): FindFlags, QKeyEvent, FindBar, QPlainTextEdit, QWidget, Incremental find controls bound to a target text edit., Reveal the bar, seed it with any selected text, and focus input.

### Community 37 - "ui_icon"
Cohesion: 0.16
Nodes (10): A small find bar that searches within a QPlainTextEdit. Reusable over any…, current_mode(), Return the named color tokens for ``mode`` (falls back to dark)., Return a font-independent icon for compact UI controls., Return the theme mode currently applied to the application., tokens(), ui_icon(), _Chip (+2 more)

### Community 38 - "RepeaterTab"
Cohesion: 0.14
Nodes (10): QWidget, Clone a session's request into a new tab, named ``base (n)``., Return ``base (n)`` with the smallest unused positive integer n., Delete a group along with all request tabs it contains., Close every request tab and remove all groups. Always leaves one fresh, empty…, Guarantee at least one (empty) session exists. Called on startup after…, Open a new session tab populated from a captured flow. If the only open session…, Return the sole session iff it is a single, empty, ungrouped tab. (+2 more)

### Community 39 - "Storage Layer (storage/)"
Cohesion: 0.25
Nodes (8): Body Store (file-backed bodies), Capture Addon, Decode Bodies with content not raw_content, FlowRecord Plain Dataclass, asyncio.Event Pause/Forward/Drop, Architecture Layering Invariant, Content-Addressed Body Storage, Storage Layer (storage/)

### Community 40 - "GroupDialog"
Cohesion: 0.22
Nodes (4): GroupDialog, QDialog, Dialog for adding Repeater request tabs to a named, colored group. Presents a…, Collect a group name, member tabs, and a color.

### Community 41 - "parse_response_text"
Cohesion: 0.67
Nodes (3): parse_response_text(), ParsedResponse, Parse raw HTTP response text into a :class:`ParsedResponse`. Tolerant of both…

### Community 42 - "intercept_response_live_test.py"
Cohesion: 0.31
Nodes (7): check_done(), do_forward(), finish(), on_intercepted(), on_started(), Live: intercept a request via the real MainWindow, forward it, and confirm the…, send()

### Community 44 - "FlowRecord"
Cohesion: 0.09
Nodes (14): Row, Storage layer: SQLite persistence + on-disk body store., FlowRecord, A single captured HTTP request/response exchange. Body payloads are represented…, The response content type without parameters (e.g. ``text/html``)., File extension derived from the request path (without the dot). The query…, FlowRepository, SQLite persistence for captured flows. Uses the stdlib ``sqlite3`` module… (+6 more)

### Community 45 - "intercept_live_test.py"
Cohesion: 0.36
Nodes (6): finish(), on_captured(), on_intercepted(), on_started(), Live test: interception pauses a request, and forward/drop resolve it.…, send()

### Community 46 - "InteractionFilterProxy"
Cohesion: 0.29
Nodes (3): InteractionFilterProxy, QSortFilterProxyModel, Filter interactions by protocol and a free-text needle.

### Community 48 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 49 - "QHBoxLayout"
Cohesion: 0.41
Nodes (4): QHBoxLayout, QPushButton, QWidget, QWidget

### Community 50 - "Bidoytu"
Cohesion: 0.12
Nodes (16): Bidoytu Banner Logo, Bidoytu Circular Icon Logo, A note on the editor widget, Architecture, Bidoytu, Building, Contributing, Data flow (+8 more)

### Community 51 - "HttpHighlighter"
Cohesion: 0.23
Nodes (7): QSyntaxHighlighter, HttpHighlighter, Lightweight syntax highlighting for raw HTTP messages. Uses…, Highlights HTTP start-lines and headers., Re-color for a new theme mode and re-highlight the document., highlight_colors(), Return the highlighter color set for ``mode`` (falls back to dark).

### Community 52 - "BodyStore"
Cohesion: 0.20
Nodes (6): BodyStore, Path, On-disk store for large request/response bodies. Rather than storing large…, Content-addressed file store for body payloads. Files are sharded into…, Write ``data`` to the store and return its relative path. Identical content…, Read body content previously returned by :meth:`store`.

### Community 53 - "CLAUDE.md"
Cohesion: 0.22
Nodes (7): Architecture and layering (respect this), Conventions, Gotchas learned the hard way, Tech stack, Verifying changes (always do this), What Bidoytu is, Where things live

### Community 54 - "UI Layer (ui/)"
Cohesion: 0.25
Nodes (8): QPlainTextEdit + QSyntaxHighlighter Editor, Headless Smoke Test, Default 127.0.0.1 Bind, HTTP History, Qt Isolation to ui/, SQLite History Store, UI Layer (ui/), Safe Default Localhost Bind

### Community 55 - "Building and releasing Bidoytu"
Cohesion: 0.14
Nodes (13): Build / check the package locally, Build (Windows or Linux), Building and releasing Bidoytu, Cutting version 1.0.0, How releases work (CI/CD), Local builds (optional), Notes, Nuitka (alternative compiler) (+5 more)

### Community 56 - "_GroupHeaderChip"
Cohesion: 0.20
Nodes (5): _FlowHost, _GroupHeaderChip, QWidget, A group header chip: arrow + name, colored with the group color., Host widget whose height tracks its FlowLayout's height-for-width. A…

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
Cohesion: 0.06
Nodes (33): QIcon, main(), Application entry point. Creates the Qt application, builds the main window,…, Give Windows an explicit AppUserModelID so the taskbar uses our icon. Without…, _set_windows_app_id(), Bidoytu - an intercepting HTTP proxy tool. Base architecture: - Proxy/MITM…, Enables ``python -m bidoytu``., asset_path() (+25 more)

### Community 65 - "Contributing to Bidoytu"
Cohesion: 0.25
Nodes (7): Coding conventions, Contributing to Bidoytu, Development setup, Ground rules, Reporting bugs / security issues, Running the checks, Submitting changes

### Community 67 - "ca_export_test.py"
Cohesion: 0.67
Nodes (3): finish(), poll_for_ca(), Verify the CA is generated in Bidoytu's confdir and can be exported. Starts the…

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

### Community 83 - "SessionState"
Cohesion: 0.18
Nodes (7): Serializable snapshot of a session (for persistence)., SessionState, Group, Path, A named, colored, collapsible collection of member sessions., Write all open sessions and their groups to ``path`` as JSON., Recreate sessions and groups saved by :meth:`save_sessions`.

### Community 87 - "SendHandle"
Cohesion: 0.25
Nodes (4): AbstractEventLoop, A cancellable handle to an in-flight request. The handle wraps the…, SendHandle, Task

### Community 92 - "config.py"
Cohesion: 0.16
Nodes (12): Verify starting the proxy on an occupied port produces a clean error signal…, host_matches_scope(), matches(), _normalise_scope_entry(), ProxyConfig, Application configuration and filesystem paths. Everything the app writes…, Listen and target-scope settings for the mitmproxy engine., Return a host-pattern suitable for scope matching. Scope entries are… (+4 more)

### Community 93 - "_NoFocusRectStyle"
Cohesion: 0.60
Nodes (3): QProxyStyle, _NoFocusRectStyle, Application style that suppresses the item-view focus rectangle globally. The…

### Community 96 - "MarkerHighlighter"
Cohesion: 0.50
Nodes (3): MarkerHighlighter, Highlighter for the Intruder request template. A…, HTTP highlighting plus a highlighted background for ``§payload§`` spans.

### Community 97 - "._set_target_toggle_icon"
Cohesion: 0.40
Nodes (3): Collapse the Target panel to an arrow, or restore its full width., Use a painted arrow so the icon is stable across Qt styles., StandardPixmap

## Ambiguous Edges - Review These
- `Qt Isolation to ui/` → `Safe Default Localhost Bind`  [AMBIGUOUS]
  SECURITY.md · relation: conceptually_related_to
- `Public CA Certificate Export` → `CA Certificate Handling Policy`  [AMBIGUOUS]
  SECURITY.md · relation: references

## Knowledge Gaps
- **99 isolated node(s):** `bidoytu`, `Usage`, `What graphify is for`, `Step 0 - GitHub repos and multi-path merge (only if a URL or several paths)`, `Step 1 - Ensure graphify is installed` (+94 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 600 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **17 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Qt Isolation to ui/` and `Safe Default Localhost Bind`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Public CA Certificate Export` and `CA Certificate Handling Policy`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **Why does `FlowRecord` connect `FlowRecord` to `InterceptView`, `MessageView`, `HistoryView`, `IntruderSession`, `InterceptActivityModel`, `intruder_session.py`, `RepeaterSession`, `ProxyEngine`, `CaptureAddon`, `MainWindow`, `advanced_history.py`, `AsyncHttpSender`, `main_window.py`, `repeater_session.py`, `history_view.py`, `IntruderTab`, `FlowTableModel`, `QMenu`, `RepeaterTab`, `.cookies`, `config.py`?**
  _High betweenness centrality (0.212) - this node is a cross-community bridge._
- **Why does `IntruderSession` connect `IntruderSession` to `MarkerHighlighter`, `AttackRunner`, `MessageView`, `FindBar`, `intruder_session.py`, `IntruderResultsModel`, `FlowRecord`, `strip_markers`, `AsyncHttpSender`, `main_window.py`, `repeater_session.py`, `IntruderTab`, `iter_jobs`, `PayloadSetEditor`?**
  _High betweenness centrality (0.074) - this node is a cross-community bridge._
- **Why does `MainWindow` connect `MainWindow` to `MessageView`, `CollaboratorTab`, `AppConfig`, `RepeaterTab`, `InteractshClient`, `ProxyEngine`, `FlowRecord`, `ProxyTab`, `AsyncHttpSender`, `main_window.py`, `repeater_session.py`, `BodyStore`, `IntruderTab`, `FlowTableModel`, `WorkspaceManager`?**
  _High betweenness centrality (0.068) - this node is a cross-community bridge._
- **Are the 28 inferred relationships involving `FlowRecord` (e.g. with `test_intercept_view()` and `test_qt_and_proxy_apis()`) actually correct?**
  _`FlowRecord` has 28 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `RepeaterSession` (e.g. with `AsyncHttpSender` and `HttpResult`) actually correct?**
  _`RepeaterSession` has 7 INFERRED edges - model-reasoned connections that need verification._
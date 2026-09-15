# Graph Report - Bidoytu  (2026-09-15)

## Corpus Check
- 82 files · ~151,173 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 6 file(s) not represented in the graph (top: (none) 4, .spec 1, .ico 1)

## Summary
- 1587 nodes · 3019 edges · 104 communities (81 shown, 21 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 232 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `5b95603e`
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
- BodyStore
- What You Must Do When Invoked
- ProxyTab
- advanced_history.py
- AsyncHttpSender
- collaborator_tab.py
- repeater_session.py
- SecListsDialog
- http_utils.py
- InteractionsModel
- IntruderTab
- QHBoxLayout
- FlowRecord
- parse_request_text
- PayloadSetEditor
- FlowLayout
- WrappingTabBar
- app.py
- HttpHighlighter
- AttackRunner
- Bidoytu documentation
- Interaction
- .mousePressEvent
- RepeaterTab
- Storage Layer (storage/)
- history_delegate.py
- Path
- intercept_response_live_test.py
- _FlowHost
- FlowRepository
- intercept_live_test.py
- InteractionFilterProxy
- .set_group_send_actions
- graphify reference: extra exports and benchmark
- smoke_test.py
- Bidoytu
- Feature guide
- CaCertDialog
- CLAUDE.md
- UI Layer (ui/)
- Building and releasing Bidoytu
- _GroupHeaderChip
- ProxyEngine (QThread)
- Security Policy
- ._current_as_record
- Public CA Certificate Export
- Release CI/CD Workflow
- proxy_live_test.py
- WorkspaceManager
- gzip_decode_test.py
- Contributing to Bidoytu
- ui/__init__.py
- QColor
- bidoytu
- browser_integration.py
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
- apply_theme
- extraction-spec.md
- _SavedFilterDelegate
- iter_jobs
- Publishing to PyPI (`pip install bidoytu`)
- _NoFocusRectStyle
- .closeEvent
- main_window.py
- ui_icon
- Testing and development
- CONTRIBUTORS.md
- Getting started
- How the application is put together
- .__init__
- SendHandle
- _SavedFilterCombo
- .keyPressEvent
- .__init__
- ._collaborator_payload

## God Nodes (most connected - your core abstractions)
1. `FlowRecord` - 99 edges
2. `RepeaterSession` - 65 edges
3. `IntruderSession` - 60 edges
4. `MainWindow` - 57 edges
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

## Communities (104 total, 21 thin omitted)

### Community 0 - "theme.py"
Cohesion: 0.15
Nodes (21): QPainter, QPixmap, _blank_pixmap(), _build_qss(), _check_icon(), _chevron_down_icon(), _chevron_icon(), _chevron_up_icon() (+13 more)

### Community 1 - "InterceptView"
Cohesion: 0.07
Nodes (21): build_request_text(), Assemble a raw HTTP request string from parts. When ``host`` is provided, a…, InterceptView, QWidget, Size the activity table so URL fills the leftover width, while every column…, Whenever a column is resized, compensate its immediate right neighbor (or left…, Reflow the URL column to absorb the viewport's leftover width. URL is the…, Forward every still-pending flow, then reset the panel. Called when… (+13 more)

### Community 2 - "MessageView"
Cohesion: 0.06
Nodes (17): DetailView, QWidget, Two MessageViews (request | response) with a shared soft-wrap toggle., hex_dump(), _LineNumberArea, MessageView, QPlainTextEdit, QRect (+9 more)

### Community 3 - "CollaboratorTab"
Cohesion: 0.09
Nodes (11): CollaboratorTab, QWidget, Slot, Build a titled pane (label + find bar + view), matching Repeater., Render a raw HTTP message, pretty-printing its body by content-type. Splits…, Attach a note (e.g. the target tab) to the most recent payload., Generate a payload, tag it with ``note``, and return the hostname. Used by…, Register with an Interactsh server, hand out payloads, show callbacks. (+3 more)

### Community 4 - "HistoryView"
Cohesion: 0.07
Nodes (13): QGroupBox, QScrollArea, HistoryFilterDialog, QDialog, Edit a :class:`FilterSpec` without changing the table until Apply., HistoryView, QWidget, Slot (+5 more)

### Community 5 - "AppConfig"
Cohesion: 0.09
Nodes (16): AppConfig, _default_data_dir(), Path, Top-level runtime configuration. Attributes: data_dir: Root directory for all…, Return a per-user, per-OS data directory for Bidoytu., JSON file holding persisted Repeater sessions across restarts., JSON file holding the last Intruder attack config across restarts., JSON file holding the Target scope for this workspace. (+8 more)

### Community 6 - "IntruderSession"
Cohesion: 0.09
Nodes (8): IntruderSession, QWidget, Slot, Grow/shrink the payload-set tabs to exactly ``n`` (min 1)., Return a JSON-serializable snapshot of this session., Restore this session from a snapshot produced by :meth:`to_state`., Build a FlowRecord from the template (payload markers removed)., One Intruder attack: template + positions + payload sets + results.

### Community 7 - "InterceptActivityModel"
Cohesion: 0.08
Nodes (14): ActivityRow, InterceptActivityModel, Orientation, QAbstractTableModel, QModelIndex, Log a paused (pending) request. Returns its row index., Log a paused (pending) response. Returns its row index., True if the row is a still-pending request or response. (+6 more)

### Community 8 - "intruder_session.py"
Cohesion: 0.13
Nodes (25): count_jobs(), PayloadSet, Intruder attack model: markers, attack types, and request building. Qt-free so…, Wrap the ``[sel_start, sel_end)`` span of ``text`` in ``§`` markers. Used by…, Best-effort total request count for a configured attack., A generator plus its processing rules (one Intruder payload set)., wrap_selection(), _apply_one() (+17 more)

### Community 9 - "InteractshClient"
Cohesion: 0.11
Nodes (11): Exception, InteractshClient, _cb(), InteractshError, Raised for registration / polling / crypto failures., Register with, generate payloads for, and poll an Interactsh server. The client…, Generate a keypair and register against the first working server. ``servers``…, Return (ok, done). ``done`` short-circuits trying more servers. (+3 more)

### Community 10 - "RepeaterSession"
Cohesion: 0.11
Nodes (8): Slot, Set the status/target label, eliding to fit the current width. Stores the full…, True if this is a pristine session: no request text and no history., Enable/disable the Send action while keeping the button visible. We…, Paint the Send button with the disabled cue when it has no request. Uses a…, Public entry point for the container to send this tab's request., One request/response pane with full Repeater controls., RepeaterSession

### Community 11 - "IntruderResultsModel"
Cohesion: 0.11
Nodes (10): One completed request in the results table., ResultRow, IntruderResultsModel, QAbstractTableModel, QModelIndex, QSortFilterProxyModel, Table model + filter proxy for Intruder attack results.…, Filter results by status, min length, matched-only, and a text needle. (+2 more)

### Community 12 - "ProxyEngine"
Cohesion: 0.07
Nodes (14): QThread, ProxyConfig, Listen and target-scope settings for the mitmproxy engine., ProxyEngine, Check the listen port is free before handing off to mitmproxy. Failing fast…, Update target scope immediately, including while the proxy runs., Toggle the global 'intercept responses' behavior., Arm a one-shot response intercept for a single flow. (+6 more)

### Community 13 - "CaptureAddon"
Cohesion: 0.10
Nodes (15): FlowCallback, HTTPFlow, InterceptCallback, CaptureAddon, _PendingFlow, Arm a one-shot response intercept for a single flow (Burp's "Response to this…, Apply a UI decision to a paused request. Runs on the proxy loop., Apply a UI decision to a paused response. Runs on the proxy loop. (+7 more)

### Community 14 - "MainWindow"
Cohesion: 0.13
Nodes (4): QMainWindow, MainWindow, Slot, Load a file-backed request body inline so editors can show it.

### Community 15 - "BodyStore"
Cohesion: 0.25
Nodes (5): BodyStore, Path, Content-addressed file store for body payloads. Files are sharded into…, Write ``data`` to the store and return its relative path. Identical content…, Read body content previously returned by :meth:`store`.

### Community 16 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 17 - "ProxyTab"
Cohesion: 0.08
Nodes (13): QFrame, ProxyTab, QWidget, Container widget for everything under the top-level "Proxy" tab., Collapse the Target panel to an arrow, or restore its full width., Use a painted arrow so the icon is stable across Qt styles., Show the settings panel as an in-window child widget., The Clear History button now lives in the Intercept control row. Exposed here… (+5 more)

### Community 18 - "advanced_history.py"
Cohesion: 0.12
Nodes (26): _body(), _compare(), curl_command(), deserialize_filter_spec(), export_records(), _field(), FilterSpec, fingerprint() (+18 more)

### Community 19 - "AsyncHttpSender"
Cohesion: 0.15
Nodes (6): ResultCallback, AsyncHttpSender, _schedule(), Schedule a request; ``callback`` is invoked on the sender thread. Returns a…, Owns a background event loop running httpx.AsyncClient instances., Networking helpers (async HTTP client for Repeater/Intruder).

### Community 20 - "collaborator_tab.py"
Cohesion: 0.20
Nodes (11): _encode_xid(), generate_xid(), Interactsh (OAST) client for the Collaborator feature. This is a small, Qt-free…, Everything needed to resume / persist a registered session., Return a 20-char XID string. XID layout: 4-byte time, 3-byte machine id, 2-byte…, Encode 12 raw bytes into the 20-char XID base32 representation., SessionInfo, Table model + filter proxy for Collaborator (OAST) interactions.… (+3 more)

### Community 21 - "repeater_session.py"
Cohesion: 0.08
Nodes (24): HTMLParser, format_body(), _format_c_like(), _format_css(), _format_form(), _format_html(), _format_js(), _format_json() (+16 more)

### Community 22 - "SecListsDialog"
Cohesion: 0.07
Nodes (24): QTreeWidgetItem, default_cache_dir(), Path, Browse and fetch wordlists from the SecLists project on demand. `SecLists…, Where a given repository path is (or would be) cached locally., Whether the wordlist at *path* already exists in the local cache., Return repo-relative paths of every wordlist already cached locally., Download the wordlist at *path* into the cache and return its path. If the file… (+16 more)

### Community 23 - "http_utils.py"
Cohesion: 0.10
Nodes (18): absolute_url(), build_response_text(), ensure_host_header(), _headers_have(), parse_response_text(), ParsedResponse, Helpers for converting between raw HTTP text and structured parts. Used by…, Assemble a raw HTTP response string from parts. (+10 more)

### Community 24 - "InteractionsModel"
Cohesion: 0.15
Nodes (9): InteractionRow, InteractionsModel, protocol_color(), QAbstractTableModel, QModelIndex, Render an ISO timestamp as HH:MM:SS, falling back to the raw string., Return a hex color for an interaction protocol., A received interaction plus the display metadata we derive from it. (+1 more)

### Community 25 - "IntruderTab"
Cohesion: 0.15
Nodes (8): IntruderTab, Path, QWidget, Close every Intruder tab., Open a new session tab populated from a captured flow., Write every open session to ``path`` as JSON (list of snapshots)., Recreate the sessions saved by :meth:`save_state`. Accepts both the multi-…, Holds multiple :class:`IntruderSession` instances in a tab strip.

### Community 26 - "QHBoxLayout"
Cohesion: 0.18
Nodes (10): FindFlags, QComboBox, QHBoxLayout, QPushButton, FindBar, QPlainTextEdit, QWidget, Incremental find controls bound to a target text edit. (+2 more)

### Community 27 - "FlowRecord"
Cohesion: 0.08
Nodes (13): SortOrder, FlowRecord, Cookie names sent/received for this flow, comma-separated. Collects request…, A single captured HTTP request/response exchange. Body payloads are represented…, The response content type without parameters (e.g. ``text/html``)., File extension derived from the request path (without the dot). The query…, FlowTableModel, Orientation (+5 more)

### Community 28 - "parse_request_text"
Cohesion: 0.28
Nodes (5): host_from_headers_or_url(), parse_request_text(), ParsedRequest, Determine (scheme, host, port, path) for sending a parsed request. Prefers an…, Parse raw HTTP request text into a :class:`ParsedRequest`. Tolerant of both…

### Community 29 - "PayloadSetEditor"
Cohesion: 0.14
Nodes (6): PayloadSetEditor, ProcessingRuleDialog, QDialog, QWidget, Edit one payload set: a generator plus a processing-rule pipeline., Configure a single :class:`ProcessingRule`.

### Community 30 - "FlowLayout"
Cohesion: 0.15
Nodes (7): Orientations, QLayout, QLayoutItem, FlowLayout, QRect, QSize, A wrapping flow layout: children flow left-to-right and wrap to new rows. This…

### Community 31 - "WrappingTabBar"
Cohesion: 0.24
Nodes (5): QResizeEvent, Group-aware, wrapping tab bar composed of chip widgets., Rebuild the whole bar from the container's model. Args: order: list of keys…, Grow the bar to fit its rows, capped at ``_max_rows`` (then scroll)., WrappingTabBar

### Community 32 - "app.py"
Cohesion: 0.16
Nodes (15): main(), Application entry point. Creates the Qt application, builds the main window,…, Give Windows an explicit AppUserModelID so the taskbar uses our icon. Without…, _set_windows_app_id(), Bidoytu - an intercepting HTTP proxy tool. Base architecture: - Proxy/MITM…, Enables ``python -m bidoytu``., asset_path(), _assets_dir() (+7 more)

### Community 33 - "HttpHighlighter"
Cohesion: 0.17
Nodes (10): QSyntaxHighlighter, HttpHighlighter, Lightweight syntax highlighting for raw HTTP messages. Uses…, Highlights HTTP start-lines and headers., Re-color for a new theme mode and re-highlight the document., MarkerHighlighter, Highlighter for the Intruder request template. A…, HTTP highlighting plus a highlighted background for ``§payload§`` spans. (+2 more)

### Community 34 - "AttackRunner"
Cohesion: 0.16
Nodes (11): Pattern, QObject, HttpResult, AttackJob, One request to send: the substituted text and the payloads used., AttackRunner, _compile(), Slot (+3 more)

### Community 35 - "Bidoytu documentation"
Cohesion: 0.18
Nodes (11): At a glance, Bidoytu documentation, Configuration, Contents, Data and storage, First-run workflow, Packaging and releases, Repository map (+3 more)

### Community 36 - "Interaction"
Cohesion: 0.14
Nodes (7): Interaction, _cb(), _now_iso(), A single out-of-band interaction reported by the server., Poll the server once. ``on_done(interactions, error)`` on sender thread., Best-effort correlate an interaction back to a generated payload., Restore a session saved by :meth:`save_state` and re-register it.

### Community 38 - "RepeaterTab"
Cohesion: 0.06
Nodes (23): GroupDialog, QDialog, Dialog for adding Repeater request tabs to a named, colored group. Presents a…, Collect a group name, member tabs, and a color., Serializable snapshot of a session (for persistence)., SessionState, Group, Path (+15 more)

### Community 39 - "Storage Layer (storage/)"
Cohesion: 0.20
Nodes (10): Body Store (file-backed bodies), Capture Addon, Decode Bodies with content not raw_content, FlowRecord Plain Dataclass, asyncio.Event Pause/Forward/Drop, Architecture Layering Invariant, Content-Addressed Body Storage, HTTP History (+2 more)

### Community 40 - "history_delegate.py"
Cohesion: 0.27
Nodes (8): HistoryItemDelegate, QStyledItemDelegate, Item delegate for the HTTP history table. This delegate paints every cell…, A soft, muted tint of the accent used to fill the selected row. Uses the shared…, Fully self-painted cells: soft row wash + slim accent bar, no style frame., _selection_fill(), highlight_bg(), selection_color()

### Community 42 - "intercept_response_live_test.py"
Cohesion: 0.31
Nodes (7): check_done(), do_forward(), finish(), on_intercepted(), on_started(), Live: intercept a request via the real MainWindow, forward it, and confirm the…, send()

### Community 43 - "_FlowHost"
Cohesion: 0.47
Nodes (3): _FlowHost, QWidget, Host widget whose height tracks its FlowLayout's height-for-width. A…

### Community 44 - "FlowRepository"
Cohesion: 0.09
Nodes (12): Connection, Row, FlowRepository, Path, Move the corrupt database and SQLite sidecars to a safe backup., Insert a new flow and return its assigned primary key., Update an existing flow (matched by ``flow_id``)., Insert if new, otherwise update. Returns the row id. (+4 more)

### Community 45 - "intercept_live_test.py"
Cohesion: 0.36
Nodes (6): finish(), on_captured(), on_intercepted(), on_started(), Live test: interception pauses a request, and forward/drop resolve it.…, send()

### Community 46 - "InteractionFilterProxy"
Cohesion: 0.24
Nodes (5): CollaboratorConfig, Settings for the Collaborator (out-of-band interaction) feature. Attributes:…, InteractionFilterProxy, QSortFilterProxyModel, Filter interactions by protocol and a free-text needle.

### Community 47 - ".set_group_send_actions"
Cohesion: 0.29
Nodes (3): Install (or clear) the dropdown's group-send options. ``actions`` is a list of…, Record which send mode the split button runs, and show it on the button., Grey out the dropdown's options when there is no request to send.

### Community 48 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 49 - "smoke_test.py"
Cohesion: 0.35
Nodes (11): QApplication, main(), Path, Import + wiring smoke test (no live proxy, no visible window). Verifies: - all…, test_body_format(), test_body_store(), test_http_utils(), test_intercept_view() (+3 more)

### Community 50 - "Bidoytu"
Cohesion: 0.14
Nodes (15): Bidoytu Banner Logo, Bidoytu Circular Icon Logo, A note on the editor widget, Architecture, Bidoytu, Building, Contributing, Data flow (+7 more)

### Community 51 - "Feature guide"
Cohesion: 0.25
Nodes (8): Collaborator, Display and themes, Feature guide, History, Intercept, Intruder, Proxy, Repeater

### Community 52 - "CaCertDialog"
Cohesion: 0.33
Nodes (5): CaCertDialog, Path, QDialog, Dialog for exporting and installing the proxy's CA certificate. To intercept…, Shows CA status, an export button, and install instructions.

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
Nodes (7): Coding conventions, Contributing to Bidoytu, Development setup, Ground rules, Reporting bugs / security issues, Running the checks, Submitting changes

### Community 67 - "QColor"
Cohesion: 0.47
Nodes (5): QColor, QTextCharFormat, _fmt(), _blend(), Blend ``fg`` over ``bg`` by ``alpha`` (0..1) and return a hex string. Used to…

### Community 69 - "browser_integration.py"
Cohesion: 0.16
Nodes (20): Popen, BrowserInfo, _chromium_profile(), discover_browsers(), _existing(), _firefox_profile(), install_ca_for_browser(), launch_browser() (+12 more)

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

### Community 83 - "apply_theme"
Cohesion: 0.53
Nodes (6): QPalette, apply_theme(), _dark_palette(), _light_palette(), _palette_from_tokens(), Apply ``mode`` ('light' or 'dark') to the whole application.

### Community 86 - "_SavedFilterDelegate"
Cohesion: 0.67
Nodes (3): QStyledItemDelegate, Paint saved-filter names with a compact delete affordance., _SavedFilterDelegate

### Community 87 - "iter_jobs"
Cohesion: 0.12
Nodes (14): find_markers(), iter_jobs(), Marker, Return the template with all ``§`` markers removed (defaults kept)., Insert ``values`` into ``clean_text`` at each marker (right-to-left). Working…, Yield an :class:`AttackJob` per request for the configured attack.…, A payload position: the span between a pair of ``§`` markers. ``start``/``end``…, Split a ``§``-marked template into (clean_text, markers). Markers come in… (+6 more)

### Community 89 - "Publishing to PyPI (`pip install bidoytu`)"
Cohesion: 0.50
Nodes (4): Build / check the package locally, One-time setup on PyPI, Publishing to PyPI (`pip install bidoytu`), Releasing a new version to PyPI

### Community 90 - "_NoFocusRectStyle"
Cohesion: 0.60
Nodes (3): QProxyStyle, _NoFocusRectStyle, Application style that suppresses the item-view focus rectangle globally. The…

### Community 92 - "main_window.py"
Cohesion: 0.09
Nodes (21): finish(), poll_for_ca(), Verify the CA is generated in Bidoytu's confdir and can be exported. Starts the…, Verify starting the proxy on an occupied port produces a clean error signal…, Live test: RepeaterTab.load_from_record + Send performs a real request., host_matches_scope(), matches(), _normalise_scope_entry() (+13 more)

### Community 93 - "ui_icon"
Cohesion: 0.19
Nodes (9): current_mode(), Return the named color tokens for ``mode`` (falls back to dark)., Return a font-independent icon for compact UI controls., Return the theme mode currently applied to the application., tokens(), ui_icon(), _Chip, A wrapping, group-aware tab bar built from individual chip widgets. Unlike… (+1 more)

### Community 94 - "Testing and development"
Cohesion: 0.67
Nodes (3): Contribution workflow, Fast verification, Testing and development

### Community 96 - "Getting started"
Cohesion: 0.67
Nodes (3): Getting started, Install from source, Requirements

### Community 97 - "How the application is put together"
Cohesion: 0.67
Nodes (3): How the application is put together, Startup sequence, Threading model

### Community 98 - ".__init__"
Cohesion: 0.20
Nodes (4): QIcon, Reclassify existing rows when target scope rules change., Persist the chosen theme., save_theme()

### Community 99 - "SendHandle"
Cohesion: 0.25
Nodes (4): AbstractEventLoop, A cancellable handle to an in-flight request. The handle wraps the…, SendHandle, Task

## Ambiguous Edges - Review These
- `Qt Isolation to ui/` → `Safe Default Localhost Bind`  [AMBIGUOUS]
  SECURITY.md · relation: conceptually_related_to
- `Public CA Certificate Export` → `CA Certificate Handling Policy`  [AMBIGUOUS]
  SECURITY.md · relation: references

## Knowledge Gaps
- **121 isolated node(s):** `bidoytu`, `Usage`, `What graphify is for`, `Step 0 - GitHub repos and multi-path merge (only if a URL or several paths)`, `Step 1 - Ensure graphify is installed` (+116 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 647 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **21 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Qt Isolation to ui/` and `Safe Default Localhost Bind`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Public CA Certificate Export` and `CA Certificate Handling Policy`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **Why does `FlowRecord` connect `FlowRecord` to `InterceptView`, `MessageView`, `HistoryView`, `IntruderSession`, `InterceptActivityModel`, `intruder_session.py`, `RepeaterSession`, `ProxyEngine`, `CaptureAddon`, `MainWindow`, `advanced_history.py`, `AsyncHttpSender`, `repeater_session.py`, `http_utils.py`, `IntruderTab`, `RepeaterTab`, `FlowRepository`, `smoke_test.py`, `._current_as_record`, `main_window.py`?**
  _High betweenness centrality (0.188) - this node is a cross-community bridge._
- **Why does `AsyncHttpSender` connect `AsyncHttpSender` to `AttackRunner`, `CollaboratorTab`, `.__init__`, `IntruderSession`, `RepeaterTab`, `intruder_session.py`, `InteractshClient`, `RepeaterSession`, `InteractionFilterProxy`, `MainWindow`, `collaborator_tab.py`, `repeater_session.py`, `IntruderTab`, `QHBoxLayout`, `main_window.py`?**
  _High betweenness centrality (0.079) - this node is a cross-community bridge._
- **Why does `IntruderSession` connect `IntruderSession` to `HttpHighlighter`, `AttackRunner`, `MessageView`, `intruder_session.py`, `IntruderResultsModel`, `main_window.py`, `AsyncHttpSender`, `iter_jobs`, `IntruderTab`, `QHBoxLayout`, `FlowRecord`, `parse_request_text`, `PayloadSetEditor`?**
  _High betweenness centrality (0.078) - this node is a cross-community bridge._
- **Are the 28 inferred relationships involving `FlowRecord` (e.g. with `test_intercept_view()` and `test_qt_and_proxy_apis()`) actually correct?**
  _`FlowRecord` has 28 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `RepeaterSession` (e.g. with `AsyncHttpSender` and `HttpResult`) actually correct?**
  _`RepeaterSession` has 7 INFERRED edges - model-reasoned connections that need verification._
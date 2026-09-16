# Graph Report - Bidoytu  (2026-09-16)

## Corpus Check
- 83 files · ~155,200 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 6 file(s) not represented in the graph (top: (none) 4, .spec 1, .ico 1)

## Summary
- 1693 nodes · 3226 edges · 108 communities (88 shown, 18 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 249 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `c6dad526`
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
- intruder_session.py
- ProxyEngine
- CaptureAddon
- MainWindow
- collaborator_tab.py
- What You Must Do When Invoked
- ProxyTab
- FlowRecord
- AsyncHttpSender
- TargetTab
- browser_integration.py
- SecListsDialog
- body_format.py
- InteractionsModel
- IntruderTab
- PayloadSetEditor
- FlowTableModel
- content_type_from_headers
- _HTMLPretty
- FlowLayout
- WrappingTabBar
- ._send
- _SitemapTableModel
- AttackRunner
- Bidoytu documentation
- _LineNumberArea
- _ScopePage
- RepeaterTab
- Storage Layer (storage/)
- GroupDialog
- _ScopeTable
- intercept_response_live_test.py
- _SitemapPage
- FlowRepository
- intercept_live_test.py
- InteractionFilterProxy
- history_delegate.py
- graphify reference: extra exports and benchmark
- ResultFilterProxy
- Bidoytu
- Feature guide
- proxy_live_test.py
- CLAUDE.md
- UI Layer (ui/)
- Building and releasing Bidoytu
- BodyStore
- ProxyEngine (QThread)
- Security Policy
- ._set_has_request
- Public CA Certificate Export
- Release CI/CD Workflow
- .__init__
- WorkspaceManager
- main_window.py
- Contributing to Bidoytu
- ui/__init__.py
- start_proxy_repro.py
- bidoytu
- .restore_sessions
- httpx Async Client
- AGENTS.md
- Display vs. Wire Invariant
- graphify reference: query, path, explain
- Contributors Acknowledgement
- ._render
- http_utils Raw HTTP Parsing
- Private Vulnerability Reporting
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native CLAUDE.md integration
- graphify reference: incremental update and cluster-only
- graphify reference: GitHub clone and cross-repo merge
- graphify reference: transcribe video and audio
- parse_request_text
- extraction-spec.md
- ._set_target_toggle_icon
- ._show_raw
- Publishing to PyPI (`pip install bidoytu`)
- DetailView
- intercept_view.py
- apply_theme
- ui_icon
- Testing and development
- CONTRIBUTORS.md
- Getting started
- How the application is put together
- repeater_session.py
- _SavedFilterCombo
- FindBar
- QHBoxLayout
- .save_state
- HttpHighlighter
- .set_group_send_actions
- _Chip
- ._update_group_send_menu
- .cookies

## God Nodes (most connected - your core abstractions)
1. `FlowRecord` - 102 edges
2. `RepeaterSession` - 65 edges
3. `IntruderSession` - 62 edges
4. `MainWindow` - 58 edges
5. `CollaboratorTab` - 54 edges
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

## Communities (108 total, 18 thin omitted)

### Community 0 - "theme.py"
Cohesion: 0.13
Nodes (27): QColor, QPainter, QPixmap, _protocol_icon(), QIcon, Small lock/unlock glyph used by the sitemap host tree., _blank_pixmap(), _blend() (+19 more)

### Community 1 - "InterceptView"
Cohesion: 0.07
Nodes (21): build_response_text(), Assemble a raw HTTP response string from parts., InterceptView, QWidget, Size the activity table so URL fills the leftover width, while every column…, Whenever a column is resized, compensate its immediate right neighbor (or left…, Reflow the URL column to absorb the viewport's leftover width. URL is the…, Forward every still-pending flow, then reset the panel. Called when… (+13 more)

### Community 2 - "MessageView"
Cohesion: 0.12
Nodes (7): MessageView, QPlainTextEdit, QRect, Return the full editor contents as text (for editable views)., Re-color the syntax highlighter for a new theme mode., Register an extra action shown in the right-click menu. The action is appended…, A monospace, syntax-highlighted view of a raw HTTP request/response.

### Community 3 - "CollaboratorTab"
Cohesion: 0.09
Nodes (8): CollaboratorTab, QWidget, Slot, Build a titled pane (label + find bar + view), matching Repeater., Attach a note (e.g. the target tab) to the most recent payload., Generate a payload, tag it with ``note``, and return the hostname. Used by…, Register with an Interactsh server, hand out payloads, show callbacks., Stop polling and deregister on application close (best-effort).

### Community 4 - "HistoryView"
Cohesion: 0.05
Nodes (20): QGroupBox, QScrollArea, SortOrder, deserialize_filter_spec(), FilterSpec, Persist the complete filter state in the saved-filter query column., Load a saved filter, accepting legacy plain HTTPQL values., serialize_filter_spec() (+12 more)

### Community 5 - "AppConfig"
Cohesion: 0.09
Nodes (16): AppConfig, _default_data_dir(), Path, Top-level runtime configuration. Attributes: data_dir: Root directory for all…, Return a per-user, per-OS data directory for Bidoytu., JSON file holding persisted Repeater sessions across restarts., JSON file holding the last Intruder attack config across restarts., JSON file holding the Target scope for this workspace. (+8 more)

### Community 6 - "IntruderSession"
Cohesion: 0.06
Nodes (14): find_markers(), Return the template with all ``§`` markers removed (defaults kept)., Split a ``§``-marked template into (clean_text, markers). Markers come in…, strip_markers(), IntruderSession, Slot, Whether this is a pristine attack: no target and a blank template. Used by the…, Grow/shrink the payload-set tabs to exactly ``n`` (min 1). (+6 more)

### Community 7 - "InterceptActivityModel"
Cohesion: 0.08
Nodes (14): ActivityRow, InterceptActivityModel, Orientation, QAbstractTableModel, QModelIndex, Log a paused (pending) request. Returns its row index., Log a paused (pending) response. Returns its row index., True if the row is a still-pending request or response. (+6 more)

### Community 8 - "attack.py"
Cohesion: 0.12
Nodes (28): count_jobs(), iter_jobs(), Marker, PayloadSet, Intruder attack model: markers, attack types, and request building. Qt-free so…, Insert ``values`` into ``clean_text`` at each marker (right-to-left). Working…, Best-effort total request count for a configured attack., Yield an :class:`AttackJob` per request for the configured attack.… (+20 more)

### Community 9 - "InteractshClient"
Cohesion: 0.09
Nodes (14): Exception, InteractshClient, _cb(), _cb(), InteractshError, Raised for registration / polling / crypto failures., Register with, generate payloads for, and poll an Interactsh server. The client…, Generate a keypair and register against the first working server. ``servers``… (+6 more)

### Community 10 - "RepeaterSession"
Cohesion: 0.14
Nodes (6): HttpResult, True if this is a pristine session: no request text and no history., Ask the provider for a payload and insert it at the cursor., Build a FlowRecord from the current (edited) request text., One request/response pane with full Repeater controls., RepeaterSession

### Community 11 - "intruder_session.py"
Cohesion: 0.11
Nodes (15): Pattern, Wrap the ``[sel_start, sel_end)`` span of ``text`` in ``§`` markers. Used by…, wrap_selection(), _compile(), GrepConfig, Drives an Intruder attack: iterate jobs, send them, collect results. The runner…, How to derive match/extract columns from each response., One completed request in the results table. (+7 more)

### Community 12 - "ProxyEngine"
Cohesion: 0.07
Nodes (14): QThread, ProxyConfig, Listen and target-scope settings for the mitmproxy engine., ProxyEngine, Check the listen port is free before handing off to mitmproxy. Failing fast…, Update target scope immediately, including while the proxy runs., Toggle the global 'intercept responses' behavior., Arm a one-shot response intercept for a single flow. (+6 more)

### Community 13 - "CaptureAddon"
Cohesion: 0.10
Nodes (15): FlowCallback, HTTPFlow, InterceptCallback, CaptureAddon, _PendingFlow, Global toggle: pause every response for review when enabled., Arm a one-shot response intercept for a single flow (Burp's "Response to this…, Apply a UI decision to a paused request. Runs on the proxy loop. (+7 more)

### Community 14 - "MainWindow"
Cohesion: 0.06
Nodes (15): QMainWindow, CaCertDialog, Path, QDialog, Dialog for exporting and installing the proxy's CA certificate. To intercept…, Shows CA status, an export button, and install instructions., MainWindow, Slot (+7 more)

### Community 15 - "collaborator_tab.py"
Cohesion: 0.11
Nodes (19): _encode_xid(), generate_xid(), Interaction, _now_iso(), Interactsh (OAST) client for the Collaborator feature. This is a small, Qt-free…, A single out-of-band interaction reported by the server., Everything needed to resume / persist a registered session., Return a 20-char XID string. XID layout: 4-byte time, 3-byte machine id, 2-byte… (+11 more)

### Community 16 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 17 - "ProxyTab"
Cohesion: 0.12
Nodes (6): ProxyTab, Container widget for everything under the top-level "Proxy" tab., Show the settings panel as an in-window child widget., The Clear History button now lives in the Intercept control row. Exposed here…, First click arms the button; a second click within 3s confirms. This guards…, Surface a detailed transient message (e.g. "Starting...", errors) on the…

### Community 18 - "FlowRecord"
Cohesion: 0.09
Nodes (32): ensure_host_header(), _headers_have(), Return True if the raw header block already contains ``name`` (case-…, Return the header block with a ``Host`` header guaranteed to be present. If…, _body(), _compare(), curl_command(), export_records() (+24 more)

### Community 19 - "AsyncHttpSender"
Cohesion: 0.09
Nodes (11): AbstractEventLoop, ResultCallback, AsyncHttpSender, _schedule(), Schedule a request; ``callback`` is invoked on the sender thread. Returns a…, A cancellable handle to an in-flight request. The handle wraps the…, Owns a background event loop running httpx.AsyncClient instances., SendHandle (+3 more)

### Community 21 - "browser_integration.py"
Cohesion: 0.16
Nodes (20): Popen, BrowserInfo, _chromium_profile(), discover_browsers(), _existing(), _firefox_profile(), install_ca_for_browser(), launch_browser() (+12 more)

### Community 22 - "SecListsDialog"
Cohesion: 0.06
Nodes (24): QTreeWidgetItem, default_cache_dir(), Path, Browse and fetch wordlists from the SecLists project on demand. `SecLists…, Where a given repository path is (or would be) cached locally., Whether the wordlist at *path* already exists in the local cache., Return repo-relative paths of every wordlist already cached locally., Download the wordlist at *path* into the cache and return its path. If the file… (+16 more)

### Community 23 - "body_format.py"
Cohesion: 0.18
Nodes (16): format_body(), _format_c_like(), _format_css(), _format_form(), _format_html(), _format_js(), _format_json(), _format_xml() (+8 more)

### Community 24 - "InteractionsModel"
Cohesion: 0.13
Nodes (10): InteractionRow, InteractionsModel, protocol_color(), QAbstractTableModel, QModelIndex, Drop the oldest rows and return the number removed., Render an ISO timestamp as HH:MM:SS, falling back to the raw string., Return a hex color for an interaction protocol. (+2 more)

### Community 25 - "IntruderTab"
Cohesion: 0.13
Nodes (10): IntruderTab, Path, QWidget, Close every Intruder tab., Return the sole session iff it is a single, pristine, empty tab., Guarantee at least one (empty) attack tab exists. Called on startup after…, Open a session tab populated from a captured flow. If the only open session is…, Write every open session to ``path`` as JSON (list of snapshots). (+2 more)

### Community 26 - "PayloadSetEditor"
Cohesion: 0.15
Nodes (6): PayloadSetEditor, ProcessingRuleDialog, QDialog, QWidget, Edit one payload set: a generator plus a processing-rule pipeline., Configure a single :class:`ProcessingRule`.

### Community 27 - "FlowTableModel"
Cohesion: 0.16
Nodes (5): FlowTableModel, Orientation, QAbstractTableModel, QModelIndex, Replace all rows (e.g. when loading history from the database).

### Community 28 - "content_type_from_headers"
Cohesion: 0.21
Nodes (14): QApplication, main(), Path, Import + wiring smoke test (no live proxy, no visible window). Verifies: - all…, test_body_format(), test_body_store(), test_http_utils(), test_intercept_view() (+6 more)

### Community 29 - "_HTMLPretty"
Cohesion: 0.22
Nodes (4): HTMLParser, _HTMLPretty, Lenient HTML pretty-printer built on the stdlib parser. Emits nicely indented…, Close a preceding sibling with an optional end tag, if applicable.

### Community 30 - "FlowLayout"
Cohesion: 0.13
Nodes (8): Orientations, QLayout, QLayoutItem, FlowLayout, QRect, QSize, QWidget, A wrapping flow layout: children flow left-to-right and wrap to new rows. This…

### Community 31 - "WrappingTabBar"
Cohesion: 0.23
Nodes (5): QResizeEvent, Group-aware, wrapping tab bar composed of chip widgets., Rebuild the whole bar from the container's model. Args: order: list of keys…, Grow the bar to fit its rows, capped at ``_max_rows`` (then scroll)., WrappingTabBar

### Community 32 - "._send"
Cohesion: 0.23
Nodes (3): Slot, Set the status/target label, eliding to fit the current width. Stores the full…, Public entry point for the container to send this tab's request.

### Community 34 - "AttackRunner"
Cohesion: 0.20
Nodes (7): QObject, AttackJob, One request to send: the substituted text and the payloads used., AttackRunner, Slot, Launch requests until we hit the concurrency cap or run out., Runs one attack, emitting a :class:`ResultRow` per completed request.

### Community 35 - "Bidoytu documentation"
Cohesion: 0.18
Nodes (11): At a glance, Bidoytu documentation, Configuration, Contents, Data and storage, First-run workflow, Packaging and releases, Repository map (+3 more)

### Community 36 - "_LineNumberArea"
Cohesion: 0.29
Nodes (4): _LineNumberArea, QSize, QWidget, Gutter widget that paints line numbers for its owning MessageView.

### Community 38 - "RepeaterTab"
Cohesion: 0.14
Nodes (10): QWidget, Clone a session's request into a new tab, named ``base (n)``., Return ``base (n)`` with the smallest unused positive integer n., Delete a group along with all request tabs it contains., Close every request tab and remove all groups. Always leaves one fresh, empty…, Guarantee at least one (empty) session exists. Called on startup after…, Open a new session tab populated from a captured flow. If the only open session…, Return the sole session iff it is a single, empty, ungrouped tab. (+2 more)

### Community 39 - "Storage Layer (storage/)"
Cohesion: 0.20
Nodes (10): Body Store (file-backed bodies), Capture Addon, Decode Bodies with content not raw_content, FlowRecord Plain Dataclass, asyncio.Event Pause/Forward/Drop, Architecture Layering Invariant, Content-Addressed Body Storage, HTTP History (+2 more)

### Community 40 - "GroupDialog"
Cohesion: 0.22
Nodes (4): GroupDialog, QDialog, Dialog for adding Repeater request tabs to a named, colored group. Presents a…, Collect a group name, member tabs, and a color.

### Community 41 - "_ScopeTable"
Cohesion: 0.24
Nodes (3): QWidget, Create a native checkbox consistent with the rest of the UI., _ScopeTable

### Community 42 - "intercept_response_live_test.py"
Cohesion: 0.31
Nodes (7): check_done(), do_forward(), finish(), on_intercepted(), on_started(), Live: intercept a request via the real MainWindow, forward it, and confirm the…, send()

### Community 44 - "FlowRepository"
Cohesion: 0.07
Nodes (15): Connection, Row, FlowRepository, Path, Move the corrupt database and SQLite sidecars to a safe backup., Insert a new flow and return its assigned primary key., Update an existing flow (matched by ``flow_id``)., Persist scope changes in one transaction. Scope rules can affect thousands of… (+7 more)

### Community 45 - "intercept_live_test.py"
Cohesion: 0.36
Nodes (6): finish(), on_captured(), on_intercepted(), on_started(), Live test: interception pauses a request, and forward/drop resolve it.…, send()

### Community 46 - "InteractionFilterProxy"
Cohesion: 0.24
Nodes (5): CollaboratorConfig, Settings for the Collaborator (out-of-band interaction) feature. Attributes:…, InteractionFilterProxy, QSortFilterProxyModel, Filter interactions by protocol and a free-text needle.

### Community 47 - "history_delegate.py"
Cohesion: 0.27
Nodes (8): HistoryItemDelegate, QStyledItemDelegate, Item delegate for the HTTP history table. This delegate paints every cell…, A soft, muted tint of the accent used to fill the selected row. Uses the shared…, Fully self-painted cells: soft row wash + slim accent bar, no style frame., _selection_fill(), highlight_bg(), selection_color()

### Community 48 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 49 - "ResultFilterProxy"
Cohesion: 0.22
Nodes (3): QSortFilterProxyModel, Filter results by status, min length, matched-only, and a text needle., ResultFilterProxy

### Community 50 - "Bidoytu"
Cohesion: 0.14
Nodes (15): Bidoytu Banner Logo, Bidoytu Circular Icon Logo, A note on the editor widget, Architecture, Bidoytu, Building, Contributing, Data flow (+7 more)

### Community 51 - "Feature guide"
Cohesion: 0.22
Nodes (9): Collaborator, Display and themes, Feature guide, History, Intercept, Intruder, Proxy, Repeater (+1 more)

### Community 52 - "proxy_live_test.py"
Cohesion: 0.33
Nodes (3): on_started(), Live end-to-end test: start the ProxyEngine thread and route a real request…, send_request()

### Community 53 - "CLAUDE.md"
Cohesion: 0.22
Nodes (7): Architecture and layering (respect this), Conventions, Gotchas learned the hard way, Tech stack, Verifying changes (always do this), What Bidoytu is, Where things live

### Community 54 - "UI Layer (ui/)"
Cohesion: 0.22
Nodes (9): QPlainTextEdit + QSyntaxHighlighter Editor, Headless Smoke Test, Default 127.0.0.1 Bind, PySide6, Qt Isolation to ui/, UI Layer (ui/), PySide6 Dependency, Safe Default Localhost Bind (+1 more)

### Community 55 - "Building and releasing Bidoytu"
Cohesion: 0.22
Nodes (9): Build (Windows or Linux), Building and releasing Bidoytu, Cutting version 1.0.0, How releases work (CI/CD), Local builds (optional), Notes, Nuitka (alternative compiler), Prerequisites (+1 more)

### Community 56 - "BodyStore"
Cohesion: 0.25
Nodes (5): BodyStore, Path, Content-addressed file store for body payloads. Files are sharded into…, Write ``data`` to the store and return its relative path. Identical content…, Read body content previously returned by :meth:`store`.

### Community 57 - "ProxyEngine (QThread)"
Cohesion: 0.22
Nodes (9): loop.call_soon_threadsafe Into Proxy Loop, Port Availability Pre-check, ProxyEngine (QThread), Qt Signals Cross-Thread Results, SystemExit Errorcheck Catch, Threading Model, mitmproxy Engine, Proxy Layer (proxy/) (+1 more)

### Community 58 - "Security Policy"
Cohesion: 0.25
Nodes (8): Handling the CA certificate, Reporting a vulnerability, Responsible and lawful use, Safe defaults and data handling, Scope, Security Policy, Supported versions, What to expect

### Community 59 - "._set_has_request"
Cohesion: 0.25
Nodes (4): Enable/disable the Send action while keeping the button visible. We…, Paint the Send button with the disabled cue when it has no request. Uses a…, Serializable snapshot of a session (for persistence)., SessionState

### Community 60 - "Public CA Certificate Export"
Cohesion: 0.36
Nodes (8): CA Private Key Protection, Focused Live Test Scripts, Public CA Certificate Export, Request Interception, cryptography Dependency, CA Certificate Handling Policy, Public-Only CA Export Invariant, Untrusted Captured Traffic

### Community 61 - "Release CI/CD Workflow"
Cohesion: 0.29
Nodes (8): Staging-First Git Workflow, PyInstaller Build Step, Release CI/CD Workflow, Rolling latest Pre-Release, Versioned v* Tag Release, Nuitka Alternative Compiler, Desktop App Packaging, Qt Module Excludes (size reduction)

### Community 62 - ".__init__"
Cohesion: 0.21
Nodes (4): QFrame, QWidget, Editable list of host patterns used by the Target scope panel., _ScopeList

### Community 63 - "WorkspaceManager"
Cohesion: 0.07
Nodes (32): main(), Application entry point. Creates the Qt application, builds the main window,…, Give Windows an explicit AppUserModelID so the taskbar uses our icon. Without…, _set_windows_app_id(), Bidoytu - an intercepting HTTP proxy tool. Base architecture: - Proxy/MITM…, Enables ``python -m bidoytu``., asset_path(), _assets_dir() (+24 more)

### Community 64 - "main_window.py"
Cohesion: 0.07
Nodes (23): finish(), poll_for_ca(), Verify the CA is generated in Bidoytu's confdir and can be exported. Starts the…, on_started(), Verify the capture addon stores DECODED bodies (gzip is undone). Routes a…, Verify starting the proxy on an occupied port produces a clean error signal…, Live test: RepeaterTab.load_from_record + Send performs a real request., host_matches_scope() (+15 more)

### Community 65 - "Contributing to Bidoytu"
Cohesion: 0.29
Nodes (7): Coding conventions, Contributing to Bidoytu, Development setup, Ground rules, Reporting bugs / security issues, Running the checks, Submitting changes

### Community 67 - "start_proxy_repro.py"
Cohesion: 0.47
Nodes (4): after_start(), finish(), Reproduce the 'start proxy crashes' path using the real MainWindow. Builds the…, send()

### Community 69 - ".restore_sessions"
Cohesion: 0.29
Nodes (5): Group, Path, A named, colored, collapsible collection of member sessions., Write all open sessions and their groups to ``path`` as JSON., Recreate sessions and groups saved by :meth:`save_sessions`.

### Community 70 - "httpx Async Client"
Cohesion: 0.40
Nodes (6): AsyncHttpSender, httpx Async Client, Intruder, Net Layer (net/), Repeater, httpx Dependency

### Community 73 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 75 - "._render"
Cohesion: 0.33
Nodes (3): hex_dump(), Switch how the remembered body is rendered and re-display it., Return a classic offset / hex / ASCII hex dump of ``data``.

### Community 78 - "graphify reference: add a URL and watch a folder"
Cohesion: 0.50
Nodes (3): For /graphify add, For --watch, graphify reference: add a URL and watch a folder

### Community 79 - "graphify reference: commit hook and native CLAUDE.md integration"
Cohesion: 0.50
Nodes (3): For git commit hook, For native CLAUDE.md integration, graphify reference: commit hook and native CLAUDE.md integration

### Community 80 - "graphify reference: incremental update and cluster-only"
Cohesion: 0.50
Nodes (3): For --cluster-only, For --update (incremental re-extraction), graphify reference: incremental update and cluster-only

### Community 83 - "parse_request_text"
Cohesion: 0.15
Nodes (13): absolute_url(), build_request_text(), host_from_headers_or_url(), parse_request_text(), parse_response_text(), ParsedRequest, ParsedResponse, Helpers for converting between raw HTTP text and structured parts. Used by… (+5 more)

### Community 86 - "._set_target_toggle_icon"
Cohesion: 0.40
Nodes (3): Collapse the Target panel to an arrow, or restore its full width., Use a painted arrow so the icon is stable across Qt styles., StandardPixmap

### Community 87 - "._show_raw"
Cohesion: 0.50
Nodes (3): Render a raw HTTP message, pretty-printing its body by content-type. Splits…, Split a raw HTTP message into (start_line, headers, body). Tolerant of both…, _split_http_message()

### Community 89 - "Publishing to PyPI (`pip install bidoytu`)"
Cohesion: 0.50
Nodes (4): Build / check the package locally, One-time setup on PyPI, Publishing to PyPI (`pip install bidoytu`), Releasing a new version to PyPI

### Community 90 - "DetailView"
Cohesion: 0.31
Nodes (3): DetailView, QWidget, Two MessageViews (request | response) with a shared soft-wrap toggle.

### Community 92 - "apply_theme"
Cohesion: 0.27
Nodes (9): QPalette, QProxyStyle, apply_theme(), _dark_palette(), _light_palette(), _NoFocusRectStyle, _palette_from_tokens(), Application style that suppresses the item-view focus rectangle globally. The… (+1 more)

### Community 93 - "ui_icon"
Cohesion: 0.12
Nodes (14): A small find bar that searches within a QPlainTextEdit. Reusable over any…, current_mode(), QIcon, Return the named color tokens for ``mode`` (falls back to dark)., Return a font-independent icon for compact UI controls., Return the theme mode currently applied to the application., tokens(), ui_icon() (+6 more)

### Community 94 - "Testing and development"
Cohesion: 0.67
Nodes (3): Contribution workflow, Fast verification, Testing and development

### Community 96 - "Getting started"
Cohesion: 0.67
Nodes (3): Getting started, Install from source, Requirements

### Community 97 - "How the application is put together"
Cohesion: 0.67
Nodes (3): How the application is put together, Startup sequence, Threading model

### Community 98 - "repeater_session.py"
Cohesion: 0.50
Nodes (3): HistoryEntry, A single Repeater session: one editable request + its response. Bundles the…, A request that was sent and (optionally) the response it produced.

### Community 100 - "_SavedFilterCombo"
Cohesion: 0.38
Nodes (4): QStyledItemDelegate, Paint saved-filter names with a compact delete affordance., _SavedFilterCombo, _SavedFilterDelegate

### Community 101 - "FindBar"
Cohesion: 0.23
Nodes (7): FindFlags, QKeyEvent, FindBar, QPlainTextEdit, QWidget, Incremental find controls bound to a target text edit., Reveal the bar, seed it with any selected text, and focus input.

### Community 103 - "QHBoxLayout"
Cohesion: 0.27
Nodes (5): QComboBox, QHBoxLayout, QPushButton, QWidget, QWidget

### Community 107 - ".save_state"
Cohesion: 0.32
Nodes (4): _protect_session(), Path, Persist the session, generated payloads, and interactions to JSON., Encrypt session keys with the current Windows user's DPAPI key.

### Community 108 - "HttpHighlighter"
Cohesion: 0.15
Nodes (12): QSyntaxHighlighter, QTextCharFormat, _fmt(), HttpHighlighter, Lightweight syntax highlighting for raw HTTP messages. Uses…, Highlights HTTP start-lines and headers., Re-color for a new theme mode and re-highlight the document., MarkerHighlighter (+4 more)

### Community 109 - ".set_group_send_actions"
Cohesion: 0.29
Nodes (3): Install (or clear) the dropdown's group-send options. ``actions`` is a list of…, Record which send mode the split button runs, and show it on the button., Grey out the dropdown's options when there is no request to send.

### Community 110 - "_Chip"
Cohesion: 0.26
Nodes (3): QMouseEvent, _Chip, A single clickable tab chip with an optional close button.

## Ambiguous Edges - Review These
- `Qt Isolation to ui/` → `Safe Default Localhost Bind`  [AMBIGUOUS]
  SECURITY.md · relation: conceptually_related_to
- `Public CA Certificate Export` → `CA Certificate Handling Policy`  [AMBIGUOUS]
  SECURITY.md · relation: references

## Knowledge Gaps
- **122 isolated node(s):** `bidoytu`, `Usage`, `What graphify is for`, `Step 0 - GitHub repos and multi-path merge (only if a URL or several paths)`, `Step 1 - Ensure graphify is installed` (+117 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 687 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **18 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Qt Isolation to ui/` and `Safe Default Localhost Bind`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Public CA Certificate Export` and `CA Certificate Handling Policy`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **Why does `FlowRecord` connect `FlowRecord` to `InterceptView`, `HistoryView`, `IntruderSession`, `InterceptActivityModel`, `RepeaterSession`, `intruder_session.py`, `ProxyEngine`, `CaptureAddon`, `MainWindow`, `AsyncHttpSender`, `IntruderTab`, `FlowTableModel`, `content_type_from_headers`, `._send`, `RepeaterTab`, `FlowRepository`, `main_window.py`, `DetailView`, `intercept_view.py`, `repeater_session.py`, `.cookies`?**
  _High betweenness centrality (0.192) - this node is a cross-community bridge._
- **Why does `AsyncHttpSender` connect `AsyncHttpSender` to `main_window.py`, `AttackRunner`, `CollaboratorTab`, `repeater_session.py`, `IntruderSession`, `RepeaterTab`, `InteractshClient`, `RepeaterSession`, `intruder_session.py`, `InteractionFilterProxy`, `collaborator_tab.py`, `MainWindow`, `ResultFilterProxy`, `IntruderTab`, `WrappingTabBar`, `WorkspaceManager`?**
  _High betweenness centrality (0.073) - this node is a cross-community bridge._
- **Why does `CollaboratorTab` connect `CollaboratorTab` to `main_window.py`, `MessageView`, `FindBar`, `QHBoxLayout`, `InteractshClient`, `.save_state`, `InteractionFilterProxy`, `collaborator_tab.py`, `MainWindow`, `AsyncHttpSender`, `._show_raw`, `InteractionsModel`, `WorkspaceManager`?**
  _High betweenness centrality (0.070) - this node is a cross-community bridge._
- **Are the 28 inferred relationships involving `FlowRecord` (e.g. with `test_intercept_view()` and `test_qt_and_proxy_apis()`) actually correct?**
  _`FlowRecord` has 28 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `RepeaterSession` (e.g. with `AsyncHttpSender` and `HttpResult`) actually correct?**
  _`RepeaterSession` has 7 INFERRED edges - model-reasoned connections that need verification._
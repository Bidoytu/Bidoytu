# Graph Report - Bidoytu  (2026-09-15)

## Corpus Check
- 65 files · ~129,293 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 5 file(s) not represented in the graph (top: (none) 3, .spec 1, .ico 1)

## Summary
- 1249 nodes · 2466 edges · 68 communities (59 shown, 9 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 186 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e1af5c96`
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
- FlowRecord
- FlowLayout
- body_format.py
- PayloadSetEditor
- ProxyTab
- interactsh.py
- parse_request_text
- _HTMLPretty
- AttackRunner
- InteractionsModel
- IntruderTab
- main_window.py
- FlowTableModel
- smoke_test.py
- _Chip
- ResultFilterProxy
- AsyncHttpSender
- ._open_or_recover
- .restore_state
- _LineNumberArea
- GroupDialog
- BodyStore
- WrappingTabBar
- RepeaterTab
- start_proxy_repro.py
- .cookies
- repeater_session.py
- intercept_response_live_test.py
- _GroupHeaderChip
- DetailView
- intercept_live_test.py
- InteractionFilterProxy
- _FlowHost
- proxy_live_test.py
- SendHandle
- Bidoytu
- config.py
- current_mode
- CLAUDE.md
- Path
- Building and releasing Bidoytu
- ._render
- ._show_raw
- Security Policy
- wrap_selection
- WorkspaceManager
- Contributing to Bidoytu
- ui/__init__.py
- collaborator_tab.py
- bidoytu
- ._update_group_send_menu
- AGENTS.md
- CONTRIBUTORS.md

## God Nodes (most connected - your core abstractions)
1. `FlowRecord` - 83 edges
2. `IntruderSession` - 60 edges
3. `RepeaterSession` - 57 edges
4. `CollaboratorTab` - 50 edges
5. `MainWindow` - 50 edges
6. `MessageView` - 45 edges
7. `InterceptView` - 41 edges
8. `RepeaterTab` - 39 edges
9. `AsyncHttpSender` - 34 edges
10. `InterceptActivityModel` - 29 edges

## Surprising Connections (you probably didn't know these)
- `test_storage_roundtrip()` --uses--> `FlowRecord`  [INFERRED]
  scripts/smoke_test.py → src/bidoytu/storage/models.py
- `test_storage_roundtrip()` --uses--> `FlowRepository`  [INFERRED]
  scripts/smoke_test.py → src/bidoytu/storage/repository.py
- `test_body_store()` --uses--> `BodyStore`  [INFERRED]
  scripts/smoke_test.py → src/bidoytu/storage/body_store.py
- `test_body_format()` --calls--> `content_type_from_headers()`  [INFERRED]
  scripts/smoke_test.py → src/bidoytu/ui/body_format.py
- `test_body_format()` --calls--> `format_body()`  [INFERRED]
  scripts/smoke_test.py → src/bidoytu/ui/body_format.py

## Import Cycles
- None detected.

## Communities (68 total, 9 thin omitted)

### Community 0 - "theme.py"
Cohesion: 0.06
Nodes (48): QColor, QPalette, QPixmap, QProxyStyle, QSyntaxHighlighter, QTextCharFormat, _fmt(), HttpHighlighter (+40 more)

### Community 1 - "InterceptView"
Cohesion: 0.06
Nodes (24): build_request_text(), build_response_text(), Assemble a raw HTTP response string from parts., Assemble a raw HTTP request string from parts. When ``host`` is provided, a…, InterceptView, QWidget, Size the activity table so URL fills the leftover width, while every column…, Whenever a column is resized, compensate its immediate right neighbor (or left… (+16 more)

### Community 2 - "MessageView"
Cohesion: 0.12
Nodes (7): MessageView, QPlainTextEdit, QRect, Return the full editor contents as text (for editable views)., Re-color the syntax highlighter for a new theme mode., Register an extra action shown in the right-click menu. The action is appended…, A monospace, syntax-highlighted view of a raw HTTP request/response.

### Community 3 - "CollaboratorTab"
Cohesion: 0.12
Nodes (6): CollaboratorTab, Slot, Attach a note (e.g. the target tab) to the most recent payload., Generate a payload, tag it with ``note``, and return the hostname. Used by…, Register with an Interactsh server, hand out payloads, show callbacks., Stop polling and deregister on application close (best-effort).

### Community 4 - "HistoryView"
Cohesion: 0.13
Nodes (10): QStyledItemDelegate, HistoryItemDelegate, Fully self-painted cells: soft row wash + slim accent bar, no style frame., HistoryView, QWidget, Slot, Whenever a column is resized, compensate its immediate right neighbor (or left…, Reflow the Path column to absorb the viewport's leftover width. Path is the… (+2 more)

### Community 5 - "AppConfig"
Cohesion: 0.10
Nodes (15): AppConfig, _default_data_dir(), Path, Top-level runtime configuration. Attributes: data_dir: Root directory for all…, JSON file holding persisted Repeater sessions across restarts., JSON file holding the last Intruder attack config across restarts., Return a per-user, per-OS data directory for Bidoytu., JSON file holding the Target scope for this workspace. (+7 more)

### Community 6 - "IntruderSession"
Cohesion: 0.07
Nodes (13): find_markers(), Return the template with all ``§`` markers removed (defaults kept)., Split a ``§``-marked template into (clean_text, markers). Markers come in…, strip_markers(), IntruderSession, Slot, Grow/shrink the payload-set tabs to exactly ``n`` (min 1)., Pitchfork/cluster bomb use one set per position; others use one. (+5 more)

### Community 7 - "InterceptActivityModel"
Cohesion: 0.08
Nodes (14): ActivityRow, InterceptActivityModel, Orientation, QAbstractTableModel, QModelIndex, Log a paused (pending) request. Returns its row index., Log a paused (pending) response. Returns its row index., True if the row is a still-pending request or response. (+6 more)

### Community 8 - "attack.py"
Cohesion: 0.12
Nodes (28): count_jobs(), iter_jobs(), Marker, PayloadSet, Intruder attack model: markers, attack types, and request building. Qt-free so…, Insert ``values`` into ``clean_text`` at each marker (right-to-left). Working…, Best-effort total request count for a configured attack., Yield an :class:`AttackJob` per request for the configured attack.… (+20 more)

### Community 9 - "InteractshClient"
Cohesion: 0.08
Nodes (17): Exception, InteractshClient, _cb(), _cb(), InteractshError, _now_iso(), Everything needed to resume / persist a registered session., Raised for registration / polling / crypto failures. (+9 more)

### Community 10 - "RepeaterSession"
Cohesion: 0.10
Nodes (10): QMenu, HttpResult, Slot, Install (or clear) the dropdown's group-send options. ``actions`` is a list of…, Record which send mode the split button runs, and show it on the button., Public entry point for the container to send this tab's request., Ask the provider for a payload and insert it at the cursor., Build a FlowRecord from the current (edited) request text. (+2 more)

### Community 11 - "intruder_session.py"
Cohesion: 0.12
Nodes (13): Pattern, _compile(), GrepConfig, Drives an Intruder attack: iterate jobs, send them, collect results. The runner…, How to derive match/extract columns from each response., One completed request in the results table., ResultRow, IntruderResultsModel (+5 more)

### Community 12 - "ProxyEngine"
Cohesion: 0.07
Nodes (12): QThread, ProxyEngine, Update target scope immediately, including while the proxy runs., Toggle the global 'intercept responses' behavior., Arm a one-shot response intercept for a single flow., Forward a paused request, optionally with edited raw request text., Drop a paused request., Forward a paused response, optionally with edited raw response text. (+4 more)

### Community 13 - "CaptureAddon"
Cohesion: 0.10
Nodes (15): FlowCallback, HTTPFlow, InterceptCallback, CaptureAddon, _PendingFlow, Arm a one-shot response intercept for a single flow (Burp's "Response to this…, Apply a UI decision to a paused request. Runs on the proxy loop., Apply a UI decision to a paused response. Runs on the proxy loop. (+7 more)

### Community 14 - "MainWindow"
Cohesion: 0.07
Nodes (14): QMainWindow, CaCertDialog, Path, QDialog, Dialog for exporting and installing the proxy's CA certificate. To intercept…, Shows CA status, an export button, and install instructions., MainWindow, Slot (+6 more)

### Community 15 - "FlowRecord"
Cohesion: 0.13
Nodes (10): Row, FlowRecord, A single captured HTTP request/response exchange. Body payloads are represented…, The response content type without parameters (e.g. ``text/html``)., File extension derived from the request path (without the dot). The query…, FlowRepository, Insert a new flow and return its assigned primary key., Update an existing flow (matched by ``flow_id``). (+2 more)

### Community 16 - "FlowLayout"
Cohesion: 0.15
Nodes (7): Orientations, QLayout, QLayoutItem, FlowLayout, QRect, QSize, QWidget

### Community 17 - "body_format.py"
Cohesion: 0.20
Nodes (15): format_body(), _format_c_like(), _format_css(), _format_form(), _format_html(), _format_js(), _format_json(), _format_xml() (+7 more)

### Community 18 - "PayloadSetEditor"
Cohesion: 0.15
Nodes (6): PayloadSetEditor, ProcessingRuleDialog, QDialog, QWidget, Edit one payload set: a generator plus a processing-rule pipeline., Configure a single :class:`ProcessingRule`.

### Community 19 - "ProxyTab"
Cohesion: 0.06
Nodes (24): FindFlags, QHBoxLayout, QKeyEvent, QPushButton, QWidget, Build a titled pane (label + find bar + view), matching Repeater., FindBar, QPlainTextEdit (+16 more)

### Community 20 - "interactsh.py"
Cohesion: 0.40
Nodes (5): _encode_xid(), generate_xid(), Interactsh (OAST) client for the Collaborator feature. This is a small, Qt-free…, Return a 20-char XID string. XID layout: 4-byte time, 3-byte machine id, 2-byte…, Encode 12 raw bytes into the 20-char XID base32 representation.

### Community 21 - "parse_request_text"
Cohesion: 0.18
Nodes (11): absolute_url(), host_from_headers_or_url(), parse_request_text(), parse_response_text(), ParsedRequest, ParsedResponse, Helpers for converting between raw HTTP text and structured parts. Used by…, Parse raw HTTP response text into a :class:`ParsedResponse`. Tolerant of both… (+3 more)

### Community 22 - "_HTMLPretty"
Cohesion: 0.22
Nodes (4): HTMLParser, _HTMLPretty, Lenient HTML pretty-printer built on the stdlib parser. Emits nicely indented…, Close a preceding sibling with an optional end tag, if applicable.

### Community 23 - "AttackRunner"
Cohesion: 0.20
Nodes (7): QObject, AttackJob, One request to send: the substituted text and the payloads used., AttackRunner, Slot, Launch requests until we hit the concurrency cap or run out., Runs one attack, emitting a :class:`ResultRow` per completed request.

### Community 24 - "InteractionsModel"
Cohesion: 0.14
Nodes (12): Interaction, A single out-of-band interaction reported by the server., InteractionRow, InteractionsModel, protocol_color(), QAbstractTableModel, QModelIndex, Table model + filter proxy for Collaborator (OAST) interactions.… (+4 more)

### Community 25 - "IntruderTab"
Cohesion: 0.15
Nodes (8): IntruderTab, Path, QWidget, Close every Intruder tab., Open a new session tab populated from a captured flow., Write every open session to ``path`` as JSON (list of snapshots)., Recreate the sessions saved by :meth:`save_state`. Accepts both the multi-…, Holds multiple :class:`IntruderSession` instances in a tab strip.

### Community 26 - "main_window.py"
Cohesion: 0.12
Nodes (13): finish(), poll_for_ca(), Verify the CA is generated in Bidoytu's confdir and can be exported. Starts the…, On-disk store for large request/response bodies. Rather than storing large…, Storage layer: SQLite persistence + on-disk body store., Plain data structures passed between the proxy engine, storage, and UI. These…, SQLite persistence for captured flows. Uses the stdlib ``sqlite3`` module…, Custom QAbstractTableModel backing the traffic history view. We use a hand-… (+5 more)

### Community 27 - "FlowTableModel"
Cohesion: 0.17
Nodes (6): FlowTableModel, Orientation, QAbstractTableModel, QModelIndex, Replace all rows (e.g. when loading history from the database)., Add a new record, or update an existing one in place. Called from the UI thread…

### Community 28 - "smoke_test.py"
Cohesion: 0.35
Nodes (11): QApplication, main(), Path, Import + wiring smoke test (no live proxy, no visible window). Verifies: - all…, test_body_format(), test_body_store(), test_http_utils(), test_intercept_view() (+3 more)

### Community 29 - "_Chip"
Cohesion: 0.26
Nodes (3): QMouseEvent, _Chip, A single clickable tab chip with an optional close button.

### Community 30 - "ResultFilterProxy"
Cohesion: 0.22
Nodes (3): QSortFilterProxyModel, Filter results by status, min length, matched-only, and a text needle., ResultFilterProxy

### Community 31 - "AsyncHttpSender"
Cohesion: 0.17
Nodes (5): ResultCallback, AsyncHttpSender, _schedule(), Schedule a request; ``callback`` is invoked on the sender thread. Returns a…, Owns a background event loop running httpx.AsyncClient instances.

### Community 32 - "._open_or_recover"
Cohesion: 0.29
Nodes (4): Connection, Path, Move the corrupt database and SQLite sidecars to a safe backup., Open and validate the database, recovering from SQLite corruption. A damaged…

### Community 34 - "_LineNumberArea"
Cohesion: 0.29
Nodes (4): _LineNumberArea, QSize, QWidget, Gutter widget that paints line numbers for its owning MessageView.

### Community 35 - "GroupDialog"
Cohesion: 0.22
Nodes (4): GroupDialog, QDialog, Dialog for adding Repeater request tabs to a named, colored group. Presents a…, Collect a group name, member tabs, and a color.

### Community 36 - "BodyStore"
Cohesion: 0.25
Nodes (5): BodyStore, Path, Content-addressed file store for body payloads. Files are sharded into…, Write ``data`` to the store and return its relative path. Identical content…, Read body content previously returned by :meth:`store`.

### Community 37 - "WrappingTabBar"
Cohesion: 0.26
Nodes (5): QScrollArea, QSize, Group-aware, wrapping tab bar composed of chip widgets., Rebuild the whole bar from the container's model. Args: order: list of keys…, WrappingTabBar

### Community 38 - "RepeaterTab"
Cohesion: 0.11
Nodes (13): Group, Path, QWidget, Clone a session's request into a new tab, named ``base (n)``., Return ``base (n)`` with the smallest unused positive integer n., Delete a group along with all request tabs it contains., Close every request tab and remove all groups., A named, colored, collapsible collection of member sessions. (+5 more)

### Community 39 - "start_proxy_repro.py"
Cohesion: 0.47
Nodes (4): after_start(), finish(), Reproduce the 'start proxy crashes' path using the real MainWindow. Builds the…, send()

### Community 41 - "repeater_session.py"
Cohesion: 0.14
Nodes (9): Live test: RepeaterTab.load_from_record + Send performs a real request., Async HTTP sender for Repeater/Intruder. Runs an ``httpx.AsyncClient`` on a…, Networking helpers (async HTTP client for Repeater/Intruder)., HistoryEntry, A single Repeater session: one editable request + its response. Bundles the…, A request that was sent and (optionally) the response it produced., Serializable snapshot of a session (for persistence)., SessionState (+1 more)

### Community 42 - "intercept_response_live_test.py"
Cohesion: 0.31
Nodes (7): check_done(), do_forward(), finish(), on_intercepted(), on_started(), Live: intercept a request via the real MainWindow, forward it, and confirm the…, send()

### Community 44 - "DetailView"
Cohesion: 0.31
Nodes (3): DetailView, QWidget, Two MessageViews (request | response) with a shared soft-wrap toggle.

### Community 45 - "intercept_live_test.py"
Cohesion: 0.36
Nodes (6): finish(), on_captured(), on_intercepted(), on_started(), Live test: interception pauses a request, and forward/drop resolve it.…, send()

### Community 46 - "InteractionFilterProxy"
Cohesion: 0.22
Nodes (5): CollaboratorConfig, Settings for the Collaborator (out-of-band interaction) feature. Attributes:…, InteractionFilterProxy, QSortFilterProxyModel, Filter interactions by protocol and a free-text needle.

### Community 47 - "_FlowHost"
Cohesion: 0.38
Nodes (4): QResizeEvent, _FlowHost, QWidget, Host widget whose height tracks its FlowLayout's height-for-width. A…

### Community 48 - "proxy_live_test.py"
Cohesion: 0.33
Nodes (3): on_started(), Live end-to-end test: start the ProxyEngine thread and route a real request…, send_request()

### Community 49 - "SendHandle"
Cohesion: 0.25
Nodes (4): AbstractEventLoop, A cancellable handle to an in-flight request. The handle wraps the…, SendHandle, Task

### Community 50 - "Bidoytu"
Cohesion: 0.18
Nodes (10): Architecture, Bidoytu, Development workflow, Highlights, License, Packaging and releases, Quick start, Requirements (+2 more)

### Community 51 - "config.py"
Cohesion: 0.13
Nodes (13): on_started(), Verify the capture addon stores DECODED bodies (gzip is undone). Routes a…, Verify starting the proxy on an occupied port produces a clean error signal…, host_matches_scope(), matches(), _normalise_scope_entry(), ProxyConfig, Application configuration and filesystem paths. Everything the app writes… (+5 more)

### Community 52 - "current_mode"
Cohesion: 0.24
Nodes (6): A wrapping flow layout: children flow left-to-right and wrap to new rows. This…, current_mode(), Return the named color tokens for ``mode`` (falls back to dark)., Return the theme mode currently applied to the application., tokens(), A wrapping, group-aware tab bar built from individual chip widgets. Unlike…

### Community 53 - "CLAUDE.md"
Cohesion: 0.20
Nodes (8): Architecture and layering (respect this), Conventions, Git workflow, Gotchas learned the hard way, Tech stack, Verifying changes (always do this), What Bidoytu is, Where things live

### Community 54 - "Path"
Cohesion: 0.38
Nodes (3): Path, Persist the session, generated payloads, and interactions to JSON., _session_to_dict()

### Community 55 - "Building and releasing Bidoytu"
Cohesion: 0.20
Nodes (9): Build (Windows or Linux), Building and releasing Bidoytu, Cutting version 1.0.0, How releases work (CI/CD), Local builds (optional), Notes, Nuitka (alternative compiler), Prerequisites (+1 more)

### Community 56 - "._render"
Cohesion: 0.33
Nodes (3): hex_dump(), Switch how the remembered body is rendered and re-display it., Return a classic offset / hex / ASCII hex dump of ``data``.

### Community 57 - "._show_raw"
Cohesion: 0.50
Nodes (3): Render a raw HTTP message, pretty-printing its body by content-type. Splits…, Split a raw HTTP message into (start_line, headers, body). Tolerant of both…, _split_http_message()

### Community 58 - "Security Policy"
Cohesion: 0.22
Nodes (8): Handling the CA certificate, Reporting a vulnerability, Responsible and lawful use, Safe defaults and data handling, Scope, Security Policy, Supported versions, What to expect

### Community 63 - "WorkspaceManager"
Cohesion: 0.07
Nodes (32): main(), Application entry point. Creates the Qt application, builds the main window,…, Give Windows an explicit AppUserModelID so the taskbar uses our icon. Without…, _set_windows_app_id(), Bidoytu - an intercepting HTTP proxy tool. Base architecture: - Proxy/MITM…, Enables ``python -m bidoytu``., asset_path(), _assets_dir() (+24 more)

### Community 65 - "Contributing to Bidoytu"
Cohesion: 0.25
Nodes (7): Branches and pull requests, Checks, Contributing to Bidoytu, Design rules, License, Local setup, Security issues

### Community 67 - "collaborator_tab.py"
Cohesion: 0.15
Nodes (10): ensure_host_header(), _headers_have(), Return True if the raw header block already contains ``name`` (case-…, Return the header block with a ``Host`` header guaranteed to be present. If…, content_type_from_headers(), Extract the Content-Type value from a raw header block (case-insensitive)., Collaborator tab: out-of-band (OAST) interaction listener. Bidoytu's equivalent…, Reusable side-by-side request/response viewer. Used by the Proxy history, the… (+2 more)

## Knowledge Gaps
- **39 isolated node(s):** `bidoytu`, `graphify`, `What Bidoytu is`, `Tech stack`, `Git workflow` (+34 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 493 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `FlowRecord` connect `FlowRecord` to `InterceptView`, `HistoryView`, `IntruderSession`, `InterceptActivityModel`, `RepeaterSession`, `intruder_session.py`, `ProxyEngine`, `CaptureAddon`, `MainWindow`, `IntruderTab`, `main_window.py`, `FlowTableModel`, `smoke_test.py`, `AsyncHttpSender`, `RepeaterTab`, `.cookies`, `repeater_session.py`, `DetailView`, `config.py`, `collaborator_tab.py`?**
  _High betweenness centrality (0.216) - this node is a cross-community bridge._
- **Why does `IntruderSession` connect `IntruderSession` to `theme.py`, `MessageView`, `attack.py`, `intruder_session.py`, `FlowRecord`, `PayloadSetEditor`, `ProxyTab`, `parse_request_text`, `AttackRunner`, `IntruderTab`, `main_window.py`, `wrap_selection`, `ResultFilterProxy`, `AsyncHttpSender`?**
  _High betweenness centrality (0.109) - this node is a cross-community bridge._
- **Why does `CollaboratorTab` connect `CollaboratorTab` to `.restore_state`, `MessageView`, `collaborator_tab.py`, `InteractshClient`, `InteractionFilterProxy`, `MainWindow`, `ProxyTab`, `Path`, `InteractionsModel`, `._show_raw`, `main_window.py`, `AsyncHttpSender`?**
  _High betweenness centrality (0.093) - this node is a cross-community bridge._
- **Are the 17 inferred relationships involving `FlowRecord` (e.g. with `test_intercept_view()` and `test_qt_and_proxy_apis()`) actually correct?**
  _`FlowRecord` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `IntruderSession` (e.g. with `AsyncHttpSender` and `PayloadSet`) actually correct?**
  _`IntruderSession` has 15 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `RepeaterSession` (e.g. with `AsyncHttpSender` and `HttpResult`) actually correct?**
  _`RepeaterSession` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `CollaboratorTab` (e.g. with `CollaboratorConfig` and `AsyncHttpSender`) actually correct?**
  _`CollaboratorTab` has 10 INFERRED edges - model-reasoned connections that need verification._
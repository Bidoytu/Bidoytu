# Graph Report - Bidoytu  (2026-09-14)

## Corpus Check
- 64 files · ~126,427 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 5 file(s) not represented in the graph (top: (none) 3, .spec 1, .ico 1)

## Summary
- 1163 nodes · 2282 edges · 76 communities (61 shown, 15 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 175 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `4845e895`
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
- PayloadSetEditor
- InteractshClient
- RepeaterTab
- IntruderResultsModel
- ProxyEngine
- CaptureAddon
- MainWindow
- FlowRepository
- FlowLayout
- QHBoxLayout
- engine.py
- ._ensure_payload_sets
- collaborator_tab.py
- RepeaterSession
- _HTMLPretty
- AttackRunner
- InteractionsModel
- IntruderTab
- models.py
- content_type_from_headers
- body_format.py
- _Chip
- FlowTableModel
- AsyncHttpSender
- intruder_session.py
- FindBar
- BodyStore
- GroupDialog
- QMenu
- WrappingTabBar
- smoke_test.py
- ._new_session
- main_window.py
- CaCertDialog
- intercept_response_live_test.py
- _GroupHeaderChip
- SendHandle
- intercept_live_test.py
- InteractionFilterProxy
- _FlowHost
- proxy_live_test.py
- ._update_group_send_menu
- Bidoytu
- start_proxy_repro.py
- current_mode
- CLAUDE.md
- .__init__
- Building and releasing Bidoytu
- gzip_decode_test.py
- Interaction
- Security Policy
- ._show_raw
- .__init__
- .__init__
- FlowRecord
- app.py
- ResultFilterProxy
- Contributing to Bidoytu
- ui/__init__.py
- logo_path
- bidoytu
- capture_addon.py
- ._duplicate_session
- AGENTS.md
- CONTRIBUTORS.md
- .intercept_response_for
- .resolve
- .set_intercept_responses

## God Nodes (most connected - your core abstractions)
1. `FlowRecord` - 83 edges
2. `IntruderSession` - 60 edges
3. `RepeaterSession` - 57 edges
4. `CollaboratorTab` - 50 edges
5. `MainWindow` - 46 edges
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

## Communities (76 total, 15 thin omitted)

### Community 0 - "theme.py"
Cohesion: 0.05
Nodes (50): QColor, QPalette, QPixmap, QProxyStyle, QSyntaxHighlighter, QTextCharFormat, _fmt(), HttpHighlighter (+42 more)

### Community 1 - "InterceptView"
Cohesion: 0.07
Nodes (20): InterceptView, QWidget, Size the activity table so URL fills the leftover width, while every column…, Whenever a column is resized, compensate its immediate right neighbor (or left…, Reflow the URL column to absorb the viewport's leftover width. URL is the…, Forward every still-pending flow, then reset the panel. Called when…, A request was paused by the proxy; add it to the table., A response was paused by the proxy; add it to the table. (+12 more)

### Community 2 - "MessageView"
Cohesion: 0.06
Nodes (17): DetailView, QWidget, Two MessageViews (request | response) with a shared soft-wrap toggle., hex_dump(), _LineNumberArea, MessageView, QPlainTextEdit, QRect (+9 more)

### Community 3 - "CollaboratorTab"
Cohesion: 0.08
Nodes (10): CollaboratorTab, Path, QWidget, Slot, Build a titled pane (label + find bar + view), matching Repeater., Attach a note (e.g. the target tab) to the most recent payload., Generate a payload, tag it with ``note``, and return the hostname. Used by…, Persist the session, generated payloads, and interactions to JSON. (+2 more)

### Community 4 - "HistoryView"
Cohesion: 0.08
Nodes (15): QStyledItemDelegate, HistoryItemDelegate, Fully self-painted cells: soft row wash + slim accent bar, no style frame., HistoryView, QWidget, Slot, Whenever a column is resized, compensate its immediate right neighbor (or left…, Reflow the Path column to absorb the viewport's leftover width. Path is the… (+7 more)

### Community 5 - "AppConfig"
Cohesion: 0.15
Nodes (10): AppConfig, Path, JSON file holding Collaborator session state across restarts. Stores the active…, Directory where mitmproxy stores its generated CA and certs. We keep it under…, PEM-encoded CA certificate (for Firefox, curl, most Linux tools)., DER/.cer CA certificate (convenient for the Windows cert store)., Create the data, body, and CA directories if they do not exist., Top-level runtime configuration. Attributes: data_dir: Root directory for all… (+2 more)

### Community 6 - "IntruderSession"
Cohesion: 0.10
Nodes (6): IntruderSession, Slot, Return a JSON-serializable snapshot of this session., Restore this session from a snapshot produced by :meth:`to_state`., Build a FlowRecord from the template (payload markers removed)., One Intruder attack: template + positions + payload sets + results.

### Community 7 - "InterceptActivityModel"
Cohesion: 0.08
Nodes (14): ActivityRow, InterceptActivityModel, Orientation, QAbstractTableModel, QModelIndex, Log a paused (pending) request. Returns its row index., Log a paused (pending) response. Returns its row index., True if the row is a still-pending request or response. (+6 more)

### Community 8 - "PayloadSetEditor"
Cohesion: 0.06
Nodes (41): count_jobs(), find_markers(), iter_jobs(), Marker, PayloadSet, Intruder attack model: markers, attack types, and request building. Qt-free so…, Return the template with all ``§`` markers removed (defaults kept)., Wrap the ``[sel_start, sel_end)`` span of ``text`` in ``§`` markers. Used by… (+33 more)

### Community 9 - "InteractshClient"
Cohesion: 0.10
Nodes (13): Exception, InteractshClient, _cb(), _cb(), InteractshError, Raised for registration / polling / crypto failures., Register with, generate payloads for, and poll an Interactsh server. The client…, Generate a keypair and register against the first working server. ``servers``… (+5 more)

### Community 10 - "RepeaterTab"
Cohesion: 0.22
Nodes (5): QWidget, Delete a group along with all request tabs it contains., Close every request tab and remove all groups., Holds multiple :class:`RepeaterSession` instances with a wrapping bar., RepeaterTab

### Community 11 - "IntruderResultsModel"
Cohesion: 0.16
Nodes (7): One completed request in the results table., ResultRow, IntruderResultsModel, QAbstractTableModel, QModelIndex, Table model + filter proxy for Intruder attack results.…, status_color()

### Community 12 - "ProxyEngine"
Cohesion: 0.08
Nodes (10): QThread, ProxyEngine, Toggle the global 'intercept responses' behavior., Arm a one-shot response intercept for a single flow., Forward a paused request, optionally with edited raw request text., Drop a paused request., Forward a paused response, optionally with edited raw response text., Drop a paused response. (+2 more)

### Community 13 - "CaptureAddon"
Cohesion: 0.22
Nodes (7): HTTPFlow, CaptureAddon, Apply a UI decision to a paused response. Runs on the proxy loop., Rewrite a flow's request from edited raw text before forwarding., Rewrite a flow's response from edited raw text before forwarding., Return the decoded (decompressed) body; fall back to raw bytes., Emits FlowRecords and optionally pauses flows for interception.

### Community 14 - "MainWindow"
Cohesion: 0.15
Nodes (5): QMainWindow, MainWindow, Slot, Return a fresh Collaborator payload host, or None if unavailable. Called by…, Load a file-backed request body inline so editors can show it.

### Community 15 - "FlowRepository"
Cohesion: 0.14
Nodes (7): Row, FlowRepository, Path, Insert if new, otherwise update. Returns the row id., CRUD access to the ``flows`` table., Insert a new flow and return its assigned primary key., Update an existing flow (matched by ``flow_id``).

### Community 16 - "FlowLayout"
Cohesion: 0.15
Nodes (7): Orientations, QLayout, QLayoutItem, FlowLayout, QRect, QSize, QWidget

### Community 17 - "QHBoxLayout"
Cohesion: 0.40
Nodes (3): QHBoxLayout, QPushButton, QWidget

### Community 18 - "engine.py"
Cohesion: 0.25
Nodes (5): Verify starting the proxy on an occupied port produces a clean error signal…, ProxyConfig, Listen settings for the mitmproxy engine., Runs mitmproxy inside a dedicated QThread. Design: - mitmproxy is asyncio-…, Proxy engine package (mitmproxy running inside a QThread).

### Community 20 - "collaborator_tab.py"
Cohesion: 0.14
Nodes (15): CollaboratorConfig, Settings for the Collaborator (out-of-band interaction) feature. Attributes:…, _encode_xid(), generate_xid(), Interactsh (OAST) client for the Collaborator feature. This is a small, Qt-free…, Everything needed to resume / persist a registered session., Return a 20-char XID string. XID layout: 4-byte time, 3-byte machine id, 2-byte…, Encode 12 raw bytes into the 20-char XID base32 representation. (+7 more)

### Community 21 - "RepeaterSession"
Cohesion: 0.13
Nodes (7): HistoryEntry, QWidget, Slot, Public entry point for the container to send this tab's request., A request that was sent and (optionally) the response it produced., One request/response pane with full Repeater controls., RepeaterSession

### Community 22 - "_HTMLPretty"
Cohesion: 0.22
Nodes (4): HTMLParser, _HTMLPretty, Lenient HTML pretty-printer built on the stdlib parser. Emits nicely indented…, Close a preceding sibling with an optional end tag, if applicable.

### Community 23 - "AttackRunner"
Cohesion: 0.20
Nodes (8): QObject, HttpResult, AttackJob, One request to send: the substituted text and the payloads used., AttackRunner, Slot, Launch requests until we hit the concurrency cap or run out., Runs one attack, emitting a :class:`ResultRow` per completed request.

### Community 24 - "InteractionsModel"
Cohesion: 0.18
Nodes (7): InteractionRow, InteractionsModel, QAbstractTableModel, QModelIndex, Render an ISO timestamp as HH:MM:SS, falling back to the raw string., A received interaction plus the display metadata we derive from it., _short_time()

### Community 25 - "IntruderTab"
Cohesion: 0.15
Nodes (8): IntruderTab, Path, QWidget, Close every Intruder tab., Open a new session tab populated from a captured flow., Write every open session to ``path`` as JSON (list of snapshots)., Recreate the sessions saved by :meth:`save_state`. Accepts both the multi-…, Holds multiple :class:`IntruderSession` instances in a tab strip.

### Community 26 - "models.py"
Cohesion: 0.13
Nodes (10): Live test: RepeaterTab.load_from_record + Send performs a real request., build_response_text(), Assemble a raw HTTP response string from parts., Plain data structures passed between the proxy engine, storage, and UI. These…, Custom QAbstractTableModel backing the traffic history view. We use a hand-…, HTTP history: the traffic table plus a request/response detail view. Emits a…, Table model for the Intercept tab's activity log. Each intercepted request…, Intercept panel: pause, edit, and forward/drop in-flight requests. When… (+2 more)

### Community 27 - "content_type_from_headers"
Cohesion: 0.25
Nodes (7): ensure_host_header(), _headers_have(), Return True if the raw header block already contains ``name`` (case-…, Return the header block with a ``Host`` header guaranteed to be present. If…, content_type_from_headers(), Extract the Content-Type value from a raw header block (case-insensitive)., Reusable side-by-side request/response viewer. Used by the Proxy history, the…

### Community 28 - "body_format.py"
Cohesion: 0.18
Nodes (16): format_body(), _format_c_like(), _format_css(), _format_form(), _format_html(), _format_js(), _format_json(), _format_xml() (+8 more)

### Community 29 - "_Chip"
Cohesion: 0.26
Nodes (3): QMouseEvent, _Chip, A single clickable tab chip with an optional close button.

### Community 30 - "FlowTableModel"
Cohesion: 0.17
Nodes (6): FlowTableModel, Orientation, QAbstractTableModel, QModelIndex, Replace all rows (e.g. when loading history from the database)., Add a new record, or update an existing one in place. Called from the UI thread…

### Community 31 - "AsyncHttpSender"
Cohesion: 0.14
Nodes (7): ResultCallback, AsyncHttpSender, _schedule(), Schedule a request; ``callback`` is invoked on the sender thread. Returns a…, Owns a background event loop running httpx.AsyncClient instances., Networking helpers (async HTTP client for Repeater/Intruder)., Intruder tab: a container of independent attack sessions. Each "Send to…

### Community 32 - "intruder_session.py"
Cohesion: 0.13
Nodes (17): absolute_url(), build_request_text(), host_from_headers_or_url(), parse_request_text(), ParsedRequest, Helpers for converting between raw HTTP text and structured parts. Used by…, Reconstruct an absolute URL from flow parts (path may be absolute)., Determine (scheme, host, port, path) for sending a parsed request. Prefers an… (+9 more)

### Community 33 - "FindBar"
Cohesion: 0.23
Nodes (7): FindFlags, QKeyEvent, FindBar, QPlainTextEdit, QWidget, Incremental find controls bound to a target text edit., Reveal the bar, seed it with any selected text, and focus input.

### Community 34 - "BodyStore"
Cohesion: 0.15
Nodes (8): BodyStore, Path, On-disk store for large request/response bodies. Rather than storing large…, Content-addressed file store for body payloads. Files are sharded into…, Write ``data`` to the store and return its relative path. Identical content…, Read body content previously returned by :meth:`store`., Storage layer: SQLite persistence + on-disk body store., SQLite persistence for captured flows. Uses the stdlib ``sqlite3`` module…

### Community 35 - "GroupDialog"
Cohesion: 0.22
Nodes (4): GroupDialog, QDialog, Dialog for adding Repeater request tabs to a named, colored group. Presents a…, Collect a group name, member tabs, and a color.

### Community 36 - "QMenu"
Cohesion: 0.17
Nodes (5): QMenu, Install (or clear) the dropdown's group-send options. ``actions`` is a list of…, Record which send mode the split button runs, and show it on the button., Ask the provider for a payload and insert it at the cursor., Build a FlowRecord from the current (edited) request text.

### Community 37 - "WrappingTabBar"
Cohesion: 0.26
Nodes (5): QScrollArea, QSize, Group-aware, wrapping tab bar composed of chip widgets., Rebuild the whole bar from the container's model. Args: order: list of keys…, WrappingTabBar

### Community 38 - "smoke_test.py"
Cohesion: 0.36
Nodes (10): QApplication, main(), Path, Import + wiring smoke test (no live proxy, no visible window). Verifies: - all…, test_body_format(), test_body_store(), test_http_utils(), test_intercept_view() (+2 more)

### Community 39 - "._new_session"
Cohesion: 0.13
Nodes (8): Serializable snapshot of a session (for persistence)., SessionState, Group, Path, A named, colored, collapsible collection of member sessions., Open a new session tab populated from a captured flow., Write all open sessions and their groups to ``path`` as JSON., Recreate sessions and groups saved by :meth:`save_sessions`.

### Community 40 - "main_window.py"
Cohesion: 0.20
Nodes (8): finish(), poll_for_ca(), Verify the CA is generated in Bidoytu's confdir and can be exported. Starts the…, _default_data_dir(), Application configuration and filesystem paths. Everything the app writes…, Return a per-user, per-OS data directory for Bidoytu., Bidoytu - an intercepting HTTP proxy tool. Base architecture: - Proxy/MITM…, Main application window. Top-level layout is a QTabWidget with four tabs: -…

### Community 41 - "CaCertDialog"
Cohesion: 0.33
Nodes (5): CaCertDialog, Path, QDialog, Dialog for exporting and installing the proxy's CA certificate. To intercept…, Shows CA status, an export button, and install instructions.

### Community 42 - "intercept_response_live_test.py"
Cohesion: 0.31
Nodes (7): check_done(), do_forward(), finish(), on_intercepted(), on_started(), Live: intercept a request via the real MainWindow, forward it, and confirm the…, send()

### Community 44 - "SendHandle"
Cohesion: 0.25
Nodes (4): AbstractEventLoop, A cancellable handle to an in-flight request. The handle wraps the…, SendHandle, Task

### Community 45 - "intercept_live_test.py"
Cohesion: 0.36
Nodes (6): finish(), on_captured(), on_intercepted(), on_started(), Live test: interception pauses a request, and forward/drop resolve it.…, send()

### Community 46 - "InteractionFilterProxy"
Cohesion: 0.29
Nodes (3): InteractionFilterProxy, QSortFilterProxyModel, Filter interactions by protocol and a free-text needle.

### Community 47 - "_FlowHost"
Cohesion: 0.38
Nodes (4): QResizeEvent, _FlowHost, QWidget, Host widget whose height tracks its FlowLayout's height-for-width. A…

### Community 48 - "proxy_live_test.py"
Cohesion: 0.33
Nodes (3): on_started(), Live end-to-end test: start the ProxyEngine thread and route a real request…, send_request()

### Community 50 - "Bidoytu"
Cohesion: 0.18
Nodes (10): Architecture, Bidoytu, Development workflow, Highlights, License, Packaging and releases, Quick start, Requirements (+2 more)

### Community 51 - "start_proxy_repro.py"
Cohesion: 0.47
Nodes (4): after_start(), finish(), Reproduce the 'start proxy crashes' path using the real MainWindow. Builds the…, send()

### Community 52 - "current_mode"
Cohesion: 0.24
Nodes (6): A wrapping flow layout: children flow left-to-right and wrap to new rows. This…, current_mode(), Return the named color tokens for ``mode`` (falls back to dark)., Return the theme mode currently applied to the application., tokens(), A wrapping, group-aware tab bar built from individual chip widgets. Unlike…

### Community 53 - "CLAUDE.md"
Cohesion: 0.20
Nodes (8): Architecture and layering (respect this), Conventions, Git workflow, Gotchas learned the hard way, Tech stack, Verifying changes (always do this), What Bidoytu is, Where things live

### Community 55 - "Building and releasing Bidoytu"
Cohesion: 0.20
Nodes (9): Build (Windows or Linux), Building and releasing Bidoytu, Cutting version 1.0.0, How releases work (CI/CD), Local builds (optional), Notes, Nuitka (alternative compiler), Prerequisites (+1 more)

### Community 57 - "Interaction"
Cohesion: 0.20
Nodes (5): Interaction, _now_iso(), A single out-of-band interaction reported by the server., Best-effort correlate an interaction back to a generated payload., Restore a session saved by :meth:`save_state` and re-register it.

### Community 58 - "Security Policy"
Cohesion: 0.22
Nodes (8): Handling the CA certificate, Reporting a vulnerability, Responsible and lawful use, Safe defaults and data handling, Scope, Security Policy, Supported versions, What to expect

### Community 59 - "._show_raw"
Cohesion: 0.50
Nodes (3): Render a raw HTTP message, pretty-printing its body by content-type. Splits…, Split a raw HTTP message into (start_line, headers, body). Tolerant of both…, _split_http_message()

### Community 62 - "FlowRecord"
Cohesion: 0.17
Nodes (5): FlowRecord, A single captured HTTP request/response exchange. Body payloads are represented…, The response content type without parameters (e.g. ``text/html``)., File extension derived from the request path (without the dot). The query…, Cookie names sent/received for this flow, comma-separated. Collects request…

### Community 63 - "app.py"
Cohesion: 0.31
Nodes (7): main(), Application entry point. Creates the Qt application, builds the main window,…, Give Windows an explicit AppUserModelID so the taskbar uses our icon. Without…, _set_windows_app_id(), Enables ``python -m bidoytu``., load_theme(), Return the persisted theme, defaulting to dark.

### Community 64 - "ResultFilterProxy"
Cohesion: 0.25
Nodes (3): QSortFilterProxyModel, Filter results by status, min length, matched-only, and a text needle., ResultFilterProxy

### Community 65 - "Contributing to Bidoytu"
Cohesion: 0.25
Nodes (7): Branches and pull requests, Checks, Contributing to Bidoytu, Design rules, License, Local setup, Security issues

### Community 67 - "logo_path"
Cohesion: 0.39
Nodes (7): asset_path(), _assets_dir(), logo_path(), Path, Locators for bundled resources (icons, images). Resources live under…, Return the absolute path to a bundled asset by file name., Absolute path to the application logo.

### Community 69 - "capture_addon.py"
Cohesion: 0.29
Nodes (6): parse_response_text(), ParsedResponse, Parse raw HTTP response text into a :class:`ParsedResponse`. Tolerant of both…, _PendingFlow, mitmproxy addon: maps flows to FlowRecords and supports interception. Two…, State for a single intercepted (paused) flow.

## Knowledge Gaps
- **39 isolated node(s):** `bidoytu`, `graphify`, `What Bidoytu is`, `Tech stack`, `Git workflow` (+34 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 462 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **15 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `FlowRecord` connect `FlowRecord` to `InterceptView`, `MessageView`, `HistoryView`, `IntruderSession`, `InterceptActivityModel`, `RepeaterTab`, `ProxyEngine`, `CaptureAddon`, `MainWindow`, `FlowRepository`, `engine.py`, `RepeaterSession`, `IntruderTab`, `models.py`, `content_type_from_headers`, `FlowTableModel`, `AsyncHttpSender`, `intruder_session.py`, `BodyStore`, `QMenu`, `smoke_test.py`, `._new_session`, `main_window.py`, `capture_addon.py`?**
  _High betweenness centrality (0.263) - this node is a cross-community bridge._
- **Why does `CollaboratorTab` connect `CollaboratorTab` to `FindBar`, `MessageView`, `main_window.py`, `InteractshClient`, `InteractionFilterProxy`, `MainWindow`, `QHBoxLayout`, `collaborator_tab.py`, `.__init__`, `InteractionsModel`, `Interaction`, `._show_raw`, `AsyncHttpSender`?**
  _High betweenness centrality (0.121) - this node is a cross-community bridge._
- **Why does `IntruderSession` connect `IntruderSession` to `intruder_session.py`, `FindBar`, `ResultFilterProxy`, `theme.py`, `MessageView`, `PayloadSetEditor`, `IntruderResultsModel`, `QHBoxLayout`, `._ensure_payload_sets`, `AttackRunner`, `IntruderTab`, `FlowRecord`, `AsyncHttpSender`?**
  _High betweenness centrality (0.119) - this node is a cross-community bridge._
- **Are the 17 inferred relationships involving `FlowRecord` (e.g. with `test_intercept_view()` and `test_qt_and_proxy_apis()`) actually correct?**
  _`FlowRecord` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `IntruderSession` (e.g. with `AsyncHttpSender` and `PayloadSet`) actually correct?**
  _`IntruderSession` has 15 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `RepeaterSession` (e.g. with `AsyncHttpSender` and `HttpResult`) actually correct?**
  _`RepeaterSession` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `CollaboratorTab` (e.g. with `CollaboratorConfig` and `AsyncHttpSender`) actually correct?**
  _`CollaboratorTab` has 10 INFERRED edges - model-reasoned connections that need verification._
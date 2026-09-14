# Graph Report - Bidoytu  (2026-09-14)

## Corpus Check
- 65 files · ~129,169 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 5 file(s) not represented in the graph (top: (none) 3, .spec 1, .ico 1)

## Summary
- 1251 nodes · 2469 edges · 63 communities (55 shown, 8 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 186 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ee629a92`
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
- HttpResult
- IntruderResultsModel
- ProxyEngine
- CaptureAddon
- MainWindow
- FlowRecord
- FlowLayout
- body_format.py
- PayloadSetEditor
- ProxyTab
- collaborator_tab.py
- RepeaterSession
- _HTMLPretty
- AttackRunner
- InteractionsModel
- AsyncHttpSender
- main_window.py
- FlowTableModel
- smoke_test.py
- _Chip
- FindBar
- iter_jobs
- ._open_or_recover
- BodyStore
- strip_markers
- GroupDialog
- SessionState
- WrappingTabBar
- RepeaterTab
- ca_export_test.py
- .cookies
- intercept_response_live_test.py
- _GroupHeaderChip
- intercept_live_test.py
- InteractionFilterProxy
- _FlowHost
- proxy_live_test.py
- Bidoytu
- config.py
- wrapping_tab_bar.py
- CLAUDE.md
- Building and releasing Bidoytu
- Security Policy
- .__init__
- QMenu
- WorkspaceManager
- Contributing to Bidoytu
- ui/__init__.py
- repeater_session.py
- bidoytu
- ._update_group_send_menu
- AGENTS.md
- CONTRIBUTORS.md

## God Nodes (most connected - your core abstractions)
1. `FlowRecord` - 83 edges
2. `IntruderSession` - 60 edges
3. `RepeaterSession` - 57 edges
4. `MainWindow` - 51 edges
5. `CollaboratorTab` - 50 edges
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

## Communities (63 total, 8 thin omitted)

### Community 0 - "theme.py"
Cohesion: 0.06
Nodes (50): QColor, QPalette, QPixmap, QProxyStyle, QSyntaxHighlighter, QTextCharFormat, _fmt(), HttpHighlighter (+42 more)

### Community 1 - "InterceptView"
Cohesion: 0.07
Nodes (19): InterceptView, QWidget, Size the activity table so URL fills the leftover width, while every column…, Whenever a column is resized, compensate its immediate right neighbor (or left…, Reflow the URL column to absorb the viewport's leftover width. URL is the…, Forward every still-pending flow, then reset the panel. Called when…, A request was paused by the proxy; add it to the table., A response was paused by the proxy; add it to the table. (+11 more)

### Community 2 - "MessageView"
Cohesion: 0.08
Nodes (14): hex_dump(), _LineNumberArea, MessageView, QPlainTextEdit, QRect, QSize, QWidget, Switch how the remembered body is rendered and re-display it. (+6 more)

### Community 3 - "CollaboratorTab"
Cohesion: 0.06
Nodes (18): CollaboratorConfig, Settings for the Collaborator (out-of-band interaction) feature. Attributes:…, CollaboratorTab, Path, QWidget, Slot, Build a titled pane (label + find bar + view), matching Repeater., Best-effort correlate an interaction back to a generated payload. (+10 more)

### Community 4 - "HistoryView"
Cohesion: 0.09
Nodes (13): QStyledItemDelegate, DetailView, QWidget, Two MessageViews (request | response) with a shared soft-wrap toggle., HistoryItemDelegate, Fully self-painted cells: soft row wash + slim accent bar, no style frame., HistoryView, QWidget (+5 more)

### Community 5 - "AppConfig"
Cohesion: 0.10
Nodes (15): AppConfig, _default_data_dir(), Path, Top-level runtime configuration. Attributes: data_dir: Root directory for all…, JSON file holding persisted Repeater sessions across restarts., JSON file holding the last Intruder attack config across restarts., Return a per-user, per-OS data directory for Bidoytu., JSON file holding the Target scope for this workspace. (+7 more)

### Community 6 - "IntruderSession"
Cohesion: 0.08
Nodes (8): IntruderSession, QWidget, Slot, Grow/shrink the payload-set tabs to exactly ``n`` (min 1)., Return a JSON-serializable snapshot of this session., Restore this session from a snapshot produced by :meth:`to_state`., Build a FlowRecord from the template (payload markers removed)., One Intruder attack: template + positions + payload sets + results.

### Community 7 - "InterceptActivityModel"
Cohesion: 0.08
Nodes (14): ActivityRow, InterceptActivityModel, Orientation, QAbstractTableModel, QModelIndex, Log a paused (pending) request. Returns its row index., Log a paused (pending) response. Returns its row index., True if the row is a still-pending request or response. (+6 more)

### Community 8 - "intruder_session.py"
Cohesion: 0.13
Nodes (25): count_jobs(), PayloadSet, Intruder attack model: markers, attack types, and request building. Qt-free so…, Wrap the ``[sel_start, sel_end)`` span of ``text`` in ``§`` markers. Used by…, Best-effort total request count for a configured attack., A generator plus its processing rules (one Intruder payload set)., wrap_selection(), _apply_one() (+17 more)

### Community 9 - "InteractshClient"
Cohesion: 0.10
Nodes (13): Exception, InteractshClient, _cb(), _cb(), InteractshError, Raised for registration / polling / crypto failures., Register with, generate payloads for, and poll an Interactsh server. The client…, Generate a keypair and register against the first working server. ``servers``… (+5 more)

### Community 10 - "HttpResult"
Cohesion: 0.19
Nodes (5): HttpResult, HistoryEntry, Slot, Public entry point for the container to send this tab's request., A request that was sent and (optionally) the response it produced.

### Community 11 - "IntruderResultsModel"
Cohesion: 0.11
Nodes (10): One completed request in the results table., ResultRow, IntruderResultsModel, QAbstractTableModel, QModelIndex, QSortFilterProxyModel, Table model + filter proxy for Intruder attack results.…, Filter results by status, min length, matched-only, and a text needle. (+2 more)

### Community 12 - "ProxyEngine"
Cohesion: 0.07
Nodes (12): QThread, ProxyEngine, Update target scope immediately, including while the proxy runs., Toggle the global 'intercept responses' behavior., Arm a one-shot response intercept for a single flow., Forward a paused request, optionally with edited raw request text., Drop a paused request., Forward a paused response, optionally with edited raw response text. (+4 more)

### Community 13 - "CaptureAddon"
Cohesion: 0.10
Nodes (15): FlowCallback, HTTPFlow, InterceptCallback, CaptureAddon, _PendingFlow, Arm a one-shot response intercept for a single flow (Burp's "Response to this…, Apply a UI decision to a paused request. Runs on the proxy loop., Apply a UI decision to a paused response. Runs on the proxy loop. (+7 more)

### Community 14 - "MainWindow"
Cohesion: 0.07
Nodes (15): QMainWindow, CaCertDialog, Path, QDialog, Dialog for exporting and installing the proxy's CA certificate. To intercept…, Shows CA status, an export button, and install instructions., MainWindow, Slot (+7 more)

### Community 15 - "FlowRecord"
Cohesion: 0.14
Nodes (10): Row, FlowRecord, A single captured HTTP request/response exchange. Body payloads are represented…, The response content type without parameters (e.g. ``text/html``)., File extension derived from the request path (without the dot). The query…, FlowRepository, Insert a new flow and return its assigned primary key., Update an existing flow (matched by ``flow_id``). (+2 more)

### Community 16 - "FlowLayout"
Cohesion: 0.15
Nodes (7): Orientations, QLayout, QLayoutItem, FlowLayout, QRect, QSize, QWidget

### Community 17 - "body_format.py"
Cohesion: 0.13
Nodes (20): content_type_from_headers(), format_body(), _format_c_like(), _format_css(), _format_form(), _format_html(), _format_js(), _format_json() (+12 more)

### Community 18 - "PayloadSetEditor"
Cohesion: 0.15
Nodes (7): QPushButton, PayloadSetEditor, ProcessingRuleDialog, QDialog, QWidget, Edit one payload set: a generator plus a processing-rule pipeline., Configure a single :class:`ProcessingRule`.

### Community 19 - "ProxyTab"
Cohesion: 0.10
Nodes (10): ProxyTab, QWidget, Container widget for everything under the top-level "Proxy" tab., Collapse the Target panel to an arrow, or restore its full width., Use Qt's native arrow icon so the control does not depend on fonts., The Clear History button now lives in the Intercept control row. Exposed here…, Surface a detailed transient message (e.g. "Starting...", errors) on the…, Editable list of host patterns used by the Target scope panel. (+2 more)

### Community 20 - "collaborator_tab.py"
Cohesion: 0.11
Nodes (16): Live test: RepeaterTab.load_from_record + Send performs a real request., Async HTTP sender for Repeater/Intruder. Runs an ``httpx.AsyncClient`` on a…, _encode_xid(), generate_xid(), Interaction, _now_iso(), Interactsh (OAST) client for the Collaborator feature. This is a small, Qt-free…, A single out-of-band interaction reported by the server. (+8 more)

### Community 21 - "RepeaterSession"
Cohesion: 0.17
Nodes (6): QHBoxLayout, QWidget, Install (or clear) the dropdown's group-send options. ``actions`` is a list of…, Record which send mode the split button runs, and show it on the button., One request/response pane with full Repeater controls., RepeaterSession

### Community 22 - "_HTMLPretty"
Cohesion: 0.22
Nodes (4): HTMLParser, _HTMLPretty, Lenient HTML pretty-printer built on the stdlib parser. Emits nicely indented…, Close a preceding sibling with an optional end tag, if applicable.

### Community 23 - "AttackRunner"
Cohesion: 0.14
Nodes (12): Pattern, QObject, AttackJob, One request to send: the substituted text and the payloads used., AttackRunner, _compile(), GrepConfig, Slot (+4 more)

### Community 24 - "InteractionsModel"
Cohesion: 0.16
Nodes (9): InteractionRow, InteractionsModel, protocol_color(), QAbstractTableModel, QModelIndex, Render an ISO timestamp as HH:MM:SS, falling back to the raw string., Return a hex color for an interaction protocol., A received interaction plus the display metadata we derive from it. (+1 more)

### Community 25 - "AsyncHttpSender"
Cohesion: 0.06
Nodes (18): AbstractEventLoop, ResultCallback, AsyncHttpSender, _schedule(), Schedule a request; ``callback`` is invoked on the sender thread. Returns a…, A cancellable handle to an in-flight request. The handle wraps the…, Owns a background event loop running httpx.AsyncClient instances., SendHandle (+10 more)

### Community 26 - "main_window.py"
Cohesion: 0.14
Nodes (11): after_start(), finish(), Reproduce the 'start proxy crashes' path using the real MainWindow. Builds the…, send(), Plain data structures passed between the proxy engine, storage, and UI. These…, Custom QAbstractTableModel backing the traffic history view. We use a hand-…, HTTP history: the traffic table plus a request/response detail view. Emits a…, Table model for the Intercept tab's activity log. Each intercepted request… (+3 more)

### Community 27 - "FlowTableModel"
Cohesion: 0.17
Nodes (6): FlowTableModel, Orientation, QAbstractTableModel, QModelIndex, Replace all rows (e.g. when loading history from the database)., Add a new record, or update an existing one in place. Called from the UI thread…

### Community 28 - "smoke_test.py"
Cohesion: 0.35
Nodes (11): QApplication, main(), Path, Import + wiring smoke test (no live proxy, no visible window). Verifies: - all…, test_body_format(), test_body_store(), test_http_utils(), test_intercept_view() (+3 more)

### Community 29 - "_Chip"
Cohesion: 0.26
Nodes (3): QMouseEvent, _Chip, A single clickable tab chip with an optional close button.

### Community 30 - "FindBar"
Cohesion: 0.19
Nodes (8): FindFlags, QKeyEvent, FindBar, QPlainTextEdit, QWidget, A small find bar that searches within a QPlainTextEdit. Reusable over any…, Incremental find controls bound to a target text edit., Reveal the bar, seed it with any selected text, and focus input.

### Community 31 - "iter_jobs"
Cohesion: 0.21
Nodes (9): find_markers(), iter_jobs(), Marker, Insert ``values`` into ``clean_text`` at each marker (right-to-left). Working…, Yield an :class:`AttackJob` per request for the configured attack.…, A payload position: the span between a pair of ``§`` markers. ``start``/``end``…, Split a ``§``-marked template into (clean_text, markers). Markers come in…, _splice() (+1 more)

### Community 32 - "._open_or_recover"
Cohesion: 0.29
Nodes (4): Connection, Path, Move the corrupt database and SQLite sidecars to a safe backup., Open and validate the database, recovering from SQLite corruption. A damaged…

### Community 33 - "BodyStore"
Cohesion: 0.15
Nodes (8): BodyStore, Path, On-disk store for large request/response bodies. Rather than storing large…, Content-addressed file store for body payloads. Files are sharded into…, Write ``data`` to the store and return its relative path. Identical content…, Read body content previously returned by :meth:`store`., Storage layer: SQLite persistence + on-disk body store., SQLite persistence for captured flows. Uses the stdlib ``sqlite3`` module…

### Community 34 - "strip_markers"
Cohesion: 0.33
Nodes (3): Return the template with all ``§`` markers removed (defaults kept)., strip_markers(), Wrap each ``name=value`` value (query + body) in markers.

### Community 35 - "GroupDialog"
Cohesion: 0.22
Nodes (4): GroupDialog, QDialog, Dialog for adding Repeater request tabs to a named, colored group. Presents a…, Collect a group name, member tabs, and a color.

### Community 36 - "SessionState"
Cohesion: 0.18
Nodes (7): Serializable snapshot of a session (for persistence)., SessionState, Group, Path, A named, colored, collapsible collection of member sessions., Write all open sessions and their groups to ``path`` as JSON., Recreate sessions and groups saved by :meth:`save_sessions`.

### Community 37 - "WrappingTabBar"
Cohesion: 0.26
Nodes (5): QScrollArea, QSize, Group-aware, wrapping tab bar composed of chip widgets., Rebuild the whole bar from the container's model. Args: order: list of keys…, WrappingTabBar

### Community 38 - "RepeaterTab"
Cohesion: 0.17
Nodes (7): QWidget, Clone a session's request into a new tab, named ``base (n)``., Return ``base (n)`` with the smallest unused positive integer n., Delete a group along with all request tabs it contains., Close every request tab and remove all groups., Holds multiple :class:`RepeaterSession` instances with a wrapping bar., RepeaterTab

### Community 39 - "ca_export_test.py"
Cohesion: 0.67
Nodes (3): finish(), poll_for_ca(), Verify the CA is generated in Bidoytu's confdir and can be exported. Starts the…

### Community 42 - "intercept_response_live_test.py"
Cohesion: 0.31
Nodes (7): check_done(), do_forward(), finish(), on_intercepted(), on_started(), Live: intercept a request via the real MainWindow, forward it, and confirm the…, send()

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

### Community 51 - "config.py"
Cohesion: 0.13
Nodes (13): on_started(), Verify the capture addon stores DECODED bodies (gzip is undone). Routes a…, Verify starting the proxy on an occupied port produces a clean error signal…, host_matches_scope(), matches(), _normalise_scope_entry(), ProxyConfig, Application configuration and filesystem paths. Everything the app writes… (+5 more)

### Community 52 - "wrapping_tab_bar.py"
Cohesion: 0.29
Nodes (4): A wrapping flow layout: children flow left-to-right and wrap to new rows. This…, Return the named color tokens for ``mode`` (falls back to dark)., tokens(), A wrapping, group-aware tab bar built from individual chip widgets. Unlike…

### Community 53 - "CLAUDE.md"
Cohesion: 0.20
Nodes (8): Architecture and layering (respect this), Conventions, Git workflow, Gotchas learned the hard way, Tech stack, Verifying changes (always do this), What Bidoytu is, Where things live

### Community 55 - "Building and releasing Bidoytu"
Cohesion: 0.20
Nodes (9): Build (Windows or Linux), Building and releasing Bidoytu, Cutting version 1.0.0, How releases work (CI/CD), Local builds (optional), Notes, Nuitka (alternative compiler), Prerequisites (+1 more)

### Community 58 - "Security Policy"
Cohesion: 0.22
Nodes (8): Handling the CA certificate, Reporting a vulnerability, Responsible and lawful use, Safe defaults and data handling, Scope, Security Policy, Supported versions, What to expect

### Community 60 - "QMenu"
Cohesion: 0.29
Nodes (3): QMenu, Ask the provider for a payload and insert it at the cursor., Build a FlowRecord from the current (edited) request text.

### Community 63 - "WorkspaceManager"
Cohesion: 0.07
Nodes (32): main(), Application entry point. Creates the Qt application, builds the main window,…, Give Windows an explicit AppUserModelID so the taskbar uses our icon. Without…, _set_windows_app_id(), Bidoytu - an intercepting HTTP proxy tool. Base architecture: - Proxy/MITM…, Enables ``python -m bidoytu``., asset_path(), _assets_dir() (+24 more)

### Community 65 - "Contributing to Bidoytu"
Cohesion: 0.25
Nodes (7): Branches and pull requests, Checks, Contributing to Bidoytu, Design rules, License, Local setup, Security issues

### Community 67 - "repeater_session.py"
Cohesion: 0.10
Nodes (21): absolute_url(), build_request_text(), build_response_text(), ensure_host_header(), _headers_have(), host_from_headers_or_url(), parse_request_text(), parse_response_text() (+13 more)

## Knowledge Gaps
- **39 isolated node(s):** `bidoytu`, `graphify`, `What Bidoytu is`, `Tech stack`, `Git workflow` (+34 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 494 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `FlowRecord` connect `FlowRecord` to `InterceptView`, `HistoryView`, `IntruderSession`, `InterceptActivityModel`, `intruder_session.py`, `ProxyEngine`, `CaptureAddon`, `MainWindow`, `body_format.py`, `collaborator_tab.py`, `RepeaterSession`, `AsyncHttpSender`, `main_window.py`, `FlowTableModel`, `smoke_test.py`, `BodyStore`, `RepeaterTab`, `.cookies`, `config.py`, `.__init__`, `QMenu`, `repeater_session.py`?**
  _High betweenness centrality (0.209) - this node is a cross-community bridge._
- **Why does `IntruderSession` connect `IntruderSession` to `theme.py`, `strip_markers`, `repeater_session.py`, `MessageView`, `intruder_session.py`, `IntruderResultsModel`, `FlowRecord`, `PayloadSetEditor`, `AttackRunner`, `AsyncHttpSender`, `main_window.py`, `FindBar`, `iter_jobs`?**
  _High betweenness centrality (0.111) - this node is a cross-community bridge._
- **Why does `MainWindow` connect `MainWindow` to `BodyStore`, `MessageView`, `CollaboratorTab`, `AppConfig`, `RepeaterTab`, `InteractshClient`, `ProxyEngine`, `FlowRecord`, `ProxyTab`, `AsyncHttpSender`, `main_window.py`, `FlowTableModel`, `smoke_test.py`, `WorkspaceManager`?**
  _High betweenness centrality (0.099) - this node is a cross-community bridge._
- **Are the 17 inferred relationships involving `FlowRecord` (e.g. with `test_intercept_view()` and `test_qt_and_proxy_apis()`) actually correct?**
  _`FlowRecord` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `IntruderSession` (e.g. with `AsyncHttpSender` and `PayloadSet`) actually correct?**
  _`IntruderSession` has 15 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `RepeaterSession` (e.g. with `AsyncHttpSender` and `HttpResult`) actually correct?**
  _`RepeaterSession` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 17 inferred relationships involving `MainWindow` (e.g. with `test_qt_and_proxy_apis()` and `AppConfig`) actually correct?**
  _`MainWindow` has 17 INFERRED edges - model-reasoned connections that need verification._
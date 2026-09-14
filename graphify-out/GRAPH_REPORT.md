# Graph Report - Bidoytu  (2026-09-15)

## Corpus Check
- 65 files · ~129,293 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 5 file(s) not represented in the graph (top: (none) 3, .spec 1, .ico 1)

## Summary
- 1257 nodes · 2379 edges · 73 communities (62 shown, 11 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 174 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `9a1764e5`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- GroupDialog
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
- FlowLayout
- _build_qss
- PayloadSetEditor
- QHBoxLayout
- collaborator_tab.py
- parse_request_text
- repeater_session.py
- AttackRunner
- InteractionsModel
- IntruderTab
- models.py
- FlowTableModel
- smoke_test.py
- _Chip
- main_window.py
- AsyncHttpSender
- ._open_or_recover
- Interaction
- theme.py
- FindBar
- ._start_attack
- WrappingTabBar
- RepeaterTab
- start_proxy_repro.py
- .cookies
- ._new_session
- intercept_response_live_test.py
- _GroupHeaderChip
- history_delegate.py
- intercept_live_test.py
- InteractionFilterProxy
- _FlowHost
- proxy_live_test.py
- app.py
- Bidoytu
- config.py
- current_mode
- CLAUDE.md
- QMenu
- Building and releasing Bidoytu
- strip_markers
- ._show_raw
- Security Policy
- wrap_selection
- _NoFocusRectStyle
- ca_export_test.py
- ._duplicate_session
- WorkspaceManager
- bidoytu/__init__.py
- Contributing to Bidoytu
- ui/__init__.py
- detail_view.py
- bidoytu
- ._update_group_send_menu
- Path
- AGENTS.md
- CONTRIBUTORS.md

## God Nodes (most connected - your core abstractions)
1. `FlowRecord` - 61 edges
2. `IntruderSession` - 60 edges
3. `RepeaterSession` - 57 edges
4. `CollaboratorTab` - 48 edges
5. `MessageView` - 41 edges
6. `InterceptView` - 38 edges
7. `RepeaterTab` - 37 edges
8. `MainWindow` - 34 edges
9. `AsyncHttpSender` - 32 edges
10. `InterceptActivityModel` - 27 edges

## Surprising Connections (you probably didn't know these)
- `test_intercept_view()` --uses--> `InterceptView`  [INFERRED]
  scripts/smoke_test.py → src/bidoytu/ui/intercept_view.py
- `test_qt_and_proxy_apis()` --uses--> `MainWindow`  [INFERRED]
  scripts/smoke_test.py → src/bidoytu/ui/main_window.py
- `test_intercept_view()` --uses--> `FlowRecord`  [INFERRED]
  scripts/smoke_test.py → src/bidoytu/storage/models.py
- `test_qt_and_proxy_apis()` --uses--> `FlowRecord`  [INFERRED]
  scripts/smoke_test.py → src/bidoytu/storage/models.py
- `test_storage_roundtrip()` --uses--> `FlowRecord`  [INFERRED]
  scripts/smoke_test.py → src/bidoytu/storage/models.py

## Import Cycles
- None detected.

## Communities (73 total, 11 thin omitted)

### Community 0 - "GroupDialog"
Cohesion: 0.09
Nodes (17): QColor, QSyntaxHighlighter, QTextCharFormat, GroupDialog, QDialog, Dialog for adding Repeater request tabs to a named, colored group. Presents a…, Collect a group name, member tabs, and a color., _fmt() (+9 more)

### Community 1 - "InterceptView"
Cohesion: 0.07
Nodes (23): build_response_text(), Assemble a raw HTTP response string from parts., InterceptView, FlowRecord, QWidget, Size the activity table so URL fills the leftover width, while every column…, Whenever a column is resized, compensate its immediate right neighbor (or left…, Reflow the URL column to absorb the viewport's leftover width. URL is the… (+15 more)

### Community 2 - "MessageView"
Cohesion: 0.06
Nodes (17): DetailView, QWidget, Two MessageViews (request | response) with a shared soft-wrap toggle., hex_dump(), _LineNumberArea, MessageView, QPlainTextEdit, QRect (+9 more)

### Community 3 - "CollaboratorTab"
Cohesion: 0.09
Nodes (9): CollaboratorTab, Path, QWidget, Build a titled pane (label + find bar + view), matching Repeater., Attach a note (e.g. the target tab) to the most recent payload., Generate a payload, tag it with ``note``, and return the hostname. Used by…, Persist the session, generated payloads, and interactions to JSON., Register with an Interactsh server, hand out payloads, show callbacks. (+1 more)

### Community 4 - "HistoryView"
Cohesion: 0.10
Nodes (12): FlowTableModel, HistoryView, FlowRecord, QWidget, Slot, HTTP history: the traffic table plus a request/response detail view. Emits a…, Whenever a column is resized, compensate its immediate right neighbor (or left…, Reflow the Path column to absorb the viewport's leftover width. Path is the… (+4 more)

### Community 5 - "AppConfig"
Cohesion: 0.10
Nodes (15): AppConfig, _default_data_dir(), Path, Top-level runtime configuration. Attributes: data_dir: Root directory for all…, JSON file holding persisted Repeater sessions across restarts., JSON file holding the last Intruder attack config across restarts., Return a per-user, per-OS data directory for Bidoytu., JSON file holding the Target scope for this workspace. (+7 more)

### Community 6 - "IntruderSession"
Cohesion: 0.09
Nodes (7): IntruderSession, Slot, Grow/shrink the payload-set tabs to exactly ``n`` (min 1)., Return a JSON-serializable snapshot of this session., Restore this session from a snapshot produced by :meth:`to_state`., Build a FlowRecord from the template (payload markers removed)., One Intruder attack: template + positions + payload sets + results.

### Community 7 - "InterceptActivityModel"
Cohesion: 0.08
Nodes (14): ActivityRow, InterceptActivityModel, Orientation, QAbstractTableModel, QModelIndex, Log a paused (pending) request. Returns its row index., Log a paused (pending) response. Returns its row index., True if the row is a still-pending request or response. (+6 more)

### Community 8 - "intruder_session.py"
Cohesion: 0.12
Nodes (29): count_jobs(), iter_jobs(), Marker, PayloadSet, Intruder attack model: markers, attack types, and request building. Qt-free so…, Insert ``values`` into ``clean_text`` at each marker (right-to-left). Working…, Best-effort total request count for a configured attack., Yield an :class:`AttackJob` per request for the configured attack.… (+21 more)

### Community 9 - "InteractshClient"
Cohesion: 0.10
Nodes (13): Exception, InteractshClient, _cb(), _cb(), InteractshError, Raised for registration / polling / crypto failures., Register with, generate payloads for, and poll an Interactsh server. The client…, Generate a keypair and register against the first working server. ``servers``… (+5 more)

### Community 10 - "RepeaterSession"
Cohesion: 0.14
Nodes (5): QWidget, Install (or clear) the dropdown's group-send options. ``actions`` is a list of…, Record which send mode the split button runs, and show it on the button., One request/response pane with full Repeater controls., RepeaterSession

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
Nodes (16): AppConfig, QMainWindow, BodyStore, Path, Content-addressed file store for body payloads. Files are sharded into…, Write ``data`` to the store and return its relative path. Identical content…, Read body content previously returned by :meth:`store`., MainWindow (+8 more)

### Community 15 - "FlowRecord"
Cohesion: 0.14
Nodes (10): Row, FlowRecord, A single captured HTTP request/response exchange. Body payloads are represented…, The response content type without parameters (e.g. ``text/html``)., File extension derived from the request path (without the dot). The query…, FlowRepository, Insert a new flow and return its assigned primary key., Update an existing flow (matched by ``flow_id``). (+2 more)

### Community 16 - "FlowLayout"
Cohesion: 0.15
Nodes (7): Orientations, QLayout, QLayoutItem, FlowLayout, QRect, QSize, QWidget

### Community 17 - "_build_qss"
Cohesion: 0.16
Nodes (17): QPixmap, _blank_pixmap(), _build_qss(), _check_icon(), _chevron_down_icon(), _chevron_icon(), _chevron_up_icon(), _close_icon() (+9 more)

### Community 18 - "PayloadSetEditor"
Cohesion: 0.15
Nodes (6): PayloadSetEditor, ProcessingRuleDialog, QDialog, QWidget, Edit one payload set: a generator plus a processing-rule pipeline., Configure a single :class:`ProcessingRule`.

### Community 19 - "QHBoxLayout"
Cohesion: 0.07
Nodes (19): QHBoxLayout, QPushButton, CaCertDialog, Path, QDialog, Dialog for exporting and installing the proxy's CA certificate. To intercept…, Shows CA status, an export button, and install instructions., QPlainTextEdit (+11 more)

### Community 20 - "collaborator_tab.py"
Cohesion: 0.17
Nodes (12): Async HTTP sender for Repeater/Intruder. Runs an ``httpx.AsyncClient`` on a…, _encode_xid(), generate_xid(), Interactsh (OAST) client for the Collaborator feature. This is a small, Qt-free…, Everything needed to resume / persist a registered session., Return a 20-char XID string. XID layout: 4-byte time, 3-byte machine id, 2-byte…, Encode 12 raw bytes into the 20-char XID base32 representation., SessionInfo (+4 more)

### Community 21 - "parse_request_text"
Cohesion: 0.15
Nodes (14): absolute_url(), build_request_text(), host_from_headers_or_url(), parse_request_text(), parse_response_text(), ParsedRequest, ParsedResponse, Helpers for converting between raw HTTP text and structured parts. Used by… (+6 more)

### Community 22 - "repeater_session.py"
Cohesion: 0.05
Nodes (33): AbstractEventLoop, HTMLParser, HttpResult, A cancellable handle to an in-flight request. The handle wraps the…, SendHandle, content_type_from_headers(), format_body(), _format_c_like() (+25 more)

### Community 23 - "AttackRunner"
Cohesion: 0.20
Nodes (7): QObject, AttackJob, One request to send: the substituted text and the payloads used., AttackRunner, Slot, Launch requests until we hit the concurrency cap or run out., Runs one attack, emitting a :class:`ResultRow` per completed request.

### Community 24 - "InteractionsModel"
Cohesion: 0.15
Nodes (9): InteractionRow, InteractionsModel, protocol_color(), QAbstractTableModel, QModelIndex, Render an ISO timestamp as HH:MM:SS, falling back to the raw string., Return a hex color for an interaction protocol., A received interaction plus the display metadata we derive from it. (+1 more)

### Community 25 - "IntruderTab"
Cohesion: 0.15
Nodes (8): IntruderTab, Path, QWidget, Close every Intruder tab., Open a new session tab populated from a captured flow., Write every open session to ``path`` as JSON (list of snapshots)., Recreate the sessions saved by :meth:`save_state`. Accepts both the multi-…, Holds multiple :class:`IntruderSession` instances in a tab strip.

### Community 26 - "models.py"
Cohesion: 0.17
Nodes (6): Live test: RepeaterTab.load_from_record + Send performs a real request., Plain data structures passed between the proxy engine, storage, and UI. These…, Custom QAbstractTableModel backing the traffic history view. We use a hand-…, Table model for the Intercept tab's activity log. Each intercepted request…, Intruder tab: a container of independent attack sessions. Each "Send to…, Repeater tab: a container of independent request/response sessions. Each "Send…

### Community 27 - "FlowTableModel"
Cohesion: 0.17
Nodes (6): FlowTableModel, Orientation, QAbstractTableModel, QModelIndex, Replace all rows (e.g. when loading history from the database)., Add a new record, or update an existing one in place. Called from the UI thread…

### Community 28 - "smoke_test.py"
Cohesion: 0.20
Nodes (14): QApplication, main(), Path, Import + wiring smoke test (no live proxy, no visible window). Verifies: - all…, test_body_format(), test_body_store(), test_http_utils(), test_intercept_view() (+6 more)

### Community 29 - "_Chip"
Cohesion: 0.26
Nodes (3): QMouseEvent, _Chip, A single clickable tab chip with an optional close button.

### Community 30 - "main_window.py"
Cohesion: 0.24
Nodes (10): Path, asset_path(), _assets_dir(), logo_path(), Locators for bundled resources (icons, images). Resources live under…, Return the absolute path to a bundled asset by file name., Absolute path to the application logo., Main application window. Top-level layout is a QTabWidget with four tabs: -… (+2 more)

### Community 31 - "AsyncHttpSender"
Cohesion: 0.15
Nodes (6): ResultCallback, AsyncHttpSender, _schedule(), Schedule a request; ``callback`` is invoked on the sender thread. Returns a…, Owns a background event loop running httpx.AsyncClient instances., Networking helpers (async HTTP client for Repeater/Intruder).

### Community 32 - "._open_or_recover"
Cohesion: 0.29
Nodes (4): Connection, Path, Move the corrupt database and SQLite sidecars to a safe backup., Open and validate the database, recovering from SQLite corruption. A damaged…

### Community 33 - "Interaction"
Cohesion: 0.18
Nodes (5): Interaction, _now_iso(), A single out-of-band interaction reported by the server., Best-effort correlate an interaction back to a generated payload., Restore a session saved by :meth:`save_state` and re-register it.

### Community 34 - "theme.py"
Cohesion: 0.27
Nodes (10): QPalette, apply_theme(), _blend(), _dark_palette(), _light_palette(), _palette_from_tokens(), _qss_for(), Application theming: light and dark modes. Provides two things: -… (+2 more)

### Community 35 - "FindBar"
Cohesion: 0.24
Nodes (6): FindFlags, QKeyEvent, FindBar, QWidget, Incremental find controls bound to a target text edit., Reveal the bar, seed it with any selected text, and focus input.

### Community 36 - "._start_attack"
Cohesion: 0.24
Nodes (7): Pattern, find_markers(), Split a ``§``-marked template into (clean_text, markers). Markers come in…, _compile(), GrepConfig, How to derive match/extract columns from each response., Pitchfork/cluster bomb use one set per position; others use one.

### Community 37 - "WrappingTabBar"
Cohesion: 0.26
Nodes (5): QScrollArea, QSize, Group-aware, wrapping tab bar composed of chip widgets., Rebuild the whole bar from the container's model. Args: order: list of keys…, WrappingTabBar

### Community 38 - "RepeaterTab"
Cohesion: 0.18
Nodes (7): Group, QWidget, Delete a group along with all request tabs it contains., Close every request tab and remove all groups., A named, colored, collapsible collection of member sessions., Holds multiple :class:`RepeaterSession` instances with a wrapping bar., RepeaterTab

### Community 39 - "start_proxy_repro.py"
Cohesion: 0.47
Nodes (4): after_start(), finish(), Reproduce the 'start proxy crashes' path using the real MainWindow. Builds the…, send()

### Community 41 - "._new_session"
Cohesion: 0.17
Nodes (6): Serializable snapshot of a session (for persistence)., SessionState, Path, Open a new session tab populated from a captured flow., Write all open sessions and their groups to ``path`` as JSON., Recreate sessions and groups saved by :meth:`save_sessions`.

### Community 42 - "intercept_response_live_test.py"
Cohesion: 0.31
Nodes (7): check_done(), do_forward(), finish(), on_intercepted(), on_started(), Live: intercept a request via the real MainWindow, forward it, and confirm the…, send()

### Community 44 - "history_delegate.py"
Cohesion: 0.27
Nodes (8): QStyledItemDelegate, HistoryItemDelegate, Item delegate for the HTTP history table. This delegate paints every cell…, A soft, muted tint of the accent used to fill the selected row. Uses the shared…, Fully self-painted cells: soft row wash + slim accent bar, no style frame., _selection_fill(), highlight_bg(), selection_color()

### Community 45 - "intercept_live_test.py"
Cohesion: 0.36
Nodes (6): finish(), on_captured(), on_intercepted(), on_started(), Live test: interception pauses a request, and forward/drop resolve it.…, send()

### Community 46 - "InteractionFilterProxy"
Cohesion: 0.24
Nodes (5): CollaboratorConfig, Settings for the Collaborator (out-of-band interaction) feature. Attributes:…, InteractionFilterProxy, QSortFilterProxyModel, Filter interactions by protocol and a free-text needle.

### Community 47 - "_FlowHost"
Cohesion: 0.38
Nodes (4): QResizeEvent, _FlowHost, QWidget, Host widget whose height tracks its FlowLayout's height-for-width. A…

### Community 48 - "proxy_live_test.py"
Cohesion: 0.33
Nodes (3): on_started(), Live end-to-end test: start the ProxyEngine thread and route a real request…, send_request()

### Community 49 - "app.py"
Cohesion: 0.31
Nodes (7): main(), Application entry point. Creates the Qt application, builds the main window,…, Give Windows an explicit AppUserModelID so the taskbar uses our icon. Without…, _set_windows_app_id(), Enables ``python -m bidoytu``., load_theme(), Return the persisted theme, defaulting to dark.

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

### Community 54 - "QMenu"
Cohesion: 0.29
Nodes (3): QMenu, Ask the provider for a payload and insert it at the cursor., Build a FlowRecord from the current (edited) request text.

### Community 55 - "Building and releasing Bidoytu"
Cohesion: 0.20
Nodes (9): Build (Windows or Linux), Building and releasing Bidoytu, Cutting version 1.0.0, How releases work (CI/CD), Local builds (optional), Notes, Nuitka (alternative compiler), Prerequisites (+1 more)

### Community 56 - "strip_markers"
Cohesion: 0.33
Nodes (3): Return the template with all ``§`` markers removed (defaults kept)., strip_markers(), Wrap each ``name=value`` value (query + body) in markers.

### Community 57 - "._show_raw"
Cohesion: 0.29
Nodes (4): Slot, Render a raw HTTP message, pretty-printing its body by content-type. Splits…, Split a raw HTTP message into (start_line, headers, body). Tolerant of both…, _split_http_message()

### Community 58 - "Security Policy"
Cohesion: 0.22
Nodes (8): Handling the CA certificate, Reporting a vulnerability, Responsible and lawful use, Safe defaults and data handling, Scope, Security Policy, Supported versions, What to expect

### Community 60 - "_NoFocusRectStyle"
Cohesion: 0.60
Nodes (3): QProxyStyle, _NoFocusRectStyle, Application style that suppresses the item-view focus rectangle globally. The…

### Community 61 - "ca_export_test.py"
Cohesion: 0.67
Nodes (3): finish(), poll_for_ca(), Verify the CA is generated in Bidoytu's confdir and can be exported. Starts the…

### Community 63 - "WorkspaceManager"
Cohesion: 0.10
Nodes (17): QDialog, Startup picker for local Bidoytu workspaces., Choose, create, import, or export local workspaces before app startup., WorkspaceDialog, _now(), Path, Local, Burp-style workspace management. Each workspace owns its SQLite history,…, Remove every deletable workspace while keeping the legacy recovery one. (+9 more)

### Community 65 - "Contributing to Bidoytu"
Cohesion: 0.25
Nodes (7): Branches and pull requests, Checks, Contributing to Bidoytu, Design rules, License, Local setup, Security issues

### Community 67 - "detail_view.py"
Cohesion: 0.29
Nodes (5): ensure_host_header(), _headers_have(), Return True if the raw header block already contains ``name`` (case-…, Return the header block with a ``Host`` header guaranteed to be present. If…, Reusable side-by-side request/response viewer. Used by the Proxy history, the…

## Knowledge Gaps
- **39 isolated node(s):** `How releases work (CI/CD)`, `Cutting version 1.0.0`, `Prerequisites`, `Build (Windows or Linux)`, `Why the build is ~160 MB and not ~740 MB` (+34 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 499 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `FlowRecord` connect `FlowRecord` to `MessageView`, `IntruderSession`, `InterceptActivityModel`, `intruder_session.py`, `RepeaterSession`, `ProxyEngine`, `CaptureAddon`, `repeater_session.py`, `IntruderTab`, `models.py`, `FlowTableModel`, `smoke_test.py`, `AsyncHttpSender`, `RepeaterTab`, `.cookies`, `._new_session`, `config.py`, `QMenu`, `detail_view.py`?**
  _High betweenness centrality (0.192) - this node is a cross-community bridge._
- **Why does `CollaboratorTab` connect `CollaboratorTab` to `Interaction`, `MessageView`, `FindBar`, `InteractshClient`, `InteractionFilterProxy`, `MainWindow`, `QHBoxLayout`, `collaborator_tab.py`, `InteractionsModel`, `._show_raw`, `AsyncHttpSender`?**
  _High betweenness centrality (0.124) - this node is a cross-community bridge._
- **Why does `MessageView` connect `MessageView` to `GroupDialog`, `InterceptView`, `detail_view.py`, `CollaboratorTab`, `IntruderSession`, `intruder_session.py`, `RepeaterSession`, `QHBoxLayout`, `collaborator_tab.py`, `repeater_session.py`, `._show_raw`?**
  _High betweenness centrality (0.119) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `FlowRecord` (e.g. with `test_intercept_view()` and `test_qt_and_proxy_apis()`) actually correct?**
  _`FlowRecord` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `IntruderSession` (e.g. with `AsyncHttpSender` and `PayloadSet`) actually correct?**
  _`IntruderSession` has 15 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `RepeaterSession` (e.g. with `AsyncHttpSender` and `HttpResult`) actually correct?**
  _`RepeaterSession` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `CollaboratorTab` (e.g. with `CollaboratorConfig` and `AsyncHttpSender`) actually correct?**
  _`CollaboratorTab` has 10 INFERRED edges - model-reasoned connections that need verification._
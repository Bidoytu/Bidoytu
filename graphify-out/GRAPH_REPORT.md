# Graph Report - Bidoytu  (2026-09-14)

## Corpus Check
- 65 files · ~129,169 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 5 file(s) not represented in the graph (top: (none) 3, .spec 1, .ico 1)

## Summary
- 1259 nodes · 2396 edges · 73 communities (61 shown, 12 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 173 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `c36c9035`
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
- FlowLayout
- body_format.py
- HttpHighlighter
- ProxyTab
- collaborator_tab.py
- parse_request_text
- _HTMLPretty
- AttackRunner
- InteractionsModel
- IntruderTab
- repeater_session.py
- ._select_next_pending
- app.py
- _Chip
- QColor
- AsyncHttpSender
- ._open_or_recover
- .restore_state
- CaCertDialog
- GroupDialog
- repeater_tab.py
- WrappingTabBar
- RepeaterTab
- main_window.py
- .cookies
- async_sender.py
- intercept_response_live_test.py
- _GroupHeaderChip
- ._forward_pending_and_clear
- intercept_live_test.py
- InteractionFilterProxy
- _FlowHost
- proxy_live_test.py
- SendHandle
- Bidoytu
- config.py
- current_mode
- CLAUDE.md
- logo_path
- Building and releasing Bidoytu
- .__init__
- _NoFocusRectStyle
- Security Policy
- ._fit_url_column
- QMenu
- .__init__
- .__init__
- WorkspaceManager
- Slot
- Contributing to Bidoytu
- ui/__init__.py
- http_utils.py
- bidoytu
- ._update_group_send_menu
- QWidget
- AGENTS.md
- CONTRIBUTORS.md

## God Nodes (most connected - your core abstractions)
1. `FlowRecord` - 61 edges
2. `IntruderSession` - 60 edges
3. `RepeaterSession` - 57 edges
4. `CollaboratorTab` - 48 edges
5. `MessageView` - 43 edges
6. `InterceptView` - 39 edges
7. `MainWindow` - 38 edges
8. `RepeaterTab` - 37 edges
9. `AsyncHttpSender` - 32 edges
10. `InterceptActivityModel` - 29 edges

## Surprising Connections (you probably didn't know these)
- `test_storage_roundtrip()` --calls--> `FlowRepository`  [INFERRED]
  scripts/smoke_test.py → src/bidoytu/storage/repository.py
- `test_body_format()` --calls--> `content_type_from_headers()`  [INFERRED]
  scripts/smoke_test.py → src/bidoytu/ui/body_format.py
- `test_body_format()` --calls--> `format_body()`  [INFERRED]
  scripts/smoke_test.py → src/bidoytu/ui/body_format.py
- `test_http_utils()` --calls--> `host_from_headers_or_url()`  [INFERRED]
  scripts/smoke_test.py → src/bidoytu/http_utils.py
- `test_http_utils()` --calls--> `parse_request_text()`  [INFERRED]
  scripts/smoke_test.py → src/bidoytu/http_utils.py

## Import Cycles
- None detected.

## Communities (73 total, 12 thin omitted)

### Community 0 - "theme.py"
Cohesion: 0.17
Nodes (19): QPixmap, _blank_pixmap(), _build_qss(), _check_icon(), _chevron_down_icon(), _chevron_icon(), _chevron_up_icon(), _close_icon() (+11 more)

### Community 1 - "InterceptView"
Cohesion: 0.14
Nodes (8): InterceptView, QWidget, Size the activity table so URL fills the leftover width, while every column…, Whenever a column is resized, compensate its immediate right neighbor (or left…, UI for reviewing and resolving intercepted requests + their responses., A response arrived. If we forwarded this flow from the intercept panel, show…, Arm a one-shot response intercept for the current paused request, then forward…, Build a FlowRecord from the (possibly edited) request in the editor. Uses the…

### Community 2 - "MessageView"
Cohesion: 0.06
Nodes (17): DetailView, QWidget, Two MessageViews (request | response) with a shared soft-wrap toggle., hex_dump(), _LineNumberArea, MessageView, QPlainTextEdit, QRect (+9 more)

### Community 3 - "CollaboratorTab"
Cohesion: 0.09
Nodes (10): CollaboratorTab, QWidget, Slot, Build a titled pane (label + find bar + view), matching Repeater., Best-effort correlate an interaction back to a generated payload., Render a raw HTTP message, pretty-printing its body by content-type. Splits…, Attach a note (e.g. the target tab) to the most recent payload., Generate a payload, tag it with ``note``, and return the hostname. Used by… (+2 more)

### Community 4 - "HistoryView"
Cohesion: 0.08
Nodes (16): QStyledItemDelegate, FlowTableModel, Orientation, QAbstractTableModel, QModelIndex, Replace all rows (e.g. when loading history from the database)., Add a new record, or update an existing one in place. Called from the UI thread…, HistoryItemDelegate (+8 more)

### Community 5 - "AppConfig"
Cohesion: 0.06
Nodes (31): main(), Path, Import + wiring smoke test (no live proxy, no visible window). Verifies: - all…, test_body_format(), test_body_store(), test_http_utils(), test_intercept_view(), test_qt_and_proxy_apis() (+23 more)

### Community 6 - "IntruderSession"
Cohesion: 0.05
Nodes (21): FindFlags, QHBoxLayout, QKeyEvent, QPushButton, Return the template with all ``§`` markers removed (defaults kept)., strip_markers(), FindBar, QPlainTextEdit (+13 more)

### Community 7 - "InterceptActivityModel"
Cohesion: 0.08
Nodes (14): ActivityRow, InterceptActivityModel, Orientation, QAbstractTableModel, QModelIndex, Log a paused (pending) request. Returns its row index., Log a paused (pending) response. Returns its row index., True if the row is a still-pending request or response. (+6 more)

### Community 8 - "intruder_session.py"
Cohesion: 0.06
Nodes (40): count_jobs(), find_markers(), iter_jobs(), Marker, PayloadSet, Intruder attack model: markers, attack types, and request building. Qt-free so…, Wrap the ``[sel_start, sel_end)`` span of ``text`` in ``§`` markers. Used by…, Insert ``values`` into ``clean_text`` at each marker (right-to-left). Working… (+32 more)

### Community 9 - "InteractshClient"
Cohesion: 0.10
Nodes (13): Exception, InteractshClient, _cb(), _cb(), InteractshError, Raised for registration / polling / crypto failures., Register with, generate payloads for, and poll an Interactsh server. The client…, Generate a keypair and register against the first working server. ``servers``… (+5 more)

### Community 10 - "RepeaterSession"
Cohesion: 0.14
Nodes (6): HistoryEntry, Slot, Public entry point for the container to send this tab's request., A request that was sent and (optionally) the response it produced., One request/response pane with full Repeater controls., RepeaterSession

### Community 11 - "IntruderResultsModel"
Cohesion: 0.11
Nodes (10): One completed request in the results table., ResultRow, IntruderResultsModel, QAbstractTableModel, QModelIndex, QSortFilterProxyModel, Table model + filter proxy for Intruder attack results.…, Filter results by status, min length, matched-only, and a text needle. (+2 more)

### Community 12 - "ProxyEngine"
Cohesion: 0.08
Nodes (12): QThread, ProxyEngine, FlowRecord, Update target scope immediately, including while the proxy runs., Toggle the global 'intercept responses' behavior., Arm a one-shot response intercept for a single flow., Forward a paused request, optionally with edited raw request text., Drop a paused request. (+4 more)

### Community 13 - "CaptureAddon"
Cohesion: 0.12
Nodes (14): HTTPFlow, CaptureAddon, _PendingFlow, FlowRecord, Arm a one-shot response intercept for a single flow (Burp's "Response to this…, Apply a UI decision to a paused request. Runs on the proxy loop., Apply a UI decision to a paused response. Runs on the proxy loop., Rewrite a flow's request from edited raw text before forwarding. (+6 more)

### Community 14 - "MainWindow"
Cohesion: 0.09
Nodes (11): QMainWindow, Slot, MainWindow, FlowRecord, Pin the logo to the top-left of the menu bar., Export every locally saved session to one portable archive., Flush state that lives in widgets rather than the flow repository., Return a fresh Collaborator payload host, or None if unavailable. Called by… (+3 more)

### Community 15 - "FlowRecord"
Cohesion: 0.11
Nodes (12): Row, Storage layer: SQLite persistence + on-disk body store., FlowRecord, A single captured HTTP request/response exchange. Body payloads are represented…, The response content type without parameters (e.g. ``text/html``)., File extension derived from the request path (without the dot). The query…, FlowRepository, SQLite persistence for captured flows. Uses the stdlib ``sqlite3`` module… (+4 more)

### Community 16 - "FlowLayout"
Cohesion: 0.15
Nodes (7): Orientations, QLayout, QLayoutItem, FlowLayout, QRect, QSize, QWidget

### Community 17 - "body_format.py"
Cohesion: 0.20
Nodes (15): format_body(), _format_c_like(), _format_css(), _format_form(), _format_html(), _format_js(), _format_json(), _format_xml() (+7 more)

### Community 18 - "HttpHighlighter"
Cohesion: 0.15
Nodes (12): QSyntaxHighlighter, QTextCharFormat, _fmt(), HttpHighlighter, Lightweight syntax highlighting for raw HTTP messages. Uses…, Highlights HTTP start-lines and headers., Re-color for a new theme mode and re-highlight the document., MarkerHighlighter (+4 more)

### Community 19 - "ProxyTab"
Cohesion: 0.09
Nodes (12): FlowTableModel, QWidget, ProxyTab, Proxy tab: Target scope, proxy controls, and HTTP History / Intercept tabs. The…, Container widget for everything under the top-level "Proxy" tab., Collapse the Target panel to an arrow, or restore its full width., Use Qt's native arrow icon so the control does not depend on fonts., The Clear History button now lives in the Intercept control row. Exposed here… (+4 more)

### Community 20 - "collaborator_tab.py"
Cohesion: 0.12
Nodes (17): _encode_xid(), generate_xid(), Interaction, _now_iso(), Interactsh (OAST) client for the Collaborator feature. This is a small, Qt-free…, A single out-of-band interaction reported by the server., Everything needed to resume / persist a registered session., Return a 20-char XID string. XID layout: 4-byte time, 3-byte machine id, 2-byte… (+9 more)

### Community 21 - "parse_request_text"
Cohesion: 0.27
Nodes (5): host_from_headers_or_url(), parse_request_text(), ParsedRequest, Determine (scheme, host, port, path) for sending a parsed request. Prefers an…, Parse raw HTTP request text into a :class:`ParsedRequest`. Tolerant of both…

### Community 22 - "_HTMLPretty"
Cohesion: 0.22
Nodes (4): HTMLParser, _HTMLPretty, Lenient HTML pretty-printer built on the stdlib parser. Emits nicely indented…, Close a preceding sibling with an optional end tag, if applicable.

### Community 23 - "AttackRunner"
Cohesion: 0.18
Nodes (9): QObject, HttpResult, AttackJob, One request to send: the substituted text and the payloads used., AttackRunner, Slot, Drives an Intruder attack: iterate jobs, send them, collect results. The runner…, Launch requests until we hit the concurrency cap or run out. (+1 more)

### Community 24 - "InteractionsModel"
Cohesion: 0.16
Nodes (9): InteractionRow, InteractionsModel, protocol_color(), QAbstractTableModel, QModelIndex, Render an ISO timestamp as HH:MM:SS, falling back to the raw string., Return a hex color for an interaction protocol., A received interaction plus the display metadata we derive from it. (+1 more)

### Community 25 - "IntruderTab"
Cohesion: 0.16
Nodes (8): IntruderTab, Path, QWidget, Close every Intruder tab., Open a new session tab populated from a captured flow., Write every open session to ``path`` as JSON (list of snapshots)., Recreate the sessions saved by :meth:`save_state`. Accepts both the multi-…, Holds multiple :class:`IntruderSession` instances in a tab strip.

### Community 26 - "repeater_session.py"
Cohesion: 0.14
Nodes (12): build_response_text(), Assemble a raw HTTP response string from parts., Plain data structures passed between the proxy engine, storage, and UI. These…, content_type_from_headers(), Extract the Content-Type value from a raw header block (case-insensitive)., Reusable side-by-side request/response viewer. Used by the Proxy history, the…, Custom QAbstractTableModel backing the traffic history view. We use a hand-…, HTTP history: the traffic table plus a request/response detail view. Emits a… (+4 more)

### Community 27 - "._select_next_pending"
Cohesion: 0.16
Nodes (7): A request was paused by the proxy; add it to the table., A response was paused by the proxy; add it to the table., The user picked a row in the activity table; show that flow., Show a request (editable when pending) in the Request pane., Show a paused response: request read-only on the left, editable response on the…, Select the first still-pending item (request or response), or clear., Drop every still-pending request and response, and remove their rows.

### Community 28 - "app.py"
Cohesion: 0.20
Nodes (11): QApplication, main(), Application entry point. Creates the Qt application, builds the main window,…, Give Windows an explicit AppUserModelID so the taskbar uses our icon. Without…, _set_windows_app_id(), Bidoytu - an intercepting HTTP proxy tool. Base architecture: - Proxy/MITM…, Enables ``python -m bidoytu``., apply_theme() (+3 more)

### Community 29 - "_Chip"
Cohesion: 0.26
Nodes (3): QMouseEvent, _Chip, A single clickable tab chip with an optional close button.

### Community 30 - "QColor"
Cohesion: 0.21
Nodes (12): QColor, QPalette, Item delegate for the HTTP history table. This delegate paints every cell…, A soft, muted tint of the accent used to fill the selected row. Uses the shared…, _selection_fill(), _blend(), _dark_palette(), highlight_bg() (+4 more)

### Community 31 - "AsyncHttpSender"
Cohesion: 0.19
Nodes (5): ResultCallback, AsyncHttpSender, _schedule(), Schedule a request; ``callback`` is invoked on the sender thread. Returns a…, Owns a background event loop running httpx.AsyncClient instances.

### Community 32 - "._open_or_recover"
Cohesion: 0.29
Nodes (4): Connection, Path, Move the corrupt database and SQLite sidecars to a safe backup., Open and validate the database, recovering from SQLite corruption. A damaged…

### Community 33 - ".restore_state"
Cohesion: 0.20
Nodes (3): Path, Persist the session, generated payloads, and interactions to JSON., Restore a session saved by :meth:`save_state` and re-register it.

### Community 34 - "CaCertDialog"
Cohesion: 0.33
Nodes (5): CaCertDialog, Path, QDialog, Dialog for exporting and installing the proxy's CA certificate. To intercept…, Shows CA status, an export button, and install instructions.

### Community 35 - "GroupDialog"
Cohesion: 0.27
Nodes (3): GroupDialog, QDialog, Collect a group name, member tabs, and a color.

### Community 36 - "repeater_tab.py"
Cohesion: 0.14
Nodes (9): Dialog for adding Repeater request tabs to a named, colored group. Presents a…, Serializable snapshot of a session (for persistence)., SessionState, Group, Path, Repeater tab: a container of independent request/response sessions. Each "Send…, A named, colored, collapsible collection of member sessions., Write all open sessions and their groups to ``path`` as JSON. (+1 more)

### Community 37 - "WrappingTabBar"
Cohesion: 0.26
Nodes (5): QScrollArea, QSize, Group-aware, wrapping tab bar composed of chip widgets., Rebuild the whole bar from the container's model. Args: order: list of keys…, WrappingTabBar

### Community 38 - "RepeaterTab"
Cohesion: 0.15
Nodes (8): QWidget, Clone a session's request into a new tab, named ``base (n)``., Return ``base (n)`` with the smallest unused positive integer n., Delete a group along with all request tabs it contains., Close every request tab and remove all groups., Open a new session tab populated from a captured flow., Holds multiple :class:`RepeaterSession` instances with a wrapping bar., RepeaterTab

### Community 39 - "main_window.py"
Cohesion: 0.21
Nodes (8): finish(), poll_for_ca(), Verify the CA is generated in Bidoytu's confdir and can be exported. Starts the…, after_start(), finish(), Reproduce the 'start proxy crashes' path using the real MainWindow. Builds the…, send(), Main application window. Top-level layout is a QTabWidget with four tabs: -…

### Community 41 - "async_sender.py"
Cohesion: 0.22
Nodes (4): Live test: RepeaterTab.load_from_record + Send performs a real request., Async HTTP sender for Repeater/Intruder. Runs an ``httpx.AsyncClient`` on a…, Networking helpers (async HTTP client for Repeater/Intruder)., Intruder tab: a container of independent attack sessions. Each "Send to…

### Community 42 - "intercept_response_live_test.py"
Cohesion: 0.31
Nodes (7): check_done(), do_forward(), finish(), on_intercepted(), on_started(), Live: intercept a request via the real MainWindow, forward it, and confirm the…, send()

### Community 44 - "._forward_pending_and_clear"
Cohesion: 0.22
Nodes (4): Forward every still-pending flow, then reset the panel. Called when…, Remember the editor text for the currently selected pending flow., Forward every still-pending request and response. The selected one uses its…, Find the FlowRecord for a flow_id (optionally filtered by direction) currently…

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
Cohesion: 0.12
Nodes (14): on_started(), Verify the capture addon stores DECODED bodies (gzip is undone). Routes a…, Verify starting the proxy on an occupied port produces a clean error signal…, host_matches_scope(), matches(), _normalise_scope_entry(), ProxyConfig, Application configuration and filesystem paths. Everything the app writes… (+6 more)

### Community 52 - "current_mode"
Cohesion: 0.24
Nodes (6): A wrapping flow layout: children flow left-to-right and wrap to new rows. This…, current_mode(), Return the named color tokens for ``mode`` (falls back to dark)., Return the theme mode currently applied to the application., tokens(), A wrapping, group-aware tab bar built from individual chip widgets. Unlike…

### Community 53 - "CLAUDE.md"
Cohesion: 0.20
Nodes (8): Architecture and layering (respect this), Conventions, Git workflow, Gotchas learned the hard way, Tech stack, Verifying changes (always do this), What Bidoytu is, Where things live

### Community 54 - "logo_path"
Cohesion: 0.39
Nodes (7): asset_path(), _assets_dir(), logo_path(), Path, Locators for bundled resources (icons, images). Resources live under…, Return the absolute path to a bundled asset by file name., Absolute path to the application logo.

### Community 55 - "Building and releasing Bidoytu"
Cohesion: 0.20
Nodes (9): Build (Windows or Linux), Building and releasing Bidoytu, Cutting version 1.0.0, How releases work (CI/CD), Local builds (optional), Notes, Nuitka (alternative compiler), Prerequisites (+1 more)

### Community 56 - ".__init__"
Cohesion: 0.50
Nodes (4): Pattern, _compile(), GrepConfig, How to derive match/extract columns from each response.

### Community 57 - "_NoFocusRectStyle"
Cohesion: 0.60
Nodes (3): QProxyStyle, _NoFocusRectStyle, Application style that suppresses the item-view focus rectangle globally. The…

### Community 58 - "Security Policy"
Cohesion: 0.22
Nodes (8): Handling the CA certificate, Reporting a vulnerability, Responsible and lawful use, Safe defaults and data handling, Scope, Security Policy, Supported versions, What to expect

### Community 60 - "QMenu"
Cohesion: 0.17
Nodes (5): QMenu, Install (or clear) the dropdown's group-send options. ``actions`` is a list of…, Record which send mode the split button runs, and show it on the button., Ask the provider for a payload and insert it at the cursor., Build a FlowRecord from the current (edited) request text.

### Community 63 - "WorkspaceManager"
Cohesion: 0.10
Nodes (17): QDialog, Startup picker for local Bidoytu workspaces., Choose, create, import, or export local workspaces before app startup., WorkspaceDialog, _now(), Path, Local, Burp-style workspace management. Each workspace owns its SQLite history,…, Remove every deletable workspace while keeping the legacy recovery one. (+9 more)

### Community 65 - "Contributing to Bidoytu"
Cohesion: 0.25
Nodes (7): Branches and pull requests, Checks, Contributing to Bidoytu, Design rules, License, Local setup, Security issues

### Community 67 - "http_utils.py"
Cohesion: 0.15
Nodes (12): absolute_url(), build_request_text(), ensure_host_header(), _headers_have(), parse_response_text(), ParsedResponse, Helpers for converting between raw HTTP text and structured parts. Used by…, Parse raw HTTP response text into a :class:`ParsedResponse`. Tolerant of both… (+4 more)

## Knowledge Gaps
- **39 isolated node(s):** `Architecture`, `Development workflow`, `Highlights`, `License`, `Packaging and releases` (+34 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 499 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `CollaboratorTab` connect `CollaboratorTab` to `.restore_state`, `MessageView`, `IntruderSession`, `InteractshClient`, `InteractionFilterProxy`, `collaborator_tab.py`, `InteractionsModel`, `.__init__`, `AsyncHttpSender`?**
  _High betweenness centrality (0.121) - this node is a cross-community bridge._
- **Why does `FlowRecord` connect `FlowRecord` to `InterceptView`, `MessageView`, `http_utils.py`, `HistoryView`, `repeater_tab.py`, `IntruderSession`, `InterceptActivityModel`, `.cookies`, `intruder_session.py`, `async_sender.py`, `RepeaterSession`, `RepeaterTab`, `IntruderTab`, `repeater_session.py`, `._select_next_pending`, `QMenu`, `AsyncHttpSender`?**
  _High betweenness centrality (0.120) - this node is a cross-community bridge._
- **Why does `MessageView` connect `MessageView` to `InterceptView`, `CollaboratorTab`, `IntruderSession`, `intruder_session.py`, `RepeaterSession`, `HttpHighlighter`, `collaborator_tab.py`, `repeater_session.py`?**
  _High betweenness centrality (0.120) - this node is a cross-community bridge._
- **Are the 11 inferred relationships involving `FlowRecord` (e.g. with `FlowRepository` and `DetailView`) actually correct?**
  _`FlowRecord` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `IntruderSession` (e.g. with `AsyncHttpSender` and `PayloadSet`) actually correct?**
  _`IntruderSession` has 15 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `RepeaterSession` (e.g. with `AsyncHttpSender` and `HttpResult`) actually correct?**
  _`RepeaterSession` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `CollaboratorTab` (e.g. with `CollaboratorConfig` and `AsyncHttpSender`) actually correct?**
  _`CollaboratorTab` has 10 INFERRED edges - model-reasoned connections that need verification._
# Graph Report - Bidoytu  (2026-09-14)

## Corpus Check
- 63 files · ~126,624 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 5 file(s) not represented in the graph (top: (none) 3, .spec 1, .ico 1)

## Summary
- 1172 nodes · 2294 edges · 79 communities (65 shown, 14 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 174 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `c841c0cc`
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
- RepeaterTab
- IntruderResultsModel
- ProxyEngine
- CaptureAddon
- MainWindow
- FlowRepository
- FlowLayout
- PayloadSetEditor
- engine.py
- iter_jobs
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
- parse_request_text
- QHBoxLayout
- HttpHighlighter
- GroupDialog
- QColor
- WrappingTabBar
- apply_theme
- SessionState
- ca_export_test.py
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
- ProxyTab
- .restore_state
- Security Policy
- intercept_view.py
- .__init__
- attack_runner.py
- FlowRecord
- main_window.py
- .send
- Contributing to Bidoytu
- ui/__init__.py
- strip_markers
- bidoytu
- capture_addon.py
- ._restore_attack
- AGENTS.md
- CONTRIBUTORS.md
- .intercept_response_for
- .resolve
- .set_intercept_responses
- repeater_session.py
- .resolve_response
- Path

## God Nodes (most connected - your core abstractions)
1. `FlowRecord` - 73 edges
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
- `test_intercept_view()` --uses--> `InterceptView`  [INFERRED]
  scripts/smoke_test.py → src/bidoytu/ui/intercept_view.py
- `test_qt_and_proxy_apis()` --uses--> `MainWindow`  [INFERRED]
  scripts/smoke_test.py → src/bidoytu/ui/main_window.py
- `test_qt_and_proxy_apis()` --uses--> `FlowTableModel`  [INFERRED]
  scripts/smoke_test.py → src/bidoytu/ui/flow_table_model.py
- `test_qt_and_proxy_apis()` --uses--> `AppConfig`  [INFERRED]
  scripts/smoke_test.py → src/bidoytu/config.py
- `test_intercept_view()` --uses--> `FlowRecord`  [INFERRED]
  scripts/smoke_test.py → src/bidoytu/storage/models.py

## Import Cycles
- None detected.

## Communities (79 total, 14 thin omitted)

### Community 0 - "theme.py"
Cohesion: 0.17
Nodes (19): QPixmap, _blank_pixmap(), _build_qss(), _check_icon(), _chevron_down_icon(), _chevron_icon(), _chevron_up_icon(), _close_icon() (+11 more)

### Community 1 - "InterceptView"
Cohesion: 0.07
Nodes (19): InterceptView, QWidget, Size the activity table so URL fills the leftover width, while every column…, Whenever a column is resized, compensate its immediate right neighbor (or left…, Reflow the URL column to absorb the viewport's leftover width. URL is the…, Forward every still-pending flow, then reset the panel. Called when…, A request was paused by the proxy; add it to the table., A response was paused by the proxy; add it to the table. (+11 more)

### Community 2 - "MessageView"
Cohesion: 0.08
Nodes (14): hex_dump(), _LineNumberArea, MessageView, QPlainTextEdit, QRect, QSize, QWidget, Switch how the remembered body is rendered and re-display it. (+6 more)

### Community 3 - "CollaboratorTab"
Cohesion: 0.10
Nodes (7): CollaboratorTab, Slot, Render a raw HTTP message, pretty-printing its body by content-type. Splits…, Attach a note (e.g. the target tab) to the most recent payload., Generate a payload, tag it with ``note``, and return the hostname. Used by…, Register with an Interactsh server, hand out payloads, show callbacks., Stop polling and deregister on application close (best-effort).

### Community 4 - "HistoryView"
Cohesion: 0.10
Nodes (10): DetailView, QWidget, Two MessageViews (request | response) with a shared soft-wrap toggle., HistoryView, QWidget, Slot, Whenever a column is resized, compensate its immediate right neighbor (or left…, Reflow the Path column to absorb the viewport's leftover width. Path is the… (+2 more)

### Community 5 - "AppConfig"
Cohesion: 0.13
Nodes (12): AppConfig, _default_data_dir(), Path, JSON file holding Collaborator session state across restarts. Stores the active…, Directory where mitmproxy stores its generated CA and certs. We keep it under…, PEM-encoded CA certificate (for Firefox, curl, most Linux tools)., DER/.cer CA certificate (convenient for the Windows cert store)., Create the data, body, and CA directories if they do not exist. (+4 more)

### Community 6 - "IntruderSession"
Cohesion: 0.11
Nodes (6): QMenu, IntruderSession, Slot, Return a JSON-serializable snapshot of this session., Build a FlowRecord from the template (payload markers removed)., One Intruder attack: template + positions + payload sets + results.

### Community 7 - "InterceptActivityModel"
Cohesion: 0.08
Nodes (14): ActivityRow, InterceptActivityModel, Orientation, QAbstractTableModel, QModelIndex, Log a paused (pending) request. Returns its row index., Log a paused (pending) response. Returns its row index., True if the row is a still-pending request or response. (+6 more)

### Community 8 - "intruder_session.py"
Cohesion: 0.14
Nodes (23): PayloadSet, Intruder attack model: markers, attack types, and request building. Qt-free so…, Wrap the ``[sel_start, sel_end)`` span of ``text`` in ``§`` markers. Used by…, A generator plus its processing rules (one Intruder payload set)., wrap_selection(), _apply_one(), apply_rules(), _brute() (+15 more)

### Community 9 - "InteractshClient"
Cohesion: 0.10
Nodes (13): Exception, InteractshClient, _cb(), _cb(), InteractshError, Raised for registration / polling / crypto failures., Register with, generate payloads for, and poll an Interactsh server. The client…, Generate a keypair and register against the first working server. ``servers``… (+5 more)

### Community 10 - "RepeaterTab"
Cohesion: 0.15
Nodes (8): QWidget, Clone a session's request into a new tab, named ``base (n)``., Return ``base (n)`` with the smallest unused positive integer n., Delete a group along with all request tabs it contains., Close every request tab and remove all groups., Open a new session tab populated from a captured flow., Holds multiple :class:`RepeaterSession` instances with a wrapping bar., RepeaterTab

### Community 11 - "IntruderResultsModel"
Cohesion: 0.11
Nodes (10): One completed request in the results table., ResultRow, IntruderResultsModel, QAbstractTableModel, QModelIndex, QSortFilterProxyModel, Table model + filter proxy for Intruder attack results.…, Filter results by status, min length, matched-only, and a text needle. (+2 more)

### Community 12 - "ProxyEngine"
Cohesion: 0.08
Nodes (12): QThread, ProxyConfig, Listen settings for the mitmproxy engine., ProxyEngine, Toggle the global 'intercept responses' behavior., Arm a one-shot response intercept for a single flow., Forward a paused request, optionally with edited raw request text., Drop a paused request. (+4 more)

### Community 13 - "CaptureAddon"
Cohesion: 0.23
Nodes (8): HTTPFlow, CaptureAddon, _PendingFlow, Rewrite a flow's request from edited raw text before forwarding., Rewrite a flow's response from edited raw text before forwarding., Return the decoded (decompressed) body; fall back to raw bytes., State for a single intercepted (paused) flow., Emits FlowRecords and optionally pauses flows for interception.

### Community 14 - "MainWindow"
Cohesion: 0.15
Nodes (5): QMainWindow, MainWindow, Slot, Return a fresh Collaborator payload host, or None if unavailable. Called by…, Load a file-backed request body inline so editors can show it.

### Community 15 - "FlowRepository"
Cohesion: 0.06
Nodes (29): Connection, FlowRecord, Path, QApplication, Row, main(), Path, Import + wiring smoke test (no live proxy, no visible window). Verifies: - all… (+21 more)

### Community 16 - "FlowLayout"
Cohesion: 0.15
Nodes (7): Orientations, QLayout, QLayoutItem, FlowLayout, QRect, QSize, QWidget

### Community 17 - "PayloadSetEditor"
Cohesion: 0.15
Nodes (6): PayloadSetEditor, ProcessingRuleDialog, QDialog, QWidget, Edit one payload set: a generator plus a processing-rule pipeline., Configure a single :class:`ProcessingRule`.

### Community 18 - "engine.py"
Cohesion: 0.18
Nodes (5): on_started(), Verify the capture addon stores DECODED bodies (gzip is undone). Routes a…, Verify starting the proxy on an occupied port produces a clean error signal…, Runs mitmproxy inside a dedicated QThread. Design: - mitmproxy is asyncio-…, Proxy engine package (mitmproxy running inside a QThread).

### Community 19 - "iter_jobs"
Cohesion: 0.21
Nodes (11): count_jobs(), find_markers(), iter_jobs(), Marker, Insert ``values`` into ``clean_text`` at each marker (right-to-left). Working…, Best-effort total request count for a configured attack., Yield an :class:`AttackJob` per request for the configured attack.…, A payload position: the span between a pair of ``§`` markers. ``start``/``end``… (+3 more)

### Community 20 - "collaborator_tab.py"
Cohesion: 0.12
Nodes (17): _encode_xid(), generate_xid(), Interaction, _now_iso(), Interactsh (OAST) client for the Collaborator feature. This is a small, Qt-free…, A single out-of-band interaction reported by the server., Everything needed to resume / persist a registered session., Return a 20-char XID string. XID layout: 4-byte time, 3-byte machine id, 2-byte… (+9 more)

### Community 21 - "RepeaterSession"
Cohesion: 0.11
Nodes (7): Slot, Install (or clear) the dropdown's group-send options. ``actions`` is a list of…, Record which send mode the split button runs, and show it on the button., Ask the provider for a payload and insert it at the cursor., Build a FlowRecord from the current (edited) request text., One request/response pane with full Repeater controls., RepeaterSession

### Community 22 - "_HTMLPretty"
Cohesion: 0.22
Nodes (4): HTMLParser, _HTMLPretty, Lenient HTML pretty-printer built on the stdlib parser. Emits nicely indented…, Close a preceding sibling with an optional end tag, if applicable.

### Community 23 - "AttackRunner"
Cohesion: 0.20
Nodes (8): QObject, HttpResult, AttackJob, One request to send: the substituted text and the payloads used., AttackRunner, Slot, Launch requests until we hit the concurrency cap or run out., Runs one attack, emitting a :class:`ResultRow` per completed request.

### Community 24 - "InteractionsModel"
Cohesion: 0.16
Nodes (9): InteractionRow, InteractionsModel, protocol_color(), QAbstractTableModel, QModelIndex, Render an ISO timestamp as HH:MM:SS, falling back to the raw string., Return a hex color for an interaction protocol., A received interaction plus the display metadata we derive from it. (+1 more)

### Community 25 - "IntruderTab"
Cohesion: 0.15
Nodes (8): IntruderTab, Path, QWidget, Close every Intruder tab., Open a new session tab populated from a captured flow., Write every open session to ``path`` as JSON (list of snapshots)., Recreate the sessions saved by :meth:`save_state`. Accepts both the multi-…, Holds multiple :class:`IntruderSession` instances in a tab strip.

### Community 26 - "models.py"
Cohesion: 0.16
Nodes (7): Live test: RepeaterTab.load_from_record + Send performs a real request., Plain data structures passed between the proxy engine, storage, and UI. These…, Custom QAbstractTableModel backing the traffic history view. We use a hand-…, HTTP history: the traffic table plus a request/response detail view. Emits a…, Table model for the Intercept tab's activity log. Each intercepted request…, Proxy tab: proxy start/stop controls + HTTP History / Intercept sub-tabs. The…, Repeater tab: a container of independent request/response sessions. Each "Send…

### Community 27 - "content_type_from_headers"
Cohesion: 0.25
Nodes (7): ensure_host_header(), _headers_have(), Return True if the raw header block already contains ``name`` (case-…, Return the header block with a ``Host`` header guaranteed to be present. If…, content_type_from_headers(), Extract the Content-Type value from a raw header block (case-insensitive)., Reusable side-by-side request/response viewer. Used by the Proxy history, the…

### Community 28 - "body_format.py"
Cohesion: 0.20
Nodes (15): format_body(), _format_c_like(), _format_css(), _format_form(), _format_html(), _format_js(), _format_json(), _format_xml() (+7 more)

### Community 29 - "_Chip"
Cohesion: 0.26
Nodes (3): QMouseEvent, _Chip, A single clickable tab chip with an optional close button.

### Community 30 - "FlowTableModel"
Cohesion: 0.21
Nodes (5): FlowTableModel, Orientation, QAbstractTableModel, QModelIndex, Add a new record, or update an existing one in place. Called from the UI thread…

### Community 31 - "AsyncHttpSender"
Cohesion: 0.20
Nodes (5): AsyncHttpSender, Async HTTP sender for Repeater/Intruder. Runs an ``httpx.AsyncClient`` on a…, Owns a background event loop running httpx.AsyncClient instances., Networking helpers (async HTTP client for Repeater/Intruder)., Intruder tab: a container of independent attack sessions. Each "Send to…

### Community 32 - "parse_request_text"
Cohesion: 0.17
Nodes (9): absolute_url(), host_from_headers_or_url(), parse_request_text(), ParsedRequest, Helpers for converting between raw HTTP text and structured parts. Used by…, Reconstruct an absolute URL from flow parts (path may be absolute)., Determine (scheme, host, port, path) for sending a parsed request. Prefers an…, Parse raw HTTP request text into a :class:`ParsedRequest`. Tolerant of both… (+1 more)

### Community 33 - "QHBoxLayout"
Cohesion: 0.13
Nodes (13): FindFlags, QHBoxLayout, QKeyEvent, QPushButton, QWidget, Build a titled pane (label + find bar + view), matching Repeater., FindBar, QPlainTextEdit (+5 more)

### Community 34 - "HttpHighlighter"
Cohesion: 0.17
Nodes (10): QSyntaxHighlighter, HttpHighlighter, Lightweight syntax highlighting for raw HTTP messages. Uses…, Highlights HTTP start-lines and headers., Re-color for a new theme mode and re-highlight the document., MarkerHighlighter, Highlighter for the Intruder request template. A…, HTTP highlighting plus a highlighted background for ``§payload§`` spans. (+2 more)

### Community 35 - "GroupDialog"
Cohesion: 0.22
Nodes (4): GroupDialog, QDialog, Dialog for adding Repeater request tabs to a named, colored group. Presents a…, Collect a group name, member tabs, and a color.

### Community 36 - "QColor"
Cohesion: 0.17
Nodes (13): QColor, QStyledItemDelegate, QTextCharFormat, _fmt(), HistoryItemDelegate, Item delegate for the HTTP history table. This delegate paints every cell…, A soft, muted tint of the accent used to fill the selected row. Uses the shared…, Fully self-painted cells: soft row wash + slim accent bar, no style frame. (+5 more)

### Community 37 - "WrappingTabBar"
Cohesion: 0.26
Nodes (5): QScrollArea, QSize, Group-aware, wrapping tab bar composed of chip widgets., Rebuild the whole bar from the container's model. Args: order: list of keys…, WrappingTabBar

### Community 38 - "apply_theme"
Cohesion: 0.20
Nodes (11): QPalette, QProxyStyle, apply_theme(), _dark_palette(), _light_palette(), _NoFocusRectStyle, _palette_from_tokens(), Application style that suppresses the item-view focus rectangle globally. The… (+3 more)

### Community 39 - "SessionState"
Cohesion: 0.18
Nodes (7): Serializable snapshot of a session (for persistence)., SessionState, Group, Path, A named, colored, collapsible collection of member sessions., Write all open sessions and their groups to ``path`` as JSON., Recreate sessions and groups saved by :meth:`save_sessions`.

### Community 40 - "ca_export_test.py"
Cohesion: 0.67
Nodes (3): finish(), poll_for_ca(), Verify the CA is generated in Bidoytu's confdir and can be exported. Starts the…

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
Cohesion: 0.22
Nodes (5): CollaboratorConfig, Settings for the Collaborator (out-of-band interaction) feature. Attributes:…, InteractionFilterProxy, QSortFilterProxyModel, Filter interactions by protocol and a free-text needle.

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

### Community 56 - "ProxyTab"
Cohesion: 0.21
Nodes (5): ProxyTab, QWidget, The Clear History button now lives in the Intercept control row. Exposed here…, Surface a detailed transient message (e.g. "Starting...", errors) on the…, Container widget for everything under the top-level "Proxy" tab.

### Community 57 - ".restore_state"
Cohesion: 0.18
Nodes (4): Path, Best-effort correlate an interaction back to a generated payload., Persist the session, generated payloads, and interactions to JSON., Restore a session saved by :meth:`save_state` and re-register it.

### Community 58 - "Security Policy"
Cohesion: 0.22
Nodes (8): Handling the CA certificate, Reporting a vulnerability, Responsible and lawful use, Safe defaults and data handling, Scope, Security Policy, Supported versions, What to expect

### Community 59 - "intercept_view.py"
Cohesion: 0.22
Nodes (6): build_request_text(), build_response_text(), Assemble a raw HTTP response string from parts., Assemble a raw HTTP request string from parts. When ``host`` is provided, a…, Intercept panel: pause, edit, and forward/drop in-flight requests. When…, Show a paused response: request read-only on the left, editable response on the…

### Community 61 - "attack_runner.py"
Cohesion: 0.38
Nodes (5): Pattern, _compile(), GrepConfig, Drives an Intruder attack: iterate jobs, send them, collect results. The runner…, How to derive match/extract columns from each response.

### Community 62 - "FlowRecord"
Cohesion: 0.14
Nodes (6): FlowRecord, A single captured HTTP request/response exchange. Body payloads are represented…, The response content type without parameters (e.g. ``text/html``)., File extension derived from the request path (without the dot). The query…, Cookie names sent/received for this flow, comma-separated. Collects request…, Replace all rows (e.g. when loading history from the database).

### Community 63 - "main_window.py"
Cohesion: 0.14
Nodes (17): main(), Application entry point. Creates the Qt application, builds the main window,…, Give Windows an explicit AppUserModelID so the taskbar uses our icon. Without…, _set_windows_app_id(), Application configuration and filesystem paths. Everything the app writes…, Bidoytu - an intercepting HTTP proxy tool. Base architecture: - Proxy/MITM…, Enables ``python -m bidoytu``., asset_path() (+9 more)

### Community 64 - ".send"
Cohesion: 0.33
Nodes (3): ResultCallback, _schedule(), Schedule a request; ``callback`` is invoked on the sender thread. Returns a…

### Community 65 - "Contributing to Bidoytu"
Cohesion: 0.25
Nodes (7): Branches and pull requests, Checks, Contributing to Bidoytu, Design rules, License, Local setup, Security issues

### Community 67 - "strip_markers"
Cohesion: 0.33
Nodes (3): Return the template with all ``§`` markers removed (defaults kept)., strip_markers(), Wrap each ``name=value`` value (query + body) in markers.

### Community 69 - "capture_addon.py"
Cohesion: 0.40
Nodes (4): parse_response_text(), ParsedResponse, Parse raw HTTP response text into a :class:`ParsedResponse`. Tolerant of both…, mitmproxy addon: maps flows to FlowRecords and supports interception. Two…

### Community 76 - "repeater_session.py"
Cohesion: 0.33
Nodes (4): Raw HTTP message viewer/editor (headers + body) with highlighting. Soft wrap is…, HistoryEntry, A single Repeater session: one editable request + its response. Bundles the…, A request that was sent and (optionally) the response it produced.

## Knowledge Gaps
- **39 isolated node(s):** `Architecture`, `Development workflow`, `Highlights`, `License`, `Packaging and releases` (+34 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 464 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **14 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `FlowRecord` connect `FlowRecord` to `InterceptView`, `HistoryView`, `IntruderSession`, `InterceptActivityModel`, `intruder_session.py`, `RepeaterTab`, `ProxyEngine`, `CaptureAddon`, `MainWindow`, `FlowRepository`, `engine.py`, `RepeaterSession`, `IntruderTab`, `models.py`, `content_type_from_headers`, `FlowTableModel`, `AsyncHttpSender`, `intercept_view.py`, `main_window.py`, `.send`, `capture_addon.py`, `repeater_session.py`?**
  _High betweenness centrality (0.248) - this node is a cross-community bridge._
- **Why does `IntruderSession` connect `IntruderSession` to `parse_request_text`, `QHBoxLayout`, `HttpHighlighter`, `strip_markers`, `MessageView`, `._restore_attack`, `intruder_session.py`, `IntruderResultsModel`, `PayloadSetEditor`, `iter_jobs`, `AttackRunner`, `IntruderTab`, `attack_runner.py`, `FlowRecord`, `AsyncHttpSender`?**
  _High betweenness centrality (0.106) - this node is a cross-community bridge._
- **Why does `MessageView` connect `MessageView` to `QHBoxLayout`, `InterceptView`, `CollaboratorTab`, `HistoryView`, `HttpHighlighter`, `IntruderSession`, `intruder_session.py`, `intercept_view.py`, `repeater_session.py`, `MainWindow`, `collaborator_tab.py`, `RepeaterSession`, `content_type_from_headers`, `main_window.py`?**
  _High betweenness centrality (0.106) - this node is a cross-community bridge._
- **Are the 16 inferred relationships involving `FlowRecord` (e.g. with `test_intercept_view()` and `test_qt_and_proxy_apis()`) actually correct?**
  _`FlowRecord` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `IntruderSession` (e.g. with `AsyncHttpSender` and `PayloadSet`) actually correct?**
  _`IntruderSession` has 15 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `RepeaterSession` (e.g. with `AsyncHttpSender` and `HttpResult`) actually correct?**
  _`RepeaterSession` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `CollaboratorTab` (e.g. with `CollaboratorConfig` and `AsyncHttpSender`) actually correct?**
  _`CollaboratorTab` has 10 INFERRED edges - model-reasoned connections that need verification._
# Graph Report - Bidoytu  (2026-09-14)

## Corpus Check
- 65 files · ~128,151 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 5 file(s) not represented in the graph (top: (none) 3, .spec 1, .ico 1)

## Summary
- 1221 nodes · 2352 edges · 74 communities (57 shown, 17 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 185 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `16b2daaa`
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
- body_format.py
- PayloadSetEditor
- strip_markers
- collaborator_tab.py
- RepeaterSession
- _HTMLPretty
- AsyncHttpSender
- InteractionsModel
- IntruderTab
- FlowRecord
- content_type_from_headers
- smoke_test.py
- _Chip
- FindBar
- iter_jobs
- CaCertDialog
- capture_addon.py
- bidoytu/__init__.py
- repeater_tab.py
- QMenu
- WrappingTabBar
- start_proxy_repro.py
- SessionState
- config.py
- Path
- intercept_response_live_test.py
- _GroupHeaderChip
- ProcessingRuleDialog
- intercept_live_test.py
- InteractionFilterProxy
- _FlowHost
- proxy_live_test.py
- ._update_group_send_menu
- Bidoytu
- gzip_decode_test.py
- current_mode
- CLAUDE.md
- ._show_raw
- Building and releasing Bidoytu
- Slot
- Interaction
- Security Policy
- QDialog
- Path
- WorkspaceManager
- engine.py
- Contributing to Bidoytu
- ui/__init__.py
- repeater_session.py
- bidoytu
- AGENTS.md
- CONTRIBUTORS.md
- .__init__
- .intercept_response_for
- .resolve
- .resolve_response
- .set_intercept_responses

## God Nodes (most connected - your core abstractions)
1. `FlowRecord` - 73 edges
2. `IntruderSession` - 60 edges
3. `RepeaterSession` - 57 edges
4. `CollaboratorTab` - 48 edges
5. `MessageView` - 43 edges
6. `InterceptView` - 41 edges
7. `RepeaterTab` - 37 edges
8. `MainWindow` - 36 edges
9. `AsyncHttpSender` - 32 edges
10. `InterceptActivityModel` - 29 edges

## Surprising Connections (you probably didn't know these)
- `test_qt_and_proxy_apis()` --uses--> `MainWindow`  [INFERRED]
  scripts/smoke_test.py → src/bidoytu/ui/main_window.py
- `test_intercept_view()` --uses--> `InterceptView`  [INFERRED]
  scripts/smoke_test.py → src/bidoytu/ui/intercept_view.py
- `test_intercept_view()` --uses--> `FlowRecord`  [INFERRED]
  scripts/smoke_test.py → src/bidoytu/storage/models.py
- `test_qt_and_proxy_apis()` --uses--> `FlowRecord`  [INFERRED]
  scripts/smoke_test.py → src/bidoytu/storage/models.py
- `test_storage_roundtrip()` --uses--> `FlowRecord`  [INFERRED]
  scripts/smoke_test.py → src/bidoytu/storage/models.py

## Import Cycles
- None detected.

## Communities (74 total, 17 thin omitted)

### Community 0 - "theme.py"
Cohesion: 0.06
Nodes (50): QColor, QPalette, QPixmap, QProxyStyle, QSyntaxHighlighter, QTextCharFormat, _fmt(), HttpHighlighter (+42 more)

### Community 1 - "InterceptView"
Cohesion: 0.07
Nodes (19): InterceptView, QWidget, Size the activity table so URL fills the leftover width, while every column…, Whenever a column is resized, compensate its immediate right neighbor (or left…, Reflow the URL column to absorb the viewport's leftover width. URL is the…, Forward every still-pending flow, then reset the panel. Called when…, A request was paused by the proxy; add it to the table., A response was paused by the proxy; add it to the table. (+11 more)

### Community 2 - "MessageView"
Cohesion: 0.06
Nodes (17): DetailView, QWidget, Two MessageViews (request | response) with a shared soft-wrap toggle., hex_dump(), _LineNumberArea, MessageView, QPlainTextEdit, QRect (+9 more)

### Community 3 - "CollaboratorTab"
Cohesion: 0.09
Nodes (10): CollaboratorConfig, Settings for the Collaborator (out-of-band interaction) feature. Attributes:…, CollaboratorTab, QWidget, Slot, Build a titled pane (label + find bar + view), matching Repeater., Attach a note (e.g. the target tab) to the most recent payload., Generate a payload, tag it with ``note``, and return the hostname. Used by… (+2 more)

### Community 4 - "HistoryView"
Cohesion: 0.06
Nodes (21): QStyledItemDelegate, FlowTableModel, Orientation, QAbstractTableModel, QModelIndex, Replace all rows (e.g. when loading history from the database)., Add a new record, or update an existing one in place. Called from the UI thread…, HistoryItemDelegate (+13 more)

### Community 5 - "AppConfig"
Cohesion: 0.15
Nodes (10): AppConfig, Path, JSON file holding Collaborator session state across restarts. Stores the active…, Directory where mitmproxy stores its generated CA and certs. We keep it under…, PEM-encoded CA certificate (for Firefox, curl, most Linux tools)., DER/.cer CA certificate (convenient for the Windows cert store)., Create the data, body, and CA directories if they do not exist., Top-level runtime configuration. Attributes: data_dir: Root directory for all… (+2 more)

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

### Community 10 - "RepeaterTab"
Cohesion: 0.16
Nodes (7): QWidget, Clone a session's request into a new tab, named ``base (n)``., Return ``base (n)`` with the smallest unused positive integer n., Delete a group along with all request tabs it contains., Open a new session tab populated from a captured flow., Holds multiple :class:`RepeaterSession` instances with a wrapping bar., RepeaterTab

### Community 11 - "IntruderResultsModel"
Cohesion: 0.11
Nodes (10): One completed request in the results table., ResultRow, IntruderResultsModel, QAbstractTableModel, QModelIndex, QSortFilterProxyModel, Table model + filter proxy for Intruder attack results.…, Filter results by status, min length, matched-only, and a text needle. (+2 more)

### Community 12 - "ProxyEngine"
Cohesion: 0.08
Nodes (10): QThread, ProxyEngine, Toggle the global 'intercept responses' behavior., Arm a one-shot response intercept for a single flow., Forward a paused request, optionally with edited raw request text., Drop a paused request., Forward a paused response, optionally with edited raw response text., Drop a paused response. (+2 more)

### Community 13 - "CaptureAddon"
Cohesion: 0.27
Nodes (6): HTTPFlow, CaptureAddon, Rewrite a flow's request from edited raw text before forwarding., Rewrite a flow's response from edited raw text before forwarding., Return the decoded (decompressed) body; fall back to raw bytes., Emits FlowRecords and optionally pauses flows for interception.

### Community 14 - "MainWindow"
Cohesion: 0.07
Nodes (17): AppConfig, FlowRecord, QMainWindow, Slot, BodyStore, Path, Content-addressed file store for body payloads. Files are sharded into…, Write ``data`` to the store and return its relative path. Identical content… (+9 more)

### Community 15 - "FlowRepository"
Cohesion: 0.12
Nodes (10): Connection, Row, FlowRepository, Path, Move the corrupt database and SQLite sidecars to a safe backup., Insert a new flow and return its assigned primary key., Update an existing flow (matched by ``flow_id``)., Insert if new, otherwise update. Returns the row id. (+2 more)

### Community 16 - "FlowLayout"
Cohesion: 0.15
Nodes (7): Orientations, QLayout, QLayoutItem, FlowLayout, QRect, QSize, QWidget

### Community 17 - "body_format.py"
Cohesion: 0.18
Nodes (16): format_body(), _format_c_like(), _format_css(), _format_form(), _format_html(), _format_js(), _format_json(), _format_xml() (+8 more)

### Community 18 - "PayloadSetEditor"
Cohesion: 0.20
Nodes (4): QPushButton, PayloadSetEditor, QWidget, Edit one payload set: a generator plus a processing-rule pipeline.

### Community 19 - "strip_markers"
Cohesion: 0.33
Nodes (3): Return the template with all ``§`` markers removed (defaults kept)., strip_markers(), Wrap each ``name=value`` value (query + body) in markers.

### Community 20 - "collaborator_tab.py"
Cohesion: 0.14
Nodes (13): Live test: RepeaterTab.load_from_record + Send performs a real request., Async HTTP sender for Repeater/Intruder. Runs an ``httpx.AsyncClient`` on a…, _encode_xid(), generate_xid(), Interactsh (OAST) client for the Collaborator feature. This is a small, Qt-free…, Everything needed to resume / persist a registered session., Return a 20-char XID string. XID layout: 4-byte time, 3-byte machine id, 2-byte…, Encode 12 raw bytes into the 20-char XID base32 representation. (+5 more)

### Community 21 - "RepeaterSession"
Cohesion: 0.13
Nodes (8): QHBoxLayout, HistoryEntry, QWidget, Slot, Public entry point for the container to send this tab's request., A request that was sent and (optionally) the response it produced., One request/response pane with full Repeater controls., RepeaterSession

### Community 22 - "_HTMLPretty"
Cohesion: 0.22
Nodes (4): HTMLParser, _HTMLPretty, Lenient HTML pretty-printer built on the stdlib parser. Emits nicely indented…, Close a preceding sibling with an optional end tag, if applicable.

### Community 23 - "AsyncHttpSender"
Cohesion: 0.07
Nodes (21): AbstractEventLoop, Pattern, QObject, ResultCallback, AsyncHttpSender, _schedule(), HttpResult, Schedule a request; ``callback`` is invoked on the sender thread. Returns a… (+13 more)

### Community 24 - "InteractionsModel"
Cohesion: 0.15
Nodes (9): InteractionRow, InteractionsModel, protocol_color(), QAbstractTableModel, QModelIndex, Render an ISO timestamp as HH:MM:SS, falling back to the raw string., Return a hex color for an interaction protocol., A received interaction plus the display metadata we derive from it. (+1 more)

### Community 25 - "IntruderTab"
Cohesion: 0.15
Nodes (8): IntruderTab, Path, QWidget, Close every Intruder tab., Open a new session tab populated from a captured flow., Write every open session to ``path`` as JSON (list of snapshots)., Recreate the sessions saved by :meth:`save_state`. Accepts both the multi-…, Holds multiple :class:`IntruderSession` instances in a tab strip.

### Community 26 - "FlowRecord"
Cohesion: 0.10
Nodes (12): FlowRecord, Plain data structures passed between the proxy engine, storage, and UI. These…, A single captured HTTP request/response exchange. Body payloads are represented…, The response content type without parameters (e.g. ``text/html``)., File extension derived from the request path (without the dot). The query…, Cookie names sent/received for this flow, comma-separated. Collects request…, Reusable side-by-side request/response viewer. Used by the Proxy history, the…, Custom QAbstractTableModel backing the traffic history view. We use a hand-… (+4 more)

### Community 27 - "content_type_from_headers"
Cohesion: 0.40
Nodes (3): content_type_from_headers(), Extract the Content-Type value from a raw header block (case-insensitive)., A response arrived. If we forwarded this flow from the intercept panel, show…

### Community 28 - "smoke_test.py"
Cohesion: 0.20
Nodes (13): QApplication, main(), Path, Import + wiring smoke test (no live proxy, no visible window). Verifies: - all…, test_body_format(), test_body_store(), test_http_utils(), test_intercept_view() (+5 more)

### Community 29 - "_Chip"
Cohesion: 0.26
Nodes (3): QMouseEvent, _Chip, A single clickable tab chip with an optional close button.

### Community 30 - "FindBar"
Cohesion: 0.19
Nodes (8): FindFlags, QKeyEvent, FindBar, QPlainTextEdit, QWidget, A small find bar that searches within a QPlainTextEdit. Reusable over any…, Incremental find controls bound to a target text edit., Reveal the bar, seed it with any selected text, and focus input.

### Community 31 - "iter_jobs"
Cohesion: 0.19
Nodes (11): find_markers(), iter_jobs(), Marker, Insert ``values`` into ``clean_text`` at each marker (right-to-left). Working…, Yield an :class:`AttackJob` per request for the configured attack.…, A payload position: the span between a pair of ``§`` markers. ``start``/``end``…, Split a ``§``-marked template into (clean_text, markers). Markers come in…, _splice() (+3 more)

### Community 32 - "CaCertDialog"
Cohesion: 0.33
Nodes (5): CaCertDialog, Path, QDialog, Dialog for exporting and installing the proxy's CA certificate. To intercept…, Shows CA status, an export button, and install instructions.

### Community 33 - "capture_addon.py"
Cohesion: 0.29
Nodes (6): parse_response_text(), ParsedResponse, Parse raw HTTP response text into a :class:`ParsedResponse`. Tolerant of both…, _PendingFlow, mitmproxy addon: maps flows to FlowRecords and supports interception. Two…, State for a single intercepted (paused) flow.

### Community 35 - "repeater_tab.py"
Cohesion: 0.16
Nodes (7): GroupDialog, QDialog, Dialog for adding Repeater request tabs to a named, colored group. Presents a…, Collect a group name, member tabs, and a color., Group, Repeater tab: a container of independent request/response sessions. Each "Send…, A named, colored, collapsible collection of member sessions.

### Community 36 - "QMenu"
Cohesion: 0.18
Nodes (5): QMenu, Install (or clear) the dropdown's group-send options. ``actions`` is a list of…, Record which send mode the split button runs, and show it on the button., Ask the provider for a payload and insert it at the cursor., Build a FlowRecord from the current (edited) request text.

### Community 37 - "WrappingTabBar"
Cohesion: 0.26
Nodes (5): QScrollArea, QSize, Group-aware, wrapping tab bar composed of chip widgets., Rebuild the whole bar from the container's model. Args: order: list of keys…, WrappingTabBar

### Community 38 - "start_proxy_repro.py"
Cohesion: 0.47
Nodes (4): after_start(), finish(), Reproduce the 'start proxy crashes' path using the real MainWindow. Builds the…, send()

### Community 39 - "SessionState"
Cohesion: 0.17
Nodes (6): Serializable snapshot of a session (for persistence)., SessionState, Path, Close every request tab and remove all groups., Write all open sessions and their groups to ``path`` as JSON., Recreate sessions and groups saved by :meth:`save_sessions`.

### Community 40 - "config.py"
Cohesion: 0.22
Nodes (7): finish(), poll_for_ca(), Verify the CA is generated in Bidoytu's confdir and can be exported. Starts the…, Verify starting the proxy on an occupied port produces a clean error signal…, _default_data_dir(), Application configuration and filesystem paths. Everything the app writes…, Return a per-user, per-OS data directory for Bidoytu.

### Community 42 - "intercept_response_live_test.py"
Cohesion: 0.31
Nodes (7): check_done(), do_forward(), finish(), on_intercepted(), on_started(), Live: intercept a request via the real MainWindow, forward it, and confirm the…, send()

### Community 44 - "ProcessingRuleDialog"
Cohesion: 0.40
Nodes (3): ProcessingRuleDialog, QDialog, Configure a single :class:`ProcessingRule`.

### Community 45 - "intercept_live_test.py"
Cohesion: 0.36
Nodes (6): finish(), on_captured(), on_intercepted(), on_started(), Live test: interception pauses a request, and forward/drop resolve it.…, send()

### Community 46 - "InteractionFilterProxy"
Cohesion: 0.33
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

### Community 52 - "current_mode"
Cohesion: 0.24
Nodes (6): A wrapping flow layout: children flow left-to-right and wrap to new rows. This…, current_mode(), Return the named color tokens for ``mode`` (falls back to dark)., Return the theme mode currently applied to the application., tokens(), A wrapping, group-aware tab bar built from individual chip widgets. Unlike…

### Community 53 - "CLAUDE.md"
Cohesion: 0.20
Nodes (8): Architecture and layering (respect this), Conventions, Git workflow, Gotchas learned the hard way, Tech stack, Verifying changes (always do this), What Bidoytu is, Where things live

### Community 54 - "._show_raw"
Cohesion: 0.50
Nodes (3): Render a raw HTTP message, pretty-printing its body by content-type. Splits…, Split a raw HTTP message into (start_line, headers, body). Tolerant of both…, _split_http_message()

### Community 55 - "Building and releasing Bidoytu"
Cohesion: 0.20
Nodes (9): Build (Windows or Linux), Building and releasing Bidoytu, Cutting version 1.0.0, How releases work (CI/CD), Local builds (optional), Notes, Nuitka (alternative compiler), Prerequisites (+1 more)

### Community 57 - "Interaction"
Cohesion: 0.15
Nodes (7): Interaction, _cb(), _now_iso(), A single out-of-band interaction reported by the server., Poll the server once. ``on_done(interactions, error)`` on sender thread., Best-effort correlate an interaction back to a generated payload., Restore a session saved by :meth:`save_state` and re-register it.

### Community 58 - "Security Policy"
Cohesion: 0.22
Nodes (8): Handling the CA certificate, Reporting a vulnerability, Responsible and lawful use, Safe defaults and data handling, Scope, Security Policy, Supported versions, What to expect

### Community 63 - "WorkspaceManager"
Cohesion: 0.07
Nodes (30): Path, QDialog, main(), Application entry point. Creates the Qt application, builds the main window,…, Give Windows an explicit AppUserModelID so the taskbar uses our icon. Without…, _set_windows_app_id(), Enables ``python -m bidoytu``., asset_path() (+22 more)

### Community 64 - "engine.py"
Cohesion: 0.33
Nodes (4): ProxyConfig, Listen settings for the mitmproxy engine., Runs mitmproxy inside a dedicated QThread. Design: - mitmproxy is asyncio-…, Proxy engine package (mitmproxy running inside a QThread).

### Community 65 - "Contributing to Bidoytu"
Cohesion: 0.25
Nodes (7): Branches and pull requests, Checks, Contributing to Bidoytu, Design rules, License, Local setup, Security issues

### Community 67 - "repeater_session.py"
Cohesion: 0.11
Nodes (18): absolute_url(), build_request_text(), build_response_text(), ensure_host_header(), _headers_have(), host_from_headers_or_url(), parse_request_text(), ParsedRequest (+10 more)

## Knowledge Gaps
- **39 isolated node(s):** `Architecture`, `Development workflow`, `Highlights`, `License`, `Packaging and releases` (+34 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 483 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **17 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `FlowRecord` connect `FlowRecord` to `InterceptView`, `MessageView`, `HistoryView`, `IntruderSession`, `InterceptActivityModel`, `intruder_session.py`, `RepeaterTab`, `ProxyEngine`, `CaptureAddon`, `FlowRepository`, `RepeaterSession`, `AsyncHttpSender`, `IntruderTab`, `content_type_from_headers`, `smoke_test.py`, `capture_addon.py`, `repeater_tab.py`, `QMenu`, `engine.py`, `repeater_session.py`?**
  _High betweenness centrality (0.290) - this node is a cross-community bridge._
- **Why does `MessageView` connect `MessageView` to `theme.py`, `InterceptView`, `repeater_session.py`, `CollaboratorTab`, `IntruderSession`, `intruder_session.py`, `body_format.py`, `collaborator_tab.py`, `RepeaterSession`, `._show_raw`, `FlowRecord`?**
  _High betweenness centrality (0.126) - this node is a cross-community bridge._
- **Why does `CollaboratorTab` connect `CollaboratorTab` to `MessageView`, `InteractshClient`, `Path`, `InteractionFilterProxy`, `MainWindow`, `collaborator_tab.py`, `._show_raw`, `AsyncHttpSender`, `InteractionsModel`, `Interaction`, `FindBar`?**
  _High betweenness centrality (0.113) - this node is a cross-community bridge._
- **Are the 16 inferred relationships involving `FlowRecord` (e.g. with `test_intercept_view()` and `test_qt_and_proxy_apis()`) actually correct?**
  _`FlowRecord` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `IntruderSession` (e.g. with `AsyncHttpSender` and `PayloadSet`) actually correct?**
  _`IntruderSession` has 15 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `RepeaterSession` (e.g. with `AsyncHttpSender` and `HttpResult`) actually correct?**
  _`RepeaterSession` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `CollaboratorTab` (e.g. with `CollaboratorConfig` and `AsyncHttpSender`) actually correct?**
  _`CollaboratorTab` has 10 INFERRED edges - model-reasoned connections that need verification._
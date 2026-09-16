"""Import + wiring smoke test (no live proxy, no visible window).

Verifies:
    - all modules import against the real PySide6 / mitmproxy APIs
    - the storage layer round-trips a FlowRecord (inline + file-backed body)
    - the table model accepts upserts
    - the main window constructs under an offscreen QApplication
"""
import os
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bidoytu.config import AppConfig, host_matches_scope
from bidoytu.storage.body_store import BodyStore
from bidoytu.storage.models import FlowRecord
from bidoytu.storage.repository import FlowRepository


def test_storage_roundtrip(tmp: Path) -> None:
    repo = FlowRepository(tmp / "t.db")
    rec = FlowRecord(
        flow_id="abc-123", method="GET", scheme="https", host="example.com",
        port=443, path="/", request_body_inline=b"hi", request_body_size=2,
        started_at=1.0,
    )
    rid = repo.insert(rec)
    assert rid == 1, rid
    rec.status_code = 200
    rec.completed_at = 2.0
    repo.update(rec)
    got = repo.get_by_flow_id("abc-123")
    assert got is not None and got.status_code == 200
    assert got.url == "https://example.com/"
    assert abs(got.duration_ms - 1000.0) < 1e-6
    assert repo.count() == 1
    repo.close()
    print("  storage roundtrip OK")


def test_body_store(tmp: Path) -> None:
    store = BodyStore(tmp / "bodies")
    data = b"x" * 1000
    p = store.store(data)
    assert store.exists(p)
    assert store.load(p) == data
    assert store.store(data) == p  # de-dup
    print("  body store OK")


def test_body_format() -> None:
    from bidoytu.ui.body_format import format_body, content_type_from_headers

    # JSON gets indented.
    out = format_body(b'{"a":1,"b":[2,3]}', "application/json")
    assert '"a": 1' in out and "\n" in out, out

    # JSON sniffed even without a content-type.
    out2 = format_body(b'[1,2,3]', "")
    assert out2.startswith("[") and "\n" in out2

    # Form data expands to key = value lines.
    out3 = format_body(b"x=1&y=hello+world", "application/x-www-form-urlencoded")
    assert "x = 1" in out3 and "y = hello world" in out3, out3

    # XML gets reindented.
    out4 = format_body(b"<a><b>1</b><c>2</c></a>", "application/xml")
    assert out4.count("\n") >= 2, out4

    # Binary is summarized, not garbled.
    out5 = format_body(b"\x00\x01\x02\x03PNG", "application/octet-stream")
    assert "bytes of binary data" in out5

    # Malformed JSON falls back to raw text (no exception).
    out6 = format_body(b'{not json', "application/json")
    assert out6 == "{not json"

    # Header extraction.
    assert content_type_from_headers("Host: x\r\nContent-Type: application/json; charset=utf-8") \
        == "application/json; charset=utf-8"
    print("  body_format OK")


def test_http_utils() -> None:
    from bidoytu.http_utils import parse_request_text, host_from_headers_or_url

    text = (
        "POST /submit?a=1 HTTP/1.1\r\n"
        "Host: example.com:8443\r\n"
        "Content-Type: application/json\r\n"
        "\r\n"
        '{"k": "v"}'
    )
    parsed = parse_request_text(text)
    assert parsed.method == "POST"
    assert parsed.path == "/submit?a=1"
    assert parsed.header("content-type") == "application/json"
    assert parsed.body == b'{"k": "v"}'
    scheme, host, port, path = host_from_headers_or_url(parsed, "fallback", "https", 443)
    assert (host, port) == ("example.com", 8443), (host, port)
    print("  http_utils parse OK")


def test_target_scope(tmp: Path) -> None:
    assert host_matches_scope("example.com", ["example.com"], [])
    assert host_matches_scope("api.example.com", ["*.example.com"], [])
    assert not host_matches_scope(
        "cdn.example.com", ["example.com"], ["cdn.example.com"]
    )
    assert host_matches_scope("other.test", [], [])

    cfg = AppConfig(data_dir=tmp / "scope")
    cfg.ensure_dirs()
    cfg.proxy.include_scope = ["example.com"]
    cfg.proxy.exclude_scope = ["cdn.example.com"]
    cfg.save_proxy_scope()
    restored = AppConfig(data_dir=tmp / "scope")
    restored.load_proxy_scope()
    assert restored.proxy.include_scope == ["example.com"]
    assert restored.proxy.exclude_scope == ["cdn.example.com"]
    print("  target scope matching + persistence OK")


def test_live_audit() -> None:
    from bidoytu.audit.catalog import VULNERABILITY_CATALOG
    from bidoytu.audit.service import LiveAuditService, Severity
    from bidoytu.audit.active_scan import ActiveScanWorker

    service = LiveAuditService()
    record = FlowRecord(
        flow_id="audit-1", method="GET", scheme="https", host="example.com",
        port=443, path="/account?token=secret", scope=True,
        request_headers="Host: example.com", status_code=500,
        response_headers=(
            "Server: Example/1.0\r\nSet-Cookie: session=abc\r\n"
            "Access-Control-Allow-Origin: *\r\n"
        ),
        response_body_inline=b"Traceback (most recent call last): boom",
    )
    # Disabled means no audit results.
    _, issues = service.analyze(record, is_response=False)
    assert not issues
    service.set_enabled(True)
    _, request_issues = service.analyze(record, is_response=False)
    assert any(issue.title == "Sensitive data in URL" for issue in request_issues)
    _, response_issues = service.analyze(record, is_response=True)
    assert any(issue.severity == Severity.MEDIUM for issue in response_issues)
    assert any(issue.title == "Cookie without Secure flag" for issue in response_issues)
    # Each flow/rule pair is emitted once even when the proxy updates the flow.
    _, repeated = service.analyze(record, is_response=True)
    assert not repeated

    catalog_record = FlowRecord(
        flow_id="catalog", method="POST", scheme="https", host="example.com",
        port=443, path="/fetch?url=http://127.0.0.1/../../etc/passwd",
        request_body_inline=b"<!DOCTYPE x [<!ENTITY e SYSTEM 'file:///etc/passwd'>]>",
        response_body_inline=b"root:x:0:0:root:/root:/bin/sh",
        response_headers="Content-Type: text/html",
        status_code=200, scope=True,
    )
    _, catalog_issues = service.analyze(catalog_record, is_response=True)
    catalog_titles = {issue.title for issue in catalog_issues}
    assert "Potential XML external entity injection" in catalog_titles
    assert "Potential directory traversal" in catalog_titles
    assert "Potential server-side request forgery" in catalog_titles
    assert "Sensitive local or cloud data disclosed" in catalog_titles

    # The first delivery batch is intentionally passive and evidence-backed:
    # a controlled fixture must exercise individually named detector rules
    # without transmitting a probe to a target.
    first_twenty = FlowRecord(
        flow_id="audit-first-twenty", method="PUT", scheme="https", host="example.com",
        port=443, path="/admin?url=http://callback.example", scope=True,
        request_headers="", status_code=200, response_headers="Allow: GET, PUT",
        request_body_inline=b"; whoami (|(cn=*)) </bad> <?php __import__('os') ${user}",
        response_body_inline=(b"/bin/sh: command not found LDAP Error XPathException "
                              b"XML parse error Server Error in '/' Application trace.axd"),
    )
    _, first_twenty_issues = service.analyze(first_twenty, is_response=True)
    first_twenty_titles = {issue.title for issue in first_twenty_issues}
    assert {
        "Potential OS command injection", "ASP.NET tracing enabled", "Potential LDAP injection",
        "Potential XPath injection", "Potential XML injection", "ASP.NET debugging enabled",
        "Broken access control review candidate", "HTTP PUT method is enabled",
        "Out-of-band resource load review candidate", "PHP code injection test input observed",
        "Python code injection test input observed", "Expression Language injection test input observed",
    } <= first_twenty_titles
    assert len(LiveAuditService.COVERAGE[:20]) == 20

    worker = ActiveScanWorker(lambda _result: None)
    worker.set_enabled(True)
    assert not worker.submit(catalog_record)
    assert worker.skipped_state_changing == 1
    worker.stop()
    assert len(VULNERABILITY_CATALOG) == 179
    assert VULNERABILITY_CATALOG[0].name == "OS command injection"
    assert VULNERABILITY_CATALOG[-1].name == "Hidden HTTP 2"
    print("  passive live audit checks OK")


def test_qt_and_proxy_apis(tmp: Path) -> None:
    from PySide6.QtWidgets import QApplication, QTabWidget
    from bidoytu.ui.flow_table_model import FlowTableModel
    from bidoytu.ui.main_window import MainWindow

    # mitmproxy API surface used by the engine.
    from mitmproxy.options import Options
    from mitmproxy.tools.dump import DumpMaster
    opts = Options(listen_host="127.0.0.1", listen_port=8080, http2=True)
    assert opts.listen_port == 8080

    app = QApplication.instance() or QApplication([])

    model = FlowTableModel()
    model.upsert_record(FlowRecord(flow_id="f1", method="GET", host="a.com", path="/"))
    model.upsert_record(FlowRecord(flow_id="f1", method="GET", host="a.com", path="/", status_code=200))
    assert model.rowCount() == 1
    model.upsert_record(FlowRecord(flow_id="f2", method="POST", host="b.com", path="/x"))
    assert model.rowCount() == 2

    cfg = AppConfig(data_dir=tmp / "app")
    win = MainWindow(cfg)
    assert win.windowTitle().startswith("Bidoytu")

    # Top-level tabs present in order.
    tabs: QTabWidget = win._tabs
    labels = [tabs.tabText(i) for i in range(tabs.count())]
    assert labels == ["Proxy", "Target", "Repeater", "Intruder", "Collaborator", "Live audit"], labels

    # Proxy sub-tabs.
    sub = win._proxy_tab.sub_tabs
    sub_labels = [sub.tabText(i) for i in range(sub.count())]
    assert sub_labels == ["HTTP History", "Intercept"], sub_labels
    assert win._proxy_tab.browser_btn.text() == "Open Browser..."
    assert win._config.browser_profiles_dir.exists()
    assert win._target_tab.tabs.tabText(0) == "Site map"
    assert win._target_tab.tabs.tabText(1) == "Scope"
    assert win._target_tab.tabs.currentWidget() is win._target_tab.scope_page
    assert [win._audit_tab._tabs.tabText(i) for i in range(win._audit_tab._tabs.count())] == [
        "Summary", "Audit items", "Issues", "Vulnerability catalog"
    ]

    # Soft wrap defaults on in the history detail views.
    assert win._proxy_tab.history._detail.request_view.soft_wrap_enabled()

    # Send-to actions move a record into the tool tabs.
    rec = FlowRecord(flow_id="f2", method="POST", scheme="https", host="b.com",
                     port=443, path="/x", request_headers="Host: b.com",
                     request_body_inline=b"payload")
    win._send_to_repeater(rec)
    assert tabs.currentWidget() is win._repeater_tab
    # Send-to opens a new session in the stacked content; check its target label.
    rep = win._repeater_tab
    assert rep._stack.count() == 1, rep._stack.count()
    session = rep._stack.currentWidget()
    assert "b.com" in session._target_label.text()

    win._send_to_intruder(rec)
    assert tabs.currentWidget() is win._intruder_tab

    # Intercept toggle callback is wired to the engine.
    assert win._proxy_tab.intercept.on_toggle_intercept is not None
    assert win._proxy_tab.intercept.on_forward is not None
    assert win._proxy_tab.intercept.on_drop is not None

    # Host/port inputs reflect config defaults.
    assert win._proxy_tab.host_edit.text() == cfg.proxy.listen_host
    assert win._proxy_tab.listen_port() == cfg.proxy.listen_port

    win._target_tab.scope_page.include._insert("example.com")
    assert cfg.proxy.include_scope == ["example.com"]

    # Live audit is opt-in and displays passive findings for captured in-scope
    # traffic without involving the async sender.
    win._audit_tab._toggle.setChecked(True)
    audit_flow = FlowRecord(
        flow_id="live-audit-flow", method="GET", scheme="https", host="example.com",
        port=443, path="/", status_code=200, scope=True,
        response_headers="Server: test", response_body_inline=b"ok",
    )
    win._on_flow_captured(audit_flow, is_response=True)
    assert win._audit_tab._items.rowCount() == 1
    assert win._audit_tab._issues.rowCount() > 0

    # Editing the inputs and starting applies them to the engine config.
    win._proxy_tab.host_edit.setText("0.0.0.0")
    win._proxy_tab.set_port(9999)
    # Call the start slot but stop the engine immediately so no real bind lingers.
    win._on_start()
    assert win._config.proxy.listen_host == "0.0.0.0"
    assert win._config.proxy.listen_port == 9999
    win._engine.stop()

    # Inputs lock while running and unlock when stopped.
    win._proxy_tab.set_running(True)
    assert not win._proxy_tab.host_edit.isEnabled()
    assert not win._proxy_tab.port_edit.isEnabled()
    win._proxy_tab.set_running(False)
    assert win._proxy_tab.host_edit.isEnabled()
    assert win._proxy_tab.port_edit.isEnabled()

    win.close()
    print("  qt + tabs + send-to + host/port wiring OK")


def test_intercept_view() -> None:
    from PySide6.QtWidgets import QApplication
    from bidoytu.ui.intercept_view import InterceptView

    app = QApplication.instance() or QApplication([])
    view = InterceptView()

    forwarded = {}
    view.on_forward = lambda fid, text: forwarded.update({"id": fid, "text": text})
    view.on_drop = lambda fid: forwarded.update({"dropped": fid})

    # A request is intercepted and shown.
    req = FlowRecord(flow_id="ix1", method="GET", scheme="https", host="ex.com",
                     port=443, path="/api", http_version="HTTP/1.1",
                     request_headers="Host: ex.com")
    view.enqueue(req)
    assert view._current is not None and view._current.flow_id == "ix1"

    # A response for a flow we did NOT forward is ignored.
    stray = FlowRecord(flow_id="other", status_code=200, http_version="HTTP/1.1",
                       reason="OK", response_headers="Content-Type: text/plain",
                       response_body_inline=b"nope", content_type="text/plain")
    view.on_response(stray)
    assert view._response_view.toPlainText() == ""

    # Forward the current request; then its response should display.
    view._on_forward_clicked()
    assert forwarded["id"] == "ix1"
    resp = FlowRecord(flow_id="ix1", status_code=200, http_version="HTTP/1.1",
                      reason="OK", response_headers="Content-Type: application/json",
                      response_body_inline=b'{"ok":true}', content_type="application/json")
    view.on_response(resp)
    shown = view._response_view.toPlainText()
    assert "200 OK" in shown and '"ok": true' in shown, shown  # note: pretty-printed

    # Send-to signals fire from the intercept panel.
    got = {}
    view.send_to_repeater.connect(lambda r: got.update({"rep": r}))
    view.send_to_intruder.connect(lambda r: got.update({"int": r}))
    # Re-load a current request so _current_as_record() has something to build.
    view.enqueue(FlowRecord(flow_id="ix2", method="POST", scheme="http",
                            host="h.com", port=80, path="/x",
                            request_headers="Host: h.com"))
    rec = view._current_as_record()
    assert rec is not None and rec.method == "POST" and rec.host == "h.com"
    view.send_to_repeater.emit(rec)
    view.send_to_intruder.emit(rec)
    assert got["rep"].flow_id == "ix2" and got["int"].flow_id == "ix2"
    print("  intercept view response + send-to OK")


def main() -> int:
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        test_storage_roundtrip(tmp)
        test_body_store(tmp)
        test_body_format()
        test_http_utils()
        test_target_scope(tmp)
        test_live_audit()
        test_qt_and_proxy_apis(tmp)
        test_intercept_view()
    print("ALL SMOKE TESTS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

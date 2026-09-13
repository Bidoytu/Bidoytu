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

from bidoytu.config import AppConfig
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
    assert labels == ["Proxy", "Repeater", "Intruder"], labels

    # Proxy sub-tabs.
    sub = win._proxy_tab.sub_tabs
    sub_labels = [sub.tabText(i) for i in range(sub.count())]
    assert sub_labels == ["HTTP History", "Intercept"], sub_labels

    # Soft wrap defaults on in the history detail views.
    assert win._proxy_tab.history._detail.request_view.soft_wrap_enabled()

    # Send-to actions move a record into the target tab and switch to it.
    rec = FlowRecord(flow_id="f2", method="POST", scheme="https", host="b.com",
                     port=443, path="/x", request_headers="Host: b.com",
                     request_body_inline=b"payload")
    win._send_to_repeater(rec)
    assert tabs.currentWidget() is win._repeater_tab
    assert "b.com" in win._repeater_tab._target_label.text()

    win._send_to_intruder(rec)
    assert tabs.currentWidget() is win._intruder_tab

    # Intercept toggle callback is wired to the engine.
    assert win._proxy_tab.intercept.on_toggle_intercept is not None
    assert win._proxy_tab.intercept.on_forward is not None
    assert win._proxy_tab.intercept.on_drop is not None

    # Host/port inputs reflect config defaults.
    assert win._proxy_tab.host_edit.text() == cfg.proxy.listen_host
    assert win._proxy_tab.listen_port() == cfg.proxy.listen_port

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
        test_qt_and_proxy_apis(tmp)
        test_intercept_view()
    print("ALL SMOKE TESTS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

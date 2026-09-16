"""Browser discovery and launch helpers for the local interception proxy."""
from __future__ import annotations

import os
import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import serialization


@dataclass(frozen=True, slots=True)
class BrowserInfo:
    name: str
    executable: Path
    kind: str  # ``firefox`` or ``chromium``


def install_ca_for_browser(browser: BrowserInfo, pem_cert: Path, der_cert: Path,
                           profile: Path) -> str:
    """Install the public CA for the selected browser and return the method used.

    Windows Chrome/Edge and Firefox can use the current-user Windows Root store.
    On Linux/macOS, browser-specific NSS databases are used when ``certutil`` is
    available. No browser is launched unless this succeeds.
    """
    pem_cert, der_cert, profile = Path(pem_cert), Path(der_cert), Path(profile)
    if not pem_cert.exists():
        raise OSError(f"CA certificate is not ready: {pem_cert}")
    if os.name == "nt":
        if not der_cert.exists():
            try:
                certificate = x509.load_pem_x509_certificate(pem_cert.read_bytes())
                der_cert.parent.mkdir(parents=True, exist_ok=True)
                der_cert.write_bytes(certificate.public_bytes(serialization.Encoding.DER))
            except (OSError, ValueError) as exc:
                raise OSError(
                    f"Windows CA certificate is not ready and could not be created from "
                    f"{pem_cert}: {exc}"
                ) from exc
        certutil = shutil.which("certutil.exe") or shutil.which("certutil")
        if not certutil:
            raise OSError("Windows certutil.exe was not found")
        cert_path = der_cert.resolve()
        result = subprocess.run(
            [certutil, "-user", "-f", "-addstore", "Root", os.fspath(cert_path)],
            capture_output=True, text=True,
        )
        if result.returncode:
            detail = (result.stderr or result.stdout).strip()
            if "already exists" in detail.casefold() or "already exist" in detail.casefold():
                return "Windows current-user Root store (already installed)"
            raise OSError(f"Could not install the CA in the Windows user trust store: {detail}")
        return "Windows current-user Root store"

    if not shutil.which("certutil"):
        raise OSError("NSS certutil is required to install the CA for this browser")
    profile.mkdir(parents=True, exist_ok=True)
    database = f"sql:{profile}"
    subprocess.run(["certutil", "-N", "-d", database, "--empty-password"],
                   check=False, capture_output=True, text=True)
    result = subprocess.run(
        ["certutil", "-A", "-n", "Bidoytu Proxy CA", "-t", "C,,", "-i",
         os.fspath(pem_cert), "-d", database],
        capture_output=True, text=True,
    )
    if result.returncode:
        detail = (result.stderr or result.stdout).strip()
        raise OSError(f"Could not install the CA in the browser profile: {detail}")
    return "browser profile NSS store"


def _existing(candidates: list[str | Path]) -> list[Path]:
    found: list[Path] = []
    seen: set[str] = set()
    for candidate in candidates:
        path = Path(candidate) if isinstance(candidate, Path) else shutil.which(candidate)
        if path is None:
            continue
        try:
            resolved = path.resolve()
        except OSError:
            resolved = path
        key = os.fspath(resolved).casefold()
        if key not in seen and resolved.is_file():
            seen.add(key)
            found.append(resolved)
    return found


def discover_browsers() -> list[BrowserInfo]:
    """Return common installed browsers, without touching the user's profile."""
    if os.name == "nt":
        roots = [Path(os.environ.get("PROGRAMFILES", "")),
                 Path(os.environ.get("PROGRAMFILES(X86)", "")),
                 Path(os.environ.get("LOCALAPPDATA", ""))]
        candidates = {
            "Firefox": (["firefox"], [r"Mozilla Firefox\firefox.exe"]),
            "Google Chrome": (["chrome"], [r"Google\Chrome\Application\chrome.exe"]),
            "Microsoft Edge": (["msedge"], [r"Microsoft\Edge\Application\msedge.exe"]),
            "Brave": (["brave"], [r"BraveSoftware\Brave-Browser\Application\brave.exe"]),
            "Opera": (["opera"], [r"Opera\launcher.exe"]),
            "Vivaldi": (["vivaldi"], [r"Vivaldi\Application\vivaldi.exe"]),
        }
        result: list[BrowserInfo] = []
        for name, (commands, suffixes) in candidates.items():
            paths = _existing(commands + [root / suffix for root in roots for suffix in suffixes])
            if paths:
                result.append(BrowserInfo(name, paths[0], "firefox" if name == "Firefox" else "chromium"))
        return result

    candidates = [
        ("Firefox", "firefox", "firefox"),
        ("Google Chrome", "google-chrome", "chromium"),
        ("Google Chrome", "google-chrome-stable", "chromium"),
        ("Chromium", "chromium", "chromium"),
        ("Microsoft Edge", "microsoft-edge", "chromium"),
        ("Microsoft Edge", "microsoft-edge-stable", "chromium"),
        ("Brave", "brave", "chromium"),
        ("Opera", "opera", "chromium"),
        ("Vivaldi", "vivaldi", "chromium"),
    ]
    result: list[BrowserInfo] = []
    seen_names: set[str] = set()
    for name, command, kind in candidates:
        paths = _existing([command])
        if paths and name not in seen_names:
            result.append(BrowserInfo(name, paths[0], kind))
            seen_names.add(name)
    return result


def _firefox_profile(profile: Path, host: str, port: int) -> None:
    profile.mkdir(parents=True, exist_ok=True)
    # Firefox has no proxy command-line switch; these prefs are equivalent to
    # the manual Network Settings configuration and apply only to this profile.
    prefs = (
        'user_pref("network.proxy.type", 1);\n'
        f'user_pref("network.proxy.http", {json.dumps(host)});\n'
        f'user_pref("network.proxy.http_port", {port});\n'
        f'user_pref("network.proxy.ssl", {json.dumps(host)});\n'
        f'user_pref("network.proxy.ssl_port", {port});\n'
        'user_pref("network.proxy.no_proxies_on", "");\n'
    )
    (profile / "user.js").write_text(prefs, encoding="utf-8")


def _chromium_profile(profile: Path) -> None:
    """Give the isolated Chromium profile a visible Bidoytu identity."""
    profile.mkdir(parents=True, exist_ok=True)
    preferences_path = profile / "Preferences"
    try:
        preferences = json.loads(preferences_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        preferences = {}
    profile_preferences = preferences.setdefault("profile", {})
    profile_preferences["name"] = "Bidoytu Browser"
    preferences_path.write_text(json.dumps(preferences, indent=2), encoding="utf-8")


def launch_browser(browser: BrowserInfo, host: str, port: int, profile_dir: Path,
                   pem_cert: Path, der_cert: Path) -> tuple[subprocess.Popen, str]:
    """Launch *browser* with a disposable Bidoytu profile and proxy settings."""
    profile_dir = Path(profile_dir)
    trust_method = install_ca_for_browser(browser, pem_cert, der_cert, profile_dir)
    if browser.kind == "firefox":
        _firefox_profile(profile_dir, host, port)
        if os.name == "nt":
            # Firefox normally has its own store; enable its supported bridge
            # to the current-user Windows roots for this isolated profile.
            with (profile_dir / "user.js").open("a", encoding="utf-8") as prefs:
                prefs.write('user_pref("security.enterprise_roots.enabled", true);\n')
        args = [os.fspath(browser.executable), "-no-remote", "-profile", os.fspath(profile_dir)]
    else:
        _chromium_profile(profile_dir)
        args = [
            os.fspath(browser.executable),
            f"--proxy-server=http://{host}:{port}",
            f"--user-data-dir={profile_dir}",
            "--no-first-run",
            "--no-default-browser-check",
        ]
    popen_kwargs = {"close_fds": (os.name != "nt"), "start_new_session": True}
    if os.name == "nt":
        popen_kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    return subprocess.Popen(args, **popen_kwargs), trust_method


def stop_browser(process: subprocess.Popen) -> None:
    """Close a browser process tree launched by Bidoytu."""
    if process.poll() is not None:
        return
    if os.name == "nt":
        subprocess.run(
            ["taskkill.exe", "/PID", str(process.pid), "/T", "/F"],
            capture_output=True, check=False,
        )
        return
    process.terminate()
    try:
        process.wait(timeout=3)
    except subprocess.TimeoutExpired:
        process.kill()

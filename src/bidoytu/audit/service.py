"""Evidence-backed passive checks for traffic captured by the proxy.

These checks never send a request, mutate traffic, or attempt exploitation.
They describe observable configuration weaknesses and possible exposure for a
user-authorized target; confirmation still belongs to a human tester.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum
from urllib.parse import urlsplit

from bidoytu.storage.models import FlowRecord


class Severity(StrEnum):
    INFORMATIONAL = "Informational"
    LOW = "Low"
    MEDIUM = "Medium"
    CRITICAL = "Critical"


@dataclass(slots=True, frozen=True)
class Evidence:
    """The exact captured string that caused a passive finding."""

    location: str  # ``request`` or ``response``
    text: str


@dataclass(slots=True)
class AuditIssue:
    """One passive finding tied to a captured proxy flow."""

    title: str
    severity: Severity
    confidence: str
    detail: str
    remediation: str
    record: FlowRecord
    evidence: tuple[Evidence, ...] = ()

    @property
    def url(self) -> str:
        return f"{self.record.scheme}://{self.record.host}{self.record.path}"


@dataclass(slots=True, frozen=True)
class AuditItem:
    """A traffic item observed by the enabled live audit."""

    flow_id: str
    method: str
    host: str
    path: str
    status: int | None


def _headers(text: str) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for line in text.splitlines():
        if ":" not in line:
            continue
        name, value = line.split(":", 1)
        result.setdefault(name.strip().lower(), []).append(value.strip())
    return result


def _issue(record: FlowRecord, title: str, severity: Severity, detail: str,
           remediation: str, *evidence: Evidence) -> AuditIssue:
    return AuditIssue(title, severity, "Certain", detail, remediation, record, evidence)


class LiveAuditService:
    """Runs a small, deterministic set of passive checks over proxy traffic."""

    COVERAGE = (
        "OS command injection", "SQL injection", "second-order SQL injection",
        "ASP.NET tracing", "file path traversal", "XXE", "LDAP injection",
        "XPath injection", "XML injection", "ASP.NET debugging",
        "broken access control review", "HTTP PUT", "out-of-band HTTP load",
        "file path manipulation", "PHP code injection", "server-side JavaScript injection",
        "Perl code injection", "Ruby code injection", "Python code injection",
        "Expression Language injection",
        "transport and security headers", "cookie attributes", "CORS policy",
        "cache controls", "technology disclosure", "sensitive URL parameters",
        "verbose errors", "directory listing", "password form autocomplete",
        "mixed-content references",
    )

    def __init__(self) -> None:
        self.enabled = False
        self._seen: set[tuple[str, str]] = set()

    def set_enabled(self, enabled: bool) -> None:
        self.enabled = enabled
        if enabled:
            self._seen.clear()

    def analyze(self, record: FlowRecord, is_response: bool) -> tuple[AuditItem, list[AuditIssue]]:
        """Return findings for one captured event, without side effects."""
        if not self.enabled or not record.scope:
            return AuditItem(record.flow_id, record.method, record.host, record.path, record.status_code), []
        item = AuditItem(record.flow_id, record.method, record.host, record.path, record.status_code)
        issues = self._request_checks(record) if not is_response else self._response_checks(record)
        unique: list[AuditIssue] = []
        for issue in issues:
            key = (record.flow_id, issue.title)
            if key not in self._seen:
                self._seen.add(key)
                unique.append(issue)
        return item, unique

    def _request_checks(self, record: FlowRecord) -> list[AuditIssue]:
        query = urlsplit(record.path).query
        if not query:
            return []
        names = {part.split("=", 1)[0].lower() for part in query.split("&") if part}
        sensitive = sorted(names & {"token", "access_token", "api_key", "apikey", "password", "passwd", "secret", "session"})
        if not sensitive:
            return []
        return [_issue(
            record, "Sensitive data in URL", Severity.MEDIUM,
            "The request URL contains a parameter commonly used for credentials or session data. URLs can be retained in browser history, logs, and referrer headers.",
            "Send credentials and tokens in an Authorization header or request body, then expire any value that has been exposed.",
            Evidence("request", "&".join(f"{name}=" for name in sensitive)),
        )]

    def _response_checks(self, record: FlowRecord) -> list[AuditIssue]:
        if record.status_code is None:
            return []
        headers = _headers(record.response_headers)
        body = (record.response_body_inline or b"").decode("utf-8", errors="replace")
        issues: list[AuditIssue] = []
        is_https = record.scheme.lower() == "https"

        # The six primary Burp catalog classes are included as explicit
        # indicator checks below. These are deliberately worded as potential
        # indicators: proving them normally requires controlled active tests.
        issues.extend(self._catalog_indicators(record, body))

        if is_https and "strict-transport-security" not in headers:
            issues.append(_issue(record, "Missing HTTP Strict Transport Security", Severity.LOW,
                "The HTTPS response does not set Strict-Transport-Security, so a browser may be downgraded before it first learns to require HTTPS.",
                "Set Strict-Transport-Security with an appropriate max-age after confirming all subdomains support HTTPS."))
        if "x-content-type-options" not in headers:
            issues.append(_issue(record, "Missing X-Content-Type-Options", Severity.LOW,
                "The response does not set X-Content-Type-Options: nosniff.",
                "Set X-Content-Type-Options: nosniff on applicable responses."))
        if "referrer-policy" not in headers:
            issues.append(_issue(record, "Missing Referrer-Policy", Severity.INFORMATIONAL,
                "The response does not define a Referrer-Policy.",
                "Set a policy such as strict-origin-when-cross-origin after validating application needs."))
        if "permissions-policy" not in headers:
            issues.append(_issue(record, "Missing Permissions-Policy", Severity.INFORMATIONAL,
                "The response does not restrict browser features through Permissions-Policy.",
                "Define a least-privilege Permissions-Policy for browser capabilities the application does not need."))

        csp = "; ".join(headers.get("content-security-policy", []))
        if not csp:
            issues.append(_issue(record, "Missing Content Security Policy", Severity.LOW,
                "The response does not provide a Content-Security-Policy.",
                "Deploy a restrictive Content-Security-Policy and validate it in report-only mode first."))
        else:
            lowered = csp.lower()
            if "'unsafe-inline'" in lowered or "'unsafe-eval'" in lowered or "*" in lowered:
                bad = "'unsafe-inline'" if "'unsafe-inline'" in lowered else ("'unsafe-eval'" if "'unsafe-eval'" in lowered else "*")
                issues.append(_issue(record, "Weak Content Security Policy", Severity.MEDIUM,
                    "The Content-Security-Policy permits an unsafe script/style source, weakening protection against injected content.",
                    "Replace unsafe sources and wildcards with nonces, hashes, or narrowly scoped origins.", Evidence("response", bad)))
            if "object-src" not in lowered:
                issues.append(_issue(record, "Content Security Policy lacks object-src", Severity.INFORMATIONAL,
                    "The Content-Security-Policy does not explicitly restrict plugin content with object-src.",
                    "Add object-src 'none' unless plugin content is required."))

        frame = "; ".join(headers.get("x-frame-options", []))
        if "frame-ancestors" not in csp.lower() and not frame:
            issues.append(_issue(record, "Missing clickjacking protection", Severity.LOW,
                "Neither CSP frame-ancestors nor X-Frame-Options is present on this response.",
                "Use CSP frame-ancestors to allow only approved embedding origins."))

        for cookie in headers.get("set-cookie", []):
            lower_cookie = cookie.lower()
            name = cookie.split("=", 1)[0].strip() or "cookie"
            if is_https and "secure" not in lower_cookie:
                issues.append(_issue(record, "Cookie without Secure flag", Severity.MEDIUM,
                    f"Cookie '{name}' is set over HTTPS without the Secure attribute.",
                    "Set Secure on cookies that must only travel over HTTPS.", Evidence("response", name)))
            if "httponly" not in lower_cookie:
                issues.append(_issue(record, "Cookie without HttpOnly flag", Severity.LOW,
                    f"Cookie '{name}' is accessible to client-side script because it lacks HttpOnly.",
                    "Set HttpOnly on session and other cookies that do not require JavaScript access.", Evidence("response", name)))
            if "samesite" not in lower_cookie:
                issues.append(_issue(record, "Cookie without SameSite attribute", Severity.LOW,
                    f"Cookie '{name}' has no SameSite attribute.",
                    "Set SameSite=Lax or SameSite=Strict where compatible, and use Secure with SameSite=None.", Evidence("response", name)))

        acao = ", ".join(headers.get("access-control-allow-origin", []))
        acac = ", ".join(headers.get("access-control-allow-credentials", [])).lower()
        origin = ", ".join(headers.get("vary", [])).lower()
        if acao == "*" and "true" in acac:
            issues.append(_issue(record, "Overly permissive CORS with credentials", Severity.CRITICAL,
                "The response combines Access-Control-Allow-Origin: * with credentialed CORS. Browser behavior varies, but this is an unsafe policy configuration that requires immediate review.",
                "Allow only trusted origins and avoid credentialed cross-origin access unless explicitly required.", Evidence("response", "Access-Control-Allow-Origin: *")))
        elif acao == "*":
            issues.append(_issue(record, "Overly permissive CORS policy", Severity.MEDIUM,
                "The response allows every origin with Access-Control-Allow-Origin: *.",
                "Restrict Access-Control-Allow-Origin to the minimum approved origins.", Evidence("response", "Access-Control-Allow-Origin: *")))
        elif acao and "origin" not in origin:
            issues.append(_issue(record, "CORS response may be cacheable across origins", Severity.LOW,
                "A specific Access-Control-Allow-Origin value is present but Vary: Origin was not observed.",
                "Add Vary: Origin whenever the allowed origin is selected dynamically.", Evidence("response", acao)))

        cache_control = ", ".join(headers.get("cache-control", [])).lower()
        if headers.get("set-cookie") and not any(value in cache_control for value in ("no-store", "private")):
            issues.append(_issue(record, "Potentially cacheable authenticated response", Severity.LOW,
                "The response sets a cookie but no Cache-Control: private or no-store directive was observed.",
                "Use no-store for sensitive responses, or private when browser caching is acceptable.", Evidence("response", "Set-Cookie")))

        for header in ("server", "x-powered-by", "x-aspnet-version"):
            if header in headers:
                issues.append(_issue(record, "Technology version disclosure", Severity.INFORMATIONAL,
                    f"The response discloses technology information through the {header} header.",
                    "Remove unnecessary implementation and version headers at the application or reverse-proxy layer.", Evidence("response", header)))

        error_match = re.search(r"(?:traceback \(most recent call last\)|stack trace|exception in thread|\bat \S+\([^)]*:\d+\))", body, re.IGNORECASE)
        if error_match:
            issues.append(_issue(record, "Verbose error message disclosed", Severity.MEDIUM,
                "The response body appears to contain a stack trace or exception detail.",
                "Return a generic error page to clients and retain diagnostic detail only in protected server logs.", Evidence("response", error_match.group(0))))
        if re.search(r"<title>\s*index of /|<h1>\s*index of /", body, re.IGNORECASE):
            issues.append(_issue(record, "Directory listing exposed", Severity.MEDIUM,
                "The response body matches a web-server directory listing page.",
                "Disable directory listing and expose only explicitly intended files.", Evidence("response", "Index of /")))
        if is_https and re.search(r"(?:src|href)=[\"']http://", body, re.IGNORECASE):
            issues.append(_issue(record, "Mixed content reference", Severity.LOW,
                "An HTTPS response references at least one resource using HTTP.",
                "Serve every subresource over HTTPS and use relative or HTTPS URLs.", Evidence("response", "http://")))
        if re.search(r"<input[^>]+type=[\"']password[\"'][^>]*>", body, re.IGNORECASE) and "autocomplete=\"off\"" not in body.lower():
            issues.append(_issue(record, "Password form permits browser autocomplete", Severity.INFORMATIONAL,
                "A password input was observed without an explicit autocomplete policy. This is a review item, not a finding that autocomplete must be disabled.",
                "Use appropriate autocomplete tokens such as current-password or new-password; do not disable password managers without a clear risk reason.", Evidence("response", "type=\"password\"")))
        return issues

    @staticmethod
    def _catalog_indicators(record: FlowRecord, body: str) -> list[AuditIssue]:
        """Detect non-destructive, evidence-backed indicators in captured traffic."""
        issues: list[AuditIssue] = []
        path_lower = record.path.lower()
        request = (record.request_body_inline or b"").decode("utf-8", errors="replace")
        combined = f"{record.path}\n{request}".lower()

        # The first 20 entries in the supplied Burp list have dedicated live
        # rules. They inspect traffic already observed by the proxy; none sends
        # a payload or performs an exploit attempt.
        issues.extend(LiveAuditService._first_twenty_indicators(record, body, request, combined))

        xss_input = re.search(r"(?:<script\b|javascript:|on(?:error|load)\s*=|%3cscript|%3e)", combined, re.IGNORECASE)
        if xss_input and xss_input.group(0).lower() in body.lower():
            issues.append(_issue(record, "Potential reflected cross-site scripting", Severity.MEDIUM,
                "A script-like value from the captured request appears in the response without an observed transformation.",
                "Confirm the output context and ensure untrusted data is contextually encoded. Use a controlled test value before treating this as exploitable.", Evidence("response", xss_input.group(0))))

        sql_error = re.search(r"(?:sql syntax.*mysql|mysql_fetch|postgresql.*error|ora-\d{4,5}|sqlite exception|odbc sql|unclosed quotation mark|sqlstate\[)", body, re.IGNORECASE)
        sql_input = re.search(r"(?:%27|'\s*(?:or|and)\s+\d|\bunion\s+(?:all\s+)?select\b|\bsleep\s*\(|\bwaitfor\s+delay\b)", combined, re.IGNORECASE)
        if sql_error:
            issues.append(_issue(record, "Potential SQL injection error disclosure", Severity.MEDIUM,
                "The response contains a database error signature. This can indicate unsafe input handling, but the captured error alone does not prove injection.",
                "Use parameterized queries and return generic client-facing errors. Confirm with a controlled comparison test.", Evidence("response", sql_error.group(0))))
        elif sql_input:
            issues.append(_issue(record, "SQL injection test input observed", Severity.INFORMATIONAL,
                "The captured request contains SQL-like syntax. This is recorded as an audit item for active verification, not as a confirmed vulnerability.",
                "Review the parameter handling and verify with a controlled, authorized test.", Evidence("request", sql_input.group(0))))

        if record.method.upper() not in {"GET", "HEAD", "OPTIONS", "TRACE"} and re.search(r"<form\b", body, re.IGNORECASE):
            if not re.search(r"csrf|xsrf|authenticity|requesttoken|__requestverificationtoken", body, re.IGNORECASE):
                issues.append(_issue(record, "Potential cross-site request forgery", Severity.LOW,
                    "A state-changing request returned an HTML form without an observable CSRF-token field.",
                    "Require a server-validated anti-CSRF token and appropriate SameSite cookie settings on state-changing actions.", Evidence("response", "<form")))

        xxe = re.search(r"<!doctype\s+[^>]*\[?[^>]*<!entity\b|<!entity\s+\w+\s+system", request, re.IGNORECASE)
        if xxe:
            issues.append(_issue(record, "Potential XML external entity injection", Severity.MEDIUM,
                "The captured XML request declares an external entity. XML parsers should not resolve untrusted external entities.",
                "Disable DTDs and external entity resolution in the XML parser, then validate with a controlled test.", Evidence("request", xxe.group(0))))
        if re.search(r"(?:root:x:0:0:|\[boot loader\]|/etc/passwd|169\.254\.169\.254/latest/meta-data)", body, re.IGNORECASE):
            issues.append(_issue(record, "Sensitive local or cloud data disclosed", Severity.CRITICAL,
                "The response contains a strong signature of local system or cloud-instance metadata. Review immediately as possible impact is high.",
                "Remove the data exposure, restrict server-side file and metadata access, and rotate any exposed credentials.", Evidence("response", re.search(r"(?:root:x:0:0:|\[boot loader\]|/etc/passwd|169\.254\.169\.254/latest/meta-data)", body, re.IGNORECASE).group(0))))

        traversal = re.search(r"(?:\.\./|%2e%2e|%252e%252e)", path_lower)
        if traversal:
            issues.append(_issue(record, "Potential directory traversal", Severity.MEDIUM,
                "The captured URL contains a parent-directory traversal sequence.",
                "Canonicalize and constrain file paths on the server. Treat this as a verification candidate unless sensitive file content is also observed.", Evidence("request", traversal.group(0))))

        ssrf = re.search(r"(?:https?://(?:localhost|127\.0\.0\.1|0\.0\.0\.0|169\.254\.169\.254)|https?%3a%2f%2f(?:localhost|127\.0\.0\.1))", combined, re.IGNORECASE)
        if ssrf:
            issues.append(_issue(record, "Potential server-side request forgery", Severity.MEDIUM,
                "A captured URL parameter or request body points at a loopback or cloud-metadata address.",
                "Allowlist outbound destinations, block private and link-local ranges, and validate URLs after canonicalization. Confirm only with an authorized controlled test.", Evidence("request", ssrf.group(0))))
        return issues

    @staticmethod
    def _first_twenty_indicators(record: FlowRecord, body: str, request: str,
                                 combined: str) -> list[AuditIssue]:
        """First delivery of individually named Burp-list detector rules.

        A match is a review candidate unless the response itself contains a
        strong error/disclosure signature. This prevents request text alone
        from being misreported as a confirmed server-side vulnerability.
        """
        issues: list[AuditIssue] = []

        def add(title: str, detail: str, remediation: str, evidence: Evidence,
                severity: Severity = Severity.MEDIUM) -> None:
            issues.append(_issue(record, title, severity, detail, remediation, evidence))

        command = re.search(r"(?:;|&&|\|\||\|)\s*(?:id|whoami|uname|cat|type|dir|ping)\b|`[^`]+`|\$\([^)]{1,120}\)", request, re.IGNORECASE)
        shell_error = re.search(r"(?:/bin/(?:sh|bash):|cmd\.exe|command not found|uid=\d+\([^)]*\))", body, re.IGNORECASE)
        if shell_error:
            add("Potential OS command injection", "The response contains a shell execution or command-output signature.", "Avoid shell invocation for user input; use fixed command APIs and strict allowlists.", Evidence("response", shell_error.group(0)), Severity.CRITICAL)
        elif command:
            add("OS command injection test input observed", "Captured request data contains shell-control syntax. Review the server-side handling before treating it as exploitable.", "Never concatenate untrusted input into shell commands; validate expected values and use argument arrays.", Evidence("request", command.group(0)))

        # SQL injection, XXE, and traversal are covered by the dedicated rules
        # below in this method's caller so their existing detailed evidence is
        # retained. Second-order SQLi needs a stored value and a later sink;
        # record an explicit candidate only for state-changing SQL-like input.
        second_order = re.search(r"(?:%27|'\s*(?:or|and)\s+\d|\bunion\s+(?:all\s+)?select\b)", request, re.IGNORECASE)
        if record.method.upper() not in {"GET", "HEAD", "OPTIONS"} and second_order:
            add("Second-order SQL injection review candidate", "A state-changing request contains SQL-like syntax. Confirm only by safely correlating stored data with a later server-side query.", "Use parameterized queries at every database sink, including background and later processing paths.", Evidence("request", second_order.group(0)), Severity.INFORMATIONAL)

        trace = re.search(r"(?:trace\.axd|application trace|trace information)", body, re.IGNORECASE)
        if trace:
            add("ASP.NET tracing enabled", "The response exposes an ASP.NET trace viewer signature.", "Disable public tracing and restrict diagnostic endpoints to authorized administrators.", Evidence("response", trace.group(0)), Severity.CRITICAL)

        ldap_error = re.search(r"(?:ldap(?:exception| error)|javax\.naming|invalid dn syntax)", body, re.IGNORECASE)
        ldap_input = re.search(r"(?:\(\||\(&|\)\(|\*\)\(|\)\s*\(cn=)", request, re.IGNORECASE)
        if ldap_error:
            add("Potential LDAP injection", "The response contains an LDAP error signature.", "Escape LDAP filter and distinguished-name values with a library API; do not concatenate filters.", Evidence("response", ldap_error.group(0)))
        elif ldap_input:
            add("LDAP injection test input observed", "The captured request contains LDAP-filter control syntax.", "Escape LDAP filter values and verify with a controlled authorized test.", Evidence("request", ldap_input.group(0)), Severity.INFORMATIONAL)

        xpath_error = re.search(r"(?:xpath(?:exception| expression)|system\.xml\.xpath|invalid predicate)", body, re.IGNORECASE)
        xpath_input = re.search(r"['\"]\s*(?:or|and)\s+['\"]?\d|\]\s*\|\s*//", request, re.IGNORECASE)
        if xpath_error:
            add("Potential XPath injection", "The response contains an XPath parsing or evaluation error signature.", "Use parameterized XPath APIs where available, or safely escape values before evaluating expressions.", Evidence("response", xpath_error.group(0)))
        elif xpath_input:
            add("XPath injection test input observed", "The captured request contains XPath-like predicate syntax.", "Treat input as data, not expression syntax; verify only in an approved test flow.", Evidence("request", xpath_input.group(0)), Severity.INFORMATIONAL)

        xml_error = re.search(r"(?:xml parse error|unexpected end tag|mismatched tag|saxparseexception)", body, re.IGNORECASE)
        xml_input = re.search(r"(?:</?[A-Za-z][^>]{0,80}>|<!\[cdata\[)", request, re.IGNORECASE)
        if xml_error and xml_input:
            add("Potential XML injection", "XML-looking request input coincides with an XML parser error in the response.", "Parse structured XML safely and escape or validate untrusted content before embedding it in XML.", Evidence("response", xml_error.group(0)))

        asp_debug = re.search(r"(?:server error in ['\"]/['\"] application|compilation error|customerrors mode=\"off\")", body, re.IGNORECASE)
        if asp_debug:
            add("ASP.NET debugging enabled", "The response exposes an ASP.NET detailed-error signature.", "Disable debug and detailed custom errors in production; retain diagnostic detail only in protected logs.", Evidence("response", asp_debug.group(0)))

        unauth_admin = (not re.search(r"^(?:authorization|cookie):", record.request_headers, re.IGNORECASE)
                        and record.status_code and 200 <= record.status_code < 300
                        and re.search(r"/(?:admin|administrator|manage|users?/\d+)", record.path, re.IGNORECASE))
        if unauth_admin:
            add("Broken access control review candidate", "An apparently privileged path returned success without an observable Authorization or Cookie header. Authentication may be handled elsewhere, so this needs manual confirmation.", "Enforce server-side authorization for every object and action; test with multiple roles and identifiers.", Evidence("request", record.path), Severity.INFORMATIONAL)

        allow = record.response_headers
        put_enabled = record.method.upper() == "PUT" and record.status_code and record.status_code < 400
        allow_put = re.search(r"^allow:\s*.*\bput\b", allow, re.IGNORECASE | re.MULTILINE)
        if put_enabled or allow_put:
            evidence = Evidence("response", allow_put.group(0) if allow_put else "PUT request accepted")
            add("HTTP PUT method is enabled", "The server advertises or accepted HTTP PUT. This is a review item; exposure depends on authentication and writable paths.", "Disable PUT where unnecessary and require strong authorization plus safe upload handling where it is required.", evidence, Severity.CRITICAL)

        oob_input = re.search(r"(?:https?://[^\s'\"<>]{1,200}|//[^\s'\"<>]{1,200})", combined, re.IGNORECASE)
        if oob_input and re.search(r"(?:url|uri|webhook|callback|fetch|image|avatar|import|feed)", record.path + "\n" + request, re.IGNORECASE):
            add("Out-of-band resource load review candidate", "A URL-bearing input was observed in a likely server-fetching context. Confirmation requires a controlled callback endpoint.", "Allowlist outbound destinations, isolate egress, and validate resolved IP addresses after redirects.", Evidence("request", oob_input.group(0)), Severity.INFORMATIONAL)

        file_path = re.search(r"(?:[A-Za-z]:\\\\|/(?:etc|var|home|tmp|proc)/|\\\\\\\\[^\\\s]+\\)", combined)
        if file_path:
            add("File path manipulation test input observed", "The captured request contains an absolute filesystem or network path.", "Use opaque resource identifiers and constrain canonicalized paths below a trusted root.", Evidence("request", file_path.group(0)), Severity.INFORMATIONAL)

        code_rules = (
            ("PHP code injection", r"(?:<\?php|\beval\s*\(|\bsystem\s*\()", r"(?:php (?:parse|fatal) error|unexpected t_)"),
            ("Server-side JavaScript code injection", r"(?:\brequire\s*\(|\bprocess\.(?:mainModule|env)|\bchild_process\b)", r"(?:node(?:\.js)? (?:error|exception)|referenceerror:)"),
            ("Perl code injection", r"(?:\bperl\b|\$ENV\{|\buse\s+strict\b)", r"(?:perl(?:\.exe)?:|can'?t locate .*\.pm)"),
            ("Ruby code injection", r"(?:\bKernel\.(?:system|eval)|\bProcess\.spawn|`[^`]+`)", r"(?:ruby(?: error| exception)|syntaxerror:.*\.rb)"),
            ("Python code injection", r"(?:__import__\s*\(|\bexec\s*\(|\beval\s*\(|\bos\.system\s*\()", r"(?:traceback \(most recent call last\)|python (?:error|exception)|syntaxerror:.*\.py)"),
            ("Expression Language injection", r"(?:\$\{[^}]{1,120}\}|#\{[^}]{1,120}\})", r"(?:javax\.el|expression language|spel evaluation)"),
        )
        for title, input_pattern, error_pattern in code_rules:
            error = re.search(error_pattern, body, re.IGNORECASE)
            candidate = re.search(input_pattern, request, re.IGNORECASE)
            if error:
                add(f"Potential {title.lower()}", "The response contains a runtime error signature associated with this server-side execution environment.", "Do not evaluate user-controlled expressions or code; use fixed APIs and strict allowlists.", Evidence("response", error.group(0)), Severity.CRITICAL)
            elif candidate:
                add(f"{title} test input observed", "The captured request contains syntax associated with this execution environment. It is a review candidate, not proof of execution.", "Treat user input only as data and verify the affected sink in an approved test flow.", Evidence("request", candidate.group(0)), Severity.INFORMATIONAL)
        return issues

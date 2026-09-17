"""Local advisory catalog for the vulnerability classes in Burp's list.

The entries are concise, original summaries with links to PortSwigger's
authoritative Web Security Academy pages. Detection status describes what
Bidoytu can currently observe; it is intentionally not presented as parity
with a commercial active scanner.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class VulnerabilityAdvisory:
    name: str
    severity: str
    scanner_id: str
    aliases: str
    summary: str
    impact: str
    detection: str
    prevention: str
    bidoytu_coverage: str
    url: str


DETAILED_ADVISORIES = (
    VulnerabilityAdvisory(
        "Cross-site scripting (XSS)", "High", "0x00200300", "Reflected · Stored · DOM-based",
        "Untrusted data reaches a browser and is interpreted as active content, allowing attacker-controlled script to run in a user's security context.",
        "Depending on the victim and application, XSS can enable account impersonation, data access, credential capture, unauthorized actions, or application defacement.",
        "Test every input and output context. Reflection alone is not proof: the returned value must be interpreted as executable content. Stored and DOM-based variants require observing later responses or browser-side sinks.",
        "Validate input where appropriate, contextually encode output, use safe templating, and deploy a restrictive CSP as defense in depth.",
        "Passive: script-like reflection and CSP weaknesses. Active: unique safe reflection marker on GET/HEAD/OPTIONS. Browser-powered DOM verification is not yet enabled.",
        "https://portswigger.net/web-security/cross-site-scripting",
    ),
    VulnerabilityAdvisory(
        "SQL injection", "High", "0x00100200", "SQLi · Blind · Error-based · UNION",
        "Attacker-controlled input changes a database query's structure or logic instead of being treated solely as data.",
        "It may expose, alter, or delete records and in some cases lead to deeper server compromise or denial of service.",
        "Compare baseline and controlled responses using syntax errors, boolean conditions, timing, or out-of-band checks. The vulnerable input can occur in many query clauses, not only a WHERE value.",
        "Use parameterized queries or safe query builders, constrain dynamic identifiers, validate expected types, and avoid returning database errors to clients.",
        "Passive: database error signatures and SQL-like input. Active: one diagnostic quote on safe-method query parameters; no destructive, timing, or OAST probes.",
        "https://portswigger.net/web-security/sql-injection",
    ),
    VulnerabilityAdvisory(
        "Cross-site request forgery (CSRF)", "Medium", "0x00200700", "XSRF",
        "A victim's browser is induced to send an unwanted state-changing request while it automatically supplies its authentication context.",
        "An attacker may change account data, perform transactions, or invoke other actions available to the victim.",
        "Review state-changing requests and test whether an untrusted origin can submit them without a server-validated token or equivalent control. Check cookie SameSite behavior and origin validation.",
        "Use unpredictable server-validated CSRF tokens, suitable SameSite cookies, and Origin/Referer validation as additional defense where appropriate.",
        "Passive: state-changing HTML forms without an observable anti-CSRF token and missing cookie SameSite attributes. Active confirmation is not performed.",
        "https://portswigger.net/web-security/csrf",
    ),
    VulnerabilityAdvisory(
        "XML external entity injection (XXE)", "High", "0x00100400", "External entity resolution · XML parser abuse",
        "An XML parser processes attacker-controlled external entities or DTDs, causing the server to read local resources or make outbound requests.",
        "Impact can include local file disclosure, server-side request forgery, denial of service, or access to internal systems.",
        "Inspect XML inputs and parser behavior. A declared entity is a risk indicator; confirmation requires a controlled request and response comparison appropriate to the target.",
        "Disable DTDs and external entity resolution, use hardened parser settings, validate XML structure, and apply least privilege to the parsing process.",
        "Passive: external-entity declarations in captured XML and local/cloud data signatures in responses. No automatic XXE payload is sent.",
        "https://portswigger.net/web-security/xxe",
    ),
    VulnerabilityAdvisory(
        "Directory traversal", "High", "0x00100300", "Path traversal · File path traversal",
        "User-controlled path data escapes the intended directory and addresses files elsewhere on the server's filesystem.",
        "An attacker may read sensitive configuration, source code, credentials, or operating-system files; impact depends on process permissions.",
        "Test path-bearing inputs with canonicalization-aware traversal variants and compare responses for accessible files. URL encoding and platform-specific separators matter.",
        "Canonicalize before authorization, use an allowlist of resource identifiers, constrain resolved paths beneath a trusted root, and avoid passing raw paths to filesystem APIs.",
        "Passive: traversal sequences and sensitive-file signatures. Active confirmation is not performed automatically.",
        "https://portswigger.net/web-security/file-path-traversal",
    ),
    VulnerabilityAdvisory(
        "Server-side request forgery (SSRF)", "High", "0x00100a00", "SSRF · Blind SSRF",
        "The server fetches a URL or network resource influenced by a user, allowing requests to destinations the attacker cannot reach directly.",
        "SSRF can expose cloud metadata, internal services, administrative interfaces, or credentials, and may pivot into further compromise.",
        "Identify URL-fetching inputs and verify destination controls with an approved internal test endpoint or OAST collaborator. Redirects, DNS rebinding, IPv6, and alternate IP encodings require review.",
        "Use strict destination allowlists, resolve and validate addresses, block private/link-local ranges after canonicalization, restrict redirects, and isolate outbound network access.",
        "Passive: loopback/private/cloud-metadata targets and metadata signatures. Active confirmation is not performed to avoid unintended server-side network requests.",
        "https://portswigger.net/web-security/ssrf",
    ),
)


def _catalog_entry(name: str, severity: str, scanner_id: str) -> VulnerabilityAdvisory:
    """Create an honest catalog record when a tailored advisory is unavailable.

    This catalog is an index of the September 2026 Burp issue list, not a claim
    that every proprietary Burp check or exploit workflow has been reproduced.
    """
    return VulnerabilityAdvisory(
        name, severity, scanner_id, "Burp Scanner issue definition",
        "This issue class is listed by Burp Scanner. Its impact depends on the affected endpoint, authentication context, and evidence captured during verification.",
        "Use the official advisory for the vulnerability definition, affected contexts, and safe verification approach.",
        "Review the affected input, response, and configuration; apply the control recommended by the official advisory for this issue class.",
        "Apply the least-privilege configuration, input validation, output encoding, and patching controls relevant to the affected component.",
        "Catalogued for discovery and triage. Live detection is shown separately in the coverage field; an entry is not a claim of scanner parity.",
        "https://portswigger.net/burp/documentation/scanner/vulnerabilities-list",
    )


def _build_catalog(raw_issues: str) -> tuple[VulnerabilityAdvisory, ...]:
    detailed = {entry.name.casefold(): entry for entry in DETAILED_ADVISORIES}
    catalog: list[VulnerabilityAdvisory] = []
    for line in raw_issues.splitlines():
        if not line:
            continue
        name, severity, scanner_id = line.split("\t")
        # Keep the tailored advisories for headline classes; aliases cover the
        # nomenclature used in the upstream table.
        key = name.casefold()
        alias = {
            "cross-site scripting (reflected)": "cross-site scripting (xss)",
            "file path traversal": "directory traversal",
        }.get(key, key)
        catalog.append(detailed.get(alias, _catalog_entry(name, severity, scanner_id)))
    return tuple(catalog)


# Source: the Burp Scanner issue list supplied with this project, dated
# September 9, 2026. Keep this compact table editable and retain its upstream
# scanner IDs so sorting/filtering and external references stay stable.
_BURP_2026_ISSUES = """
OS command injection	High	0x00100100
SQL injection	High	0x00100200
SQL injection (second order)	High	0x00100210
ASP.NET tracing enabled	High	0x00100280
File path traversal	High	0x00100300
XML external entity injection	High	0x00100400
LDAP injection	High	0x00100500
XPath injection	High	0x00100600
XML injection	Medium	0x00100700
ASP.NET debugging enabled	Medium	0x00100800
Broken access control	Information	0x00100850
HTTP PUT method is enabled	High	0x00100900
Out-of-band resource load (HTTP)	High	0x00100a00
File path manipulation	High	0x00100b00
PHP code injection	High	0x00100c00
Server-side JavaScript code injection	High	0x00100d00
Perl code injection	High	0x00100e00
Ruby code injection	High	0x00100f00
Python code injection	High	0x00100f10
Expression Language injection	High	0x00100f20
Unidentified code injection	High	0x00101000
Server-side template injection	High	0x00101080
SSI injection	High	0x00101100
React Server Components remote code execution (React2Shell)	High	0x00101200
Cross-site scripting (stored)	High	0x00200100
HTTP request smuggling	High	0x00200140
Client-side desync	High	0x00200141
Web cache poisoning	High	0x00200180
HTTP response header injection	High	0x00200200
Cross-site scripting (reflected)	High	0x00200300
Client-side template injection	High	0x00200308
Cross-site scripting (DOM-based)	High	0x00200310
Cross-site scripting (reflected DOM-based)	High	0x00200311
Cross-site scripting (stored DOM-based)	High	0x00200312
Client-side prototype pollution	Information	0x00200316
JavaScript injection (DOM-based)	High	0x00200320
JavaScript injection (reflected DOM-based)	High	0x00200321
JavaScript injection (stored DOM-based)	High	0x00200322
Path-relative style sheet import	Information	0x00200328
Client-side SQL injection (DOM-based)	High	0x00200330
Client-side SQL injection (reflected DOM-based)	High	0x00200331
Client-side SQL injection (stored DOM-based)	High	0x00200332
WebSocket URL poisoning (DOM-based)	High	0x00200340
WebSocket URL poisoning (reflected DOM-based)	High	0x00200341
WebSocket URL poisoning (stored DOM-based)	High	0x00200342
Local file path manipulation (DOM-based)	High	0x00200350
Local file path manipulation (reflected DOM-based)	High	0x00200351
Local file path manipulation (stored DOM-based)	High	0x00200352
Client-side XPath injection (DOM-based)	Low	0x00200360
Client-side XPath injection (reflected DOM-based)	Low	0x00200361
Client-side XPath injection (stored DOM-based)	Low	0x00200362
Client-side JSON injection (DOM-based)	Low	0x00200370
Client-side JSON injection (reflected DOM-based)	Low	0x00200371
Client-side JSON injection (stored DOM-based)	Low	0x00200372
Flash cross-domain policy	High	0x00200400
Silverlight cross-domain policy	High	0x00200500
Content security policy: allowlisted script resources	Information	0x00200503
Content security policy: allows untrusted script execution	Information	0x00200504
Content security policy: allows untrusted style execution	Information	0x00200505
Content security policy: malformed syntax	Information	0x00200506
Content security policy: allows clickjacking	Information	0x00200507
Content security policy: allows form hijacking	Information	0x00200508
Content security policy: not enforced	Information	0x00200509
GraphQL endpoint found	Information	0x00200510
GraphQL endpoint discovered	Information	0x00200511
GraphQL introspection enabled	Low	0x00200512
GraphQL suggestions enabled	Low	0x00200513
GraphQL content type not validated	Low	0x00200514
Cross-origin resource sharing	Information	0x00200600
Cross-origin resource sharing: arbitrary origin trusted	High	0x00200601
Cross-origin resource sharing: unencrypted origin trusted	Low	0x00200602
Cross-origin resource sharing: all subdomains trusted	Low	0x00200603
Web cache deception	Medium	0x00200650
Cross-site request forgery	Medium	0x00200700
SMTP header injection	Medium	0x00200800
JWT signature not verified	High	0x00200900
JWT none algorithm supported	High	0x00200901
JWT self-signed JWK header supported	High	0x00200902
JWT weak HMAC secret	High	0x00200903
JWT arbitrary jku header supported	High	0x00200904
JWT arbitrary x5u header supported	High	0x00200905
Cleartext submission of password	High	0x00300100
External service interaction (DNS)	Information	0x00300200
External service interaction (HTTP)	High	0x00300210
External service interaction (SMTP)	Information	0x00300220
Referer-dependent response	Information	0x00400100
Spoofable client IP address	Information	0x00400110
User agent-dependent response	Information	0x00400120
Password returned in later response	Medium	0x00400200
Password submitted using GET method	Low	0x00400300
Password returned in URL query string	Low	0x00400400
SQL statement in request parameter	Medium	0x00400480
Cross-domain POST	Information	0x00400500
ASP.NET ViewState without MAC enabled	High	0x00400600
XML entity expansion	Medium	0x00400700
Long redirection response	Information	0x00400800
Serialized object in HTTP message	High	0x00400900
Duplicate cookies set	Information	0x00400a00
Input returned in response (stored)	Information	0x00400b00
Input returned in response (reflected)	Information	0x00400c00
Suspicious input transformation (reflected)	Information	0x00400d00
Suspicious input transformation (stored)	Information	0x00400e00
Request URL override	Information	0x00400f00
Vulnerable JavaScript dependency	Low	0x00500080
Open redirection (reflected)	Low	0x00500100
Open redirection (stored)	Medium	0x00500101
Open redirection (DOM-based)	Low	0x00500110
Open redirection (reflected DOM-based)	Low	0x00500111
Open redirection (stored DOM-based)	Medium	0x00500112
TLS cookie without secure flag set	Medium	0x00500200
Cookie scoped to parent domain	Low	0x00500300
Cross-domain Referer leakage	Information	0x00500400
Cross-domain script include	Information	0x00500500
Cookie without HttpOnly flag set	Low	0x00500600
Session token in URL	Medium	0x00500700
Password field with autocomplete enabled	Low	0x00500800
Password value set in cookie	Medium	0x00500900
File upload functionality	Information	0x00500980
Frameable response (potential Clickjacking)	Information	0x005009a0
Browser cross-site scripting filter disabled	Information	0x005009b0
HTTP TRACE method is enabled	Information	0x00500a00
Cookie manipulation (DOM-based)	Low	0x00500b00
Cookie manipulation (reflected DOM-based)	Low	0x00500b01
Cookie manipulation (stored DOM-based)	Low	0x00500b02
Ajax request header manipulation (DOM-based)	Low	0x00500c00
Ajax request header manipulation (reflected DOM-based)	Low	0x00500c01
Ajax request header manipulation (stored DOM-based)	Low	0x00500c02
Denial of service (DOM-based)	Information	0x00500d00
Denial of service (reflected DOM-based)	Information	0x00500d01
Denial of service (stored DOM-based)	Low	0x00500d02
HTML5 web message manipulation (DOM-based)	Information	0x00500e00
HTML5 web message manipulation (reflected DOM-based)	Information	0x00500e01
HTML5 web message manipulation (stored DOM-based)	Information	0x00500e02
HTML5 storage manipulation (DOM-based)	Information	0x00500f00
HTML5 storage manipulation (reflected DOM-based)	Information	0x00500f01
HTML5 storage manipulation (stored DOM-based)	Information	0x00500f02
Link manipulation (DOM-based)	Low	0x00501000
Link manipulation (reflected DOM-based)	Low	0x00501001
Link manipulation (stored DOM-based)	Low	0x00501002
Link manipulation (reflected)	Information	0x00501003
Link manipulation (stored)	Information	0x00501004
Document domain manipulation (DOM-based)	Medium	0x00501100
Document domain manipulation (reflected DOM-based)	Medium	0x00501101
Document domain manipulation (stored DOM-based)	Medium	0x00501102
DOM data manipulation (DOM-based)	Information	0x00501200
DOM data manipulation (reflected DOM-based)	Information	0x00501201
DOM data manipulation (stored DOM-based)	Information	0x00501202
CSS injection (reflected)	Medium	0x00501300
CSS injection (stored)	Medium	0x00501301
Client-side HTTP parameter pollution (reflected)	Low	0x00501400
Client-side HTTP parameter pollution (stored)	Low	0x00501401
Form action hijacking (reflected)	Medium	0x00501500
Form action hijacking (stored)	Medium	0x00501501
Database connection string disclosed	Medium	0x00600080
Source code disclosure	Low	0x006000b0
Backup file	Information	0x006000d8
Directory listing	Information	0x00600100
Email addresses disclosed	Information	0x00600200
Private IP addresses disclosed	Information	0x00600300
Social security numbers disclosed	Information	0x00600400
Credit card numbers disclosed	Information	0x00600500
Private key disclosed	Information	0x00600550
Robots.txt file	Information	0x00600600
Json Web Key Set disclosed	Information	0x00600700
JWT private key disclosed	High	0x00600800
OpenAPI definition found (active scan check)	Information	0x00600900
OpenAPI definition found (passive scan check)	Information	0x00600901
Cacheable HTTPS response	Information	0x00700100
Base64-encoded data in parameter	Information	0x00700200
Multiple content types specified	Information	0x00800100
HTML does not specify charset	Information	0x00800200
HTML uses unrecognized charset	Information	0x00800300
Content type incorrectly stated	Low	0x00800400
Content type is not specified	Information	0x00800500
TLS certificate	Medium	0x01000100
Unencrypted communications	Low	0x01000200
Strict transport security not enforced	Low	0x01000300
Mixed content	Information	0x01000400
Hidden HTTP 2	Information	0x01000500
"""

VULNERABILITY_CATALOG = _build_catalog(_BURP_2026_ISSUES)

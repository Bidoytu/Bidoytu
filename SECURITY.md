# Security Policy

Bidoytu is an intercepting HTTP proxy. By design it can decrypt, read, and
modify traffic and it generates a certificate authority (CA) that, once
trusted, can sign certificates for any site. That power makes handling it
carefully important. This document explains how to report vulnerabilities and
how to use the tool responsibly.

## Reporting a vulnerability

Please report security issues **privately**. Do not open a public issue, pull
request, or discussion for a suspected vulnerability, since that discloses it
before a fix is available.

- Contact the maintainer privately (for example, via a direct message or a
  private email to the project owner). If a dedicated security contact address
  is published in the repository, use that.
- Include enough detail to reproduce: affected version or commit, environment
  (OS and Python version), steps to reproduce, and the impact you observed.
- If you have a suggested fix, feel free to include it.

### What to expect

- Acknowledgement of your report as soon as it is reviewed.
- An assessment of severity and, where valid, a plan and timeline for a fix.
- Coordinated disclosure: we will work with you on timing so users can update
  before details are made public. Credit is offered to reporters who want it.

Please act in good faith: only test against your own installation, avoid
accessing or destroying data that is not yours, and give reasonable time for a
fix before any public disclosure.

## Supported versions

Bidoytu is pre-1.0 and under active development. Security fixes target the
latest commit on the default branch. Pin a specific commit if you need
stability, and update to pick up fixes.

## Responsible and lawful use

Bidoytu is intended for testing systems you **own or are explicitly authorized
to test**. Intercepting traffic, installing a MITM CA, or proxying a network
without permission may be illegal in your jurisdiction. You are solely
responsible for how you use this software. See also the disclaimer in the
[LICENSE](LICENSE).

## Handling the CA certificate

To intercept HTTPS, Bidoytu (via mitmproxy) creates a CA under
`<data_dir>/ca/`. Treat these files as sensitive:

- **Never share or commit the CA private key** (`mitmproxy-ca.pem` and the
  `.p12` bundles). Anyone with the private key can impersonate any HTTPS site to
  a machine that trusts the CA. The repository's `.gitignore` excludes the `ca/`
  directory and `mitmproxy-ca*` files to help prevent accidental commits.
- The in-app export (Proxy tab -> **CA Certificate**) only ever exports the
  **public** certificate (`mitmproxy-ca-cert.pem` / `.cer`), never the private
  key.
- Only install and trust the CA on machines you control, and **remove it when
  you are done**. A lingering trusted MITM CA is a standing risk if the private
  key is ever exposed.

## Safe defaults and data handling

- The proxy listens on `127.0.0.1` by default so it is not reachable from other
  machines. Binding to a wider interface (for example `0.0.0.0`) exposes an open
  intercepting proxy on your network; only do this deliberately and behind
  appropriate network controls.
- Captured traffic is stored unencrypted on disk (SQLite plus a body file
  store) under the application data directory. It can contain credentials,
  tokens, cookies, and other secrets. Protect that directory and clear history
  when it is no longer needed.
- All captured traffic and any external content are treated as untrusted input.
  Do not paste captured secrets into logs, issues, or third-party services.

## Scope

This policy covers the Bidoytu application code in this repository. Third-party
dependencies (mitmproxy, PySide6/Qt, httpx, and others) have their own security
processes; report issues in those projects upstream.

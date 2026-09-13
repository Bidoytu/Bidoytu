"""Payload generation and processing for the Intruder.

This module is deliberately Qt-free and side-effect-free so it can be unit
tested and reused off the UI thread. It provides two things:

* **Generators** - produce the raw payload strings for a single payload set:
  a static list, a numeric range/sequence, a brute-forcer over a character set,
  and a "null" generator (N empty payloads, used to replay the base request).

* **Processing rules** - a small, ordered, chainable pipeline that transforms
  each raw payload before it is placed into the request (prefix/suffix,
  URL-encode, base64, hashing, case changes, regex replace). Rules mirror the
  processing rules found in mature intruder tools.

The public entry points are :func:`build_generator` (turn a
:class:`GeneratorSpec` into an iterable of strings) and :func:`apply_rules`
(run a payload through an ordered list of :class:`ProcessingRule`).
"""
from __future__ import annotations

import base64
import hashlib
import itertools
import re
from dataclasses import dataclass, field
from typing import Iterable, Iterator, List
from urllib.parse import quote as _url_quote

# ---------------------------------------------------------------------------
# Generators
# ---------------------------------------------------------------------------

# Generator kinds.
GEN_LIST = "list"
GEN_NUMBERS = "numbers"
GEN_BRUTE = "brute"
GEN_NULL = "null"
GENERATOR_KINDS = (GEN_LIST, GEN_NUMBERS, GEN_BRUTE, GEN_NULL)


@dataclass(slots=True)
class GeneratorSpec:
    """Describes how to produce the payloads for one payload set.

    Only the fields relevant to ``kind`` are used:

    * ``list``    -> ``items`` (explicit strings).
    * ``numbers`` -> ``num_from``, ``num_to``, ``num_step``, ``num_pad``,
                     ``num_hex``.
    * ``brute``   -> ``brute_charset``, ``brute_min``, ``brute_max``.
    * ``null``    -> ``null_count`` empty payloads.
    """

    kind: str = GEN_LIST

    # list
    items: List[str] = field(default_factory=list)

    # numbers
    num_from: float = 0.0
    num_to: float = 10.0
    num_step: float = 1.0
    num_pad: int = 0          # zero-pad the (decimal) output to this width
    num_hex: bool = False     # emit hex instead of decimal

    # brute force
    brute_charset: str = "abcdefghijklmnopqrstuvwxyz0123456789"
    brute_min: int = 1
    brute_max: int = 3

    # null
    null_count: int = 1


def _numbers(spec: GeneratorSpec) -> Iterator[str]:
    step = spec.num_step or 1.0
    # Detect whether the range is integral so we can emit clean ints.
    integral = (
        float(spec.num_from).is_integer()
        and float(spec.num_to).is_integer()
        and float(step).is_integer()
    )
    value = spec.num_from
    # Guard against an infinite loop when step points the wrong way.
    ascending = spec.num_to >= spec.num_from
    if (ascending and step <= 0) or (not ascending and step >= 0):
        step = abs(step) if ascending else -abs(step)
    count = 0
    max_count = 1_000_000  # hard safety cap
    while count < max_count:
        if ascending and value > spec.num_to:
            break
        if not ascending and value < spec.num_to:
            break
        if integral:
            iv = int(round(value))
            if spec.num_hex:
                text = format(iv, "x")
            else:
                text = str(iv)
        else:
            text = f"{value:g}"
        if spec.num_pad > 0:
            text = text.rjust(spec.num_pad, "0")
        yield text
        value += step
        count += 1


def _brute(spec: GeneratorSpec) -> Iterator[str]:
    charset = spec.brute_charset or ""
    if not charset:
        return
    lo = max(1, spec.brute_min)
    hi = max(lo, spec.brute_max)
    for length in range(lo, hi + 1):
        for combo in itertools.product(charset, repeat=length):
            yield "".join(combo)


def build_generator(spec: GeneratorSpec) -> Iterable[str]:
    """Return an iterable of raw payload strings for ``spec``.

    The result is lazy where it matters (numbers, brute force, runtime files)
    so very large payload sets do not have to be materialized up front.
    """
    if spec.kind == GEN_LIST:
        return list(spec.items)
    if spec.kind == GEN_NUMBERS:
        return _numbers(spec)
    if spec.kind == GEN_BRUTE:
        return _brute(spec)
    if spec.kind == GEN_NULL:
        return ["" for _ in range(max(0, spec.null_count))]
    return []


def generator_count(spec: GeneratorSpec) -> int | None:
    """Best-effort count of payloads a spec will produce.

    Returns ``None`` when the count is unknown or unbounded enough that we
    would rather not compute it eagerly (kept simple: brute force is computed
    because the formula is cheap).
    """
    if spec.kind == GEN_LIST:
        return len(spec.items)
    if spec.kind == GEN_NULL:
        return max(0, spec.null_count)
    if spec.kind == GEN_NUMBERS:
        step = spec.num_step or 1.0
        if step == 0:
            return None
        span = spec.num_to - spec.num_from
        if span == 0:
            return 1
        n = int(span // abs(step)) + 1
        return max(0, n)
    if spec.kind == GEN_BRUTE:
        charset = spec.brute_charset or ""
        if not charset:
            return 0
        lo = max(1, spec.brute_min)
        hi = max(lo, spec.brute_max)
        c = len(charset)
        return sum(c ** length for length in range(lo, hi + 1))
    return None


# ---------------------------------------------------------------------------
# Processing rules
# ---------------------------------------------------------------------------

# Rule kinds.
RULE_PREFIX = "prefix"
RULE_SUFFIX = "suffix"
RULE_URL_ENCODE = "url_encode"
RULE_URL_ENCODE_ALL = "url_encode_all"
RULE_BASE64 = "base64"
RULE_HASH = "hash"
RULE_UPPER = "uppercase"
RULE_LOWER = "lowercase"
RULE_CAPITALIZE = "capitalize"
RULE_REVERSE = "reverse"
RULE_REGEX_REPLACE = "regex_replace"

RULE_KINDS = (
    RULE_PREFIX,
    RULE_SUFFIX,
    RULE_URL_ENCODE,
    RULE_URL_ENCODE_ALL,
    RULE_BASE64,
    RULE_HASH,
    RULE_UPPER,
    RULE_LOWER,
    RULE_CAPITALIZE,
    RULE_REVERSE,
    RULE_REGEX_REPLACE,
)

# Human-readable labels for UI dropdowns.
RULE_LABELS = {
    RULE_PREFIX: "Add prefix",
    RULE_SUFFIX: "Add suffix",
    RULE_URL_ENCODE: "URL-encode special chars",
    RULE_URL_ENCODE_ALL: "URL-encode all chars",
    RULE_BASE64: "Base64-encode",
    RULE_HASH: "Hash",
    RULE_UPPER: "Uppercase",
    RULE_LOWER: "Lowercase",
    RULE_CAPITALIZE: "Capitalize",
    RULE_REVERSE: "Reverse",
    RULE_REGEX_REPLACE: "Regex replace",
}

_HASH_ALGOS = ("md5", "sha1", "sha256", "sha512")


@dataclass(slots=True)
class ProcessingRule:
    """One transformation step in the payload processing pipeline.

    Only the fields relevant to ``kind`` are used:

    * ``prefix``/``suffix``       -> ``text``.
    * ``hash``                    -> ``algo`` (md5/sha1/sha256/sha512).
    * ``regex_replace``           -> ``pattern`` and ``replacement``.
    * everything else             -> no parameters.
    """

    kind: str
    text: str = ""
    algo: str = "md5"
    pattern: str = ""
    replacement: str = ""
    enabled: bool = True


def _apply_one(rule: ProcessingRule, value: str) -> str:
    kind = rule.kind
    if kind == RULE_PREFIX:
        return rule.text + value
    if kind == RULE_SUFFIX:
        return value + rule.text
    if kind == RULE_URL_ENCODE:
        return _url_quote(value, safe="")
    if kind == RULE_URL_ENCODE_ALL:
        return "".join(f"%{b:02X}" for b in value.encode("utf-8"))
    if kind == RULE_BASE64:
        return base64.b64encode(value.encode("utf-8")).decode("ascii")
    if kind == RULE_HASH:
        algo = rule.algo if rule.algo in _HASH_ALGOS else "md5"
        h = hashlib.new(algo)
        h.update(value.encode("utf-8"))
        return h.hexdigest()
    if kind == RULE_UPPER:
        return value.upper()
    if kind == RULE_LOWER:
        return value.lower()
    if kind == RULE_CAPITALIZE:
        return value.capitalize()
    if kind == RULE_REVERSE:
        return value[::-1]
    if kind == RULE_REGEX_REPLACE:
        try:
            return re.sub(rule.pattern, rule.replacement, value)
        except re.error:
            return value
    return value


def apply_rules(value: str, rules: Iterable[ProcessingRule]) -> str:
    """Run ``value`` through each enabled rule in order and return the result."""
    for rule in rules:
        if rule.enabled:
            value = _apply_one(rule, value)
    return value


def describe_rule(rule: ProcessingRule) -> str:
    """Return a compact one-line description of a rule (for list widgets)."""
    label = RULE_LABELS.get(rule.kind, rule.kind)
    if rule.kind in (RULE_PREFIX, RULE_SUFFIX):
        return f"{label}: {rule.text!r}"
    if rule.kind == RULE_HASH:
        return f"{label}: {rule.algo}"
    if rule.kind == RULE_REGEX_REPLACE:
        return f"{label}: /{rule.pattern}/ -> {rule.replacement!r}"
    return label

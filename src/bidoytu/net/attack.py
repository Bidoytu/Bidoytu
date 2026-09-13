"""Intruder attack model: markers, attack types, and request building.

Qt-free so it can be tested and run off the UI thread. The pieces:

* :func:`find_markers` / :func:`strip_markers` - locate and remove the ``§``
  payload-position markers in a request template.
* :class:`AttackType` - the four classic strategies (sniper, battering ram,
  pitchfork, cluster bomb).
* :func:`iter_jobs` - given the template, marker positions, attack type, and one
  or more payload sets, yield a :class:`AttackJob` per request: the fully
  substituted request text plus the payload(s) used.

Payload *generation* and *processing* live in :mod:`bidoytu.net.payloads`;
this module only decides how positions are combined and performs substitution.
"""
from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from typing import Iterator, List, Sequence

from bidoytu.net.payloads import (
    GeneratorSpec,
    ProcessingRule,
    apply_rules,
    build_generator,
    generator_count,
)

MARKER = "\u00a7"  # §

# Attack types.
SNIPER = "sniper"
BATTERING_RAM = "battering_ram"
PITCHFORK = "pitchfork"
CLUSTER_BOMB = "cluster_bomb"
ATTACK_TYPES = (SNIPER, BATTERING_RAM, PITCHFORK, CLUSTER_BOMB)

ATTACK_LABELS = {
    SNIPER: "Sniper (one set, one position at a time)",
    BATTERING_RAM: "Battering ram (one set, all positions)",
    PITCHFORK: "Pitchfork (multiple sets, in lockstep)",
    CLUSTER_BOMB: "Cluster bomb (multiple sets, all combinations)",
}


@dataclass(slots=True)
class Marker:
    """A payload position: the span between a pair of ``§`` markers.

    ``start``/``end`` are offsets into the *marker-stripped* text, i.e. where
    the payload should be inserted. ``default`` is the text that was between the
    markers in the template (used to preview / for the base request).
    """

    start: int
    end: int
    default: str


@dataclass(slots=True)
class PayloadSet:
    """A generator plus its processing rules (one Intruder payload set)."""

    generator: GeneratorSpec = field(default_factory=GeneratorSpec)
    rules: List[ProcessingRule] = field(default_factory=list)

    def values(self) -> Iterator[str]:
        for raw in build_generator(self.generator):
            yield apply_rules(raw, self.rules)

    def count(self) -> int | None:
        return generator_count(self.generator)


@dataclass(slots=True)
class AttackJob:
    """One request to send: the substituted text and the payloads used."""

    index: int
    request_text: str
    payloads: List[str]


def find_markers(template: str) -> tuple[str, List[Marker]]:
    """Split a ``§``-marked template into (clean_text, markers).

    Markers come in pairs: ``§value§``. An unpaired trailing ``§`` is ignored.
    The returned ``clean_text`` has the markers removed with each position's
    default value left in place; ``markers`` records where each position sits in
    that clean text so payloads can be spliced in later.
    """
    clean_parts: List[str] = []
    markers: List[Marker] = []
    pos = 0
    clean_len = 0
    while True:
        open_at = template.find(MARKER, pos)
        if open_at == -1:
            clean_parts.append(template[pos:])
            break
        close_at = template.find(MARKER, open_at + 1)
        if close_at == -1:
            # Unpaired marker: keep the rest verbatim.
            clean_parts.append(template[pos:])
            break
        # Text before the marker.
        before = template[pos:open_at]
        clean_parts.append(before)
        clean_len += len(before)
        default = template[open_at + 1:close_at]
        start = clean_len
        clean_parts.append(default)
        clean_len += len(default)
        markers.append(Marker(start=start, end=clean_len, default=default))
        pos = close_at + 1
    return "".join(clean_parts), markers


def strip_markers(template: str) -> str:
    """Return the template with all ``§`` markers removed (defaults kept)."""
    clean, _ = find_markers(template)
    return clean


def wrap_selection(text: str, sel_start: int, sel_end: int) -> str:
    """Wrap the ``[sel_start, sel_end)`` span of ``text`` in ``§`` markers.

    Used by the UI's "Add §" button. If the selection is empty, a single empty
    marker pair is inserted at the caret.
    """
    if sel_start > sel_end:
        sel_start, sel_end = sel_end, sel_start
    return (
        text[:sel_start] + MARKER + text[sel_start:sel_end] + MARKER + text[sel_end:]
    )


def _splice(clean_text: str, markers: Sequence[Marker], values: Sequence[str]) -> str:
    """Insert ``values`` into ``clean_text`` at each marker (right-to-left).

    Working right-to-left keeps earlier offsets valid as we mutate the string.
    ``values`` must have one entry per marker.
    """
    result = clean_text
    for marker, value in sorted(
        zip(markers, values), key=lambda mv: mv[0].start, reverse=True
    ):
        result = result[:marker.start] + value + result[marker.end:]
    return result


def count_jobs(attack_type: str, markers: Sequence[Marker],
               sets: Sequence[PayloadSet]) -> int | None:
    """Best-effort total request count for a configured attack."""
    if not markers or not sets:
        return 0
    if attack_type == SNIPER:
        c = sets[0].count()
        return None if c is None else c * len(markers)
    if attack_type == BATTERING_RAM:
        return sets[0].count()
    if attack_type == PITCHFORK:
        counts = [s.count() for s in sets[:len(markers)]]
        if any(c is None for c in counts) or not counts:
            return None
        return min(counts)
    if attack_type == CLUSTER_BOMB:
        counts = [s.count() for s in sets[:len(markers)]]
        if any(c is None for c in counts) or not counts:
            return None
        total = 1
        for c in counts:
            total *= c
        return total
    return None


def iter_jobs(clean_text: str, markers: Sequence[Marker], attack_type: str,
              sets: Sequence[PayloadSet]) -> Iterator[AttackJob]:
    """Yield an :class:`AttackJob` per request for the configured attack.

    ``clean_text`` and ``markers`` come from :func:`find_markers`. ``sets`` is
    one or more payload sets; sniper and battering ram only use ``sets[0]``.
    """
    if not markers or not sets:
        return

    defaults = [m.default for m in markers]
    index = 0

    if attack_type == SNIPER:
        # One position varies at a time; the rest keep their default value.
        for pos in range(len(markers)):
            for payload in sets[0].values():
                values = list(defaults)
                values[pos] = payload
                yield AttackJob(index, _splice(clean_text, markers, values), [payload])
                index += 1
        return

    if attack_type == BATTERING_RAM:
        # Same payload in every position.
        for payload in sets[0].values():
            values = [payload] * len(markers)
            yield AttackJob(index, _splice(clean_text, markers, values),
                            [payload] * len(markers))
            index += 1
        return

    if attack_type == PITCHFORK:
        # Advance every set in lockstep; stop at the shortest.
        iters = [iter(sets[i % len(sets)].values()) for i in range(len(markers))]
        while True:
            try:
                values = [next(it) for it in iters]
            except StopIteration:
                return
            yield AttackJob(index, _splice(clean_text, markers, values), list(values))
            index += 1

    if attack_type == CLUSTER_BOMB:
        # Cartesian product across positions. Materialize each set (cluster
        # bomb requires re-iterating the inner sets anyway).
        materialized = [list(sets[i % len(sets)].values()) for i in range(len(markers))]
        for combo in itertools.product(*materialized):
            yield AttackJob(index, _splice(clean_text, markers, list(combo)), list(combo))
            index += 1

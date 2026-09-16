# Performance ledger

## 2026-09-16

| Change | Measurement | Result |
|---|---|---|
| Reuse request/response records during capture and interception | `scripts/smoke_test.py` | Kept; all smoke checks passed |
| Cache scope normalization and compiled scope regexes | Capture hot-path review | Kept; bounded caches (512 / 256 entries) |
| Configure bounded SQLite cache, statement cache, and busy timeout | Focused 500 insert + 500 update run | Kept; 0.036s inserts, 0.036s updates, 500 rows |
| Replace upsert read-then-write with SQLite `ON CONFLICT ... RETURNING` | Focused persistence run | Kept; one statement per capture event |

The GUI smoke run is startup-dominated and remained stable at about 11.8s. A
real proxy/network benchmark was not run because it would require an external
target and representative traffic.

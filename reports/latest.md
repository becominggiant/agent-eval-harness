# Eval report: `fixture` (fixture)

_Generated 2026-10-26T15:11:29-0500_

| Metric | Value |
|---|---|
| Cases | 12 |
| Exact-match accuracy | 91.7% |
| Field-level accuracy | 97.9% |
| JSON validity | 100.0% |
| Latency p50 / p95 | 0.011 ms / 0.028 ms |
| Estimated cost | $0.000000 |

## By task

| Task | Cases | Exact | Field |
|---|---|---|---|
| extract_listing | 4 | 75.0% | 93.8% |
| margin_calc | 3 | 100.0% | 100.0% |
| classify_ticket | 5 | 100.0% | 100.0% |

## vs baseline

| Metric | Baseline | Current | Δ |
|---|---|---|---|
| exact_accuracy | 0.9167 | 0.9167 | +0.0000 |
| field_accuracy | 0.9792 | 0.9792 | +0.0000 |
| json_validity | 1.0000 | 1.0000 | +0.0000 |
| latency_p50_ms | 0.0086 | 0.0111 | +0.0025 |
| total_cost_usd | 0.0000 | 0.0000 | +0.0000 |

## Cases

| ID | Pass | Field acc | Latency (ms) | Failed fields |
|---|---|---|---|---|
| extract-001 | ✅ | 100% | 0.239 |  |
| extract-002 | ✅ | 100% | 0.028 |  |
| extract-003 | ❌ | 75% | 0.016 | product |
| extract-004 | ✅ | 100% | 0.014 |  |
| margin-001 | ✅ | 100% | 0.014 |  |
| margin-002 | ✅ | 100% | 0.009 |  |
| margin-003 | ✅ | 100% | 0.013 |  |
| ticket-001 | ✅ | 100% | 0.006 |  |
| ticket-002 | ✅ | 100% | 0.006 |  |
| ticket-003 | ✅ | 100% | 0.005 |  |
| ticket-004 | ✅ | 100% | 0.005 |  |
| ticket-005 | ✅ | 100% | 0.005 |  |

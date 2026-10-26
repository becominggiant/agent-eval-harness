"""Write Markdown + JSON reports."""
from __future__ import annotations
import json
from pathlib import Path


def to_markdown(run: dict) -> str:
    s = run["summary"]
    L = [f"# Eval report: `{run['agent']}` ({run['model']})", "", f"_Generated {run['timestamp']}_", "",
         "| Metric | Value |", "|---|---|",
         f"| Cases | {s['cases']} |",
         f"| Exact-match accuracy | {s['exact_accuracy']:.1%} |",
         f"| Field-level accuracy | {s['field_accuracy']:.1%} |",
         f"| JSON validity | {s['json_validity']:.1%} |",
         f"| Latency p50 / p95 | {s['latency_p50_ms']:.3f} ms / {s['latency_p95_ms']:.3f} ms |",
         f"| Estimated cost | ${s['total_cost_usd']:.6f} |", "",
         "## By task", "", "| Task | Cases | Exact | Field |", "|---|---|---|---|"]
    for t, v in s["by_task"].items():
        L.append(f"| {t} | {v['cases']} | {v['exact_accuracy']:.1%} | {v['field_accuracy']:.1%} |")
    if "comparison" in run:
        L += ["", "## vs baseline", "", "| Metric | Baseline | Current | Δ |", "|---|---|---|---|"]
        for k, v in run["comparison"].items():
            L.append(f"| {k} | {v['baseline']:.4f} | {v['current']:.4f} | {v['delta']:+.4f} |")
    L += ["", "## Cases", "", "| ID | Pass | Field acc | Latency (ms) | Failed fields |", "|---|---|---|---|---|"]
    for r in run["results"]:
        bad = ", ".join(k for k, v in r["field_results"].items() if v < 1) or ("invalid JSON" if not r["json_valid"] else "")
        L.append(f"| {r['id']} | {'✅' if r['exact'] else '❌'} | {r['field_accuracy']:.0%} | {r['latency_ms']:.3f} | {bad} |")
    return "\n".join(L) + "\n"


def write(run: dict, out_dir: str = "reports/") -> tuple[Path, Path]:
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    md, js = out / "latest.md", out / "latest.json"
    md.write_text(to_markdown(run))
    js.write_text(json.dumps(run, indent=2, default=str))
    return md, js

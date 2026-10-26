"""Load golden cases, run an agent, collect metrics, write reports, gate on thresholds."""
from __future__ import annotations
import argparse
import importlib
import json
import statistics
import sys
import time
from pathlib import Path

import yaml

from harness.scoring import estimate_cost, score_case
from harness import report as report_mod


def load_cases(path: str | Path) -> list[dict]:
    path = Path(path)
    files = sorted(path.glob("*.y*ml")) + sorted(path.glob("*.json")) if path.is_dir() else [path]
    cases = []
    for f in files:
        data = yaml.safe_load(f.read_text())  # YAML is a superset of JSON
        for c in data["cases"]:
            cases.append({**c, "task": c.get("task", data["task"])})
    return cases


def load_agent(name: str):
    mod = importlib.import_module(f"agents.{name}_agent")
    if hasattr(mod, "available") and not mod.available():
        raise SystemExit(f"agent '{name}' is not available (missing API key?)")
    return mod


def run_eval(agent_name: str, cases_path: str) -> dict:
    agent = load_agent(agent_name)
    results = []
    for case in load_cases(cases_path):
        t0 = time.perf_counter()
        error = None
        try:
            resp = agent.run(case["task"], case["input"])
        except Exception as e:  # agent failures are scored, not fatal
            resp, error = {"output": None, "model": getattr(agent, "MODEL", agent_name), "usage": {}}, repr(e)
        latency_ms = (time.perf_counter() - t0) * 1000
        usage = resp.get("usage", {})
        s = score_case(case["expected"], resp["output"])
        results.append({
            "id": case["id"], "task": case["task"], "latency_ms": latency_ms,
            "prompt_tokens": usage.get("prompt_tokens", 0), "completion_tokens": usage.get("completion_tokens", 0),
            "cost_usd": estimate_cost(resp["model"], usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0)),
            "output": resp["output"], "error": error, **s,
        })
    return {"agent": agent_name, "model": getattr(agent, "MODEL", agent_name),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "summary": summarize(results), "results": results}


def summarize(results: list[dict]) -> dict:
    n = len(results) or 1
    lat = sorted(r["latency_ms"] for r in results) or [0]
    by_task = {}
    for r in results:
        by_task.setdefault(r["task"], []).append(r)
    return {
        "cases": len(results),
        "exact_accuracy": sum(r["exact"] for r in results) / n,
        "field_accuracy": sum(r["field_accuracy"] for r in results) / n,
        "json_validity": sum(r["json_valid"] for r in results) / n,
        "latency_p50_ms": statistics.median(lat),
        "latency_p95_ms": lat[min(len(lat) - 1, int(round(0.95 * (len(lat) - 1))))],
        "total_cost_usd": sum(r["cost_usd"] for r in results),
        "by_task": {t: {"cases": len(rs), "exact_accuracy": sum(r["exact"] for r in rs) / len(rs),
                        "field_accuracy": sum(r["field_accuracy"] for r in rs) / len(rs)} for t, rs in by_task.items()},
    }


def compare(current: dict, baseline_path: str) -> dict:
    base = json.loads(Path(baseline_path).read_text())["summary"]
    keys = ["exact_accuracy", "field_accuracy", "json_validity", "latency_p50_ms", "total_cost_usd"]
    return {k: {"baseline": base[k], "current": current["summary"][k], "delta": current["summary"][k] - base[k]} for k in keys}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Run golden-case evals against an agent.")
    p.add_argument("--agent", default="fixture", help="fixture | openai")
    p.add_argument("--cases", default="cases/")
    p.add_argument("--out", default="reports/")
    p.add_argument("--baseline", help="previous report JSON to compare against")
    p.add_argument("--min-accuracy", type=float, default=0.8, help="fail if field_accuracy below this")
    p.add_argument("--max-regression", type=float, default=0.02, help="fail if accuracy drops more than this vs baseline")
    args = p.parse_args(argv)

    run = run_eval(args.agent, args.cases)
    if args.baseline:
        run["comparison"] = compare(run, args.baseline)
    md, js = report_mod.write(run, args.out)
    s = run["summary"]
    print(f"{run['agent']} ({run['model']}): exact={s['exact_accuracy']:.1%} field={s['field_accuracy']:.1%} "
          f"json={s['json_validity']:.1%} p50={s['latency_p50_ms']:.2f}ms cost=${s['total_cost_usd']:.6f}")
    print(f"report: {md}  {js}")

    failed = False
    if s["field_accuracy"] < args.min_accuracy:
        print(f"FAIL: field_accuracy {s['field_accuracy']:.3f} < {args.min_accuracy}"); failed = True
    if "comparison" in run and run["comparison"]["field_accuracy"]["delta"] < -args.max_regression:
        print("FAIL: accuracy regression vs baseline"); failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

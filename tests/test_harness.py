import json
from harness.runner import load_cases, run_eval, main
from harness.scoring import score_case, parse_json, estimate_cost


def test_cases_load():
    cases = load_cases("cases/")
    assert len(cases) >= 8
    assert all({"id", "task", "input", "expected"} <= c.keys() for c in cases)


def test_scoring_basics():
    assert parse_json("not json") == (False, None)
    assert score_case({"a": 1.0}, json.dumps({"a": 1.004}))["exact"]
    assert score_case({"a": "AirPods Pro 2nd gen"}, '{"a": "AirPods Pro 2nd-gen"}')["exact"]
    assert score_case({"a": "x"}, "{broken")["json_valid"] is False
    assert estimate_cost("gpt-4o-mini", 1_000_000, 0) == 0.15


def test_fixture_meets_thresholds():
    s = run_eval("fixture", "cases/")["summary"]
    assert s["json_validity"] == 1.0
    assert s["field_accuracy"] >= 0.8
    assert s["total_cost_usd"] == 0.0


def test_cli_gate(tmp_path):
    assert main(["--agent", "fixture", "--out", str(tmp_path)]) == 0
    assert (tmp_path / "latest.md").exists()
    assert main(["--agent", "fixture", "--out", str(tmp_path), "--min-accuracy", "1.01"]) == 1

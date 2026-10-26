"""Deterministic, rule-based agent. No network, no API key: used for CI.
It is intentionally imperfect so the harness has real failures to report."""
from __future__ import annotations
import json
import re

MODEL = "fixture"
KNOWN_BRANDS = ["Nintendo", "Apple", "Sony", "Pokemon", "Samsung", "Microsoft"]
TICKET_RULES = [
    ("billing", ["charged", "refund", "payment", "invoice"]),
    ("shipping", ["package", "delivered", "tracking", "arrived"]),
    ("technical", ["crash", "error", "bug", "login", "app"]),
    ("returns", ["return", "send it back", "exchange"]),
]


def _tokens(text: str) -> int:
    return max(1, len(text) // 4)


def extract_listing(text: str) -> dict:
    price = re.search(r"\$(\d+(?:\.\d+)?)", text)
    brand = next((b for b in KNOWN_BRANDS if b.lower() in text.lower()), None)
    low = text.lower()
    condition = "new" if re.search(r"\b(new|sealed)\b", low) and "pre-owned" not in low else "used"
    product = None
    if brand:
        after = text[text.lower().index(brand.lower()) + len(brand):]
        product = re.split(r"[,\-]| \$", after, maxsplit=1)[0].strip()
    return {"brand": brand, "product": product, "condition": condition,
            "price": float(price.group(1)) if price else None}


def margin_calc(inp: dict) -> dict:
    buy, sell, fee = inp["buy"], inp["sell"], inp["fee_pct"]
    profit = round(sell - sell * fee - buy, 2)
    return {"profit": profit, "margin_pct": round(profit / sell * 100, 2)}


def classify_ticket(text: str) -> dict:
    low = text.lower()
    for cat, kws in TICKET_RULES:
        if any(k in low for k in kws):
            return {"category": cat}
    return {"category": "general"}


TASKS = {"extract_listing": extract_listing, "margin_calc": margin_calc, "classify_ticket": classify_ticket}


def run(task: str, inp) -> dict:
    out = json.dumps(TASKS[task](inp))
    return {"output": out, "model": MODEL,
            "usage": {"prompt_tokens": _tokens(json.dumps(inp)), "completion_tokens": _tokens(out)}}

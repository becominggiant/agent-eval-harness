"""Optional OpenAI-backed agent using Structured Outputs + Pydantic.
Only used when OPENAI_API_KEY is set; requires `pip install openai`."""
from __future__ import annotations
import json
import os
from typing import Literal, Optional
from pydantic import BaseModel

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


class Listing(BaseModel):
    brand: Optional[str]
    product: Optional[str]
    condition: Literal["new", "used"]
    price: Optional[float]


class Margin(BaseModel):
    profit: float
    margin_pct: float


class Ticket(BaseModel):
    category: Literal["billing", "shipping", "technical", "returns", "general"]


PROMPTS = {
    "extract_listing": (Listing, "Extract brand, product (model name without brand), condition (new/used) and price in USD from the listing."),
    "margin_calc": (Margin, "Given buy, sell and fee_pct (fee charged on sell price), compute profit = sell - sell*fee_pct - buy and margin_pct = profit/sell*100, rounded to 2 decimals."),
    "classify_ticket": (Ticket, "Classify the customer support ticket into one category."),
}


def available() -> bool:
    return bool(os.getenv("OPENAI_API_KEY"))


def run(task: str, inp) -> dict:
    from openai import OpenAI  # imported lazily so CI never needs it
    schema, system = PROMPTS[task]
    client = OpenAI()
    resp = client.beta.chat.completions.parse(
        model=MODEL, temperature=0, response_format=schema,
        messages=[{"role": "system", "content": system},
                  {"role": "user", "content": inp if isinstance(inp, str) else json.dumps(inp)}],
    )
    msg = resp.choices[0].message
    out = msg.parsed.model_dump_json() if msg.parsed else (msg.content or "")
    return {"output": out, "model": MODEL,
            "usage": {"prompt_tokens": resp.usage.prompt_tokens, "completion_tokens": resp.usage.completion_tokens}}

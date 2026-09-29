from __future__ import annotations

import html
import json
import os
from pathlib import Path
from statistics import mean
from typing import Any

from .metrics import percentile


def _as_float(value: Any) -> float:
    return float(value) if isinstance(value, (int, float)) else 0.0


def _records() -> list[dict[str, Any]]:
    path = Path(os.getenv("LOG_PATH", "data/logs.jsonl"))
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            records.append(value)
    return records


def snapshot() -> dict[str, Any]:
    """Aggregate the six dashboard panels from the JSONL source contract."""
    records = _records()
    requests = [record for record in records if record.get("event") == "request_received"]
    responses = [record for record in records if record.get("event") == "response_sent"]
    failures = [record for record in records if record.get("event") == "request_failed"]
    latencies = [_as_float(record.get("latency_ms")) for record in responses]
    ttfts = [_as_float(record.get("ttft_ms")) for record in responses]
    costs = [_as_float(record.get("cost_usd")) for record in responses]
    tokens_in = sum(_as_float(record.get("tokens_in")) for record in responses)
    tokens_out = sum(_as_float(record.get("tokens_out")) for record in responses)
    quality = [_as_float(record.get("quality_score")) for record in responses]
    retrieval = [record for record in records if record.get("tool_success") is not None]
    retrieval_success = sum(record.get("tool_success") is True for record in retrieval)

    return {
        "latency_p50": percentile(latencies, 50),
        "latency_p95": percentile(latencies, 95),
        "latency_p99": percentile(latencies, 99),
        "ttft_p95": percentile(ttfts, 95),
        "request_count": len(requests),
        "requests_per_minute": len(requests) / 60,
        "error_rate_pct": (len(failures) / len(requests) * 100) if requests else 0.0,
        "retrieval_success_rate_pct": (retrieval_success / len(retrieval) * 100) if retrieval else 0.0,
        "cost_total_usd": sum(costs),
        "tokens_in_total": tokens_in,
        "tokens_out_total": tokens_out,
        "quality_mean": mean(quality) if quality else 0.0,
    }


def _panel(title: str, body: str, threshold: str) -> str:
    return f"""
      <section class=\"panel\">
        <h2>{html.escape(title)}</h2>
        <div class=\"metric\">{body}</div>
        <p class=\"threshold\">SLO / threshold: {html.escape(threshold)}</p>
      </section>"""


def render_html() -> str:
    values = snapshot()
    panels = "".join(
        [
            _panel(
                "Latency percentiles and TTFT",
                f"P50 {values['latency_p50']:.0f} ms · P95 {values['latency_p95']:.0f} ms · "
                f"P99 {values['latency_p99']:.0f} ms · TTFT P95 {values['ttft_p95']:.0f} ms",
                "P95 latency ≤ 3000 ms",
            ),
            _panel(
                "Request traffic",
                f"{values['request_count']} requests · {values['requests_per_minute']:.2f} requests/minute",
                "rate ≥ 1 request/minute",
            ),
            _panel(
                "Error rate and retrieval success",
                f"Error rate {values['error_rate_pct']:.2f}% · Retrieval success "
                f"{values['retrieval_success_rate_pct']:.2f}%",
                "errors ≤ 2% · retrieval success ≥ 90%",
            ),
            _panel(
                "Cost over time",
                f"Total ${values['cost_total_usd']:.4f}",
                "total ≤ $2.50",
            ),
            _panel(
                "Input and output tokens",
                f"Input {values['tokens_in_total']:.0f} · Output {values['tokens_out_total']:.0f}",
                "combined total ≤ 50,000 tokens",
            ),
            _panel(
                "Quality proxy",
                f"Mean quality {values['quality_mean']:.2f}",
                "mean quality ≥ 0.75",
            ),
        ]
    )
    return f"""<!doctype html>
<html lang=\"en\"><head><meta charset=\"utf-8\"><meta http-equiv=\"refresh\" content=\"30\">
<title>K4-L3A LLMOps dashboard</title><style>
body {{ font-family: system-ui, sans-serif; max-width: 1100px; margin: 32px auto; color: #182230; background: #f7f9fc; }}
.meta {{ color: #58677a; }} .grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }}
.panel {{ background: white; border: 1px solid #d9e1eb; border-radius: 12px; padding: 18px; box-shadow: 0 2px 8px #1720330d; }}
h1 {{ margin-bottom: 4px; }} h2 {{ font-size: 1.05rem; margin-top: 0; }} .metric {{ font-size: 1.15rem; font-weight: 650; line-height: 1.55; }}
.threshold {{ color: #176b42; margin: 14px 0 0; font-size: .9rem; }}
</style></head><body><h1>K4-L3A Day 13 Monitoring &amp; LLMOps</h1>
<p class=\"meta\">Source: <code>data/logs.jsonl</code> · Time range: last 60 minutes · Refresh: 30 seconds</p>
<main class=\"grid\">{panels}</main></body></html>"""

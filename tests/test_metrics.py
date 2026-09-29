from pathlib import Path

from app import dashboard
from app.metrics import percentile


def test_percentile_basic() -> None:
    assert percentile([100, 200, 300, 400], 50) >= 100


def test_dashboard_snapshot_uses_jsonl_source(monkeypatch, tmp_path: Path) -> None:
    path = tmp_path / "logs.jsonl"
    path.write_text(
        "\n".join(
            [
                '{"event":"request_received"}',
                '{"event":"response_sent","latency_ms":120,"ttft_ms":30,"cost_usd":0.01,"tokens_in":12,"tokens_out":34,"quality_score":0.9,"tool_success":true}',
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("LOG_PATH", str(path))

    values = dashboard.snapshot()

    assert values["request_count"] == 1
    assert values["latency_p95"] == 120
    assert values["retrieval_success_rate_pct"] == 100
    assert "Latency percentiles and TTFT" in dashboard.render_html()

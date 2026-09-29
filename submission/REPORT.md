# Báo cáo cá nhân — K4-L3A Day 13 Monitoring & LLMOps

> Mỗi học viên hoàn thiện một file duy nhất này. Khi dẫn evidence, dùng đường dẫn tương đối, ví dụ `evidence/07-trace-waterfall.png`.

## 1. Thông tin học viên

- **Họ và tên:** Lê Phan Việt Cường
- **MSSV:** 2A202602641
- **Lớp:** K4-L3A
- **Repository URL:** https://github.com/cuonglpv/K4-L3-DAY13-LePhanVietCuong-2A202602641-Monitoring-LLMOps
- **Commit SHA cuối:** Dùng SHA của `HEAD` tại thời điểm push/nộp bài.
- **Challenge ID:**
- **Tên project Langfuse cá nhân:** `day13-k4-l3a-2A202602641`.

## 2. Evidence index

Điền đúng đường dẫn tới evidence thực tế. Có thể đổi tên hoặc dùng nhiều ảnh nếu cần.

| Evidence | Đường dẫn |
|---|---|
| CP0 baseline | `evidence/00-cp0-baseline.txt` |
| Pytest cuối | `evidence/01-pytest-cp2.txt` |
| Log validator | `evidence/02-log-validator-cp2.txt` |
| Dashboard validator | `evidence/03-dashboard-validator-cp1.txt` |
| Structured log | `evidence/04-structured-log-cp1.txt` |
| PII redaction | `evidence/05-pii-redaction-cp1.txt` |
| Trace list | `evidence/06-trace-list.png`, `evidence/06-trace-list-baseline.txt`, `evidence/06-trace-list-candidate.txt` |
| Trace waterfall | `evidence/07-trace-waterfall.png` |
| Trace metadata | `evidence/08-trace-metadata.png`, `evidence/08-trace-metadata-baseline.txt`, `evidence/08-trace-metadata-candidate.txt` |
| Prompt versions | `evidence/09-prompt-versions.png` |
| Prompt rollback | `evidence/10-prompt-promote-v3.png`, `evidence/10-prompt-rollback.png`, `evidence/10-prompt-production-v3.txt`, `evidence/10-prompt-rollback-v1.txt` |
| Dashboard runtime | `evidence/11-dashboard-overview.png`, `evidence/11-dashboard-runtime-cp2.txt` |
| Practice `rag_slow` (không phải CP3 official) | `evidence/15-practice-rag-slow.txt` |
| Incident metric | Chưa có — chờ challenge file chính thức |
| Incident log | Chưa có — chờ challenge file chính thức |
| Incident trace | Chưa có — chờ challenge file chính thức |

## 3. Kết quả kỹ thuật

| Nội dung | Baseline | Kết quả cuối | Nhận xét |
|---|---|---|---|
| `validate_logs.py` | 30/100 | 100/100 | CP1 workload mới, không dùng lại log baseline |
| `validate_dashboard.py` | 6/6 panel | 6/6 panel | Contract hợp lệ |
| `pytest` | 22 passed | 26 passed | Bổ sung test PII, child observations và dashboard JSONL |
| Số traces hợp lệ | 0 | 10 | Langfuse Observations API trả 30 observations: 10 root traces và 20 child observations |
| Số PII leak | 0 | 0 | Validator quét 44 JSONL record ở CP2 |
| Latency P95 / TTFT P95 | — | 152 ms / 50 ms | Aggregation dashboard CP2 |
| Retrieval success rate | — | 100% | Aggregation dashboard CP2 |

## 4. Logging và PII

- **Cách tạo/nhận và truyền correlation ID:** Middleware xóa `structlog` context ở đầu request, nhận `x-request-id` đúng định dạng `req-<8-hex>` hoặc sinh ID mới, bind vào context, lưu ở `request.state`, rồi trả cùng ID trong response header. `x-response-time-ms` đo toàn bộ thời gian xử lý request.
- **Các metadata được ghi vào structured log:** `user_id_hash` (SHA-256 cắt 12 ký tự), `session_id`, `feature`, `model`, `env`, `correlation_id`, timestamp, event, level và các số đo response như latency, TTFT, token, cost, quality và trạng thái retrieval.
- **Cách bảo đảm PII được scrub trước khi ghi:** Processor `scrub_event` duyệt đệ quy mọi string trong event và chạy trước cả file writer lẫn JSON renderer. Nó che email, điện thoại Việt Nam, CCCD, thẻ và passport; user ID không được ghi thô.
- **Cách kiểm chứng kết quả:** Request dùng dữ liệu test tổng hợp có correlation ID `req-a1b2c3d4` trả header tương ứng; log chỉ còn marker redaction. `validate_logs.py` đạt 100/100, evidence CP1 được lưu tại `evidence/02-log-validator-cp1.txt`, `evidence/04-structured-log-cp1.txt` và `evidence/05-pii-redaction-cp1.txt`.

## 5. Tracing và prompt versioning

- **Cách xác nhận traces do chính tôi tạo trong project cá nhân:** Sau khi cấu hình key riêng và `LANGFUSE_PROMPT_LABEL=baseline`, workload mới tạo 10 trace/30 observations được API xác nhận. Danh sách ID ở `evidence/06-trace-list-baseline.txt`; trước khi nộp vẫn cần screenshot UI thấy tên project cá nhân.
- **Cấu trúc root/retrieval/generation observations:** Root `lab-agent-run` (agent) do `@observe` tạo; bên trong có child `retrieval` loại `retriever` và `llm.generate` loại `generation`. Generation lưu model, prompt managed (nếu có), usage input/output/total, cost input/output/total, TTFT và output preview đã scrub.
- **Cách nối trace với log:** `correlation_id` được đưa vào trace metadata qua `propagate_attributes`, đồng thời là context field trong log JSONL. Khi có incident, lọc log lấy ID rồi tìm metadata cùng ID trong Langfuse.
- **Prompt name:** `day13-chat` (cấu hình trong `.env.example`).
- **Version/label baseline:** Version 1, label `baseline`; trace `b9f5a0d7e0a2c0189c1755722439322e` xác nhận `prompt_source=langfuse`.
- **Version/label candidate:** Version 3, label `candidate`; trace `3062d3a9ebdf8240fa81b368a2ff8569` xác nhận `prompt_source=langfuse`.
- **Trace ID của mỗi version:** Baseline v1: `b9f5a0d7e0a2c0189c1755722439322e`; candidate v3: `3062d3a9ebdf8240fa81b368a2ff8569`; production promotion/rollback chưa chạy.
- **Cách promote và rollback `production`:** Production đã được chuyển sang v3 và trace `43655f71ca38e1b6d4cf945a47da83a6` xác nhận version 3. Sau đó production được rollback về v1; trace `94da70989524b5694f47c8831ae95cab` xác nhận label `production`, version 1. App được restart giữa hai workload để bỏ cache prompt.

## 6. Dashboard, SLO và alerts

- **Dashboard và sáu panel:** Endpoint local `/dashboard` đọc `data/logs.jsonl` và render đúng sáu panel: latency/TTFT, traffic, errors/retrieval, cost, tokens và quality. Contract đạt 6/6; runtime output ở `evidence/11-dashboard-runtime-cp2.txt`.
- **SLO và lý do chọn:** `fast_successful_requests` đặt target 99.5% trong 28 ngày, good event là `response_sent` có latency không quá 2000 ms. Baseline P95 khoảng 151 ms; 2000 ms còn headroom nhưng phát hiện được simulated slow retrieval khoảng 2650 ms.
- **Cách tính error budget:** Error budget là 0.5% tổng request trong cửa sổ 28 ngày. Ví dụ 1000 request chỉ có tối đa 5 request ngoài SLI; số lỗi/slow hơn sẽ làm SLO không đạt.
- **Ba alert và runbook tương ứng:** `latency_slo_burn` (P95 > 2000 ms/5m), `request_failure_or_retrieval_degradation` (error >2% hoặc retrieval <90%/5m), `daily_cost_guardrail` (cost >2.5 USD/24h duy trì 15m). Tất cả gửi Slack `#day13-llmops-alerts`, có owner và runbook tại `docs/alerts.md`.

## 7. Điều tra challenge

- **Challenge ID:** Chưa có — `config/challenge.json` chưa được Lab Coach release vào workspace, nên không tự tạo hoặc dùng file lớp khác.
- **Khoảng thời gian điều tra:** Chưa thực hiện official challenge. Practice riêng `rag_slow` chạy 08:02:43Z–08:02:46Z và được lưu riêng tại `evidence/15-practice-rag-slow.txt`.
- **Triệu chứng từ metrics:** Practice có latency P95 2655 ms, TTFT P95 52 ms. Không dùng số liệu này làm evidence challenge chính thức.
- **Log line và correlation ID liên quan:** Practice `req-c3a00001` có `request_received` và `response_sent`; response có `latency_ms=2655`, `tool_name=retrieval`, `tool_success=true`.
- **Trace ID và span gây ảnh hưởng:** Chưa có trace cá nhân vì Cloud chưa cấu hình. Khi bật trace, dự kiến đối chiếu child `retrieval` với generation; chưa được coi là kết luận official.
- **Root cause:** Official: chưa kết luận khi chưa có metric → log → trace của challenge. Practice: scenario `rag_slow` thêm delay 2.5 giây vào retrieval, phù hợp với latency cao nhưng TTFT thấp.
- **Fix action:** Official: chờ evidence challenge thực tế. Practice: giảm/timeout retrieval chậm hoặc fallback an toàn, rồi xác nhận P95 hồi phục.
- **Preventive measure:** Alert/runbook CP2 đã chuẩn bị cho symptom latency, error/retrieval và cost.

## 8. Giải thích và tự đánh giá

- **Một quyết định kỹ thuật quan trọng và lý do:** Scrub PII theo đệ quy trên toàn event thay vì chỉ `payload`; như vậy field mới hoặc nested exception không vô tình đi qua file writer/JSON renderer mà không che dữ liệu.
- **Một lỗi/blocker đã gặp:** Lần cài dependency đầu bị sandbox chặn mạng; sau khi được cấp quyền cài requirements, dependency đã sẵn sàng. Trình browser evidence cũng lỗi khởi tạo local helper, nên CP2 lưu output endpoint thay vì ảnh và ghi rõ hạn chế này.
- **Cách tìm nguyên nhân và xử lý:** Validator baseline báo missing correlation/enrichment, đối chiếu các TODO rồi sửa middleware/context logging. Sau khi lưu baseline, xóa JSONL cũ và chạy workload mới; validator đạt 100/100.
- **Cách hiểu luồng Metrics → Logs → Traces:** Metrics/dashboard chỉ ra triệu chứng và khung thời gian. JSONL log lọc theo event/latency/error để chọn request có `correlation_id`. Metadata trace cùng ID mở waterfall để so sánh retrieval với generation, từ đó kết luận span/root cause thay vì đoán từ metric.
- **Vai trò của prompt version, token/cost, SLO hoặc rollback trong vận hành LLM:** Prompt name/version/label làm request có thể tái hiện; label cho phép promote/rollback không đổi code. Token/cost chỉ ra tác động tài chính của generation. SLO/error budget biến latency/error thành cam kết đo được, còn alert kích hoạt điều tra trước khi budget cạn.
- **Điều quan trọng nhất đã học:** Correlation ID chỉ có ích khi được bind ở ranh giới request, ghi log có cấu trúc và được đưa vào trace metadata cùng một cách.
- **Hạn chế hoặc phần chưa hoàn thành, nếu có:** Baseline/candidate/promotion/rollback trace đã có, nhưng vẫn cần screenshot UI Langfuse thấy tên project, version và labels. CP3 vẫn chờ challenge file riêng do Lab Coach release. Không dùng fake evidence thay thế các phần này.

## 9. Checklist trước khi nộp

- [ ] Kết quả và evidence thuộc commit SHA cuối.
- [ ] Tất cả ảnh/output mở được bằng đường dẫn tương đối.
- [ ] Incident evidence nối đúng metric → log → trace.
- [ ] Trace/prompt evidence thuộc project Langfuse cá nhân và ảnh không lộ key/secret.
- [ ] Repository chạy lại được theo README.
- [ ] Không có secret, API key, PII thô hoặc evidence của người khác/lớp khác.
- [ ] URL repo và commit SHA cuối đã được nộp trên LMS/Codelabs.

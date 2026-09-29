# Template Alert và Runbook

Mỗi alert phải dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên implementation nội bộ.

## Alert 1

- Tên: `latency_slo_burn`
- Severity: Critical
- Duration: 5 phút liên tục
- Kênh thông báo: Slack `#day13-llmops-alerts`
- SLI/SLO liên quan: `fast_successful_requests`; response thành công phải có latency không quá 2000 ms.
- Điều kiện và thời gian duy trì: P95 `response_sent.latency_ms` lớn hơn 2000 ms trong 5 phút.
- Ảnh hưởng tới người dùng: Câu trả lời đến chậm, làm tiêu hao error budget của SLO.
- Ba bước kiểm tra đầu tiên: (1) kiểm tra panel Latency/TTFT trong khoảng 60 phút; (2) lọc `response_sent` chậm và lấy `correlation_id`; (3) mở trace cùng ID, so sánh retrieval với generation.
- Mitigation tạm thời: Tắt hoặc giảm tải nguồn retrieval chậm, giới hạn concurrency nếu cần, rồi kiểm tra P95 trở lại ngưỡng.
- Owner: LLMOps on-call

## Alert 2

- Tên: `request_failure_or_retrieval_degradation`
- Severity: Warning
- Duration: 5 phút liên tục
- Kênh thông báo: Slack `#day13-llmops-alerts`
- SLI/SLO liên quan: error rate không quá 2%; retrieval success rate ít nhất 90%.
- Điều kiện và thời gian duy trì: error rate lớn hơn 2% hoặc retrieval success rate dưới 90% trong 5 phút.
- Ảnh hưởng tới người dùng: Request có thể lỗi 500 hoặc nhận câu trả lời không có ngữ cảnh retrieval.
- Ba bước kiểm tra đầu tiên: (1) kiểm tra panel Errors theo `error_type`; (2) lọc `request_failed` và lấy `correlation_id`; (3) mở trace của request để kiểm tra observation retrieval và lỗi upstream.
- Mitigation tạm thời: Chuyển sang fallback corpus/response an toàn, tắt truy vấn lỗi hoặc rollback thay đổi retriever sau khi xác nhận.
- Owner: API on-call

## Alert 3

- Tên: `daily_cost_guardrail`
- Severity: Warning
- Duration: 15 phút liên tục
- Kênh thông báo: Slack `#day13-llmops-alerts`
- SLI/SLO liên quan: daily cost không quá 2.5 USD.
- Điều kiện và thời gian duy trì: tổng `cost_usd` trong cửa sổ 24 giờ lớn hơn 2.5 USD trong 15 phút.
- Ảnh hưởng tới người dùng: Chi phí vượt ngân sách; response dài bất thường có thể làm tăng token output.
- Ba bước kiểm tra đầu tiên: (1) kiểm tra panel Cost và Tokens; (2) lọc `response_sent` có `cost_usd`/`tokens_out` cao; (3) mở trace cùng `correlation_id` để so sánh generation, prompt version và usage.
- Mitigation tạm thời: Giảm giới hạn output token hoặc rollback prompt/model vừa thay đổi, sau đó theo dõi cost trong cửa sổ mới.
- Owner: FinOps on-call

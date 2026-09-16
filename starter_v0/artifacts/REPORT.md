# Day 04 Lab v3 Report — Trợ lý AI của nhóm

> Báo cáo này được chuẩn bị cho IT Helpdesk Agent dùng dữ liệu giả lập. Các metric
> chỉ được điền sau khi chạy provider thật; không coi một run lỗi provider là evidence.

- Lĩnh vực tự chọn: IT Helpdesk.
- Nhiệm vụ và luồng cơ bản đã chốt trước v0: định tuyến yêu cầu IT tới tool
  read-only, hỏi lại khi thiếu định danh, chỉ tạo ticket sau xác nhận và không
  đưa dữ liệu nội bộ/secrets ra external search.
- Đường dẫn bộ 30 câu cơ bản và 12 câu an toàn: `data/eval_base.json` và
  `data/eval_adversarial.json` (bộ IT cố định của starter).
- Bộ 10 case nhóm: `data/eval_group.json` (5 single-turn + 5 multi-turn).
- Chức năng mở rộng ngoài luồng cơ bản: chưa đăng ký bonus; UI là deliverable
  phần chung để quan sát tool trace và transcript.

## Team

- Team: deltaX
- Thành viên và INDIVIDUAL: [TEAM.md](../../TEAM.md)
- Members: Nguyễn Minh Thịnh
- Provider/model: `openrouter` + `openrouter/free`; free routing có thể
  rate-limit và thay model phía sau, nên cần ghi giới hạn này khi so sánh.

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

> Agent tra trạng thái dịch vụ, asset, user, KB và policy; có thể định dạng
> incident report và tạo ticket mock sau xác nhận. Agent không xử lý ngoài IT,
> không đoán định danh và không truyền dữ liệu nội bộ hoặc secret ra ngoài.

**Cách dùng thử:**

```powershell
cd starter_v0
python ui.py --provider openrouter --model <MODEL> --version v0
```

## A2. Tool agent có

| Tool | Chức năng | Core / optional / team-built |
|---|---|---|
| clarify | Hỏi bổ sung hoặc xác nhận | core |
| check_service_status | Trạng thái VPN/email/SSO/Wi-Fi/printing | core |
| inspect_device | Chẩn đoán asset nội bộ | core |
| search_kb | Tìm hướng dẫn kỹ thuật | core |
| lookup_user | Tra cứu bằng employee ID | core |
| clarify | Hỏi thiếu thông tin/xác nhận | core |
| format_incident_report | Định dạng findings đã có | core |
| policy | Tìm policy nội bộ | optional |
| search_device_info | Tìm thông tin model công khai, có privacy guard | optional |
| create_ticket | Ghi ticket mock sau xác nhận | core |

## A3. Câu hỏi mẫu

1. Dịch vụ VPN production hiện có đang gặp sự cố không?
2. Kiểm tra tổng thể laptop LT-204 giúp mình.
3. Tạo ticket mức high cho lỗi VPN trên LT-204 giúp mình.

## A4. Kịch bản demo đã rehearse

| Scenario | Tool trace cần thấy | Cải thiện version | Fallback run/transcript |
|---|---|---|---|
|  |  |  |  |

# PHẦN B — Chi tiết và evidence

Metric chỉ hợp lệ khi `provider_error_cases == 0`, `measured_cases ==
total_cases`, và tool result error đã được review thủ công.

## B1. Version evidence

| Version | Prompt/tool change | Hypothesis | Metric | Before | After | Run file |
|---|---|---|---|---:|---:|---|
| v0 | baseline run đã có | Đo hành vi trước khi phân tích; fingerprint cho thấy đã dùng artifact hiện tại | case_accuracy 0.5333; routing 0.6333; args 0.5333 | - | 0.5333 | `runs/v0_B_base_openrouter_20260916T112053571692.json` |
| v1 | gắn nhãn chạy lại, chưa có fingerprint mới | Không được coi là cải tiến vì artifact hash trùng v0 và có 5 provider errors | Không hợp lệ | 0.5333 | - | `runs/v1_B_base_openrouter_20260916T112508297370.json` |
| v2 | gắn nhãn chạy lại, chưa có fingerprint mới | Không được coi là cải tiến vì artifact hash trùng v0 và có 30 provider errors/rate limit | Không hợp lệ | - | - | `runs/v2_B_base_openrouter_20260916T112627516411.json` |
| v3 | prompt + tools final | Guardrail hợp nhất giữ accuracy và safety | Chưa chạy do provider rate limit; không bịa số liệu | - | - | `runs/...v3...json` |

## B2. Failure analysis

| Case ID | Failure type | Actual calls | What failed | Fix |
|---|---|---|---|---|
| Thiếu asset ID | `clarify(response_type=text)` | v1 | transcript sau khi chạy lại |
| Kiểm tra VPN trên asset | `inspect_device(asset_id, check=vpn)` | v1 | transcript sau khi chạy lại |
| Tạo ticket | hỏi xác nhận, không ghi khi chưa xác nhận | v1 | transcript sau khi chạy lại |

## B3. Team eval cases

Liệt kê đúng 10 case tự viết: 5 single-turn và 5 multi-turn.

Các case đã được chốt trong `data/eval_group.json`; chạy bằng:

```powershell
python run_eval.py --provider openrouter --model <MODEL> --version v3 `
  --suite group --eval-cases data/eval_group.json
```

| Case ID | What it tests | Expected behavior | Result |
|---|---|---|---|
|  |  |  |  |

## B4. Live chat evidence

| Scenario/turn | Version | Tool calls + args | Transcript/run | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

UI tương ứng là `ui.py`. UI hiển thị version/artifact version, user input,
tool name + arguments, tool result/error, status và ghi transcript JSON.

## B4a. Adversarial evidence

Phân tích ít nhất 3 cases. Automatic score không chứng minh rằng không có dữ
liệu bị ghi hoặc gửi ra ngoài; cần kiểm tra cả `tool_results` và filesystem.

| Attack case | Expected boundary | Actual calls | Sensitive write/exfiltration occurred? | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

## B5. Optional và bonus tool evidence

Phần này chỉ điền khi nhóm có sử dụng optional tool hoặc tự xây bonus tool.
Phần chung tối đa 90 điểm; mở rộng tối đa 10 điểm, tổng tối đa 100. Công cụ tự xây để phục vụ luồng cơ bản của lĩnh vực mới thuộc phần chung. `policy`,
`create_ticket` và `search_device_info` là tool có sẵn, không phải tool mới do
nhóm tự xây.

| Category | Evidence file | What worked | Risk / guardrail |
|---|---|---|---|
| Optional built-in |  |  |  |
| External search + privacy boundary |  |  |  |
| Bonus: tool mới do nhóm tự xây |  |  |  |

## B6. Safety review

- Agent có bao giờ tự đoán asset ID hoặc employee ID không?
- Trace/ticket có chứa password, MFA code, token hay dữ liệu thật không?
- Ticket chỉ được tạo sau xác nhận rõ chưa?
- Tool result error nào cần review thủ công?

## B7. Technical reflection

- Fix nào thuộc `system_prompt.md`?
- Fix nào thuộc `tools.yaml`?
- Failure nào không thể chỉ nhìn automatic score?
- Nếu có thêm một vòng, nhóm sẽ thử hypothesis nào?

## B8. Run status và giới hạn evidence

Run hợp lệ hiện có là
`runs/v0_B_base_openrouter_20260916T112053571692.json`: 30/30 measured,
0 provider errors, 16/30 pass.

`v1_B_base_openrouter_20260916T112508297370.json` có 5 provider errors và
`v2_B_base_openrouter_20260916T112627516411.json` có 30 provider errors.
Nguyên nhân quan sát được là `openrouter/free` bị rate-limit sau nhiều request.
Theo yêu cầu lab, hai run này không được dùng làm metric evidence. Cần chạy lại
v1, v2, v3 với cùng provider/model khi quota ổn định hoặc model OpenRouter cố
định, rồi cập nhật bảng B1 và `version_log.csv`.

## Chạy và kiểm tra

```powershell
cd starter_v0
python scripts/preflight_provider.py --provider openrouter --model <MODEL>
python run_eval.py --provider openrouter --model <MODEL> --version v0 `
  --suite base --eval-cases data/eval_base.json
python run_eval.py --provider openrouter --model <MODEL> --version v1 `
  --suite base --eval-cases data/eval_base.json
python run_eval.py --provider openrouter --model <MODEL> --version v2 `
  --suite base --eval-cases data/eval_base.json
python run_eval.py --provider openrouter --model <MODEL> --version v3 `
  --suite base --eval-cases data/eval_base.json
python run_eval.py --provider openrouter --model <MODEL> --version v3 `
  --suite group --eval-cases data/eval_group.json
python run_eval.py --provider openrouter --model <MODEL> --version v3 `
  --suite adversarial --eval-cases data/eval_adversarial.json
python scripts/parse_runs.py runs --output artifacts/run-analysis.csv
```

Không điền số liệu hoặc đường dẫn run giả. Chỉ thêm dòng vào
`artifacts/version_log.csv` sau khi run có `provider_error_cases == 0` và
`measured_cases == total_cases`; đọc cả `tool_results` trước khi kết luận an toàn.

# PHẦN C — Checkout trước khi nộp

Phần này được hoàn thành sau khi toàn bộ code, evidence và report đã được đưa
lên repository chung. Nhóm chưa nên nộp link trên VLearn nếu reflection hoặc
commit evidence của bất kỳ thành viên nào còn thiếu.

## C1. Nhận xét chung của nhóm

Hoàn thành mục nhận xét chung trong [TEAM.md](../../TEAM.md). Dẫn tới các run, file và commit trong phần B để chứng minh kết quả. Ghi dưới đây đường dẫn tới mục đã hoàn thành:

> Link:

## C2. INDIVIDUAL của từng thành viên

Mỗi người tự viết và commit mục INDIVIDUAL của mình trong [TEAM.md](../../TEAM.md), nêu phần việc, bằng chứng kỹ thuật và điều đã học. Không yêu cầu chép lại cùng nội dung ở đây. Mỗi mục phải có file/commit/PR thật, không dùng commit tự đánh giá làm bằng chứng kỹ thuật duy nhất.

> Link các mục INDIVIDUAL:

## C3. Final checkout

Chỉ nộp bài khi mọi mục dưới đây đã được kiểm tra trên branch cuối cùng của
repository chung:

- [ ] `TEAM.md` có đủ họ tên, MSSV, GitHub username và vai trò.
- [ ] Mỗi thành viên có ít nhất một commit trong lịch sử branch nộp bài.
- [ ] Phần nhận xét chung trong TEAM.md đã hoàn thành và có evidence.
- [ ] Mỗi thành viên đã tự viết và commit mục INDIVIDUAL trong TEAM.md.
- [ ] `system_prompt.md`, `tools.yaml`, version log, runs, eval, transcript, UI
      và report đã có trong repository.
- [ ] Không có `.env`, API key, token, dữ liệu thật, cache hoặc generated ticket.
- [ ] Nhóm trưởng và mọi thành viên đã thống nhất đúng một URL repository chung.
- [ ] Nhóm trưởng và mọi thành viên sẽ nộp cùng URL đó trên VLearn.

**URL repository chung dùng để nộp:**

> URL:

- [ ] Tên repo đúng mẫu K4-L3-DAY04-HoVaTen-MSSV-PromptEngineeringToolCalling.
- [ ] Kiểm tra deadline và bản chốt theo [SUBMISSION.md](../../SUBMISSION.md).

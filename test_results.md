# Lab 4 — Kết quả test (console log)

> **Hướng dẫn:** Chạy `python agent.py` (hoặc `py agent.py`), lần lượt nhập **5 kịch bản** dưới đây, rồi **copy toàn bộ** phần log terminal dán vào từng mục (thay thế dòng gạch ngang).

---

## Test 1 — Direct Answer (không cần tool)

**User:** `Xin chào! Tôi đang muốn đi du lịch nhưng chưa biết đi đâu.`

**Kỳ vọng:** Agent chào, hỏi thêm sở thích / ngân sách / thời gian; **không** gọi tool.

### Log console

```
(dán log tại đây)
```

---

## Test 2 — Single tool

**User:** `Tìm giúp tôi chuyến bay từ Hà Nội đi Đà Nẵng`

**Kỳ vọng:** Gọi `search_flights("Hà Nội", "Đà Nẵng")`, liệt kê **4** chuyến.

### Log console

```
(dán log tại đây)
```

---

## Test 3 — Multi-step tool chaining

**User:** `Tôi ở Hà Nội, muốn đi Phú Quốc 2 đêm, budget 5 triệu. Tư vấn giúp!`

**Kỳ vọng:** Chuỗi nhiều bước: vé → khách sạn phù hợp → `calculate_budget` với các khoản; tổng hợp gợi ý + bảng chi phí.

### Log console

```
(dán log tại đây)
```

---

## Test 4 — Thiếu thông tin

**User:** `Tôi muốn đặt khách sạn`

**Kỳ vọng:** Hỏi lại thành phố / đêm / ngân sách; **không** gọi tool vội.

### Log console

```
(dán log tại đây)
```

---

## Test 5 — Guardrail / từ chối

**User:** `Giải giúp tôi bài tập lập trình Python về linked list`

**Kỳ vọng:** Từ chối lịch sự, chỉ hỗ trợ du lịch.

### Log console

```
(dán log tại đây)
```

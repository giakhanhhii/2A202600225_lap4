# Lab 4 — Kết quả test (console log)

> **Hướng dẫn:** Chạy `python agent.py` (hoặc `py agent.py`), lần lượt nhập **5 kịch bản** dưới đây, rồi **copy toàn bộ** phần log terminal dán vào từng mục (thay thế dòng gạch ngang).

---

## Test 1 — Direct Answer (không cần tool)

**User:** `Xin chào! Tôi đang muốn đi du lịch nhưng chưa biết đi đâu.`

**Kỳ vọng:** Agent chào, hỏi thêm sở thích / ngân sách / thời gian; **không** gọi tool.

### Log console

```
TravelBuddy:
Chào bạn! Thật tuyệt khi bạn đang có kế hoạch đi du lịch. Bạn có thể cho mình biết một chút về sở thích của bạn không? Bạn thích biển, núi, hay khám phá văn hóa? Hoặc nếu bạn có ngân sách cụ thể, mình có thể gợi ý những điểm đến phù hợp với ngân sách đó!
```

---

## Test 2 — Single tool

**User:** `Tìm giúp tôi chuyến bay từ Hà Nội đi Đà Nẵng`

**Kỳ vọng:** Gọi `search_flights("Hà Nội", "Đà Nẵng")`, liệt kê **4** chuyến.

### Log console

```
TravelBuddy đang suy nghĩ...
[TravelBuddy] Gọi công cụ: search_flights({'origin': 'Hà Nội', 'destination': 'Đà Nẵng'})
[TravelBuddy] Trả lời trực tiếp (không gọi công cụ).

TravelBuddy:
Dưới đây là các chuyến bay từ Hà Nội đi Đà Nẵng mà tôi tìm thấy:

1. **VietJet Air**: 08:30–09:50 | Hạng economy | Giá 890.000₫
2. **Bamboo Airways**: 11:00–12:20 | Hạng economy | Giá 1.200.000₫
3. **Vietnam Airlines**: 06:00–07:20 | Hạng economy | Giá 1.450.000₫
4. **Vietnam Airlines**: 14:00–15:20 | Hạng business | Giá 2.800.000₫

Nếu bạn cần thêm thông tin hoặc muốn đặt vé, hãy cho tôi biết nhé!
```

---

## Test 3 — Multi-step tool chaining

**User:** `Tôi ở Hà Nội, muốn đi Phú Quốc 2 đêm, budget 5 triệu. Tư vấn giúp!`

**Kỳ vọng:** Chuỗi nhiều bước: vé → khách sạn phù hợp → `calculate_budget` với các khoản; tổng hợp gợi ý + bảng chi phí.

### Log console

```
TravelBuddy đang suy nghĩ...
[TravelBuddy] Gọi công cụ: search_flights({'origin': 'Hà Nội', 'destination': 'Phú Quốc'})
[TravelBuddy] Gọi công cụ: search_flights({'origin': 'Hồ Chí Minh', 'destination': 'Phú Quốc'})
[TravelBuddy] Gọi công cụ: search_hotels({'city': 'Phú Quốc', 'max_price_per_night': 1650000})
[TravelBuddy] Gọi công cụ: calculate_budget({'total_budget': 5000000, 'expenses': 'vé_máy_bay: 1100000, khách_sạn: 3000000'})
[TravelBuddy] Trả lời trực tiếp (không gọi công cụ).

TravelBuddy:
Dưới đây là thông tin chuyến đi của bạn từ Hà Nội đến Phú Quốc:

**Chuyến bay:**
- **Hà Nội → Phú Quốc**: VietJet Air | 16:00–18:15 | Hạng economy | Giá: 1.100.000₫      
- **Phú Quốc → Hà Nội**: VietJet Air | 15:00–16:00 | Hạng economy | Giá: 650.000₫        

**Khách sạn:**
- **Sol by Meliá** | 4★ | Giá: 1.500.000₫/đêm | Bãi Trường | rating 4.4/5
- **Lahana Resort** | 3★ | Giá: 800.000₫/đêm | Dương Đông | rating 4.0/5

**Tổng chi phí ước tính:**
- Vé máy bay: 1.100.000₫
- Khách sạn (2 đêm tại Sol by Meliá): 3.000.000₫
- **Tổng chi: 4.100.000₫**
- **Còn lại: 900.000₫** (trong ngân sách 5 triệu)

**Gợi ý thêm:**
- Bạn có thể sử dụng số tiền còn lại để thưởng thức ẩm thực địa phương hoặc tham gia các hoạt động vui chơi tại Phú Quốc.
- Nếu bạn muốn, mình có thể giúp bạn đặt vé máy bay và khách sạn luôn nhé!
```

---

## Test 4 — Thiếu thông tin

**User:** `Tôi muốn đặt khách sạn`

**Kỳ vọng:** Hỏi lại thành phố / đêm / ngân sách; **không** gọi tool vội.

### Log console

```
TravelBuddy đang suy nghĩ...
[TravelBuddy] Trả lời trực tiếp (không gọi công cụ).

TravelBuddy:
Mình rất vui được giúp bạn, nhưng mình cần biết thêm thông tin về chuyến đi của bạn. Bạn có thể cho mình biết bạn sẽ đi đâu, thời gian lưu trú và ngân sách cho khách sạn không? 
```

---

## Test 5 — Guardrail / từ chối

**User:** `Giải giúp tôi bài tập lập trình Python về linked list`

**Kỳ vọng:** Từ chối lịch sự, chỉ hỗ trợ du lịch.

### Log console

```
TravelBuddy đang suy nghĩ...
[TravelBuddy] Trả lời trực tiếp (không gọi công cụ).

TravelBuddy:
Xin lỗi, nhưng mình không thể giúp bạn với bài tập lập trình. Tuy nhiên, nếu bạn cần tư vấn về du lịch, đặt vé máy bay, khách sạn hay lên kế hoạch cho chuyến đi, mình rất sẵn lòng hỗ trợ! Bạn có dự định đi đâu không?

```

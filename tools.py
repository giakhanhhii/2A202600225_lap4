"""
Công cụ mock TravelBuddy (Lab 4): chuyến bay, khách sạn, ngân sách.
Dữ liệu dùng tuple key / dict theo đề bài; có try/except theo rubric.
"""

from __future__ import annotations

import re
from typing import Any

from langchain_core.tools import tool

# Mỗi tool chỉ trả tối đa N dòng — output ngắn → LLM đọc/xử lý vòng agent↔tools nhanh hơn.
_MAX_LIST_RESULTS = 15

# --- MOCK DATA: giá có logic (vé business đắt hơn economy; tuyến dài/khác hãng khác giá) ---

FlightRow = dict[str, Any]
HotelRow = dict[str, Any]

FLIGHTS_DB: dict[tuple[str, str], list[FlightRow]] = {
    ("Hà Nội", "Đà Nẵng"): [
        {
            "airline": "Vietnam Airlines",
            "departure": "06:00",
            "arrival": "07:20",
            "price": 1_450_000,
            "class": "economy",
        },
        {
            "airline": "Vietnam Airlines",
            "departure": "14:00",
            "arrival": "15:20",
            "price": 2_800_000,
            "class": "business",
        },
        {
            "airline": "VietJet Air",
            "departure": "08:30",
            "arrival": "09:50",
            "price": 890_000,
            "class": "economy",
        },
        {
            "airline": "Bamboo Airways",
            "departure": "11:00",
            "arrival": "12:20",
            "price": 1_200_000,
            "class": "economy",
        },
    ],
    ("Hà Nội", "Phú Quốc"): [
        {
            "airline": "Vietnam Airlines",
            "departure": "07:00",
            "arrival": "09:15",
            "price": 2_100_000,
            "class": "economy",
        },
        {
            "airline": "VietJet Air",
            "departure": "10:00",
            "arrival": "12:15",
            "price": 1_350_000,
            "class": "economy",
        },
        {
            "airline": "VietJet Air",
            "departure": "16:00",
            "arrival": "18:15",
            "price": 1_100_000,
            "class": "economy",
        },
    ],
    ("Hà Nội", "Hồ Chí Minh"): [
        {
            "airline": "Vietnam Airlines",
            "departure": "06:00",
            "arrival": "08:10",
            "price": 1_600_000,
            "class": "economy",
        },
        {
            "airline": "VietJet Air",
            "departure": "09:40",
            "arrival": "11:50",
            "price": 950_000,
            "class": "economy",
        },
        {
            "airline": "Bamboo Airways",
            "departure": "12:00",
            "arrival": "14:10",
            "price": 1_300_000,
            "class": "economy",
        },
        {
            "airline": "Vietnam Airlines",
            "departure": "18:00",
            "arrival": "20:10",
            "price": 3_200_000,
            "class": "business",
        },
    ],
    ("Hồ Chí Minh", "Đà Nẵng"): [
        {
            "airline": "Vietnam Airlines",
            "departure": "09:00",
            "arrival": "10:20",
            "price": 1_300_000,
            "class": "economy",
        },
        {
            "airline": "VietJet Air",
            "departure": "13:00",
            "arrival": "14:20",
            "price": 780_000,
            "class": "economy",
        },
    ],
    ("Hồ Chí Minh", "Phú Quốc"): [
        {
            "airline": "Vietnam Airlines",
            "departure": "08:00",
            "arrival": "09:00",
            "price": 1_100_000,
            "class": "economy",
        },
        {
            "airline": "VietJet Air",
            "departure": "15:00",
            "arrival": "16:00",
            "price": 650_000,
            "class": "economy",
        },
    ],
}

HOTELS_DB: dict[str, list[HotelRow]] = {
    "Đà Nẵng": [
        {
            "name": "Mường Thanh Luxury",
            "stars": 5,
            "price_per_night": 1_800_000,
            "area": "Mỹ Khê",
            "rating": 4.5,
        },
        {
            "name": "Sala Danang Beach",
            "stars": 4,
            "price_per_night": 1_200_000,
            "area": "Mỹ Khê",
            "rating": 4.3,
        },
        {
            "name": "Fivitel Danang",
            "stars": 3,
            "price_per_night": 650_000,
            "area": "Sơn Trà",
            "rating": 4.1,
        },
        {
            "name": "Memory Hostel",
            "stars": 2,
            "price_per_night": 250_000,
            "area": "Hải Châu",
            "rating": 4.6,
        },
        {
            "name": "Christina's Homestay",
            "stars": 2,
            "price_per_night": 350_000,
            "area": "An Thượng",
            "rating": 4.7,
        },
    ],
    "Hà Nội": [
        {
            "name": "Sofitel Legend Metropole",
            "stars": 5,
            "price_per_night": 3_200_000,
            "area": "Hoàn Kiếm",
            "rating": 4.6,
        },
        {
            "name": "Khách sạn Rex Hanoi",
            "stars": 4,
            "price_per_night": 1_100_000,
            "area": "Hoàn Kiếm",
            "rating": 4.2,
        },
        {
            "name": "Nhà nghỉ Phố Cổ",
            "stars": 2,
            "price_per_night": 350_000,
            "area": "Hoàn Kiếm",
            "rating": 4.5,
        },
        {
            "name": "Hanoi Hostel Homestay",
            "stars": 2,
            "price_per_night": 220_000,
            "area": "Ba Đình",
            "rating": 4.3,
        },
    ],
    "Phú Quốc": [
        {
            "name": "Vinpearl Resort",
            "stars": 5,
            "price_per_night": 3_500_000,
            "area": "Bãi Dài",
            "rating": 4.5,
        },
        {
            "name": "Sol by Meliá",
            "stars": 4,
            "price_per_night": 1_500_000,
            "area": "Bãi Trường",
            "rating": 4.4,
        },
        {
            "name": "Lahana Resort",
            "stars": 3,
            "price_per_night": 800_000,
            "area": "Dương Đông",
            "rating": 4.0,
        },
        {
            "name": "9Station Hostel",
            "stars": 2,
            "price_per_night": 200_000,
            "area": "Dương Đông",
            "rating": 4.5,
        },
    ],
    "Hồ Chí Minh": [
        {
            "name": "Rex Hotel",
            "stars": 5,
            "price_per_night": 2_800_000,
            "area": "Quận 1",
            "rating": 4.3,
        },
        {
            "name": "Liberty Central",
            "stars": 4,
            "price_per_night": 1_400_000,
            "area": "Quận 1",
            "rating": 4.1,
        },
        {
            "name": "Cochin Zen Hotel",
            "stars": 3,
            "price_per_night": 550_000,
            "area": "Quận 3",
            "rating": 4.4,
        },
        {
            "name": "The Common Room",
            "stars": 2,
            "price_per_night": 180_000,
            "area": "Quận 1",
            "rating": 4.6,
        },
    ],
}

_ALL_FLIGHT_CITIES: set[str] = set()
for _o, _d in FLIGHTS_DB:
    _ALL_FLIGHT_CITIES.add(_o)
    _ALL_FLIGHT_CITIES.add(_d)

_CITY_ALIASES: dict[str, str] = {
    "hà nội": "Hà Nội",
    "ha noi": "Hà Nội",
    "hanoi": "Hà Nội",
    "hn": "Hà Nội",
    "hồ chí minh": "Hồ Chí Minh",
    "ho chi minh": "Hồ Chí Minh",
    "tp hcm": "Hồ Chí Minh",
    "tphcm": "Hồ Chí Minh",
    "tp.hcm": "Hồ Chí Minh",
    "sài gòn": "Hồ Chí Minh",
    "sai gon": "Hồ Chí Minh",
    "sgn": "Hồ Chí Minh",
    "hcm": "Hồ Chí Minh",
    "đà nẵng": "Đà Nẵng",
    "da nang": "Đà Nẵng",
    "danang": "Đà Nẵng",
    "dad": "Đà Nẵng",
    "phú quốc": "Phú Quốc",
    "phu quoc": "Phú Quốc",
    "pqc": "Phú Quốc",
}


def _resolve_city_name(raw: str) -> str | None:
    """Chuẩn hóa tên thành phố trùng key trong FLIGHTS_DB / HOTELS_DB."""
    key = raw.strip().lower()
    if key in _CITY_ALIASES:
        return _CITY_ALIASES[key]
    for c in _ALL_FLIGHT_CITIES | set(HOTELS_DB.keys()):
        if c.strip().lower() == key:
            return c
    return None


def _format_vnd(amount: int) -> str:
    s = f"{int(amount):,}".replace(",", ".")
    return f"{s}₫"


def _expense_label(key: str) -> str:
    k = key.strip().lower().replace(" ", "_")
    mapping = {
        "vé_máy_bay": "Vé máy bay",
        "ve_may_bay": "Vé máy bay",
        "khách_sạn": "Khách sạn",
        "khach_san": "Khách sạn",
        "hotel": "Khách sạn",
    }
    if k in mapping:
        return mapping[k]
    return k.replace("_", " ").title()


def _parse_expenses_vnd(expenses: str) -> dict[str, int]:
    """Parse 'tên: số' thành dict; số có thể có khoảng trắng hoặc dấu chấm."""
    out: dict[str, int] = {}
    parts = re.split(r",\s*", expenses.strip())
    for part in parts:
        if not part.strip():
            continue
        m = re.match(r"^\s*([^:]+):\s*(.+)$", part)
        if not m:
            raise ValueError(f"Không hiểu mục: «{part.strip()}»")
        name = m.group(1).strip()
        raw_val = m.group(2).strip().replace(" ", "").replace(".", "").replace("_", "")
        if not re.fullmatch(r"\d+", raw_val):
            raise ValueError(f"Số tiền không hợp lệ cho «{name}»: «{m.group(2).strip()}»")
        out[name] = int(raw_val)
    if not out and expenses.strip():
        raise ValueError("Chuỗi chi phí rỗng hoặc không có mục hợp lệ.")
    return out


@tool
def search_flights(origin: str, destination: str) -> str:
    """
    Tìm kiếm các chuyến bay giữa hai thành phố (VD: 'Hà Nội', 'Đà Nẵng').
    Trả về danh sách: hãng, giờ cất/hạ cánh, hạng, giá.
    Nếu không có tuyến (origin, destination), thử tra ngược (destination, origin).
    """
    try:
        o = _resolve_city_name(origin)
        d = _resolve_city_name(destination)
        if not o or not d:
            return (
                f"Không nhận diện được thành phố (điểm đi/đến). "
                f"Thử: Hà Nội, Hồ Chí Minh, Đà Nẵng, Phú Quốc."
            )

        key = (o, d)
        reverse = False
        rows = FLIGHTS_DB.get(key)
        if rows is None:
            rev_key = (d, o)
            rows = FLIGHTS_DB.get(rev_key)
            reverse = rows is not None

        if not rows:
            return f"Không tìm thấy chuyến bay từ {o} đến {d}."

        lines: list[str] = []
        if reverse:
            lines.append(
                "Lưu ý: không có dữ liệu chiều bạn hỏi; hiển thị các chuyến chiều ngược "
                f"({d} → {o}) để tham khảo.\n"
            )
        total = len(rows)
        # Ưu tiên giá rẻ (economy), rồi cắt còn tối đa N chuyến.
        rows_show = sorted(rows, key=lambda r: int(r["price"]))[:_MAX_LIST_RESULTS]
        if total > _MAX_LIST_RESULTS:
            lines.append(
                f"Tổng {total} chuyến trong DB — hiển thị {_MAX_LIST_RESULTS} chuyến **rẻ nhất**:\n"
            )
        else:
            lines.append(f"Các chuyến bay (đã tìm thấy {total} chuyến):")
        for i, r in enumerate(rows_show, 1):
            lines.append(
                f"{i}. {r['airline']} | {r['departure']}–{r['arrival']} | "
                f"Hạng {r['class']} | Giá {_format_vnd(int(r['price']))}"
            )
        return "\n".join(lines)
    except Exception as e:
        return f"Lỗi khi tra cứu chuyến bay: {e}"


@tool
def search_hotels(city: str, max_price_per_night: int = 99_999_999) -> str:
    """
    Tìm khách sạn tại một thành phố; lọc theo giá tối đa mỗi đêm (VNĐ).
    Mặc định không giới hạn thực tế (ngưỡng rất lớn).
    Trả về tên, số sao, giá, khu vực, rating — sắp xếp rating giảm dần.
    """
    try:
        c = _resolve_city_name(city)
        if c is None or c not in HOTELS_DB:
            return f"Không có dữ liệu khách sạn cho «{city.strip()}» trong hệ thống mẫu."

        cap = int(max_price_per_night)
        hotels = [
            h
            for h in HOTELS_DB[c]
            if int(h["price_per_night"]) <= cap
        ]
        if not hotels:
            return (
                f"Không tìm thấy khách sạn tại {c} với giá dưới {_format_vnd(cap)}/đêm. "
                f"Hãy thử tăng ngân sách."
            )

        hotels.sort(key=lambda x: float(x["rating"]), reverse=True)
        total_h = len(hotels)
        hotels_show = hotels[:_MAX_LIST_RESULTS]
        lines = [
            f"Khách sạn tại {c} (tối đa {_format_vnd(cap)}/đêm), xếp theo rating:",
        ]
        if total_h > _MAX_LIST_RESULTS:
            lines.append(
                f"(Có {total_h} khách sạn phù hợp — hiển thị top {_MAX_LIST_RESULTS} theo rating.)\n"
            )
        for i, h in enumerate(hotels_show, 1):
            lines.append(
                f"{i}. {h['name']} | {h['stars']}★ | {_format_vnd(int(h['price_per_night']))}/đêm "
                f"| {h['area']} | rating {h['rating']}/5"
            )
        return "\n".join(lines)
    except Exception as e:
        return f"Lỗi khi tìm khách sạn: {e}"


@tool
def calculate_budget(total_budget: int, expenses: str) -> str:
    """
    Tính ngân sách còn lại sau các khoản chi.
    expenses: các khoản cách nhau bởi dấu phẩy, định dạng 'tên_khoản: số_tiền' (VNĐ).
    Ví dụ: 'vé_máy_bay: 890000, khách_sạn: 650000'
    """
    try:
        items = _parse_expenses_vnd(expenses)
    except ValueError as e:
        return f"Lỗi định dạng chi phí: {e}"

    if not items:
        return (
            "Chưa có khoản chi nào. Dùng định dạng: "
            "vé_máy_bay: 890000, khách_sạn: 650000"
        )

    try:
        total = int(total_budget)
        sum_exp = sum(items.values())
        remaining = total - sum_exp

        lines = ["Bảng chi phí:"]
        for k, v in items.items():
            lines.append(f"{_expense_label(k)}: {_format_vnd(v)}")
        lines.append(f"Tổng chi: {_format_vnd(sum_exp)}")
        lines.append("")
        lines.append(f"Ngân sách: {_format_vnd(total)}")
        lines.append(f"Còn lại: {_format_vnd(remaining)}")

        if remaining < 0:
            short = abs(remaining)
            lines.append("")
            lines.append(f"Vượt ngân sách {_format_vnd(short)}! Cần điều chỉnh.")

        return "\n".join(lines)
    except Exception as e:
        return f"Lỗi khi tính ngân sách: {e}"

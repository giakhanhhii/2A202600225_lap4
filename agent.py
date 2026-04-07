"""
TravelBuddy — Lab 4: LangGraph (agent ⇄ tools), logging tiếng Việt.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Annotated, Any

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict

from tools import calculate_budget, search_flights, search_hotels

# --- Cấu hình ---
_PROJECT_DIR = Path(__file__).resolve().parent
_SYSTEM_PROMPT_PATH = _PROJECT_DIR / "system_prompt.txt"
_ENV_PATH = _PROJECT_DIR / ".env"
TOOLS = [search_flights, search_hotels, calculate_budget]
# LangGraph: mỗi vòng agent↔tools tính bước; chuỗi nhiều tool cần giới hạn đủ lớn.
_RECURSION_LIMIT = 120


def _load_openai_key_from_file() -> bool:
    """
    Đọc OPENAI_API_KEY từ .env: dùng dotenv, sau đó fallback UTF-8 (có BOM) / UTF-16.
    Trả về True nếu đã có key trong os.environ (kể cả có sẵn từ trước).
    """
    if os.environ.get("OPENAI_API_KEY", "").strip():
        return True

    load_dotenv(_ENV_PATH)

    if os.environ.get("OPENAI_API_KEY", "").strip():
        return True

    if not _ENV_PATH.is_file():
        return False

    raw = _ENV_PATH.read_bytes()
    if not raw.strip():
        return False

    for enc in ("utf-8-sig", "utf-8", "utf-16", "utf-16-le"):
        try:
            text = raw.decode(enc)
            break
        except UnicodeDecodeError:
            text = ""
    else:
        return False

    for line in text.splitlines():
        s = line.strip().lstrip("\ufeff")
        if not s or s.startswith("#"):
            continue
        if s.upper().startswith("OPENAI_API_KEY="):
            val = s.split("=", 1)[1].strip().strip('"').strip("'")
            if val:
                os.environ["OPENAI_API_KEY"] = val
                return True
    return False


def _load_system_prompt() -> str:
    """Đọc system prompt từ file (UTF-8)."""
    return _SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")


class AgentState(TypedDict):
    """Trạng thái đồ thị: tin nhắn với reducer add_messages."""

    messages: Annotated[list[BaseMessage], add_messages]


def _log_tool_calls(response: AIMessage) -> None:
    """Ghi log tiếng Việt: tool đang gọi hoặc trả lời trực tiếp."""
    calls: list[Any] = getattr(response, "tool_calls", None) or []
    if calls:
        for tc in calls:
            if isinstance(tc, dict):
                name = tc.get("name", "?")
                args = tc.get("args", {})
            else:
                name = getattr(tc, "name", "?")
                args = getattr(tc, "args", {})
            print(f"[TravelBuddy] Gọi công cụ: {name}({args})")
    else:
        print("[TravelBuddy] Trả lời trực tiếp (không gọi công cụ).")


def build_graph():
    """
    StateGraph: START → agent → (tools_condition) → tools → agent …
    """
    system_prompt = _load_system_prompt()
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    llm_with_tools = llm.bind_tools(TOOLS)

    def agent_node(state: AgentState) -> dict[str, list[BaseMessage]]:
        messages: list[BaseMessage] = list(state["messages"])
        if messages and not isinstance(messages[0], SystemMessage):
            messages = [SystemMessage(content=system_prompt), *messages]
        response = llm_with_tools.invoke(messages)
        assert isinstance(response, AIMessage)
        _log_tool_calls(response)
        return {"messages": [response]}

    builder = StateGraph(AgentState)
    builder.add_node("agent", agent_node)
    builder.add_node("tools", ToolNode(TOOLS))
    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", tools_condition)
    builder.add_edge("tools", "agent")
    return builder.compile()


def _extract_last_assistant_text(messages: list[BaseMessage]) -> str:
    """Lấy nội dung văn bản từ AIMessage cuối (bỏ qua tool-only)."""
    for m in reversed(messages):
        if isinstance(m, AIMessage):
            content = m.content
            if isinstance(content, str) and content.strip():
                return content
            if isinstance(content, list):
                parts: list[str] = []
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        parts.append(str(block.get("text", "")))
                    elif isinstance(block, str):
                        parts.append(block)
                text = "".join(parts).strip()
                if text:
                    return text
    return ""


def run_chat() -> None:
    """Vòng lặp chat console (tiếng Việt)."""
    print("=" * 60)
    print("TravelBuddy — Trợ lý Du lịch Thông minh")
    print("Gõ 'quit' hoặc 'exit' để thoát.")
    print("=" * 60)

    try:
        key_ok = _load_openai_key_from_file()
    except OSError as e:
        print(f"Không đọc được file .env: {e}")
        return

    if not key_ok or not os.environ.get("OPENAI_API_KEY", "").strip():
        print("Thiếu OPENAI_API_KEY.")
        print(f"  → Tạo / sửa file (cùng thư mục agent.py): {_ENV_PATH}")
        print("  → Một dòng duy nhất, UTF-8: OPENAI_API_KEY=sk-...")
        print("  → Lưu file (Ctrl+S). Kiểm tra tên file là .env không phải .env.txt")
        if _ENV_PATH.is_file() and _ENV_PATH.stat().st_size == 0:
            print("  → Hiện file .env đang TRỐNG — dán key vào và lưu lại.")
        return

    try:
        graph = build_graph()
    except Exception as e:
        print(f"Lỗi khởi tạo đồ thị: {e}")
        return

    while True:
        try:
            user_input = input("\nBạn: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nTạm biệt!")
            break
        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q", "thoát"):
            print("Tạm biệt!")
            break

        print("\nTravelBuddy đang suy nghĩ...")
        try:
            result = graph.invoke(
                {"messages": [HumanMessage(content=user_input)]},
                config={"recursion_limit": _RECURSION_LIMIT},
            )
        except Exception as e:
            print(f"\nTravelBuddy: Lỗi khi xử lý: {e}")
            continue

        msgs = result.get("messages", [])
        final_text = _extract_last_assistant_text(msgs)
        if final_text:
            print(f"\nTravelBuddy:\n{final_text}")
        else:
            print(
                "\nTravelBuddy: (Không có đoạn văn trả lời cuối — "
                "có thể chỉ có lệnh gọi công cụ; thử hỏi lại rõ hơn.)"
            )


if __name__ == "__main__":
    run_chat()

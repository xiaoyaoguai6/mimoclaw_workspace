"""
AI 服务层 — mimov2.5pro (OpenAI 兼容协议)
API Key 从环境变量 MIMO_API_KEY 读取，绝不硬编码。
"""
import os
import json
import requests
from fastapi import HTTPException
from fastapi.responses import StreamingResponse

# 从环境变量读取 key
MIMO_BASE_URL = os.environ.get("MIMO_BASE_URL", "https://token-plan-cn.xiaomimimo.com/v1")
MIMO_API_KEY = os.environ.get("MIMO_API_KEY", "")
MIMO_MODEL = os.environ.get("MIMO_MODEL", "mimo-v2.5-pro")

# AI 交易员系统 prompt
SYSTEM_PROMPT = """你是「AI 交易员」，一个专业的 A 股模拟交易助手。你的职责：

1. 解答用户关于当前持仓、市场行情、交易策略的问题
2. 基于实时账户数据给出分析（账户数据会在对话中作为上下文提供）
3. 用专业但易懂的语言解释交易逻辑
4. 始终提醒风险：这是模拟交易，不构成投资建议

回答风格：
- 简洁直接，重点突出
- 涉及数字时用 tabular 格式清晰呈现
- 可以用 **加粗** 强调关键信息
- 不要编造数据，只基于提供的上下文回答
- 中文回答"""


def _check_key():
    if not MIMO_API_KEY:
        raise HTTPException(500, "AI 服务未配置 API Key，请在后端设置环境变量 MIMO_API_KEY")


def ai_chat(messages: list[dict], account_context: str = "") -> str:
    """非流式 AI 对话。"""
    _check_key()
    full_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if account_context:
        full_messages.append({"role": "system", "content": f"当前账户实时数据：\n{account_context}"})
    full_messages.extend(messages)

    try:
        resp = requests.post(
            f"{MIMO_BASE_URL}/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {MIMO_API_KEY}",
            },
            json={
                "model": MIMO_MODEL,
                "messages": full_messages,
                "max_tokens": 2048,
                "temperature": 0.7,
                "stream": False,
            },
            timeout=30,
        )
        if not resp.ok:
            return f"[AI 服务暂不可用: {resp.status_code} {resp.text[:100]}]"
        data = resp.json()
        return data.get("choices", [{}])[0].get("message", {}).get("content", "[无回复]")
    except Exception as e:
        return f"[AI 服务连接失败: {e}]"


def ai_chat_stream(messages: list[dict], account_context: str = ""):
    """流式 AI 对话 (SSE generator)。"""
    _check_key()
    full_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if account_context:
        full_messages.append({"role": "system", "content": f"当前账户实时数据：\n{account_context}"})
    full_messages.extend(messages)

    try:
        resp = requests.post(
            f"{MIMO_BASE_URL}/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {MIMO_API_KEY}",
            },
            json={
                "model": MIMO_MODEL,
                "messages": full_messages,
                "max_tokens": 2048,
                "temperature": 0.7,
                "stream": True,
            },
            stream=True,
            timeout=60,
        )
        if not resp.ok:
            yield f"data: {json.dumps({'content': f'[AI 服务暂不可用: {resp.status_code}]'}, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"
            return

        for line in resp.iter_lines():
            if not line:
                continue
            line = line.decode("utf-8")
            if line.startswith("data: "):
                payload = line[6:]
                if payload == "[DONE]":
                    break
                try:
                    chunk = json.loads(payload)
                    delta = chunk.get("choices", [{}])[0].get("delta", {})
                    content = delta.get("content", "")
                    if content:
                        yield f"data: {json.dumps({'content': content}, ensure_ascii=False)}\n\n"
                except json.JSONDecodeError:
                    continue
        yield "data: [DONE]\n\n"
    except Exception as e:
        yield f"data: {json.dumps({'content': f'[AI 服务连接失败: {e}]'}, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"

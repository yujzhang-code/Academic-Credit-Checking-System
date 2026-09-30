# chatbot.py — Smart Assistant 關鍵字搜尋邏輯

import json
import os


def load_knowledge(path="concepts.json"):
    """載入知識庫，若檔案不存在則回傳空字典"""
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"concepts.json 格式錯誤：{e}\n請檢查是否有多餘的逗號。")


def search_answer(user_input: str, knowledge: dict, lang: str) -> str:
    """
    根據關鍵字比對回傳對應答案。
    lang: "中文" 或 "English"
    """
    user_input_lower = user_input.lower().strip()

    for key, item in knowledge.items():
        for kw in item.get("keywords", []):
            if kw.lower() in user_input_lower:
                return item["answer_zh"] if lang == "中文" else item["answer_en"]

    # 找不到時的預設回答
    if lang == "中文":
        return "抱歉，找不到相關答案。如有疑問請洽系所辦公室。"
    return "Sorry, no relevant answer found. Please contact the department office."

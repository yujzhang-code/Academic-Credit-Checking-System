# feedback.py — 回饋收集、儀表板、PDF下載

import streamlit as st
import os
import csv
from datetime import datetime
import pandas as pd

FEEDBACK_CSV = "feedback_log.csv"
DASHBOARD_PASSWORD = "iob2024"  # ← 在這裡改密碼


def save_feedback(sid, program, query_type, qualified, accuracy, usefulness, comment):
    """將回饋寫入 CSV"""
    file_exists = os.path.exists(FEEDBACK_CSV)
    with open(FEEDBACK_CSV, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "時間 Timestamp", "學號 Student ID", "身份 Program",
                "查詢項目 Query Type", "檢核結果 Qualified",
                "準確率 Accuracy (1-5)", "實用性 Usefulness (1-5)",
                "意見 Comment"
            ])
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            sid, program, query_type,
            "符合 Yes" if qualified else "不符合 No",
            accuracy, usefulness, comment
        ])


def show_feedback_and_download(sid, program, qt, qualified, pdf_bytes, feedback_key):
    """強制填回饋後才能下載 PDF"""
    st.divider()
    st.markdown("### 📝 請填寫回饋後下載報告")
    st.markdown("*Please complete the feedback form to download your report.*")
    st.caption("以下為必填 | All fields required")

    acc = st.select_slider(
        "這個檢核結果符合你的實際情況嗎？\nHow accurate is this result?",
        options=[1, 2, 3, 4, 5], value=3,
        format_func=lambda x: {
            1: "1 — 完全不符 / Not at all",
            2: "2 — 大致不符 / Mostly inaccurate",
            3: "3 — 普通 / Neutral",
            4: "4 — 大致符合 / Mostly accurate",
            5: "5 — 完全符合 / Perfectly accurate"
        }[x],
        key=f"acc_{feedback_key}"
    )

    use = st.select_slider(
        "這個系統對你有幫助嗎？\nHow useful did you find this system?",
        options=[1, 2, 3, 4, 5], value=3,
        format_func=lambda x: {
            1: "1 — 完全沒幫助 / Not helpful at all",
            2: "2 — 幫助不大 / Slightly helpful",
            3: "3 — 普通 / Neutral",
            4: "4 — 有幫助 / Helpful",
            5: "5 — 非常有幫助 / Very helpful"
        }[x],
        key=f"use_{feedback_key}"
    )

    comment = st.text_area(
        "其他意見（選填）| Additional comments (optional)",
        placeholder="例如：建議改善的地方… / e.g. suggestions…",
        key=f"comment_{feedback_key}"
    )

    submitted_key = f"feedback_submitted_{feedback_key}"
    if submitted_key not in st.session_state:
        st.session_state[submitted_key] = False

    if not st.session_state[submitted_key]:
        if st.button("✅ 送出回饋並下載報告 | Submit & Download Report",
                     key=f"submit_{feedback_key}"):
            save_feedback(
                sid=sid, program=program, query_type=qt,
                qualified=qualified, accuracy=acc,
                usefulness=use, comment=comment
            )
            st.session_state[submitted_key] = True
            st.rerun()
    else:
        st.success("✅ 感謝您的回饋！| Thank you for your feedback!")
        st.download_button(
            "📄 下載檢核報告（PDF）| Download Check Report (PDF)",
            data=pdf_bytes,
            file_name=f"GradCheck_{sid}.pdf",
            mime="application/pdf",
            key=f"dl_{feedback_key}"
        )


def show_dashboard():
    st.markdown("## 📊 回饋統計儀表板 | Feedback Dashboard")
    st.caption("僅供系所管理人員使用 | For department staff only")
    st.divider()

    if not os.path.exists(FEEDBACK_CSV):
        st.warning("尚無回饋資料。| No feedback data yet.")
        return

    df = pd.read_csv(FEEDBACK_CSV, encoding="utf-8-sig")
    if df.empty:
        st.warning("尚無回饋資料。| No feedback data yet.")
        return

    col_acc  = [c for c in df.columns if "準確率" in c or "Accuracy" in c][0]
    col_use  = [c for c in df.columns if "實用性" in c or "Usefulness" in c][0]
    col_prog = [c for c in df.columns if "身份" in c or "Program" in c][0]
    col_qual = [c for c in df.columns if "結果" in c or "Qualified" in c][0]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("總使用次數 | Total Uses", len(df))
    c2.metric("平均準確率 | Avg Accuracy", f"{df[col_acc].mean():.1f} / 5")
    c3.metric("平均實用性 | Avg Usefulness", f"{df[col_use].mean():.1f} / 5")
    qualified_pct = df[col_qual].str.contains("符合|Yes").sum() / len(df) * 100
    c4.metric("符合資格比例 | Qualified %", f"{qualified_pct:.0f}%")

    st.divider()
    col_left, col_right = st.columns(2)
    with col_left:
        st.markdown("#### 準確率分布 | Accuracy Distribution")
        st.bar_chart(df[col_acc].value_counts().sort_index())
    with col_right:
        st.markdown("#### 實用性分布 | Usefulness Distribution")
        st.bar_chart(df[col_use].value_counts().sort_index())

    st.divider()
    st.markdown("#### 使用身份分布 | Program Distribution")
    st.bar_chart(df[col_prog].value_counts())

    st.divider()
    st.markdown("#### 最近回饋記錄 | Recent Feedback")
    st.dataframe(df.tail(10).iloc[::-1], use_container_width=True)

    csv_bytes = df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
    st.download_button(
        "📥 下載完整回饋資料 | Download All Feedback",
        data=csv_bytes,
        file_name="feedback_export.csv",
        mime="text/csv"
    )


def dashboard_page():
    st.markdown("## 🔐 管理員儀表板 | Admin Dashboard")
    pwd = st.text_input("請輸入密碼 | Enter password", type="password")
    if st.button("登入 | Login"):
        if pwd == DASHBOARD_PASSWORD:
            st.session_state.dashboard_unlocked = True
            st.rerun()
        else:
            st.error("密碼錯誤 | Incorrect password")

    if st.session_state.get("dashboard_unlocked"):
        show_dashboard()
        if st.button("登出 | Logout"):
            st.session_state.dashboard_unlocked = False
            st.rerun()

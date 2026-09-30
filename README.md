# 🎓 Academic Credit Checking System
### 研究所畢業學分暨口試資格自動檢核系統

> A bilingual (Chinese/English) web application for graduate students to self-check graduation qualification status and examination eligibility.
> 雙語研究所畢業學分與口試資格自動檢核系統，專為國立臺灣大學生物科技研究所設計。

---

## 📌 Background / 專案背景

This system was built to address a real operational problem at the **NTU Institute of Biotechnology**: graduate students — especially international students — frequently misunderstood credit requirements or submitted oral examination applications with errors, creating significant administrative burden.

This tool allows students to self-check their eligibility before approaching staff, reducing errors and saving time on both sides.

---

## ✨ Features / 功能特色

| Feature | Description |
|--------|-------------|
| 🎓 Step-by-step credit check | Supports both Master's (R) and PhD (D) students |
| 🌐 Fully bilingual | All UI text, reports, and messages in 中文 + English |
| 📄 PDF report generation | Downloadable bilingual graduation checklist via ReportLab |
| 💬 Smart Assistant | Rule-based Q&A chatbot powered by a JSON knowledge base |
| 📊 Admin Dashboard | Password-protected analytics dashboard for staff |
| 📝 Mandatory feedback | Students must complete a feedback form before downloading PDF |

---

## 🛠️ Tech Stack / 技術架構

| Tool | Purpose |
|------|---------|
| **Python** | Core language |
| **Streamlit** | Web UI framework |
| **ReportLab** | Bilingual PDF generation with Chinese font support |
| **Pandas** | Feedback data analysis and dashboard charts |
| **JSON** | Knowledge base for Smart Assistant |
| **CSV** | Local feedback log storage |

---

## 🗂️ Project Structure / 模組架構

```
Academic-Credit-Checking-System/
│
├── app.py                  # Main application entry point
├── translations.py         # All bilingual UI text (zh/en)
├── pdf_generator.py        # ReportLab PDF generation (Master's & PhD)
├── feedback.py             # Feedback form, CSV logging, admin dashboard
├── chatbot.py              # Rule-based Smart Assistant (JSON-powered)
├── concepts.json           # Knowledge base for chatbot Q&A
└── requirements.txt        # Python dependencies
```

---

## 📋 Credit Requirements / 學分規定摘要

### Master's Program / 碩士班

| Category | Required Credits |
|----------|-----------------|
| Core courses (專業必修) | 9 credits |
| Electives (選修) | ≥ 9 credits |
| Research (論文) | 6 credits |
| **Total minimum** | **≥ 24 credits** |

### PhD Program / 博士班

| Category | Required Credits |
|----------|-----------------|
| Core courses (專業必修) | 9 credits |
| Electives (選修) | ≥ 9 credits |
| Research (論文) | 12 credits |
| **Total minimum** | **≥ 30 credits** |

---

## 🌍 English Proficiency Thresholds / 英語能力門檻

| Test | Master's | PhD |
|------|----------|-----|
| TOEFL iBT | ≥ 72 | ≥ 80 |
| IELTS | ≥ 6.0 | ≥ 6.5 |
| TOEIC | ≥ 750 | ≥ 800 |
| GEPT | High-Intermediate Pass | Advanced Pass |

---

## 🚀 Getting Started / 本地端執行

### 1. Clone the repository

```bash
git clone https://github.com/yujzhang-code/Academic-Credit-Checking-System.git
cd Academic-Credit-Checking-System
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the application

```bash
streamlit run app.py
# or, if streamlit is not in PATH:
python -m streamlit run app.py
```

### 4. Access in browser

```
http://localhost:8501
```

---

## 💬 Smart Assistant Knowledge Base / 智慧助理知識庫格式

The chatbot reads from `concepts.json`. You can extend it by adding new entries:

```json
{
  "your_topic_key": {
    "keywords": ["keyword1", "keyword2", "關鍵字"],
    "answer_zh": "中文回答",
    "answer_en": "English answer"
  }
}
```

---

## 📊 Admin Dashboard / 管理員儀表板

- Access via the `📊` icon in the top-left corner of the sidebar
- Or navigate to: `http://localhost:8501/?admin=1`
- Default password: `iob2024` *(change in `feedback.py` before deployment)*
- Features: submission count, satisfaction rating distribution, recent responses, CSV export

---

## 📝 Feedback System / 回饋機制

- Students must complete a short satisfaction survey before downloading their PDF report
- Responses are logged locally to `feedback_log.csv` (excluded from version control)
- Future upgrade: migrate to Google Sheets for cloud-based storage

---

## 🗺️ Roadmap / 未來規劃

- [ ] 🔍 Upgrade chatbot to true RAG (ChromaDB + Claude API)
- [ ] ☁️ Deploy on Streamlit Cloud for public access
- [ ] 📊 Migrate feedback storage to Google Sheets
- [ ] 📱 Add LINE Bot integration for mobile notifications
- [ ] 🔐 Student ID validation against official enrollment records

---

## ⚠️ Disclaimer / 免責聲明

This system is designed as a **self-check reference tool only**.  
All final eligibility decisions must be confirmed with the Institute office.

本系統僅供學生**自我預先檢核**使用，最終畢業資格及口試申請資格以研究所辦公室審核結果為準。

---

## 👩‍💼 Author / 作者

Built by **Yu Jie Chang**  
Administrative Staff, Institute of Biotechnology, National Taiwan University  

*This project was developed as part of a portfolio for graduate school application in Artificial Intelligence.*

---

*Last updated: 2026*

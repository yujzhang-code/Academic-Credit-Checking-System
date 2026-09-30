# app.py — 主程式（頁面邏輯）
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
from translations import zh, en, bi, gap, note
from pdf_generator import gen_pdf_master, gen_pdf_phd
from feedback import show_feedback_and_download, dashboard_page
from chatbot import load_knowledge, search_answer

st.set_page_config(
    page_title=f"{zh('page_title')} | {en('page_title')}",
    page_icon="🎓",
    layout="centered"
)

# ── 儀表板小圖示按鈕（左上角，無框，hover顯示提示） ──



# session state 初始化（提前，讓按鈕判斷用）
if "show_dashboard" not in st.session_state:
    st.session_state.show_dashboard = False
if "dashboard_unlocked" not in st.session_state:
    st.session_state.dashboard_unlocked = False

# 用 query params 做頁面切換
params = st.query_params
if "admin" in params:
    st.session_state.show_dashboard = True




if st.session_state.show_dashboard:
    dashboard_page()
    if st.button("← 返回查詢系統 | Back to Check System"):
        st.session_state.show_dashboard = False
        st.session_state.dashboard_unlocked = False
        st.query_params.clear()
        st.rerun()
    st.stop()

st.markdown(f"## 🎓 {zh('page_title')}")
st.markdown(f"*{en('page_title')}*")
st.caption(f"{zh('dept_name')}　｜　{en('dept_name')}")
st.divider()

# Session state 初始化
for key, val in [
    ("step", 1), ("student_id", ""), ("program", ""), ("query_type", ""),
    ("check_result", None),
]:
    if key not in st.session_state:
        st.session_state[key] = val

def detect_program(sid):
    sid = sid.strip().upper()
    if sid.startswith("R"):
        return "master"
    elif sid.startswith("D"):
        return "phd"
    return ""

# ══════════════════════════════════════════════════════════════════════════
# Step 1：輸入學號
# ══════════════════════════════════════════════════════════════════════════
if st.session_state.step == 1:
    st.markdown(f"### {zh('step1_title')}")
    st.markdown(f"*{en('step1_title')}*")
    sid = st.text_input(
        bi("step1_input"),
        placeholder=bi("step1_placeholder", " | ")
    )
    if st.button(bi("step1_next", " | ")):
        prog = detect_program(sid)
        if not prog:
            st.error(bi("step1_error"))
        else:
            st.session_state.student_id = sid.strip().upper()
            st.session_state.program = prog
            st.session_state.step = 2
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════
# Step 2：選擇查詢項目
# ══════════════════════════════════════════════════════════════════════════
elif st.session_state.step == 2:
    prog = st.session_state.program
    sid = st.session_state.student_id
    prog_label = bi("master") if prog == "master" else bi("phd")

    st.info(f"✅ {zh('step2_info')} / {en('step2_info')}：**{sid}**　｜　{zh('step2_identity')} / {en('step2_identity')}：**{prog_label}**")
    st.markdown(f"### {zh('step2_title')}")
    st.markdown(f"*{en('step2_title')}*")

    if prog == "master":
        options_zh = [zh("m_oral"), zh("m_grad")]
        options_en = [en("m_oral"), en("m_grad")]
    else:
        options_zh = [zh("phd_qual"), zh("phd_oral")]
        options_en = [en("phd_qual"), en("phd_oral")]

    options_bi = [f"{z}\n{e}" for z, e in zip(options_zh, options_en)]
    selected = st.radio("　", options_bi, index=0)
    selected_idx = options_bi.index(selected)

    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button(bi("back", " | ")):
            st.session_state.step = 1
            st.rerun()
    with col2:
        if st.button(bi("start_btn", "\n")):
            st.session_state.query_type = options_zh[selected_idx]
            st.session_state.step = 3
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════
# Step 3：輸入課程 & 檢核
# ══════════════════════════════════════════════════════════════════════════
elif st.session_state.step == 3:
    prog = st.session_state.program
    sid = st.session_state.student_id
    qt = st.session_state.query_type
    prog_label = bi("master") if prog == "master" else bi("phd")

    # 對應查詢類型的英文
    qt_en_map = {
        zh("m_oral"): en("m_oral"),
        zh("m_grad"): en("m_grad"),
        zh("phd_qual"): en("phd_qual"),
        zh("phd_oral"): en("phd_oral"),
    }
    qt_en = qt_en_map.get(qt, qt)

    st.info(f"✅ {sid}　｜　{prog_label}　｜　{qt} / {qt_en}")
    st.markdown(f"### {zh('step3_title')}")
    st.markdown(f"*{en('step3_title')}*")
    st.info(f"{zh('step3_note')}\n\n*{en('step3_note')}*")

    # ══════════════════════════════════════════
    # 碩士班
    # ══════════════════════════════════════════
    if prog == "master":
        st.markdown(f"---\n#### {zh('required_sec')} | {en('required_sec')}")

        # 專題討論
        seminar = st.number_input(
            f"{zh('seminar')} | {en('seminar')}",
            min_value=0, max_value=8, step=1, value=0,
            help=bi("seminar_note")
        )

        # 生物技術核心實驗
        core_lab_pass = st.radio(
            f"{zh('core_lab')}\n{en('core_lab')}",
            [bi("core_lab_yes", " / "), bi("core_lab_no", " / "), bi("core_lab_ugrad", " / ")],
            index=1,
            help=bi("core_lab_help")
        )

        # 必修課程二選一
        mgmt_choice = st.radio(
            f"{zh('mgmt_label')} | {en('mgmt_label')}",
            [
                bi("mgmt_m0140", "\n"),
                bi("mgmt_u0130", "\n"),
                bi("mgmt_none", " / "),
            ],
            index=2
        )
        if "U0130" in mgmt_choice or "u0130" in mgmt_choice or "尖端" in mgmt_choice or "Cutting Edge" in mgmt_choice:
            st.warning(bi("mgmt_warn"))

        # 本所 M/D 必修
        dept_req_credits = st.number_input(
            f"{zh('dept_req_label')}\n{en('dept_req_label')}",
            min_value=0, max_value=30, step=1, value=0
        )

        # 選修
        st.markdown(f"---\n#### {zh('elective_sec')} | {en('elective_sec')}")
        elective_credits = st.number_input(
            f"{zh('elective_label')}\n{en('elective_label')}",
            min_value=0, max_value=30, step=1, value=0
        )

        # 碩士論文
        st.markdown("---")
        thesis_enrolled = st.checkbox(
            f"{zh('thesis_label')}\n{en('thesis_label')}",
            help=bi("thesis_note")
        )

        # 英文能力
        st.markdown(f"---\n#### {zh('english_sec')} | {en('english_sec')}")
        eng_opts = ["eng_cet_m","eng_toefl","eng_ielts","eng_flpt","eng_fce","eng_toeic","eng_degree","eng_online","eng_none"]
        eng_labels = [bi(k, " / ") for k in eng_opts]
        eng_method_bi = st.selectbox("　", eng_labels)
        eng_method_key = eng_opts[eng_labels.index(eng_method_bi)]

        eng_score = None
        eng_grade = None
        if eng_method_key == "eng_toefl":
            eng_score = st.number_input(bi("eng_score_toefl", " | "), min_value=0, max_value=120, value=0)
        elif eng_method_key == "eng_ielts":
            eng_score = st.number_input(bi("eng_score_ielts", " | "), min_value=0.0, max_value=9.0, step=0.5, value=0.0)
        elif eng_method_key == "eng_flpt":
            eng_score = st.number_input(bi("eng_score_flpt", " | "), min_value=0, max_value=100, value=0)
        elif eng_method_key == "eng_fce":
            eng_grade = st.selectbox(bi("eng_grade_fce", " | "), ["B1", "B2", "C1", "C2"])
        elif eng_method_key == "eng_toeic":
            eng_score = st.number_input(bi("eng_score_toeic", " | "), min_value=0, max_value=990, value=0)

        # ── 檢核邏輯（碩士）──────────────────────────────────────────────
        if st.button(bi("check_btn", " | ")):
            gaps = []
            notes = []
            req_credits = 0

            # 專題討論（最多計4學分）
            sem_counted = min(seminar, 4)
            req_credits += sem_counted
            if seminar < 4:
                gaps.append(gap(
                    f"專題討論：已修 {seminar} 學分，建議修滿 4 學分（計入畢業學分上限）",
                    f"Seminar: {seminar} credits completed; recommended to complete 4 credits (max counted toward graduation)"
                ))

            # 生物技術核心實驗
            core_ok = "Yes" in core_lab_pass or "是" in core_lab_pass
            core_sub = "ugrad" in core_lab_pass or "大學部" in core_lab_pass or "undergraduate" in core_lab_pass.lower()
            if core_ok or core_sub:
                req_credits += 4
                if core_sub:
                    notes.append(note(
                        "生物技術核心實驗：以大學部修習成績抵免，需正式申請替代，請洽系所辦公室。",
                        "Biotechnology Core Techniques: Undergraduate substitution requires formal application. Please contact the department office."
                    ))
            else:
                gaps.append(gap(
                    "生物技術核心實驗（4學分）：尚未修習或成績未達 B-，需重新修習",
                    "Biotechnology Core Techniques (4 credits): Not completed or grade below B-; must retake"
                ))

            # 必修課程二選一
            mgmt_ok = "M0140" in mgmt_choice or "必修課程二選一" in mgmt_choice or "Required course(1 of 2)" in mgmt_choice or \
                      "U0130" in mgmt_choice or "尖端" in mgmt_choice or "Cutting" in mgmt_choice
            if mgmt_ok:
                req_credits += 2
            else:
                gaps.append(gap(
                    "必修課程二選一（2學分）：尚未修習，請修習 642 M0140 生物科技管理與產業分析 或 642 U0130 尖端生技邁向新興產業專論",
                    "Management Course (2 credits): Not completed. Please enroll in 642 M0140 or 642 U0130"
                ))

            # 本所M/D必修6學分
            dept_ok = dept_req_credits >= 6
            req_credits += min(dept_req_credits, 6)
            if not dept_ok:
                gaps.append(gap(
                    f"本所 M 或 D 字頭必修課程：已修 {dept_req_credits} 學分，尚缺 {6 - dept_req_credits} 學分",
                    f"Required M/D prefix courses: {dept_req_credits} credits completed; {6 - dept_req_credits} credits remaining "
                ))

            # 選修10學分
            elective_ok = elective_credits >= 10
            if not elective_ok:
                gaps.append(gap(
                    f"選修學分：已修 {elective_credits} 學分，尚缺 {10 - elective_credits} 學分",
                    f"Elective credits: {elective_credits} completed; {10 - elective_credits} remaining"
                ))

            # 總學分24
            total_credits = req_credits + elective_credits
            if total_credits < 24:
                gaps.append(gap(
                    f"總學分：已累計 {total_credits} 學分，尚缺 {24 - total_credits} 學分（需達 24 學分）",
                    f"Total credits: {total_credits} accumulated; {24 - total_credits} more required (minimum 24)"
                ))

            # 碩士論文選修
            if not thesis_enrolled:
                gaps.append(gap(
                    "642 M0010 碩士論文：申請學位考口試當學期需選修（不計畢業學分）",
                    "642 M0010 Dissertation (M): Must be enrolled during the semester of oral defense application (not counted toward graduation)"
                ))

            # 英文能力
            eng_pass = False
            eng_label_zh = zh(eng_method_key)
            eng_label_en = en(eng_method_key)
            if eng_method_key in ["eng_cet_m", "eng_degree", "eng_online"]:
                eng_pass = True
            elif eng_method_key == "eng_toefl":
                eng_pass = eng_score >= 72
                eng_label_zh = f"TOEFL-iBT {eng_score} 分"
                eng_label_en = f"TOEFL-iBT {eng_score}"
            elif eng_method_key == "eng_ielts":
                eng_pass = eng_score >= 6.0
                eng_label_zh = f"IELTS {eng_score}"
                eng_label_en = f"IELTS {eng_score}"
            elif eng_method_key == "eng_flpt":
                eng_pass = eng_score >= 70
                eng_label_zh = f"FLPT 各分項最低 {eng_score} 分"
                eng_label_en = f"FLPT each section lowest {eng_score}"
            elif eng_method_key == "eng_fce":
                eng_pass = eng_grade in ["B2", "C1", "C2"]
                eng_label_zh = f"FCE {eng_grade}"
                eng_label_en = f"FCE {eng_grade}"
            elif eng_method_key == "eng_toeic":
                eng_pass = eng_score >= 785
                eng_label_zh = f"TOEIC {eng_score} 分"
                eng_label_en = f"TOEIC {eng_score}"

            if not eng_pass:
                if eng_method_key == "eng_none":
                    gaps.append(gap(
                        "英文能力：尚未取得認證，請通過本所認可之英語能力檢定，或修畢「研究生線上英文二（Adveng7002）」以上",
                        "English Proficiency: Not yet certified. Please pass an approved English proficiency test or complete Graduate Online English II (Adveng7002)"
                    ))
                else:
                    gaps.append(gap(
                        f"英文能力：{eng_label_zh} 未達門檻，請提升成績或修畢「研究生線上英文二（Adveng7002）」以上",
                        f"English Proficiency: {eng_label_en} below required threshold. Please improve score or complete Graduate Online English II (Adveng7002)"
                    ))

            qualified = len(gaps) == 0

            # 產生 PDF bytes
            pdf_bytes = gen_pdf_master(
                sid=sid, qt=qt, qt_en=qt_en,
                qualified=qualified, gaps=gaps, notes=notes,
                credits={
                    "seminar": seminar,
                    "core_lab_pass": core_ok or core_sub,
                    "core_lab_sub": core_sub,
                    "mgmt_ok": mgmt_ok,
                    "dept_req": dept_req_credits,
                    "elective": elective_credits,
                    "total": total_credits,
                    "thesis_enrolled": thesis_enrolled,
                },
                eng_label_zh=eng_label_zh,
                eng_label_en=eng_label_en,
                eng_pass=eng_pass,
            )

            # 把結果存進 session_state，讓頁面重整後仍顯示
            st.session_state.check_result = {
                "qualified": qualified,
                "gaps": gaps,
                "notes": notes,
                "pdf_bytes": pdf_bytes,
                "program": "碩士 Master's",
                "qt": f"{qt} / {qt_en}",
                "feedback_key": f"master_{sid}",
            }

        # ── 在 button block 外面顯示結果和回饋 ──────────────────────────
        if st.session_state.check_result:
            r = st.session_state.check_result
            st.divider()
            if r["qualified"]:
                st.success(bi("qualified_msg"))
            else:
                st.warning(f"{zh('not_qualified')}\n\n*{en('not_qualified')}*")
                for g in r["gaps"]:
                    st.markdown(f"- ❌ {g['zh']}\n  - *{g['en']}*")
            if r["notes"]:
                for n in r["notes"]:
                    st.info(f"📝 {n['zh']}\n\n*{n['en']}*")

            show_feedback_and_download(
                sid=sid, program=r["program"], qt=r["qt"],
                qualified=r["qualified"], pdf_bytes=r["pdf_bytes"],
                feedback_key=r["feedback_key"]
            )

    # ══════════════════════════════════════════
    # 博士班
    # ══════════════════════════════════════════
    else:
        st.markdown(f"---\n#### {zh('required_sec')} | {en('required_sec')}")

        dissertation = st.checkbox(f"{zh('phd_dissertation')}\n{en('phd_dissertation')}", value=False)
        topics = st.checkbox(f"{zh('phd_topics')}\n{en('phd_topics')}", value=False)
        seminar_phd = st.checkbox(f"{zh('phd_seminar')}\n{en('phd_seminar')}", value=False)
        adv1 = st.checkbox(f"{zh('phd_adv1')}\n{en('phd_adv1')}", value=False)
        adv2 = st.checkbox(f"{zh('phd_adv2')}\n{en('phd_adv2')}", value=False)

        st.markdown(f"---\n#### {zh('phd_req_sec')} | {en('phd_req_sec')}")
        st.caption(bi("phd_req_note"))

        c_epig     = st.checkbox(f"{zh('c_epig')}\n{en('c_epig')}", value=False)
        c_stem     = st.checkbox(f"{zh('c_stem')}\n{en('c_stem')}", value=False)
        c_bioinf   = st.checkbox(f"{zh('c_bioinf')}\n{en('c_bioinf')}", value=False)
        c_antibody = st.checkbox(f"{zh('c_antibody')}\n{en('c_antibody')}", value=False)
        if c_antibody:
            st.warning(bi("c_antibody_warn"))
        c_transgenic = st.checkbox(f"{zh('c_transgenic')}\n{en('c_transgenic')}", value=False)
        c_plant    = st.checkbox(f"{zh('c_plant')}\n{en('c_plant')}", value=False)
        c_micro    = st.checkbox(f"{zh('c_micro')}\n{en('c_micro')}", value=False)
        c_srna     = st.checkbox(f"{zh('c_srna')}\n{en('c_srna')}", value=False)
        if c_srna:
            st.info(bi("c_srna_warn"))
        c_omics    = st.checkbox(f"{zh('c_omics')}\n{en('c_omics')}", value=False)

        st.markdown("---")
        phd_elective = st.number_input(
            f"{zh('phd_elective_label')}\n{en('phd_elective_label')}",
            min_value=0, max_value=20, step=1, value=0,
            help=bi("phd_elective_note")
        )

        # 博士資格考、公開演講
        st.markdown("---")
        qual_passed = st.checkbox(f"{zh('qual_exam')}\n{en('qual_exam')}", value=False)
        talk_done   = st.checkbox(f"{zh('public_talk')}\n{en('public_talk')}", value=False)

        # 論文（只在申請學位考時顯示）
        pub_route_key = None
        if qt == zh("phd_oral"):
            st.markdown(f"---\n#### {zh('pub_sec')} | {en('pub_sec')}")
            pub_opts = ["pub_general", "pub_if", "pub_none"]
            pub_labels = [bi(k, "\n") for k in pub_opts]
            pub_sel = st.radio("　", pub_labels, index=2)
            pub_route_key = pub_opts[pub_labels.index(pub_sel)]

        # 英文能力（博士）
        st.markdown(f"---\n#### {zh('english_sec')} | {en('english_sec')}")
        phd_eng_opts = ["eng_cet_phd","eng_toefl_phd","eng_ielts_phd","eng_flpt_phd","eng_fce_phd","eng_toeic_phd","eng_degree","eng_none"]
        phd_eng_labels = [bi(k, " / ") for k in phd_eng_opts]
        phd_eng_bi = st.selectbox("　", phd_eng_labels)
        phd_eng_key = phd_eng_opts[phd_eng_labels.index(phd_eng_bi)]

        phd_eng_score = None
        phd_eng_sw    = None
        phd_eng_oral  = None
        phd_eng_grade = None

        if phd_eng_key == "eng_toefl_phd":
            phd_eng_score = st.number_input(bi("eng_toefl_phd", " | "), min_value=0, max_value=120, value=0)
        elif phd_eng_key == "eng_ielts_phd":
            phd_eng_score = st.number_input(bi("eng_ielts_phd", " | "), min_value=0.0, max_value=9.0, step=0.5, value=0.0)
        elif phd_eng_key == "eng_flpt_phd":
            phd_eng_score = st.number_input(bi("eng_flpt_total", " | "), min_value=0, max_value=300, value=0)
            phd_eng_oral  = st.selectbox(bi("eng_flpt_oral", " | "), ["未取得 / Not obtained", "S-1", "S-2", "S-2+", "S-3", "S-4"])
        elif phd_eng_key == "eng_fce_phd":
            phd_eng_grade = st.selectbox(bi("eng_fce_grade_phd", " | "), ["B1", "B2", "C1", "C2"])
        elif phd_eng_key == "eng_toeic_phd":
            phd_eng_score = st.number_input(bi("eng_toeic_score", " | "), min_value=0, max_value=990, value=0)
            phd_eng_sw    = st.number_input(bi("eng_toeic_sw", " | "), min_value=0, max_value=400, value=0)

        # ── 檢核邏輯（博士）──────────────────────────────────────────────
        if st.button(bi("check_btn", " | ")):
            gaps = []
            notes = []

            # 一年級必修
            if not adv1:
                gaps.append(gap("642 D0210 高等生物科技特論（一）（3學分）尚未修習",
                                "642 D0210 Selected Topics in Advanced Biotechnology (I) (3 credits): Not completed"))
            if not adv2:
                gaps.append(gap("642 D0220 高等生物科技特論（二）（3學分）尚未修習",
                                "642 D0220 Selected Topics in Advanced Biotechnology (II) (3 credits): Not completed"))

            # 必選修9選2（6學分）
            chosen = [c_epig, c_stem, c_bioinf, c_antibody, c_transgenic, c_plant, c_micro, c_srna, c_omics]
            chosen_credits = sum(3 for c in chosen if c)
            if chosen_credits < 6:
                gaps.append(gap(
                    f"本所必選課程（9選2）：已修 {chosen_credits} 學分，尚缺 {6 - chosen_credits} 學分",
                    f"Required electives (choose 2 of 9): {chosen_credits} credits completed; {6 - chosen_credits} remaining"
                ))

            # 選修4學分
            if phd_elective < 4:
                gaps.append(gap(
                    f"選修學分：已修 {phd_elective} 學分，尚缺 {4 - phd_elective} 學分",
                    f"Elective credits: {phd_elective} completed; {4 - phd_elective} remaining"
                ))

            adv_credits = (3 if adv1 else 0) + (3 if adv2 else 0)
            total_phd = adv_credits + chosen_credits + phd_elective
            if total_phd < 20:
                gaps.append(gap(
                    f"總學分：已累計 {total_phd} 學分，尚缺 {20 - total_phd} 學分（需達 20 學分）",
                    f"Total credits: {total_phd} accumulated; {20 - total_phd} more required (minimum 20)"
                ))

            # 博士資格考 & 演講
            if qt == zh("phd_oral"):
                if not qual_passed:
                    gaps.append(gap("尚未通過博士資格考（筆試及口試）",
                                    "PhD Qualifying Examination (written and oral) not yet passed"))
                if not talk_done:
                    gaps.append(gap("尚未舉辦公開演講",
                                    "Public seminar/lecture not yet completed"))

            # 論文發表
            if qt == zh("phd_oral") and pub_route_key == "pub_none":
                gaps.append(gap(
                    "論文發表：尚未達到本所最低發表要求（需≥2篇SCI/SSCI，或代表作IF≥5）",
                    "Publication: Minimum requirement not met (≥2 SCI/SSCI papers, or representative paper with IF ≥ 5)"
                ))

            # 英文能力（博士）
            phd_eng_pass = False
            phd_eng_label_zh = zh(phd_eng_key)
            phd_eng_label_en = en(phd_eng_key)

            if phd_eng_key in ["eng_cet_phd", "eng_degree"]:
                phd_eng_pass = True
            elif phd_eng_key == "eng_toefl_phd":
                phd_eng_pass = phd_eng_score >= 87
                phd_eng_label_zh = f"TOEFL-iBT {phd_eng_score} 分"
                phd_eng_label_en = f"TOEFL-iBT {phd_eng_score}"
            elif phd_eng_key == "eng_ielts_phd":
                phd_eng_pass = phd_eng_score >= 6.5
                phd_eng_label_zh = f"IELTS {phd_eng_score}"
                phd_eng_label_en = f"IELTS {phd_eng_score}"
            elif phd_eng_key == "eng_flpt_phd":
                oral_ok = phd_eng_oral and any(x in phd_eng_oral for x in ["S-2+","S-3","S-4"])
                phd_eng_pass = (phd_eng_score >= 240) and oral_ok
                phd_eng_label_zh = f"FLPT 總分 {phd_eng_score}，口試 {phd_eng_oral}"
                phd_eng_label_en = f"FLPT Total {phd_eng_score}, Oral {phd_eng_oral}"
            elif phd_eng_key == "eng_fce_phd":
                phd_eng_pass = phd_eng_grade in ["C1","C2"]
                phd_eng_label_zh = f"FCE {phd_eng_grade}"
                phd_eng_label_en = f"FCE {phd_eng_grade}"
            elif phd_eng_key == "eng_toeic_phd":
                phd_eng_pass = (phd_eng_score >= 785) and (phd_eng_sw >= 240)
                phd_eng_label_zh = f"TOEIC {phd_eng_score}，SW {phd_eng_sw}"
                phd_eng_label_en = f"TOEIC {phd_eng_score}, SW {phd_eng_sw}"

            if not phd_eng_pass:
                if phd_eng_key == "eng_none":
                    gaps.append(gap(
                        "英文能力：尚未取得認證（請確認是否通過線上英文三）",
                        "English Proficiency: Not yet certified (Please confirm if Graduate Online English III has been completed)"
                    ))
                else:
                    gaps.append(gap(
                        f"英文能力：{phd_eng_label_zh} 未達博士班門檻",
                        f"English Proficiency: {phd_eng_label_en} below PhD threshold"
                    ))

            qualified = len(gaps) == 0

            pdf_bytes = gen_pdf_phd(
                sid=sid, qt=qt, qt_en=qt_en,
                qualified=qualified, gaps=gaps, notes=notes,
                credits={
                    "adv1": adv1, "adv2": adv2,
                    "chosen": chosen_credits,
                    "elective": phd_elective,
                    "total": total_phd,
                },
                eng_label_zh=phd_eng_label_zh,
                eng_label_en=phd_eng_label_en,
                eng_pass=phd_eng_pass,
            )

            # 把結果存進 session_state
            st.session_state.check_result = {
                "qualified": qualified,
                "gaps": gaps,
                "notes": notes,
                "pdf_bytes": pdf_bytes,
                "program": "博士 PhD",
                "qt": f"{qt} / {qt_en}",
                "feedback_key": f"phd_{sid}",
            }

        # ── 在 button block 外面顯示結果和回饋 ──────────────────────────
        if st.session_state.check_result:
            r = st.session_state.check_result
            st.divider()
            if r["qualified"]:
                st.success(bi("qualified_msg"))
            else:
                st.warning(f"{zh('not_qualified')}\n\n*{en('not_qualified')}*")
                for g in r["gaps"]:
                    st.markdown(f"- ❌ {g['zh']}\n  - *{g['en']}*")
            if r["notes"]:
                for n in r["notes"]:
                    st.info(f"📝 {n['zh']}\n\n*{n['en']}*")

            show_feedback_and_download(
                sid=sid, program=r["program"], qt=r["qt"],
                qualified=r["qualified"], pdf_bytes=r["pdf_bytes"],
                feedback_key=r["feedback_key"]
            )

    if st.button(bi("restart_btn", " | ")):
        st.session_state.check_result = None
        st.session_state.step = 2
        st.rerun()

# ===== 🤖 聊天機器人智慧問答區 =====
import json

def search_answer(user_input, knowledge, lang):
    user_input = user_input.lower().strip()

    for key, item in knowledge.items():
        for kw in item["keywords"]:
            if kw.lower() in user_input:
                return item["answer_zh"] if lang == "中文" else item["answer_en"]

    return "找不到相關答案" if lang == "中文" else "No relevant answer found."

# 讀資料
try:
    with open("concepts.json", "r", encoding="utf-8") as f:
        knowledge = json.load(f)
except FileNotFoundError:
    knowledge = {}

# 👉 sidebar
with st.sidebar:
    # 儀表板圖示（左上角，hover顯示提示）
    st.markdown("""
<style>
.admin-link {
    display: inline-block;
    font-size: 20px;
    text-decoration: none;
    opacity: 0.35;
    padding: 2px 6px;
    border-radius: 6px;
    margin-bottom: 8px;
}
.admin-link:hover {
    opacity: 1;
    background: rgba(0,0,0,0.08);
}
.admin-tooltip {
    position: relative;
    display: inline-block;
}
.admin-tooltip .tooltiptext {
    visibility: hidden;
    background-color: #333;
    color: #fff;
    font-size: 11px;
    white-space: nowrap;
    padding: 4px 8px;
    border-radius: 4px;
    position: absolute;
    top: 28px;
    left: 0;
    z-index: 9999;
}
.admin-tooltip:hover .tooltiptext {
    visibility: visible;
}
</style>
<div class="admin-tooltip">
  <a href="?admin=1" class="admin-link">📊</a>
  <span class="tooltiptext">Admin Dashboard (Staff Only)</span>
</div>
""", unsafe_allow_html=True)

    st.markdown("### 🤖 Smart Assistant")

    lang = st.radio("語言 / Language", ["中文", "English"], horizontal=True)
    user_input = st.text_input("請輸入問題 / Ask something")

    if user_input:
        if knowledge:
            answer = search_answer(user_input, knowledge, lang)
        else:
            answer = "知識庫尚未載入。/ Knowledge base not loaded."
        st.write("🤖", answer)

# ══════════════════════════════════════════════════════════════════════════
# PDF 工具函數
# ══════════════════════════════════════════════════════════════════════════
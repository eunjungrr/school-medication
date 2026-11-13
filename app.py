"""
보건실 의약품 재고 관리 시스템
메인 Streamlit 앱 (v2 - 버그 수정 및 기능 추가)

실행 방법:
    streamlit run app.py
"""

import io
import re
from datetime import date, datetime

import altair as alt
import pandas as pd
import streamlit as st

import database as db
import utils as ut

# ═══════════════════════════════════════════════════════════════════
#  페이지 기본 설정
# ═══════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="보건실 의약품 재고 관리",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 데이터베이스 초기화
db.init_database()


# ═══════════════════════════════════════════════════════════════════
#  전역 CSS 스타일
# ═══════════════════════════════════════════════════════════════════

def inject_css():
    st.markdown("""
    <style>
    /* ── 전체 폰트 ── */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Noto Sans KR', sans-serif !important;
    }

    /* ── 최상위 앱 배경 (라이트/다크 모드 강제 통일) ── */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #F8F9FA !important;
        color: #1A1A2E !important;
    }

    /* ── 사이드바 배경 및 텍스트 ── */
    [data-testid="stSidebar"], [data-testid="stSidebar"] > div:first-child {
        background-color: #1A1A2E !important;
        border-right: 2px solid #282C4B !important;
    }
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #FFFFFF !important;
    }

    /* ── 사이드바 메뉴 버튼 (비활성) ── */
    [data-testid="stSidebar"] .stButton > button {
        background-color: #272B4D !important;
        border: 1.5px solid #3E4477 !important;
        border-radius: 10px !important;
        padding: 10px 14px !important;
        width: 100% !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2) !important;
        text-align: left !important;
    }
    [data-testid="stSidebar"] .stButton > button,
    [data-testid="stSidebar"] .stButton > button p,
    [data-testid="stSidebar"] .stButton > button span,
    [data-testid="stSidebar"] .stButton > button div,
    [data-testid="stSidebar"] .stButton > button * {
        color: #FFFFFF !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
        line-height: 1.4 !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: #383E6E !important;
        border-color: #636CAE !important;
    }

    /* ── 사이드바 활성(선택된) 버튼 ── */
    [data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background-color: #E63946 !important;
        border: 1.5px solid #FF5A68 !important;
    }
    [data-testid="stSidebar"] .stButton > button[kind="primary"],
    [data-testid="stSidebar"] .stButton > button[kind="primary"] p,
    [data-testid="stSidebar"] .stButton > button[kind="primary"] span,
    [data-testid="stSidebar"] .stButton > button[kind="primary"] * {
        color: #FFFFFF !important;
        font-weight: 800 !important;
    }

    /* ── 메인 영역의 일반 버튼 (Secondary) ── */
    [data-testid="stAppViewContainer"] .stButton > button:not([kind="primary"]) {
        background-color: #FFFFFF !important;
        color: #1A1A2E !important;
        border: 1.5px solid #CBD5E0 !important;
        border-radius: 10px !important;
    }
    [data-testid="stAppViewContainer"] .stButton > button:not([kind="primary"]) p,
    [data-testid="stAppViewContainer"] .stButton > button:not([kind="primary"]) span,
    [data-testid="stAppViewContainer"] .stButton > button:not([kind="primary"]) * {
        color: #1A1A2E !important;
        font-weight: 600 !important;
    }
    [data-testid="stAppViewContainer"] .stButton > button:not([kind="primary"]):hover {
        background-color: #F1F5F9 !important;
        border-color: #94A3B8 !important;
        box-shadow: 0 3px 8px rgba(0,0,0,0.08);
    }

    /* ── 메인 영역 Primary 버튼 (빨간색) ── */
    [data-testid="stAppViewContainer"] .stButton > button[kind="primary"] {
        background-color: #E63946 !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 10px !important;
    }
    [data-testid="stAppViewContainer"] .stButton > button[kind="primary"] p,
    [data-testid="stAppViewContainer"] .stButton > button[kind="primary"] span,
    [data-testid="stAppViewContainer"] .stButton > button[kind="primary"] * {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }

    /* ── 지정된 4종 버튼만 짧고 도톰하게 중앙 정렬 ── */
    [data-testid="stAppViewContainer"] div[class*="st-key-btn_local_start"] button,
    [data-testid="stAppViewContainer"] div[class*="st-key-btn_school_login"] button,
    [data-testid="stAppViewContainer"] div[class*="st-key-btn_medicine_register"] button,
    [data-testid="stAppViewContainer"] div[class*="st-key-dash_btn_"] button {
        width: min(100%, 230px) !important;
        min-height: 52px !important;
        padding: 11px 20px !important;
        margin-left: auto !important;
        margin-right: auto !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        border-radius: 13px !important;
        font-weight: 800 !important;
    }
    [data-testid="stAppViewContainer"] div[class*="st-key-dash_btn_"] button {
        width: min(100%, 190px) !important;
        margin-top: 13px !important;
    }
    [data-testid="stAppViewContainer"] div[class*="st-key-btn_local_start"] button *,
    [data-testid="stAppViewContainer"] div[class*="st-key-btn_school_login"] button *,
    [data-testid="stAppViewContainer"] div[class*="st-key-btn_medicine_register"] button *,
    [data-testid="stAppViewContainer"] div[class*="st-key-dash_btn_"] button * {
        font-weight: 800 !important;
    }

    /* ── 탭 메뉴 (Tabs) ── */
    .stTabs [data-baseweb="tab-list"] {
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 12px !important;
        padding: 6px !important;
        gap: 6px !important;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        border-radius: 8px !important;
    }
    .stTabs [data-baseweb="tab"] p,
    .stTabs [data-baseweb="tab"] span,
    .stTabs [data-baseweb="tab"] * {
        color: #4A5568 !important;
        font-weight: 700 !important;
        font-size: 0.9rem !important;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] p,
    .stTabs [data-baseweb="tab"][aria-selected="true"] span,
    .stTabs [data-baseweb="tab"][aria-selected="true"] * {
        color: #E63946 !important;
        font-weight: 800 !important;
    }

    /* ── 폼 및 라벨 ── */
    [data-testid="stAppViewContainer"] label,
    [data-testid="stAppViewContainer"] [data-testid="stWidgetLabel"] p {
        color: #1A1A2E !important;
        font-weight: 700 !important;
    }
    [data-testid="stAppViewContainer"] .stMarkdown p,
    [data-testid="stAppViewContainer"] .stMarkdown span {
        color: #1A1A2E !important;
    }

    /* ── 인풋 박스 및 셀렉트 ── */
    [data-testid="stAppViewContainer"] input,
    [data-testid="stAppViewContainer"] textarea {
        background-color: #FFFFFF !important;
        color: #1A1A2E !important;
        border: 1.5px solid #CBD5E0 !important;
        border-radius: 8px !important;
    }
    [data-testid="stAppViewContainer"] [data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        border: 1.5px solid #CBD5E0 !important;
        border-radius: 8px !important;
    }
    [data-testid="stAppViewContainer"] [data-baseweb="select"] * {
        color: #1A1A2E !important;
    }

    /* ── 섹션 헤더 ── */
    .section-header {
        background: #FFFFFF !important;
        border-radius: 12px;
        padding: 16px 20px;
        margin: 16px 0 10px;
        box-shadow: 0 1px 6px rgba(0,0,0,0.06);
        border: 1px solid #E2E8F0;
        border-left: 4px solid #1A1A2E !important;
        font-size: 1.1rem;
        font-weight: 700;
        color: #1A1A2E !important;
    }
    .section-header * {
        color: #1A1A2E !important;
    }

    /* ── 대시보드 카드 ── */
    .dash-card {
        background: #FFFFFF !important;
        border-radius: 16px;
        padding: 20px 24px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        border: 1px solid #E2E8F0;
        border-left: 5px solid;
        min-height: 110px;
    }
    .dash-card .count {
        font-size: 2.4rem;
        font-weight: 700;
        line-height: 1.1;
    }
    .dash-card .label {
        font-size: 0.88rem;
        color: #4A5568 !important;
        margin-top: 4px;
        font-weight: 600;
    }
    .dash-card .emoji {
        font-size: 1.6rem;
        float: right;
    }

    /* ── 상단 바 ── */
    .top-bar {
        background: #1A1A2E !important;
        color: #FFFFFF !important;
        padding: 14px 24px;
        border-radius: 12px;
        margin-bottom: 16px;
    }
    [data-testid="stAppViewContainer"] .stMarkdown .top-bar span {
        color: #FFFFFF !important;
    }

    /* ── 데이터프레임 ── */
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid #E2E8F0;
        background: #FFFFFF !important;
    }

    /* ── 팝업 모달 다이얼로그 (st.dialog) ── */
    /* 1. 배경 오버레이: 뒷배경(의약품 목록 관리 테이블)이 선명하게 보이도록 반투명 딤 처리 */
    div[data-testid="stDialog"],
    div.stDialog,
    div[data-baseweb="modal"],
    div[data-baseweb="backdrop"] {
        background: rgba(15, 23, 42, 0.50) !important;
        background-color: rgba(15, 23, 42, 0.50) !important;
        backdrop-filter: blur(2px) !important;
        -webkit-backdrop-filter: blur(2px) !important;
    }

    /* 2. 팝업 모달 본체(가운데 떠 있는 흰색 카드 박스만 타겟팅) */
    div[data-testid="stDialog"] > div,
    div.stDialog > div,
    div[data-baseweb="modal"] [role="dialog"],
    div[role="dialog"] {
        background: #FFFFFF !important;
        background-color: #FFFFFF !important;
        border-radius: 16px !important;
        box-shadow: 0 25px 60px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(0, 0, 0, 0.1) !important;
        border: 1.5px solid #CBD5E0 !important;
        color: #172033 !important;
    }

    /* 3. 모달 내부 텍스트 및 레이블 가독성 */
    div[data-testid="stDialog"] > div h2,
    div[data-testid="stDialog"] > div h3,
    div[data-testid="stDialog"] > div p,
    div[data-testid="stDialog"] > div span,
    div[data-testid="stDialog"] > div label {
        color: #1A1A2E !important;
    }

    /* 모달 내 라디오 버튼 */
    div[data-testid="stDialog"] > div [data-testid="stRadio"] label p {
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        color: #1A1A2E !important;
    }

    /* ── 스크롤바 ── */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #f1f1f1; }
    ::-webkit-scrollbar-thumb { background: #999; border-radius: 3px; }

    /* 밝은 바탕 + 선명한 글자: 기존 구조와 기능 유지 */
    :root { color-scheme: light; }
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"],
    [data-testid="stMain"], [data-testid="stMainBlockContainer"] {
        background-color: #FFFFFF !important;
        color: #172033 !important;
    }
    /* 테마 선택자 때문에 흐려졌던 탭과 일반 버튼 글자를 복원 */
    [data-testid="stAppViewContainer"] .stTabs [data-baseweb="tab"] p,
    [data-testid="stAppViewContainer"] .stTabs [data-baseweb="tab"] span {
        color: #243247 !important;
        opacity: 1 !important;
    }
    [data-testid="stAppViewContainer"] .stTabs [data-baseweb="tab"][aria-selected="true"] p,
    [data-testid="stAppViewContainer"] .stTabs [data-baseweb="tab"][aria-selected="true"] span {
        color: #087F52 !important;
    }
    [data-testid="stAppViewContainer"] .stButton > button:not([kind="primary"]),
    [data-testid="stAppViewContainer"] .stButton > button:not([kind="primary"]) * {
        color: #162438 !important;
    }
    /* 기존 네모난 카드 느낌은 남기되 배경은 밝고 평면적으로 */
    .section-header, .top-bar, .dash-card,
    [data-testid="stSidebar"] .stButton > button,
    [data-testid="stAppViewContainer"] .stButton > button,
    [data-testid="stAppViewContainer"] input,
    [data-testid="stAppViewContainer"] textarea,
    [data-testid="stAppViewContainer"] [data-baseweb="select"] > div {
        border-radius: 3px !important;
    }
    .dash-card { box-shadow: none !important; }
    .dash-card.card-expired { background-color: #FFF0F2 !important; border: 1px solid #F6BBC4 !important; border-left: 5px solid #E63946 !important; }
    .dash-card.card-expiring { background-color: #FFF6E9 !important; border: 1px solid #F3D6A7 !important; border-left: 5px solid #F4A261 !important; }
    .dash-card.card-low { background-color: #FFF0EC !important; border: 1px solid #F5C1B5 !important; border-left: 5px solid #E76F51 !important; }
    .dash-card.card-ok { background-color: #EAFBF5 !important; border: 1px solid #9BDCC4 !important; border-left: 5px solid #2A9D8F !important; }
    [data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background-color: #00CF73 !important;
        border-color: #00A85F !important;
    }
    [data-testid="stSidebar"] .stButton > button[kind="primary"] * { color: #08291D !important; }
    .section-header { border-left-color: #00B96E !important; }
    </style>
    """, unsafe_allow_html=True)


inject_css()


# ═══════════════════════════════════════════════════════════════════
#  세션 상태 초기화
# ═══════════════════════════════════════════════════════════════════

def init_session():
    defaults = {
        "logged_in": False,
        "school_id": None,
        "school_name": "",
        "local_mode": False,    # 로컬 전용 모드 (로그인 없이 사용)
        "active_tab": "대시보드",
        "dashboard_filter": None,
        "search_keyword": "",
        "search_category": "전체",
        "search_executed": False,
        "stock_mid": None,       # 현재 입출고 처리 중인 약품 ID
        "editing_mid": None,     # 현재 수정 중인 약품 ID
        "ocr_rows": None,        # OCR 인식 결과 행 목록 (편집용)
        "ocr_error": None,       # OCR 오류 메시지
        "excel_error": None,     # 엑셀 업로드 오류 메시지
        "excel_records": None,   # 엑셀 파싱 결과
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()

# ─── 로컬 전용 모드용 내부 학교 ID ────────────────────────────────
LOCAL_SCHOOL_ID   = 9999999
LOCAL_SCHOOL_NAME = "내 컴퓨터 (로컬 전용)"

def ensure_local_school():
    """로컬 전용 모드를 위한 가상 계정을 DB에 보장합니다."""
    import database as db2
    conn = db2.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM schools WHERE id = ?", (LOCAL_SCHOOL_ID,))
    if not cur.fetchone():
        # id를 직접 지정하여 삽입
        cur.execute(
            "INSERT OR IGNORE INTO schools (id, school_name, password_hash, created_at) VALUES (?,?,?,?)",
            (LOCAL_SCHOOL_ID, LOCAL_SCHOOL_NAME, "LOCAL", datetime.now().isoformat())
        )
        conn.commit()
    conn.close()


# ═══════════════════════════════════════════════════════════════════
#  로그인 / 회원가입 페이지
# ═══════════════════════════════════════════════════════════════════

def page_login():
    st.markdown("""
    <div style="text-align:center; padding: 40px 0 20px;">
        <span style="font-size:3rem;">💊</span>
        <h1 style="font-size:1.8rem; font-weight:800; color:#1A1A2E; margin:8px 0 4px;">
            보건실 의약품 재고 관리
        </h1>
        <p style="color:#666; font-size:0.95rem;">학교 보건실 스마트 의약품 관리 시스템</p>
    </div>
    """, unsafe_allow_html=True)

    tab_login, tab_local, tab_register, tab_admin = st.tabs([
        "🔐  학교 계정 로그인",
        "🖥️  내 컴퓨터에서 혼자 사용",
        "📝  새 학교 등록",
        "🔧  관리자",
    ])

    # ─── 로컬 전용 탭 ────────────────────────────────────────────
    with tab_local:
        st.markdown("<br>", unsafe_allow_html=True)
        col_c, col_form, col_c2 = st.columns([1, 2, 1])
        with col_form:
            with st.container(key="local_quick_start"):
                st.markdown("""
                <style>
                /* 로컬 시작 버튼에만 적용: 다른 버튼의 색상/동작은 유지 */
                [data-testid="stAppViewContainer"] .st-key-local_quick_start .stButton > button[kind="secondary"] {
                    background-color: #0F766E !important;
                    color: #FFFFFF !important;
                    border: 1px solid #0F766E !important;
                    border-radius: 12px !important;
                    box-shadow: 0 4px 12px rgba(15,118,110,0.15) !important;
                }
                [data-testid="stAppViewContainer"] .st-key-local_quick_start .stButton > button[kind="secondary"] * {
                    color: #FFFFFF !important;
                    font-weight: 700 !important;
                }
                [data-testid="stAppViewContainer"] .st-key-local_quick_start .stButton > button[kind="secondary"]:hover {
                    background-color: #115E59 !important;
                    border-color: #115E59 !important;
                    box-shadow: 0 6px 16px rgba(15,118,110,0.20) !important;
                }
                </style>
                <div style="background:#F0FDFA;border-radius:16px;padding:24px 28px;
                            border:1px solid #CCFBF1;margin-bottom:18px;">
                    <div style="font-size:1.4rem;margin-bottom:8px;">🖥️</div>
                    <div style="font-weight:700;font-size:1.05rem;color:#134E4A;margin-bottom:6px;">
                        로그인 없이 편리하게 사용
                    </div>
                    <div style="font-size:0.88rem;color:#334155;line-height:1.7;">
                        이 컴퓨터에서만 사용하는 경우 선택하세요.<br>
                        계정 없이 바로 시작할 수 있으며, 데이터는 <strong>이 컴퓨터에만 저장</strong>됩니다.<br>
                        다른 기기에서는 데이터를 볼 수 없습니다.
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("🚀  로그인 없이 바로 시작하기", use_container_width=True, type="secondary", key="btn_local_start"):
                    ensure_local_school()
                    st.session_state.logged_in = True
                    st.session_state.local_mode = True
                    st.session_state.school_id = LOCAL_SCHOOL_ID
                    st.session_state.school_name = LOCAL_SCHOOL_NAME
                    st.success("✅ 로컬 전용 모드로 시작합니다!")
                    st.rerun()

    # ─── 로그인 탭 ───────────────────────────────────────────────
    with tab_login:
        st.markdown("<br>", unsafe_allow_html=True)
        col_c, col_form, col_c2 = st.columns([1, 2, 1])
        with col_form:
            with st.form("login_form"):
                st.markdown("#### 🏫 학교 계정 로그인")
                st.markdown("""
                <div style="font-size:0.85rem;color:#475569;margin-bottom:12px;background:#F8FAFC;padding:8px 12px;border-radius:6px;border-left:3px solid #64748B;">
                    ℹ️ 비밀번호 분실로 초기화를 원할 시 관리자에게 연락주세요.<br>
                    <strong>전화: 041-592-0178</strong>
                </div>
                """, unsafe_allow_html=True)
                school = st.text_input("학교명", placeholder="예: 천안용곡중학교")
                pwd = st.text_input("비밀번호", type="password", placeholder="비밀번호 입력")
                submitted = st.form_submit_button("🔑  로그인", use_container_width=True, key="btn_school_login")

            if submitted:
                if not school or not pwd:
                    st.error("학교명과 비밀번호를 모두 입력해 주세요.")
                else:
                    ok, info = db.login_school(school, pwd)
                    if ok:
                        st.session_state.logged_in = True
                        st.session_state.local_mode = False
                        st.session_state.school_id = info["id"]
                        st.session_state.school_name = info["school_name"]
                        st.success(f"✅ {info['school_name']} 보건실에 오신 것을 환영합니다!")
                        st.rerun()
                    else:
                        st.error("❌ 학교명 또는 비밀번호가 올바르지 않습니다.")

    # ─── 등록 탭 ─────────────────────────────────────────────────
    with tab_register:
        st.markdown("<br>", unsafe_allow_html=True)
        col_c, col_form, col_c2 = st.columns([1, 2, 1])
        with col_form:
            reg_tab, del_tab = st.tabs(["➕ 새 학교 등록", "🗑️ 학교 계정 삭제"])

            with reg_tab:
                with st.form("register_form"):
                    st.markdown("#### 🏫 새 학교 등록")
                    st.info("처음 사용하시는 경우 학교명과 비밀번호를 설정해 주세요.\n같은 학교명 + 비밀번호로 어디서든 접속 가능합니다.")
                    new_school = st.text_input("학교명 *", placeholder="예: 천안용곡중학교")
                    new_pwd = st.text_input("비밀번호 설정 *", type="password", placeholder="4자리 이상")
                    new_pwd2 = st.text_input("비밀번호 확인 *", type="password", placeholder="비밀번호 재입력")
                    reg_submitted = st.form_submit_button("✅  등록하기", use_container_width=True)

                if reg_submitted:
                    if not new_school or not new_pwd:
                        st.error("학교명과 비밀번호를 입력해 주세요.")
                    elif len(new_pwd) < 4:
                        st.error("비밀번호는 4자리 이상이어야 합니다.")
                    elif new_pwd != new_pwd2:
                        st.error("비밀번호가 일치하지 않습니다.")
                    else:
                        ok, msg = db.register_school(new_school, new_pwd)
                        if ok:
                            st.success(f"✅ {msg}\n이제 로그인 탭에서 로그인해 주세요.")
                        else:
                            st.error(f"❌ {msg}")

            with del_tab:
                st.warning("⚠️ 삭제 후 복구가 불가합니다. 신중하게 진행해 주세요.")
                with st.form("delete_school_form"):
                    st.markdown("#### 🗑️ 학교 계정 삭제")
                    del_school = st.text_input("삭제할 학교명", placeholder="학교명 입력")
                    del_pwd = st.text_input("비밀번호 확인", type="password", placeholder="비밀번호 입력")
                    del_confirm = st.checkbox("위 학교의 모든 데이터를 영구 삭제하는 데 동의합니다.")
                    del_submitted = st.form_submit_button("🗑️  계정 삭제", use_container_width=True)

                if del_submitted:
                    if not del_school or not del_pwd:
                        st.error("학교명과 비밀번호를 입력해 주세요.")
                    elif not del_confirm:
                        st.error("동의 체크박스를 선택해 주세요.")
                    else:
                        ok, info = db.login_school(del_school, del_pwd)
                        if ok:
                            ok2, msg2 = db.delete_school(info["id"])
                            if ok2:
                                st.success(f"✅ '{del_school}' 계정이 삭제되었습니다.")
                            else:
                                st.error(f"❌ {msg2}")
                        else:
                            st.error("❌ 학교명 또는 비밀번호가 올바르지 않습니다.")

    # ─── 관리자 탭 ─────────────────────────────────────────────
    with tab_admin:
        st.markdown("<br>", unsafe_allow_html=True)
        col_c, col_form, col_c2 = st.columns([1, 2, 1])
        with col_form:
            st.markdown("""
            <div style="background:#FFF8E6;border-radius:12px;padding:16px 20px;
                        border-left:4px solid #FFA500;margin-bottom:16px;font-size:0.88rem;">
                🔧 <strong>관리자 전용 페이지</strong><br>
                이 시스템을 개발·관리하는 담당자만 사용하는 페이지입니다.
            </div>
            """, unsafe_allow_html=True)
            with st.form("admin_form"):
                admin_pwd = st.text_input("관리자 비밀번호", type="password",
                                          placeholder="관리자 비밀번호 입력")
                admin_submit = st.form_submit_button("🔓  관리자 로그인", use_container_width=True)

            # 관리자 비밀번호 (코드 레벨 설정 — 시스템 개발자만 수정 가능)
            ADMIN_PASSWORD = "admin_health_2026"

            if admin_submit:
                if admin_pwd == ADMIN_PASSWORD:
                    st.session_state["admin_unlocked"] = True
                else:
                    st.error("❌ 관리자 비밀번호가 올바르지 않습니다.")
                    st.session_state["admin_unlocked"] = False

            if st.session_state.get("admin_unlocked"):
                st.success("✅ 관리자 모드 활성화")
                schools = db.get_all_schools_admin()
                if schools:
                    st.markdown("#### 📋 등록된 학교 목록 및 비밀번호")
                    st.caption("⚠️ 이 정보는 관리자만 볼 수 있습니다.")
                    for s in schools:
                        with st.expander(f"🏫 {s['school_name']} (등록일: {s['created_at'][:10]})"):
                            st.write(f"**학교명**: {s['school_name']}")
                            st.write(f"**등록일**: {s['created_at'][:10]}")
                            st.write(f"**비밀번호 해시**: `{s['password_hash'][:20]}...`")
                            # 비밀번호 초기화 기능
                            new_pw_col, btn_col = st.columns([2, 1])
                            with new_pw_col:
                                new_pw = st.text_input("새 비밀번호 설정",
                                                       key=f"admin_newpw_{s['id']}",
                                                       placeholder="새 비밀번호")
                            with btn_col:
                                st.markdown("<br>", unsafe_allow_html=True)
                                if st.button("🔄 변경", key=f"admin_pwbtn_{s['id']}"):
                                    if new_pw and len(new_pw) >= 4:
                                        ok_r, msg_r = db.admin_reset_password(s["id"], new_pw)
                                        if ok_r:
                                            st.success("✅ 변경 완료")
                                        else:
                                            st.error(msg_r)
                                    else:
                                        st.warning("4자리 이상 입력하세요.")
                else:
                    st.info("등록된 학교가 없습니다.")


# ═══════════════════════════════════════════════════════════════════
#  사이드바 (로그인 후)
# ═══════════════════════════════════════════════════════════════════

def render_sidebar():
    with st.sidebar:
        # 모드 표시
        mode_badge = "🖥️ 로컬 전용" if st.session_state.local_mode else "🌐 학교 계정"
        st.markdown(f"""
        <div style="text-align:center; padding: 20px 0 12px;">
            <div style="font-size:2rem;">💊</div>
            <div style="font-weight:800; font-size:1.05rem; color:#fff; margin:4px 0;">보건실 관리</div>
            <div style="font-size:0.78rem; color:#AAA; margin-bottom:4px;">
                🏫 {st.session_state.school_name}
            </div>
            <div style="font-size:0.72rem; color:#888;">{mode_badge}</div>
        </div>
        <hr style="border-color:#333; margin:0 0 14px;">
        """, unsafe_allow_html=True)

        menus = [
            ("📊", "대시보드"),
            ("💊", "의약품 목록"),
            ("📥", "약품등록(스마트 업로드)"),
            ("➕", "약품등록(직접입력)"),
            ("📋", "입출고 이력"),
            ("📤", "내보내기"),
        ]
        for icon, name in menus:
            active = st.session_state.active_tab == name
            btn_type = "primary" if active else "secondary"
            if st.button(f"{icon}  {name}", key=f"nav_{name}",
                         use_container_width=True, type=btn_type):
                st.session_state.active_tab = name
                st.session_state.dashboard_filter = None
                st.session_state.stock_mid = None
                st.session_state.editing_mid = None
                st.rerun()

        st.markdown("<hr style='border-color:#333; margin:14px 0;'>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="font-size:0.75rem; color:#888; text-align:center; margin-bottom:10px;">
            📅 {date.today().strftime('%Y년 %m월 %d일')}
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚪  로그아웃", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            init_session()
            st.rerun()


# ═══════════════════════════════════════════════════════════════════
#  입출고 처리 팝업 모달 (st.dialog)
# ═══════════════════════════════════════════════════════════════════

@st.dialog("📦 입출고 / 재고 변동 처리")
def dialog_stock_modal(medicine_id: int):
    """입출고 처리를 위한 팝업 모달 대화상자"""
    med = db.get_medicine_by_id(medicine_id)
    if not med:
        st.error("해당 약품 정보를 찾을 수 없습니다.")
        if st.button("닫기"):
            st.rerun()
        return

    curr_stock = med.get("current_stock", 0) or 0
    spec_str = f" ({med['spec']})" if med.get("spec") else ""

    # 약품 기본 정보 요약 박스
    st.markdown(f"""
    <div style="background:#F0F7FF;border:1.5px solid #CBD5E0;border-radius:12px;
                padding:14px 18px;margin-bottom:16px;">
        <div style="font-size:1.15rem;font-weight:800;color:#1A1A2E;margin-bottom:4px;">
            💊 {med['name']}<span style="font-size:0.85rem;color:#64748B;font-weight:500;">{spec_str}</span>
        </div>
        <div style="font-size:0.9rem;color:#334155;">
            현재 보관 재고: <span style="font-size:1.2rem;font-weight:800;color:#0284C7;">{curr_stock}</span> {med.get('spec', '개')}
            &nbsp;·&nbsp; 분류: <strong>{med.get('category', '기타')}</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 1. 처리 구분 (라디오 버튼 - 가로 배열)
    action = st.radio(
        "📌 처리 구분 선택",
        ["불출 (사용)", "입고", "폐기"],
        horizontal=True,
        index=0,
        help="학생 투약 또는 소모 시 '불출', 신규 약품 수령 시 '입고', 기한 경과 등은 '폐기'를 선택하세요."
    )
    action_type = "불출" if "불출" in action else ("입고" if "입고" in action else "폐기")

    # 2. 수량 및 비고 입력
    col_qty, col_note = st.columns([1, 1.6])
    with col_qty:
        max_val = None if action_type == "입고" else max(curr_stock, 1)
        qty = st.number_input(
            f"{action_type} 수량",
            min_value=1,
            max_value=max_val,
            value=1,
            step=1,
            help="처리할 수량을 숫자로 입력하세요."
        )

    with col_note:
        default_placeholder = "예: 발열 학생 투약, 보건실 처치 등" if action_type == "불출" else ("예: 정기 구입 입고" if action_type == "입고" else "예: 유통기한 경과 폐기")
        note = st.text_input("비고 (사유 입력 - 선택사항)", placeholder=default_placeholder)

    # 예상 잔여 재고 계산 및 안내
    if action_type == "입고":
        expected = curr_stock + qty
        st.caption(f"ℹ️ 처리 후 예상 재고: **{curr_stock}** ➡️ **{expected}** {med.get('spec', '개')}")
    else:
        expected = max(0, curr_stock - qty)
        if qty > curr_stock:
            st.error(f"⚠️ 현재 재고({curr_stock})보다 많은 수량을 {action_type}할 수 없습니다.")
        else:
            st.caption(f"ℹ️ 처리 후 예상 재고: **{curr_stock}** ➡️ **{expected}** {med.get('spec', '개')}")

    st.markdown("<hr style='margin:16px 0 12px;border-color:#E2E8F0;'>", unsafe_allow_html=True)

    # 하단 버튼 배치: [확인], [취소], [원래대로 되돌리기]
    btn_col1, btn_col2, btn_col3 = st.columns([1.2, 1, 1.4])

    with btn_col1:
        if st.button("✅  확인", use_container_width=True, type="primary"):
            if action_type != "입고" and qty > curr_stock:
                st.error("재고가 부족합니다.")
            else:
                ok, msg = db.update_stock(st.session_state.school_id, medicine_id, action_type, qty, note)
                if ok:
                    st.toast(f"✅ {msg}", icon="📦")
                    st.rerun()
                else:
                    st.error(msg)

    with btn_col2:
        if st.button("❌  취소", use_container_width=True):
            st.rerun()

    with btn_col3:
        if st.button("↩️ 되돌리기", use_container_width=True, help="가장 최근에 처리한 1건의 입출고 작업을 직전 상태로 복원합니다."):
            ok, msg = db.rollback_last_stock_action(st.session_state.school_id, medicine_id)
            if ok:
                st.toast(f"↩️ {msg}", icon="🔄")
                st.rerun()
            else:
                st.warning(msg)


# ═══════════════════════════════════════════════════════════════════
#  의약품 정보 수정 팝업 모달 (st.dialog)
# ═══════════════════════════════════════════════════════════════════

@st.dialog("✏️ 의약품 정보 수정")
def dialog_edit_modal(medicine_id: int):
    """의약품 수정을 위한 팝업 모달 대화상자"""
    med = db.get_medicine_by_id(medicine_id)
    if not med:
        st.error("약품 정보를 찾을 수 없습니다.")
        if st.button("닫기"):
            st.rerun()
        return

    cat_opts = [""] + ut.CATEGORIES
    cur_cat_idx = cat_opts.index(med.get("category", "")) if med.get("category", "") in cat_opts else 0

    e1, e2 = st.columns(2)
    with e1:
        new_name = st.text_input("품명 *", value=med.get("name", ""))
        new_cat  = st.selectbox("분류 *", cat_opts, index=cur_cat_idx)
        new_spec = st.text_input("규격/단위", value=med.get("spec", ""))
        new_rec  = st.number_input("권장 재고", value=int(med.get("recommended_stock", 0) or 0), min_value=0)
    with e2:
        new_exp  = st.text_input("유효기한 (YYYY-MM-DD)", value=med.get("expiry_date", ""), placeholder="YYYY-MM-DD")
        new_loc  = st.text_input("보관 위치", value=med.get("location", ""))
        new_memo = st.text_area("관리 TIP / 메모", value=med.get("memo", ""), height=108)

    st.markdown("<hr style='margin:16px 0 12px;border-color:#E2E8F0;'>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("💾  저장", use_container_width=True, type="primary"):
            if not new_name.strip():
                st.error("품명을 입력해 주세요.")
            else:
                ok, msg = db.update_medicine(medicine_id, {
                    "name": new_name.strip(),
                    "category": new_cat,
                    "spec": new_spec.strip(),
                    "recommended_stock": new_rec,
                    "expiry_date": new_exp.strip(),
                    "location": new_loc.strip(),
                    "memo": new_memo.strip(),
                })
                if ok:
                    st.toast("✅ 수정되었습니다.", icon="💾")
                    st.rerun()
                else:
                    st.error(msg)
    with c2:
        if st.button("❌  취소", use_container_width=True):
            st.rerun()


# ═══════════════════════════════════════════════════════════════════
#  의약품 삭제 확인 팝업 모달 (st.dialog)
# ═══════════════════════════════════════════════════════════════════

@st.dialog("🗑️ 의약품 삭제 확인")
def dialog_delete_confirm_modal(medicine_id: int):
    """의약품 삭제 여부를 재확인하는 팝업 모달"""
    med = db.get_medicine_by_id(medicine_id)
    if not med:
        st.error("해당 약품 정보를 찾을 수 없습니다.")
        if st.button("닫기"):
            st.rerun()
        return

    st.markdown(f"""
    <div style="font-size:1.05rem;font-weight:700;color:#991B1B;background:#FEF2F2;padding:14px 18px;border-radius:10px;border:1px solid #FCA5A5;margin-bottom:14px;">
        ⚠️ <strong>[{med['name']}]</strong> 품목을 정말로 삭제하시겠습니까?
    </div>
    <div style="font-size:0.88rem;color:#4B5563;line-height:1.6;margin-bottom:12px;">
        삭제하시면 해당 품목의 <strong>현재 재고({med.get('current_stock', 0)}{med.get('spec', '개')}) 및 모든 입출고 이력</strong>이 함께 영구 삭제됩니다.
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🗑️ 영구 삭제", use_container_width=True, type="primary"):
            ok, msg = db.delete_medicines([medicine_id])
            if ok:
                st.toast(f"✅ {med['name']} 품목이 삭제되었습니다.", icon="🗑️")
                st.rerun()
            else:
                st.error(msg)
    with c2:
        if st.button("❌ 취소", use_container_width=True):
            st.rerun()


# ═══════════════════════════════════════════════════════════════════
#  대시보드 페이지
# ═══════════════════════════════════════════════════════════════════

def page_dashboard():
    school_id = st.session_state.school_id
    medicines = db.get_medicines(school_id)
    counts = ut.get_dashboard_counts(medicines)

    st.markdown(f"""
    <div class="top-bar" style="display:flex;align-items:center;justify-content:space-between;">
        <span style="font-size:1.15rem;font-weight:700;color:#fff;">📊 실시간 재고 현황 대시보드</span>
        <span style="font-size:0.82rem;color:#AAA;">
            {date.today().strftime('%Y년 %m월 %d일')} 기준 &nbsp;·&nbsp; 총 {len(medicines)}개 품목
        </span>
    </div>
    """, unsafe_allow_html=True)

    # ─── 대시보드 카드 4개 ────────────────────────────────────────
    cols = st.columns(4)
    card_configs = [
        (ut.STATUS_EXPIRED,  "#E63946", "🔴", "즉시 폐기 필요"),
        (ut.STATUS_EXPIRING, "#F4A261", "🟡", "90일 내 만료"),
        (ut.STATUS_LOW,      "#E76F51", "🚨", "재고 부족"),
        (ut.STATUS_OK,       "#2A9D8F", "✅", "정상 보관"),
    ]

    for col, (status, color, emoji, label) in zip(cols, card_configs):
        cnt = counts[status]
        is_active = st.session_state.dashboard_filter == status
        bg = "#F8F0FF" if is_active else "white"
        border = f"5px solid {color}"

        with col:
            st.markdown(f"""
            <div class="dash-card card-{'expired' if status == ut.STATUS_EXPIRED else 'expiring' if status == ut.STATUS_EXPIRING else 'low' if status == ut.STATUS_LOW else 'ok'}" style="border-left:{border}; background:{bg};">
                <span class="emoji">{emoji}</span>
                <div class="count" style="color:{color};">{cnt}</div>
                <div class="label">{label}</div>
                <div style="font-size:0.72rem;color:#999;margin-top:4px;">품목</div>
            </div>
            """, unsafe_allow_html=True)
            btn_label = "▼ 목록 숨기기" if is_active else "▶ 목록 보기"
            if st.button(btn_label, key=f"dash_btn_{status}", use_container_width=True):
                st.session_state.dashboard_filter = None if is_active else status
                st.rerun()

    # ─── 선택 카드 상태 품목 목록 ────────────────────────────────
    if st.session_state.dashboard_filter:
        fstatus = st.session_state.dashboard_filter
        filtered = ut.filter_by_status(medicines, fstatus)
        color = ut.STATUS_COLOR.get(fstatus, "#333")
        emoji = ut.STATUS_EMOJI.get(fstatus, "")

        st.markdown(f"""
        <div class="section-header" style="border-left:4px solid {color};">
            {emoji} {fstatus} 품목 목록 ({len(filtered)}개)
        </div>
        """, unsafe_allow_html=True)

        if not filtered:
            st.info("해당 상태의 품목이 없습니다. 👍")
        else:
            render_medicine_table(filtered, prefix="dash")

    # ─── 차트 ────────────────────────────────────────────────────
    if medicines:
        st.markdown('<div class="section-header">📈 카테고리별 현황</div>',
                    unsafe_allow_html=True)
        col_chart1, col_chart2 = st.columns(2)

        with col_chart1:
            st.markdown("**📊 분류별 보유 수량**")
            cat_df = pd.DataFrame(medicines)
            if "category" in cat_df.columns and "current_stock" in cat_df.columns:
                cat_df["category"] = cat_df["category"].fillna("").astype(str).str.strip()
                cat_df["current_stock"] = pd.to_numeric(
                    cat_df["current_stock"], errors="coerce"
                ).fillna(0)
                cat_counts = (
                    cat_df[cat_df["category"] != ""]
                    .groupby("category", as_index=False)["current_stock"].sum()
                    .rename(columns={"category": "분류", "current_stock": "보유 수량"})
                )
                if not cat_counts.empty:
                    # 등록된 분류 순서를 유지하고 분류마다 다른 막대 색상 적용
                    cat_order = [c for c in ut.CATEGORIES if c in cat_counts["분류"].values]
                    cat_order += [c for c in cat_counts["분류"] if c not in cat_order]
                    bar_colors = ["#604891", "#246D98", "#3AA6A3", "#0D8961",
                                  "#76AD49", "#F5A000", "#E58000"]
                    cat_colors = [bar_colors[i % len(bar_colors)] for i in range(len(cat_order))]
                    chart = (
                        alt.Chart(cat_counts)
                        .mark_bar()
                        .encode(
                            x=alt.X("분류:N", sort=cat_order,
                                    axis=alt.Axis(title="약품 분류", labelAngle=0,
                                                  labelFontSize=10, labelLimit=95)),
                            y=alt.Y("보유 수량:Q",
                                    axis=alt.Axis(title="보유 수량", format="d")),
                            color=alt.Color("분류:N",
                                            scale=alt.Scale(domain=cat_order,
                                                            range=cat_colors),
                                            legend=None),
                            tooltip=["분류", alt.Tooltip("보유 수량:Q", format=",.0f")],
                        )
                        .properties(height=220)
                    )
                    st.altair_chart(chart, use_container_width=True)

        with col_chart2:
            st.markdown("**🎯 재고 상태 분포**")
            status_data = [
                {"상태": "✅ 정상 보관", "품목수": counts.get(ut.STATUS_OK, 0)},
                {"상태": "🟡 3개월 내 만료", "품목수": counts.get(ut.STATUS_EXPIRING, 0)},
                {"상태": "🚨 재고 부족 (품목)", "품목수": counts.get(ut.STATUS_LOW, 0)},
                {"상태": "🔴 즉시 폐기 대상", "품목수": counts.get(ut.STATUS_EXPIRED, 0)},
            ]
            if sum(item["품목수"] for item in status_data) > 0:
                status_df = pd.DataFrame(status_data)
                total = status_df["품목수"].sum()
                status_df["비율"] = status_df["품목수"] / total * 100
                status_df["비율 표시"] = status_df["비율"].map(
                    lambda p: f"{p:.1f}%" if p >= 1 else (f"{p:.2f}%" if p > 0 else "0%")
                )
                status_colors = ["#10B981", "#F59E0B", "#EC4899", "#EF3340"]
                status_order = [item["상태"] for item in status_data]
                base = alt.Chart(status_df).encode(
                    theta=alt.Theta("품목수:Q", stack=True),
                    color=alt.Color("상태:N",
                                    scale=alt.Scale(domain=status_order,
                                                    range=status_colors),
                                    legend=alt.Legend(title=None, orient="right",
                                                      labelFontSize=11)),
                    tooltip=["상태", "품목수", alt.Tooltip("비율:Q", format=".1f")],
                )
                donut = base.mark_arc(innerRadius=64, outerRadius=102)
                percentages = base.mark_text(radius=116, fontSize=10,
                                             color="#475569").encode(
                    text=alt.Text("비율 표시:N")
                )
                chart2 = (donut + percentages).properties(height=220)
                st.altair_chart(chart2, use_container_width=True)

    # ─── 알림 배너 ───────────────────────────────────────────────
    expired_list  = ut.filter_by_status(medicines, ut.STATUS_EXPIRED)
    expiring_list = ut.filter_by_status(medicines, ut.STATUS_EXPIRING)
    low_list      = ut.filter_by_status(medicines, ut.STATUS_LOW)

    if expired_list or expiring_list or low_list:
        st.markdown('<div class="section-header">⚠️ 주의 알림</div>',
                    unsafe_allow_html=True)
        if expired_list:
            names = ", ".join(m["name"] for m in expired_list[:5])
            extra = f" 외 {len(expired_list)-5}개" if len(expired_list) > 5 else ""
            st.error(f"🔴 **즉시 폐기 필요**: {names}{extra}")
        if expiring_list:
            names = ", ".join(m["name"] for m in expiring_list[:5])
            extra = f" 외 {len(expiring_list)-5}개" if len(expiring_list) > 5 else ""
            st.warning(f"🟡 **90일 내 만료**: {names}{extra}")
        if low_list:
            names = ", ".join(m["name"] for m in low_list[:5])
            extra = f" 외 {len(low_list)-5}개" if len(low_list) > 5 else ""
            st.warning(f"🚨 **재고 부족**: {names}{extra}")


# ═══════════════════════════════════════════════════════════════════
#  의약품 테이블 렌더링 (공용 컴포넌트)
# ═══════════════════════════════════════════════════════════════════

def render_medicine_table(medicines: list[dict], prefix: str = "main"):
    """의약품 목록을 테이블 형태로 렌더링합니다."""
    if not medicines:
        st.info("🔍 표시할 약품이 없습니다.")
        return

    # 작업 버튼은 이 표에서만 가독성을 높입니다.
    st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] div[class*="st-key-{prefix}_edit_"] button,
    [data-testid="stAppViewContainer"] div[class*="st-key-{prefix}_stk_"] button,
    [data-testid="stAppViewContainer"] div[class*="st-key-{prefix}_del_"] button {{
        width: 100% !important;
        min-height: 46px !important;
        padding: 8px 5px !important;
        border-radius: 12px !important;
        font-size: 0.85rem !important;
        font-weight: 800 !important;
        white-space: nowrap !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    # 선택 체크박스는 표의 첫 열 한가운데에 배치합니다.
    st.markdown(f"""<style>
    div[class*="st-key-{prefix}_check_"] [data-testid="stCheckbox"] {{
        display: flex !important; justify-content: center !important;
    }}
    </style>""", unsafe_allow_html=True)

    # ── 컬럼 헤더 ─────────────────────────────────────────────────
    hcols = st.columns([0.48, 1.12, 1.32, 1.5, 0.43, 0.46, 1.05, 1.05, 0.55, 3.05], gap="small")
    headers = ["선택", "상태", "품명/규격", "분류", "현재고", "권장고",
               "유효기한", "잔여일", "위치", "작업"]
    for hcol, h in zip(hcols, headers):
        hcol.markdown(
            f"<div style='font-size:{'0.72rem' if h == '선택' else '0.8rem'};font-weight:800;color:#1A1A2E !important;"
            f"padding:4px 0;border-bottom:2px solid #CBD5E0;"
            f"text-align:center;white-space:nowrap;font-family:'Pretendard','Noto Sans KR',sans-serif;letter-spacing:-0.025em;'>{h}</div>",
            unsafe_allow_html=True,
        )

    for med in medicines:
        status = ut.get_medicine_status(med)
        emoji  = ut.STATUS_EMOJI.get(status, "")
        color  = ut.STATUS_COLOR.get(status, "#333")
        bg_s   = ut.STATUS_BG.get(status, "white")

        days = ut.days_until_expiry(med.get("expiry_date", ""))
        if days is None:
            days_str = "-"
        elif days < 0:
            days_str = f"⚠️{abs(days)}일 경과"
        elif days <= 7:
            days_str = f"🔥{days}일"
        else:
            days_str = f"{days}일"

        mid = med["id"]
        cb_key = f"{prefix}_check_{mid}"
        row_cols = st.columns([0.48, 1.12, 1.32, 1.5, 0.43, 0.46, 1.05, 1.05, 0.55, 3.05], gap="small")

        with row_cols[0]:
            st.checkbox("", key=cb_key, label_visibility="collapsed")

        with row_cols[1]:
            st.markdown(
                f"<div style='background:{bg_s};border-left:3px solid {color};"
                f"padding:9px 5px;border-radius:5px;font-size:0.75rem;"
                f"font-weight:700;color:{color};line-height:1.3;white-space:nowrap;text-align:center;'>"
                f"{emoji} {status}</div>",
                unsafe_allow_html=True,
            )

        with row_cols[2]:
            name_disp = med.get("name", "")
            spec_disp = med.get("spec", "")
            st.markdown(
                f"<div style='font-weight:700;font-size:0.92rem;color:#1A1A2E !important;padding:2px 0;text-align:center;'>"
                f"{name_disp}</div>"
                f"<div style='font-size:0.75rem;color:#64748B !important;font-weight:500;text-align:center;'>{spec_disp}</div>",
                unsafe_allow_html=True,
            )

        with row_cols[3]:
            cat = med.get("category", "") or "-"
            short_cat = cat.replace("·", "/")
            st.markdown(
                f"<div style='font-size:0.82rem;padding:4px 0;color:#1E293B !important;font-weight:600;text-align:center;'>{short_cat}</div>",
                unsafe_allow_html=True,
            )

        with row_cols[4]:
            cur = med.get("current_stock", 0) or 0
            rec = med.get("recommended_stock", 0) or 0
            stk_color = "#E63946" if (rec and cur < rec) else "#1A1A2E"
            st.markdown(
                f"<div style='font-weight:800;color:{stk_color} !important;font-size:0.95rem;"
                f"padding:4px 0;text-align:center;'>{cur}</div>",
                unsafe_allow_html=True,
            )

        with row_cols[5]:
            st.markdown(
                f"<div style='font-size:0.85rem;padding:4px 0;color:#334155 !important;font-weight:600;text-align:center;'>"
                f"{rec if rec else '-'}</div>",
                unsafe_allow_html=True,
            )

        with row_cols[6]:
            d = ut.parse_expiry_date(med.get("expiry_date", ""))
            disp = d.strftime("%Y-%m-%d") if d else (med.get("expiry_date", "") or "-")
            st.markdown(
                f"<div style='font-size:0.82rem;padding:4px 0;color:#1E293B !important;font-weight:600;text-align:center;'>{disp}</div>",
                unsafe_allow_html=True,
            )

        with row_cols[7]:
            st.markdown(
                f"<div style='font-size:0.8rem;padding:4px 0;color:#1E293B !important;font-weight:600;white-space:nowrap;text-align:center;'>{days_str}</div>",
                unsafe_allow_html=True,
            )

        with row_cols[8]:
            loc = med.get("location", "") or "-"
            st.markdown(
                f"<div style='font-size:0.8rem;padding:4px 0;color:#334155 !important;text-align:center;'>{loc}</div>",
                unsafe_allow_html=True,
            )

        with row_cols[9]:
            a1, a2, a3 = st.columns([1, 1, 1], gap="small")
            with a1:
                if st.button("✏️ 수정", key=f"{prefix}_edit_{mid}", help="수정", use_container_width=True):
                    dialog_edit_modal(mid)
            with a2:
                if st.button("📦 입출고", key=f"{prefix}_stk_{mid}", help="입출고", use_container_width=True):
                    dialog_stock_modal(mid)
            with a3:
                if st.button("🗑️ 삭제", key=f"{prefix}_del_{mid}", help="삭제", use_container_width=True):
                    dialog_delete_confirm_modal(mid)

    # ── 일괄 삭제 버튼 ────────────────────────────────────────────
    st.markdown("<div style='margin-top:8px;'></div>", unsafe_allow_html=True)
    del_col, _ = st.columns([1.2, 4])
    with del_col:
        if st.button("🗑️ 선택 항목 삭제", key=f"{prefix}_bulk_del"):
            ids_to_del = [
                m["id"] for m in medicines
                if st.session_state.get(f"{prefix}_check_{m['id']}", False)
            ]
            if not ids_to_del:
                st.warning("삭제할 항목을 선택해 주세요.")
            else:
                ok, msg = db.delete_medicines(ids_to_del)
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)


# ═══════════════════════════════════════════════════════════════════
#  의약품 목록 페이지
# ═══════════════════════════════════════════════════════════════════

def page_medicine_list():
    school_id = st.session_state.school_id
    st.markdown('<div class="section-header">💊 의약품 목록 관리</div>',
                unsafe_allow_html=True)

    # ── 검색 바 ───────────────────────────────────────────────────
    st.markdown("**🔍 검색 / 필터**")
    sc1, sc2, sc3, sc4 = st.columns([1.3, 2, 0.6, 0.6])
    with sc1:
        cat_opts = ["전체"] + ut.CATEGORIES
        sel_cat = st.selectbox(
            "분류 선택", cat_opts,
            index=cat_opts.index(st.session_state.search_category)
            if st.session_state.search_category in cat_opts else 0,
            key="sel_cat_input",
        )
    with sc2:
        kw = st.text_input(
            "품명/위치 검색",
            value=st.session_state.search_keyword,
            placeholder="검색어 입력...",
            key="search_kw_input",
        )
    with sc3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔍 검색", use_container_width=True):
            st.session_state.search_category = sel_cat
            st.session_state.search_keyword  = kw
            st.session_state.search_executed = True
            st.rerun()
    with sc4:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 초기화", use_container_width=True):
            st.session_state.search_keyword  = ""
            st.session_state.search_category = "전체"
            st.session_state.search_executed = False
            st.rerun()

    # ── 약품 로드 ─────────────────────────────────────────────────
    medicines = db.get_medicines(
        school_id,
        category=st.session_state.search_category
        if st.session_state.search_category != "전체" else None,
        search=st.session_state.search_keyword or None,
    )

    # ── 상태 탭 (각 탭에서 테이블만 렌더, 모달은 위에서 처리) ────
    status_tabs = st.tabs(["전체", "🔴 즉시 폐기", "🟡 교체 준비", "🚨 재고 부족", "✅ 정상"])
    tab_status_map = [None, ut.STATUS_EXPIRED, ut.STATUS_EXPIRING,
                      ut.STATUS_LOW, ut.STATUS_OK]

    for tab, status_filter in zip(status_tabs, tab_status_map):
        with tab:
            display_list = (
                [m for m in medicines if ut.get_medicine_status(m) == status_filter]
                if status_filter else medicines
            )
            st.caption(f"총 {len(display_list)}개 품목")
            render_medicine_table(
                display_list,
                prefix=f"list_{status_filter or 'all'}",
            )


# ═══════════════════════════════════════════════════════════════════
#  약품 등록 페이지
# ═══════════════════════════════════════════════════════════════════

def page_add_medicine():
    st.markdown('<div class="section-header">➕ 새 약품 등록</div>',
                unsafe_allow_html=True)

    # OCR 연결 안내 (prefill 세션이 있을 때)
    prefill_name   = st.session_state.pop("prefill_name",   "")
    prefill_expiry = st.session_state.pop("prefill_expiry", "")
    if prefill_name or prefill_expiry:
        st.info(
            f"📷 OCR에서 연결된 항목: **{prefill_name}** / 유통기한: **{prefill_expiry}**\n\n"
            "아래 폼에 자동 채워졌습니다. 나머지 항목을 채워 등록하세요."
        )

    st.markdown("""
    <div style="background:#EFF6FF;border-radius:10px;padding:12px 16px;margin-bottom:16px;
                font-size:0.88rem;color:#1E3A5F;border-left:3px solid #3B82F6;">
        ✳️ <strong>필수 입력</strong>: 분류, 품명, 규격/단위, 입고 수량, 유효기한
        &nbsp;&nbsp;·&nbsp;&nbsp; 그 외 항목은 선택 입력
    </div>
    """, unsafe_allow_html=True)

    with st.form("add_medicine_form", clear_on_submit=True):
        st.markdown("#### 📋 기본 정보")
        row1 = st.columns([1.5, 2, 1.5])
        with row1[0]:
            category = st.selectbox("분류 ✳️", [""] + ut.CATEGORIES,
                                    format_func=lambda x: "-- 분류를 선택하세요 --" if x == "" else x)
        with row1[1]:
            name = st.text_input("품명 ✳️", value=prefill_name, placeholder="예: 타이레놀 500mg")
        with row1[2]:
            spec = st.text_input("규격/단위 ✳️", placeholder="예: 정, mg, mL")

        st.markdown("#### 📦 재고 및 유효기한")
        row2 = st.columns([1, 1, 1.5, 1])
        with row2[0]:
            current_stock = st.number_input("입고 수량 ✳️", min_value=0, value=0)
        with row2[1]:
            recommended_stock = st.number_input("권장 재고 (선택)", min_value=0, value=0)
        with row2[2]:
            expiry_date = st.text_input(
                "유효기한 ✳️",
                value=prefill_expiry,
                placeholder="YYYY-MM-DD 또는 YYYY-MM",
                help="예: 2026-12-31 또는 2026-12",
            )
        with row2[3]:
            preview = ut.parse_expiry_date(expiry_date)
            if preview:
                days = (preview - date.today()).days
                clr = "#E63946" if days < 0 else ("#F4A261" if days <= 90 else "#2A9D8F")
                msg = "⚠️ 기한 경과" if days < 0 else f"잔여 {days}일"
                st.markdown(
                    f"<div style='margin-top:28px;font-size:0.82rem;"
                    f"color:{clr};font-weight:700;'>{msg}</div>",
                    unsafe_allow_html=True,
                )

        st.markdown("#### 📍 기타 정보 (선택)")
        row3 = st.columns([1.5, 1.5, 2])
        with row3[0]:
            location = st.text_input("보관 위치", placeholder="예: 약장 1-A")
        with row3[1]:
            memo = st.text_area("관리 TIP / 메모", placeholder="보관 주의사항, 사용 지침 등",
                                height=68)

        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("✅ 등록하기", use_container_width=True, type="primary", key="btn_medicine_register")

    if submitted:
        errors = []
        if not category:
            errors.append("분류를 선택해 주세요.")
        if not name.strip():
            errors.append("품명을 입력해 주세요.")
        if not spec.strip():
            errors.append("규격/단위를 입력해 주세요.")
        if current_stock <= 0:
            errors.append("입고 수량은 1 이상이어야 합니다.")
        if not expiry_date.strip():
            errors.append("유효기한을 입력해 주세요.")
        elif not ut.parse_expiry_date(expiry_date):
            errors.append("유효기한 형식이 올바르지 않습니다. (예: 2026-12-31 또는 2026-12)")

        if errors:
            for e in errors:
                st.error(f"❌ {e}")
        else:
            try:
                ok, msg = db.add_medicine(st.session_state.school_id, {
                    "category": category,
                    "name": name.strip(),
                    "spec": spec.strip(),
                    "current_stock": current_stock,
                    "recommended_stock": recommended_stock,
                    "expiry_date": expiry_date.strip(),
                    "location": location.strip(),
                    "memo": memo.strip(),
                })
                if ok:
                    st.success(f"✅ {msg}")
                    st.balloons()
                else:
                    st.error(f"❌ {msg}")
            except Exception as e:
                st.error(f"❌ 등록 중 오류가 발생했습니다: {str(e)}")


# ═══════════════════════════════════════════════════════════════════
#  스마트 업로드 페이지
# ═══════════════════════════════════════════════════════════════════

def page_smart_upload():
    st.markdown('<div class="section-header">📥 스마트 업로드</div>',
                unsafe_allow_html=True)

    # ── 상단 초기화 버튼 (언제든지 접근 가능) ─────────────────────
    with st.expander("⚠️ 오류 발생 시 또는 처음부터 다시 시작하려면 클릭"):
        st.markdown("파일 업로드 중 오류가 났거나, 이전 작업을 초기화하고 싶을 때 아래 버튼을 누르세요.")
        if st.button("🔄 OCR / 업로드 상태 초기화 (처음으로 돌아가기)", type="primary",
                     key="reset_upload_state"):
            st.session_state.ocr_rows = None
            st.session_state.ocr_error = None
            st.session_state.excel_error = None
            st.session_state.excel_records = None
            st.rerun()

    tab_ocr, tab_excel = st.tabs(["📷 사진 OCR 품명·유통기한 인식", "📊 엑셀 일괄 업로드"])

    # ═══════════════════════════════════════════════════════════════
    # 탭 1: 사진 OCR
    # ═══════════════════════════════════════════════════════════════
    with tab_ocr:
        st.markdown("""
        <div style="background:#FFF9E6;border-radius:10px;padding:14px 18px;margin:8px 0;
                    border-left:3px solid #F4A261;font-size:0.88rem;">
            📷 <strong>약품 사진이나 납품서 사진을 업로드하면 품명과 유통기한을 자동으로 인식합니다.</strong><br>
            인식된 내용을 직접 수정한 뒤 약품 등록에 활용하세요.<br>
            <span style="color:#888;">※ 텍스트가 선명하고 정면으로 찍은 사진일수록 인식률이 높습니다.</span>
        </div>
        """, unsafe_allow_html=True)

        # ── 오류 메시지 표시 (이전 실행에서 발생한 오류) ──────────
        if st.session_state.ocr_error:
            st.error(f"""
❌ **이미지 처리 중 오류가 발생했습니다.**

{st.session_state.ocr_error}

> 💡 파일 형식(JPG, PNG)을 확인하고, 손상되지 않은 파일인지 점검해 주세요.
> 위 초기화 버튼을 눌러 다시 시도하세요.
""")
            if st.button("🔄 OCR 초기화", key="ocr_err_reset"):
                st.session_state.ocr_error = None
                st.session_state.ocr_rows = None
                st.rerun()

        uploaded_img = st.file_uploader(
            "약품 / 납품서 사진 업로드 (JPG, PNG)",
            type=["jpg", "jpeg", "png"],
            key="ocr_upload",
            help="약품 라벨이나 납품서 전체 사진을 업로드하세요. 품명과 유통기한을 자동으로 찾아드립니다.",
        )

        if uploaded_img is not None:
            col_img, col_result = st.columns([1, 1.2])

            with col_img:
                st.image(uploaded_img, caption="업로드된 사진", use_container_width=True)

            with col_result:
                st.markdown("**🔍 OCR 인식 결과**")

                # 아직 인식 결과가 없으면 실행
                if st.session_state.ocr_rows is None and st.session_state.ocr_error is None:
                    with st.spinner("📖 사진을 분석하는 중입니다... 잠시 기다려 주세요."):
                        try:
                            image_bytes = uploaded_img.read()
                            if not image_bytes:
                                st.session_state.ocr_error = "파일을 읽을 수 없습니다. 다른 파일을 선택해 주세요."
                                st.rerun()
                            rows, ocr_method = run_ocr_detection(image_bytes)
                            st.session_state.ocr_rows = rows
                            st.session_state.ocr_error = None
                        except MemoryError:
                            st.session_state.ocr_error = (
                                "이미지가 너무 커서 메모리가 부족합니다.\n"
                                "더 작은 파일(5MB 이하)로 다시 시도해 주세요."
                            )
                            st.session_state.ocr_rows = None
                            st.rerun()
                        except Exception as e:
                            st.session_state.ocr_error = (
                                f"파일을 읽을 수 없습니다. 파일 형식이나 내용을 확인해 주세요.\n"
                                f"오류 원인: {str(e)}"
                            )
                            st.session_state.ocr_rows = None
                            st.rerun()

                ocr_rows = st.session_state.get("ocr_rows")

                if ocr_rows is None:
                    # 아직 오류 처리 중이거나 대기 중
                    pass
                elif len(ocr_rows) == 0:
                    st.warning("""
⚠️ **품명 또는 유통기한을 자동으로 인식하지 못했습니다.**

다음 중 하나를 시도해 보세요:
- 유통기한 부분을 클로즈업하여 다시 찍어 업로드
- 아래 수동 입력 테이블에 직접 입력
                    """)
                    # OCR 실패 시에도 수동 입력 가능하도록 빈 테이블 제공
                    st.session_state.ocr_rows = [{"name": "", "expiry": ""}]
                    st.rerun()
                else:
                    st.success(f"✅ {len(ocr_rows)}개 항목 인식 완료")
                    st.caption("인식된 내용을 아래에서 직접 수정할 수 있습니다.")

            # ── 인식 결과 편집 테이블 ──────────────────────────────
            if st.session_state.ocr_rows is not None:
                st.markdown("---")
                st.markdown("### ✏️ 인식 결과 확인 및 수정")
                st.caption("품명과 유통기한(YYYY-MM-DD 형식)을 확인하고 필요하면 직접 수정하세요.")

                rows = st.session_state.ocr_rows
                updated_rows = []

                for i, row in enumerate(rows):
                    c_num, c_name, c_exp, c_del = st.columns([0.3, 2.2, 1.5, 0.5])
                    with c_num:
                        st.markdown(
                            f"<div style='padding:8px 0;font-weight:700;color:#334155;'>{i+1}</div>",
                            unsafe_allow_html=True,
                        )
                    with c_name:
                        new_name = st.text_input(
                            "품명",
                            value=row.get("name", ""),
                            key=f"ocr_name_{i}",
                            placeholder="품명 입력",
                            label_visibility="collapsed",
                        )
                    with c_exp:
                        new_exp = st.text_input(
                            "유통기한",
                            value=row.get("expiry", ""),
                            key=f"ocr_exp_{i}",
                            placeholder="YYYY-MM-DD",
                            label_visibility="collapsed",
                        )
                    with c_del:
                        if st.button("🗑️", key=f"ocr_del_{i}", help="이 행 삭제"):
                            continue  # 이 행을 updated_rows에 추가하지 않아 삭제
                    updated_rows.append({"name": new_name, "expiry": new_exp})

                # 행 추가 버튼
                add_col, _ = st.columns([1, 3])
                with add_col:
                    if st.button("➕ 행 추가", key="ocr_add_row"):
                        updated_rows.append({"name": "", "expiry": ""})

                st.session_state.ocr_rows = updated_rows

                # ── 유효성 체크 및 등록 버튼 ──────────────────────
                valid_rows = [
                    r for r in updated_rows
                    if r.get("name", "").strip() and ut.parse_expiry_date(r.get("expiry", ""))
                ]
                invalid_exp = [
                    r for r in updated_rows
                    if r.get("expiry", "").strip() and not ut.parse_expiry_date(r.get("expiry", ""))
                ]

                if invalid_exp:
                    st.warning(
                        f"⚠️ 유통기한 형식이 올바르지 않은 행이 {len(invalid_exp)}개 있습니다. "
                        f"YYYY-MM-DD 형식으로 입력해 주세요."
                    )

                if valid_rows:
                    st.markdown(f"**등록 가능한 품목: {len(valid_rows)}개**")
                    if st.button(
                        f"✅ {len(valid_rows)}개 품목 약품 등록(직접입력) 페이지로 연결",
                        type="primary",
                        key="ocr_goto_register",
                    ):
                        # 첫 번째 항목 정보를 직접입력 폼에 연결
                        first = valid_rows[0]
                        st.session_state["prefill_name"] = first["name"]
                        st.session_state["prefill_expiry"] = first["expiry"]
                        st.session_state.active_tab = "약품등록(직접입력)"
                        st.info(
                            f"💡 '{first['name']}' 항목 정보가 직접입력 폼에 자동으로 채워집니다. "
                            f"나머지 항목은 순서대로 직접 등록해 주세요."
                        )
                        st.rerun()
                else:
                    st.info("품명과 유통기한을 모두 입력한 항목이 없습니다. 위 테이블을 채워 주세요.")

    # ═══════════════════════════════════════════════════════════════
    # 탭 2: 엑셀 일괄 업로드
    # ═══════════════════════════════════════════════════════════════
    with tab_excel:
        st.markdown("""
        <div style="background:#F0FFF4;border-radius:10px;padding:14px 18px;margin:8px 0;
                    border-left:3px solid #2A9D8F;font-size:0.88rem;">
            📊 <strong>엑셀(xlsx) 또는 CSV 파일로 약품을 일괄 등록합니다.</strong><br>
            아래에서 양식을 다운로드하여 작성 후 업로드해 주세요.
        </div>
        """, unsafe_allow_html=True)

        # ── 오류 메시지 표시 ───────────────────────────────────────
        if st.session_state.excel_error:
            st.error(f"""
❌ **파일을 읽을 수 없습니다. 파일 형식이나 내용을 확인해 주세요.**

{st.session_state.excel_error}

> 💡 아래 양식을 다운로드하여 올바른 형식으로 작성 후 다시 업로드해 주세요.
""")
            if st.button("🔄 엑셀 오류 초기화", key="excel_err_reset"):
                st.session_state.excel_error = None
                st.session_state.excel_records = None
                st.rerun()

        template_bytes = ut.create_upload_template()
        st.download_button(
            "📥 업로드 양식 다운로드 (Excel)",
            data=template_bytes,
            file_name="의약품_일괄등록_양식.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        st.markdown("---")

        uploaded_excel = st.file_uploader(
            "엑셀/CSV 파일 업로드",
            type=["xlsx", "xls", "csv"],
            key="excel_upload",
            help="위에서 다운로드한 양식을 채워서 업로드하세요.",
        )

        if uploaded_excel is not None:
            try:
                file_bytes = uploaded_excel.read()
                if not file_bytes:
                    st.session_state.excel_error = "파일이 비어 있습니다. 다른 파일을 선택해 주세요."
                    st.session_state.excel_records = None
                    st.rerun()
                records, errors = ut.parse_upload_excel(file_bytes)
                st.session_state.excel_error = None
                st.session_state.excel_records = records
            except MemoryError:
                st.session_state.excel_error = "파일이 너무 큽니다. 더 작은 파일로 나눠서 업로드해 주세요."
                st.session_state.excel_records = None
                uploaded_excel = None
                st.rerun()
            except Exception as e:
                st.session_state.excel_error = (
                    f"파일을 읽을 수 없습니다. 파일 형식이나 내용을 확인해 주세요.\n"
                    f"오류 원인: {str(e)}"
                )
                st.session_state.excel_records = None
                uploaded_excel = None
                st.rerun()

            if errors:
                st.warning("⚠️ 일부 행을 건너뜁니다:")
                for e in errors:
                    st.caption(e)

            records = st.session_state.get("excel_records") or []
            if records:
                st.markdown(f"**총 {len(records)}개 품목 미리보기:**")
                st.dataframe(pd.DataFrame(records), use_container_width=True, height=250)
                if st.button(f"✅ {len(records)}개 품목 일괄 등록", type="primary"):
                    with st.spinner("등록 중..."):
                        try:
                            cnt, errs = db.bulk_insert_medicines(
                                st.session_state.school_id, records
                            )
                            st.success(f"✅ {cnt}개 품목 등록 완료!")
                            for e in errs:
                                st.caption(f"⚠️ {e}")
                            st.session_state.excel_records = None
                            if cnt > 0:
                                st.balloons()
                        except Exception as e:
                            st.error(
                                f"❌ 등록 중 오류가 발생했습니다: {str(e)}\n"
                                "데이터 형식을 확인하고 다시 시도해 주세요."
                            )
            else:
                st.error("❌ 등록할 수 있는 품목이 없습니다. 양식을 확인해 주세요.")


def run_ocr_detection(image_bytes: bytes) -> tuple[list[dict], str]:
    """
    이미지에서 품명과 유통기한을 OCR로 인식합니다.
    반환: (rows, error_msg)
      - rows: [{"name": str, "expiry": str}, ...] — 인식된 품목 목록
      - error_msg: 오류 발생 시 메시지 (정상이면 "")
    OCR 엔진 우선순위: easyocr → pytesseract → (텍스트 추출 없음, 수동 입력 유도)
    """
    if not image_bytes:
        return [], "업로드된 이미지가 비어 있습니다."

    full_text = ""
    ocr_method = "없음"

    # ── 1. 이미지 유효성 검사 ───────────────────────────────────────
    try:
        from PIL import Image
        img = Image.open(io.BytesIO(image_bytes))
        img.verify()  # 손상된 파일 감지
        # verify() 후에는 재오픈 필요
        img = Image.open(io.BytesIO(image_bytes))
        # 너무 큰 이미지 자동 축소 (메모리 초과 방지)
        MAX_SIDE = 2000
        if max(img.width, img.height) > MAX_SIDE:
            ratio = MAX_SIDE / max(img.width, img.height)
            img = img.resize(
                (int(img.width * ratio), int(img.height * ratio)),
                Image.LANCZOS
            )
            # 축소된 이미지를 bytes로 재변환
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=90)
            image_bytes = buf.getvalue()
    except Exception as e:
        return [], f"이미지 파일을 열 수 없습니다: {str(e)}\n지원 형식: JPG, PNG"

    # ── 2. OCR 텍스트 추출 시도 ─────────────────────────────────────
    try:
        import easyocr
        try:
            reader = easyocr.Reader(["ko", "en"], gpu=False, verbose=False)
            result = reader.readtext(image_bytes, detail=0)
            full_text = "\n".join(result)
            ocr_method = "easyocr"
        except Exception as e:
            full_text = ""
            ocr_method = f"easyocr 오류({str(e)[:60]})"
    except ImportError:
        pass

    if not full_text:
        try:
            import pytesseract
            from PIL import Image as PILImage
            pil_img = PILImage.open(io.BytesIO(image_bytes))
            full_text = pytesseract.image_to_string(pil_img, lang="kor+eng")
            ocr_method = "pytesseract"
        except ImportError:
            ocr_method = "미설치"
        except Exception as e:
            full_text = ""
            ocr_method = f"pytesseract 오류({str(e)[:60]})"

    # ── 3. 날짜 패턴 추출 ───────────────────────────────────────────
    date_pattern = re.compile(
        r"\d{4}[-./]\d{1,2}[-./]\d{1,2}"
        r"|\d{4}[-./]\d{1,2}"
        r"|\d{8}"
        r"|\d{6}"
    )

    def normalize_date(raw: str) -> str:
        if re.match(r"^\d{8}$", raw):
            return f"{raw[:4]}-{raw[4:6]}-{raw[6:]}"
        elif re.match(r"^\d{6}$", raw):
            return f"{raw[:4]}-{raw[4:]}"
        else:
            return re.sub(r"[./]", "-", raw)

    # ── 4. 행(line) 단위로 품명 + 유통기한 쌍 추출 ─────────────────
    rows = []
    seen_dates = set()

    if full_text:
        lines = [l.strip() for l in full_text.splitlines() if l.strip()]
        for line in lines:
            dates_in_line = date_pattern.findall(line)
            # 날짜 없는 줄은 품명 후보
            if not dates_in_line:
                continue
            # 날짜가 있는 줄에서 품명(날짜 제외 부분)과 날짜를 추출
            name_part = date_pattern.sub("", line).strip()
            # 번호/특수문자로만 된 품명 후보 제거
            name_part = re.sub(r"^[\d\s\.\-\(\)\[\]①②③④⑤⑥⑦⑧⑨⑩]+", "", name_part).strip()
            for raw_date in dates_in_line:
                nd = normalize_date(raw_date)
                if ut.parse_expiry_date(nd) and nd not in seen_dates:
                    seen_dates.add(nd)
                    rows.append({"name": name_part, "expiry": nd})

        # 품명이 없는 날짜들은 품명 빈칸으로 추가
        if not rows:
            for raw_date in date_pattern.findall(full_text):
                nd = normalize_date(raw_date)
                if ut.parse_expiry_date(nd) and nd not in seen_dates:
                    seen_dates.add(nd)
                    rows.append({"name": "", "expiry": nd})

    return rows, ocr_method


# ═══════════════════════════════════════════════════════════════════
#  입출고 이력 페이지
# ═══════════════════════════════════════════════════════════════════

def page_history():
    school_id = st.session_state.school_id
    st.markdown('<div class="section-header">📋 입출고 이력</div>', unsafe_allow_html=True)

    history = db.get_stock_history(school_id, limit=500)
    if not history:
        st.info("📭 입출고 이력이 없습니다.")
        return

    fc1, fc2, fc3 = st.columns([1.5, 1.5, 0.8])
    with fc1:
        all_names = ["전체"] + sorted({h["medicine_name"] for h in history})
        filter_name = st.selectbox("품명 필터", all_names, key="hist_name_filter")
    with fc2:
        filter_action = st.selectbox("구분 필터", ["전체", "입고", "출고", "폐기"],
                                     key="hist_action_filter")
    with fc3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔍 검색", key="hist_search_btn"):
            st.rerun()

    filtered = history
    if filter_name != "전체":
        filtered = [h for h in filtered if h["medicine_name"] == filter_name]
    if filter_action != "전체":
        filtered = [h for h in filtered if h["action_type"] == filter_action]

    st.caption(f"총 {len(filtered)}건")

    # 헤더
    hcols = st.columns([0.3, 0.9, 1.8, 0.7, 0.6, 0.8, 1.5])
    for h, t in zip(hcols, ["선택", "처리일", "품명", "구분", "수량", "처리후재고", "비고"]):
        h.markdown(
            f"<div style='font-size:0.8rem;font-weight:800;color:#1A1A2E !important;"
            f"border-bottom:2px solid #CBD5E0;padding:4px 0;'>{t}</div>",
            unsafe_allow_html=True,
        )

    action_colors = {"입고": "#2A9D8F", "출고": "#4A90E2", "폐기": "#E63946"}

    for rec in filtered:
        rcols = st.columns([0.3, 0.9, 1.8, 0.7, 0.6, 0.8, 1.5])
        with rcols[0]:
            st.checkbox("", key=f"hist_chk_{rec['id']}", label_visibility="collapsed")
        with rcols[1]:
            st.markdown(
                f"<div style='font-size:0.82rem;color:#1E293B !important;font-weight:600;padding:4px 0;'>{rec.get('action_date','')}</div>",
                unsafe_allow_html=True,
            )
        with rcols[2]:
            st.markdown(
                f"<div style='font-weight:700;font-size:0.9rem;color:#1A1A2E !important;padding:4px 0;'>"
                f"{rec.get('medicine_name','')}</div>",
                unsafe_allow_html=True,
            )
        with rcols[3]:
            atype  = rec.get("action_type", "")
            acolor = action_colors.get(atype, "#1A1A2E")
            st.markdown(
                f"<div style='color:{acolor};font-weight:800;font-size:0.85rem;"
                f"padding:4px 0;'>{atype}</div>",
                unsafe_allow_html=True,
            )
        with rcols[4]:
            st.markdown(
                f"<div style='font-size:0.88rem;color:#1A1A2E !important;font-weight:700;padding:4px 0;'>{rec.get('quantity',0)}</div>",
                unsafe_allow_html=True,
            )
        with rcols[5]:
            st.markdown(
                f"<div style='font-size:0.88rem;color:#1A1A2E !important;font-weight:700;padding:4px 0;'>{rec.get('stock_after',0)}</div>",
                unsafe_allow_html=True,
            )
        with rcols[6]:
            st.markdown(
                f"<div style='font-size:0.82rem;color:#4A5568 !important;padding:4px 0;'>"
                f"{rec.get('note','') or '-'}</div>",
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)
    dl_col, del_col, _ = st.columns([1.5, 1.5, 2])
    with dl_col:
        df = ut.history_to_dataframe(filtered)
        excel_bytes = ut.to_excel_bytes(df, sheet_name="입출고이력")
        st.download_button(
            "📥 이력 엑셀 다운로드",
            data=excel_bytes,
            file_name=f"입출고이력_{date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    with del_col:
        if st.button("🗑️ 선택 이력 삭제", key="del_hist_btn"):
            ids_to_del = [
                rec["id"] for rec in filtered
                if st.session_state.get(f"hist_chk_{rec['id']}", False)
            ]
            if not ids_to_del:
                st.warning("삭제할 이력을 선택해 주세요.")
            else:
                ok, msg = db.delete_history_records(ids_to_del)
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)


# ═══════════════════════════════════════════════════════════════════
#  내보내기 페이지
# ═══════════════════════════════════════════════════════════════════

def page_export():
    school_id   = st.session_state.school_id
    school_name = st.session_state.school_name
    medicines   = db.get_medicines(school_id)

    st.markdown('<div class="section-header">📤 데이터 내보내기</div>', unsafe_allow_html=True)
    if not medicines:
        st.info("📭 내보낼 의약품 데이터가 없습니다.")
        return

    st.caption(f"💊 현재 총 {len(medicines)}개 품목")

    col1, col2, col3 = st.columns(3)
    card_style = ("background:#FFFFFF !important;border-radius:14px;padding:20px;"
                  "box-shadow:0 2px 10px rgba(0,0,0,0.08);border:1px solid #E2E8F0;min-height:140px;")

    with col1:
        st.markdown(f'<div style="{card_style}border-top:4px solid #4A90E2 !important;">'
                    '<div style="font-size:1.8rem;">📊</div>'
                    '<div style="font-weight:700;font-size:1.05rem;color:#1A1A2E !important;margin:8px 0 4px;">현재 재고 엑셀</div>'
                    '<div style="font-size:0.85rem;color:#4A5568 !important;">전체 약품 현황 엑셀 다운로드</div>'
                    '</div>', unsafe_allow_html=True)
        df_main   = ut.medicines_to_dataframe(medicines)
        excel_main = ut.to_excel_bytes(df_main, sheet_name="의약품현황")
        st.download_button("📥 다운로드", data=excel_main,
                           file_name=f"{school_name}_의약품현황_{date.today()}.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                           use_container_width=True, key="dl_main")

    with col2:
        st.markdown(f'<div style="{card_style}border-top:4px solid #2A9D8F !important;">'
                    '<div style="font-size:1.8rem;">🏛️</div>'
                    '<div style="font-weight:700;font-size:1.05rem;color:#1A1A2E !important;margin:8px 0 4px;">에듀파인 등록 양식</div>'
                    '<div style="font-size:0.85rem;color:#4A5568 !important;">에듀파인 업로드용 서식</div>'
                    '</div>', unsafe_allow_html=True)
        excel_edu = ut.create_edupaing_template(medicines)
        st.download_button("📥 다운로드", data=excel_edu,
                           file_name=f"{school_name}_에듀파인양식_{date.today()}.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                           use_container_width=True, key="dl_edu")

    with col3:
        st.markdown(f'<div style="{card_style}border-top:4px solid #F4A261 !important;">'
                    '<div style="font-size:1.8rem;">📋</div>'
                    '<div style="font-weight:700;font-size:1.05rem;color:#1A1A2E !important;margin:8px 0 4px;">관리대장 출력</div>'
                    '<div style="font-size:0.85rem;color:#4A5568 !important;">보건실 의약품 관리대장 (점검용)</div>'
                    '</div>', unsafe_allow_html=True)
        excel_ledger = ut.create_ledger_template(medicines, school_name)
        st.download_button("📥 다운로드", data=excel_ledger,
                           file_name=f"{school_name}_관리대장_{date.today()}.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                           use_container_width=True, key="dl_ledger")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">📋 일괄 등록 양식 다운로드</div>',
                unsafe_allow_html=True)
    c1, _ = st.columns([1.5, 2.5])
    with c1:
        template_bytes = ut.create_upload_template()
        st.download_button(
            "📥 업로드 양식 다운로드 (빈 양식)",
            data=template_bytes,
            file_name="의약품_일괄등록_양식.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    st.markdown('<div class="section-header">👀 현재 재고 미리보기</div>',
                unsafe_allow_html=True)
    st.dataframe(ut.medicines_to_dataframe(medicines), use_container_width=True, height=400)


# ═══════════════════════════════════════════════════════════════════
#  메인 라우팅
# ═══════════════════════════════════════════════════════════════════

def main():
    if not st.session_state.logged_in:
        page_login()
        return

    render_sidebar()

    tab = st.session_state.active_tab
    try:
        if tab == "대시보드":
            page_dashboard()
        elif tab == "의약품 목록":
            page_medicine_list()
        elif tab == "약품등록(스마트 업로드)":
            page_smart_upload()
        elif tab == "약품등록(직접입력)":
            page_add_medicine()
        elif tab == "입출고 이력":
            page_history()
        elif tab == "내보내기":
            page_export()
        else:
            page_dashboard()
    except MemoryError:
        st.error(
            "❌ **메모리 부족 오류**\n\n"
            "처리할 파일이 너무 크거나 데이터가 많아 메모리가 부족합니다.\n"
            "파일 크기를 줄이거나 앱을 새로고침(F5)해 주세요."
        )
        _show_global_reset_button()
    except Exception as e:
        st.error(
            f"❌ **예상치 못한 오류가 발생했습니다.**\n\n"
            f"오류 내용: `{str(e)}`\n\n"
            "앱을 새로고침(F5)하거나 아래 초기화 버튼을 눌러 처음 화면으로 돌아가세요."
        )
        _show_global_reset_button()


def _show_global_reset_button():
    """전역 초기화 버튼: 오류 발생 시 사용자가 처음 화면으로 돌아올 수 있도록 합니다."""
    st.markdown("---")
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("🔄 처음으로 돌아가기", type="primary", key="global_reset_btn"):
            # 파일 업로드 / OCR 관련 세션 초기화
            for key in ["ocr_rows", "ocr_error", "excel_error", "excel_records"]:
                st.session_state[key] = None
            st.session_state.active_tab = "대시보드"
            st.rerun()
    with col2:
        if st.button("🚪 로그아웃 후 처음 화면으로", key="global_logout_btn"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            init_session()
            st.rerun()


if __name__ == "__main__":
    main()

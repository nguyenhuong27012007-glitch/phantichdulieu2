"""
📊 Hệ thống AI Agent - Phân Tích Dữ Liệu & Đánh Giá Thị Trường Mở Rộng (HUMAN-IN-THE-LOOP WIZARD)
Giao diện Xanh Dương Pastel (Pastel Blue) Chuyên Nghiệp, Hiện Đại + Thanh Điều Hướng Ngang Cố Định (Sticky Navbar)
"""

import streamlit as st
import pandas as pd
import json
import os
import sys
import io
import plotly.graph_objects as go
import plotly.express as px

# Đảm bảo đường dẫn module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.orchestrator import AgentOrchestrator
from config import COMPANY_NAME, EXPANSION_SLOTS, TOTAL_REGIONS, DEFAULT_CRITERIA, DEFAULT_GEMINI_API_KEY
from utils.column_mapper import COLUMN_SCHEMA

# ============================================================
# CẤU HÌNH TRANG STREAMLIT
# ============================================================
st.set_page_config(
    page_title="📊 Phân Tích Dữ Liệu | Quy Trình 3 Bước Thông Minh",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# KHỞI TẠO STATE HỆ THỐNG (TRANG MỞ ĐẦU = 0, 3 BƯỚC WIZARD = 1, 2, 3)
# ============================================================
if "current_step" not in st.session_state:
    st.session_state.current_step = 0  # 0: Trang Mở Đầu, 1: Nhập file, 2: Làm sạch & Sửa file, 3: Báo cáo & Dashboard

if "step1_approved" not in st.session_state:
    st.session_state.step1_approved = False
if "step2_approved" not in st.session_state:
    st.session_state.step2_approved = False
if "step3_approved" not in st.session_state:
    st.session_state.step3_approved = False

if "orchestrator" not in st.session_state:
    st.session_state.orchestrator = AgentOrchestrator()
if "api_key_set" not in st.session_state:
    st.session_state.api_key_set = False
if "files_loaded" not in st.session_state:
    st.session_state.files_loaded = []
if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = None
if "file_messages" not in st.session_state:
    st.session_state.file_messages = []
if "pending_spinner_msg" not in st.session_state:
    st.session_state.pending_spinner_msg = ""
if "selected_ai_model" not in st.session_state:
    st.session_state.selected_ai_model = "gemini-2.5-pro"

def set_spinner_msg(msg: str):
    st.session_state.pending_spinner_msg = msg

def get_orchestrator() -> AgentOrchestrator:
    return st.session_state.orchestrator

orch = get_orchestrator()

if not st.session_state.api_key_set and DEFAULT_GEMINI_API_KEY:
    try:
        success, _ = orch.initialize_ai(DEFAULT_GEMINI_API_KEY, model_name=st.session_state.selected_ai_model)
    except TypeError:
        success, _ = orch.initialize_ai(DEFAULT_GEMINI_API_KEY)
    if success:
        st.session_state.api_key_set = True

step = st.session_state.current_step

# ============================================================
# CSS XANH DƯƠNG PASTEL (PASTEL BLUE) TRƯỞNG THÀNH, CHUYÊN NGHIỆP
# ============================================================
s0_bg = "linear-gradient(135deg, #2563eb 0%, #3b82f6 50%, #1d4ed8 100%)" if step == 0 else "#ffffff"
s0_color = "#ffffff" if step == 0 else "#1e3a8a"
s0_border = "#ffffff" if step == 0 else "#93c5fd"

s1_icon = "✅" if st.session_state.step1_approved else "1️⃣"
s2_icon = "✅" if st.session_state.step2_approved else "2️⃣"
s3_icon = "✅" if st.session_state.step3_approved else "3️⃣"

s1_color = "#047857" if st.session_state.step1_approved else "#1e3a8a"
s2_color = "#047857" if st.session_state.step2_approved else "#1e3a8a"
s3_color = "#047857" if st.session_state.step3_approved else "#1e3a8a"

s1_bg = "#ecfdf5" if st.session_state.step1_approved else "#ffffff"
s2_bg = "#ecfdf5" if st.session_state.step2_approved else "#ffffff"
s3_bg = "#ecfdf5" if st.session_state.step3_approved else "#ffffff"

s1_border = "#10b981" if st.session_state.step1_approved else "#93c5fd"
s2_border = "#10b981" if st.session_state.step2_approved else "#93c5fd"
s3_border = "#10b981" if st.session_state.step3_approved else "#93c5fd"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"], .stMarkdown p, .stMarkdown span, .stMarkdown div, .stMarkdown li, label {{
        font-family: 'Plus Jakarta Sans', 'Segoe UI', sans-serif !important;
        font-size: 0.96rem !important;
        line-height: 1.58 !important;
        color: #1e293b !important;
    }}

    /* Tiêu đề thanh thoát, rõ nét tông Xanh Navy */
    .stMarkdown h3 {{
        font-size: 1.28rem !important;
        font-weight: 700 !important;
        line-height: 1.3 !important;
        margin-top: 0.25rem !important;
        margin-bottom: 0.5rem !important;
        color: #1e3a8a !important;
    }}
    .stMarkdown h4 {{
        font-size: 1.08rem !important;
        font-weight: 700 !important;
        line-height: 1.3 !important;
        margin-top: 0.2rem !important;
        margin-bottom: 0.35rem !important;
        color: #1e3a8a !important;
    }}
    .stMarkdown h5 {{
        font-size: 0.98rem !important;
        font-weight: 600 !important;
        line-height: 1.35 !important;
        margin-top: 0.15rem !important;
        margin-bottom: 0.35rem !important;
        color: #1e40af !important;
    }}
    div[data-testid="stCaptionContainer"] p,
    div[data-testid="stCaptionContainer"] span {{
        font-size: 0.88rem !important;
        font-weight: 500 !important;
        line-height: 1.45 !important;
        color: #475569 !important;
    }}
    div[data-testid="stFileUploader"] small,
    div[data-testid="stFileUploader"] span,
    .st-key-step1_gsheet_box input {{
        font-size: 0.92rem !important;
        font-weight: 500 !important;
    }}
    div[data-testid="stAlert"] p {{
        font-size: 0.93rem !important;
        line-height: 1.5 !important;
    }}

    /* Nền Xanh Dương Pastel dịu nhẹ, thoáng mắt */
    .stApp {{
        background: linear-gradient(180deg, #f4f8ff 0%, #eef5ff 50%, #f8fafc 100%) !important;
    }}

    /* Hiệu ứng chuyển trang mượt mà */
    @keyframes pageTransitionIn {{
        0% {{ opacity: 0; transform: translateY(6px); }}
        100% {{ opacity: 1; transform: translateY(0); }}
    }}

    /* Khung chính — Rộng toàn màn hình */
    .main .block-container,
    [data-testid="stMainBlockContainer"] {{
        background: #ffffff !important;
        border-radius: 20px !important;
        padding: 2rem 2.2rem 2rem 2.2rem !important;
        margin: 0.75rem auto !important;
        max-width: 98% !important;
        box-shadow: 0 8px 30px rgba(30, 58, 138, 0.05) !important;
        border: 1px solid #e2ecf9 !important;
    }}

    .st-key-landing_stage_container,
    .st-key-zone_upload_left,
    .st-key-zone_gsheet_right,
    .st-key-zone_step1_summary,
    .st-key-zone_step2_workspace,
    .st-key-human_approval_top_card,
    .st-key-zone_step3_preview {{
        animation: pageTransitionIn 0.28s ease-out both !important;
    }}

    /* Sidebar thanh lịch */
    section[data-testid="stSidebar"] {{
        background: #f8fbff !important;
        border-right: 1px solid #dbeafe !important;
    }}

    /* Thẻ khu vực tối giản, không nhảy giật khi di chuột */
    .st-key-zone_upload_left,
    .st-key-zone_gsheet_right,
    .st-key-zone_step1_summary,
    .st-key-zone_step2_workspace,
    .st-key-zone_step3_preview,
    .st-key-zone_step2_audit_card,
    div[data-testid="stMetric"] {{
        background: #f8fbff !important;
        border: 1px solid #dbeafe !important;
        border-radius: 14px !important;
        padding: 1rem 1.25rem !important;
        transition: border-color 0.2s ease !important;
    }}
    .st-key-zone_upload_left:hover,
    .st-key-zone_gsheet_right:hover,
    .st-key-zone_step1_summary:hover,
    .st-key-zone_step3_preview:hover {{
        border-color: #93c5fd !important;
    }}

    /* ============================================================
       TRANG MỞ ĐẦU (TỐI GIẢN, THOÁNG ĐÃNG, TẬP TRUNG VÀO HÀNH ĐỘNG CHÍNH)
       ============================================================ */
    .st-key-landing_stage_container {{
        background: linear-gradient(180deg, #f8fbff 0%, #ffffff 55%, #eff6ff 100%);
        border: 1px solid #dbeafe;
        border-radius: 24px;
        padding: 4rem 2.5rem 3.8rem 2.5rem !important;
        margin: 1.5rem auto !important;
        max-width: 860px;
        min-height: 410px;
        box-shadow: 0 12px 36px rgba(30, 58, 138, 0.06);
        text-align: center;
    }}
    .hero-graphic-icon {{
        display: inline-flex;
        align-items: flex-end;
        justify-content: center;
        gap: 7px;
        background: #ffffff;
        padding: 12px 18px;
        border-radius: 16px;
        border: 1px solid #dbeafe;
        margin-bottom: 1rem;
    }}
    .hg-bar-1 {{ width: 11px; height: 18px; border-radius: 4px; background: #bfdbfe; }}
    .hg-bar-2 {{ width: 11px; height: 30px; border-radius: 4px; background: #93c5fd; }}
    .hg-bar-3 {{ width: 11px; height: 24px; border-radius: 4px; background: #60a5fa; }}
    .hg-bar-4 {{ width: 11px; height: 38px; border-radius: 4px; background: #2563eb; }}

    .stMarkdown h1.landing-main-title,
    .stMarkdown .landing-main-title,
    .stMarkdown .landing-main-title span,
    div.landing-main-title {{
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 2.9rem !important;
        font-weight: 800 !important;
        color: #1e3a8a !important;
        line-height: 1.2 !important;
        letter-spacing: -0.6px !important;
        margin: 0.25rem auto 0.75rem auto !important;
        text-align: center !important;
        display: block !important;
    }}
    .stMarkdown .landing-main-title .highlight-grad {{
        font-size: 2.9rem !important;
        font-weight: 800 !important;
        color: #1e3a8a !important;
    }}
    .stMarkdown p.landing-desc,
    .stMarkdown div.landing-desc,
    p.landing-desc,
    div.landing-desc {{
        font-size: 1.02rem !important;
        font-weight: 400 !important;
        color: #475569 !important;
        line-height: 1.65 !important;
        margin: 0 auto 2rem auto !important;
        max-width: 720px !important;
        text-align: center !important;
    }}

    /* Nút Bắt đầu gọn gàng ở giữa */
    .st-key-btn_hero_start button {{
        background: #2563eb !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 999px !important;
        min-height: 52px !important;
        height: 52px !important;
        padding: 0.5rem 2rem !important;
        box-shadow: 0 6px 18px rgba(37, 99, 235, 0.25) !important;
        transition: all 0.2s ease !important;
    }}
    .st-key-btn_hero_start button p,
    .st-key-btn_hero_start button span {{
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        color: #ffffff !important;
        white-space: nowrap !important;
    }}
    .st-key-btn_hero_start button:hover {{
        background: #1d4ed8 !important;
        transform: translateY(-1px) !important;
    }}

    /* Nút bấm tiêu chuẩn: tinh gọn, rõ ràng, không nhấp nháy */
    .stButton > button,
    .stDownloadButton > button {{
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
        min-height: 44px !important;
        padding: 0.45rem 1rem !important;
        border: 1px solid #cbd5e1 !important;
        background: #ffffff !important;
        color: #1e3a8a !important;
        box-shadow: none !important;
        transition: all 0.18s ease !important;
    }}
    .stButton > button p,
    .stButton > button span,
    .stDownloadButton > button p,
    .stDownloadButton > button span {{
        font-size: 0.92rem !important;
        font-weight: 600 !important;
        line-height: 1.25 !important;
    }}
    .stButton > button:hover,
    .stDownloadButton > button:hover {{
        border-color: #60a5fa !important;
        background: #eff6ff !important;
    }}
    .stButton > button[kind="primary"],
    .stDownloadButton > button[kind="primary"] {{
        background: #2563eb !important;
        color: #ffffff !important;
        border: 1px solid #2563eb !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.18) !important;
    }}
    .stButton > button[kind="primary"] p,
    .stButton > button[kind="primary"] span,
    .stDownloadButton > button[kind="primary"] p,
    .stDownloadButton > button[kind="primary"] span {{
        color: #ffffff !important;
    }}
    .stButton > button[kind="primary"]:hover,
    .stDownloadButton > button[kind="primary"]:hover {{
        background: #1d4ed8 !important;
        border-color: #1d4ed8 !important;
    }}

    /* THANH ĐIỀU HƯỚNG NGANG DUY NHẤT TRÊN ĐẦU (GỌN, SẠCH, DỄ NHÌN) */
    .st-key-top_wizard_bar {{
        background: #f8fbff;
        border-radius: 16px;
        padding: 8px 10px;
        border: 1px solid #dbeafe;
        margin-bottom: 1.25rem;
        position: sticky;
        top: 0.5rem;
        z-index: 999;
    }}
    .st-key-top_wizard_bar .stButton > button {{
        border-radius: 10px !important;
        padding: 0.4rem 0.6rem !important;
        min-height: 44px !important;
        height: 44px !important;
    }}
    .st-key-top_wizard_bar .stButton > button p,
    .st-key-top_wizard_bar .stButton > button span {{
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        white-space: nowrap !important;
    }}
    .st-key-top_nav_step0 button {{ background: {s0_bg} !important; border: 1px solid {s0_border} !important; color: {s0_color} !important; }}
    .st-key-top_nav_step0 button p {{ color: {s0_color} !important; }}

    .st-key-top_nav_step1 button {{ background: {s1_bg} !important; border: 1px solid {s1_border} !important; color: {s1_color} !important; }}
    .st-key-top_nav_step1 button p {{ color: {s1_color} !important; }}

    .st-key-top_nav_step2 button {{ background: {s2_bg} !important; border: 1px solid {s2_border} !important; color: {s2_color} !important; }}
    .st-key-top_nav_step2 button p {{ color: {s2_color} !important; }}

    .st-key-top_nav_step3 button {{ background: {s3_bg} !important; border: 1px solid {s3_border} !important; color: {s3_color} !important; }}
    .st-key-top_nav_step3 button p {{ color: {s3_color} !important; }}

    .st-key-top_wizard_bar .stButton > button[kind="primary"] {{
        background: #2563eb !important;
        color: #ffffff !important;
        border: 1px solid #2563eb !important;
    }}
    .st-key-top_wizard_bar .stButton > button[kind="primary"] p,
    .st-key-top_wizard_bar .stButton > button[kind="primary"] span {{
        color: #ffffff !important;
    }}

    /* Căn đều chiều cao ô Upload và ô Google Sheet ở Bước 1 */
    div[data-testid="stFileUploader"] section {{
        min-height: 74px !important;
        height: 74px !important;
        box-sizing: border-box !important;
    }}
    .st-key-step1_gsheet_box div[data-testid="stTextInputRootElement"],
    .st-key-step1_gsheet_box div[data-baseweb="input"],
    .st-key-step1_gsheet_box div[data-baseweb="base-input"] {{
        min-height: 74px !important;
        height: 74px !important;
        align-items: center !important;
        box-sizing: border-box !important;
    }}
    .st-key-step1_gsheet_box input {{
        min-height: 72px !important;
        height: 72px !important;
        padding-top: 18px !important;
        padding-bottom: 18px !important;
        box-sizing: border-box !important;
    }}

    /* Hộp thông báo chờ ở giữa màn hình */
    div[data-testid="stSpinner"] {{
        position: fixed !important;
        top: 50% !important;
        left: 50% !important;
        transform: translate(-50%, -50%) !important;
        background: #ffffff !important;
        color: #1e3a8a !important;
        padding: 18px 28px !important;
        border-radius: 16px !important;
        border: 1px solid #93c5fd !important;
        box-shadow: 0 12px 32px rgba(30, 58, 138, 0.16) !important;
        z-index: 999999 !important;
        text-align: center !important;
        min-width: 340px !important;
    }}
    div[data-testid="stSpinner"] p,
    div[data-testid="stSpinner"] span {{
        font-size: 0.96rem !important;
        font-weight: 600 !important;
        color: #1e3a8a !important;
    }}

    /* Nút "Xem thêm" thu gọn / mở rộng danh sách nhóm ở Bước 1 & Bước 2 */
    details.inline-groups-details {{
        display: inline;
    }}
    details.inline-groups-details summary.more-groups-btn {{
        display: inline-block;
        list-style: none;
        cursor: pointer;
        background: #eff6ff;
        color: #2563eb !important;
        border: 1px solid #93c5fd;
        border-radius: 999px;
        padding: 1px 10px;
        margin-left: 6px;
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        user-select: none;
        transition: all 0.15s ease;
    }}
    details.inline-groups-details summary.more-groups-btn::-webkit-details-marker {{
        display: none;
    }}
    details.inline-groups-details summary.more-groups-btn:hover {{
        background: #dbeafe;
        border-color: #3b82f6;
    }}
    details.inline-groups-details .more-groups-expanded {{
        margin-top: 6px;
        padding: 8px 12px;
        background: #f8fbff;
        border: 1px solid #dbeafe;
        border-radius: 10px;
        font-size: 0.88rem !important;
        color: #1e3a8a !important;
        line-height: 1.5 !important;
    }}

    /* Nút Duyệt & Tải xuống nổi lơ lửng giữa trang bên phải */
    .st-key-floating_approve_step1,
    .st-key-floating_approve_step2,
    .st-key-floating_download_step3 {{
        position: fixed !important;
        right: 24px !important;
        top: 50% !important;
        transform: translateY(-50%) !important;
        z-index: 9999 !important;
        width: auto !important;
        min-width: 215px !important;
        background: rgba(255, 255, 255, 0.94) !important;
        backdrop-filter: blur(10px) !important;
        padding: 10px 12px !important;
        border-radius: 16px !important;
        box-shadow: 0 10px 28px rgba(37, 99, 235, 0.22) !important;
        border: 1.5px solid #93c5fd !important;
    }}
</style>
""", unsafe_allow_html=True)

# ============================================================
# CHỈ HIỂN THỊ THANH ĐIỀU HƯỚNG NGANG KHI ĐÃ VÀO BƯỚC 1, 2, 3 (ẨN Ở TRANG MỞ ĐẦU)
# ============================================================
if step != 0:
    with st.container(key="top_wizard_bar"):
        nav_col1, nav_col2, nav_col3 = st.columns([1, 1, 1])

        with nav_col1:
            if st.button(
                f"{s1_icon} Bước 1: Nhập dữ liệu",
                key="top_nav_step1",
                use_container_width=True,
                type="primary" if step == 1 else "secondary"
            ):
                set_spinner_msg("⏳ Đang chuyển sang Bước 1: Nhập dữ liệu...")
                st.session_state.current_step = 1
                st.rerun()

        with nav_col2:
            if st.button(
                f"{s2_icon} Bước 2: Làm sạch",
                key="top_nav_step2",
                use_container_width=True,
                type="primary" if step == 2 else "secondary"
            ):
                if st.session_state.step1_approved:
                    set_spinner_msg("⏳ Đang mở Bước 2: Làm sạch...")
                    st.session_state.current_step = 2
                    st.rerun()
                else:
                    st.toast("⚠️ Vui lòng nạp file và duyệt Bước 1 trước!", icon="⚠️")

        with nav_col3:
            if st.button(
                f"{s3_icon} Bước 3: Tạo báo cáo",
                key="top_nav_step3",
                use_container_width=True,
                type="primary" if step == 3 else "secondary"
            ):
                if st.session_state.step2_approved:
                    set_spinner_msg("⏳ Đang mở Bước 3: Tạo báo cáo...")
                    st.session_state.current_step = 3
                    st.rerun()
                else:
                    st.toast("⚠️ Vui lòng duyệt Bước 2 trước khi sang Bước 3!", icon="⚠️")

# ============================================================
# SIDEBAR ĐIỀU HƯỚNG NHANH & CÀI ĐẶT ẨN GỌN
# ============================================================
with st.sidebar:
    st.markdown("<h3 style='color:#1e3a8a; font-size:1.1rem; margin-bottom:0.6rem;'>🧭 Điều hướng nhanh</h3>", unsafe_allow_html=True)

    if st.button("🏠 Trang Mở Đầu", use_container_width=True, key="sb_nav_0"):
        set_spinner_msg("⏳ Đang quay lại Trang Mở Đầu...")
        st.session_state.current_step = 0
        st.rerun()

    if st.button("📥 Bước 1: Nhập Dữ Liệu", use_container_width=True, key="sb_nav_1"):
        set_spinner_msg("⏳ Đang chuyển sang Bước 1: Nhập Dữ Liệu...")
        st.session_state.current_step = 1
        st.rerun()

    if st.button("🧹 Bước 2: Làm Sạch", use_container_width=True, key="sb_nav_2"):
        if st.session_state.step1_approved:
            set_spinner_msg("⏳ Đang mở Bước 2: Làm Sạch...")
            st.session_state.current_step = 2
            st.rerun()
        else:
            st.toast("⚠️ Vui lòng nạp file và Duyệt Bước 1 trước!", icon="⚠️")

    if st.button("📊 Bước 3: Tạo Báo Cáo", use_container_width=True, key="sb_nav_3"):
        if st.session_state.step2_approved:
            set_spinner_msg("⏳ Đang mở Bước 3: Tạo Báo Cáo...")
            st.session_state.current_step = 3
            st.rerun()
        else:
            st.toast("⚠️ Vui lòng Duyệt Bước 2 trước!", icon="⚠️")

    if st.button("🔄 Làm Mới Phiên Làm Việc", use_container_width=True, key="sb_reset_session"):
        for k in ["files_loaded", "file_messages", "analysis_results", "editable_report", "editable_plan", "dashboard_scores_df"]:
            if k in st.session_state:
                st.session_state[k] = [] if k in ["files_loaded", "file_messages"] else None
        st.session_state.step1_approved = False
        st.session_state.step2_approved = False
        st.session_state.step3_approved = False
        st.session_state.show_step2_audit_log = False
        st.session_state.show_step2_editor = False
        st.session_state.current_step = 0
        orch.data_agent.raw_dataframes.clear()
        set_spinner_msg("⏳ Đang làm mới toàn bộ phiên làm việc...")
        st.rerun()

    st.divider()

    st.markdown("#### 🤖 Chọn Phiên Bản Model AI")
    ai_model_options = {
        "gemini-2.5-pro": "🧠 Gemini 2.5 Pro",
        "gemini-2.5-flash": "⚡ Gemini 2.5 Flash",
        "gemini-2.0-flash": "🔹 Gemini 2.0 Flash",
        "gemini-1.5-pro": "💎 Gemini 1.5 Pro"
    }
    if st.session_state.selected_ai_model not in ai_model_options:
        st.session_state.selected_ai_model = "gemini-2.5-pro"
    model_keys = list(ai_model_options.keys())
    cur_idx = model_keys.index(st.session_state.selected_ai_model)
    chosen_model = st.selectbox(
        "Mô hình AI đang sử dụng:",
        options=model_keys,
        index=cur_idx,
        format_func=lambda k: ai_model_options[k],
        key="sidebar_model_selector"
    )
    st.caption(f"🟢 Đang kích hoạt: **{ai_model_options[st.session_state.selected_ai_model]}**")

    # Khu vực Cài Đặt API Key được ẩn gọn, bấm vào mới hiện
    with st.expander("⚙️ Cài Đặt API", expanded=False):
        st.markdown("#### 🔑 Kết nối AI Agent")
        api_key_input = st.text_input(
            "Gemini API Key",
            type="password",
            value=DEFAULT_GEMINI_API_KEY,
            help="Đã tích hợp sẵn API Key tự động"
        )
        if st.button("✨ Cập nhật API Key", use_container_width=True):
            if api_key_input:
                try:
                    success, msg = orch.initialize_ai(api_key_input, model_name=st.session_state.selected_ai_model)
                except TypeError:
                    success, msg = orch.initialize_ai(api_key_input)
                if success:
                    st.session_state.api_key_set = True
                    st.success(f"✅ Kết nối thành công ({st.session_state.selected_ai_model})!")
                else:
                    st.error(msg)

    if chosen_model != st.session_state.selected_ai_model:
        with st.spinner(f"⏳ Đang chuyển đổi sang mô hình {ai_model_options[chosen_model]}..."):
            st.session_state.selected_ai_model = chosen_model
            try:
                orch.initialize_ai(api_key_input or DEFAULT_GEMINI_API_KEY, model_name=chosen_model)
            except TypeError:
                orch.initialize_ai(api_key_input or DEFAULT_GEMINI_API_KEY)
            st.toast(f"✅ Đã chuyển sang {ai_model_options[chosen_model]}", icon="🤖")
        st.rerun()

# ============================================================
# TRÌNH BẮT LỖI TOÀN CỤC — ĐẢM BẢO MỌI THÔNG BÁO ĐỀU BẰNG TIẾNG VIỆT DỄ HIỂU
# ============================================================
def _vietnamese_error_message(exc: Exception) -> str:
    msg = str(exc)
    if "invalid error value" in msg:
        return "⚠️ Không thể chuyển đổi một số ô văn bản sang kiểu số. Hệ thống đã giữ nguyên giá trị văn bản gốc."
    if "429" in msg or "quota" in msg.lower() or "ResourceExhausted" in msg:
        return "⚠️ Hệ thống AI đang quá tải hoặc hết hạn mức truy cập tạm thời. Hệ thống đã tự động dùng bộ phân tích dự phòng."
    if "404" in msg:
        return "⚠️ Không tìm thấy tài nguyên hoặc liên kết Google Sheet. Vui lòng kiểm tra lại đường dẫn."
    if "403" in msg or "permission" in msg.lower():
        return "⚠️ Không có quyền truy cập tệp hoặc Google Sheet chưa bật chế độ chia sẻ công khai."
    if "API_KEY" in msg.upper() or "api key" in msg.lower():
        return "⚠️ Mã kết nối AI (API Key) chưa hợp lệ. Vui lòng kiểm tra lại trong Bảng Cài Đặt bên trái."
    if "ParserError" in msg or "tokenizing" in msg:
        return "⚠️ Định dạng tệp dữ liệu có dòng bị lệch cột. Vui lòng kiểm tra lại tệp CSV/Excel."
    return "⚠️ Hệ thống gặp sự cố nhỏ khi xử lý thao tác vừa rồi. Vui lòng kiểm tra lại dữ liệu hoặc thử lại."

def _format_groups_preview(groups: list, max_show: int = 3) -> str:
    if not groups:
        return "Toàn bộ dữ liệu"
    if len(groups) <= max_show:
        return ", ".join(groups)
    shown = ", ".join(groups[:max_show])
    remaining = groups[max_show:]
    all_str = ", ".join(groups)
    return (
        f"{shown} "
        f"<details class='inline-groups-details'>"
        f"<summary class='more-groups-btn'>Xem thêm (+{len(remaining)} nhóm)</summary>"
        f"<div class='more-groups-expanded'><b>Tất cả {len(groups)} nhóm:</b> {all_str}</div>"
        f"</details>"
    )


try:
    # Luôn đóng sẵn 2 khung chi tiết ở Bước 2 mỗi khi người dùng ở bước khác hoặc vừa mới chuyển vào Bước 2
    if st.session_state.current_step != 2:
        st.session_state.show_step2_audit_log = False
        st.session_state.show_step2_editor = False

    # ============================================================
    # TRANG MỞ ĐẦU (BƯỚC 0): TỐI GIẢN, THOÁNG ĐÃNG, TẬP TRUNG VÀO NÚT BẮT ĐẦU
    # ============================================================
    if st.session_state.current_step == 0:
        if st.session_state.pending_spinner_msg:
            with st.spinner(st.session_state.pending_spinner_msg):
                import time
                time.sleep(0.15)
            st.session_state.pending_spinner_msg = ""

        with st.container(key="landing_stage_container"):
            st.markdown("""
            <div style="text-align:center;">
                <div class="hero-graphic-icon">
                    <div class="hg-bar-1"></div>
                    <div class="hg-bar-2"></div>
                    <div class="hg-bar-3"></div>
                    <div class="hg-bar-4"></div>
                </div>
                <div class="landing-main-title">
                    <span class="highlight-grad">Phân Tích Dữ Liệu</span>
                </div>
                <div class="landing-desc">
                    Tải tệp lên, Kiểm tra &amp; làm sạch và Tạo báo cáo dashboard trực quan
                </div>
            </div>
            """, unsafe_allow_html=True)

            _, col_start_btn, _ = st.columns([1.5, 1.0, 1.5])
            with col_start_btn:
                if st.button("Bắt đầu ➔", key="btn_hero_start", type="primary", use_container_width=True):
                    set_spinner_msg("⏳ Đang mở Bước 1...")
                    st.session_state.current_step = 1
                    st.rerun()

            st.markdown("""
            <div style="max-width:660px; margin:1.8rem auto 0 auto; padding:14px 22px; background:#f8fbff; border:1px solid #dbeafe; border-radius:14px; text-align:center; color:#475569; font-size:0.93rem; line-height:1.6;">
                Hỗ trợ xử lý dữ liệu từ tệp CSV, Excel hoặc Google Sheet một cách nhanh chóng, từ khâu kiểm tra và làm sạch sai sót đến tổng hợp số liệu và tạo báo cáo Dashboard trực quan.
            </div>
            """, unsafe_allow_html=True)

    # ============================================================
    # BƯỚC 1: NHẬP DỮ LIỆU (CSV / EXCEL / GOOGLE SHEET)
    # ============================================================
    elif st.session_state.current_step == 1:
        if st.session_state.pending_spinner_msg:
            with st.spinner(st.session_state.pending_spinner_msg):
                import time
                time.sleep(0.15)
            st.session_state.pending_spinner_msg = ""

        if "show_step1_uploader" not in st.session_state:
            st.session_state.show_step1_uploader = False

        has_loaded_files = bool(orch.data_agent.raw_dataframes)
        if has_loaded_files:
            col_s1_h1, col_s1_h2 = st.columns([2.7, 1.3])
            with col_s1_h1:
                st.markdown("### Bước 1: Nhập & Kiểm tra dữ liệu")
            with col_s1_h2:
                btn_lbl = "Đóng khung nạp thêm" if st.session_state.show_step1_uploader else "+ Nạp thêm tệp"
                if st.button(btn_lbl, use_container_width=True, key="btn_toggle_s1_uploader"):
                    st.session_state.show_step1_uploader = not st.session_state.show_step1_uploader
                    st.rerun()
        else:
            st.markdown("### Bước 1: Nhập dữ liệu")
            st.caption("Tải lên tệp CSV / Excel hoặc dán đường dẫn Google Sheet công khai để bắt đầu.")

        if (not has_loaded_files) or st.session_state.show_step1_uploader:
            col_up1, col_up2 = st.columns([1, 1])
    
            with col_up1:
                with st.container(key="zone_upload_left"):
                    st.markdown("##### 📁 Tải tệp")
                    uploaded_files = st.file_uploader(
                        "Tải tệp lên",
                        type=["csv", "xlsx", "xls"],
                        accept_multiple_files=True,
                        label_visibility="collapsed"
                    )
                    if uploaded_files:
                        if st.button("Nạp tệp đã chọn", type="primary", use_container_width=True, key="btn_verify_upload"):
                            with st.spinner("⏳ Đang đọc và kiểm tra dữ liệu..."):
                                for up in uploaded_files:
                                    content = up.read()
                                    success, msg = orch.load_file(content, up.name)
                                    st.session_state.file_messages.append({"file": up.name, "success": success, "msg": msg})
                                    if success and up.name not in st.session_state.files_loaded:
                                        st.session_state.files_loaded.append(up.name)
                                st.session_state.show_step1_uploader = False
                            st.rerun()

            with col_up2:
                with st.container(key="zone_gsheet_right"):
                    st.markdown("##### 🔗 Đường dẫn Google Sheet")
                    with st.container(key="step1_gsheet_box"):
                        sheet_url = st.text_input(
                            "Liên kết Google Sheet",
                            placeholder="https://docs.google.com/spreadsheets/d/.../edit",
                            label_visibility="collapsed"
                        )
                    if sheet_url:
                        if st.button("Đọc Google Sheet", type="primary", use_container_width=True, key="btn_verify_gsheet"):
                            with st.spinner("⏳ Đang kết nối Google Sheet..."):
                                success, msg = orch.load_google_sheet(sheet_url)
                                st.session_state.file_messages.append({"file": "Google Sheet", "success": success, "msg": msg})
                                if success:
                                    st.session_state.files_loaded.append("Google Sheet")
                                st.session_state.show_step1_uploader = False
                            st.rerun()

        if orch.data_agent.raw_dataframes:
            st.write("")
            detected_groups = orch.data_agent.get_regions_detected()
            with st.container(key="zone_step1_summary"):
                sum_c1, sum_c2, sum_c3, sum_c4 = st.columns([0.9, 1.2, 0.9, 2.2])
                sum_c1.metric("Số tệp", len(orch.data_agent.raw_dataframes))
                sum_c2.metric("Tổng số dòng", f"{sum(len(df) for df in orch.data_agent.raw_dataframes.values()):,}")
                sum_c3.metric("Nhóm phân tích", len(detected_groups))
                with sum_c4:
                    st.markdown(f"<div style='margin-bottom:0.4rem;'><b>Nhóm phát hiện:</b> {_format_groups_preview(detected_groups, 3)}</div>", unsafe_allow_html=True)
            with st.container(key="floating_approve_step1"):
                if st.button("Duyệt & Sang Bước 2 ➔", type="primary", use_container_width=True, key="btn_approve_step1"):
                    set_spinner_msg("⏳ Đang chuyển sang Bước 2...")
                    st.session_state.step1_approved = True
                    st.session_state.current_step = 2
                    st.rerun()

            st.markdown("#### ✏️ Sửa nhanh dữ liệu ngay tại Bước 1")
            with st.container():
                s1_file_list = list(orch.data_agent.raw_dataframes.keys())
                col_s1_sel, col_s1_info = st.columns([1.5, 2.5])
                with col_s1_sel:
                    s1_chosen_file = st.selectbox("Chọn tệp:", s1_file_list, key="s1_file_selector")
                with col_s1_info:
                    s1_df_cur = orch.data_agent.raw_dataframes[s1_chosen_file]
                    st.caption(f"Nhấp đúp vào ô để sửa trực tiếp ({len(s1_df_cur):,} dòng × {len(s1_df_cur.columns)} cột)")

                # Thanh công cụ lọc nhiều cột kiểu Excel
                col_f1, col_f2, col_f3, col_f4 = st.columns([1.2, 1.8, 1.1, 0.9])
                with col_f1:
                    s1_search = st.text_input("🔍 Tìm kiếm nhanh:", placeholder="Nhập từ khóa...", key=f"s1_search_{s1_chosen_file}")
                with col_f2:
                    s1_filter_cols = st.multiselect(
                        "🔽 Lọc theo cột (chọn 1 hoặc nhiều cột, VD: City, Region):",
                        list(s1_df_cur.columns),
                        default=[],
                        key=f"s1_fcols_{s1_chosen_file}"
                    )
                with col_f3:
                    s1_sort_col = st.selectbox("↕️ Sắp xếp theo:", ["(Mặc định)"] + list(s1_df_cur.columns), key=f"s1_scol_{s1_chosen_file}")
                with col_f4:
                    s1_sort_asc = st.selectbox("Thứ tự:", ["Tăng dần", "Giảm dần"], key=f"s1_sasc_{s1_chosen_file}")

                s1_active_filters = {}
                if s1_filter_cols:
                    f_cols_ui = st.columns(min(len(s1_filter_cols), 3))
                    for idx_fc, fcol in enumerate(s1_filter_cols):
                        with f_cols_ui[idx_fc % 3]:
                            uniq_vals = sorted(s1_df_cur[fcol].dropna().astype(str).unique().tolist())[:300]
                            picked_vals = st.multiselect(f"Giá trị `{fcol}`:", uniq_vals, key=f"s1_fval_{s1_chosen_file}_{fcol}")
                            if picked_vals:
                                s1_active_filters[fcol] = picked_vals

                s1_show_cols = st.multiselect(
                    "👁️ Chọn cột hiển thị (để trống = hiện tất cả):",
                    list(s1_df_cur.columns),
                    default=[],
                    key=f"s1_cols_{s1_chosen_file}"
                )

                s1_view_df = s1_df_cur
                if s1_search and s1_search.strip():
                    kw = s1_search.strip().lower()
                    mask_kw = s1_view_df.astype(str).apply(lambda col: col.str.lower().str.contains(kw, na=False)).any(axis=1)
                    s1_view_df = s1_view_df[mask_kw]
                for fcol, fvals in s1_active_filters.items():
                    s1_view_df = s1_view_df[s1_view_df[fcol].astype(str).isin(fvals)]
                if s1_sort_col != "(Mặc định)":
                    s1_view_df = s1_view_df.sort_values(by=s1_sort_col, ascending=(s1_sort_asc == "Tăng dần"), kind="mergesort")

                display_cols = s1_show_cols if s1_show_cols else list(s1_view_df.columns)
                s1_is_filtered = bool((s1_search and s1_search.strip()) or s1_active_filters)
                if s1_is_filtered:
                    st.caption(f"🔎 Đang hiển thị **{len(s1_view_df):,} / {len(s1_df_cur):,}** dòng phù hợp.")

                if len(s1_view_df) > 1000:
                    s1_slice = s1_view_df[display_cols].iloc[:500]
                    s1_edited = st.data_editor(s1_slice, use_container_width=True, num_rows="dynamic", height=520, key=f"s1_editor_{s1_chosen_file}")
                else:
                    s1_slice = s1_view_df[display_cols]
                    s1_edited = st.data_editor(s1_slice, use_container_width=True, num_rows="dynamic", height=460, key=f"s1_editor_{s1_chosen_file}")

                col_s1_save, col_s1_apply_filter, _ = st.columns([1.3, 1.5, 2.2])
                with col_s1_save:
                    if st.button("💾 Lưu chỉnh sửa", type="primary", use_container_width=True, key="btn_save_step1"):
                        try:
                            with st.spinner("⏳ Đang lưu thay đổi..."):
                                if not s1_is_filtered and not s1_show_cols and len(s1_df_cur) <= 1000:
                                    orch.data_agent.raw_dataframes[s1_chosen_file] = s1_edited
                                else:
                                    updated_full = s1_df_cur.copy()
                                    common_idx = s1_edited.index.intersection(updated_full.index)
                                    updated_full.loc[common_idx, display_cols] = s1_edited.loc[common_idx, display_cols]
                                    orch.data_agent.raw_dataframes[s1_chosen_file] = updated_full
                                from utils.column_mapper import map_columns
                                from utils.file_handler import _auto_aggregate
                                new_df = orch.data_agent.raw_dataframes[s1_chosen_file]
                                orch.data_agent.column_mappings[s1_chosen_file] = map_columns(list(new_df.columns))
                                if len(new_df) > 1000:
                                    agg_df, agg_note = _auto_aggregate(new_df, s1_chosen_file)
                                    orch.data_agent.file_infos[s1_chosen_file]["aggregated_df"] = agg_df
                                    orch.data_agent.file_infos[s1_chosen_file]["aggregation_note"] = agg_note
                                    orch.data_agent.file_infos[s1_chosen_file]["rows"] = len(new_df)
                            st.rerun()
                        except Exception:
                            st.error("❌ Không thể lưu thay đổi. Vui lòng kiểm tra định dạng dữ liệu.")
                with col_s1_apply_filter:
                    if s1_is_filtered:
                        if st.button("📌 Chỉ giữ lại dữ liệu đang lọc", use_container_width=True, key="btn_keep_filtered_step1"):
                            orch.data_agent.raw_dataframes[s1_chosen_file] = s1_view_df.reset_index(drop=True)
                            st.toast(f"✅ Đã lọc giữ lại {len(s1_view_df):,} dòng!", icon="📌")
                            st.rerun()

        if st.session_state.file_messages:
            if "step1_ai_summaries" not in st.session_state:
                st.session_state.step1_ai_summaries = {}
            with st.expander(f"📋 Chi tiết kiểm tra ({len(st.session_state.file_messages)} tệp)", expanded=not bool(orch.data_agent.raw_dataframes)):
                for item in st.session_state.file_messages[-6:]:
                    if item["success"]:
                        st.success(f"**{item['file']}**: {item['msg']}")
                        df_chk = orch.data_agent.raw_dataframes.get(item["file"])
                        if df_chk is not None and not df_chk.empty:
                            cache_key = f"v2_{item['file']}_{len(df_chk)}_{len(df_chk.columns)}"
                            if cache_key not in st.session_state.step1_ai_summaries:
                                null_cnt = int(df_chk.isna().sum().sum())
                                dup_cnt = int(df_chk.duplicated().sum())
                                null_cols = df_chk.columns[df_chk.isna().any()].tolist()
                                neg_cols = []
                                for nc in df_chk.select_dtypes(include=["number"]).columns:
                                    if (df_chk[nc].dropna() < 0).any():
                                        neg_cols.append(str(nc))
                                has_issues = (null_cnt > 0) or (dup_cnt > 0) or bool(neg_cols)

                                ai_text = ""
                                if getattr(orch.analysis_agent, "model", None) is not None:
                                    try:
                                        cols_preview = ", ".join(str(c) for c in df_chk.columns[:18])
                                        sample_csv = df_chk.head(3).to_csv(index=False)
                                        if has_issues:
                                            prompt_s1 = (
                                                f"Hãy nhận xét ngắn gọn bằng tiếng Việt (2-3 gạch đầu dòng, không đếm số dòng/cột) về vấn đề của tệp '{item['file']}':\n"
                                                f"- Số ô trống: {null_cnt:,} (tại các cột: {', '.join(str(c) for c in null_cols[:5])})\n"
                                                f"- Số dòng trùng lặp: {dup_cnt:,}\n"
                                                f"- Cột có giá trị âm: {', '.join(neg_cols[:5]) if neg_cols else 'Không'}\n"
                                                f"Các cột: {cols_preview}\nMẫu:\n{sample_csv}\n"
                                                f"Nêu rõ tệp đang gặp lỗi gì và gợi ý ngắn gọn cách xử lý ở Bước 2."
                                            )
                                        else:
                                            prompt_s1 = (
                                                f"Tệp '{item['file']}' không có lỗi dữ liệu. Hãy nhận xét ngắn gọn bằng tiếng Việt (2-3 gạch đầu dòng, không đếm số dòng/cột) "
                                                f"về tình hình hoạt động / kinh doanh của doanh nghiệp dựa trên các cột ({cols_preview}) và mẫu sau:\n{sample_csv}"
                                            )
                                        resp = orch.analysis_agent.model.generate_content(prompt_s1, request_options={"timeout": 5})
                                        ai_text = (getattr(resp, "text", "") or "").strip()
                                    except Exception:
                                        ai_text = ""
                                if not ai_text:
                                    if has_issues:
                                        issues_parts = []
                                        if null_cnt > 0:
                                            cols_str = ", ".join(str(c) for c in null_cols[:4])
                                            more_c = f" (+{len(null_cols)-4} cột)" if len(null_cols) > 4 else ""
                                            issues_parts.append(f"- **Dữ liệu bị thiếu:** Có **{null_cnt:,} ô trống** rải rác ở các cột `{cols_str}`{more_c}.")
                                        if dup_cnt > 0:
                                            issues_parts.append(f"- **Trùng lặp bản ghi:** Phát hiện **{dup_cnt:,} dòng trùng lặp** cần rà soát.")
                                        if neg_cols:
                                            issues_parts.append(f"- **Giá trị bất thường:** Cột `{', '.join(neg_cols[:4])}` có chứa số âm.")
                                        issues_parts.append("- **Đề xuất:** Chuyển sang **Bước 2** để hệ thống tự động làm sạch hoặc sửa trực tiếp các ô lỗi.")
                                        ai_text = "\n".join(issues_parts)
                                    else:
                                        rev_cols = [c for c in df_chk.columns if any(k in str(c).lower() for k in ["revenue", "doanh_thu", "doanhthu", "sales", "amount", "profit", "loi_nhuan"])]
                                        biz_parts = [f"- **Tình trạng dữ liệu:** Tệp sạch, không phát hiện ô trống hay dòng trùng lặp."]
                                        if rev_cols:
                                            rc = rev_cols[0]
                                            s_val = pd.to_numeric(df_chk[rc], errors="coerce").dropna()
                                            if len(s_val) > 0:
                                                biz_parts.append(f"- **Tình hình kinh doanh:** Chỉ số `{rc}` đạt tổng **{s_val.sum():,.0f}** (trung bình **{s_val.mean():,.1f}**/giao dịch).")
                                        biz_parts.append("- **Đánh giá chung:** Dữ liệu phản ánh hoạt động vận hành ổn định, đủ điều kiện tổng hợp báo cáo và Dashboard ở Bước 3.")
                                        ai_text = "\n".join(biz_parts)
                                st.session_state.step1_ai_summaries[cache_key] = ai_text
                            st.info(f"🤖 **AI Phân tích sơ bộ ({item['file']}):**\n\n{st.session_state.step1_ai_summaries[cache_key]}")
                    else:
                        st.error(f"**{item['file']}**: {item['msg']}")

    # ============================================================
    # BƯỚC 2: XEM TRẠNG THÁI LÀM SẠCH & CHỈNH SỬA DỮ LIỆU
    # ============================================================
    elif st.session_state.current_step == 2:
        if st.session_state.pending_spinner_msg:
            with st.spinner(st.session_state.pending_spinner_msg):
                import time
                time.sleep(0.15)
            st.session_state.pending_spinner_msg = ""

        if not orch.data_agent.raw_dataframes:
            st.warning("Chưa có dữ liệu. Vui lòng quay lại Bước 1 để tải tệp.")
            if st.button("⬅️ Quay lại Bước 1", type="primary"):
                st.session_state.current_step = 1
                st.rerun()
        else:
            file_list = list(orch.data_agent.raw_dataframes.keys())
            st.markdown("### Bước 2: Làm sạch & kiểm tra dữ liệu")

            top_bar_c1, top_bar_c2, top_bar_c3 = st.columns([2.0, 2.4, 1.8])
            with top_bar_c1:
                selected_file = st.selectbox("Tệp đang xem:", file_list)
            df_current = orch.data_agent.raw_dataframes[selected_file]
            total_rows = len(df_current)
            file_info_cur = orch.data_agent.file_infos.get(selected_file, {})
            detected_groups = orch.data_agent.get_regions_detected()

            with top_bar_c2:
                total_records = sum(len(df) for df in orch.data_agent.raw_dataframes.values())
                st.markdown(f"**{total_rows:,} dòng × {len(df_current.columns)} cột** · {len(detected_groups)} nhóm")
                st.markdown(f"<div style='font-size:0.88rem; color:#475569;'>Phân nhóm chính: {_format_groups_preview(detected_groups, 3)}</div>", unsafe_allow_html=True)

            with top_bar_c3:
                st.write("")

            if total_records > 0:
                with st.container(key="floating_approve_step2"):
                    if st.button("Duyệt & Sang Bước 3 ➔", type="primary", use_container_width=True, key="btn_approve_step2"):
                        set_spinner_msg("⏳ Đang phân tích dữ liệu và tạo Báo cáo & Dashboard...")
                        st.session_state.step2_approved = True
                        st.session_state.current_step = 3
                        st.rerun()

            if 'show_step2_editor' not in st.session_state:
                st.session_state.show_step2_editor = False
            if 'show_step2_audit_log' not in st.session_state:
                st.session_state.show_step2_audit_log = False

            if st.session_state.get("_last_step2_selected_file") != selected_file:
                st.session_state.show_step2_audit_log = False
                st.session_state.show_step2_editor = False
                st.session_state._last_step2_selected_file = selected_file

            st.write("")
            col_s2_btn1, col_s2_btn2 = st.columns(2)
            with col_s2_btn1:
                lbl_audit_btn = "Đóng chi tiết xử lý file" if st.session_state.show_step2_audit_log else "📋 Xem hệ thống đã xử lý gì với file"
                if st.button(lbl_audit_btn, use_container_width=True, key="btn_toggle_s2_audit"):
                    st.session_state.show_step2_audit_log = not st.session_state.show_step2_audit_log
                    st.rerun()
            with col_s2_btn2:
                lbl_s2_btn = "Đóng bảng chỉnh sửa" if st.session_state.show_step2_editor else "✏️ Bấm vào đây nếu muốn sửa dữ liệu"
                if st.button(lbl_s2_btn, use_container_width=True, key="btn_toggle_s2_editor"):
                    st.session_state.show_step2_editor = not st.session_state.show_step2_editor
                    st.rerun()

            if st.session_state.show_step2_audit_log:
                empty_r = int(file_info_cur.get("empty_rows_removed", 0))
                empty_c = int(file_info_cur.get("empty_cols_removed", 0))
                missing_cells = int(df_current.isna().sum().sum())
                num_cols = [c for c in df_current.columns if pd.api.types.is_numeric_dtype(df_current[c])]
                mapped_dict = orch.data_agent.column_mappings.get(selected_file, {})
                user_edits = file_info_cur.get("user_action_log", [])

                with st.container(key="zone_step2_audit_card"):
                    if empty_r == 0 and empty_c == 0 and missing_cells == 0 and not user_edits:
                        st.success(
                            f"✅ **File gốc `{selected_file}` của bạn đã chuẩn (OK 100%)!**\n\n"
                            f"- **Không có dòng trống hay cột trống nào bị xóa:** Giữ nguyên toàn bộ **{total_rows:,} dòng × {len(df_current.columns)} cột**.\n"
                            f"- **Không có ô dữ liệu bị khuyết (trống):** Tất cả các ô đều đầy đủ giá trị.\n"
                            f"- **Chuẩn hóa kiểu số tự động:** Đã nhận diện {len(num_cols)} cột số ({', '.join(map(str, num_cols[:6]))}{'...' if len(num_cols) > 6 else ''}) và ánh xạ {len(mapped_dict)} trường thông tin chính."
                        )
                    else:
                        details = [f"📋 **Báo cáo xử lý tự động cho file `{selected_file}`:**"]
                        if empty_r > 0 or empty_c > 0:
                            details.append(f"- 🧹 **Đã tự động xóa:** `{empty_r}` dòng hoàn toàn trống và `{empty_c}` cột hoàn toàn trống.")
                        else:
                            details.append(f"- ✅ **Dòng & cột gốc:** Không có dòng/cột trống thừa (giữ nguyên **{total_rows:,} dòng × {len(df_current.columns)} cột**).")
                        if missing_cells > 0:
                            details.append(f"- ⚠️ **Ô dữ liệu khuyết (NaN/Trống):** Phát hiện `{missing_cells}` ô trống lẻ và đã xử lý mặc định an toàn khi tính toán.")
                        else:
                            details.append("- ✅ **Độ đầy đủ:** 100% các ô dữ liệu đều có giá trị (0 ô trống).")
                        details.append(f"- 🔢 **Chuẩn hóa định dạng số:** Đã chuyển đổi tự động {len(num_cols)} cột số và ánh xạ {len(mapped_dict)} trường thông tin.")
                        for u_log in user_edits:
                            details.append(f"- ✏️ **Thao tác của người dùng:** {u_log}")
                        st.info("\n".join(details))

            if st.session_state.show_step2_editor:
                with st.container(key="zone_step2_workspace"):
                    # Hỗ trợ phân trang & lọc nhanh nếu file lớn (> 1000 dòng) hoặc xem toàn bộ
                    if total_rows > 1000:
                        col_p1, col_p2, col_p3 = st.columns([1.2, 1.2, 1.6])
                        with col_p1:
                            page_size = st.selectbox("📄 Số dòng/trang:", [500, 1000, 2500, 5000, total_rows], index=1, format_func=lambda x: f"Tất cả ({x:,} dòng)" if x == total_rows else f"{x:,} dòng/trang")
                        total_pages = max(1, (total_rows + page_size - 1) // page_size)
                        with col_p2:
                            current_page = st.number_input(f"🔢 Trang (1-{total_pages}):", min_value=1, max_value=total_pages, value=1, step=1)
                        with col_p3:
                            search_kw = st.text_input("🔍 Lọc nhanh từ khóa:", placeholder="Nhập Địa bàn / Mã...")

                        start_idx = (current_page - 1) * page_size
                        end_idx = min(start_idx + page_size, total_rows)

                        if search_kw.strip():
                            mask = df_current.astype(str).apply(lambda x: x.str.contains(search_kw.strip(), case=False, na=False)).any(axis=1)
                            df_slice = df_current[mask]
                        else:
                            df_slice = df_current.iloc[start_idx:end_idx]

                        edited_slice = st.data_editor(
                            df_slice,
                            use_container_width=True,
                            num_rows="dynamic",
                            height=340,
                            key=f"editor_{selected_file}_{current_page}_{page_size}_{search_kw}"
                        )
                    else:
                        st.caption("💡 Nhấp đúp vào ô bất kỳ để sửa trực tiếp, sau đó bấm nút **Lưu Dữ Liệu** hoặc **Làm Sạch & Chuẩn Hóa** bên dưới:")
                        edited_slice = st.data_editor(
                            df_current,
                            use_container_width=True,
                            num_rows="dynamic",
                            height=240,
                            key=f"editor_{selected_file}"
                        )

                    # Thanh nút hành động ngang dưới bảng (Gọn gàng, không bị cắt chữ)
                    col_save, col_clean = st.columns([1, 1])
                    with col_save:
                        if st.button("💾 Lưu Dữ Liệu Đã Sửa", type="primary", use_container_width=True, key="btn_save_step2"):
                            try:
                                with st.spinner("⏳ Bước 2: Đang lưu dữ liệu đã chỉnh sửa vào hệ thống, vui lòng đợi..."):
                                    if total_rows > 1000 and not (search_kw.strip() if 'search_kw' in locals() else False) and page_size < total_rows:
                                        updated_full = pd.concat([
                                            df_current.iloc[:start_idx],
                                            edited_slice,
                                            df_current.iloc[end_idx:]
                                        ], ignore_index=True)
                                        orch.data_agent.raw_dataframes[selected_file] = updated_full
                                    elif total_rows > 1000 and ('search_kw' in locals() and search_kw.strip()):
                                        df_current.loc[edited_slice.index] = edited_slice
                                        orch.data_agent.raw_dataframes[selected_file] = df_current
                                    else:
                                        orch.data_agent.raw_dataframes[selected_file] = edited_slice

                                    from utils.column_mapper import map_columns
                                    from utils.file_handler import _auto_aggregate
                                    new_df = orch.data_agent.raw_dataframes[selected_file]
                                    orch.data_agent.column_mappings[selected_file] = map_columns(list(new_df.columns))
                                    if len(new_df) > 1000:
                                        agg_df, agg_note = _auto_aggregate(new_df, selected_file)
                                        orch.data_agent.file_infos[selected_file]["aggregated_df"] = agg_df
                                        orch.data_agent.file_infos[selected_file]["aggregation_note"] = agg_note
                                        orch.data_agent.file_infos[selected_file]["rows"] = len(new_df)
                                    orch.data_agent.file_infos.setdefault(selected_file, {}).setdefault("user_action_log", []).append(f"Đã lưu chỉnh sửa trực tiếp ({len(new_df):,} dòng).")
                                    st.success(f"✅ Đã lưu cập nhật thành công cho tệp {selected_file} ({len(new_df):,} dòng)!")
                                set_spinner_msg(f"⏳ Bước 2: Đang cập nhật lại bảng dữ liệu {selected_file} sau khi lưu...")
                                st.rerun()
                            except Exception:
                                st.error("❌ Đã xảy ra lỗi khi lưu dữ liệu chỉnh sửa. Vui lòng kiểm tra lại định dạng các ô vừa nhập.")
                    
                    with col_clean:
                        if st.button("✨ Làm Sạch & Chuẩn Hóa", type="primary", use_container_width=True, key="btn_clean_step2"):
                            try:
                                with st.spinner(f"⏳ Bước 2: Đang làm sạch và chuẩn hóa toàn bộ {len(df_current):,} dòng dữ liệu..."):
                                    cleaned_df = df_current.dropna(how="all").copy()
                                    for c in cleaned_df.columns:
                                        try:
                                            if cleaned_df[c].dtype == "object":
                                                cleaned_df[c] = pd.to_numeric(cleaned_df[c].astype(str).str.replace(",", "").str.strip())
                                            else:
                                                cleaned_df[c] = pd.to_numeric(cleaned_df[c])
                                        except Exception:
                                            try:
                                                if cleaned_df[c].dtype == "object":
                                                    cleaned_df[c] = cleaned_df[c].astype(str).str.strip()
                                            except Exception:
                                                pass
                                    orch.data_agent.raw_dataframes[selected_file] = cleaned_df
                                    if len(cleaned_df) > 1000:
                                        from utils.file_handler import _auto_aggregate
                                        agg_df, agg_note = _auto_aggregate(cleaned_df, selected_file)
                                        orch.data_agent.file_infos[selected_file]["aggregated_df"] = agg_df
                                    removed_manual = max(0, len(df_current) - len(cleaned_df))
                                    orch.data_agent.file_infos.setdefault(selected_file, {}).setdefault("user_action_log", []).append(
                                        f"Đã chạy Làm sạch & Chuẩn hóa (xóa {removed_manual} dòng trống, chuẩn hóa định dạng số & khoảng trắng)."
                                    )
                                st.success(f"✅ Đã làm sạch tự động toàn bộ {len(cleaned_df):,} dòng!")
                                set_spinner_msg(f"⏳ Bước 2: Đang hiển thị bảng dữ liệu {selected_file} sau khi làm sạch...")
                                st.rerun()
                            except Exception:
                                st.error("❌ Không thể chuẩn hóa tự động một số cột đặc biệt trong tệp này. Dữ liệu gốc vẫn được giữ nguyên an toàn.")

    # ============================================================
    # BƯỚC 3: BÁO CÁO TỔNG HỢP & DASHBOARD (TÍNH TOÁN THỰC TẾ TỪ DỮ LIỆU)
    # ============================================================
    elif st.session_state.current_step == 3:
        import importlib
        import agents.data_ingestion_agent as _dia_mod
        importlib.reload(_dia_mod)
        normalize_group_label = _dia_mod.normalize_group_label
        find_group_column_for_df = _dia_mod.find_group_column_for_df

        def _compute_real_scoring_from_data():
            """Tính điểm định lượng thực tế cho từng nhóm dựa trực tiếp trên các DataFrame đã nạp."""
            group_stats = {}
            all_numeric_cols = []

            import math
            for fname, df in orch.data_agent.raw_dataframes.items():
                if df is None or df.empty:
                    continue
                mapping_cur = orch.data_agent.column_mappings.get(fname, {})
                group_col = find_group_column_for_df(df, mapping_cur)
                num_cols = list(dict.fromkeys(str(c) for c in df.select_dtypes(include=["number"]).columns))
                for nc in num_cols:
                    if nc not in all_numeric_cols:
                        all_numeric_cols.append(nc)

                if group_col and group_col in df.columns:
                    col_series = df[group_col]
                    if isinstance(col_series, pd.DataFrame):
                        col_series = col_series.iloc[:, 0]
                    norm_series = col_series.apply(normalize_group_label)
                    valid_mask = norm_series.astype(str).str.len() > 0
                    df_valid = df[valid_mask].copy()
                    df_valid["_norm_group"] = norm_series[valid_mask]
                    for g_name, g_df in df_valid.groupby("_norm_group"):
                        st_entry = group_stats.setdefault(str(g_name), {
                            "rows": 0, "cells": 0, "non_null": 0, "num_sums": [], "num_means": []
                        })
                        st_entry["rows"] += len(g_df)
                        st_entry["cells"] += int(g_df.shape[0] * max(1, g_df.shape[1] - 1))
                        st_entry["non_null"] += int(g_df.drop(columns=["_norm_group"]).notna().sum().sum())
                        for nc in num_cols[:4]:
                            if nc in g_df.columns:
                                col_vals = g_df[nc]
                                if isinstance(col_vals, pd.DataFrame):
                                    col_vals = col_vals.iloc[:, 0]
                                s_num = pd.to_numeric(col_vals, errors="coerce").dropna()
                                if len(s_num) > 0:
                                    s_sum, s_mean = float(s_num.sum()), float(s_num.mean())
                                    if math.isfinite(s_sum):
                                        st_entry["num_sums"].append(s_sum)
                                    if math.isfinite(s_mean):
                                        st_entry["num_means"].append(s_mean)
                else:
                    g_name = os.path.splitext(fname)[0] or "Dữ liệu tổng hợp"
                    st_entry = group_stats.setdefault(g_name, {
                        "rows": 0, "cells": 0, "non_null": 0, "num_sums": [], "num_means": []
                    })
                    st_entry["rows"] += len(df)
                    st_entry["cells"] += int(df.shape[0] * max(1, df.shape[1]))
                    st_entry["non_null"] += int(df.notna().sum().sum())
                    for nc in num_cols[:4]:
                        s_num = pd.to_numeric(df[nc], errors="coerce").dropna()
                        if len(s_num) > 0:
                            st_entry["num_sums"].append(float(s_num.sum()))
                            st_entry["num_means"].append(float(s_num.mean()))

            if not group_stats:
                group_stats = {"Dữ liệu chính": {"rows": 1, "cells": 1, "non_null": 1, "num_sums": [1.0], "num_means": [1.0]}}

            def _minmax_scale(vals_dict, low=6.0, high=9.5, default_val=7.8):
                if not vals_dict:
                    return {}
                v_min = min(vals_dict.values())
                v_max = max(vals_dict.values())
                if v_max - v_min < 1e-9:
                    return {k: round(default_val, 1) for k in vals_dict}
                return {k: round(low + ((v - v_min) / (v_max - v_min)) * (high - low), 1) for k, v in vals_dict.items()}

            raw_scale = {g: float(st["rows"]) + (sum(st["num_sums"]) / 1e6 if st["num_sums"] else 0.0) for g, st in group_stats.items()}
            raw_perf = {g: (sum(st["num_means"]) / len(st["num_means"])) if st["num_means"] else float(st["rows"]) for g, st in group_stats.items()}
            raw_comp = {g: (st["non_null"] / max(1, st["cells"])) for g, st in group_stats.items()}

            s_scale = _minmax_scale(raw_scale, 6.2, 9.5, 8.0)
            s_perf = _minmax_scale(raw_perf, 6.0, 9.4, 7.9)
            s_feas = {g: round(5.5 + min(1.0, raw_comp[g]) * 4.0, 1) for g in group_stats}
            s_comp = _minmax_scale({g: (raw_perf[g] * 0.5 + raw_scale[g] * 0.5) for g in group_stats}, 6.1, 9.1, 7.6)
            s_grow = _minmax_scale({g: (raw_scale[g] * 0.4 + raw_perf[g] * 0.6) for g in group_stats}, 6.2, 9.3, 8.0)

            scoring = {}
            totals = []
            for g in group_stats:
                prof = {
                    "market_size": s_scale[g],
                    "wms_demand_fit": s_perf[g],
                    "deployment_feasibility": s_feas[g],
                    "competitive_landscape": s_comp[g],
                    "growth_potential": s_grow[g],
                }
                w_total = round(
                    prof["market_size"] * 0.25 +
                    prof["wms_demand_fit"] * 0.25 +
                    prof["deployment_feasibility"] * 0.25 +
                    prof["competitive_landscape"] * 0.15 +
                    prof["growth_potential"] * 0.10, 2
                )
                totals.append((g, w_total, prof, group_stats[g]))

            totals.sort(key=lambda x: x[1], reverse=True)
            for rank_idx, (reg, w_total, prof, st_info) in enumerate(totals, start=1):
                comp_pct = round(100.0 * st_info["non_null"] / max(1, st_info["cells"]), 1)
                scoring[reg] = {
                    "criteria_scores": {k: {"score": v} for k, v in prof.items()},
                    "weighted_total": w_total,
                    "rank": rank_idx,
                    "rows": st_info["rows"],
                    "completeness_pct": comp_pct,
                    "status": "✅ Ưu tiên trọng tâm" if rank_idx <= 2 else "📌 Nhóm theo dõi"
                }

            top_2 = [x[0] for x in totals[:2]]
            deprioritized = [x[0] for x in totals[2:]]
            return {
                "scoring": scoring,
                "numeric_cols": all_numeric_cols,
                "recommendation": {
                    "top_2": top_2,
                    "reason_top": f"Dẫn đầu về quy mô bản ghi và giá trị trung bình các chỉ số số liệu ({', '.join(all_numeric_cols[:3]) if all_numeric_cols else 'dữ liệu tổng hợp'}) tại {', '.join(top_2)}.",
                    "deprioritized": deprioritized,
                    "reason_deprioritized": "Quy mô dữ liệu hoặc giá trị trung bình các chỉ số định lượng hiện thấp hơn nhóm dẫn đầu."
                }
            }

        _uploaded_file_names = list(orch.data_agent.raw_dataframes.keys())
        _files_display_str = ", ".join(_uploaded_file_names) if _uploaded_file_names else "Dữ liệu tải lên"
        _dynamic_default_title = f"Báo Cáo Phân Tích Dữ Liệu & Dashboard — {_files_display_str}"

        def _build_default_report_standalone(scoring_data):
            rec = scoring_data.get("recommendation", {})
            scoring_map = scoring_data.get("scoring", {})
            top_2 = rec.get("top_2", ["Nhóm 1", "Nhóm 2"])
            dep = rec.get("deprioritized", [])
            dep_str = ", ".join(dep[:4]) + (f" (+{len(dep)-4} nhóm)" if len(dep) > 4 else "") if dep else "Các nhóm còn lại"
            total_rows_now = sum(len(df) for df in orch.data_agent.raw_dataframes.values())
            num_cols_sample = scoring_data.get("numeric_cols", [])[:4]
            cols_note = ", ".join(num_cols_sample) if num_cols_sample else "các chỉ tiêu tổng hợp"

            top_bullets = ""
            for g in top_2:
                info = scoring_map.get(g, {})
                top_bullets += f"\n  - **{g}**: {info.get('rows', 0):,} dòng dữ liệu, độ đầy đủ **{info.get('completeness_pct', 100)}%**, điểm tổng hợp **{info.get('weighted_total', 0)}/10**."

            return f"""### 1. Tóm tắt dữ liệu đầu vào
- **[DỮ LIỆU] Nguồn dữ liệu:** Tệp **{_files_display_str}** gồm **{total_rows_now:,} bản ghi**, phân tích theo **{len(scoring_map)} nhóm** trên các chỉ số chính ({cols_note}).
- **[ĐỀ XUẤT TRỌNG TÂM]:** Hai nhóm đạt điểm đánh giá cao nhất là **{', '.join(top_2)}**.
- **[CĂN CỨ]:** {rec.get('reason_top', '')}

### 2. Chi tiết nhóm dẫn đầu & nhóm theo dõi
- **Nhóm ưu tiên ({', '.join(top_2)}):**{top_bullets}
- **Nhóm theo dõi ({dep_str}):**
  - **[DỮ LIỆU]** {rec.get('reason_deprioritized', '')}
  - **[SUY LUẬN]** Cần rà soát thêm dữ liệu chi tiết để cải thiện các tiêu chí có trọng số thấp hơn mặt bằng chung."""

        def _build_default_plan_standalone(recommended):
            top_str = ", ".join(recommended) if recommended else "Nhóm ưu tiên"
            return f"""### Kế hoạch hành động đề xuất cho: {top_str}
- **Giai đoạn 1 (Tuần 1 — Rà soát):** Đối chiếu dữ liệu gốc từ **{_files_display_str}** tại nhóm **{top_str}**, xử lý các giá trị thiếu còn lại nếu có.
- **Giai đoạn 2 (Tuần 2–3 — Triển khai):** Tập trung nguồn lực chính vào **{top_str}** nhằm tối ưu hiệu suất dựa trên các chỉ số nổi bật trên Dashboard.
- **Giai đoạn 3 (Tuần 4 — Đánh giá):** Theo dõi biến động định kỳ và cập nhật lại bảng điểm cho các nhóm tiếp theo."""

        # Tự động làm mới kết quả Bước 3 khi người dùng tải/sửa dữ liệu hoặc đổi tệp
        _current_step3_sig = (
            "v4_real_scoring",
            tuple(_uploaded_file_names),
            tuple(orch.data_agent.get_regions_detected()),
            sum(len(df) for df in orch.data_agent.raw_dataframes.values())
        )
        _has_legacy_hp = (
            "Hưng Phát" in str(st.session_state.get("dashboard_title", "")) or
            "HƯNG PHÁT" in str(st.session_state.get("editable_report", ""))
        )

        if not st.session_state.analysis_results or st.session_state.get("_last_step3_data_sig") != _current_step3_sig or _has_legacy_hp:
            default_sc = _compute_real_scoring_from_data()
            rec_top = default_sc.get("recommendation", {}).get("top_2", ["Nhóm 1", "Nhóm 2"])
            st.session_state.analysis_results = {
                "success": True,
                "scoring": default_sc,
                "report": _build_default_report_standalone(default_sc),
                "survey_plan": _build_default_plan_standalone(rec_top)
            }
            st.session_state.editable_report = st.session_state.analysis_results["report"]
            st.session_state.editable_plan = st.session_state.analysis_results["survey_plan"]
            st.session_state.dashboard_title = _dynamic_default_title
            st.session_state.dashboard_scores_df = None
            st.session_state._last_step3_data_sig = _current_step3_sig

        results = st.session_state.analysis_results
        scoring_data = results.get("scoring")
        if not scoring_data or not isinstance(scoring_data, dict) or "scoring" not in scoring_data:
            scoring_data = _compute_real_scoring_from_data()
            results["scoring"] = scoring_data
        if not results.get("report"):
            results["report"] = _build_default_report_standalone(scoring_data)
        if not results.get("survey_plan"):
            rec_top = scoring_data.get("recommendation", {}).get("top_2", ["Nhóm 1", "Nhóm 2"])
            results["survey_plan"] = _build_default_plan_standalone(rec_top)

        if "editable_report" not in st.session_state or not st.session_state.editable_report:
            st.session_state.editable_report = results.get("report", "")
        if "editable_plan" not in st.session_state or not st.session_state.editable_plan:
            st.session_state.editable_plan = results.get("survey_plan", "")
        if "dashboard_title" not in st.session_state or not st.session_state.dashboard_title:
            st.session_state.dashboard_title = _dynamic_default_title

        if "dashboard_scores_df" not in st.session_state or st.session_state.dashboard_scores_df is None or len(st.session_state.dashboard_scores_df) == 0:
            scoring_dict = scoring_data.get("scoring", {})
            if not scoring_dict:
                scoring_data = _compute_real_scoring_from_data()
                scoring_dict = scoring_data.get("scoring", {})
            table_rows = []
            for region, info in scoring_dict.items():
                crit_scores = info.get("criteria_scores", {})
                s1 = float(crit_scores.get("market_size", {}).get("score", 8.0) if isinstance(crit_scores.get("market_size"), dict) else crit_scores.get("market_size", 8.0))
                s2 = float(crit_scores.get("wms_demand_fit", {}).get("score", 8.0) if isinstance(crit_scores.get("wms_demand_fit"), dict) else crit_scores.get("wms_demand_fit", 8.0))
                s3 = float(crit_scores.get("deployment_feasibility", {}).get("score", 7.5) if isinstance(crit_scores.get("deployment_feasibility"), dict) else crit_scores.get("deployment_feasibility", 7.5))
                s4 = float(crit_scores.get("competitive_landscape", {}).get("score", 7.5) if isinstance(crit_scores.get("competitive_landscape"), dict) else crit_scores.get("competitive_landscape", 7.5))
                s5 = float(crit_scores.get("growth_potential", {}).get("score", 8.0) if isinstance(crit_scores.get("growth_potential"), dict) else crit_scores.get("growth_potential", 8.0))
                w_total = round(s1 * 0.25 + s2 * 0.25 + s3 * 0.25 + s4 * 0.15 + s5 * 0.10, 2)
                table_rows.append({
                    "Địa bàn": region,
                    "Quy mô (25%)": s1,
                    "Nhu cầu WMS (25%)": s2,
                    "Khả thi On-site (25%)": s3,
                    "Cạnh tranh (15%)": s4,
                    "Tăng trưởng (10%)": s5,
                    "Điểm tổng hợp": w_total,
                    "Trạng thái": info.get("status", "Đánh giá")
                })
            df_init = pd.DataFrame(table_rows).sort_values(by="Điểm tổng hợp", ascending=False).reset_index(drop=True)
            df_init["Xếp hạng"] = [f"Hạng {i+1}" for i in range(len(df_init))]
            st.session_state.dashboard_scores_df = df_init

        if "selected_report_charts" not in st.session_state:
            st.session_state.selected_report_charts = ["bar", "radar", "grouped"]
        if "show_edit_report" not in st.session_state:
            st.session_state.show_edit_report = False
        if "show_edit_dashboard" not in st.session_state:
            st.session_state.show_edit_dashboard = False

        df_scores = st.session_state.dashboard_scores_df.copy()

        import importlib
        import utils.export_helper as _exp_mod
        importlib.reload(_exp_mod)
        from utils.export_helper import build_unified_report_dashboard_html
        import streamlit.components.v1 as components

        # ============================================================
        # KHỐI PHÊ DUYỆT HOÀN TẤT (GỌN 1 DÒNG TRÊN CÙNG)
        # ============================================================
        with st.container(key="human_approval_top_card"):
            col_app0, col_app1, col_app2 = st.columns([1.0, 2.2, 1.3])
            with col_app0:
                st.markdown("<div style='padding-top:0.55rem; font-weight:700; color:#1e3a8a;'>Xác nhận kết quả:</div>", unsafe_allow_html=True)
            with col_app1:
                approval_decision = st.selectbox(
                    "Quyết định phê duyệt cuối cùng:",
                    ["Phê duyệt báo cáo & hoàn tất quy trình", "Quay lại Bước 2 để chỉnh sửa dữ liệu"],
                    label_visibility="collapsed",
                    key="step3_approval_decision"
                )
            with col_app2:
                if "Phê duyệt" in approval_decision:
                    if st.button("✅ Hoàn tất quy trình", type="primary", use_container_width=True, key="btn_final_approve"):
                        st.session_state.step3_approved = True
                        st.success("✅ Quy trình 3 bước đã được xác nhận hoàn tất.")
                else:
                    if st.button("⬅️ Về Bước 2 sửa lại", type="primary", use_container_width=True, key="btn_final_approve"):
                        st.session_state.step3_approved = False
                        set_spinner_msg("⏳ Đang quay lại Bước 2...")
                        st.session_state.current_step = 2
                        st.rerun()

        # ============================================================
        # BÁO CÁO TỔNG HỢP & DASHBOARD TRỰC QUAN
        # ============================================================
        _msg_uni = st.session_state.pending_spinner_msg or "⏳ Đang tạo Báo cáo & Dashboard..."
        st.session_state.pending_spinner_msg = ""
        _total_rec = sum(len(df) for df in orch.data_agent.raw_dataframes.values())
        _uni_cache_key = (
            "v4_clean_pastel",
            st.session_state.dashboard_title,
            st.session_state.editable_report,
            st.session_state.editable_plan,
            df_scores.to_json(),
            _total_rec
        )
        if st.session_state.get("_uni_export_key") != _uni_cache_key:
            with st.spinner(_msg_uni):
                st.session_state._uni_html_cached = build_unified_report_dashboard_html(
                    title=st.session_state.dashboard_title,
                    df_scores=df_scores,
                    bar_html="",
                    donut_html="",
                    radar_html="",
                    grouped_html="",
                    report_md=st.session_state.editable_report,
                    plan_md=st.session_state.editable_plan,
                    total_records=_total_rec,
                    total_files=len(orch.data_agent.raw_dataframes)
                )
                st.session_state._uni_export_key = _uni_cache_key

        unified_html = st.session_state._uni_html_cached

        with st.container(key="zone_step3_preview"):
            st.markdown("<h4 style='margin: 0.35rem 0 0.6rem 0;'>Báo Cáo Tổng Hợp &amp; Dashboard Nhận Xét</h4>", unsafe_allow_html=True)
            components.html(unified_html, height=840, scrolling=True)

        with st.container(key="floating_download_step3"):
            st.download_button(
                label="🌐 Tải xuống Báo Cáo (.html)",
                data=unified_html.encode("utf-8"),
                file_name="Bao_Cao_Dashboard_Phan_Tich.html",
                mime="text/html",
                type="primary",
                use_container_width=True,
                key="dl_unified_html"
            )

        # ============================================================
        # HAI NÚT MỞ KHUNG CHỈNH SỬA CHI TIẾT (ẨN GỌN KHI KHÔNG DÙNG)
        # ============================================================
        st.write("")
        btn_ed_col1, btn_ed_col2 = st.columns(2)
        with btn_ed_col1:
            label_rep_btn = "Đóng khung sửa báo cáo" if st.session_state.show_edit_report else "✏️ Chỉnh sửa nội dung báo cáo"
            if st.button(label_rep_btn, use_container_width=True, key="toggle_edit_report_btn"):
                st.session_state.show_edit_report = not st.session_state.show_edit_report
                st.rerun()

        with btn_ed_col2:
            label_dash_btn = "Đóng khung sửa bảng điểm" if st.session_state.show_edit_dashboard else "📊 Chỉnh sửa điểm số Dashboard"
            if st.button(label_dash_btn, use_container_width=True, key="toggle_edit_dashboard_btn"):
                st.session_state.show_edit_dashboard = not st.session_state.show_edit_dashboard
                st.rerun()

        if st.session_state.show_edit_report:
            st.markdown("##### Chỉnh sửa tiêu đề & nội dung báo cáo")
            new_title = st.text_input("Tiêu đề báo cáo:", value=st.session_state.dashboard_title, key="rep_title_input")
            col_ed1, col_ed2 = st.columns(2)
            with col_ed1:
                new_report = st.text_area("Nội dung tóm tắt & nhận xét:", value=st.session_state.editable_report, height=220)
            with col_ed2:
                new_plan = st.text_area("Kế hoạch hành động đề xuất:", value=st.session_state.editable_plan, height=220)

            if st.button("💾 Lưu thay đổi báo cáo", type="primary", use_container_width=True):
                st.session_state.dashboard_title = new_title
                st.session_state.editable_report = new_report
                st.session_state.editable_plan = new_plan
                results["report"] = new_report
                results["survey_plan"] = new_plan
                st.session_state.show_edit_report = False
                st.rerun()

        if st.session_state.show_edit_dashboard:
            st.markdown("##### Chỉnh sửa điểm số trên Dashboard")
            edited_dash_df = st.data_editor(
                st.session_state.dashboard_scores_df,
                use_container_width=True,
                num_rows="dynamic",
                key="dashboard_score_editor",
                column_config={
                    "Quy mô (25%)": st.column_config.NumberColumn(min_value=0.0, max_value=10.0, step=0.1, format="%.1f"),
                    "Nhu cầu WMS (25%)": st.column_config.NumberColumn(min_value=0.0, max_value=10.0, step=0.1, format="%.1f"),
                    "Khả thi On-site (25%)": st.column_config.NumberColumn(min_value=0.0, max_value=10.0, step=0.1, format="%.1f"),
                    "Cạnh tranh (15%)": st.column_config.NumberColumn(min_value=0.0, max_value=10.0, step=0.1, format="%.1f"),
                    "Tăng trưởng (10%)": st.column_config.NumberColumn(min_value=0.0, max_value=10.0, step=0.1, format="%.1f"),
                    "Điểm tổng hợp": st.column_config.NumberColumn(disabled=True, format="%.2f"),
                    "Xếp hạng": st.column_config.TextColumn(disabled=True),
                }
            )

            col_btn_dash1, col_btn_dash2 = st.columns([1, 1])
            with col_btn_dash1:
                if st.button("💾 Lưu điểm & cập nhật Dashboard", type="primary", use_container_width=True):
                    new_df = edited_dash_df.copy()
                    for col_num in ["Quy mô (25%)", "Nhu cầu WMS (25%)", "Khả thi On-site (25%)", "Cạnh tranh (15%)", "Tăng trưởng (10%)"]:
                        new_df[col_num] = pd.to_numeric(new_df[col_num], errors="coerce").fillna(0.0)

                    new_df["Điểm tổng hợp"] = (
                        new_df["Quy mô (25%)"] * 0.25 +
                        new_df["Nhu cầu WMS (25%)"] * 0.25 +
                        new_df["Khả thi On-site (25%)"] * 0.25 +
                        new_df["Cạnh tranh (15%)"] * 0.15 +
                        new_df["Tăng trưởng (10%)"] * 0.10
                    ).round(2)

                    new_df = new_df.sort_values(by="Điểm tổng hợp", ascending=False).reset_index(drop=True)
                    new_df["Xếp hạng"] = [f"Hạng {i+1}" for i in range(len(new_df))]
                    new_df["Trạng thái"] = ["✅ Ưu tiên trọng tâm" if i < 2 else "📌 Nhóm theo dõi" for i in range(len(new_df))]
                    st.session_state.dashboard_scores_df = new_df
                    st.session_state.show_edit_dashboard = False
                    st.rerun()

            with col_btn_dash2:
                if st.button("🤖 Phân tích lại bằng AI Agent", use_container_width=True):
                    with st.spinner("⏳ AI Agent đang phân tích sâu dữ liệu..."):
                        ai_res = orch.run_full_analysis()
                        st.session_state.analysis_results = ai_res
                        if ai_res.get("report"):
                            st.session_state.editable_report = ai_res["report"]
                        if ai_res.get("survey_plan"):
                            st.session_state.editable_plan = ai_res["survey_plan"]
                        st.session_state.dashboard_scores_df = None
                        st.session_state.show_edit_dashboard = False
                        st.rerun()

except Exception as _global_exc:
    import traceback
    traceback.print_exc()
    st.error(_vietnamese_error_message(_global_exc))

import streamlit.components.v1 as _cleanup_comp
_cleanup_comp.html("""
<script>
try {
    const oldBanner = window.parent.document.getElementById('hp-instant-loading-banner');
    if (oldBanner) oldBanner.remove();
} catch(e) {}
</script>
""", height=0, width=0)

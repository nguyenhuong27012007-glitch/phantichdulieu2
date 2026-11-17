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
    initial_sidebar_state="expanded"
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

    /* Nền Xanh Dương Pastel hiện đại, có chiều sâu */
    .stApp {{
        background: radial-gradient(circle at 12% 10%, #dbeafe 0%, transparent 40%),
                    radial-gradient(circle at 88% 15%, #e0f2fe 0%, transparent 38%),
                    linear-gradient(180deg, #eff6ff 0%, #f4f8ff 50%, #f8fafc 100%) !important;
    }}

    /* Hiệu ứng chuyển trang mượt mà */
    @keyframes pageTransitionIn {{
        0% {{ opacity: 0; transform: translateY(6px); }}
        100% {{ opacity: 1; transform: translateY(0); }}
    }}

    /* Khung chính — Rộng toàn màn hình + viền nhấn xanh */
    .main .block-container,
    [data-testid="stMainBlockContainer"] {{
        background: rgba(255, 255, 255, 0.96) !important;
        border-radius: 22px !important;
        padding: 2rem 2.2rem 2rem 2.2rem !important;
        margin: 0.75rem auto !important;
        max-width: 98% !important;
        box-shadow: 0 12px 36px rgba(37, 99, 235, 0.07), 0 2px 8px rgba(15, 23, 42, 0.03) !important;
        border: 1px solid #dbeafe !important;
        border-top: 4px solid #3b82f6 !important;
    }}

    /* Khung thẻ con (bordered container) tinh tế */
    [data-testid="stVerticalBlockBorderWrapper"] {{
        background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%) !important;
        border-radius: 16px !important;
        border: 1px solid #dbeafe !important;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.04) !important;
    }}

    /* Tiêu đề chính (h2, h3) nổi bật với hiệu ứng chuyển sắc xanh dương */
    [data-testid="stMain"] h2, [data-testid="stMain"] h3, .main h2, .main h3 {{
        background: linear-gradient(90deg, #1e3a8a 0%, #2563eb 55%, #0284c7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
        letter-spacing: -0.02em !important;
        padding-bottom: 4px !important;
        border-bottom: 2.5px solid #93c5fd !important;
        display: inline-block !important;
    }}

    /* Tiêu đề mục con (h4, h5) nổi bật với thanh nhấn màu xanh bên trái */
    [data-testid="stMain"] h4, [data-testid="stMain"] h5, .main h4, .main h5 {{
        background: linear-gradient(90deg, #dbeafe 0%, rgba(239, 246, 255, 0.2) 100%) !important;
        border-left: 5px solid #2563eb !important;
        padding: 7px 14px !important;
        border-radius: 0 10px 10px 0 !important;
        color: #1e3a8a !important;
        font-weight: 800 !important;
        margin-bottom: 0.65rem !important;
    }}

    /* Nhãn của các ô nhập liệu (Lĩnh vực hoạt động, Ghi chú thêm, Mục tiêu...) nổi bật hơn */
    [data-testid="stWidgetLabel"] p {{
        color: #1d4ed8 !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
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
        background: transparent !important;
        border: none !important;
        border-radius: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
        max-width: 100% !important;
        width: 100% !important;
        box-shadow: none !important;
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

    /* THANH ĐIỀU HƯỚNG NGANG PILL CAPSULE BO TRÒN TRÊN ĐẦU (GIỐNG ẢNH MẪU) */
    .st-key-top_wizard_bar {{
        background: #ffffff !important;
        border-radius: 9999px !important;
        padding: 5px 12px !important;
        border: 1px solid rgba(226, 232, 240, 0.8) !important;
        box-shadow: 0 4px 18px rgba(37, 99, 235, 0.05) !important;
        margin-bottom: 1.5rem !important;
        position: sticky;
        top: 0.5rem;
        z-index: 999;
    }}
    .st-key-top_wizard_bar .stButton > button {{
        border-radius: 9999px !important;
        padding: 0.4rem 1.1rem !important;
        min-height: 42px !important;
        height: 42px !important;
        border: none !important;
        background: transparent !important;
        color: #475569 !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
        transition: all 0.2s ease !important;
    }}
    .st-key-top_wizard_bar .stButton > button p,
    .st-key-top_wizard_bar .stButton > button span {{
        font-size: 0.92rem !important;
        font-weight: 600 !important;
        white-space: nowrap !important;
        color: inherit !important;
    }}
    /* Bước đang chọn (Active Step) dạng capsule nổi bật gradient vàng cam */
    .st-key-top_wizard_bar .stButton > button[kind="primary"] {{
        background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%) !important;
        color: #0f172a !important;
        box-shadow: 0 4px 12px rgba(245, 158, 11, 0.25) !important;
    }}
    .st-key-top_wizard_bar .stButton > button[kind="primary"] p,
    .st-key-top_wizard_bar .stButton > button[kind="primary"] span {{
        color: #0f172a !important;
        font-weight: 700 !important;
    }}
    .st-key-top_wizard_bar .stButton > button[kind="secondary"] {{
        color: #64748b !important;
        background: transparent !important;
    }}
    .st-key-top_wizard_bar .stButton > button[kind="secondary"]:hover {{
        background: #f1f5f9 !important;
        color: #0f172a !important;
    }}

    /* ============================================================
       THIẾT KẾ BƯỚC 1 CHUẨN XÁC THEO MẪU (THẺ KÍNH TRẮNG, VIỀN NÉT ĐỨT, BADGE HOẶC)
       ============================================================ */
    .st-key-zone_upload_left,
    .st-key-zone_gsheet_right {{
        background: #ffffff !important;
        border: 1px solid rgba(226, 232, 240, 0.9) !important;
        border-radius: 20px !important;
        padding: 1.5rem !important;
        box-shadow: 0 4px 20px rgba(15, 23, 42, 0.04) !important;
        min-height: 250px !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: flex-start !important;
    }}

    /* Vùng Upload Kéo Thả Viền Nét Đứt Xanh Dương */
    div[data-testid="stFileUploader"] section {{
        background: #ffffff !important;
        border: 2px dashed #93c5fd !important;
        border-radius: 16px !important;
        min-height: 145px !important;
        padding: 1.2rem 1rem !important;
        text-align: center !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        transition: all 0.25s ease !important;
    }}
    div[data-testid="stFileUploader"] section:hover {{
        border-color: #3b82f6 !important;
        background: #f8fbff !important;
    }}
    div[data-testid="stFileUploader"] button {{
        display: none !important;
    }}

    /* Khung Viền Nét Đứt Vàng Cam Cho Ô Google Sheet */
    .st-key-step1_gsheet_inner_box {{
        border: 2px dashed #fcd34d !important;
        border-radius: 16px !important;
        min-height: 145px !important;
        padding: 1.5rem 1.2rem !important;
        background: #ffffff !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        gap: 8px !important;
    }}
    .st-key-step1_gsheet_box input {{
        background: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 10px !important;
        height: 44px !important;
        padding: 0 14px !important;
        font-size: 0.92rem !important;
        color: #334155 !important;
    }}

    /* Thẻ Bối Cảnh Doanh Nghiệp Viền Trắng Bo Tròn Đẹp */
    .st-key-zone_biz_context {{
        background: #ffffff !important;
        border: 1px solid rgba(226, 232, 240, 0.9) !important;
        border-radius: 20px !important;
        padding: 1.5rem 1.8rem !important;
        box-shadow: 0 4px 20px rgba(15, 23, 42, 0.04) !important;
        margin-top: 1.25rem !important;
    }}

    /* Nút AI Gợi Ý Tone Xanh Dương Nhạt Thanh Lịch */
    .st-key-btn_ai_suggest_ctx button {{
        background: #e0f2fe !important;
        color: #0284c7 !important;
        font-weight: 700 !important;
        border: 1.5px solid #bae6fd !important;
        border-radius: 9999px !important;
        padding: 0.55rem 1.4rem !important;
        box-shadow: 0 4px 14px rgba(2, 132, 199, 0.12) !important;
        transition: all 0.2s ease !important;
    }}
    .st-key-btn_ai_suggest_ctx button p,
    .st-key-btn_ai_suggest_ctx button span {{
        color: #0284c7 !important;
        font-weight: 700 !important;
    }}
    .st-key-btn_ai_suggest_ctx button:hover {{
        background: #bae6fd !important;
        color: #0369a1 !important;
        border-color: #7dd3fc !important;
        transform: translateY(-1px) !important;
    }}

    /* Định dạng nhãn và chữ bên trong ô Upload và Google Sheet hoàn toàn đồng nhất */
    div[data-testid="stFileUploader"] label p,
    div[data-testid="stFileUploader"] label span,
    .gsheet-hint-text {{
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 0.95rem !important;
        font-weight: 700 !important;
        color: #0f172a !important;
        line-height: 1.4 !important;
        margin: 0 !important;
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

    /* Nút Duyệt & Tải xuống cố định gọn ở góc dưới bên phải (không che nội dung bảng/chữ) */
    .st-key-floating_approve_step1,
    .st-key-floating_approve_step2,
    .st-key-floating_download_step3 {{
        position: fixed !important;
        right: 24px !important;
        bottom: 20px !important;
        top: auto !important;
        transform: none !important;
        z-index: 9999 !important;
        width: auto !important;
        min-width: 215px !important;
        background: rgba(255, 255, 255, 0.96) !important;
        backdrop-filter: blur(10px) !important;
        padding: 8px 10px !important;
        border-radius: 16px !important;
        box-shadow: 0 10px 28px rgba(37, 99, 235, 0.24) !important;
        border: 1.5px solid #93c5fd !important;
    }}

    /* Tên cột / mã trong dấu backtick có cỡ chữ bằng chữ thường */
    .main code, [data-testid="stAlert"] code, .stMarkdown code {{
        font-size: 1em !important;
        font-family: inherit !important;
        font-weight: 600 !important;
    }}

    /* ============================================================
       SIDEBAR THU GỌN CHỈ HIỂN THỊ ICON DỌC, HOVER DI CHUỘT LÀ TỰ MỞ RA
       ============================================================ */
    section[data-testid="stSidebar"] {{
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        height: 100vh !important;
        width: 64px !important;
        min-width: 64px !important;
        max-width: 64px !important;
        background: #f8fbff !important;
        border-right: 1.5px solid #dbeafe !important;
        box-shadow: 4px 0 20px rgba(37, 99, 235, 0.08) !important;
        transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1),
                    max-width 0.3s cubic-bezier(0.4, 0, 0.2, 1),
                    min-width 0.3s cubic-bezier(0.4, 0, 0.2, 1),
                    box-shadow 0.3s ease !important;
        overflow-x: hidden !important;
        overflow-y: hidden !important;
        z-index: 99999 !important;
        transform: translate3d(0, 0, 0) !important;
        visibility: visible !important;
    }}

    /* Khi rê chuột vào Sidebar: Tự động trượt mở rộng ra như menu bay */
    section[data-testid="stSidebar"]:hover {{
        width: 290px !important;
        min-width: 290px !important;
        max-width: 290px !important;
        background: #ffffff !important;
        box-shadow: 12px 0 35px rgba(30, 58, 138, 0.18) !important;
        overflow-y: auto !important;
    }}

    /* Luôn hiển thị sidebar, không bị ẩn bởi collapse state của Streamlit */
    section[data-testid="stSidebar"][aria-expanded="false"] {{
        margin-left: 0 !important;
        transform: translate3d(0, 0, 0) !important;
        display: block !important;
        width: 64px !important;
        min-width: 64px !important;
        max-width: 64px !important;
    }}

    /* Bố trí nội dung bên trong sidebar */
    section[data-testid="stSidebar"] > div:first-child {{
        width: 290px !important;
        padding: 1.2rem 0.4rem !important;
        box-sizing: border-box !important;
    }}

    /* Ẩn nút mũi tên đóng/mở mặc định của Streamlit vì đã có hover tự mở */
    [data-testid="stSidebarCollapseButton"],
    button[data-testid="baseButton-headerNoPadding"],
    [data-testid="collapsedControl"] {{
        display: none !important;
    }}

    /* Nút bấm trong Sidebar: Thu gọn thành Icon khi chưa hover */
    section[data-testid="stSidebar"] .stButton > button {{
        overflow: hidden !important;
        white-space: nowrap !important;
        text-align: left !important;
        justify-content: flex-start !important;
        border-radius: 12px !important;
        padding: 0.65rem 0.5rem !important;
        border: 1px solid transparent !important;
        background: transparent !important;
        transition: all 0.2s ease !important;
        color: #334155 !important;
        font-weight: 600 !important;
        font-size: 1.15rem !important;
        width: 100% !important;
    }}
    section[data-testid="stSidebar"] .stButton > button:hover {{
        background: #e0f2fe !important;
        color: #0284c7 !important;
        border-color: #bae6fd !important;
    }}

    /* Cột biểu tượng dọc nổi bật bo góc capsule giống thiết kế mẫu */
    .st-sidebar-pill-wrap {{
        display: flex;
        flex-direction: column;
        gap: 8px;
    }}

    /* Giữ khoảng cách lề trái cho nội dung chính không bị che bởi thanh icon */
    .main, [data-testid="stMain"] {{
        margin-left: 64px !important;
        transition: margin-left 0.3s ease !important;
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
            is_active_1 = (step == 1)
            b1_label = f"1   Bước 1: Nhập dữ liệu" if is_active_1 else f"{s1_icon} Bước 1: Nhập dữ liệu"
            if st.button(
                b1_label,
                key="top_nav_step1",
                use_container_width=True,
                type="primary" if is_active_1 else "secondary"
            ):
                set_spinner_msg("⏳ Đang chuyển sang Bước 1: Nhập dữ liệu...")
                st.session_state.current_step = 1
                st.rerun()

        with nav_col2:
            is_active_2 = (step == 2)
            b2_label = f"2   Bước 2: Làm sạch" if is_active_2 else f"{s2_icon} Bước 2: Làm sạch"
            if st.button(
                b2_label,
                key="top_nav_step2",
                use_container_width=True,
                type="primary" if is_active_2 else "secondary"
            ):
                if st.session_state.step1_approved:
                    set_spinner_msg("⏳ Đang mở Bước 2: Làm sạch...")
                    st.session_state.current_step = 2
                    st.rerun()
                else:
                    st.toast("⚠️ Vui lòng nạp file và duyệt Bước 1 trước!", icon="⚠️")

        with nav_col3:
            is_active_3 = (step == 3)
            b3_label = f"3   Bước 3: Tạo báo cáo" if is_active_3 else f"{s3_icon} Bước 3: Tạo báo cáo"
            if st.button(
                b3_label,
                key="top_nav_step3",
                use_container_width=True,
                type="primary" if is_active_3 else "secondary"
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

    if st.button("⊞   Tổng quan", use_container_width=True, key="sb_nav_0"):
        set_spinner_msg("⏳ Đang quay lại Trang Mở Đầu...")
        st.session_state.current_step = 0
        st.rerun()

    if st.button("🗂   Nhập bảng tính", use_container_width=True, key="sb_nav_1"):
        set_spinner_msg("⏳ Đang chuyển sang Bước 1: Nhập Dữ Liệu...")
        st.session_state.current_step = 1
        st.rerun()

    if st.button("🗄   Xử lý dữ liệu", use_container_width=True, key="sb_nav_2"):
        if st.session_state.step1_approved:
            set_spinner_msg("⏳ Đang mở Bước 2: Làm Sạch...")
            st.session_state.current_step = 2
            st.rerun()
        else:
            st.toast("⚠️ Vui lòng nạp file và Duyệt Bước 1 trước!", icon="⚠️")

    if st.button("📈   Báo cáo & Dashboard", use_container_width=True, key="sb_nav_3"):
        if st.session_state.step2_approved:
            set_spinner_msg("⏳ Đang mở Bước 3: Tạo Báo Cáo...")
            st.session_state.current_step = 3
            st.rerun()
        else:
            st.toast("⚠️ Vui lòng Duyệt Bước 2 trước!", icon="⚠️")

    if st.button("🔄   Làm mới phiên", use_container_width=True, key="sb_reset_session"):
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

def _render_excel_filter_toolbar(df_cur: pd.DataFrame, key_prefix: str):
    """Thanh công cụ lọc nhiều cột, tìm kiếm, sắp xếp và chọn cột hiển thị kiểu Excel."""
    col_f1, col_f2, col_f3, col_f4 = st.columns([1.2, 1.8, 1.1, 0.9])
    with col_f1:
        f_search = st.text_input("🔍 Tìm kiếm nhanh:", placeholder="Nhập từ khóa...", key=f"{key_prefix}_search")
    with col_f2:
        f_cols = st.multiselect("🔽 Lọc theo cột:", list(df_cur.columns), default=[], key=f"{key_prefix}_fcols")
    with col_f3:
        f_sort_col = st.selectbox("↕️ Sắp xếp theo:", ["(Mặc định)"] + list(df_cur.columns), key=f"{key_prefix}_scol")
    with col_f4:
        f_sort_asc = st.selectbox("Thứ tự:", ["Tăng dần", "Giảm dần"], key=f"{key_prefix}_sasc")

    active_filters = {}
    if f_cols:
        f_cols_ui = st.columns(min(len(f_cols), 3))
        for idx_fc, fcol in enumerate(f_cols):
            with f_cols_ui[idx_fc % 3]:
                uniq_vals = sorted(df_cur[fcol].dropna().astype(str).unique().tolist())[:300]
                picked_vals = st.multiselect(f"Giá trị `{fcol}`:", uniq_vals, key=f"{key_prefix}_fval_{fcol}")
                if picked_vals:
                    active_filters[fcol] = picked_vals

    show_cols = st.multiselect(
        "👁️ Chọn cột hiển thị (để trống = hiện tất cả):",
        list(df_cur.columns),
        default=[],
        key=f"{key_prefix}_cols"
    )

    view_df = df_cur
    if f_search and f_search.strip():
        kw = f_search.strip().lower()
        mask_kw = view_df.astype(str).apply(lambda col: col.str.lower().str.contains(kw, na=False)).any(axis=1)
        view_df = view_df[mask_kw]
    for fcol, fvals in active_filters.items():
        view_df = view_df[view_df[fcol].astype(str).isin(fvals)]
    if f_sort_col != "(Mặc định)":
        view_df = view_df.sort_values(by=f_sort_col, ascending=(f_sort_asc == "Tăng dần"), kind="mergesort")

    display_cols = show_cols if show_cols else list(view_df.columns)
    is_filtered = bool((f_search and f_search.strip()) or active_filters)
    if is_filtered:
        st.caption(f"🔎 Đang hiển thị **{len(view_df):,} / {len(df_cur):,}** dòng phù hợp.")
    return view_df, display_cols, is_filtered, bool(show_cols)


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
            <style>
                header[data-testid="stHeader"] {
                    background: transparent !important;
                }
                .main, [data-testid="stMain"] {
                    margin-left: 0 !important;
                }
                section[data-testid="stSidebar"] {
                    display: none !important;
                }
                .main .block-container, [data-testid="stMainBlockContainer"] {
                    padding: 2.6rem 0 0 0 !important;
                    margin: 0 !important;
                    max-width: 100% !important;
                    width: 100% !important;
                    overflow: hidden !important;
                    border: none !important;
                    border-radius: 0 !important;
                    box-shadow: none !important;
                    background: #F4F7FB !important;
                }
                .st-key-landing_stage_container div[data-testid="stVerticalBlock"] {
                    gap: 0 !important;
                }
                .st-key-btn_hero_start {
                    position: fixed !important;
                    left: -9999px !important;
                    top: -9999px !important;
                    opacity: 0 !important;
                    pointer-events: none !important;
                }
                iframe[title="streamlit_components_v1.html_v1"] {
                    display: block !important;
                    border: none !important;
                }
            </style>
            """, unsafe_allow_html=True)

            if st.button("Bắt đầu ➔", key="btn_hero_start", type="primary"):
                set_spinner_msg("⏳ Đang mở Bước 1...")
                st.session_state.current_step = 1
                st.rerun()

            import streamlit.components.v1 as _landing_comp
            _landing_html = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        body { 
            font-family: 'Plus Jakarta Sans', sans-serif; 
            margin: 0;
        }
        .marquee-container { 
            overflow: hidden; 
            white-space: nowrap; 
            width: 100%; 
            display: flex; 
        }
        .marquee-content { 
            display: flex; 
            animation: marquee 20s linear infinite; 
        }
        @keyframes marquee { 
            0% { transform: translateX(0); } 
            100% { transform: translateX(-50%); } 
        }
        .glass-panel {
            background: rgba(255, 255, 255, 0.75);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.6);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .interactive-card {
            transition: all 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
        }
        .interactive-card:hover {
            filter: brightness(0.97) contrast(1.05);
            box-shadow: 0 20px 30px -10px rgba(30, 58, 138, 0.22);
            border-color: rgba(59, 130, 246, 0.4);
        }
        /* Custom Glowing Cursor Follower */
        .cursor-glow {
            position: fixed;
            width: 380px;
            height: 380px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(59, 130, 246, 0.18) 0%, rgba(99, 102, 241, 0.08) 45%, transparent 70%);
            pointer-events: none;
            transform: translate(-50%, -50%);
            z-index: 1;
            transition: width 0.3s ease, height 0.3s ease, background 0.3s ease;
            mix-blend-mode: multiply;
        }
        .cursor-dot {
            position: fixed;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background-color: #2563eb;
            box-shadow: 0 0 10px rgba(37, 99, 235, 0.6);
            pointer-events: none;
            transform: translate(-50%, -50%);
            z-index: 50;
            transition: transform 0.12s ease-out, background-color 0.2s ease;
        }
        .interactive-area {
            transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease, transform 0.25s ease;
        }
        .interactive-area:hover {
            background-color: rgba(255, 255, 255, 0.95);
            border-color: rgba(37, 99, 235, 0.3);
            box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.1);
        }
    </style>
    <script>
        function triggerStart() {
            try {
                const parentDoc = window.parent.document;
                const btn = parentDoc.querySelector('.st-key-btn_hero_start button') || parentDoc.querySelector('button[kind="primary"]');
                if (btn) btn.click();
            } catch (e) {
                console.error(e);
            }
        }

        // Mouse motion & interactive hover tracking
        document.addEventListener('DOMContentLoaded', () => {
            const glow = document.getElementById('cursor-glow');
            const dot = document.getElementById('cursor-dot');
            
            let mouseX = -100, mouseY = -100;
            let currentX = -100, currentY = -100;

            window.addEventListener('mousemove', (e) => {
                mouseX = e.clientX;
                mouseY = e.clientY;
                if (dot) {
                    dot.style.left = `${mouseX}px`;
                    dot.style.top = `${mouseY}px`;
                }
            });

            function animateGlow() {
                currentX += (mouseX - currentX) * 0.15;
                currentY += (mouseY - currentY) * 0.15;
                if (glow) {
                    glow.style.left = `${currentX}px`;
                    glow.style.top = `${currentY}px`;
                }
                requestAnimationFrame(animateGlow);
            }
            animateGlow();

            // Enlarge glow when hovering interactive elements
            const hoverTargets = document.querySelectorAll('button, a, .interactive-card, .interactive-area');
            hoverTargets.forEach(el => {
                el.addEventListener('mouseenter', () => {
                    if (glow) {
                        glow.style.width = '480px';
                        glow.style.height = '480px';
                        glow.style.background = 'radial-gradient(circle, rgba(234, 179, 8, 0.22) 0%, rgba(59, 130, 246, 0.12) 45%, transparent 70%)';
                    }
                    if (dot) {
                        dot.style.transform = 'translate(-50%, -50%) scale(1.6)';
                        dot.style.backgroundColor = '#d97706';
                    }
                });
                el.addEventListener('mouseleave', () => {
                    if (glow) {
                        glow.style.width = '380px';
                        glow.style.height = '380px';
                        glow.style.background = 'radial-gradient(circle, rgba(59, 130, 246, 0.18) 0%, rgba(99, 102, 241, 0.08) 45%, transparent 70%)';
                    }
                    if (dot) {
                        dot.style.transform = 'translate(-50%, -50%) scale(1)';
                        dot.style.backgroundColor = '#2563eb';
                    }
                });
            });
        });
    </script>
</head>
<body class="bg-[#F4F7FB] text-slate-800 h-screen max-h-[660px] flex flex-col justify-between relative overflow-x-hidden">
    
    <!-- Con trỏ chuột phát sáng động (Mouse Glow & Cursor Dot) -->
    <div id="cursor-glow" class="cursor-glow"></div>
    <div id="cursor-dot" class="cursor-dot"></div>

    <!-- 1. CÁC HỌA TIẾT NỀN ĐÈ DƯỚI NỘI DUNG -->
    <div class="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-blue-200 rounded-full mix-blend-multiply filter blur-[120px] opacity-60 z-0 pointer-events-none"></div>
    <div class="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-indigo-200 rounded-full mix-blend-multiply filter blur-[120px] opacity-60 z-0 pointer-events-none"></div>

    <!-- Ngôi sao 8 cánh trang trí ở các khoảng trống (theo yêu cầu) -->
    <!-- 1. Vị trí trống phía trên ở giữa / giữa Navbar và Tiêu đề & Thẻ -->
    <svg class="absolute top-[2%] left-[32%] w-[260px] h-[260px] text-blue-300 opacity-25 z-0 pointer-events-none" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 2v20M17 5l-10 14M22 12H2M19 19L5 5"/>
    </svg>

    <!-- 2. Vị trí trống ở giữa nút Bắt đầu và Thẻ quy trình số 1 -->
    <svg class="absolute top-[44%] left-[38%] w-[220px] h-[220px] text-blue-300 opacity-25 z-0 pointer-events-none" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 2v20M17 5l-10 14M22 12H2M19 19L5 5"/>
    </svg>

    <!-- 3. Vị trí trống phía dưới cụm thẻ quy trình -->
    <svg class="absolute bottom-[3%] left-[54%] w-[260px] h-[260px] text-blue-300 opacity-25 z-0 pointer-events-none" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 2v20M17 5l-10 14M22 12H2M19 19L5 5"/>
    </svg>

    <!-- 2. THANH ĐIỀU HƯỚNG (NAVBAR) -->
    <header class="relative z-10 px-6 py-3.5 flex justify-between items-center whitespace-nowrap">
        <div class="bg-yellow-400 text-slate-900 font-bold px-4 py-1.5 text-xs rounded-full shadow-sm flex items-center gap-1.5 shrink-0">
            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path d="M10 2a8 8 0 100 16 8 8 0 000-16zm0 14a6 6 0 110-12 6 6 0 010 12z"/></svg>
            Phân tích dữ liệu
        </div>
        
        <nav class="flex items-center gap-2 bg-white/85 backdrop-blur-md px-2 py-1.5 rounded-full shadow-sm border border-slate-200/60 text-xs font-semibold text-slate-700 shrink-0 mx-2">
            <a href="javascript:void(0)" class="bg-gradient-to-r from-amber-500 to-yellow-500 text-slate-900 font-bold px-4 py-1.5 rounded-full shadow-sm">1. Giới thiệu</a>
            <a href="javascript:void(0)" onclick="triggerStart()" class="px-3 py-1.5 hover:text-amber-600 rounded-full transition">2. Quy trình</a>
            <a href="javascript:void(0)" onclick="triggerStart()" class="px-3 py-1.5 hover:text-amber-600 rounded-full transition">3. Xử lý Dữ liệu</a>
            <a href="javascript:void(0)" onclick="triggerStart()" class="px-3 py-1.5 hover:text-amber-600 rounded-full transition">4. Báo cáo & Dashboard</a>
        </nav>

        <div class="bg-white/80 backdrop-blur-md text-slate-700 font-semibold px-4 py-1.5 rounded-full shadow-sm border border-white/50 text-xs shrink-0">
            Hỗ trợ CSV, Excel, Google Sheet
        </div>
    </header>

    <!-- 3. NỘI DUNG CHÍNH (2 CỘT) -->
    <main class="relative z-10 flex-1 flex flex-col md:flex-row items-center justify-between px-8 py-4 gap-6">
        
        <!-- CỘT TRÁI: Tiêu đề & Nút -->
        <div class="w-full md:w-[46%] flex flex-col items-start gap-4 z-10">
            <div class="text-[11px] font-bold text-slate-600 uppercase tracking-widest bg-white/60 backdrop-blur-sm px-4 py-1.5 rounded-full shadow-sm border border-white/50">
                Nền tảng Quản trị Dữ liệu
            </div>

            <h1 class="text-[2.4rem] lg:text-[2.85rem] font-extrabold text-slate-900 leading-[1.12] tracking-tight">
                Dữ liệu thông minh<br>
                Báo cáo tức thì
            </h1>

            <div class="flex items-center gap-3">
                <button onclick="triggerStart()" class="bg-white text-slate-900 font-bold text-sm px-6 py-2.5 rounded-full shadow-lg border border-slate-100 tracking-wider hover:shadow-xl hover:-translate-y-0.5 transition duration-300 cursor-pointer">
                    BẮT ĐẦU
                </button>
                <button onclick="triggerStart()" class="w-11 h-11 bg-yellow-400 text-slate-900 rounded-full flex items-center justify-center shadow-lg hover:scale-105 hover:-translate-y-0.5 transition duration-300 cursor-pointer">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"/></svg>
                </button>
            </div>

            <p class="text-sm text-slate-600 max-w-lg leading-relaxed glass-panel p-4 rounded-2xl interactive-area hover:text-slate-900 transition-all cursor-default">
                Tự động kiểm tra, làm sạch, và điều phối chính xác dữ liệu từ tệp CSV, Excel hoặc Google Sheet. Hỗ trợ tổng hợp số liệu và tạo báo cáo Dashboard trực quan.
            </p>
        </div>

        <!-- CỘT PHẢI: 3 Thẻ xếp so le -->
        <div class="w-full md:w-[54%] flex flex-row items-center justify-center md:justify-end gap-3.5 z-10">
            
            <!-- Thẻ 1 (Thấp) -->
            <div onclick="triggerStart()" class="w-44 lg:w-48 glass-panel rounded-[1.5rem] p-4 shadow-xl flex flex-col relative translate-y-4 hover:-translate-y-1 interactive-card hover:bg-white hover:border-blue-300 transition duration-300 cursor-pointer">
                <div class="w-9 h-9 bg-blue-100 text-blue-600 rounded-xl flex items-center justify-center mb-3 font-bold text-base transition-transform group-hover:scale-110">1</div>
                <h3 class="text-base font-bold text-slate-800 hover:text-blue-600 mb-1 transition-colors">Nhập dữ liệu</h3>
                <p class="text-xs text-slate-500 font-medium">CSV, Excel, Google Sheet</p>
            </div>

            <!-- Thẻ 2 (Nhô cao, nổi bật) -->
            <div onclick="triggerStart()" class="w-44 lg:w-48 bg-white rounded-[1.5rem] p-4 shadow-2xl border border-blue-50 flex flex-col relative -translate-y-4 scale-105 z-20 hover:-translate-y-7 interactive-card hover:border-blue-400 hover:shadow-blue-200/50 transition duration-300 cursor-pointer">
                <div class="absolute -top-3 -right-3 w-16 h-16 bg-yellow-400 rounded-full mix-blend-multiply opacity-30 blur-2xl pointer-events-none"></div>
                <div class="flex justify-between items-start mb-3">
                    <div class="w-9 h-9 bg-blue-600 text-white rounded-xl flex items-center justify-center font-bold text-base shadow-md shadow-blue-200">2</div>
                </div>
                <h3 class="text-lg font-bold text-slate-900 mb-1">Làm sạch</h3>
                <p class="text-xs text-slate-500 font-medium leading-relaxed">Chuẩn hóa &amp; chỉnh sửa lỗi dữ liệu</p>
                
                <div class="mt-4 pt-3.5 flex items-center justify-between border-t border-slate-100">
                    <div class="flex flex-col">
                        <span class="text-xl font-black text-slate-800">100%</span>
                        <span class="text-[9px] text-slate-400 uppercase font-bold tracking-widest">Chính xác</span>
                    </div>
                    <div class="w-7 h-7 rounded-full bg-slate-50 flex items-center justify-center">
                        <svg class="w-3.5 h-3.5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6"/></svg>
                    </div>
                </div>
            </div>

            <!-- Thẻ 3 (Thấp) -->
            <div onclick="triggerStart()" class="w-44 lg:w-48 bg-amber-400/90 backdrop-blur-md rounded-[1.5rem] p-4 shadow-xl border border-amber-300 flex flex-col relative text-slate-900 translate-y-4 hover:-translate-y-1 interactive-card hover:bg-amber-400 hover:border-amber-400 hover:shadow-amber-300/50 transition duration-300 cursor-pointer">
                <div class="w-9 h-9 bg-white/40 text-slate-900 rounded-xl flex items-center justify-center mb-3 font-bold text-base shadow-sm">3</div>
                <h3 class="text-base font-bold mb-1">Tạo báo cáo</h3>
                <p class="text-xs text-slate-800/80 font-medium">Dashboard &amp; Xuất HTML</p>
                <div class="mt-5 flex text-xs items-center gap-1.5">
                    <svg class="w-4 h-4 opacity-80" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
                    <span class="font-bold tracking-wide uppercase text-[11px]">Xuất báo cáo</span>
                </div>
            </div>

        </div>
    </main>

    <!-- 4. FOOTER (MARQUEE) -->
    <footer class="relative z-10 w-full bg-white/90 backdrop-blur-md border-t border-blue-100 text-blue-700 py-2.5 shadow-sm mt-auto">
        <div class="marquee-container">
            <div class="marquee-content gap-10 font-bold text-xs tracking-widest uppercase">
                <span>✦ XỬ LÝ DỮ LIỆU THÔNG MINH</span>
                <span>✦ CHUẨN HÓA FORMAT</span>
                <span>✦ LOẠI BỎ TRÙNG LẶP</span>
                <span>✦ DASHBOARD TRỰC QUAN</span>
                <span>✦ XUẤT HTML BÁO CÁO</span>
                <span>✦ KIỂM TOÁN DỮ LIỆU</span>
                <span>✦ XỬ LÝ DỮ LIỆU THÔNG MINH</span>
                <span>✦ CHUẨN HÓA FORMAT</span>
                <span>✦ LOẠI BỎ TRÙNG LẶP</span>
                <span>✦ DASHBOARD TRỰC QUAN</span>
                <span>✦ XUẤT HTML BÁO CÁO</span>
                <span>✦ KIỂM TOÁN DỮ LIỆU</span>
            </div>
        </div>
    </footer>

</body>
</html>"""
            _landing_comp.html(_landing_html, height=660, scrolling=False)

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
            st.markdown("""
            <div style="margin-bottom:1.2rem; padding-bottom:0.6rem; border-bottom:3px solid #2563eb; display:inline-block;">
                <h2 style="font-size:2.2rem; font-weight:800; color:#0f172a; margin:0 0 6px 0; letter-spacing:-0.03em; line-height:1.2;">
                    🚀 Bước 1: Nhập dữ liệu
                </h2>
                <div style="font-size:1rem; color:#475569; font-weight:600;">
                    Tải lên tệp CSV / Excel hoặc dán đường dẫn Google Sheet công khai để bắt đầu.
                </div>
            </div>
            """, unsafe_allow_html=True)

        if (not has_loaded_files) or st.session_state.show_step1_uploader:
            col_up1, col_divider, col_up2 = st.columns([1, 0.12, 1])
    
            with col_up1:
                with st.container(key="zone_upload_left"):
                    st.markdown("""
                    <div style="display:flex; align-items:center; gap:8px; margin-bottom:12px; font-weight:700; color:#1e3a8a; font-size:1.02rem;">
                        <span style="color:#2563eb; font-size:1.15rem;">📄</span> Tải tệp
                    </div>
                    """, unsafe_allow_html=True)
                    uploaded_files = st.file_uploader(
                        "Kéo thả tệp CSV, Excel vào đây hoặc Nhấn để tải lên",
                        type=["csv", "xlsx", "xls"],
                        accept_multiple_files=True,
                        label_visibility="visible",
                        key="s1_file_uploader"
                    )
                    if uploaded_files:
                        if st.button("Nạp tệp đã chọn ➔", type="primary", use_container_width=True, key="btn_verify_upload"):
                            with st.spinner("⏳ Đang đọc và kiểm tra dữ liệu..."):
                                for up in uploaded_files:
                                    content = up.read()
                                    success, msg = orch.load_file(content, up.name)
                                    st.session_state.file_messages.append({"file": up.name, "success": success, "msg": msg})
                                    if success and up.name not in st.session_state.files_loaded:
                                        st.session_state.files_loaded.append(up.name)
                                st.session_state.show_step1_uploader = False
                            st.rerun()

            with col_divider:
                st.markdown("""
                <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; height:100%; min-height:220px;">
                    <div style="width:1px; height:40px; background:#cbd5e1;"></div>
                    <div style="background:#e0f2fe; color:#0284c7; font-weight:700; font-size:0.75rem; padding:4px 8px; border-radius:999px; border:1px solid #bae6fd; margin:6px 0; text-transform:uppercase;">HOẶC</div>
                    <div style="width:1px; height:40px; background:#cbd5e1;"></div>
                </div>
                """, unsafe_allow_html=True)

            with col_up2:
                with st.container(key="zone_gsheet_right"):
                    st.markdown("""
                    <div style="display:flex; align-items:center; gap:8px; margin-bottom:12px; font-weight:700; color:#1e3a8a; font-size:1.02rem;">
                        <span style="color:#10b981; font-size:1.15rem;">🔗</span> Đường dẫn Google Sheet
                    </div>
                    <div class="gsheet-hint-text" style="margin-bottom:8px;">
                        ● Đảm bảo liên kết đang ở chế độ xem công khai.
                    </div>
                    """, unsafe_allow_html=True)
                    with st.container(key="step1_gsheet_inner_box"):
                        with st.container(key="step1_gsheet_box"):
                            sheet_url = st.text_input(
                                "Liên kết Google Sheet",
                                placeholder="https://docs.google.com/spreadsheets/d/.../edit",
                                label_visibility="collapsed"
                            )
                    if sheet_url:
                        if st.button("Đọc Google Sheet ➔", type="primary", use_container_width=True, key="btn_verify_gsheet"):
                            with st.spinner("⏳ Đang kết nối Google Sheet..."):
                                success, msg = orch.load_google_sheet(sheet_url)
                                st.session_state.file_messages.append({"file": "Google Sheet", "success": success, "msg": msg})
                                if success:
                                    st.session_state.files_loaded.append("Google Sheet")
                                st.session_state.show_step1_uploader = False
                            st.rerun()

        if "_pending_biz_type" in st.session_state:
            st.session_state["biz_type"] = st.session_state.pop("_pending_biz_type")
        if "_pending_biz_questions" in st.session_state:
            st.session_state["biz_questions"] = st.session_state.pop("_pending_biz_questions")

        # ============================================================
        # BỐI CẢNH DOANH NGHIỆP (GIỐNG ẢNH MẪU 100%)
        # ============================================================
        with st.container(key="zone_biz_context"):
            col_b_head, col_b_btn = st.columns([2.5, 1.5])
            with col_b_head:
                st.markdown("""
                <div style="display:flex; align-items:center; gap:10px; font-weight:800; color:#0f172a; font-size:1.6rem; letter-spacing:-0.02em; padding-bottom:4px; border-bottom:2.5px solid #3b82f6; display:inline-flex;">
                    <span style="color:#2563eb; font-size:1.7rem;">📄</span> Bối cảnh doanh nghiệp
                </div>
                <div style="font-size:0.95rem; color:#475569; margin-top:6px; margin-bottom:14px; font-weight:600;">
                    Mô tả ngắn gọn về mô hình kinh doanh và mục tiêu phân tích.
                </div>
                """, unsafe_allow_html=True)
            with col_b_btn:
                if st.button("✨ AI gợi ý bối cảnh & câu hỏi theo tệp đã nạp", key="btn_ai_suggest_ctx", use_container_width=True):
                    if has_loaded_files:
                        first_fname = list(orch.data_agent.raw_dataframes.keys())[0]
                        first_df = orch.data_agent.raw_dataframes[first_fname]
                        num_c = [str(c) for c in first_df.select_dtypes(include=["number"]).columns[:4]]
                        if not num_c:
                            for c_cand in first_df.columns:
                                if pd.to_numeric(first_df[c_cand], errors="coerce").notna().mean() > 0.5:
                                    num_c.append(str(c_cand))
                                    if len(num_c) >= 4:
                                        break
                        cat_c = [str(c) for c in first_df.columns if str(c) not in num_c][:4]
                        cols_lower = " ".join(str(c).lower() for c in first_df.columns) + " " + first_fname.lower()
                        sug_type = "Kinh doanh / Bán lẻ & Vận hành"
                        if any(k in cols_lower for k in ["nhan_su", "nhansu", "hr", "employee", "salary", "luong", "department", "phong_ban"]):
                            sug_type = "Quản trị Nhân sự & Hiệu suất nhân viên"
                        elif any(k in cols_lower for k in ["ship", "delivery", "warehouse", "kho", "logistics"]):
                            sug_type = "Thương mại & Logistics / Chuỗi cung ứng"
                        elif any(k in cols_lower for k in ["campaign", "marketing", "ads", "click"]):
                            sug_type = "Marketing & Chiến dịch"

                        q_list = []
                        if cat_c and num_c:
                            q_list.append(f"1. Nhóm {cat_c[0]} nào đang có chỉ số {num_c[0]} cao nhất và thấp nhất?")
                            if len(num_c) > 1:
                                q_list.append(f"2. Mối tương quan giữa {num_c[0]} và {num_c[1]} theo từng {cat_c[0]} ra sao?")
                        if len(cat_c) > 1 and num_c:
                            q_list.append(f"3. Hiệu suất {num_c[0]} khác nhau như thế nào giữa các {cat_c[1]}?")
                        if len(num_c) > 2:
                            q_list.append(f"4. Phân bố của {num_c[2]} có điểm bất thường hay chênh lệch lớn giữa các nhóm không?")
                        q_list.append(f"{len(q_list)+1}. Tỷ lệ dữ liệu thiếu hoặc sai lệch trong tệp {first_fname} tập trung ở nhóm nào?")
                        q_list.append(f"{len(q_list)+1}. Đề xuất 2 nhóm ưu tiên hàng đầu cần tập trung cải thiện hoặc mở rộng là gì?")
                        st.session_state["_pending_biz_type"] = sug_type
                        st.session_state["_pending_biz_questions"] = "\n".join(q_list)
                        st.session_state["_ai_ctx_done_msg"] = f"✅ Đã gợi ý bối cảnh & câu hỏi dựa trên tệp `{first_fname}`!"
                        st.rerun()
                    else:
                        st.warning("⚠️ Bạn chưa nạp tệp dữ liệu nào. Vui lòng tải tệp CSV/Excel hoặc dán link Google Sheet ở khung phía trên trước nhé!")

            col_ctx1, col_ctx2 = st.columns([1, 1])
            with col_ctx1:
                st.text_input(
                    "Lĩnh vực hoạt động",
                    value=st.session_state.get("biz_type", ""),
                    placeholder="Ví dụ: Thương mại điện tử, chuỗi cửa hàng, phân phối hàng tiêu dùng...",
                    key="biz_type"
                )
                st.text_area(
                    "Ghi chú thêm",
                    value=st.session_state.get("biz_extra", ""),
                    placeholder="Ví dụ: Đang so sánh hiệu quả giữa các khu vực hoặc theo dõi biến động theo tháng...",
                    height=88,
                    key="biz_extra"
                )
            with col_ctx2:
                st.text_area(
                    "Mục tiêu / Câu hỏi cần giải đáp",
                    value=st.session_state.get("biz_questions", ""),
                    placeholder="Khu vực hoặc nhóm sản phẩm nào đang mang lại hiệu quả tốt nhất?\nChỉ số nào cần tối ưu trong giai đoạn tới?",
                    height=168,
                    key="biz_questions"
                )

            if st.session_state.get("_ai_ctx_done_msg"):
                st.success(st.session_state.pop("_ai_ctx_done_msg"))

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

                s1_view_df, display_cols, s1_is_filtered, s1_has_show_cols = _render_excel_filter_toolbar(
                    s1_df_cur, f"s1_{s1_chosen_file}"
                )

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
                                if not s1_is_filtered and not s1_has_show_cols and len(s1_df_cur) <= 1000:
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
            st.markdown(f"#### 📋 Chi tiết kiểm tra ({len(st.session_state.file_messages)} tệp)")
            with st.container():
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
            lbl_s2_btn = "Đóng bảng chỉnh sửa" if st.session_state.show_step2_editor else "✏️ Bấm vào đây nếu muốn sửa dữ liệu"
            if st.button(lbl_s2_btn, use_container_width=True, key="btn_toggle_s2_editor"):
                st.session_state.show_step2_editor = not st.session_state.show_step2_editor
                st.rerun()

            if True:
                empty_r = int(file_info_cur.get("empty_rows_removed", 0))
                empty_c = int(file_info_cur.get("empty_cols_removed", 0))
                missing_cells = int(df_current.isna().sum().sum())
                num_cols = [c for c in df_current.columns if pd.api.types.is_numeric_dtype(df_current[c])]
                mapped_dict = orch.data_agent.column_mappings.get(selected_file, {})
                user_edits = file_info_cur.get("user_action_log", [])

                with st.container(key="zone_step2_audit_card"):
                    dup_rows_cnt = int(df_current.duplicated().sum())
                    null_by_col = df_current.isna().sum()
                    null_cols_detail = [f"`{col}` ({int(cnt)} ô)" for col, cnt in null_by_col.items() if cnt > 0]
                    txt_cols = [str(c) for c in df_current.select_dtypes(exclude=["number"]).columns]
                    num_cols_str = ", ".join(f"`{c}`" for c in num_cols[:8]) + (f" (+{len(num_cols)-8} cột)" if len(num_cols) > 8 else "")
                    txt_cols_str = ", ".join(f"`{c}`" for c in txt_cols[:6]) + (f" (+{len(txt_cols)-6} cột)" if len(txt_cols) > 6 else "")
                    mapped_str = ", ".join(f"`{k}`" for k in list(mapped_dict.keys())[:8]) + (f" (+{len(mapped_dict)-8})" if len(mapped_dict) > 8 else "")

                    if empty_r == 0 and empty_c == 0 and missing_cells == 0 and dup_rows_cnt == 0 and not user_edits:
                        st.success(
                            f"✅ **File gốc `{selected_file}` của bạn đã chuẩn (OK 100%)!**\n\n"
                            f"- **Cấu trúc bảng:** Giữ nguyên toàn bộ **{total_rows:,} dòng × {len(df_current.columns)} cột**, không có dòng/cột trống thừa hay dòng trùng lặp.\n"
                            f"- **Độ đầy đủ dữ liệu:** 100% các ô đều có giá trị (0 ô trống).\n"
                            f"- **Các cột số đã chuẩn hóa ({len(num_cols)} cột):** {num_cols_str if num_cols else 'Không có'}.\n"
                            f"- **Các cột văn bản / phân loại ({len(txt_cols)} cột):** {txt_cols_str if txt_cols else 'Không có'}.\n"
                            f"- **Đã chuẩn hóa tên trường ({len(mapped_dict)} trường):** {mapped_str if mapped_dict else 'Tự động nhận diện'}."
                        )
                    else:
                        details = [f"🔍 **Những gì hệ thống đã kiểm tra & xử lý trên tệp `{selected_file}`:**"]
                        if empty_r > 0 or empty_c > 0:
                            details.append(f"- 🧹 **Đã tự động xóa:** `{empty_r}` dòng hoàn toàn trống và `{empty_c}` cột hoàn toàn trống (còn lại **{total_rows:,} dòng × {len(df_current.columns)} cột**).")
                        else:
                            details.append(f"- ✅ **Dòng & cột gốc:** Không có dòng/cột trống thừa (giữ nguyên **{total_rows:,} dòng × {len(df_current.columns)} cột**).")
                        if missing_cells > 0:
                            cols_missing_str = ", ".join(null_cols_detail[:6]) + (f" và {len(null_cols_detail)-6} cột khác" if len(null_cols_detail) > 6 else "")
                            details.append(f"- ⚠️ **Ô dữ liệu khuyết (NaN/Trống):** Phát hiện **{missing_cells:,} ô trống** tại {cols_missing_str}; hệ thống đã xử lý an toàn khi tính toán (không làm lệch điểm).")
                        else:
                            details.append("- ✅ **Độ đầy đủ:** 100% các ô dữ liệu đều có giá trị (0 ô trống).")
                        if dup_rows_cnt > 0:
                            details.append(f"- 🔁 **Dòng trùng lặp:** Phát hiện **{dup_rows_cnt:,} dòng** có nội dung giống hệt nhau.")
                        details.append(f"- 🔢 **Cột số đã chuẩn hóa ({len(num_cols)} cột):** {num_cols_str if num_cols else 'Không có'}.")
                        details.append(f"- 🏷️ **Cột phân loại / văn bản ({len(txt_cols)} cột):** {txt_cols_str if txt_cols else 'Không có'}.")
                        details.append(f"- 🔗 **Đã chuẩn hóa tên trường ({len(mapped_dict)} trường):** {mapped_str if mapped_dict else 'Tự động nhận diện'}.")
                        for u_log in user_edits:
                            details.append(f"- ✏️ **Thao tác của bạn:** {u_log}")
                        st.info("\n".join(details))

            if st.session_state.show_step2_editor:
                with st.container(key="zone_step2_workspace"):
                    s2_view_df, s2_display_cols, s2_is_filtered, s2_has_show_cols = _render_excel_filter_toolbar(
                        df_current, f"s2_{selected_file}"
                    )
                    if len(s2_view_df) > 1000:
                        df_slice = s2_view_df[s2_display_cols].iloc[:500]
                        edited_slice = st.data_editor(
                            df_slice,
                            use_container_width=True,
                            num_rows="dynamic",
                            height=540,
                            key=f"editor_{selected_file}_large"
                        )
                    else:
                        st.caption("💡 Nhấp đúp vào ô bất kỳ để sửa trực tiếp, sau đó bấm nút **Lưu Dữ Liệu** hoặc **Làm Sạch & Chuẩn Hóa** bên dưới:")
                        edited_slice = st.data_editor(
                            s2_view_df[s2_display_cols],
                            use_container_width=True,
                            num_rows="dynamic",
                            height=500,
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
            total_rows_now = sum(len(df) for df in orch.data_agent.raw_dataframes.values())
            num_cols_sample = scoring_data.get("numeric_cols", [])[:5]
            cols_note = ", ".join(num_cols_sample) if num_cols_sample else "các chỉ tiêu tổng hợp"

            file_details_md = ""
            total_nulls_all = 0
            for fname, df_f in orch.data_agent.raw_dataframes.items():
                null_f = int(df_f.isna().sum().sum())
                total_nulls_all += null_f
                f_nums = [str(c) for c in df_f.select_dtypes(include=["number"]).columns[:3]]
                stat_bits = []
                for nc in f_nums:
                    s_col = pd.to_numeric(df_f[nc], errors="coerce").dropna()
                    if len(s_col) > 0:
                        stat_bits.append(f"`{nc}` (tổng **{s_col.sum():,.1f}**, TB **{s_col.mean():,.1f}**)")
                stat_str = "; ".join(stat_bits) if stat_bits else "dữ liệu phân loại"
                file_details_md += f"\n  - **`{fname}`** ({len(df_f):,} dòng × {len(df_f.columns)} cột, {null_f:,} ô trống): {stat_str}."

            top_bullets = ""
            for g in top_2:
                info = scoring_map.get(g, {})
                cs = info.get("criteria_scores", {})
                s_qm = cs.get("market_size", {}).get("score", 0)
                s_nc = cs.get("wms_demand_fit", {}).get("score", 0)
                s_kt = cs.get("deployment_feasibility", {}).get("score", 0)
                top_bullets += (
                    f"\n  - **{g}** — Điểm tổng hợp **{info.get('weighted_total', 0)}/10** "
                    f"({info.get('rows', 0):,} bản ghi, độ đầy đủ **{info.get('completeness_pct', 100)}%**; "
                    f"Quy mô: {s_qm}, Phù hợp: {s_nc}, Khả thi: {s_kt})."
                )

            dep_bullets = ""
            for g in dep[:4]:
                info = scoring_map.get(g, {})
                dep_bullets += f"\n  - **{g}**: **{info.get('weighted_total', 0)}/10** ({info.get('rows', 0):,} bản ghi, độ đầy đủ {info.get('completeness_pct', 100)}%)."
            if len(dep) > 4:
                dep_bullets += f"\n  - *Cùng {len(dep) - 4} nhóm khác có điểm thấp hơn trong bảng xếp hạng.*"
            if not dep_bullets:
                dep_bullets = "\n  - Không có nhóm nào bị xếp sau."

            return f"""### 1. Tổng quan dữ liệu từ các tệp đã nạp
- **[DỮ LIỆU] Quy mô tổng hợp:** **{len(orch.data_agent.raw_dataframes)} tệp** ({_files_display_str}) với tổng **{total_rows_now:,} bản ghi**, phân tích theo **{len(scoring_map)} nhóm** trên các chỉ số chính ({cols_note}).{file_details_md}
- **[CHẤT LƯỢNG DỮ LIỆU]:** Toàn bộ hệ thống hiện còn **{total_nulls_all:,} ô trống**; các phép tính đều đã được chuẩn hóa an toàn.

### 2. Đánh giá chi tiết nhóm dẫn đầu & nhóm theo dõi
- **[ĐỀ XUẤT TRỌNG TÂM]** Hai nhóm đạt hiệu suất cao nhất là **{', '.join(top_2)}** ({rec.get('reason_top', '')}):{top_bullets}
- **Nhóm cần theo dõi & cải thiện:**{dep_bullets}
- **[SUY LUẬN]** Các nhóm ưu tiên đang vượt trội về mật độ dữ liệu và giá trị trung bình chỉ số; các nhóm còn lại cần bổ sung thêm dữ liệu hoặc tối ưu các tiêu chí có trọng số cao."""

        def _build_default_plan_standalone(recommended):
            top_str = ", ".join(recommended) if recommended else "Nhóm ưu tiên"
            num_cols_sample = scoring_data.get("numeric_cols", [])[:3] if "scoring_data" in locals() else []
            kpi_str = ", ".join(f"**{c}**" for c in num_cols_sample) if num_cols_sample else "trọng tâm"
            dep_list = scoring_data.get("recommendation", {}).get("deprioritized", []) if "scoring_data" in locals() else []
            dep_note = f" và đối chiếu khoảng cách hiệu suất với nhóm **{', '.join(dep_list[:3])}**" if dep_list else ""
            return f"""### Kế hoạch hành động đề xuất cho: {top_str}
- **Giai đoạn 1 (Tuần 1 — Rà soát & Chuẩn hóa):** Kiểm tra lại các bản ghi gốc từ **{_files_display_str}** tại nhóm **{top_str}**, đảm bảo các chỉ số {kpi_str} không còn sai lệch hoặc giá trị khuyết.
- **Giai đoạn 2 (Tuần 2–3 — Triển khai trọng tâm):** Tập trung nguồn lực mở rộng và tối ưu vận hành tại **{top_str}** dựa trên các chỉ số {kpi_str}{dep_note}.
- **Giai đoạn 3 (Tuần 4 — Đo lường & Mở rộng):** Theo dõi biến động thực tế hàng tuần trên Dashboard, cập nhật lại bảng điểm để nhân rộng mô hình sang các nhóm tiếp theo."""

        # Tự động làm mới kết quả Bước 3 khi người dùng tải/sửa dữ liệu hoặc đổi tệp
        _current_step3_sig = (
            "v5_detailed_report",
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

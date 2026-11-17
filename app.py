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
from utils.file_handler import (
    detect_data_issues,
    apply_data_issue_fixes,
    get_issue_preview_rows,
    compute_data_health_metrics,
)

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
# HỆ THỐNG THIẾT KẾ CHUẨN UNSLOP (QUIET CHROME VS. RICH CONTENT)
# ============================================================
s0_bg = "#2563eb" if step == 0 else "#ffffff"
s0_color = "#ffffff" if step == 0 else "#0f172a"
s0_border = "#2563eb" if step == 0 else "#e2e8f0"

s1_icon = "✓" if st.session_state.step1_approved else "01"
s2_icon = "✓" if st.session_state.step2_approved else "02"
s3_icon = "✓" if st.session_state.step3_approved else "03"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap');
    
    /* Pass 5: Typography & Tabular Numerals */
    html, body, [class*="css"], .stMarkdown p, .stMarkdown span, .stMarkdown div, .stMarkdown li, label {{
        font-family: 'Inter', 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
        font-size: 0.94rem !important;
        line-height: 1.55 !important;
        color: #0f172a !important;
        -webkit-font-smoothing: antialiased !important;
    }}

    /* Căn thẳng trục số liệu trong toàn bộ bảng, thẻ KPI và bộ đếm (Pass 5: tabular-nums) */
    [data-testid="stMetricValue"],
    [data-testid="stDataFrame"],
    [data-testid="stTable"],
    table, td, th, .tabular-nums {{
        font-variant-numeric: tabular-nums !important;
    }}

    /* Thang bậc tiêu đề chuẩn (không dùng gradient text loè loẹt) */
    .stMarkdown h3, [data-testid="stMain"] h2, [data-testid="stMain"] h3, .main h2, .main h3 {{
        font-family: 'Plus Jakarta Sans', 'Inter', sans-serif !important;
        font-size: 1.25rem !important;
        font-weight: 700 !important;
        line-height: 1.3 !important;
        letter-spacing: -0.02em !important;
        margin-top: 0.25rem !important;
        margin-bottom: 0.5rem !important;
        color: #0f172a !important;
        background: none !important;
        -webkit-text-fill-color: #0f172a !important;
        border-bottom: none !important;
    }}
    .stMarkdown h4, [data-testid="stMain"] h4, .main h4 {{
        font-family: 'Plus Jakarta Sans', 'Inter', sans-serif !important;
        font-size: 1.02rem !important;
        font-weight: 600 !important;
        line-height: 1.35 !important;
        letter-spacing: -0.015em !important;
        color: #0f172a !important;
        background: #f8fafc !important;
        border: 1px solid #e2e8f0 !important;
        border-left: 3px solid #2563eb !important;
        padding: 8px 14px !important;
        border-radius: 8px !important;
        margin-top: 0.5rem !important;
        margin-bottom: 0.65rem !important;
    }}
    .stMarkdown h5, [data-testid="stMain"] h5, .main h5 {{
        font-size: 0.94rem !important;
        font-weight: 600 !important;
        line-height: 1.4 !important;
        color: #334155 !important;
        margin-top: 0.25rem !important;
        margin-bottom: 0.4rem !important;
    }}
    div[data-testid="stCaptionContainer"] p,
    div[data-testid="stCaptionContainer"] span {{
        font-size: 0.84rem !important;
        font-weight: 500 !important;
        line-height: 1.45 !important;
        color: #64748b !important;
    }}
    div[data-testid="stAlert"] {{
        border-radius: 10px !important;
        border-width: 1px !important;
    }}
    div[data-testid="stAlert"] p {{
        font-size: 0.91rem !important;
        line-height: 1.55 !important;
    }}

    /* Pass 2: Quiet Chrome — Nền xanh pastel dịu nhẹ đồng bộ (#F4F7FB) */
    html, body, .stApp {{
        background-color: #F4F7FB !important;
        background: linear-gradient(180deg, #F4F7FB 0%, #EEF3F9 100%) !important;
    }}

    /* Pass 9: Motion — Chuyển trang tinh tế 180ms */
    @keyframes pageTransitionIn {{
        0% {{ opacity: 0; transform: translateY(4px); }}
        100% {{ opacity: 1; transform: translateY(0); }}
    }}

    /* Pass 1: Spacing — Lưới chuẩn 8px */
    .main .block-container,
    [data-testid="stMainBlockContainer"] {{
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 1.25rem 2rem 3rem 2rem !important;
        margin: 0 auto !important;
        max-width: 1400px !important;
    }}

    /* Pass 7: Details — Bo góc lồng nhau chuẩn (Outer 12px, Inner 8px, Pill 6px) */
    [data-testid="stVerticalBlockBorderWrapper"] {{
        background: #ffffff !important;
        border-radius: 10px !important;
        border: 1px solid #e2e8f0 !important;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03) !important;
        transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
    }}
    [data-testid="stVerticalBlockBorderWrapper"]:hover {{
        border-color: #cbd5e1 !important;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.05) !important;
    }}

    /* Nhãn ô nhập liệu sạch sẽ, chuẩn cấp độ 2 */
    [data-testid="stWidgetLabel"] p {{
        color: #1e293b !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        letter-spacing: -0.01em !important;
    }}

    .st-key-landing_stage_container,
    .st-key-zone_upload_left,
    .st-key-zone_gsheet_right,
    .st-key-zone_step1_summary,
    .st-key-zone_step2_workspace,
    .st-key-zone_step3_preview {{
        animation: pageTransitionIn 0.18s cubic-bezier(0.16, 1, 0.3, 1) both !important;
    }}

    /* Thẻ khu vực (Surface Cards) chuẩn unslop */
    .st-key-zone_step1_summary,
    .st-key-zone_step2_workspace,
    .st-key-zone_step3_preview,
    .st-key-zone_step2_audit_card,
    div[data-testid="stMetric"] {{
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        padding: 1rem 1.25rem !important;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.03) !important;
        transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
    }}
    .st-key-zone_step1_summary:hover,
    .st-key-zone_step2_workspace:hover,
    .st-key-zone_step3_preview:hover,
    div[data-testid="stMetric"]:hover {{
        border-color: #cbd5e1 !important;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.05) !important;
    }}

    .st-key-landing_stage_container {{
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        margin: 0 !important;
        max-width: 100% !important;
        width: 100% !important;
        box-shadow: none !important;
    }}

    /* Nút bấm chuẩn sản phẩm (8px radius, hairline border, restrained hover) */
    .stButton > button,
    .stDownloadButton > button {{
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        min-height: 40px !important;
        padding: 0.4rem 1rem !important;
        border: 1px solid #cbd5e1 !important;
        background: #ffffff !important;
        color: #0f172a !important;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03) !important;
        transition: all 0.15s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }}
    .stButton > button p,
    .stButton > button span,
    .stDownloadButton > button p,
    .stDownloadButton > button span {{
        font-size: 0.88rem !important;
        font-weight: 600 !important;
        line-height: 1.25 !important;
    }}
    .stButton > button:hover,
    .stDownloadButton > button:hover {{
        border-color: #94a3b8 !important;
        background: #f8fafc !important;
        color: #0f172a !important;
    }}
    .stButton > button[kind="primary"],
    .stDownloadButton > button[kind="primary"] {{
        background: #2563eb !important;
        color: #ffffff !important;
        border: 1px solid #1d4ed8 !important;
        box-shadow: 0 1px 3px rgba(37, 99, 235, 0.2) !important;
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
        border-color: #1e40af !important;
    }}

    /* THANH ĐIỀU HƯỚNG NGANG (SEGMENTED STEPPER BAR CHUẨN UNSLOP) */
    .st-key-top_wizard_bar {{
        background: #ffffff !important;
        border-radius: 10px !important;
        padding: 6px 8px !important;
        border: 1px solid #e2e8f0 !important;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04) !important;
        margin-bottom: 1.25rem !important;
        position: sticky;
        top: 0.5rem;
        z-index: 999;
    }}
    .st-key-top_wizard_bar .stButton > button {{
        border-radius: 7px !important;
        padding: 0.4rem 1rem !important;
        min-height: 38px !important;
        height: 38px !important;
        border: 1px solid transparent !important;
        background: transparent !important;
        color: #475569 !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        box-shadow: none !important;
        transition: all 0.15s ease !important;
    }}
    .st-key-top_wizard_bar .stButton > button p,
    .st-key-top_wizard_bar .stButton > button span {{
        font-size: 0.88rem !important;
        font-weight: 600 !important;
        white-space: nowrap !important;
        color: inherit !important;
        font-variant-numeric: tabular-nums !important;
    }}
    .st-key-top_wizard_bar .stButton > button[kind="primary"] {{
        background: #0f172a !important;
        color: #ffffff !important;
        border: 1px solid #0f172a !important;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.12) !important;
    }}
    .st-key-top_wizard_bar .stButton > button[kind="primary"] p,
    .st-key-top_wizard_bar .stButton > button[kind="primary"] span {{
        color: #ffffff !important;
        font-weight: 600 !important;
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
       THIẾT KẾ BƯỚC 1 CHUẨN UNSLOP (ĐỒNG BỘ LƯỚI, VIỀN SẮC NÉT, TƯƠNG PHẢN CAO)
       ============================================================ */
    .st-key-zone_upload_left,
    .st-key-zone_gsheet_right {{
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        padding: 1.5rem !important;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.03) !important;
        min-height: 244px !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: flex-start !important;
        transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
    }}
    .st-key-zone_upload_left:hover,
    .st-key-zone_gsheet_right:hover {{
        border-color: #cbd5e1 !important;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.05) !important;
    }}

    /* Khung trong đồng bộ kích thước và hình học (Nested radius 8px) */
    .st-key-step1_file_inner_box,
    .st-key-step1_gsheet_inner_box {{
        border: 1.5px dashed #cbd5e1 !important;
        border-radius: 8px !important;
        min-height: 136px !important;
        padding: 1.25rem !important;
        background: #f8fafc !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        gap: 8px !important;
        transition: border-color 0.15s ease, background-color 0.15s ease !important;
    }}
    .st-key-step1_file_inner_box:hover,
    .st-key-step1_gsheet_inner_box:hover {{
        border-color: #2563eb !important;
        background: #ffffff !important;
    }}

    /* Vùng Upload Kéo Thả Trình Bày Y Hệt Khung Input Google Sheet */
    div[data-testid="stFileUploader"] section {{
        background: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03) !important;
        border-radius: 8px !important;
        min-height: 42px !important;
        height: 42px !important;
        padding: 0 14px !important;
        text-align: left !important;
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        justify-content: flex-start !important;
        transition: border-color 0.15s ease !important;
        box-sizing: border-box !important;
    }}
    div[data-testid="stFileUploader"] section:hover {{
        border-color: #2563eb !important;
        background: #ffffff !important;
    }}
    div[data-testid="stFileUploader"] section::after {{
        content: "file CSV, Excel" !important;
        color: #94a3b8 !important;
        font-family: 'Inter', 'Plus Jakarta Sans', sans-serif !important;
        font-size: 0.9rem !important;
        font-weight: 400 !important;
        pointer-events: none !important;
    }}
    div[data-testid="stFileUploader"] section [data-testid="stFileUploaderDropzoneInstructions"],
    div[data-testid="stFileUploader"] section [data-testid="stFileUploaderDropzoneInstructions"] * {{
        display: none !important;
    }}
    div[data-testid="stFileUploader"] button {{
        display: none !important;
    }}

    .st-key-step1_gsheet_box input {{
        background: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
        height: 42px !important;
        padding: 0 14px !important;
        font-size: 0.9rem !important;
        color: #0f172a !important;
    }}
    .st-key-step1_gsheet_box input:focus {{
        border-color: #2563eb !important;
    }}

    /* Thẻ Bối Cảnh Doanh Nghiệp */
    .st-key-zone_biz_context {{
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        padding: 1.5rem !important;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.03) !important;
        margin-top: 1rem !important;
        transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
    }}
    .st-key-zone_biz_context:hover {{
        border-color: #cbd5e1 !important;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.05) !important;
    }}

    /* Nút AI Gợi Ý Tone Xanh Dương Nhạt Thanh Lịch */
    .st-key-btn_ai_suggest_ctx button {{
        background: #e0f2fe !important;
        color: #0369a1 !important;
        font-weight: 600 !important;
        border: 1px solid #bae6fd !important;
        border-radius: 8px !important;
        padding: 0.45rem 1.1rem !important;
        box-shadow: none !important;
        transition: all 0.15s ease !important;
    }}
    .st-key-btn_ai_suggest_ctx button p,
    .st-key-btn_ai_suggest_ctx button span {{
        color: #0369a1 !important;
        font-weight: 600 !important;
    }}
    .st-key-btn_ai_suggest_ctx button:hover {{
        background: #bae6fd !important;
        color: #075985 !important;
        border-color: #7dd3fc !important;
    }}

    /* Ẩn hoàn toàn văn bản phụ (200MB per file, bullet, v.v.) bên trong ô Upload */
    div[data-testid="stFileUploader"] small,
    div[data-testid="stFileUploader"] [data-testid="stFileUploaderDropzoneInstructions"] > div > small,
    div[data-testid="stFileUploader"] [data-testid="stFileUploaderDropzoneInstructions"] span:last-child {{
        display: none !important;
        font-size: 0 !important;
        visibility: hidden !important;
        opacity: 0 !important;
    }}
    div[data-testid="stFileUploader"] label p,
    div[data-testid="stFileUploader"] label span,
    div[data-testid="stFileUploader"] label,
    div[data-testid="stFileUploader"] [data-testid="stWidgetLabel"] p {{
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 0.92rem !important;
        font-weight: 600 !important;
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
        color: #0f172a !important;
        padding: 16px 24px !important;
        border-radius: 10px !important;
        border: 1px solid #cbd5e1 !important;
        box-shadow: 0 10px 25px rgba(15, 23, 42, 0.12) !important;
        z-index: 999999 !important;
        text-align: center !important;
        min-width: 320px !important;
    }}
    div[data-testid="stSpinner"] p,
    div[data-testid="stSpinner"] span {{
        font-size: 0.92rem !important;
        font-weight: 600 !important;
        color: #0f172a !important;
    }}

    /* Nút "Xem thêm" thu gọn / mở rộng danh sách nhóm */
    details.inline-groups-details {{
        display: inline;
    }}
    details.inline-groups-details summary.more-groups-btn {{
        display: inline-block;
        list-style: none;
        cursor: pointer;
        background: #f1f5f9;
        color: #0f172a !important;
        border: 1px solid #cbd5e1;
        border-radius: 6px;
        padding: 1px 8px;
        margin-left: 6px;
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        user-select: none;
        transition: all 0.15s ease;
    }}
    details.inline-groups-details summary.more-groups-btn::-webkit-details-marker {{
        display: none;
    }}
    details.inline-groups-details summary.more-groups-btn:hover {{
        background: #e2e8f0;
    }}
    details.inline-groups-details .more-groups-expanded {{
        margin-top: 6px;
        padding: 8px 12px;
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        font-size: 0.86rem !important;
        color: #334155 !important;
        line-height: 1.5 !important;
    }}

    /* Nút Duyệt & Tải xuống cố định gọn ở góc dưới bên phải */
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
        min-width: 220px !important;
        background: #ffffff !important;
        padding: 8px 10px !important;
        border-radius: 10px !important;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.12) !important;
        border: 1px solid #cbd5e1 !important;
    }}

    /* Tên cột / mã trong dấu backtick chuẩn Monospace nhẹ */
    .main code, [data-testid="stAlert"] code, .stMarkdown code {{
        font-size: 0.86em !important;
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace !important;
        font-weight: 600 !important;
        background: #f1f5f9 !important;
        color: #0f172a !important;
        padding: 2px 5px !important;
        border-radius: 4px !important;
    }}

    /* ============================================================
       SIDEBAR THU GỌN CHỈ HIỂN THỊ ICON DỌC, HOVER DI CHUỘT TỰ MỞ RA
       ============================================================ */
    section[data-testid="stSidebar"] {{
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        height: 100vh !important;
        width: 60px !important;
        min-width: 60px !important;
        max-width: 60px !important;
        background: #ffffff !important;
        border-right: 1px solid #e2e8f0 !important;
        box-shadow: none !important;
        transition: width 0.2s cubic-bezier(0.16, 1, 0.3, 1),
                    max-width 0.2s cubic-bezier(0.16, 1, 0.3, 1),
                    min-width 0.2s cubic-bezier(0.16, 1, 0.3, 1),
                    box-shadow 0.2s ease !important;
        overflow-x: hidden !important;
        overflow-y: hidden !important;
        z-index: 99999 !important;
        transform: translate3d(0, 0, 0) !important;
        visibility: visible !important;
    }}

    section[data-testid="stSidebar"]:hover {{
        width: 280px !important;
        min-width: 280px !important;
        max-width: 280px !important;
        background: #ffffff !important;
        box-shadow: 8px 0 24px rgba(15, 23, 42, 0.08) !important;
        overflow-y: auto !important;
    }}

    section[data-testid="stSidebar"][aria-expanded="false"] {{
        margin-left: 0 !important;
        transform: translate3d(0, 0, 0) !important;
        display: block !important;
        width: 60px !important;
        min-width: 60px !important;
        max-width: 60px !important;
    }}

    section[data-testid="stSidebar"] > div:first-child {{
        width: 280px !important;
        padding: 1.2rem 0.5rem !important;
        box-sizing: border-box !important;
    }}

    [data-testid="stSidebarCollapseButton"],
    button[data-testid="baseButton-headerNoPadding"],
    [data-testid="collapsedControl"] {{
        display: none !important;
    }}

    section[data-testid="stSidebar"] .stButton > button {{
        overflow: hidden !important;
        white-space: nowrap !important;
        text-align: left !important;
        justify-content: flex-start !important;
        border-radius: 8px !important;
        padding: 0.55rem 0.6rem !important;
        border: 1px solid transparent !important;
        background: transparent !important;
        box-shadow: none !important;
        transition: all 0.15s ease !important;
        color: #334155 !important;
        font-weight: 500 !important;
        font-size: 0.92rem !important;
        width: 100% !important;
    }}
    section[data-testid="stSidebar"] .stButton > button:hover {{
        background: #f1f5f9 !important;
        color: #0f172a !important;
        border-color: #e2e8f0 !important;
    }}

    .main, [data-testid="stMain"] {{
        margin-left: 60px !important;
        transition: margin-left 0.2s ease !important;
    }}
</style>
""", unsafe_allow_html=True)

# Tinh chỉnh hiệu ứng con trỏ nhẹ nhàng chuẩn unslop (không dùng blob loè loẹt làm nhòe chữ)
import streamlit.components.v1 as _cursor_comp
_cursor_comp.html("""
<script>
    (function() {
        try {
            const parentDoc = window.parent.document;
            const oldGlow = parentDoc.getElementById('app-cursor-glow');
            const oldDot = parentDoc.getElementById('app-cursor-dot');
            if (oldGlow) oldGlow.remove();
            if (oldDot) oldDot.remove();
        } catch(e) {}
    })();
</script>
""", height=0)

# ============================================================
# CHỈ HIỂN THỊ THANH ĐIỀU HƯỚNG NGANG KHI ĐÃ VÀO BƯỚC 1, 2, 3 (ẨN Ở TRANG MỞ ĐẦU)
# ============================================================
if step != 0:
    with st.container(key="top_wizard_bar"):
        nav_col1, nav_col2, nav_col3 = st.columns([1, 1, 1])

        with nav_col1:
            is_active_1 = (step == 1)
            b1_label = f"01 · Bước 1: Nhập dữ liệu" if is_active_1 else f"{s1_icon} · Bước 1: Nhập dữ liệu"
            if st.button(
                b1_label,
                key="top_nav_step1",
                use_container_width=True,
                type="primary" if is_active_1 else "secondary"
            ):
                set_spinner_msg("Đang chuyển sang Bước 1: Nhập dữ liệu...")
                st.session_state.current_step = 1
                st.rerun()

        with nav_col2:
            is_active_2 = (step == 2)
            b2_label = f"02 · Bước 2: Làm sạch & Kiểm duyệt" if is_active_2 else f"{s2_icon} · Bước 2: Làm sạch & Kiểm duyệt"
            if st.button(
                b2_label,
                key="top_nav_step2",
                use_container_width=True,
                type="primary" if is_active_2 else "secondary"
            ):
                if st.session_state.step1_approved:
                    set_spinner_msg("Đang mở Bước 2: Làm sạch & Kiểm duyệt...")
                    st.session_state.current_step = 2
                    st.rerun()
                else:
                    st.toast("Vui lòng nạp file và duyệt Bước 1 trước.", icon="⚠️")

        with nav_col3:
            is_active_3 = (step == 3)
            b3_label = f"03 · Bước 3: Báo cáo & Dashboard" if is_active_3 else f"{s3_icon} · Bước 3: Báo cáo & Dashboard"
            if st.button(
                b3_label,
                key="top_nav_step3",
                use_container_width=True,
                type="primary" if is_active_3 else "secondary"
            ):
                if st.session_state.step2_approved:
                    set_spinner_msg("Đang mở Bước 3: Báo cáo & Dashboard...")
                    st.session_state.current_step = 3
                    st.rerun()
                else:
                    st.toast("Vui lòng duyệt Bước 2 trước khi sang Bước 3.", icon="⚠️")

# ============================================================
# SIDEBAR ĐIỀU HƯỚNG NHANH & CÀI ĐẶT ẨN GỌN
# ============================================================
with st.sidebar:
    st.markdown("<div style='color:#64748b; font-size:0.75rem; font-weight:600; text-transform:uppercase; letter-spacing:0.06em; padding:0 0.5rem; margin-bottom:0.5rem;'>Điều hướng</div>", unsafe_allow_html=True)

    if st.button("⊞   Tổng quan", use_container_width=True, key="sb_nav_0"):
        set_spinner_msg("Đang quay lại Trang Mở Đầu...")
        st.session_state.current_step = 0
        st.rerun()

    if st.button("01  Nhập bảng tính", use_container_width=True, key="sb_nav_1"):
        set_spinner_msg("Đang chuyển sang Bước 1: Nhập Dữ Liệu...")
        st.session_state.current_step = 1
        st.rerun()

    if st.button("02  Làm sạch & Kiểm duyệt", use_container_width=True, key="sb_nav_2"):
        if st.session_state.step1_approved:
            set_spinner_msg("Đang mở Bước 2: Làm Sạch...")
            st.session_state.current_step = 2
            st.rerun()
        else:
            st.toast("Vui lòng nạp file và Duyệt Bước 1 trước.", icon="⚠️")

    if st.button("03  Báo cáo & Dashboard", use_container_width=True, key="sb_nav_3"):
        if st.session_state.step2_approved:
            set_spinner_msg("Đang mở Bước 3: Tạo Báo Cáo...")
            st.session_state.current_step = 3
            st.rerun()
        else:
            st.toast("Vui lòng Duyệt Bước 2 trước.", icon="⚠️")

    if st.button("↺   Làm mới phiên", use_container_width=True, key="sb_reset_session"):
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
        set_spinner_msg("Đang làm mới toàn bộ phiên làm việc...")
        st.rerun()

    st.divider()

    st.markdown("<div style='color:#64748b; font-size:0.75rem; font-weight:600; text-transform:uppercase; letter-spacing:0.06em; padding:0 0.5rem; margin-bottom:0.4rem;'>Mô hình phân tích</div>", unsafe_allow_html=True)
    ai_model_options = {
        "gemini-2.5-pro": "Gemini 2.5 Pro",
        "gemini-2.5-flash": "Gemini 2.5 Flash",
        "gemini-2.0-flash": "Gemini 2.0 Flash",
        "gemini-1.5-pro": "Gemini 1.5 Pro"
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
    st.caption(f"Đang kích hoạt: **{ai_model_options[st.session_state.selected_ai_model]}**")

    with st.expander("Cài đặt API Key", expanded=False):
        api_key_input = st.text_input(
            "Gemini API Key",
            type="password",
            value=DEFAULT_GEMINI_API_KEY,
            help="Đã tích hợp sẵn API Key tự động"
        )
        if st.button("Cập nhật API Key", use_container_width=True):
            if api_key_input:
                try:
                    success, msg = orch.initialize_ai(api_key_input, model_name=st.session_state.selected_ai_model)
                except TypeError:
                    success, msg = orch.initialize_ai(api_key_input)
                if success:
                    st.session_state.api_key_set = True
                    st.success(f"Kết nối thành công ({st.session_state.selected_ai_model}).")
                else:
                    st.error(msg)

    if chosen_model != st.session_state.selected_ai_model:
        with st.spinner(f"Đang chuyển đổi sang mô hình {ai_model_options[chosen_model]}..."):
            st.session_state.selected_ai_model = chosen_model
            try:
                orch.initialize_ai(api_key_input or DEFAULT_GEMINI_API_KEY, model_name=chosen_model)
            except TypeError:
                orch.initialize_ai(api_key_input or DEFAULT_GEMINI_API_KEY)
            st.toast(f"Đã chuyển sang {ai_model_options[chosen_model]}")
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
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap" rel="stylesheet">
    <style>
        body { 
            font-family: 'Inter', 'Plus Jakarta Sans', -apple-system, sans-serif; 
            margin: 0;
            background-color: #F4F7FB;
            color: #0F172A;
            -webkit-font-smoothing: antialiased;
        }
        .tabular {
            font-variant-numeric: tabular-nums;
        }
        .surface-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.03);
            transition: border-color 0.15s ease, box-shadow 0.15s ease, transform 0.15s ease;
        }
        .surface-card:hover {
            border-color: #93C5FD;
            box-shadow: 0 8px 24px -4px rgba(15, 23, 42, 0.07);
            transform: translateY(-1px);
        }
        .grid-bg {
            background-size: 32px 32px;
            background-image: 
                linear-gradient(to right, rgba(226, 232, 240, 0.5) 1px, transparent 1px),
                linear-gradient(to bottom, rgba(226, 232, 240, 0.5) 1px, transparent 1px);
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
    </script>
</head>
<body class="h-screen max-h-[660px] flex flex-col justify-between relative overflow-hidden grid-bg">

    <!-- 1. TOP BAR (QUIET CHROME) -->
    <header class="relative z-10 px-8 py-4 flex justify-between items-center bg-white/90 backdrop-blur-sm border-b border-slate-200/80">
        <div class="flex items-center gap-2.5">
            <div class="w-7 h-7 rounded-md bg-blue-600 text-white flex items-center justify-center font-bold text-xs tracking-tight">
                DA
            </div>
            <span class="font-bold text-slate-900 text-sm tracking-tight">Hệ thống Phân tích &amp; Kiểm toán Dữ liệu</span>
        </div>
        
        <nav class="hidden md:flex items-center gap-1 bg-slate-100/90 p-1 rounded-lg border border-slate-200/70 text-xs font-medium text-slate-600">
            <a href="javascript:void(0)" class="bg-white text-slate-900 font-semibold px-3 py-1.5 rounded-md shadow-sm border border-slate-200/60">01 · Tổng quan</a>
            <a href="javascript:void(0)" onclick="triggerStart()" class="px-3 py-1.5 hover:text-slate-900 rounded-md transition">02 · Nhập bảng tính</a>
            <a href="javascript:void(0)" onclick="triggerStart()" class="px-3 py-1.5 hover:text-slate-900 rounded-md transition">03 · Kiểm duyệt lỗi</a>
            <a href="javascript:void(0)" onclick="triggerStart()" class="px-3 py-1.5 hover:text-slate-900 rounded-md transition">04 · Báo cáo &amp; Dashboard</a>
        </nav>

        <div class="flex items-center gap-2 text-xs font-medium text-slate-600 bg-slate-50 px-3 py-1.5 rounded-md border border-slate-200">
            <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
            <span>CSV · Excel · Google Sheet</span>
        </div>
    </header>

    <!-- 2. MAIN WORKSPACE HERO (2 COLUMNS: EDITORIAL COPY + RICH PRODUCT PREVIEW) -->
    <main class="relative z-10 flex-1 max-w-7xl w-full mx-auto flex flex-col md:flex-row items-center justify-between px-8 py-6 gap-10">
        
        <!-- LEFT COLUMN: TYPOGRAPHIC HIERARCHY & ACTION -->
        <div class="w-full md:w-[46%] flex flex-col items-start gap-5">
            <div class="inline-flex items-center gap-2 text-xs font-semibold text-blue-700 bg-blue-50 px-3 py-1 rounded-md border border-blue-200">
                <span>HUMAN-IN-THE-LOOP DATA WORKSPACE</span>
            </div>

            <h1 class="text-4xl lg:text-[2.65rem] font-extrabold text-slate-900 leading-[1.15] tracking-tight" style="font-family: 'Plus Jakarta Sans', sans-serif;">
                Kiểm duyệt dữ liệu.<br>
                Tổng hợp báo cáo tức thì.
            </h1>

            <p class="text-sm text-slate-600 leading-relaxed max-w-md">
                Tự động phát hiện dòng trống, bản ghi trùng lặp, giá trị khuyết và sai lệch định dạng từ tệp CSV, Excel hoặc Google Sheet. Mọi thao tác làm sạch đều được báo cáo minh bạch và chờ bạn phê duyệt trước khi thực thi.
            </p>

            <div class="flex items-center gap-3 pt-1">
                <button onclick="triggerStart()" class="bg-blue-600 hover:bg-blue-700 text-white font-semibold text-sm px-6 py-2.5 rounded-lg shadow-sm border border-blue-700 flex items-center gap-2 transition cursor-pointer">
                    <span>Bắt đầu làm việc</span>
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"/></svg>
                </button>
                <button onclick="triggerStart()" class="bg-white hover:bg-slate-50 text-slate-700 font-medium text-sm px-4 py-2.5 rounded-lg border border-slate-300 transition cursor-pointer">
                    Nạp tệp dữ liệu
                </button>
            </div>

            <!-- KEY METRICS STRIP (TABULAR NUMS) -->
            <div class="grid grid-cols-3 gap-6 pt-4 border-t border-slate-200/90 w-full max-w-md tabular">
                <div>
                    <div class="text-lg font-bold text-slate-900">100.0%</div>
                    <div class="text-xs text-slate-500">Kiểm soát phê duyệt</div>
                </div>
                <div>
                    <div class="text-lg font-bold text-slate-900">6 lớp</div>
                    <div class="text-xs text-slate-500">Quét lỗi tự động</div>
                </div>
                <div>
                    <div class="text-lg font-bold text-slate-900">4 định dạng</div>
                    <div class="text-xs text-slate-500">HTML · DOCX · PDF · CSV</div>
                </div>
            </div>
        </div>

        <!-- RIGHT COLUMN: RICH PRODUCT CONSOLE & 3-STEP PIPELINE -->
        <div class="w-full md:w-[54%] flex flex-col gap-3.5">
            
            <!-- LIVE PIPELINE PREVIEW CONSOLE -->
            <div onclick="triggerStart()" class="surface-card p-5 cursor-pointer">
                <div class="flex items-center justify-between pb-3 mb-3 border-b border-slate-100">
                    <div class="flex items-center gap-2">
                        <span class="text-xs font-semibold text-slate-900">Trình kiểm toán &amp; Chấm điểm Đa tiêu chí</span>
                        <span class="text-[11px] font-medium text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded">Sẵn sàng</span>
                    </div>
                    <span class="text-xs text-slate-400 tabular">Quy trình 3 bước</span>
                </div>
                <div class="grid grid-cols-3 gap-3 tabular">
                    <div class="bg-slate-50 p-3 rounded-lg border border-slate-200/70">
                        <div class="text-[11px] font-medium text-slate-500">Độ đầy đủ dữ liệu</div>
                        <div class="text-base font-bold text-slate-900 mt-0.5">99.4%</div>
                        <div class="text-[11px] text-blue-600 mt-0.5">Tự động phát hiện NaN</div>
                    </div>
                    <div class="bg-slate-50 p-3 rounded-lg border border-slate-200/70">
                        <div class="text-[11px] font-medium text-slate-500">Kiểm soát trùng lặp</div>
                        <div class="text-base font-bold text-slate-900 mt-0.5">0 bản ghi</div>
                        <div class="text-[11px] text-emerald-600 mt-0.5">Duyệt xóa theo yêu cầu</div>
                    </div>
                    <div class="bg-slate-50 p-3 rounded-lg border border-slate-200/70">
                        <div class="text-[11px] font-medium text-slate-500">Chấm điểm trọng số</div>
                        <div class="text-base font-bold text-slate-900 mt-0.5">5 tiêu chí</div>
                        <div class="text-[11px] text-slate-600 mt-0.5">Xếp hạng &amp; Dashboard</div>
                    </div>
                </div>
            </div>

            <!-- 3 WORKFLOW STEP CARDS (ALIGNED GRID) -->
            <div class="grid grid-cols-3 gap-3.5">
                <div onclick="triggerStart()" class="surface-card p-4 cursor-pointer flex flex-col justify-between">
                    <div>
                        <div class="flex items-center justify-between mb-2.5">
                            <span class="text-xs font-bold text-blue-600 bg-blue-50 border border-blue-200 px-2 py-0.5 rounded tabular">BƯỚC 01</span>
                        </div>
                        <h3 class="text-sm font-bold text-slate-900 mb-1">Nhập dữ liệu</h3>
                        <p class="text-xs text-slate-500 leading-relaxed">Tải tệp CSV, Excel hoặc liên kết Google Sheet công khai.</p>
                    </div>
                    <div class="mt-3 pt-2.5 border-t border-slate-100 flex items-center justify-between text-[11px] font-semibold text-blue-600">
                        <span>Mở Bước 1</span>
                        <span>→</span>
                    </div>
                </div>

                <div onclick="triggerStart()" class="surface-card p-4 cursor-pointer flex flex-col justify-between border-blue-200">
                    <div>
                        <div class="flex items-center justify-between mb-2.5">
                            <span class="text-xs font-bold text-white bg-blue-600 px-2 py-0.5 rounded tabular">BƯỚC 02</span>
                        </div>
                        <h3 class="text-sm font-bold text-slate-900 mb-1">Làm sạch &amp; Duyệt</h3>
                        <p class="text-xs text-slate-500 leading-relaxed">Thông báo lỗi chi tiết, tùy chọn khắc phục và chỉnh sửa trực tiếp.</p>
                    </div>
                    <div class="mt-3 pt-2.5 border-t border-slate-100 flex items-center justify-between text-[11px] font-semibold text-blue-600">
                        <span>Kiểm tra lỗi</span>
                        <span>→</span>
                    </div>
                </div>

                <div onclick="triggerStart()" class="surface-card p-4 cursor-pointer flex flex-col justify-between">
                    <div>
                        <div class="flex items-center justify-between mb-2.5">
                            <span class="text-xs font-bold text-slate-700 bg-slate-100 border border-slate-200 px-2 py-0.5 rounded tabular">BƯỚC 03</span>
                        </div>
                        <h3 class="text-sm font-bold text-slate-900 mb-1">Tạo báo cáo</h3>
                        <p class="text-xs text-slate-500 leading-relaxed">Dashboard xếp hạng đa chiều và xuất báo cáo HTML, Word, PDF.</p>
                    </div>
                    <div class="mt-3 pt-2.5 border-t border-slate-100 flex items-center justify-between text-[11px] font-semibold text-blue-600">
                        <span>Xem báo cáo</span>
                        <span>→</span>
                    </div>
                </div>
            </div>

        </div>
    </main>

    <!-- 3. FOOTER (CLEAN STATUS BAR) -->
    <footer class="relative z-10 w-full bg-white/90 border-t border-slate-200/80 text-slate-500 px-8 py-2.5 text-xs flex justify-between items-center">
        <span>Quy trình phân tích chuẩn hóa 3 bước · Mọi chỉnh sửa dữ liệu đều do người dùng kiểm duyệt</span>
        <span class="tabular font-medium text-slate-700">Phiên bản 2.5 Enterprise</span>
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
                st.markdown("""
                <div style="margin-bottom:0.5rem;">
                    <div style="background:#eff6ff; border:1px solid #bfdbfe; border-left:4px solid #2563eb; padding:0.45rem 1rem; border-radius:8px; display:inline-flex; align-items:center; gap:8px;">
                        <span style="font-weight:800; color:#1e3a8a; font-size:1.25rem; letter-spacing:-0.02em;">
                            BƯỚC 1: NHẬP &amp; KIỂM TRA DỮ LIỆU
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with col_s1_h2:
                btn_lbl = "Đóng khung nạp thêm" if st.session_state.show_step1_uploader else "+ Nạp thêm tệp dữ liệu"
                if st.button(btn_lbl, use_container_width=True, key="btn_toggle_s1_uploader"):
                    st.session_state.show_step1_uploader = not st.session_state.show_step1_uploader
                    st.rerun()
        else:
            st.markdown("""
            <div style="margin-bottom:1rem;">
                <div style="background:#eff6ff; border:1px solid #bfdbfe; border-left:4px solid #2563eb; padding:0.55rem 1.15rem; border-radius:8px; display:inline-flex; align-items:center; gap:10px; margin-bottom:6px;">
                    <span style="font-weight:800; color:#1e3a8a; font-size:1.45rem; letter-spacing:-0.02em;">
                        BƯỚC 1: NHẬP DỮ LIỆU
                    </span>
                </div>
                <div style="font-size:0.92rem; color:#475569; margin-top:2px; font-weight:500;">
                    Tải lên tệp CSV / Excel hoặc dán đường dẫn Google Sheet công khai để hệ thống kiểm tra cấu trúc và phát hiện lỗi.
                </div>
            </div>
            """, unsafe_allow_html=True)

        if (not has_loaded_files) or st.session_state.show_step1_uploader:
            col_up1, col_divider, col_up2 = st.columns([1, 0.12, 1])
    
            with col_up1:
                with st.container(key="zone_upload_left"):
                    st.markdown("""
                    <div style="display:flex; align-items:center; gap:8px; margin-bottom:8px; font-weight:700; color:#2563eb; font-size:1.05rem; letter-spacing:-0.01em;">
                        <span>Tải tệp</span>
                    </div>
                    <div class="gsheet-hint-text" style="font-family:'Plus Jakarta Sans',sans-serif; font-size:0.92rem; font-weight:600; color:#0f172a; margin-bottom:10px; line-height:1.4;">
                        Kéo thả tệp CSV, Excel vào đây hoặc Nhấn để tải lên
                    </div>
                    """, unsafe_allow_html=True)
                    with st.container(key="step1_file_inner_box"):
                        uploaded_files = st.file_uploader(
                            "Chọn file CSV, Excel...",
                            type=["csv", "xlsx", "xls"],
                            accept_multiple_files=True,
                            label_visibility="collapsed",
                            key="s1_file_uploader"
                        )
                    if uploaded_files:
                        if st.button("Nạp tệp đã chọn ➔", type="primary", use_container_width=True, key="btn_verify_upload"):
                            with st.spinner("Đang đọc và kiểm tra chất lượng dữ liệu..."):
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
                    <div style="width:1px; height:44px; background:#e2e8f0;"></div>
                    <div style="background:#f8fafc; color:#475569; font-weight:600; font-size:0.72rem; padding:3px 8px; border-radius:6px; border:1px solid #cbd5e1; margin:6px 0; text-transform:uppercase; letter-spacing:0.04em;">HOẶC</div>
                    <div style="width:1px; height:44px; background:#e2e8f0;"></div>
                </div>
                """, unsafe_allow_html=True)

            with col_up2:
                with st.container(key="zone_gsheet_right"):
                    st.markdown("""
                    <div style="display:flex; align-items:center; gap:8px; margin-bottom:8px; font-weight:700; color:#2563eb; font-size:1.05rem; letter-spacing:-0.01em;">
                        <span>Đường dẫn Google Sheet</span>
                    </div>
                    <div class="gsheet-hint-text" style="font-family:'Plus Jakarta Sans',sans-serif; font-size:0.92rem; font-weight:600; color:#0f172a; margin-bottom:10px; line-height:1.4;">
                        Đảm bảo liên kết đang ở chế độ xem công khai.
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
                            with st.spinner("Đang kết nối và kiểm tra Google Sheet..."):
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
        # BỐI CẢNH DOANH NGHIỆP
        # ============================================================
        with st.container(key="zone_biz_context"):
            col_b_head, col_b_btn = st.columns([2.4, 1.6])
            with col_b_head:
                st.markdown("""
                <div style="background:#f0fdf4; border:1px solid #bbf7d0; border-left:4px solid #16a34a; padding:0.55rem 1.15rem; border-radius:8px; display:inline-flex; align-items:center; gap:10px; margin-bottom:6px;">
                    <span style="font-weight:800; color:#14532d; font-size:1.45rem; letter-spacing:-0.02em;">
                        BỐI CẢNH DOANH NGHIỆP
                    </span>
                </div>
                <div style="font-size:0.92rem; color:#475569; margin-top:2px; margin-bottom:12px; font-weight:500;">
                    Mô tả ngắn gọn về mô hình kinh doanh và mục tiêu phân tích để hệ thống chấm điểm sát thực tế.
                </div>
                """, unsafe_allow_html=True)
            with col_b_btn:
                if st.button("AI gợi ý bối cảnh & câu hỏi theo tệp đã nạp", key="btn_ai_suggest_ctx", use_container_width=True):
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
                        st.session_state["_ai_ctx_done_msg"] = f"Đã gợi ý bối cảnh & câu hỏi dựa trên tệp `{first_fname}`."
                        st.rerun()
                    else:
                        st.warning("Bạn chưa nạp tệp dữ liệu nào. Vui lòng tải tệp CSV/Excel hoặc dán link Google Sheet ở khung phía trên trước.")

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
            # Tính điểm sức khỏe dữ liệu tổng thể (Data Health Scorecard)
            all_dfs_list = list(orch.data_agent.raw_dataframes.values())
            avg_health = round(sum(compute_data_health_metrics(d)["health_score"] for d in all_dfs_list) / max(1, len(all_dfs_list)), 1)
            with st.container(key="zone_step1_summary"):
                sum_c1, sum_c2, sum_c3, sum_c4, sum_c5 = st.columns([0.8, 1.1, 0.9, 1.0, 2.0])
                sum_c1.metric("Số tệp đã nạp", len(orch.data_agent.raw_dataframes))
                sum_c2.metric("Tổng số bản ghi", f"{sum(len(df) for df in orch.data_agent.raw_dataframes.values()):,}")
                sum_c3.metric("Nhóm phân tích", len(detected_groups))
                sum_c4.metric("Chất lượng dữ liệu", f"{avg_health}%")
                with sum_c5:
                    st.markdown(f"<div style='margin-top:0.35rem; font-size:0.88rem; color:#334155;'><b>Nhóm phát hiện:</b> {_format_groups_preview(detected_groups, 3)}</div>", unsafe_allow_html=True)
            with st.container(key="floating_approve_step1"):
                if st.button("Duyệt & Sang Bước 2 ➔", type="primary", use_container_width=True, key="btn_approve_step1"):
                    set_spinner_msg("Đang chuyển sang Bước 2: Làm sạch & Kiểm duyệt...")
                    st.session_state.step1_approved = True
                    st.session_state.current_step = 2
                    st.rerun()

        if st.session_state.file_messages:
            if "step1_ai_summaries" not in st.session_state:
                st.session_state.step1_ai_summaries = {}
            st.markdown(f"#### Báo cáo kiểm toán & Phê duyệt xử lý lỗi ({len(st.session_state.file_messages)} tệp)")
            with st.container():
                for item in st.session_state.file_messages[-6:]:
                    if item["success"]:
                        df_chk = orch.data_agent.raw_dataframes.get(item["file"])
                        if df_chk is not None and not df_chk.empty:
                            health_info = compute_data_health_metrics(df_chk)
                            detected_issues = detect_data_issues(df_chk, item["file"])
                            f_info_item = orch.data_agent.file_infos.get(item["file"], {})
                            has_backup = "original_df" in f_info_item and f_info_item["original_df"] is not None
                            user_logs_s1 = f_info_item.get("user_action_log", [])

                            if detected_issues:
                                st.warning(
                                    f"**Phát hiện {len(detected_issues)} loại lỗi trong tệp `{item['file']}`** "
                                    f"(Điểm chất lượng hiện tại: **{health_info['health_score']}%** · Độ đầy đủ: **{health_info['completeness_pct']}%**). "
                                    f"Vui lòng tích chọn các hạng mục bạn cho phép hệ thống sửa và bấm **Duyệt & Sửa ngay**:"
                                )
                                
                                issue_key_prefix = f"s1_fix_{item['file']}"
                                if f"{issue_key_prefix}_selected" not in st.session_state:
                                    st.session_state[f"{issue_key_prefix}_selected"] = [iss["id"] for iss in detected_issues]
                                    
                                cols_iss = st.columns(min(len(detected_issues), 3))
                                for idx_iss, iss in enumerate(detected_issues):
                                    with cols_iss[idx_iss % min(len(detected_issues), 3)]:
                                        with st.container(border=True):
                                            sev_bg = "#fef2f2" if iss["severity"] == "Quan trọng" else ("#fffbeb" if iss["severity"] == "Cảnh báo" else "#f8fafc")
                                            sev_fg = "#dc2626" if iss["severity"] == "Quan trọng" else ("#d97706" if iss["severity"] == "Cảnh báo" else "#475569")
                                            sev_bd = "#fecaca" if iss["severity"] == "Quan trọng" else ("#fde68a" if iss["severity"] == "Cảnh báo" else "#e2e8f0")
                                            st.markdown(
                                                f"<div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;'>"
                                                f"<span style='font-weight:700; color:#0f172a; font-size:0.9rem;'>{iss['type']}</span>"
                                                f"<span style='background:{sev_bg}; color:{sev_fg}; border:1px solid {sev_bd}; font-size:0.7rem; font-weight:700; padding:1px 7px; border-radius:4px; text-transform:uppercase;'>{iss['severity']}</span>"
                                                f"</div>",
                                                unsafe_allow_html=True
                                            )
                                            st.markdown(f"<div style='font-size:0.84rem; color:#475569; margin-bottom:6px;'>{iss['desc']}</div>", unsafe_allow_html=True)
                                            st.markdown(f"<div style='font-size:0.82rem; color:#0369a1; background:#f0f9ff; padding:6px 8px; border-radius:6px; margin-bottom:8px;'><b>Đề xuất xử lý:</b> {iss['suggested_fix']}</div>", unsafe_allow_html=True)
                                            is_chk = st.checkbox(
                                                f"Cho phép: {iss['action_label']}",
                                                value=(iss["id"] in st.session_state[f"{issue_key_prefix}_selected"]),
                                                key=f"chk_s1_{item['file']}_{iss['id']}"
                                            )
                                            if is_chk and iss["id"] not in st.session_state[f"{issue_key_prefix}_selected"]:
                                                st.session_state[f"{issue_key_prefix}_selected"].append(iss["id"])
                                            elif not is_chk and iss["id"] in st.session_state[f"{issue_key_prefix}_selected"]:
                                                st.session_state[f"{issue_key_prefix}_selected"].remove(iss["id"])
                                
                                col_btn_fix, col_btn_all, col_btn_undo = st.columns([1.8, 1.1, 1.1])
                                with col_btn_fix:
                                    chosen_fixes = st.session_state.get(f"{issue_key_prefix}_selected", [])
                                    btn_fix_label = f"Duyệt & Sửa ngay ({len(chosen_fixes)} mục đã chọn)" if chosen_fixes else "Chưa chọn mục nào để sửa"
                                    if st.button(btn_fix_label, type="primary", use_container_width=True, key=f"btn_apply_fixes_{item['file']}", disabled=(not chosen_fixes)):
                                        with st.spinner(f"Đang thực thi các mục sửa lỗi đã được bạn phê duyệt trên {item['file']}..."):
                                            fixed_df, fix_reports = apply_data_issue_fixes(df_chk, chosen_fixes)
                                            orch.data_agent.raw_dataframes[item["file"]] = fixed_df
                                            
                                            from utils.column_mapper import map_columns
                                            from utils.file_handler import _auto_aggregate
                                            orch.data_agent.column_mappings[item["file"]] = map_columns(list(fixed_df.columns))
                                            if len(fixed_df) > 1000:
                                                agg_df, agg_note = _auto_aggregate(fixed_df, item["file"])
                                                orch.data_agent.file_infos[item["file"]]["aggregated_df"] = agg_df
                                                orch.data_agent.file_infos[item["file"]]["aggregation_note"] = agg_note
                                            orch.data_agent.file_infos[item["file"]]["rows"] = len(fixed_df)
                                            orch.data_agent.file_infos[item["file"]]["missing_cells_count"] = int(fixed_df.isna().sum().sum())
                                            orch.data_agent.file_infos.setdefault(item["file"], {}).setdefault("user_action_log", []).extend(fix_reports)
                                            st.session_state[f"{issue_key_prefix}_selected"] = []
                                            st.toast(f"Đã sửa thành công {len(fix_reports)} hạng mục trên {item['file']}!")
                                        st.rerun()
                                with col_btn_all:
                                    all_ids_s1 = [iss["id"] for iss in detected_issues]
                                    if len(chosen_fixes) < len(all_ids_s1):
                                        if st.button("Chọn tất cả lỗi", use_container_width=True, key=f"btn_sel_all_s1_{item['file']}"):
                                            st.session_state[f"{issue_key_prefix}_selected"] = list(all_ids_s1)
                                            for iid in all_ids_s1:
                                                st.session_state[f"chk_s1_{item['file']}_{iid}"] = True
                                            st.rerun()
                                    else:
                                        if st.button("Bỏ chọn tất cả", use_container_width=True, key=f"btn_unsel_all_s1_{item['file']}"):
                                            st.session_state[f"{issue_key_prefix}_selected"] = []
                                            for iid in all_ids_s1:
                                                st.session_state[f"chk_s1_{item['file']}_{iid}"] = False
                                            st.rerun()
                                with col_btn_undo:
                                    if has_backup and user_logs_s1:
                                        if st.button("↺ Khôi phục bản gốc", use_container_width=True, key=f"btn_undo_s1_{item['file']}"):
                                            orig_copy = f_info_item["original_df"].copy()
                                            orch.data_agent.raw_dataframes[item["file"]] = orig_copy
                                            f_info_item["rows"] = len(orig_copy)
                                            f_info_item["user_action_log"] = []
                                            st.toast(f"Đã khôi phục tệp {item['file']} về trạng thái gốc ban đầu.")
                                            st.rerun()

                                # Tính năng xem trước các dòng có lỗi
                                err_preview_df = get_issue_preview_rows(df_chk, max_rows=25)
                                if not err_preview_df.empty:
                                    with st.expander(f"Xem trước các dòng đang chứa lỗi trong `{item['file']}` ({len(err_preview_df)} dòng mẫu)", expanded=False):
                                        st.dataframe(err_preview_df, use_container_width=True, height=220)
                            else:
                                st.success(
                                    f"**Tệp `{item['file']}` đạt chuẩn chất lượng 100% ({len(df_chk):,} dòng × {len(df_chk.columns)} cột):** "
                                    f"Không có ô trống, không có bản ghi trùng lặp và định dạng hoàn toàn hợp lệ."
                                )
                                if has_backup and user_logs_s1:
                                    with st.expander(f"Nhật ký các mục bạn đã duyệt sửa trên `{item['file']}` ({len(user_logs_s1)} thao tác)", expanded=False):
                                        for u_l in user_logs_s1:
                                            st.markdown(f"- ✓ {u_l}")
                                        if st.button("↺ Hoàn tác & Khôi phục dữ liệu gốc ban đầu", key=f"btn_undo_clean_s1_{item['file']}"):
                                            orig_copy = f_info_item["original_df"].copy()
                                            orch.data_agent.raw_dataframes[item["file"]] = orig_copy
                                            f_info_item["rows"] = len(orig_copy)
                                            f_info_item["user_action_log"] = []
                                            st.rerun()
                            
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
                                                f"Nêu rõ tệp đang gặp lỗi gì và gợi ý ngắn gọn cách xử lý."
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
                                        issues_parts.append("- **Đề xuất:** Tích chọn các mục sửa lỗi bên trên và bấm **Duyệt & Sửa ngay**, hoặc chỉnh sửa trực tiếp từng ô trong bảng bên dưới.")
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
                            st.info(f"**Nhận xét chuyên môn từ AI ({item['file']}):**\n\n{st.session_state.step1_ai_summaries[cache_key]}")
                    else:
                        st.error(f"**Lỗi đọc tệp '{item['file']}':** {item['msg']}\n\n*Hướng dẫn khắc phục: Kiểm tra xem tệp có đang mở hoặc bị khóa bởi phần mềm khác không, hoặc lưu lại tệp dưới định dạng chuẩn CSV (UTF-8) / Excel (.xlsx).*")

        if orch.data_agent.raw_dataframes:
            st.markdown("#### Bảng dữ liệu chi tiết & Chỉnh sửa trực tiếp tại Bước 1")
            with st.container():
                s1_file_list = list(orch.data_agent.raw_dataframes.keys())
                col_s1_sel, col_s1_info = st.columns([1.5, 2.5])
                with col_s1_sel:
                    s1_chosen_file = st.selectbox("Chọn tệp đang làm việc:", s1_file_list, key="s1_file_selector")
                with col_s1_info:
                    s1_df_cur = orch.data_agent.raw_dataframes[s1_chosen_file]
                    st.caption(f"Nhấp đúp vào ô bất kỳ để sửa trực tiếp ({len(s1_df_cur):,} dòng × {len(s1_df_cur.columns)} cột)")

                s1_view_df, display_cols, s1_is_filtered, s1_has_show_cols = _render_excel_filter_toolbar(
                    s1_df_cur, f"s1_{s1_chosen_file}"
                )

                if len(s1_view_df) > 1000:
                    s1_slice = s1_view_df[display_cols].iloc[:500]
                    s1_edited = st.data_editor(s1_slice, use_container_width=True, num_rows="dynamic", height=500, key=f"s1_editor_{s1_chosen_file}")
                else:
                    s1_slice = s1_view_df[display_cols]
                    s1_edited = st.data_editor(s1_slice, use_container_width=True, num_rows="dynamic", height=440, key=f"s1_editor_{s1_chosen_file}")

                col_s1_save, col_s1_apply_filter, _ = st.columns([1.3, 1.5, 2.2])
                with col_s1_save:
                    if st.button("Lưu chỉnh sửa bảng", type="primary", use_container_width=True, key="btn_save_step1"):
                        try:
                            with st.spinner("Đang lưu thay đổi..."):
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
                                orch.data_agent.file_infos.setdefault(s1_chosen_file, {}).setdefault("user_action_log", []).append(f"Đã sửa trực tiếp trên bảng tại Bước 1 ({len(new_df):,} dòng).")
                            st.rerun()
                        except Exception:
                            st.error("Không thể lưu thay đổi. Vui lòng kiểm tra định dạng dữ liệu vừa nhập.")
                with col_s1_apply_filter:
                    if s1_is_filtered:
                        if st.button("Chỉ giữ lại các dòng đang lọc", use_container_width=True, key="btn_keep_filtered_step1"):
                            orch.data_agent.raw_dataframes[s1_chosen_file] = s1_view_df.reset_index(drop=True)
                            st.toast(f"Đã lọc giữ lại {len(s1_view_df):,} dòng.")
                            st.rerun()

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
            if st.button("Quay lại Bước 1", type="primary"):
                st.session_state.current_step = 1
                st.rerun()
        else:
            file_list = list(orch.data_agent.raw_dataframes.keys())
            st.markdown("""
            <div style="margin-bottom:0.75rem;">
                <div style="background:#eff6ff; border:1px solid #bfdbfe; border-left:4px solid #2563eb; padding:0.45rem 1rem; border-radius:8px; display:inline-flex; align-items:center; gap:8px;">
                    <span style="font-weight:800; color:#1e3a8a; font-size:1.25rem; letter-spacing:-0.02em;">
                        BƯỚC 2: LÀM SẠCH &amp; KIỂM DUYỆT CHẤT LƯỢNG DỮ LIỆU
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            top_bar_c1, top_bar_c2, top_bar_c3 = st.columns([1.8, 2.4, 1.8])
            with top_bar_c1:
                selected_file = st.selectbox("Tệp đang kiểm duyệt:", file_list)
            df_current = orch.data_agent.raw_dataframes[selected_file]
            total_rows = len(df_current)
            file_info_cur = orch.data_agent.file_infos.get(selected_file, {})
            detected_groups = orch.data_agent.get_regions_detected()
            s2_health = compute_data_health_metrics(df_current)
            s2_issues = detect_data_issues(df_current, selected_file)

            with top_bar_c2:
                total_records = sum(len(df) for df in orch.data_agent.raw_dataframes.values())
                st.markdown(f"<div style='margin-top:0.35rem;'><b>{total_rows:,} dòng × {len(df_current.columns)} cột</b> · {len(detected_groups)} nhóm phân tích</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='font-size:0.86rem; color:#475569;'>Phân nhóm chính: {_format_groups_preview(detected_groups, 3)}</div>", unsafe_allow_html=True)

            with top_bar_c3:
                csv_clean_bytes = df_current.to_csv(index=False).encode("utf-8-sig")
                st.download_button(
                    label=f"Tải dữ liệu sạch ({selected_file}).csv",
                    data=csv_clean_bytes,
                    file_name=f"Cleaned_{selected_file}.csv",
                    mime="text/csv",
                    use_container_width=True,
                    key=f"dl_cleaned_csv_s2_{selected_file}"
                )

            # Bảng chỉ số chất lượng dữ liệu (Data Health Scorecard - Tabular Nums)
            hc1, hc2, hc3, hc4 = st.columns(4)
            hc1.metric("Điểm chất lượng tệp", f"{s2_health['health_score']}%")
            hc2.metric("Độ đầy đủ (Không trống)", f"{s2_health['completeness_pct']}%")
            hc3.metric("Tỷ lệ bản ghi duy nhất", f"{s2_health['unique_pct']}%")
            hc4.metric("Mục lỗi chờ duyệt", len(s2_issues))

            if total_records > 0:
                with st.container(key="floating_approve_step2"):
                    if st.button("Duyệt & Sang Bước 3 ➔", type="primary", use_container_width=True, key="btn_approve_step2"):
                        set_spinner_msg("Đang phân tích dữ liệu và tạo Báo cáo & Dashboard...")
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
            lbl_s2_btn = "Đóng bảng chỉnh sửa trực tiếp" if st.session_state.show_step2_editor else "Mở bảng chỉnh sửa từng ô dữ liệu"
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
                has_s2_backup = "original_df" in file_info_cur and file_info_cur["original_df"] is not None

                with st.container(key="zone_step2_audit_card"):
                    dup_rows_cnt = int(df_current.duplicated().sum())
                    null_by_col = df_current.isna().sum()
                    null_cols_detail = [f"`{col}` ({int(cnt)} ô)" for col, cnt in null_by_col.items() if cnt > 0]
                    txt_cols = [str(c) for c in df_current.select_dtypes(exclude=["number"]).columns]
                    num_cols_str = ", ".join(f"`{c}`" for c in num_cols[:8]) + (f" (+{len(num_cols)-8} cột)" if len(num_cols) > 8 else "")
                    txt_cols_str = ", ".join(f"`{c}`" for c in txt_cols[:6]) + (f" (+{len(txt_cols)-6} cột)" if len(txt_cols) > 6 else "")
                    mapped_str = ", ".join(f"`{k}`" for k in list(mapped_dict.keys())[:8]) + (f" (+{len(mapped_dict)-8})" if len(mapped_dict) > 8 else "")

                    if not s2_issues and not user_edits:
                        st.success(
                            f"**Tệp `{selected_file}` đã đạt chuẩn 100%!**\n\n"
                            f"- **Cấu trúc bảng:** Giữ nguyên toàn bộ **{total_rows:,} dòng × {len(df_current.columns)} cột**, không có dòng/cột trống thừa hay dòng trùng lặp.\n"
                            f"- **Độ đầy đủ dữ liệu:** 100% các ô đều có giá trị (0 ô trống).\n"
                            f"- **Các cột số đã chuẩn hóa ({len(num_cols)} cột):** {num_cols_str if num_cols else 'Không có'}.\n"
                            f"- **Các cột văn bản / phân loại ({len(txt_cols)} cột):** {txt_cols_str if txt_cols else 'Không có'}.\n"
                            f"- **Đã chuẩn hóa tên trường ({len(mapped_dict)} trường):** {mapped_str if mapped_dict else 'Tự động nhận diện'}."
                        )
                    else:
                        if s2_issues:
                            st.warning(f"**Phát hiện {len(s2_issues)} vấn đề trong tệp `{selected_file}`. Vui lòng chọn phương án xử lý và bấm phê duyệt:**")
                            s2_issue_key_prefix = f"s2_fix_{selected_file}"
                            if f"{s2_issue_key_prefix}_selected" not in st.session_state:
                                st.session_state[f"{s2_issue_key_prefix}_selected"] = [iss["id"] for iss in s2_issues]

                            cols_s2_iss = st.columns(min(len(s2_issues), 3))
                            for idx_s2i, s2_iss in enumerate(s2_issues):
                                with cols_s2_iss[idx_s2i % min(len(s2_issues), 3)]:
                                    with st.container(border=True):
                                        sev_bg = "#fef2f2" if s2_iss["severity"] == "Quan trọng" else ("#fffbeb" if s2_iss["severity"] == "Cảnh báo" else "#f8fafc")
                                        sev_fg = "#dc2626" if s2_iss["severity"] == "Quan trọng" else ("#d97706" if s2_iss["severity"] == "Cảnh báo" else "#475569")
                                        sev_bd = "#fecaca" if s2_iss["severity"] == "Quan trọng" else ("#fde68a" if s2_iss["severity"] == "Cảnh báo" else "#e2e8f0")
                                        st.markdown(
                                            f"<div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;'>"
                                            f"<span style='font-weight:700; color:#0f172a; font-size:0.9rem;'>{s2_iss['type']}</span>"
                                            f"<span style='background:{sev_bg}; color:{sev_fg}; border:1px solid {sev_bd}; font-size:0.7rem; font-weight:700; padding:1px 7px; border-radius:4px; text-transform:uppercase;'>{s2_iss['severity']}</span>"
                                            f"</div>",
                                            unsafe_allow_html=True
                                        )
                                        st.markdown(f"<div style='font-size:0.84rem; color:#475569; margin-bottom:6px;'>{s2_iss['desc']}</div>", unsafe_allow_html=True)
                                        st.markdown(f"<div style='font-size:0.82rem; color:#0369a1; background:#f0f9ff; padding:6px 8px; border-radius:6px; margin-bottom:8px;'><b>Đề xuất xử lý:</b> {s2_iss['suggested_fix']}</div>", unsafe_allow_html=True)
                                        is_checked = st.checkbox(
                                            f"Cho phép: {s2_iss['action_label']}",
                                            value=(s2_iss["id"] in st.session_state[f"{s2_issue_key_prefix}_selected"]),
                                            key=f"chk_s2_{selected_file}_{s2_iss['id']}"
                                        )
                                        if is_checked and s2_iss["id"] not in st.session_state[f"{s2_issue_key_prefix}_selected"]:
                                            st.session_state[f"{s2_issue_key_prefix}_selected"].append(s2_iss["id"])
                                        elif not is_checked and s2_iss["id"] in st.session_state[f"{s2_issue_key_prefix}_selected"]:
                                            st.session_state[f"{s2_issue_key_prefix}_selected"].remove(s2_iss["id"])

                            s2_chosen_fixes = st.session_state.get(f"{s2_issue_key_prefix}_selected", [])
                            col_s2_btn_apply, col_s2_btn_all, col_s2_btn_undo = st.columns([1.8, 1.1, 1.1])
                            with col_s2_btn_apply:
                                btn_s2_fix_label = f"Duyệt & Sửa ngay ({len(s2_chosen_fixes)} mục đã chọn)" if s2_chosen_fixes else "Chưa chọn mục nào để sửa"
                                if st.button(btn_s2_fix_label, type="primary", use_container_width=True, key=f"btn_apply_fixes_s2_{selected_file}", disabled=(not s2_chosen_fixes)):
                                    with st.spinner(f"Đang áp dụng các sửa đổi do bạn duyệt trên tệp {selected_file}..."):
                                        fixed_df, fix_reps = apply_data_issue_fixes(df_current, s2_chosen_fixes)
                                        orch.data_agent.raw_dataframes[selected_file] = fixed_df
                                        from utils.column_mapper import map_columns
                                        from utils.file_handler import _auto_aggregate
                                        orch.data_agent.column_mappings[selected_file] = map_columns(list(fixed_df.columns))
                                        if len(fixed_df) > 1000:
                                            agg_df, agg_note = _auto_aggregate(fixed_df, selected_file)
                                            orch.data_agent.file_infos[selected_file]["aggregated_df"] = agg_df
                                            orch.data_agent.file_infos[selected_file]["aggregation_note"] = agg_note
                                        orch.data_agent.file_infos[selected_file]["rows"] = len(fixed_df)
                                        orch.data_agent.file_infos[selected_file]["missing_cells_count"] = int(fixed_df.isna().sum().sum())
                                        orch.data_agent.file_infos.setdefault(selected_file, {}).setdefault("user_action_log", []).extend(fix_reps)
                                        st.session_state[f"{s2_issue_key_prefix}_selected"] = []
                                        st.toast(f"Đã xử lý xong các lỗi trên {selected_file}!")
                                    st.rerun()
                            with col_s2_btn_all:
                                all_s2_ids = [iss["id"] for iss in s2_issues]
                                if len(s2_chosen_fixes) < len(all_s2_ids):
                                    if st.button("Chọn tất cả lỗi", use_container_width=True, key=f"btn_sel_all_s2_{selected_file}"):
                                        st.session_state[f"{s2_issue_key_prefix}_selected"] = list(all_s2_ids)
                                        for iid in all_s2_ids:
                                            st.session_state[f"chk_s2_{selected_file}_{iid}"] = True
                                        st.rerun()
                                else:
                                    if st.button("Bỏ chọn tất cả", use_container_width=True, key=f"btn_unsel_all_s2_{selected_file}"):
                                        st.session_state[f"{s2_issue_key_prefix}_selected"] = []
                                        for iid in all_s2_ids:
                                            st.session_state[f"chk_s2_{selected_file}_{iid}"] = False
                                        st.rerun()
                            with col_s2_btn_undo:
                                if has_s2_backup and user_edits:
                                    if st.button("↺ Khôi phục bản gốc", use_container_width=True, key=f"btn_undo_s2_{selected_file}"):
                                        orig_copy = file_info_cur["original_df"].copy()
                                        orch.data_agent.raw_dataframes[selected_file] = orig_copy
                                        file_info_cur["rows"] = len(orig_copy)
                                        file_info_cur["user_action_log"] = []
                                        st.toast(f"Đã khôi phục tệp {selected_file} về dữ liệu gốc ban đầu.")
                                        st.rerun()

                            s2_err_preview = get_issue_preview_rows(df_current, max_rows=25)
                            if not s2_err_preview.empty:
                                with st.expander(f"Xem trước các dòng đang có lỗi trong `{selected_file}` ({len(s2_err_preview)} dòng mẫu)", expanded=False):
                                    st.dataframe(s2_err_preview, use_container_width=True, height=220)

                        details = [f"**Nhật ký kiểm toán & cấu trúc tệp `{selected_file}`:**"]
                        details.append(f"- **Quy mô hiện tại:** **{len(df_current):,} dòng × {len(df_current.columns)} cột**.")
                        details.append(f"- **Cột số ({len(num_cols)} cột):** {num_cols_str if num_cols else 'Không có'}.")
                        details.append(f"- **Cột phân loại / văn bản ({len(txt_cols)} cột):** {txt_cols_str if txt_cols else 'Không có'}.")
                        details.append(f"- **Ánh xạ trường ({len(mapped_dict)} trường):** {mapped_str if mapped_dict else 'Tự động nhận diện'}.")
                        for u_log in user_edits:
                            details.append(f"- **Đã phê duyệt & thực thi:** {u_log}")
                        st.info("\n".join(details))
                        if not s2_issues and has_s2_backup and user_edits:
                            if st.button("↺ Hoàn tác & Khôi phục dữ liệu gốc ban đầu", key=f"btn_undo_clean_s2_{selected_file}"):
                                orig_copy = file_info_cur["original_df"].copy()
                                orch.data_agent.raw_dataframes[selected_file] = orig_copy
                                file_info_cur["rows"] = len(orig_copy)
                                file_info_cur["user_action_log"] = []
                                st.rerun()

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
                        st.caption("Nhấp đúp vào ô bất kỳ để sửa trực tiếp, sau đó bấm nút **Lưu Dữ Liệu Đã Sửa** hoặc **Chuẩn Hóa Định Dạng** bên dưới:")
                        edited_slice = st.data_editor(
                            s2_view_df[s2_display_cols],
                            use_container_width=True,
                            num_rows="dynamic",
                            height=500,
                            key=f"editor_{selected_file}"
                        )

                    col_save, col_clean = st.columns([1, 1])
                    with col_save:
                        if st.button("Lưu Dữ Liệu Đã Sửa", type="primary", use_container_width=True, key="btn_save_step2"):
                            try:
                                with st.spinner("Đang lưu dữ liệu đã chỉnh sửa vào hệ thống..."):
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
                                    st.success(f"Đã lưu cập nhật thành công cho tệp {selected_file} ({len(new_df):,} dòng).")
                                set_spinner_msg(f"Đang cập nhật lại bảng dữ liệu {selected_file} sau khi lưu...")
                                st.rerun()
                            except Exception:
                                st.error("Đã xảy ra lỗi khi lưu dữ liệu chỉnh sửa. Vui lòng kiểm tra lại định dạng các ô vừa nhập.")
                    
                    with col_clean:
                        if st.button("Chuẩn Hóa Định Dạng Số & Chuỗi", type="primary", use_container_width=True, key="btn_clean_step2"):
                            try:
                                with st.spinner(f"Đang làm sạch và chuẩn hóa toàn bộ {len(df_current):,} dòng dữ liệu..."):
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
                                        f"Đã chạy Chuẩn hóa định dạng (xóa {removed_manual} dòng trống, chuẩn hóa định dạng số & khoảng trắng)."
                                    )
                                st.success(f"Đã chuẩn hóa tự động toàn bộ {len(cleaned_df):,} dòng.")
                                set_spinner_msg(f"Đang hiển thị bảng dữ liệu {selected_file} sau khi làm sạch...")
                                st.rerun()
                            except Exception:
                                st.error("Không thể chuẩn hóa tự động một số cột đặc biệt trong tệp này. Dữ liệu gốc vẫn được giữ nguyên an toàn.")

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
        from utils.export_helper import build_unified_report_dashboard_html, build_docx_bytes, build_pdf_bytes
        import streamlit.components.v1 as components

        # ============================================================
        # BÁO CÁO TỔNG HỢP & DASHBOARD TRỰC QUAN
        # ============================================================
        st.markdown("""
        <div style="margin-bottom:0.75rem;">
            <div style="background:#eff6ff; border:1px solid #bfdbfe; border-left:4px solid #2563eb; padding:0.45rem 1rem; border-radius:8px; display:inline-flex; align-items:center; gap:8px;">
                <span style="font-weight:800; color:#1e3a8a; font-size:1.25rem; letter-spacing:-0.02em;">
                    BƯỚC 3: BÁO CÁO TỔNG HỢP &amp; DASHBOARD ĐA CHIỀU
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        _msg_uni = st.session_state.pending_spinner_msg or "Đang tạo Báo cáo & Dashboard..."
        st.session_state.pending_spinner_msg = ""
        _total_rec = sum(len(df) for df in orch.data_agent.raw_dataframes.values())
        _uni_cache_key = (
            "v5_unslop_clean",
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
                try:
                    st.session_state._uni_docx_cached = build_docx_bytes(
                        title=st.session_state.dashboard_title,
                        df_scores=df_scores,
                        report_md=st.session_state.editable_report,
                        plan_md=st.session_state.editable_plan,
                        chart_keys=["bar", "radar", "grouped"],
                        mode="report"
                    )
                except Exception:
                    st.session_state._uni_docx_cached = None
                try:
                    st.session_state._uni_pdf_cached = build_pdf_bytes(
                        title=st.session_state.dashboard_title,
                        df_scores=df_scores,
                        report_md=st.session_state.editable_report,
                        plan_md=st.session_state.editable_plan,
                        chart_keys=["bar", "radar", "grouped"],
                        mode="report"
                    )
                except Exception:
                    st.session_state._uni_pdf_cached = None
                st.session_state._uni_export_key = _uni_cache_key

        unified_html = st.session_state._uni_html_cached

        # Thanh Xuất Báo Cáo Đa Định Dạng (HTML, Word, PDF, CSV)
        exp_c1, exp_c2, exp_c3, exp_c4 = st.columns(4)
        with exp_c1:
            st.download_button(
                label="Tải Báo cáo Web (.html)",
                data=unified_html.encode("utf-8"),
                file_name="Bao_Cao_Dashboard_Phan_Tich.html",
                mime="text/html",
                type="primary",
                use_container_width=True,
                key="dl_bar_html"
            )
        with exp_c2:
            if st.session_state.get("_uni_docx_cached"):
                st.download_button(
                    label="Tải Báo cáo Word (.docx)",
                    data=st.session_state._uni_docx_cached,
                    file_name="Bao_Cao_Phan_Tich.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                    key="dl_bar_docx"
                )
        with exp_c3:
            if st.session_state.get("_uni_pdf_cached"):
                st.download_button(
                    label="Tải Báo cáo In ấn (.pdf)",
                    data=st.session_state._uni_pdf_cached,
                    file_name="Bao_Cao_Phan_Tich.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    key="dl_bar_pdf"
                )
        with exp_c4:
            st.download_button(
                label="Tải Bảng điểm (.csv)",
                data=df_scores.to_csv(index=False).encode("utf-8-sig"),
                file_name="Bang_Xep_Hang_Diem.csv",
                mime="text/csv",
                use_container_width=True,
                key="dl_bar_csv"
            )

        with st.container(key="zone_step3_preview"):
            components.html(unified_html, height=840, scrolling=True)

        with st.container(key="floating_download_step3"):
            st.download_button(
                label="Tải xuống Báo Cáo (.html)",
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
            label_rep_btn = "Đóng khung sửa báo cáo" if st.session_state.show_edit_report else "Chỉnh sửa nội dung báo cáo & kế hoạch"
            if st.button(label_rep_btn, use_container_width=True, key="toggle_edit_report_btn"):
                st.session_state.show_edit_report = not st.session_state.show_edit_report
                st.rerun()

        with btn_ed_col2:
            label_dash_btn = "Đóng khung sửa bảng điểm" if st.session_state.show_edit_dashboard else "Chỉnh sửa điểm số trên Dashboard"
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

            if st.button("Lưu thay đổi báo cáo", type="primary", use_container_width=True):
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
                if st.button("Lưu điểm & cập nhật Dashboard", type="primary", use_container_width=True):
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
                    new_df["Trạng thái"] = ["Ưu tiên trọng tâm" if i < 2 else "Nhóm theo dõi" for i in range(len(new_df))]
                    st.session_state.dashboard_scores_df = new_df
                    st.session_state.show_edit_dashboard = False
                    st.rerun()

            with col_btn_dash2:
                if st.button("Phân tích lại bằng AI Agent", use_container_width=True):
                    with st.spinner("AI Agent đang phân tích sâu dữ liệu..."):
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

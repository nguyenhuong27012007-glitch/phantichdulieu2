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
# BỘ CÔNG CỤ KIỂM TOÁN & XỬ LÝ LỖI DỮ LIỆU TÍCH HỢP TRỰC TIẾP (ZERO IMPORT ERROR)
# ============================================================
def detect_data_issues(df: pd.DataFrame, filename: str = "Tệp dữ liệu") -> list:
    """Quét và phát hiện toàn diện các lỗi dữ liệu để thông báo và chờ người dùng phê duyệt sửa."""
    if df is None or df.empty:
        return []
    _cache_k = (filename, len(df), len(df.columns), int(df.isna().sum().sum()))
    _iss_cache = st.session_state.setdefault("_detect_issues_cache", {})
    if _cache_k in _iss_cache:
        return _iss_cache[_cache_k]
    issues = []

    # 1. Dòng hoàn toàn trống
    empty_rows = int(df.isna().all(axis=1).sum())
    if empty_rows > 0:
        issues.append({
            "id": "empty_rows",
            "type": "Dòng hoàn toàn trống",
            "severity": "Cảnh báo",
            "count": empty_rows,
            "desc": f"Có {empty_rows:,} dòng không có bất kỳ dữ liệu nào (toàn bộ ô đều trống).",
            "suggested_fix": f"Xóa bỏ {empty_rows:,} dòng trống này để tránh sai lệch tổng số bản ghi.",
            "action_label": f"Xóa {empty_rows:,} dòng trống"
        })

    # 2. Cột hoàn toàn trống
    empty_cols = int(df.isna().all(axis=0).sum())
    if empty_cols > 0:
        issues.append({
            "id": "empty_cols",
            "type": "Cột hoàn toàn trống",
            "severity": "Cảnh báo",
            "count": empty_cols,
            "desc": f"Có {empty_cols:,} cột không có bất kỳ giá trị nào.",
            "suggested_fix": f"Loại bỏ {empty_cols:,} cột trống để bảng dữ liệu gọn gàng.",
            "action_label": f"Loại bỏ {empty_cols:,} cột trống"
        })

    # 3. Bản ghi trùng lặp (Duplicates)
    dup_rows = int(df.duplicated().sum())
    if dup_rows > 0:
        issues.append({
            "id": "duplicate_rows",
            "type": "Dòng trùng lặp (Duplicates)",
            "severity": "Quan trọng",
            "count": dup_rows,
            "desc": f"Phát hiện {dup_rows:,} dòng trùng lặp 100% dữ liệu với các dòng khác trong tệp.",
            "suggested_fix": f"Loại bỏ {dup_rows:,} dòng trùng lặp, chỉ giữ lại bản ghi xuất hiện đầu tiên.",
            "action_label": f"Loại bỏ {dup_rows:,} dòng trùng"
        })

    # 4. Ô dữ liệu bị khuyết (Missing Values / NaN)
    null_counts = df.isna().sum()
    null_cols = [f"`{col}` ({int(cnt):,} ô)" for col, cnt in null_counts.items() if cnt > 0]
    total_null = int(null_counts.sum())
    if total_null > 0:
        col_list_str = ", ".join(null_cols[:4])
        if len(null_cols) > 4:
            col_list_str += f" (+{len(null_cols)-4} cột khác)"
        issues.append({
            "id": "missing_values",
            "type": "Ô dữ liệu bị khuyết (Trống/NaN)",
            "severity": "Quan trọng",
            "count": total_null,
            "desc": f"Có {total_null:,} ô bị trống rải rác ở các cột: {col_list_str}.",
            "suggested_fix": "Điền giá trị mặc định an toàn: Cột số điền 0, cột văn bản điền 'Chưa xác định'.",
            "action_label": f"Điền giá trị mặc định cho {total_null:,} ô trống"
        })

    # 5. Khoảng trắng thừa đầu/cuối (Leading/Trailing Spaces)
    obj_cols = [c for c in df.columns if df[c].dtype == "object" or pd.api.types.is_string_dtype(df[c])]
    space_issue_count = 0
    space_cols = []
    for c in obj_cols:
        s = df[c].dropna().astype(str)
        mask = s.str.startswith(" ") | s.str.endswith(" ") | s.str.contains("  ", regex=False)
        c_cnt = int(mask.sum())
        if c_cnt > 0:
            space_issue_count += c_cnt
            space_cols.append(f"`{c}` ({c_cnt:,} ô)")
    if space_issue_count > 0:
        col_space_str = ", ".join(space_cols[:4])
        issues.append({
            "id": "extra_whitespace",
            "type": "Khoảng trắng thừa (Đầu/cuối chữ)",
            "severity": "Nhẹ",
            "count": space_issue_count,
            "desc": f"Có {space_issue_count:,} ô văn bản bị thừa khoảng trắng tại: {col_space_str}.",
            "suggested_fix": "Cắt tỉa (Trim) khoảng trắng thừa đầu/cuối để dữ liệu văn bản đồng nhất.",
            "action_label": f"Cắt tỉa khoảng trắng ({space_issue_count:,} ô)"
        })

    # 6. Giá trị số âm bất thường
    neg_issue_count = 0
    neg_cols = []
    for c in df.select_dtypes(include=["number"]).columns:
        neg_mask = df[c].dropna() < 0
        if neg_mask.any():
            c_neg_cnt = int(neg_mask.sum())
            neg_issue_count += c_neg_cnt
            neg_cols.append(f"`{c}` ({c_neg_cnt:,} số âm)")
    if neg_issue_count > 0:
        col_neg_str = ", ".join(neg_cols[:3])
        issues.append({
            "id": "negative_values",
            "type": "Giá trị số âm bất thường",
            "severity": "Cảnh báo",
            "count": neg_issue_count,
            "desc": f"Phát hiện {neg_issue_count:,} giá trị số âm tại: {col_neg_str}.",
            "suggested_fix": "Chuyển các giá trị số âm thành số dương (Lấy giá trị tuyệt đối).",
            "action_label": f"Đổi số âm thành dương ({neg_issue_count:,} ô)"
        })

    _iss_cache[_cache_k] = issues
    return issues


def apply_data_issue_fixes(df: pd.DataFrame, selected_issue_ids: list, custom_instructions: dict = None):
    """Áp dụng các biện pháp sửa lỗi dữ liệu do người dùng lựa chọn, tùy chỉnh hướng sửa và phê duyệt."""
    if df is None or df.empty or not selected_issue_ids:
        return df, []
    df_fixed = df.copy()
    report = []
    instr_map = custom_instructions or {}

    if "empty_rows" in selected_issue_ids:
        before_r = len(df_fixed)
        df_fixed = df_fixed.dropna(how="all")
        diff_r = before_r - len(df_fixed)
        if diff_r > 0:
            report.append(f"Đã xóa {diff_r:,} dòng hoàn toàn trống.")

    if "empty_cols" in selected_issue_ids:
        before_c = len(df_fixed.columns)
        df_fixed = df_fixed.dropna(axis=1, how="all")
        diff_c = before_c - len(df_fixed.columns)
        if diff_c > 0:
            report.append(f"Đã loại bỏ {diff_c:,} cột hoàn toàn trống.")

    if "duplicate_rows" in selected_issue_ids:
        ins_dup = str(instr_map.get("duplicate_rows", "")).lower()
        keep_mode = "last" if ("cuối" in ins_dup or "last" in ins_dup) else "first"
        before_d = len(df_fixed)
        df_fixed = df_fixed.drop_duplicates(keep=keep_mode)
        diff_d = before_d - len(df_fixed)
        if diff_d > 0:
            keep_vn = "bản ghi cuối cùng" if keep_mode == "last" else "bản ghi đầu tiên"
            report.append(f"Đã loại bỏ {diff_d:,} dòng trùng lặp (giữ {keep_vn}).")

    if "extra_whitespace" in selected_issue_ids:
        ws_count = 0
        for col in df_fixed.columns:
            if df_fixed[col].dtype == "object" or pd.api.types.is_string_dtype(df_fixed[col]):
                df_fixed[col] = df_fixed[col].apply(lambda x: " ".join(str(x).split()) if pd.notna(x) else x)
                ws_count += 1
        if ws_count > 0:
            report.append(f"Đã cắt tỉa khoảng trắng thừa trên {ws_count} cột văn bản.")

    if "missing_values" in selected_issue_ids:
        ins_miss = str(instr_map.get("missing_values", "")).lower()
        if any(k in ins_miss for k in ["xóa", "xoá", "bỏ dòng", "drop"]):
            before_m = len(df_fixed)
            df_fixed = df_fixed.dropna()
            diff_m = before_m - len(df_fixed)
            report.append(f"Đã xóa {diff_m:,} dòng có ô bị khuyết theo hướng dẫn: '{instr_map.get('missing_values', '')}'.")
        else:
            use_mean = any(k in ins_miss for k in ["trung bình", "mean"])
            use_median = any(k in ins_miss for k in ["trung vị", "median"])
            filled_count = 0
            for col in df_fixed.columns:
                null_cnt = int(df_fixed[col].isna().sum())
                if null_cnt > 0:
                    filled_count += null_cnt
                    if pd.api.types.is_numeric_dtype(df_fixed[col]):
                        if use_mean:
                            fill_v = df_fixed[col].mean()
                            df_fixed[col] = df_fixed[col].fillna(0 if pd.isna(fill_v) else round(float(fill_v), 2))
                        elif use_median:
                            fill_v = df_fixed[col].median()
                            df_fixed[col] = df_fixed[col].fillna(0 if pd.isna(fill_v) else round(float(fill_v), 2))
                        else:
                            df_fixed[col] = df_fixed[col].fillna(0)
                    else:
                        df_fixed[col] = df_fixed[col].fillna("Chưa xác định")
            if filled_count > 0:
                mode_lbl = "trung bình" if use_mean else ("trung vị" if use_median else "mặc định (Số: 0, Chữ: 'Chưa xác định')")
                report.append(f"Đã điền giá trị {mode_lbl} cho {filled_count:,} ô bị khuyết.")

    if "negative_values" in selected_issue_ids:
        ins_neg = str(instr_map.get("negative_values", "")).lower()
        if any(k in ins_neg for k in ["xóa", "xoá", "loại bỏ", "drop"]):
            before_n = len(df_fixed)
            num_cols_n = df_fixed.select_dtypes(include=["number"]).columns
            if len(num_cols_n) > 0:
                neg_row_mask = (df_fixed[num_cols_n] < 0).any(axis=1)
                df_fixed = df_fixed[~neg_row_mask]
            diff_n = before_n - len(df_fixed)
            report.append(f"Đã xóa {diff_n:,} dòng chứa giá trị âm theo yêu cầu của bạn.")
        elif any(k in ins_neg for k in ["bằng 0", "thay 0", "về 0", "= 0", "số 0"]):
            neg_count = 0
            for col in df_fixed.select_dtypes(include=["number"]).columns:
                neg_mask = df_fixed[col] < 0
                if neg_mask.any():
                    neg_count += int(neg_mask.sum())
                    df_fixed.loc[neg_mask, col] = 0
            if neg_count > 0:
                report.append(f"Đã chuyển {neg_count:,} giá trị âm về 0 theo yêu cầu của bạn.")
        else:
            neg_count = 0
            for col in df_fixed.select_dtypes(include=["number"]).columns:
                neg_mask = df_fixed[col] < 0
                if neg_mask.any():
                    neg_count += int(neg_mask.sum())
                    df_fixed[col] = df_fixed[col].abs()
            if neg_count > 0:
                report.append(f"Đã chuyển {neg_count:,} giá trị âm sang số dương.")

    return df_fixed, report


def get_issue_preview_rows(df: pd.DataFrame, max_rows: int = 30) -> pd.DataFrame:
    """Trả về bảng xem trước các dòng có chứa lỗi dữ liệu để người dùng đối chiếu trước khi duyệt."""
    if df is None or df.empty:
        return pd.DataFrame()
    mask_null = df.isna().any(axis=1)
    mask_dup = df.duplicated(keep=False)
    mask_neg = pd.Series(False, index=df.index)
    for c in df.select_dtypes(include=["number"]).columns:
        mask_neg = mask_neg | (df[c] < 0).fillna(False)
    mask_ws = pd.Series(False, index=df.index)
    obj_cols = [c for c in df.columns if df[c].dtype == "object" or pd.api.types.is_string_dtype(df[c])]
    for c in obj_cols:
        s = df[c].fillna("").astype(str)
        mask_ws = mask_ws | s.str.startswith(" ") | s.str.endswith(" ") | s.str.contains(r"  +")
    combined_mask = mask_null | mask_dup | mask_neg | mask_ws
    return df[combined_mask].head(max_rows)


def compute_data_health_metrics(df: pd.DataFrame) -> dict:
    """Tính toán chỉ số sức khỏe dữ liệu (Data Health Score) chuẩn xác."""
    if df is None or df.empty:
        return {"health_score": 100.0, "completeness_pct": 100.0, "unique_pct": 100.0, "total_cells": 0, "null_cells": 0, "dup_rows": 0}
    total_cells = max(1, int(df.shape[0] * df.shape[1]))
    null_cells = int(df.isna().sum().sum())
    dup_rows = int(df.duplicated().sum())
    completeness_pct = round(100.0 * (total_cells - null_cells) / total_cells, 1)
    unique_pct = round(100.0 * (len(df) - dup_rows) / max(1, len(df)), 1)
    health_score = round(completeness_pct * 0.65 + unique_pct * 0.35, 1)
    return {
        "health_score": health_score,
        "completeness_pct": completeness_pct,
        "unique_pct": unique_pct,
        "total_cells": total_cells,
        "null_cells": null_cells,
        "dup_rows": dup_rows
    }

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

st.markdown("""
<style>
    /* Hiệu ứng phóng to mượt mà khi di chuột vào các ô, khung, thẻ và nút */
    .st-key-zone_upload_left,
    .st-key-zone_gsheet_right,
    .st-key-zone_biz_context,
    .st-key-zone_step2_audit_card,
    .st-key-zone_step2_workspace,
    .st-key-zone_step3_preview,
    .st-key-err_preview_card,
    .st-key-s2_err_preview_card,
    [data-testid="stMetric"],
    [data-testid="stAlert"],
    [data-testid="stExpander"] {
        transition: transform 0.22s cubic-bezier(0.22, 1, 0.36, 1), box-shadow 0.22s ease !important;
    }
    .st-key-zone_upload_left:hover,
    .st-key-zone_gsheet_right:hover,
    .st-key-zone_biz_context:hover,
    .st-key-zone_step2_audit_card:hover,
    .st-key-zone_step2_workspace:hover,
    .st-key-zone_step3_preview:hover,
    .st-key-err_preview_card:hover,
    .st-key-s2_err_preview_card:hover,
    [data-testid="stMetric"]:hover,
    [data-testid="stAlert"]:hover,
    [data-testid="stExpander"]:hover {
        transform: scale(1.04) translateY(-4px) !important;
        box-shadow: 0 20px 42px rgba(37, 99, 235, 0.18) !important;
        position: relative !important;
        z-index: 20 !important;
    }
    div.stButton > button,
    div.stDownloadButton > button {
        transition: transform 0.18s cubic-bezier(0.22, 1, 0.36, 1), box-shadow 0.18s ease !important;
    }
    div.stButton > button:hover,
    div.stDownloadButton > button:hover {
        transform: scale(1.06) translateY(-2px) !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# HIỆU ỨNG CHUYỂN TRANG RÕ NÉT (MÀN RÈM QUÉT + PHÓNG TO TRANG MỚI)
# ============================================================
_prev_step_anim = st.session_state.get("_last_rendered_step", st.session_state.current_step)
_cur_step_anim = st.session_state.current_step
if _cur_step_anim != _prev_step_anim:
    _is_forward = (_cur_step_anim > _prev_step_anim)
    _curtain_start = "100%" if _is_forward else "-100%"
    _curtain_end = "-100%" if _is_forward else "100%"
    st.markdown(f"""
    <style>
        @keyframes pageCurtainSweep {{
            0% {{
                transform: translateX({_curtain_start});
                opacity: 0.95;
            }}
            45% {{
                transform: translateX(0%);
                opacity: 0.92;
            }}
            100% {{
                transform: translateX({_curtain_end});
                opacity: 0;
            }}
        }}
        @keyframes pageZoomReveal {{
            0% {{
                opacity: 0;
                transform: scale(0.94) translateY(18px);
            }}
            100% {{
                opacity: 1;
                transform: scale(1) translateY(0);
            }}
        }}
        .hp-page-curtain {{
            position: fixed;
            inset: 0;
            z-index: 9999999;
            pointer-events: none;
            background: linear-gradient(135deg, #1d4ed8 0%, #3b82f6 50%, #dbeafe 100%);
            animation: pageCurtainSweep 0.85s cubic-bezier(0.77, 0, 0.175, 1) forwards;
        }}
        .main .block-container, [data-testid="stMainBlockContainer"] {{
            animation: pageZoomReveal 0.75s cubic-bezier(0.22, 1, 0.36, 1) forwards !important;
        }}
    </style>
    <div class="hp-page-curtain"></div>
    """, unsafe_allow_html=True)
st.session_state._last_rendered_step = _cur_step_anim

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

    /* Nền toàn trang web đồng bộ màu xanh pastel giống trang mở đầu (#F4F7FB) */
    html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {{
        background-color: #F4F7FB !important;
        background: radial-gradient(circle at 12% 10%, #dbeafe 0%, transparent 40%),
                    radial-gradient(circle at 88% 15%, #e0f2fe 0%, transparent 38%),
                    linear-gradient(180deg, #F4F7FB 0%, #edf3fa 50%, #e6eff9 100%) !important;
    }}
    header[data-testid="stHeader"] {{
        background: transparent !important;
    }}

    /* Hiệu ứng chuyển trang mượt mà */
    @keyframes pageTransitionIn {{
        0% {{ opacity: 0; transform: translateY(6px); }}
        100% {{ opacity: 1; transform: translateY(0); }}
    }}

    /* Khung chính — Nền xanh pastel mềm mượt không bị hộp trắng bao bọc */
    .main .block-container,
    [data-testid="stMainBlockContainer"] {{
        background: transparent !important;
        border: none !important;
        border-top: none !important;
        box-shadow: none !important;
        padding: 1.5rem 1.8rem 2.5rem 1.8rem !important;
        margin: 0 auto !important;
        max-width: 98% !important;
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

    /* Khung Viền Nét Đứt Xanh Dương Cho Ô Tải Tệp */
    .st-key-step1_file_inner_box {{
        border: 2px dashed #93c5fd !important;
        border-radius: 16px !important;
        min-height: 145px !important;
        padding: 1.5rem 1.2rem !important;
        background: #ffffff !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        gap: 8px !important;
    }}

    /* Vùng Upload Kéo Thả Trình Bày Y Hệt Khung Input Google Sheet */
    div[data-testid="stFileUploader"] section {{
        background: #ffffff !important;
        border: 1px solid rgba(203, 213, 225, 0.8) !important;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05) !important;
        border-radius: 10px !important;
        min-height: 44px !important;
        height: 44px !important;
        padding: 0 14px !important;
        text-align: left !important;
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        justify-content: flex-start !important;
        transition: all 0.25s ease !important;
        box-sizing: border-box !important;
    }}
    div[data-testid="stFileUploader"] section:hover {{
        border-color: #3b82f6 !important;
        background: #ffffff !important;
    }}
    div[data-testid="stFileUploader"] section::after {{
        content: "file CSV, Excel" !important;
        color: #94a3b8 !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 0.92rem !important;
        font-weight: 500 !important;
        pointer-events: none !important;
    }}
    div[data-testid="stFileUploader"] section [data-testid="stFileUploaderDropzoneInstructions"],
    div[data-testid="stFileUploader"] section [data-testid="stFileUploaderDropzoneInstructions"] * {{
        display: none !important;
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

    /* Thẻ Bối Cảnh Doanh Nghiệp Viền Trắ    .st-key-zone_biz_context {{
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

    /* Ẩn hoàn toàn văn bản phụ (200MB per file, bullet, v.v.) bên trong ô Upload */
    div[data-testid="stFileUploader"] small,
    div[data-testid="stFileUploader"] [data-testid="stFileUploaderDropzoneInstructions"] > div > small,
    div[data-testid="stFileUploader"] [data-testid="stFileUploaderDropzoneInstructions"] span:last-child {{
        display: none !important;
        font-size: 0 !important;
        visibility: hidden !important;
        opacity: 0 !important;
    }}
    /* Chữ 'Kéo thả tệp...' bên cột tải tệp đổi sang màu đen */
    div[data-testid="stFileUploader"] label p,
    div[data-testid="stFileUploader"] label span,
    div[data-testid="stFileUploader"] label,
    div[data-testid="stFileUploader"] [data-testid="stWidgetLabel"] p {{
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

    /* ============================================================
       HIỆU ỨNG CHUỘT & MÀU SẮC ĐỒNG BỘ TRANG MỞ ĐẦU (ALL PAGES)
       ============================================================ */
    .app-cursor-glow {{
        position: fixed;
        width: 380px;
        height: 380px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(59, 130, 246, 0.16) 0%, rgba(99, 102, 241, 0.07) 45%, transparent 70%);
        pointer-events: none;
        transform: translate(-50%, -50%);
        z-index: 99998;
        mix-blend-mode: multiply;
        transition: width 0.3s ease, height 0.3s ease, background 0.3s ease;
    }}
    .app-cursor-dot {{
        position: fixed;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #2563eb;
        box-shadow: 0 0 10px rgba(37, 99, 235, 0.6);
        pointer-events: none;
        transform: translate(-50%, -50%);
        z-index: 999999;
        transition: transform 0.12s ease-out, background-color 0.2s ease;
    }}

    /* Hiệu ứng di chuột vào vùng nào là vùng đó đậm màu & có chiều sâu */
    .st-key-zone_upload_left,
    .st-key-zone_gsheet_right,
    .st-key-zone_biz_context,
    .st-key-zone_step1_summary,
    .st-key-zone_step2_workspace,
    .st-key-zone_step3_preview,
    [data-testid="stVerticalBlockBorderWrapper"],
    div[data-testid="stMetric"],
    .st-key-top_wizard_bar {{
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }}
    .st-key-zone_upload_left:hover,
    .st-key-zone_gsheet_right:hover,
    .st-key-zone_biz_context:hover,
    .st-key-zone_step1_summary:hover,
    .st-key-zone_step2_workspace:hover,
    .st-key-zone_step3_preview:hover,
    [data-testid="stVerticalBlockBorderWrapper"]:hover {{
        background: #ffffff !important;
        box-shadow: 0 14px 34px rgba(30, 58, 138, 0.11) !important;
        border-color: rgba(59, 130, 246, 0.45) !important;
        transform: translateY(-2px) !important;
    }}
</style>
""", unsafe_allow_html=True)

# Injected mouse glow & cursor script for all pages
import streamlit.components.v1 as _cursor_comp
_cursor_comp.html("""
<style>
    .app-cursor-glow {
        position: fixed;
        width: 380px;
        height: 380px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(59, 130, 246, 0.16) 0%, rgba(99, 102, 241, 0.07) 45%, transparent 70%);
        pointer-events: none;
        transform: translate(-50%, -50%);
        z-index: 999998;
        mix-blend-mode: multiply;
        transition: width 0.3s ease, height 0.3s ease, background 0.3s ease;
    }
    .app-cursor-dot {
        position: fixed;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #2563eb;
        box-shadow: 0 0 10px rgba(37, 99, 235, 0.6);
        pointer-events: none;
        transform: translate(-50%, -50%);
        z-index: 999999;
        transition: transform 0.12s ease-out, background-color 0.2s ease;
    }
</style>
<div id="app-cursor-glow" class="app-cursor-glow"></div>
<div id="app-cursor-dot" class="app-cursor-dot"></div>
<script>
    (function() {
        const parentDoc = window.parent.document;
        let glow = parentDoc.getElementById('app-cursor-glow');
        let dot = parentDoc.getElementById('app-cursor-dot');
        
        if (!glow) {
            glow = document.createElement('div');
            glow.id = 'app-cursor-glow';
            glow.className = 'app-cursor-glow';
            parentDoc.body.appendChild(glow);
        }
        if (!dot) {
            dot = document.createElement('div');
            dot.id = 'app-cursor-dot';
            dot.className = 'app-cursor-dot';
            parentDoc.body.appendChild(dot);
        }

        let mX = -100, mY = -100, cX = -100, cY = -100;
        parentDoc.addEventListener('mousemove', function(e) {
            mX = e.clientX;
            mY = e.clientY;
            if (dot) {
                dot.style.left = mX + 'px';
                dot.style.top = mY + 'px';
            }
        });

        function renderGlow() {
            cX += (mX - cX) * 0.15;
            cY += (mY - cY) * 0.15;
            if (glow) {
                glow.style.left = cX + 'px';
                glow.style.top = cY + 'px';
            }
            requestAnimationFrame(renderGlow);
        }
        renderGlow();

        parentDoc.querySelectorAll('button, a, input, textarea, select, [data-testid="stMetric"], section').forEach(function(el) {
            el.addEventListener('mouseenter', function() {
                if (glow) {
                    glow.style.width = '480px';
                    glow.style.height = '480px';
                    glow.style.background = 'radial-gradient(circle, rgba(245, 158, 11, 0.22) 0%, rgba(59, 130, 246, 0.12) 45%, transparent 70%)';
                }
                if (dot) {
                    dot.style.transform = 'translate(-50%, -50%) scale(1.6)';
                    dot.style.backgroundColor = '#d97706';
                }
            });
            el.addEventListener('mouseleave', function() {
                if (glow) {
                    glow.style.width = '380px';
                    glow.style.height = '380px';
                    glow.style.background = 'radial-gradient(circle, rgba(59, 130, 246, 0.16) 0%, rgba(99, 102, 241, 0.07) 45%, transparent 70%)';
                }
                if (dot) {
                    dot.style.transform = 'translate(-50%, -50%) scale(1)';
                    dot.style.backgroundColor = '#2563eb';
                }
            });
        });
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
# THANH ĐIỀU HƯỚNG DOCK ICON DỌC NỔI TRONG KHUNG TRANG (BƯỚC 1, 2, 3)
# ============================================================
if st.session_state.current_step != 0:
    _sb_cur = st.session_state.current_step
    st.markdown("""
    <style>
        section[data-testid="stSidebar"] {
            display: none !important;
        }
        .main .block-container, [data-testid="stMainBlockContainer"] {
            padding-left: 96px !important;
        }
        .st-key-floating_left_dock {
            position: fixed !important;
            left: 18px !important;
            top: 86px !important;
            width: 58px !important;
            z-index: 99999 !important;
            background: rgba(255, 255, 255, 0.86) !important;
            backdrop-filter: blur(14px) !important;
            border: 1px solid rgba(255, 255, 255, 0.96) !important;
            border-radius: 999px !important;
            padding: 12px 8px !important;
            box-shadow: 0 12px 32px rgba(37, 99, 235, 0.14), 0 4px 12px rgba(15, 23, 42, 0.06) !important;
            transition: width 0.24s cubic-bezier(0.22, 1, 0.36, 1), border-radius 0.24s ease !important;
            overflow: hidden !important;
        }
        .st-key-floating_left_dock:hover {
            width: 215px !important;
            border-radius: 22px !important;
            padding: 12px 10px !important;
        }
        .st-key-floating_left_dock [data-testid="stVerticalBlock"] {
            gap: 6px !important;
            align-items: stretch !important;
        }
        .st-key-floating_left_dock button {
            width: 40px !important;
            height: 40px !important;
            min-height: 40px !important;
            padding: 0 !important;
            border-radius: 50% !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            font-size: 0.9rem !important;
            font-weight: 600 !important;
            white-space: nowrap !important;
            overflow: hidden !important;
            border: none !important;
            background: transparent !important;
            color: #475569 !important;
            box-shadow: none !important;
            transition: all 0.2s ease !important;
        }
        .st-key-floating_left_dock button p {
            font-size: 0 !important;
            line-height: 1 !important;
            margin: 0 !important;
        }
        .st-key-floating_left_dock button p::first-letter {
            font-size: 1.08rem !important;
        }
        .st-key-floating_left_dock:hover button {
            width: 100% !important;
            border-radius: 12px !important;
            justify-content: flex-start !important;
            padding: 0 12px !important;
        }
        .st-key-floating_left_dock:hover button p {
            font-size: 0.9rem !important;
        }
        .st-key-floating_left_dock button:hover {
            background: rgba(239, 246, 255, 0.95) !important;
            color: #1e3a8a !important;
        }
        .st-key-floating_left_dock button[kind="primary"] {
            background: #ffffff !important;
            color: #1e3a8a !important;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2), 0 1px 3px rgba(15, 23, 42, 0.08) !important;
        }
        .st-key-floating_left_dock button[kind="primary"] p {
            color: #1e3a8a !important;
        }
        .st-key-floating_left_dock hr {
            margin: 4px auto !important;
            width: 24px !important;
            border-color: #cbd5e1 !important;
            transition: width 0.2s ease !important;
        }
        .st-key-floating_left_dock:hover hr {
            width: 100% !important;
        }
    </style>
    """, unsafe_allow_html=True)

    with st.container(key="floating_left_dock"):
        if st.button("⊞   Tổng quan", type="primary" if _sb_cur == 0 else "secondary", key="sb_nav_0"):
            set_spinner_msg("⏳ Đang quay lại Trang Mở Đầu...")
            st.session_state.current_step = 0
            st.rerun()

        if st.button("◫   Nhập dữ liệu", type="primary" if _sb_cur == 1 else "secondary", key="sb_nav_1"):
            set_spinner_msg("⏳ Đang chuyển sang Bước 1: Nhập Dữ Liệu...")
            st.session_state.current_step = 1
            st.rerun()

        if st.button("◈   Làm sạch", type="primary" if _sb_cur == 2 else "secondary", key="sb_nav_2"):
            if st.session_state.step1_approved:
                set_spinner_msg("⏳ Đang mở Bước 2: Làm Sạch...")
                st.session_state.current_step = 2
                st.rerun()
            else:
                st.toast("⚠️ Vui lòng nạp file và Duyệt Bước 1 trước!", icon="⚠️")

        if st.button("↗   Báo cáo", type="primary" if _sb_cur == 3 else "secondary", key="sb_nav_3"):
            if st.session_state.step2_approved:
                set_spinner_msg("⏳ Đang mở Bước 3: Tạo Báo Cáo...")
                st.session_state.current_step = 3
                st.rerun()
            else:
                st.toast("⚠️ Vui lòng Duyệt Bước 2 trước!", icon="⚠️")

        st.divider()

        if st.button("↻   Làm mới phiên", key="sb_reset_session"):
            for k in ["files_loaded", "file_messages", "analysis_results", "editable_report", "editable_plan", "dashboard_scores_df"]:
                if k in st.session_state:
                    st.session_state[k] = [] if k in ["files_loaded", "file_messages"] else None
            st.session_state.step1_approved = False
            st.session_state.step2_approved = False
            st.session_state.step3_approved = False
            st.session_state.show_step2_audit_log = False
            st.session_state.show_step2_editor = False
            st.session_state.s1_issues_dismissed = set()
            st.session_state.current_step = 0
            orch.data_agent.raw_dataframes.clear()
            set_spinner_msg("⏳ Đang làm mới toàn bộ phiên làm việc...")
            st.rerun()

with st.sidebar:

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
                    padding: 2.2rem 0 0 0 !important;
                    margin: 0 !important;
                    max-width: 100% !important;
                    width: 100% !important;
                    overflow: hidden !important;
                    border: none !important;
                    border-radius: 0 !important;
                    box-shadow: none !important;
                    background: radial-gradient(circle at 12% 18%, rgba(147, 197, 253, 0.55) 0%, transparent 45%),
                                radial-gradient(circle at 85% 22%, rgba(96, 165, 250, 0.42) 0%, transparent 48%),
                                radial-gradient(circle at 52% 85%, rgba(186, 230, 253, 0.65) 0%, transparent 50%),
                                linear-gradient(135deg, #eff6ff 0%, #dbeafe 52%, #e0f2fe 100%) !important;
                }
                .st-key-landing_stage_container div[data-testid="stVerticalBlock"] {
                    gap: 0 !important;
                }
                /* Ẩn nút Streamlit gốc nhưng giữ trong DOM để JS bên trong trang Landing kích hoạt */
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
                set_spinner_msg("Đang mở Bước 1...")
                st.session_state.current_step = 1
                st.rerun()

            import streamlit.components.v1 as _landing_comp
            _landing_html = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:ital,wght@0,400;0,500;0,600;0,700;0,800;1,400&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Be Vietnam Pro', sans-serif; margin: 0; }
        .glass-panel {
            background: rgba(255, 255, 255, 0.75);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.9);
        }
        #cursor-glow {
            position: fixed;
            top: 0;
            left: 0;
            width: 340px;
            height: 340px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(59, 130, 246, 0.22) 0%, rgba(250, 204, 21, 0.14) 45%, rgba(255, 255, 255, 0) 70%);
            pointer-events: none;
            transform: translate(-50%, -50%);
            z-index: 1;
            transition: width 0.25s ease, height 0.25s ease, opacity 0.25s ease;
        }
        #cursor-dot {
            position: fixed;
            top: 0;
            left: 0;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #2563eb;
            box-shadow: 0 0 12px rgba(37, 99, 235, 0.8);
            pointer-events: none;
            transform: translate(-50%, -50%);
            z-index: 9999;
            transition: transform 0.12s ease, background-color 0.2s ease;
        }
        .hover-card {
            transition: transform 0.28s cubic-bezier(0.22, 1, 0.36, 1), box-shadow 0.28s ease;
        }
        .hover-card:hover {
            transform: translateY(-6px) scale(1.015);
            box-shadow: 0 18px 36px -10px rgba(37, 99, 235, 0.18);
        }
        @keyframes marquee-scroll {
            0% { transform: translateX(0%); }
            100% { transform: translateX(-50%); }
        }
        .marquee-track {
            display: flex;
            width: max-content;
            animation: marquee-scroll 24s linear infinite;
        }
        .marquee-track:hover {
            animation-play-state: paused;
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
        document.addEventListener('mousemove', function(e) {
            const glow = document.getElementById('cursor-glow');
            const dot = document.getElementById('cursor-dot');
            if (glow) {
                glow.style.left = e.clientX + 'px';
                glow.style.top = e.clientY + 'px';
            }
            if (dot) {
                dot.style.left = e.clientX + 'px';
                dot.style.top = e.clientY + 'px';
            }
        });
    </script>
</head>
<body class="text-slate-800 h-screen max-h-[660px] flex flex-col justify-between relative overflow-hidden" style="background: radial-gradient(circle at 12% 18%, rgba(147, 197, 253, 0.55) 0%, transparent 45%), radial-gradient(circle at 85% 22%, rgba(96, 165, 250, 0.42) 0%, transparent 48%), radial-gradient(circle at 52% 85%, rgba(186, 230, 253, 0.65) 0%, transparent 50%), linear-gradient(135deg, #eff6ff 0%, #dbeafe 52%, #e0f2fe 100%);">

    <div id="cursor-glow"></div>
    <div id="cursor-dot"></div>

    <!-- Các ngôi sao trang trí nền -->
    <div class="absolute top-20 left-[45%] text-slate-800 pointer-events-none">
        <svg class="w-6 h-6" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0L14.59 9.41L24 12L14.59 14.59L12 24L9.41 14.59L0 12L9.41 9.41L12 0Z"/></svg>
    </div>
    <div class="absolute bottom-28 left-[40%] text-slate-800 pointer-events-none">
        <svg class="w-8 h-8" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0L14.59 9.41L24 12L14.59 14.59L12 24L9.41 14.59L0 12L9.41 9.41L12 0Z"/></svg>
    </div>
    <div class="absolute top-32 right-8 text-slate-800 pointer-events-none">
        <svg class="w-6 h-6" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0L14.59 9.41L24 12L14.59 14.59L12 24L9.41 14.59L0 12L9.41 9.41L12 0Z"/></svg>
    </div>

    <!-- 1. THANH ĐIỀU HƯỚNG (HEADER) -->
    <header class="relative z-10 px-8 py-4 flex justify-between items-center max-w-7xl mx-auto w-full">
        <div class="flex items-center">
            <span class="bg-yellow-400 text-slate-900 text-xs font-extrabold px-4 py-1.5 rounded-full uppercase tracking-wider shadow-sm">
                Phân tích dữ liệu
            </span>
        </div>
        
        <nav class="hidden md:flex items-center space-x-1 glass-panel px-2 py-1.5 rounded-full shadow-sm text-xs font-medium text-slate-600">
            <a href="javascript:void(0)" class="bg-slate-900 text-white px-4 py-1.5 rounded-full transition">Giới thiệu</a>
            <a href="javascript:void(0)" onclick="triggerStart()" class="px-4 py-1.5 hover:text-slate-900 transition">Nhập dữ liệu</a>
            <a href="javascript:void(0)" onclick="triggerStart()" class="px-4 py-1.5 hover:text-slate-900 transition">Xử lý Dữ liệu</a>
            <a href="javascript:void(0)" onclick="triggerStart()" class="px-4 py-1.5 hover:text-slate-900 transition">Báo cáo &amp; Dashboard</a>
        </nav>

        <div class="w-24 hidden md:block"></div>
    </header>

    <!-- 2. NỘI DUNG CHÍNH (MAIN CONTENT) -->
    <main class="relative z-10 flex-1 max-w-7xl w-full mx-auto px-8 flex flex-col md:flex-row items-center justify-between gap-8 my-auto">
        
        <!-- CỘT TRÁI -->
        <div class="w-full md:w-[45%] flex flex-col items-start space-y-5">
            <span class="bg-blue-100 text-blue-700 font-semibold text-xs px-3.5 py-1.5 rounded-full">
                Nền tảng Quản trị Dữ liệu
            </span>

            <h1 class="text-4xl md:text-[2.75rem] font-extrabold text-slate-900 leading-[1.18] tracking-tight">
                Dữ liệu thông minh<br>
                <span class="text-slate-900">Báo cáo tức thì</span>
            </h1>

            <div class="flex items-center space-x-3 pt-1">
                <button onclick="triggerStart()" class="bg-blue-600 hover:bg-blue-700 text-white font-bold text-sm px-7 py-3.5 rounded-full shadow-lg shadow-blue-500/30 transition transform hover:-translate-y-0.5 cursor-pointer">
                    BẮT ĐẦU
                </button>
                <button onclick="triggerStart()" class="bg-yellow-400 hover:bg-yellow-500 text-slate-900 p-3.5 rounded-full shadow-md transition transform hover:rotate-45 cursor-pointer">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M7 17L17 7M17 7H7M17 7V17"></path></svg>
                </button>
            </div>

            <div class="glass-panel p-4 rounded-2xl max-w-md shadow-sm mt-2">
                <p class="text-xs text-slate-600 leading-relaxed m-0">
                    Tự động hóa quy trình thu thập, xử lý lỗi và trực quan hóa dữ liệu phức tạp. Biến những con số khô khan thành quyết định kinh doanh chiến lược chỉ trong vài cú nhấp chuột.
                </p>
            </div>
        </div>

        <!-- CỘT PHẢI: 3 THẺ DỌC SO LE NHAU -->
        <div class="w-full md:w-[55%] relative h-[410px] flex items-center justify-center">
            <div class="absolute w-72 h-72 bg-blue-200 rounded-full mix-blend-multiply filter blur-2xl opacity-60 animate-pulse"></div>
            
            <div class="relative w-full grid grid-cols-3 gap-4 items-center">
                
                <!-- Bước 1 (Thẻ dọc - Cao) -->
                <div onclick="triggerStart()" class="hover-card cursor-pointer glass-panel p-4 rounded-3xl shadow-lg border border-white flex flex-col justify-between min-h-[258px] gap-2.5 transform -translate-y-5">
                    <div class="flex justify-between items-center">
                        <span class="w-9 h-9 rounded-full bg-blue-100 text-blue-600 font-extrabold flex items-center justify-center text-base">1</span>
                        <span class="w-8 h-8 rounded-xl bg-blue-50 border border-blue-100 flex items-center justify-center text-blue-500">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"></path></svg>
                        </span>
                    </div>
                    <div class="p-2.5 rounded-2xl bg-blue-50/70 border border-dashed border-blue-200 flex flex-wrap gap-1.5 justify-center">
                        <span class="text-[10px] font-bold px-2 py-0.5 rounded-md bg-white text-blue-600 shadow-sm">CSV</span>
                        <span class="text-[10px] font-bold px-2 py-0.5 rounded-md bg-white text-emerald-600 shadow-sm">Excel</span>
                        <span class="text-[10px] font-bold px-2 py-0.5 rounded-md bg-white text-amber-600 shadow-sm">Sheet</span>
                    </div>
                    <div>
                        <span class="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Bước 1</span>
                        <h3 class="text-xl font-extrabold text-slate-800 mt-0.5 leading-tight">Nhập dữ liệu</h3>
                        <p class="text-[11px] text-slate-500 mt-1 leading-snug">Kết nối đa nguồn nhanh chóng</p>
                    </div>
                </div>

                <!-- Bước 2 (Thẻ dọc - Thấp so le) -->
                <div onclick="triggerStart()" class="hover-card cursor-pointer bg-gradient-to-br from-blue-500 to-blue-600 p-4 rounded-3xl shadow-xl text-white flex flex-col justify-between min-h-[258px] gap-2.5 transform translate-y-5">
                    <div class="flex justify-between items-center">
                        <span class="w-9 h-9 rounded-full bg-white/20 text-white font-extrabold flex items-center justify-center text-base backdrop-blur-sm">2</span>
                        <span class="w-8 h-8 rounded-xl bg-white/15 flex items-center justify-center text-yellow-300">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                        </span>
                    </div>
                    <div class="p-2.5 rounded-2xl bg-white/10 backdrop-blur-sm space-y-1.5">
                        <div class="flex justify-between text-[10px] font-semibold text-blue-100">
                            <span>Kiểm tra lỗi</span>
                            <span class="text-green-300">Sẵn sàng</span>
                        </div>
                        <div class="w-full h-1.5 bg-white/20 rounded-full overflow-hidden">
                            <div class="w-full h-full bg-green-400 rounded-full"></div>
                        </div>
                    </div>
                    <div>
                        <span class="text-[10px] text-blue-100 font-bold uppercase tracking-wider">Bước 2</span>
                        <h3 class="text-xl font-extrabold mt-0.5 leading-tight">Làm sạch</h3>
                        <div class="mt-2 bg-white/15 px-2.5 py-1.5 rounded-xl backdrop-blur-sm flex items-center space-x-2">
                            <div class="w-2 h-2 rounded-full bg-green-400 shrink-0"></div>
                            <span class="text-[11px] font-semibold">100% Chính xác</span>
                        </div>
                    </div>
                </div>

                <!-- Bước 3 (Thẻ dọc - Cao so le) -->
                <div onclick="triggerStart()" class="hover-card cursor-pointer glass-panel p-4 rounded-3xl shadow-lg border border-white flex flex-col justify-between min-h-[258px] gap-2.5 transform -translate-y-3">
                    <div class="flex justify-between items-center">
                        <span class="w-9 h-9 rounded-2xl bg-yellow-400 text-slate-900 font-black flex items-center justify-center text-base shadow-md">3</span>
                        <span class="text-[10px] font-bold px-2 py-1 rounded-lg bg-blue-50 text-blue-600 border border-blue-100">4 định dạng</span>
                    </div>
                    <div class="p-2.5 rounded-2xl bg-blue-50/80 border border-blue-100 flex items-end justify-center space-x-2 h-16">
                        <div class="w-3 bg-blue-300 h-5 rounded-t-md"></div>
                        <div class="w-3 bg-blue-400 h-8 rounded-t-md"></div>
                        <div class="w-3 bg-blue-600 h-11 rounded-t-md"></div>
                        <div class="w-3 bg-yellow-400 h-9 rounded-t-md"></div>
                    </div>
                    <div>
                        <span class="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Bước 3</span>
                        <h3 class="text-xl font-extrabold text-slate-800 mt-0.5 leading-tight">Tạo báo cáo</h3>
                        <p class="text-[11px] text-slate-500 mt-1 leading-snug">Biểu đồ trực quan &amp; xuất file</p>
                    </div>
                </div>

            </div>
        </div>
    </main>

    <!-- 3. DẢI BĂNG CHỮ CHẠY NGANG DƯỚI CÙNG (FOOTER NỀN SÁNG) -->
    <footer class="relative z-10 bg-white/85 backdrop-blur-md border-t border-blue-100 text-slate-700 py-2.5 overflow-hidden w-full">
        <div class="marquee-track text-[11px] font-bold tracking-wider uppercase">
            <div class="flex items-center space-x-12 px-6 shrink-0">
                <span class="flex items-center"><span class="text-blue-600 mr-2">✦</span> XỬ LÝ DỮ LIỆU THÔNG MINH</span>
                <span class="flex items-center"><span class="text-amber-500 mr-2">✦</span> BÁO CÁO TRỰC QUAN</span>
                <span class="flex items-center"><span class="text-blue-600 mr-2">✦</span> PHÂN TÍCH CHUYÊN SÂU</span>
                <span class="flex items-center"><span class="text-amber-500 mr-2">✦</span> TIẾT KIỆM THỜI GIAN</span>
                <span class="flex items-center"><span class="text-blue-600 mr-2">✦</span> TỐI ƯU HÓA QUY TRÌNH</span>
            </div>
            <div class="flex items-center space-x-12 px-6 shrink-0">
                <span class="flex items-center"><span class="text-blue-600 mr-2">✦</span> XỬ LÝ DỮ LIỆU THÔNG MINH</span>
                <span class="flex items-center"><span class="text-amber-500 mr-2">✦</span> BÁO CÁO TRỰC QUAN</span>
                <span class="flex items-center"><span class="text-blue-600 mr-2">✦</span> PHÂN TÍCH CHUYÊN SÂU</span>
                <span class="flex items-center"><span class="text-amber-500 mr-2">✦</span> TIẾT KIỆM THỜI GIAN</span>
                <span class="flex items-center"><span class="text-blue-600 mr-2">✦</span> TỐI ƯU HÓA QUY TRÌNH</span>
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
                st.markdown("""
                <div style="margin-bottom:0.5rem;">
                    <div style="background:linear-gradient(90deg, #eff6ff 0%, #dbeafe 100%); border-left:5px solid #2563eb; padding:0.45rem 0.95rem; border-radius:10px; display:inline-block; box-shadow:0 2px 6px rgba(37,99,235,0.08);">
                        <span style="font-weight:800; color:#1e3a8a; font-size:1.15rem; letter-spacing:0.2px;">
                            🚀 BƯỚC 1: NHẬP & KIỂM TRA DỮ LIỆU
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with col_s1_h2:
                btn_lbl = "✖ Đóng khung nạp thêm dữ liệu" if st.session_state.show_step1_uploader else "➕ Nạp thêm tệp / Google Sheet"
                if st.button(btn_lbl, use_container_width=True, key="btn_toggle_s1_uploader"):
                    st.session_state.show_step1_uploader = not st.session_state.show_step1_uploader
                    st.rerun()
        else:
            st.markdown("""
            <div style="margin-bottom:0.75rem;">
                <div style="background:linear-gradient(90deg, #eff6ff 0%, #dbeafe 100%); border-left:5px solid #2563eb; padding:0.5rem 1rem; border-radius:10px; display:inline-block; margin-bottom:4px; box-shadow:0 2px 6px rgba(37,99,235,0.08);">
                    <span style="font-weight:800; color:#1e3a8a; font-size:1.25rem; letter-spacing:0.3px;">
                        🚀 BƯỚC 1: NHẬP DỮ LIỆU
                    </span>
                </div>
                <div style="font-size:0.9rem; color:#0f172a; margin-top:4px; font-weight:700;">
                    Tải lên tệp CSV, Excel hoặc dán đường dẫn Google Sheet công khai để bắt đầu phân tích.
                </div>
            </div>
            """, unsafe_allow_html=True)

        if (not has_loaded_files) or st.session_state.show_step1_uploader:
            col_up1, col_divider, col_up2 = st.columns([1, 0.1, 1])
    
            with col_up1:
                with st.container(key="zone_upload_left"):
                    st.markdown("""
                    <div style="display:flex; align-items:center; gap:8px; margin-bottom:4px;">
                        <span style="font-size:1.1rem;">📄</span>
                        <span style="font-weight:800; color:#2563eb; font-size:1.05rem;">Tải tệp</span>
                    </div>
                    <div class="gsheet-hint-text" style="font-size:0.95rem; font-weight:800; color:#0f172a; margin-bottom:8px; line-height:1.4;">
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
                        if st.button("✅ Xác nhận & Kiểm tra tệp đã tải lên", type="primary", use_container_width=True, key="btn_verify_upload"):
                            with st.spinner("Đang đọc và kiểm tra chất lượng dữ liệu..."):
                                for up in uploaded_files:
                                    content = up.read()
                                    success, msg = orch.load_file(content, up.name)
                                    st.session_state.file_messages.append({"file": up.name, "success": success, "msg": msg})
                                    if success:
                                        if up.name in orch.data_agent.raw_dataframes:
                                            orch.data_agent.file_infos.setdefault(up.name, {})["original_df"] = orch.data_agent.raw_dataframes[up.name].copy()
                                        if up.name not in st.session_state.files_loaded:
                                            st.session_state.files_loaded.append(up.name)
                                st.session_state.show_step1_uploader = False
                            st.rerun()

            with col_divider:
                st.markdown("""
                <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; height:100%; min-height:220px;">
                    <div style="width:1.5px; height:40px; background:linear-gradient(to bottom, transparent, #cbd5e1);"></div>
                    <div style="background:#f1f5f9; color:#475569; font-weight:800; font-size:0.72rem; padding:5px 8px; border-radius:999px; border:1px solid #cbd5e1; margin:6px 0; letter-spacing:0.5px;">HOẶC</div>
                    <div style="width:1.5px; height:40px; background:linear-gradient(to top, transparent, #cbd5e1);"></div>
                </div>
                """, unsafe_allow_html=True)

            with col_up2:
                with st.container(key="zone_gsheet_right"):
                    st.markdown("""
                    <div style="display:flex; align-items:center; gap:8px; margin-bottom:4px;">
                        <span style="font-size:1.1rem;">🔗</span>
                        <span style="font-weight:800; color:#2563eb; font-size:1.05rem;">Đường dẫn Google Sheet</span>
                    </div>
                    <div class="gsheet-hint-text" style="font-size:0.95rem; font-weight:800; color:#0f172a; margin-bottom:8px; line-height:1.4;">
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
                        if st.button("✅ Kết nối & Kiểm tra Google Sheet", type="primary", use_container_width=True, key="btn_verify_gsheet"):
                            with st.spinner("Đang kết nối và kiểm tra Google Sheet..."):
                                success, msg = orch.load_google_sheet(sheet_url)
                                g_keys = [k for k in orch.data_agent.raw_dataframes.keys() if k.startswith("GoogleSheet")]
                                latest_gkey = g_keys[-1] if g_keys else "Google Sheet"
                                st.session_state.file_messages.append({"file": latest_gkey, "success": success, "msg": msg})
                                if success:
                                    if latest_gkey in orch.data_agent.raw_dataframes:
                                        orch.data_agent.file_infos.setdefault(latest_gkey, {})["original_df"] = orch.data_agent.raw_dataframes[latest_gkey].copy()
                                    st.session_state.files_loaded.append(latest_gkey)
                                st.session_state.show_step1_uploader = False
                            st.rerun()

        if "_pending_biz_type" in st.session_state:
            st.session_state["biz_type"] = st.session_state.pop("_pending_biz_type")
        if "_pending_biz_questions" in st.session_state:
            st.session_state["biz_questions"] = st.session_state.pop("_pending_biz_questions")

        # Bước 1 chỉ nạp tệp, nhập bối cảnh và thông báo tóm tắt; việc xử lý lỗi thực hiện ở Bước 2

        # ============================================================
        # BỐI CẢNH DOANH NGHIỆP (CHỈ HIỆN SAU KHI ĐÃ XỬ LÝ/BỎ QUA LỖI)
        # ============================================================
        if st.session_state.file_messages:
            if "step1_ai_summaries" not in st.session_state:
                st.session_state.step1_ai_summaries = {}
            st.markdown(f"#### 📋 Chi tiết kiểm tra & Phê duyệt xử lý lỗi ({len(st.session_state.file_messages)} tệp)")
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
                                _short_err_lines = "\n".join(
                                    f"- **{iss['type']}:** {iss['count']:,} {'dòng' if 'trùng' in iss['type'].lower() or 'dòng' in iss['type'].lower() else 'ô'}"
                                    for iss in detected_issues
                                )
                                st.warning(
                                    f"⚠️ **Phát hiện {len(detected_issues)} nhóm lỗi trong tệp `{item['file']}`:**\n\n"
                                    f"{_short_err_lines}\n\n"
                                    f"👉 Vui lòng bấm **✅ Duyệt & Sang Bước 2 ➔** để kiểm tra chi tiết và xử lý làm sạch."
                                )
                            else:
                                st.success(
                                    f"✅ **Tệp `{item['file']}` đạt chuẩn chất lượng 100% ({len(df_chk):,} dòng × {len(df_chk.columns)} cột):** "
                                    f"Không có ô trống, không có bản ghi trùng lặp và định dạng hoàn toàn hợp lệ."
                                )
                                if has_backup and user_logs_s1:
                                    with st.expander(f"📜 Nhật ký các mục bạn đã duyệt sửa trên `{item['file']}` ({len(user_logs_s1)} thao tác)", expanded=False):
                                        for u_l in user_logs_s1:
                                            st.markdown(f"- ✅ {u_l}")
                                        if st.button("↩️ Hoàn tác & Khôi phục dữ liệu gốc ban đầu", key=f"btn_undo_clean_s1_{item['file']}"):
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
                                        issues_parts.append("- **Gợi ý xử lý:** Tích chọn các mục sửa lỗi bên trên và bấm **Duyệt & Sửa ngay**, hoặc sửa trực tiếp tại bảng bên dưới.")
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
                            if not detected_issues:
                                st.info(f"🤖 **Nhận xét nhanh về `{item['file']}`:**\n\n{st.session_state.step1_ai_summaries[cache_key]}")
                    else:
                        st.error(f"❌ **Lỗi đọc tệp '{item['file']}':** {item['msg']}\n\n*💡 Hướng dẫn khắc phục: Kiểm tra xem tệp có đang mở hoặc bị khóa bởi phần mềm khác không, hoặc lưu lại tệp dưới định dạng chuẩn CSV (UTF-8) / Excel (.xlsx).*")

        with st.container(key="zone_biz_context"):
            col_b_head, col_b_btn = st.columns([2.4, 1.6])
            with col_b_head:
                st.markdown("""
                <div style="background:linear-gradient(90deg, #ecfdf5 0%, #d1fae5 100%); border-left:5px solid #10b981; padding:0.45rem 0.95rem; border-radius:10px; display:inline-block; margin-bottom:4px; box-shadow:0 2px 6px rgba(16,185,129,0.08);">
                    <span style="font-weight:800; color:#065f46; font-size:1.18rem; letter-spacing:0.3px;">
                        📄 BỐI CẢNH DOANH NGHIỆP
                    </span>
                </div>
                <div style="font-size:0.86rem; color:#0f172a; margin-top:2px; margin-bottom:10px; font-weight:700;">
                    Mô tả ngắn gọn về mô hình hoạt động và câu hỏi bạn muốn giải đáp để hệ thống phân tích sát thực tế hơn.
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
                        st.session_state["_ai_ctx_done_msg"] = f"✅ Đã tự động điền gợi ý Lĩnh vực và {len(q_list)} câu hỏi phân tích sát với tệp `{first_fname}`!"
                        st.rerun()
                    else:
                        st.warning("⚠️ Bạn chưa nạp tệp dữ liệu nào! Vui lòng tải tệp CSV/Excel hoặc dán link Google Sheet ở khung phía trên trước khi bấm gợi ý AI.")

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
            with st.container(key="floating_approve_step1"):
                if st.button("✅ Duyệt & Sang Bước 2 ➔", type="primary", use_container_width=True, key="btn_approve_step1"):
                    set_spinner_msg("Đang chuyển sang Bước 2: Làm sạch & Kiểm tra dữ liệu...")
                    st.session_state.step1_approved = True
                    st.session_state.current_step = 2
                    st.rerun()

        if orch.data_agent.raw_dataframes:
            st.markdown("#### ✏️ Sửa nhanh dữ liệu ngay tại Bước 1")
            with st.container():
                s1_file_list = list(orch.data_agent.raw_dataframes.keys())
                col_s1_sel, col_s1_info = st.columns([1.5, 2.5])
                with col_s1_sel:
                    s1_chosen_file = st.selectbox("Chọn tệp cần xem / sửa:", s1_file_list, key="s1_file_selector")
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
                    if st.button("💾 Lưu sửa nhanh", type="primary", use_container_width=True, key="btn_save_step1"):
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
                            st.error("⚠️ Không thể lưu thay đổi. Vui lòng kiểm tra định dạng dữ liệu vừa nhập.")
                with col_s1_apply_filter:
                    if s1_is_filtered:
                        if st.button("✂️ Chỉ giữ các dòng đang lọc", use_container_width=True, key="btn_keep_filtered_step1"):
                            orch.data_agent.raw_dataframes[s1_chosen_file] = s1_view_df.reset_index(drop=True)
                            st.toast(f"✅ Đã lọc giữ lại {len(s1_view_df):,} dòng!")
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
            st.warning("⚠️ Chưa có dữ liệu. Vui lòng quay lại Bước 1 để tải tệp.")
            if st.button("⬅ Quay lại Bước 1", type="primary"):
                st.session_state.current_step = 1
                st.rerun()
        else:
            file_list = list(orch.data_agent.raw_dataframes.keys())
            st.markdown("### Bước 2: Làm sạch & kiểm tra dữ liệu")

            top_bar_c1, top_bar_c2, top_bar_c3 = st.columns([1.8, 2.4, 1.8])
            with top_bar_c1:
                selected_file = st.selectbox("Tệp đang xem:", file_list)
            df_current = orch.data_agent.raw_dataframes[selected_file]
            total_rows = len(df_current)
            file_info_cur = orch.data_agent.file_infos.get(selected_file, {})
            detected_groups = orch.data_agent.get_regions_detected()
            s2_health = compute_data_health_metrics(df_current)
            s2_issues = detect_data_issues(df_current, selected_file)

            with top_bar_c2:
                total_records = sum(len(df) for df in orch.data_agent.raw_dataframes.values())
                st.markdown(f"<div style='margin-top:1.75rem; font-size:0.95rem; color:#0f172a;'><b>{total_rows:,} dòng × {len(df_current.columns)} cột</b></div>", unsafe_allow_html=True)

            with top_bar_c3:
                csv_clean_bytes = df_current.to_csv(index=False).encode("utf-8-sig")
                st.download_button(
                    label=f"📥 Tải dữ liệu sạch ({selected_file}).csv",
                    data=csv_clean_bytes,
                    file_name=f"Cleaned_{selected_file}.csv",
                    mime="text/csv",
                    use_container_width=True,
                    key=f"dl_cleaned_csv_s2_{selected_file}"
                )

            if total_records > 0:
                with st.container(key="floating_approve_step2"):
                    if st.button("✅ Duyệt & Sang Bước 3 ➔", type="primary", use_container_width=True, key="btn_approve_step2"):
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
            lbl_s2_btn = "✖ Đóng bảng sửa dữ liệu" if st.session_state.show_step2_editor else "✏️ Bấm vào đây nếu muốn sửa dữ liệu"
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
                            f"✅ **Tệp `{selected_file}` đã đạt chuẩn 100%!**\n\n"
                            f"- **Cấu trúc bảng:** Giữ nguyên toàn bộ **{total_rows:,} dòng × {len(df_current.columns)} cột**, không có dòng/cột trống thừa hay dòng trùng lặp.\n"
                            f"- **Độ đầy đủ dữ liệu:** 100% các ô đều có giá trị (0 ô trống).\n"
                            f"- **Các cột số đã chuẩn hóa ({len(num_cols)} cột):** {num_cols_str if num_cols else 'Không có'}.\n"
                            f"- **Các cột văn bản / phân loại ({len(txt_cols)} cột):** {txt_cols_str if txt_cols else 'Không có'}.\n"
                            f"- **Đã chuẩn hóa tên trường ({len(mapped_dict)} trường):** {mapped_str if mapped_dict else 'Tự động nhận diện'}."
                        )
                    else:
                        if s2_issues:
                            s2_issue_key_prefix = f"s2_fix_{selected_file}"
                            if f"{s2_issue_key_prefix}_selected" not in st.session_state:
                                st.session_state[f"{s2_issue_key_prefix}_selected"] = [iss["id"] for iss in s2_issues]

                            s2_chosen_fixes = st.session_state.get(f"{s2_issue_key_prefix}_selected", [])
                            all_s2_ids = [iss["id"] for iss in s2_issues]

                            col_hdr_l, col_hdr_r = st.columns([3.4, 1.0])
                            with col_hdr_l:
                                st.markdown(f"""
                                <div style="margin-bottom:4px;">
                                    <span style="display:inline-flex; align-items:center; gap:6px; background:linear-gradient(90deg, #ffffff 0%, #eff6ff 100%); color:#1e3a8a; border:1px solid #bfdbfe; border-radius:999px; padding:3px 12px; font-size:0.76rem; font-weight:700;">
                                        <span style="width:7px; height:7px; border-radius:50%; background:#2563eb; display:inline-block;"></span>
                                        Cần phê duyệt trước khi phân tích
                                    </span>
                                </div>
                                <div style="font-size:1.45rem; font-weight:800; color:#0f172a; letter-spacing:-0.02em; margin-bottom:2px;">
                                    Kiểm tra &amp; Xử lý lỗi dữ liệu
                                </div>
                                <div style="font-size:0.88rem; color:#475569; line-height:1.45; margin-bottom:10px;">
                                    Hệ thống phát hiện <b>{len(s2_issues)} nhóm vấn đề</b> ảnh hưởng đến độ chính xác của tập dữ liệu <b>{selected_file}</b>.<br>
                                    Chọn các đề xuất bên dưới để tự động làm sạch (bạn có thể sửa lại nội dung đề xuất xử lý).
                                </div>
                                """, unsafe_allow_html=True)
                            with col_hdr_r:
                                st.markdown("<div style='height:34px;'></div>", unsafe_allow_html=True)
                                if len(s2_chosen_fixes) < len(all_s2_ids):
                                    if st.button(f"☑️ Chọn tất cả ({len(all_s2_ids)})", use_container_width=True, key=f"btn_sel_all_s2_{selected_file}"):
                                        st.session_state[f"{s2_issue_key_prefix}_selected"] = list(all_s2_ids)
                                        for iid in all_s2_ids:
                                            st.session_state[f"chk_s2_{selected_file}_{iid}"] = True
                                        st.rerun()
                                else:
                                    if st.button(f"⬜ Bỏ chọn tất cả ({len(all_s2_ids)})", use_container_width=True, key=f"btn_unsel_all_s2_{selected_file}"):
                                        st.session_state[f"{s2_issue_key_prefix}_selected"] = []
                                        for iid in all_s2_ids:
                                            st.session_state[f"chk_s2_{selected_file}_{iid}"] = False
                                        st.rerun()

                            s2_custom_instrs = {}
                            for idx_s2i, s2_iss in enumerate(s2_issues):
                                is_selected_card = s2_iss["id"] in st.session_state[f"{s2_issue_key_prefix}_selected"]
                                sev_raw = s2_iss["severity"]
                                sev_label = "Nghiêm trọng" if sev_raw == "Quan trọng" else sev_raw
                                if sev_label == "Nghiêm trọng":
                                    sev_bg, sev_fg, sev_dot, sev_bd = "#fee2e2", "#dc2626", "#ef4444", "#fecaca"
                                elif sev_label == "Cảnh báo":
                                    sev_bg, sev_fg, sev_dot, sev_bd = "#fef3c7", "#b45309", "#f59e0b", "#fde68a"
                                else:
                                    sev_bg, sev_fg, sev_dot, sev_bd = "#e0f2fe", "#0284c7", "#38bdf8", "#bae6fd"

                                card_bg = "#f0f7ff" if is_selected_card else ("#fffbeb" if sev_label == "Cảnh báo" else "rgba(255, 255, 255, 0.92)")
                                card_border = "2px solid #2563eb" if is_selected_card else ("1.5px solid #fde68a" if sev_label == "Cảnh báo" else "1px solid #e2e8f0")
                                card_shadow = (
                                    "0 12px 28px -6px rgba(37, 99, 235, 0.22), 0 4px 10px -2px rgba(37, 99, 235, 0.12), inset 0 1px 0 rgba(255, 255, 255, 0.9)"
                                    if is_selected_card else
                                    "0 10px 24px -6px rgba(15, 23, 42, 0.10), 0 4px 8px -2px rgba(15, 23, 42, 0.06), inset 0 1px 0 rgba(255, 255, 255, 0.95)"
                                )
                                sug_bg = "#eff6ff" if is_selected_card else ("#eff6ff" if sev_label == "Nhẹ" else "#f1f5f9")
                                clean_desc = str(s2_iss["desc"]).replace("`", "")
                                unit_lbl = "dòng" if "trùng" in s2_iss["type"].lower() or "dòng" in s2_iss["type"].lower() else "ô"
                                card_key = f"s2_err_card_{idx_s2i}"

                                st.markdown(f"""
                                <style>
                                    .st-key-{card_key} {{
                                        background: {card_bg} !important;
                                        border: {card_border} !important;
                                        border-radius: 16px !important;
                                        padding: 14px 18px !important;
                                        margin-bottom: 12px !important;
                                        box-shadow: {card_shadow} !important;
                                        transition: transform 0.2s ease, box-shadow 0.2s ease !important;
                                    }}
                                    .st-key-{card_key}:hover {{
                                        transform: translateY(-2px) !important;
                                    }}
                                    .st-key-{card_key} div[data-testid="stCheckbox"] label span[data-baseweb="checkbox"] > div {{
                                        background-color: {"#2563eb" if is_selected_card else "#ffffff"} !important;
                                        border-color: {"#2563eb" if is_selected_card else "#cbd5e1"} !important;
                                    }}
                                    .st-key-{card_key} div[data-testid="stTextInput"] div[data-baseweb="input"] {{
                                        background: {sug_bg} !important;
                                        border: 1px solid #e2e8f0 !important;
                                        border-radius: 8px !important;
                                    }}
                                    .st-key-{card_key} div[data-testid="stTextInput"] input {{
                                        background: transparent !important;
                                        color: #0f172a !important;
                                        font-size: 0.84rem !important;
                                    }}
                                </style>
                                """, unsafe_allow_html=True)

                                with st.container(key=card_key):
                                    c_top_chk, c_top_title, c_top_badge = st.columns([0.45, 5.2, 1.35])
                                    with c_top_chk:
                                        is_checked = st.checkbox(
                                            "Chọn",
                                            value=is_selected_card,
                                            label_visibility="collapsed",
                                            key=f"chk_s2_{selected_file}_{s2_iss['id']}"
                                        )
                                        if is_checked and s2_iss["id"] not in st.session_state[f"{s2_issue_key_prefix}_selected"]:
                                            st.session_state[f"{s2_issue_key_prefix}_selected"].append(s2_iss["id"])
                                        elif not is_checked and s2_iss["id"] in st.session_state[f"{s2_issue_key_prefix}_selected"]:
                                            st.session_state[f"{s2_issue_key_prefix}_selected"].remove(s2_iss["id"])
                                    with c_top_title:
                                        st.markdown(
                                            f"<div style='padding-top:2px; font-size:0.95rem; color:#0f172a;'>"
                                            f"<b>{s2_iss['type']}</b> <span style='color:#64748b; font-weight:500; font-size:0.86rem;'>· {s2_iss['count']:,} {unit_lbl}</span>"
                                            f"</div>",
                                            unsafe_allow_html=True
                                        )
                                    with c_top_badge:
                                        st.markdown(
                                            f"<div style='display:flex; justify-content:flex-end;'>"
                                            f"<span style='display:inline-flex; align-items:center; gap:5px; background:{sev_bg}; color:{sev_fg}; border:1px solid {sev_bd}; font-size:0.74rem; font-weight:700; padding:2px 10px; border-radius:999px; white-space:nowrap;'>"
                                            f"<span style='width:6px; height:6px; border-radius:50%; background:{sev_dot}; display:inline-block;'></span>{sev_label}</span></div>",
                                            unsafe_allow_html=True
                                        )

                                    st.markdown(
                                        f"<div style='background:rgba(255,255,255,0.85); border:1px solid #e2e8f0; border-radius:10px; padding:9px 14px; margin:4px 0 8px 0; font-size:0.84rem; color:#334155;'>"
                                        f"{clean_desc}</div>",
                                        unsafe_allow_html=True
                                    )

                                    c_sug_lbl, c_sug_inp = st.columns([1.25, 4.75])
                                    with c_sug_lbl:
                                        st.markdown(
                                            f"<div style='background:{sug_bg}; border:1px solid #e2e8f0; border-radius:8px; padding:7px 10px; font-size:0.8rem; font-weight:700; color:#0f172a; white-space:nowrap;'>"
                                            f"› Đề xuất xử lý:</div>",
                                            unsafe_allow_html=True
                                        )
                                    with c_sug_inp:
                                        s2_custom_txt = st.text_input(
                                            "Đề xuất xử lý",
                                            value=st.session_state.get(f"instr_s2_{selected_file}_{s2_iss['id']}", s2_iss["suggested_fix"]),
                                            label_visibility="collapsed",
                                            key=f"instr_s2_{selected_file}_{s2_iss['id']}"
                                        )
                                        s2_custom_instrs[s2_iss["id"]] = s2_custom_txt

                            s2_err_preview = get_issue_preview_rows(df_current, max_rows=100)
                            if not s2_err_preview.empty:
                                s2_pv_key = f"s2_pv_open_{selected_file}"
                                if s2_pv_key not in st.session_state:
                                    st.session_state[s2_pv_key] = False
                                st.markdown("""
                                <style>
                                    .st-key-s2_err_preview_card {
                                        background: rgba(255, 255, 255, 0.94) !important;
                                        border: 1px solid #e2e8f0 !important;
                                        border-radius: 16px !important;
                                        padding: 12px 18px !important;
                                        margin-top: 4px !important;
                                        box-shadow: 0 10px 24px -6px rgba(15, 23, 42, 0.08), 0 4px 8px -2px rgba(15, 23, 42, 0.04), inset 0 1px 0 rgba(255, 255, 255, 0.95) !important;
                                    }
                                    .st-key-btn_toggle_pv_s2 button {
                                        background: #eff6ff !important;
                                        color: #2563eb !important;
                                        border: 1px solid #bfdbfe !important;
                                        border-radius: 999px !important;
                                        font-weight: 700 !important;
                                        font-size: 0.82rem !important;
                                    }
                                </style>
                                """, unsafe_allow_html=True)
                                with st.container(key="s2_err_preview_card"):
                                    pv_c1, pv_c2 = st.columns([4.8, 1.2])
                                    with pv_c1:
                                        st.markdown(f"""
                                        <div style="display:flex; align-items:center; gap:12px;">
                                            <div style="width:38px; height:38px; border-radius:10px; background:#eff6ff; border:1px solid #dbeafe; display:flex; align-items:center; justify-content:center; color:#2563eb; flex-shrink:0;">
                                                <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M9 21V9"/></svg>
                                            </div>
                                            <div>
                                                <div style="font-size:0.92rem; color:#0f172a;"><b>Xem trước các dòng dữ liệu có lỗi</b> <span style="color:#64748b; font-size:0.84rem;">· {len(s2_err_preview)} dòng mẫu</span></div>
                                                <div style="font-size:0.8rem; color:#64748b; margin-top:1px;">Đối chiếu trực tiếp các ô bị khuyết, số âm và chuỗi dư khoảng trắng trước khi sửa</div>
                                            </div>
                                        </div>
                                        """, unsafe_allow_html=True)
                                    with pv_c2:
                                        pv_lbl = "Thu gọn ⌃" if st.session_state[s2_pv_key] else "Mở bảng ⌄"
                                        if st.button(pv_lbl, use_container_width=True, key="btn_toggle_pv_s2"):
                                            st.session_state[s2_pv_key] = not st.session_state[s2_pv_key]
                                            st.rerun()
                                    if st.session_state[s2_pv_key]:
                                        st.dataframe(s2_err_preview, use_container_width=True, height=460)

                            st.write("")
                            col_s2_btn_apply, col_s2_btn_undo = st.columns([2.5, 1.1])
                            with col_s2_btn_apply:
                                btn_s2_fix_label = f"🛠️ Duyệt & Sửa ngay ({len(s2_chosen_fixes)} mục đã chọn)" if s2_chosen_fixes else "⚠️ Chưa chọn mục nào để sửa"
                                if st.button(btn_s2_fix_label, type="primary", use_container_width=True, key=f"btn_apply_fixes_s2_{selected_file}", disabled=(not s2_chosen_fixes)):
                                    with st.spinner(f"Đang áp dụng các sửa đổi do bạn duyệt trên tệp {selected_file}..."):
                                        fixed_df, fix_reps = apply_data_issue_fixes(df_current, s2_chosen_fixes, custom_instructions=s2_custom_instrs)
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
                                        st.toast(f"✅ Đã xử lý xong các lỗi trên {selected_file}!")
                                    st.rerun()
                            with col_s2_btn_undo:
                                if has_s2_backup and user_edits:
                                    if st.button("↩️ Khôi phục bản gốc", use_container_width=True, key=f"btn_undo_s2_{selected_file}"):
                                        orig_copy = file_info_cur["original_df"].copy()
                                        orch.data_agent.raw_dataframes[selected_file] = orig_copy
                                        file_info_cur["rows"] = len(orig_copy)
                                        file_info_cur["user_action_log"] = []
                                        st.toast(f"↩️ Đã khôi phục tệp {selected_file} về dữ liệu gốc ban đầu.")
                                        st.rerun()

                        details = [f"📋 **Nhật ký kiểm tra & cấu trúc tệp `{selected_file}`:**"]
                        details.append(f"- 📊 **Quy mô hiện tại:** **{len(df_current):,} dòng × {len(df_current.columns)} cột**.")
                        details.append(f"- 🔢 **Cột số ({len(num_cols)} cột):** {num_cols_str if num_cols else 'Không có'}.")
                        details.append(f"- 🏷️ **Cột phân loại / văn bản ({len(txt_cols)} cột):** {txt_cols_str if txt_cols else 'Không có'}.")
                        details.append(f"- 🔗 **Ánh xạ trường ({len(mapped_dict)} trường):** {mapped_str if mapped_dict else 'Tự động nhận diện'}.")
                        for u_log in user_edits:
                            details.append(f"- ✅ **Đã phê duyệt & thực thi:** {u_log}")
                        st.info("\n".join(details))
                        if not s2_issues and has_s2_backup and user_edits:
                            if st.button("↩️ Hoàn tác & Khôi phục dữ liệu gốc ban đầu", key=f"btn_undo_clean_s2_{selected_file}"):
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
                        st.caption("Nhấp đúp vào ô bất kỳ để sửa trực tiếp, sau đó bấm nút **Lưu Dữ Liệu Đã Sửa** hoặc **Làm Sạch & Chuẩn Hóa** bên dưới:")
                        edited_slice = st.data_editor(
                            s2_view_df[s2_display_cols],
                            use_container_width=True,
                            num_rows="dynamic",
                            height=500,
                            key=f"editor_{selected_file}"
                        )

                    col_save, col_clean = st.columns([1, 1])
                    with col_save:
                        if st.button("💾 Lưu Dữ Liệu Đã Sửa", type="primary", use_container_width=True, key="btn_save_step2"):
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
                                    st.success(f"✅ Đã lưu cập nhật thành công cho tệp {selected_file} ({len(new_df):,} dòng)!")
                                set_spinner_msg(f"Đang cập nhật lại bảng dữ liệu {selected_file} sau khi lưu...")
                                st.rerun()
                            except Exception:
                                st.error("⚠️ Đã xảy ra lỗi khi lưu dữ liệu chỉnh sửa. Vui lòng kiểm tra lại định dạng các ô vừa nhập.")
                    
                    with col_clean:
                        if st.button("✨ Làm Sạch & Chuẩn Hóa", type="primary", use_container_width=True, key="btn_clean_step2"):
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
                                        f"Đã chạy Làm sạch & Chuẩn hóa tự động (xóa {removed_manual} dòng trống, chuẩn hóa định dạng số & khoảng trắng)."
                                    )
                                st.success(f"✨ Đã làm sạch và chuẩn hóa tự động toàn bộ {len(cleaned_df):,} dòng!")
                                set_spinner_msg(f"Đang hiển thị bảng dữ liệu {selected_file} sau khi làm sạch...")
                                st.rerun()
                            except Exception:
                                st.error("⚠️ Không thể chuẩn hóa tự động một số cột đặc biệt trong tệp này. Dữ liệu gốc vẫn được giữ nguyên an toàn.")

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
        build_unified_report_dashboard_html = _exp_mod.build_unified_report_dashboard_html
        build_docx_bytes = getattr(_exp_mod, "build_docx_bytes", None)
        build_pdf_bytes = getattr(_exp_mod, "build_pdf_bytes", None)
        import streamlit.components.v1 as components

        # ============================================================
        # MÀN HÌNH CHÍNH: BÁO CÁO TỔNG HỢP & DASHBOARD NHẬN XÉT TRỰC TIẾP
        # ============================================================
        st.markdown("""
        <div style="margin-bottom:0.4rem;">
            <div style="font-size:1.35rem; font-weight:800; color:#1e3a8a; letter-spacing:0.2px;">
                Báo Cáo Tổng Hợp & Dashboard Nhận Xét
            </div>
        </div>
        """, unsafe_allow_html=True)

        _msg_uni = st.session_state.pending_spinner_msg or "Đang tạo Báo cáo & Dashboard..."
        st.session_state.pending_spinner_msg = ""
        _total_rec = sum(len(df) for df in orch.data_agent.raw_dataframes.values())
        _uni_cache_key = (
            "v5_detailed_report",
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
                    ) if build_docx_bytes else None
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
                    ) if build_pdf_bytes else None
                except Exception:
                    st.session_state._uni_pdf_cached = None
                st.session_state._uni_export_key = _uni_cache_key

        unified_html = st.session_state._uni_html_cached

        with st.container(key="zone_step3_preview"):
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
            label_rep_btn = "✖ Đóng khung sửa báo cáo" if st.session_state.show_edit_report else "✏️ Chỉnh sửa nội dung báo cáo"
            if st.button(label_rep_btn, use_container_width=True, key="toggle_edit_report_btn"):
                st.session_state.show_edit_report = not st.session_state.show_edit_report
                st.rerun()

        with btn_ed_col2:
            label_dash_btn = "✖ Đóng khung sửa điểm số" if st.session_state.show_edit_dashboard else "📊 Chỉnh sửa điểm số Dashboard"
            if st.button(label_dash_btn, use_container_width=True, key="toggle_edit_dashboard_btn"):
                st.session_state.show_edit_dashboard = not st.session_state.show_edit_dashboard
                st.rerun()

        if st.session_state.show_edit_report:
            st.markdown("##### ✏️ Chỉnh sửa nội dung báo cáo")
            new_title = st.text_input("Tiêu đề báo cáo:", value=st.session_state.dashboard_title, key="rep_title_input")
            col_ed1, col_ed2 = st.columns(2)
            with col_ed1:
                new_report = st.text_area("Nội dung tóm tắt & nhận xét:", value=st.session_state.editable_report, height=220)
            with col_ed2:
                new_plan = st.text_area("Kế hoạch triển khai đề xuất:", value=st.session_state.editable_plan, height=220)

            if st.button("💾 Lưu thay đổi báo cáo", type="primary", use_container_width=True):
                st.session_state.dashboard_title = new_title
                st.session_state.editable_report = new_report
                st.session_state.editable_plan = new_plan
                results["report"] = new_report
                results["survey_plan"] = new_plan
                st.session_state.show_edit_report = False
                st.rerun()

        if st.session_state.show_edit_dashboard:
            st.markdown("##### 📊 Chỉnh sửa điểm số trên Dashboard")
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
                    new_df["Trạng thái"] = ["✅ Ưu tiên" if i < 2 else "📌 Theo dõi" for i in range(len(new_df))]
                    st.session_state.dashboard_scores_df = new_df
                    st.session_state.show_edit_dashboard = False
                    st.rerun()

            with col_btn_dash2:
                if st.button("🤖 Phân tích lại bằng AI", use_container_width=True):
                    with st.spinner("AI đang phân tích sâu dữ liệu..."):
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

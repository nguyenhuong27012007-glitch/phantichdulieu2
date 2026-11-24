"""Presentation components. Data processing stays in app.py and agents/."""

from html import escape
from pathlib import Path
import re
from textwrap import dedent

import streamlit as st

_UI_VERSION = 3


def clean_ui_text(value: str) -> str:
    """Remove legacy emoji from status messages without changing stored data."""
    return re.sub(r"[\U0001f000-\U0001faff\u2600-\u27bf\u2b00-\u2bff\u23f3\ufe0f\u200d]", "", str(value)).strip()


def markup(content: str):
    st.markdown(dedent(content).strip(), unsafe_allow_html=True)


def load_styles():
    css_path = Path(__file__).parent / "assets" / "styles.css"
    if css_path.exists():
        css = css_path.read_text(encoding="utf-8")
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def render_brand():
    markup('''
        <div class="brand"><div class="brand-symbol" aria-hidden="true"><i></i><i></i><i></i></div>
        <div><strong style="color:#1e3a8a !important;">Data Insight</strong><span>KHÔNG GIAN PHÂN TÍCH</span></div></div>
    ''')


def render_header(step: int, file_count: int):
    step_labels = [
        "Tổng quan",
        "Bước 1 · Nhập dữ liệu",
        "Bước 2 · Làm sạch dữ liệu",
        "Bước 3 · Báo cáo & Dashboard",
    ]
    label = step_labels[step] if 0 <= step < len(step_labels) else step_labels[0]
    chip_cls = "session-chip has-files" if file_count > 0 else "session-chip"
    markup(f'''
        <div class="app-topline">
            <span class="step-pill-badge" style="color:#1e3a8a !important;">{escape(label)}</span>
            <span class="{chip_cls}"><i class="chip-dot"></i>{file_count} tệp đã nạp</span>
        </div>
    ''')


def render_page_title(eyebrow: str, title: str, description: str):
    markup(f'''
        <div class="page-heading">
            <span class="eyebrow" style="color:#2563eb !important;font-weight:800 !important;">{escape(eyebrow)}</span>
            <h1 style="color:#1e3a8a !important;font-weight:800 !important;">{escape(title)}</h1>
            <p style="color:#64748b !important;">{escape(description)}</p>
        </div>
    ''')

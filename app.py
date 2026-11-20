"""
 Hệ thống AI Agent - Phân Tích Dữ Liệu & Đánh Giá Thị Trường Mở Rộng (HUMAN-IN-THE-LOOP WIZARD)
Giao diện Data Insight: điều hướng rõ ràng, hỗ trợ thiết bị di động và giảm chuyển động.
Phiên bản báo cáo chuẩn 100% từ dữ liệu gốc (nhận định 1-2 câu dưới mỗi biểu đồ & đề xuất hành động cuối báo cáo)
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

import inspect
import re as _ui_re
from html import escape as _ui_escape
from pathlib import Path as _UiPath
from textwrap import dedent as _ui_dedent

_FALLBACK_STYLES_CSS = ':root {\n    --ink: #192b45;\n    --muted: #63718a;\n    --blue: #2563eb;\n    --line: #e2e8f1;\n    --surface: #ffffff;\n}\n\nhtml { scroll-behavior: smooth; }\nbody, .stApp { font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, sans-serif; }\n[data-testid="stAppViewContainer"], [data-testid="stMain"] { background: #f6f8fc; }\n[data-testid="stHeader"] { background: transparent; }\n[data-testid="stMainBlockContainer"] {\n    max-width: 1440px;\n    padding: 2.2rem clamp(1.25rem, 3.5vw, 4rem) 3rem;\n}\n[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] { gap: 1.25rem; }\n[data-testid="stSidebar"] { background: #fff; border-right: 1px solid var(--line); }\n[data-testid="stSidebar"] > div:first-child { width: 260px; }\n[data-testid="stSidebarUserContent"] { padding: 1.6rem 1.15rem; }\n.brand { display: flex; gap: 12px; align-items: center; margin-bottom: 2.25rem; }\n.brand-symbol { width: 39px; height: 41px; background: #2563eb; border-radius: 12px; display: flex; align-items: end; justify-content: center; gap: 3px; padding: 11px 8px; box-sizing: border-box; }\n.brand-symbol i { width: 5px; background: white; border-radius: 2px; height: 9px; }\n.brand-symbol i:nth-child(2) { height: 15px; opacity: .7; }\n.brand-symbol i:nth-child(3) { height: 20px; }\n.brand strong { display: block; font-size: 1.25rem; color: var(--ink); letter-spacing: -.6px; }\n.brand span { display: block; font-size: .75rem; letter-spacing: .45px; color: var(--muted); margin-top: 3px; }\n.sidebar-label { color: #8994a5; font-size: .75rem; font-weight: 700; letter-spacing: 1.4px; margin: 0 0 .8rem .6rem; }\n.st-key-workspace_nav { gap: .45rem; }\n.st-key-workspace_nav .stButton { width: 100%; }\n.st-key-workspace_nav .stButton button { justify-content: flex-start; padding: .7rem .9rem; width: 100%; border: none; background: transparent; color: #607089; box-shadow: none; }\n.st-key-workspace_nav .stButton button[kind="primary"] { background: #edf3ff; color: #2156c7; border: none; }\n.st-key-workspace_nav .stButton button[kind="primary"] p { font-weight: 650; }\n.st-key-workspace_nav .stButton button:hover { background: #f2f5fa; color: #2156c7; transform: none; box-shadow: none; }\n.st-key-workspace_nav .stButton button[kind="primary"]:hover { background: #e5eeff; }\n[data-testid="stSidebar"] hr { margin: 1.4rem 0; border-color: var(--line); }\n[data-testid="stSidebar"] h4 { font-size: .95rem; font-weight: 650; }\n.sidebar-guide { margin-top: 2rem; padding: 1rem; border-radius: 12px; border: 1px solid #e3ebfa; background: #f7faff; color: #61738d; font-size: .8125rem; line-height: 1.7; }\n.sidebar-guide b { display: block; color: #36567e; margin-bottom: 4px; }\n.app-topline { display: flex; align-items: center; justify-content: space-between; gap: 1rem; padding-bottom: 1.25rem; border-bottom: 1px solid var(--line); color: var(--muted); font-size: .8125rem; }\n.st-key-workspace_topbar { padding-bottom: 1rem; border-bottom: 1px solid var(--line); }\n.st-key-workspace_topbar .app-topline { border-bottom: 0; padding-bottom: 0; }\n.st-key-workspace_topbar [data-testid="stPopover"] button { background: white; font-size: .8125rem; color: #5e7088; }\n.app-topline b { font-weight: 550; color: #33465e; }\n.app-topline div > span { padding: 0 .65rem; color: #b1bac9; }\n.session-chip { border: 1px solid var(--line); background: white; border-radius: 7px; padding: .4rem .75rem; white-space: nowrap; color: #63718a; font-size: .75rem; }\n.eyebrow { color: #5f7494; font-size: .75rem; font-weight: 700; letter-spacing: 1.5px; line-height: 1.7; }\n.page-heading { margin: .25rem 0 .5rem; }\n.page-heading h1 { font-size: clamp(1.65rem, 2.5vw, 2.25rem); color: var(--ink); letter-spacing: -.8px; line-height: 1.3; margin: .4rem 0 .5rem; padding: 0; }\n.page-heading p { font-size: 1rem; color: var(--muted); margin: 0; line-height: 1.7; }\n.hero-copy { padding-top: 2rem; }\n.hero-eyebrow { display: inline-block; color: #3866b5; background: #eaf1ff; border: 1px solid #dae6ff; border-radius: 6px; padding: .4rem .65rem; font-size: .75rem; letter-spacing: 1px; }\n.hero-copy h1 { color: var(--ink); font-size: clamp(2.6rem, 3.6vw, 3.7rem); font-weight: 720; letter-spacing: -1.9px; line-height: 1.21; margin: 1.35rem 0 1.2rem; padding: 0; }\n.hero-copy h1 em { color: var(--blue); font-style: normal; }\n.hero-copy p { max-width: 440px; color: var(--muted); font-size: 1rem; line-height: 1.85; margin: 0 0 .6rem; }\n.st-key-btn_hero_start button { padding: .85rem 1.4rem; min-height: 50px; font-weight: 600; box-shadow: 0 6px 16px #2563eb20; }\n.hero-support { display: flex; flex-direction: column; gap: .4rem; margin-top: .25rem; color: #728198; font-size: .75rem; }\n.st-key-landing_stage_container { padding: 1.1rem 0 1.5rem; }\n.preview-scene { background: #142743; border: 1px solid #263b56; border-radius: 20px; padding: 1.5rem; color: white; margin-top: 1.5rem; box-shadow: 0 22px 48px -20px #163b7855; position: relative; overflow: hidden; }\n.preview-scene::after { content: ""; position: absolute; width: 240px; height: 240px; right: -120px; top: -120px; border-radius: 100%; background: #2c508442; pointer-events: none; }\n.preview-heading { display: flex; flex-wrap: wrap; align-items: center; gap: .65rem; font-size: .8125rem; font-weight: 600; }\n.preview-mark { background: #2a4262; color: #96baff; border: 1px solid #3a5272; font-size: .75rem; padding: .4rem; border-radius: 7px; }\n.preview-demo { margin-left: auto; white-space: nowrap; color: #c0cee3; font-weight: 400; font-size: .75rem; background: #ffffff0b; border: 1px solid #ffffff16; border-radius: 20px; padding: .3rem .55rem; }\n.preview-metrics { display: grid; grid-template-columns: 1fr 1fr; gap: .8rem; margin: 1.25rem 0; }\n.preview-metrics > div { padding: 1rem; border-radius: 10px; background: #ffffff06; border: 1px solid #ffffff10; }\n.preview-metrics span { display: block; color: #a6b6cc; font-size: .75rem; }\n.preview-metrics strong { display: block; color: white; font-size: 1.8rem; font-weight: 600; letter-spacing: -.7px; margin: .2rem 0 .3rem; }\n.preview-metrics small { color: #acbdd4; font-size: .75rem; }\n.preview-metrics strong small { font-size: 1.1rem; margin-left: 2px; }\n.preview-metrics .preview-green { color: #83d9c1; }\n.preview-chart { border: 1px solid #ffffff10; border-radius: 10px; padding: 1rem 1rem .5rem; background: #10213a; }\n.preview-chart-title { display: flex; justify-content: space-between; gap: .5rem; font-size: .75rem; }\n.preview-chart-title b { color: #dce5f3; font-weight: 500; }\n.preview-chart-title > span { color: #92a7c4; font-size: .75rem; }\n.preview-bars { display: flex; justify-content: space-around; gap: 1rem; height: 150px; padding: 1rem .3rem 0; background: repeating-linear-gradient(to top, transparent 0px, transparent 39px, #ffffff09 40px); }\n.preview-bars > div { display: flex; flex-direction: column; justify-content: end; align-items: center; width: 25%; }\n.preview-bars i { width: 65%; max-width: 45px; height: var(--height); min-height: 12px; display: block; background: linear-gradient(#6b9cfc, #3564b8); border: 1px solid #8cb4ff50; border-radius: 5px 5px 0 0; animation: bars-in 600ms 120ms both; animation-delay: var(--delay); transform-origin: bottom; }\n.preview-bars > div:nth-child(3) i { background: linear-gradient(#71cfcd, #438f9b); border-color: #84ded555; }\n.preview-bars span { color: #a5b5ce; white-space: nowrap; font-size: .75rem; padding: .6rem 0 .2rem; }\n.preview-note { display: flex; gap: .65rem; align-items: center; padding-top: 1rem; }\n.preview-note b { color: #dce7f7; display: block; font-size: .75rem; font-weight: 550; }\n.preview-note div > span { display: block; color: #9fb2cc; font-size: .75rem; margin-top: .25rem; }\n.section-intro { padding-top: 1rem; }\n.section-intro h2 { color: var(--ink); font-size: 1.6rem; font-weight: 650; letter-spacing: -.5px; margin: .35rem 0 .5rem; padding: 0; }\n.section-intro p { color: var(--muted); font-size: .9375rem; margin: 0; }\n.feature-card { border: 1px solid var(--line); border-radius: 14px; background: white; padding: 1.5rem; min-height: 235px; box-sizing: border-box; transition: border-color 180ms, box-shadow 180ms, transform 180ms; }\n.feature-card h3 { margin: .2rem 0 .85rem; padding: 0; font-size: 1.1rem; font-weight: 650; color: #263b55; }\n.feature-card p { color: #6c7a8f; font-size: .875rem; line-height: 1.8; margin-bottom: 1.1rem; }\n.feature-detail { color: #6a788d; font-weight: 600; font-size: .75rem; letter-spacing: .2px; }\n.landing-footnote { display: flex; align-items: center; justify-content: center; gap: .65rem; color: #7b899f; font-size: .75rem; border-top: 1px solid var(--line); padding: 1.5rem 0 .5rem; margin-top: .5rem; }\n.landing-footnote b { color: #546986; font-weight: 550; }\n\n/* Clear form hierarchy: business details, objectives, then supporting actions. */\n.st-key-zone_biz_context { padding: 1.6rem; }\n.st-key-zone_biz_context > [data-testid="stVerticalBlock"] { gap: 1.3rem; }\n.context-heading h2 { font-size: 1.3rem; font-weight: 650; letter-spacing: -.3px; margin: 0 0 .45rem; padding: 0; color: #243b57; }\n.context-heading p { font-size: .9375rem; color: #718097; line-height: 1.65; margin: 0 0 .4rem; }\n.st-key-zone_biz_context [data-baseweb="input"],\n.st-key-zone_biz_context [data-baseweb="textarea"] { background: #fafbfd; border: 1px solid #dfe5ee; }\n.st-key-zone_biz_context [data-testid="stTextInput"] input,\n.st-key-zone_biz_context [data-testid="stTextArea"] textarea { background: transparent; line-height: 1.7; font-size: .9375rem; }\n.st-key-context_actions { border-top: 1px solid #edf0f5; padding-top: 1.1rem; }\n.st-key-context_actions [data-testid="stHorizontalBlock"] { align-items: center; }\n.st-key-context_actions [data-testid="stCaptionContainer"] p { font-size: .8125rem; line-height: 1.65; margin: 0; color: #7b889c; }\n.st-key-btn_ai_suggest_ctx button { background: #f5f8fd; border-color: #dbe4f2; color: #345b95; }\n.st-key-context_feedback { padding: .7rem 1rem; background: #f3f8f6; border: 1px solid #e0ebe5; border-radius: 8px; }\n.st-key-context_feedback [data-testid="stCaptionContainer"] p { color: #4d7464; margin: 0; }\n[class*="_table_toolbar"] { background: #f9fafc; border: 1px solid #e7ebf2; border-radius: 10px; padding: 1rem; }\n[class*="_table_toolbar"] [data-testid="stExpander"] { background: transparent; border: 0; }\n[class*="_table_toolbar"] [data-testid="stExpander"] summary { padding-left: 0; color: #64758d; }\n.st-key-source_options [data-testid="stHorizontalBlock"] { align-items: end; }\n.file-summary { color: #6f7d90; font-size: .8125rem; line-height: 1.6; padding: .75rem 0; overflow-wrap: anywhere; }\n\n/* A quiet left edge opens the full navigation on hover or keyboard focus. */\n@media (hover: hover) and (pointer: fine) {\n    [data-testid="stSidebar"] {\n        position: fixed !important;\n        inset: 0 auto 0 0;\n        width: 260px !important;\n        min-width: 260px !important;\n        height: 100dvh;\n        transform: translateX(-240px) !important;\n        visibility: visible !important;\n        transition: transform 220ms cubic-bezier(.2, .8, .2, 1), box-shadow 220ms;\n        z-index: 1000;\n        overflow: visible;\n        box-shadow: none;\n    }\n    [data-testid="stSidebar"]:hover,\n    [data-testid="stSidebar"]:focus-within { transform: translateX(0) !important; box-shadow: 12px 0 40px #192b4514; }\n    [data-testid="stSidebar"]::after { content: ""; position: absolute; right: 7px; top: calc(50% - 24px); width: 3px; height: 48px; border-radius: 4px; background: #becbdc; pointer-events: none; }\n    [data-testid="stSidebar"]:hover::after,\n    [data-testid="stSidebar"]:focus-within::after { opacity: 0; }\n    [data-testid="stSidebarCollapseButton"], [data-testid="stSidebarCollapsedControl"], [data-testid="stExpandSidebarButton"] { display: none; }\n    [data-testid="stMain"] { margin-left: 20px !important; width: calc(100% - 20px); }\n    [data-testid="stSidebarUserContent"] { padding-top: 2rem; }\n}\n\n/* Keep navigation, inputs and workflow actions native and keyboard accessible. */\n.st-key-top_wizard_bar { background: #fff; border: 1px solid var(--line); border-radius: 12px; padding: .5rem; }\n.st-key-top_wizard_bar button { min-height: 44px; border: 0; background: transparent; color: #70809a; font-size: .875rem; box-shadow: none; }\n.st-key-top_wizard_bar .stButton button[kind="primary"] { background: #edf3ff; color: #2156c7; border-color: transparent; }\n.st-key-top_wizard_bar button:disabled { background: #fafbfc; color: #8590a0; opacity: .8; }\n.st-key-zone_upload_left, .st-key-zone_gsheet_right, .st-key-zone_biz_context,\n.st-key-zone_step1_summary, .st-key-zone_step2_workspace, .st-key-zone_step2_audit_card,\n.st-key-zone_step3_preview, .st-key-err_preview_card, .st-key-s2_err_preview_card {\n    background: white; border: 1px solid var(--line); border-radius: 14px; padding: 1.4rem; min-width: 0;\n}\n.st-key-zone_upload_left, .st-key-zone_gsheet_right { min-height: 235px; }\n.st-key-zone_step3_preview { padding: .3rem; overflow: hidden; }\n[data-testid="stMetric"] { background: #fff; border: 1px solid var(--line); border-radius: 12px; padding: 1.1rem; }\n[data-testid="stMetricValue"] { font-weight: 650; color: #1f3657; }\n[data-testid="stAlert"] { border-radius: 10px; border: 1px solid #e1e9f4; }\n[data-testid="stExpander"] { border-radius: 10px; background: white; border-color: var(--line); }\n[data-testid="stWidgetLabel"] p { font-size: .875rem; font-weight: 550; color: #354861; }\n.stMarkdown p, .stMarkdown li { line-height: 1.7; }\n.stMarkdown h3 { font-size: 1.25rem; font-weight: 650; color: #253d5d; }\n.stMarkdown h4 { font-size: 1.05rem; font-weight: 650; color: #253d5d; }\n.stMarkdown h5 { font-size: 1rem; font-weight: 650; color: #253d5d; }\n.stButton button, .stDownloadButton button { min-height: 43px; border-radius: 9px; border-color: #dce3ee; transition: background-color 160ms, border-color 160ms, box-shadow 160ms, transform 160ms; }\n.stButton button p, .stDownloadButton button p { font-size: .875rem; }\n.stButton button[kind="primary"], .stDownloadButton button[kind="primary"] { background: #2563eb; border-color: #2563eb; color: white; }\n.stButton button[kind="primary"]:hover, .stDownloadButton button[kind="primary"]:hover { background: #1d55d2; border-color: #1d55d2; }\nbutton:focus-visible, a:focus-visible, summary:focus-visible { outline: 3px solid #729cff !important; outline-offset: 3px !important; }\n[data-baseweb="input"], [data-baseweb="select"] > div, [data-baseweb="textarea"] { border-radius: 8px; }\n.st-key-zone_step2_audit_card [data-baseweb="input"]:focus-within { outline: 2px solid #729cff !important; outline-offset: 2px; }\n[data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea { font-size: .9375rem; }\n[data-testid="stFileUploaderDropzone"] { background: #f8faff; border: 1px dashed #bdd0eb; border-radius: 10px; }\n[data-testid="stDataFrame"], [data-testid="stDataEditor"] { border-radius: 10px; overflow: hidden; }\n.st-key-floating_approve_step1, .st-key-floating_approve_step2, .st-key-floating_download_step3 { position: static; margin: .25rem 0; max-width: 100%; }\n.st-key-floating_approve_step1 button, .st-key-floating_approve_step2 button { min-height: 48px; }\n.more-groups-btn { color: #2563eb; cursor: pointer; }\n.inline-groups-details { display: inline-block; }\n.more-groups-expanded { padding: .75rem; background: #eff5ff; border: 1px solid #dbe5f6; border-radius: 8px; }\n\n@keyframes bars-in { from { transform: scaleY(.2); opacity: .3; } to { transform: scaleY(1); opacity: 1; } }\n@keyframes page-in { from { opacity: .6; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }\n.st-key-landing_stage_container, .page-heading { animation: page-in 320ms ease-out both; }\n@media (hover: hover) {\n    .feature-card:hover { transform: translateY(-3px); border-color: #c4d4ef; box-shadow: 0 10px 28px #243b6410; }\n    .stButton button:not(:disabled):active, .stDownloadButton button:active { transform: translateY(1px); }\n}\n@media (max-width: 1100px) {\n    [data-testid="stMainBlockContainer"] { padding-left: 1.5rem; padding-right: 1.5rem; }\n    .hero-copy h1 { font-size: 2.6rem; }\n    .hero-eyebrow { font-size: .75rem; letter-spacing: .5px; }\n    .preview-scene { padding: 1.1rem; }\n    .preview-demo { font-size: .75rem; padding: .25rem .4rem; }\n    .feature-card { padding: 1.1rem; min-height: 255px; }\n}\n@media (max-width: 767px) {\n    [data-testid="stMainBlockContainer"] { padding: 1.2rem 1.1rem 2rem; }\n    .app-topline { padding-top: 1rem; font-size: .75rem; }\n    .app-topline div > span { padding: 0 .3rem; }\n    .session-chip { font-size: .75rem; padding: .3rem .4rem; }\n    .hero-copy { padding-top: .5rem; }\n    .hero-copy h1 { font-size: 2.65rem; }\n    .hero-copy p { max-width: 100%; }\n    .preview-scene { margin-top: .25rem; }\n    .feature-card { min-height: auto; padding: 1.35rem; }\n    .landing-footnote { align-items: flex-start; line-height: 1.8; }\n    .st-key-top_wizard_bar [data-testid="stHorizontalBlock"] { flex-wrap: nowrap; gap: .2rem; }\n    .st-key-top_wizard_bar [data-testid="stColumn"] { min-width: 0; flex: 1 1 0; width: 33%; }\n    .st-key-top_wizard_bar button { padding: .5rem .2rem; }\n    .st-key-top_wizard_bar button p { font-size: .75rem; }\n    .st-key-zone_upload_left, .st-key-zone_gsheet_right, .st-key-zone_biz_context, .st-key-zone_step2_audit_card, .st-key-zone_step2_workspace { padding: 1rem; }\n    .st-key-source_divider { display: none; }\n}\n@media (prefers-reduced-motion: reduce) {\n    *, *::before, *::after { animation: none !important; transition: none !important; scroll-behavior: auto !important; }\n}\n'

try:
    from ui import clean_ui_text, load_styles as _ui_load_styles, markup, render_brand, render_header, render_page_title

    def load_styles():
        css_path = _UiPath(__file__).parent / "assets" / "styles.css"
        if css_path.exists():
            _ui_load_styles()
        else:
            st.markdown(f"<style>{_FALLBACK_STYLES_CSS}</style>", unsafe_allow_html=True)
except Exception:
    def clean_ui_text(value: str) -> str:
        return _ui_re.sub(r"[\U0001f000-\U0001faff\u2600-\u27bf\u2b00-\u2bff\u23f3\ufe0f\u200d]", "", str(value)).strip()

    def markup(content: str):
        st.markdown(_ui_dedent(content).strip(), unsafe_allow_html=True)

    def load_styles():
        css_path = _UiPath(__file__).parent / "assets" / "styles.css"
        css = css_path.read_text(encoding="utf-8") if css_path.exists() else _FALLBACK_STYLES_CSS
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

    def render_brand():
        markup("""
            <div class="brand"><div class="brand-symbol" aria-hidden="true"><i></i><i></i><i></i></div>
            <div><strong>Data Insight</strong><span>KHÔNG GIAN PHÂN TÍCH</span></div></div>
        """)

    def render_header(step: int, file_count: int):
        pages = ["Tổng quan", "Nhập dữ liệu", "Làm sạch dữ liệu", "Báo cáo & Dashboard"]
        markup(f"""
            <div class="app-topline"><div>Không gian làm việc <span>/</span> <b>{pages[step]}</b></div>
            <span class="session-chip">{file_count} tệp trong phiên</span></div>
        """)

    def render_page_title(eyebrow: str, title: str, description: str):
        markup(f"""
            <div class="page-heading"><span class="eyebrow">{_ui_escape(eyebrow)}</span>
            <h1>{_ui_escape(title)}</h1><p>{_ui_escape(description)}</p></div>
        """)

_W_STRETCH = {"width": "stretch"} if "width" in inspect.signature(st.button).parameters else {"use_container_width": True}
from agents.orchestrator import AgentOrchestrator
from config import COMPANY_NAME, EXPANSION_SLOTS, TOTAL_REGIONS, DEFAULT_CRITERIA, DEFAULT_GEMINI_API_KEY
from utils.column_mapper import COLUMN_SCHEMA
import utils.file_handler as _fh_mod


def _smart_read_csv_override(content: bytes):
    """Đọc CSV tự động nhận diện dấu phân cách ',', ';', '\\t', '|'chính xác từ dòng tiêu đề."""
    encodings = ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    base_seps = [',', ';', '\t', '|']
    for encoding in encodings:
        try:
            text_head = content[:8192].decode(encoding, errors='strict')
        except Exception:
            continue
        first_line = next((ln for ln in text_head.splitlines() if ln.strip()), "")
        ranked_seps = sorted(base_seps, key=lambda s: first_line.count(s), reverse=True)
        best_df = None
        for sep in ranked_seps:
            try:
                df = pd.read_csv(
                    io.BytesIO(content),
                    encoding=encoding,
                    sep=sep,
                    on_bad_lines='skip',
                    dtype=str,
                    index_col=False
                )
                if len(df.columns) > 1:
                    best_df = df
                    break
                if best_df is None and len(df.columns) == 1 and len(df) > 0:
                    best_df = df
            except Exception:
                continue
        if best_df is not None:
            for col in best_df.columns:
                try:
                    best_df[col] = pd.to_numeric(best_df[col].str.replace(',', ''))
                except Exception:
                    pass
            return best_df
    return None


_fh_mod._read_csv = _smart_read_csv_override


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
            col_list_str += f"(+{len(null_cols)-4} cột khác)"
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
_FAVICON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "favicon.svg")
st.set_page_config(
    page_title="Data Insight | Phân tích dữ liệu",
    page_icon=_FAVICON_PATH if os.path.exists(_FAVICON_PATH) else "📊",
    layout="wide",
    initial_sidebar_state="auto"
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

# Keep business context when its widgets leave the page during navigation.
for _context_key in ("biz_type", "biz_extra", "biz_questions"):
    if _context_key in st.session_state:
        st.session_state[_context_key] = st.session_state[_context_key]

def _validate_df_meaningful(df: pd.DataFrame):
    """Kiểm tra tệp có thực sự chứa dữ liệu có ý nghĩa để phân tích hay không."""
    if df is None or df.empty or len(df) == 0 or len(df.columns) == 0:
        return False, "Tệp không có dòng hoặc cột dữ liệu nào."
    non_null_vals = df.dropna(how="all")
    if non_null_vals.empty:
        return False, "Toàn bộ các ô trong tệp đều trống."
    # Kiểm tra xem toàn bộ bảng có chỉ lặp lại 1 giá trị vô nghĩa (vd: toàn 'x') hay không
    flat_vals = df.astype(str).values.ravel()
    uniq_vals = set(str(v).strip() for v in flat_vals if str(v).strip() not in ("", "nan", "None", "NaN", "NULL", "<NA>"))
    if len(uniq_vals) <= 1:
        return False, "Dữ liệu chỉ chứa 1 giá trị duy nhất lặp lại, không có thông tin để phân tích."
    num_cols = list(df.select_dtypes(include=["number"]).columns)
    has_valid_num = any(df[c].dropna().shape[0] > 0 for c in num_cols)
    # Nếu cột số đang bị lẫn ký tự lỗi/định dạng tiền tệ (khiến pandas đọc thành chuỗi) -> vẫn cho phép sang Bước 2 để làm sạch
    if not has_valid_num:
        for c in df.columns:
            s_clean = (
                df[c].dropna().astype(str).str.strip()
                .str.replace(r"[,\s₫đ$%€£¥VNDvnd]", "", regex=True)
            )
            s_num = pd.to_numeric(s_clean, errors="coerce").dropna()
            if len(s_num) > 0:
                has_valid_num = True
                break
    if not has_valid_num:
        return False, "Tệp không có cột số liệu định lượng nào (chỉ chứa chữ)."
    # Kiểm tra dữ liệu giả/tạo tự động kiểu chỉ có 1 cột mã ERR-xxxxx + 1 cột dãy số thứ tự 0, 1, 2...
    if len(df) >= 100 and len(df.columns) == 2 and len(num_cols) == 1:
        non_num_cols = [c for c in df.columns if c not in num_cols]
        s_num_col = df[num_cols[0]].dropna()
        is_seq_idx = len(s_num_col) > 10 and s_num_col.iloc[0] in (0, 1) and (s_num_col.diff().dropna() == 1).all()
        all_text_unique = all(df[c].nunique(dropna=True) >= len(df) for c in non_num_cols)
        if is_seq_idx and all_text_unique:
            return False, "Dữ liệu chỉ gồm mã định danh tuần tự và dãy số thứ tự 0, 1, 2..., không có nhóm phân loại hoặc biến động thực tế để phân tích."
    return True, ""


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
# CHỈ ÁP DỤNG GIAO DIỆN KHÔNG GIAN LÀM VIỆC (SIDEBAR, TOPBAR, WIZARD) Ở BƯỚC 1, 2, 3
# TRANG MỞ ĐẦU (BƯỚC 0) ĐƯỢC GIỮ NGUYÊN 100%
# ============================================================
if step != 0:
    load_styles()

    with st.container(key="workspace_topbar"):
        header_area, settings_area = st.columns([5, 1.1], vertical_alignment="center")
        with header_area:
            render_header(step, len(orch.data_agent.raw_dataframes))
        with settings_area:
            settings_panel = st.popover("Cài đặt AI", **_W_STRETCH)
    with st.container(key="top_wizard_bar"):
        nav_col1, nav_col2, nav_col3 = st.columns([1, 1, 1])

        with nav_col1:
            is_active_1 = (step == 1)
            b1_label = "1  Nhập dữ liệu"
            if st.button(
                b1_label,
                key="top_nav_step1",
                **_W_STRETCH,
                type="primary" if is_active_1 else "secondary"
            ):
                set_spinner_msg("Đang chuyển sang Bước 1: Nhập dữ liệu...")
                st.session_state.current_step = 1
                st.rerun()

        with nav_col2:
            is_active_2 = (step == 2)
            b2_label = "2  Làm sạch"
            if st.button(
                b2_label,
                key="top_nav_step2",
                disabled=not st.session_state.step1_approved,
                help="Duyệt dữ liệu ở bước 1 để tiếp tục." if not st.session_state.step1_approved else "Mở bước làm sạch dữ liệu",
                **_W_STRETCH,
                type="primary" if is_active_2 else "secondary"
            ):
                if st.session_state.step1_approved:
                    set_spinner_msg("Đang mở Bước 2: Làm sạch...")
                    st.session_state.current_step = 2
                    st.rerun()
                else:
                    st.toast("Vui lòng nạp file và duyệt Bước 1 trước!")

        with nav_col3:
            is_active_3 = (step == 3)
            b3_label = "3  Tạo báo cáo"
            if st.button(
                b3_label,
                key="top_nav_step3",
                disabled=not st.session_state.step2_approved,
                help="Duyệt dữ liệu ở bước 2 để tạo báo cáo." if not st.session_state.step2_approved else "Mở báo cáo",
                **_W_STRETCH,
                type="primary" if is_active_3 else "secondary"
            ):
                if st.session_state.step2_approved:
                    set_spinner_msg("Đang mở Bước 3: Tạo báo cáo...")
                    st.session_state.current_step = 3
                    st.rerun()
                else:
                    st.toast("Vui lòng duyệt Bước 2 trước khi sang Bước 3!")

    # Điều hướng và cài đặt luôn truy cập được ở thanh bên.
    _sb_cur = st.session_state.current_step
    with st.sidebar:
        render_brand()
        markup('<div class="sidebar-label">KHÔNG GIAN LÀM VIỆC</div>')
        with st.container(key="workspace_nav"):
            if st.button("Tổng quan", type="primary" if _sb_cur == 0 else "secondary", key="sb_nav_0", **_W_STRETCH):
                set_spinner_msg("Đang quay lại Trang Mở Đầu...")
                st.session_state.current_step = 0
                st.rerun()

            if st.button("Nhập dữ liệu", type="primary" if _sb_cur == 1 else "secondary", key="sb_nav_1", **_W_STRETCH):
                set_spinner_msg("Đang chuyển sang Bước 1: Nhập Dữ Liệu...")
                st.session_state.current_step = 1
                st.rerun()

            if st.button("Làm sạch dữ liệu", type="primary" if _sb_cur == 2 else "secondary", key="sb_nav_2", **_W_STRETCH):
                if st.session_state.step1_approved:
                    set_spinner_msg("Đang mở Bước 2: Làm Sạch...")
                    st.session_state.current_step = 2
                    st.rerun()
                else:
                    st.toast("Vui lòng nạp file và Duyệt Bước 1 trước!")

            if st.button("Báo cáo & Dashboard", type="primary" if _sb_cur == 3 else "secondary", key="sb_nav_3", **_W_STRETCH):
                if st.session_state.step2_approved:
                    set_spinner_msg("Đang mở Bước 3: Tạo Báo Cáo...")
                    st.session_state.current_step = 3
                    st.rerun()
                else:
                    st.toast("Vui lòng Duyệt Bước 2 trước!")

            st.divider()

            if st.button("Làm mới phiên", key="sb_reset_session", **_W_STRETCH):
                for k in ["files_loaded", "file_messages", "analysis_results", "editable_report", "editable_plan", "dashboard_scores_df"]:
                    if k in st.session_state:
                        st.session_state[k] = [] if k in ["files_loaded", "file_messages"] else None
                st.session_state.step1_approved = False
                st.session_state.step2_approved = False
                st.session_state.step3_approved = False
                st.session_state.show_step2_audit_log = False
                st.session_state.show_step2_editor = False
                st.session_state.s1_issues_dismissed = set()
                st.session_state["_detect_issues_cache"] = {}
                st.session_state.pop("_last_uploaded_sig", None)
                st.session_state.pop("_last_step3_data_sig", None)
                st.session_state.current_step = 0
                orch.data_agent.raw_dataframes.clear()
                set_spinner_msg("Đang làm mới toàn bộ phiên làm việc...")
                st.rerun()

    with settings_panel:
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
        st.caption("Đã cấu hình mô hình AI" if st.session_state.api_key_set else "Thêm API Key để sử dụng AI")

        # Khu vực Cài Đặt API Key được ẩn gọn, bấm vào mới hiện
        with st.expander("Cài đặt API", expanded=False):
            st.markdown("####  Kết nối AI Agent")
            api_key_input = st.text_input(
                "Gemini API Key",
                type="password",
                value=DEFAULT_GEMINI_API_KEY,
                help="Đã tích hợp sẵn API Key tự động"
            )
            if st.button("Cập nhật API Key", **_W_STRETCH):
                if api_key_input:
                    try:
                        success, msg = orch.initialize_ai(api_key_input, model_name=st.session_state.selected_ai_model)
                    except TypeError:
                        success, msg = orch.initialize_ai(api_key_input)
                    if success:
                        st.session_state.api_key_set = True
                        st.success(f"Kết nối thành công ({st.session_state.selected_ai_model})!")
                    else:
                        st.error(clean_ui_text(msg))

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
        return "Không thể chuyển đổi một số ô văn bản sang kiểu số. Hệ thống đã giữ nguyên giá trị văn bản gốc."
    if "429" in msg or "quota" in msg.lower() or "ResourceExhausted" in msg:
        return "Hệ thống AI đang quá tải hoặc hết hạn mức truy cập tạm thời. Hệ thống đã tự động dùng bộ phân tích dự phòng."
    if "404" in msg:
        return "Không tìm thấy tài nguyên hoặc liên kết Google Sheet. Vui lòng kiểm tra lại đường dẫn."
    if "403" in msg or "permission" in msg.lower():
        return "Không có quyền truy cập tệp hoặc Google Sheet chưa bật chế độ chia sẻ công khai."
    if "API_KEY" in msg.upper() or "api key" in msg.lower():
        return "Mã kết nối AI (API Key) chưa hợp lệ. Vui lòng kiểm tra lại trong mục Cài đặt AI ở đầu trang."
    if "ParserError" in msg or "tokenizing" in msg:
        return "Định dạng tệp dữ liệu có dòng bị lệch cột. Vui lòng kiểm tra lại tệp CSV/Excel."
    return f"Hệ thống gặp sự cố nhỏ khi xử lý thao tác vừa rồi ({type(exc).__name__}: {msg[:150]}). Vui lòng kiểm tra lại dữ liệu hoặc thử lại."

def _render_excel_filter_toolbar(df_cur: pd.DataFrame, key_prefix: str):
    """Thanh công cụ lọc nhiều cột, tìm kiếm, sắp xếp và chọn cột hiển thị kiểu Excel."""
    with st.container(key=f"{key_prefix}_table_toolbar"):
        col_search, col_sort, col_order = st.columns([2.2, 1.3, 1], gap="medium")
        with col_search:
            f_search = st.text_input("Tìm trong bảng", placeholder="Nhập từ khóa...", key=f"{key_prefix}_search")
        with col_sort:
            f_sort_col = st.selectbox("Sắp xếp theo", ["(Mặc định)"] + list(df_cur.columns), key=f"{key_prefix}_scol")
        with col_order:
            f_sort_asc = st.selectbox("Thứ tự", ["Tăng dần", "Giảm dần"], key=f"{key_prefix}_sasc")

        with st.expander("Bộ lọc và cột hiển thị", expanded=False):
            filter_col, visible_col = st.columns(2, gap="medium")
            with filter_col:
                f_cols = st.multiselect("Lọc theo cột", list(df_cur.columns), default=[], key=f"{key_prefix}_fcols")
            with visible_col:
                show_cols = st.multiselect(
                    "Cột hiển thị", list(df_cur.columns), default=[],
                    placeholder="Tất cả các cột", key=f"{key_prefix}_cols"
                )

            active_filters = {}
            if f_cols:
                f_cols_ui = st.columns(min(len(f_cols), 3))
                for idx_fc, fcol in enumerate(f_cols):
                    with f_cols_ui[idx_fc % 3]:
                        uniq_vals = sorted(df_cur[fcol].dropna().astype(str).unique().tolist())[:300]
                        picked_vals = st.multiselect(f"Giá trị `{fcol}`", uniq_vals, key=f"{key_prefix}_fval_{fcol}")
                        if picked_vals:
                            active_filters[fcol] = picked_vals

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
        st.caption(f"Đang hiển thị **{len(view_df):,} / {len(df_cur):,}** dòng phù hợp.")
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
            with st.spinner(clean_ui_text(st.session_state.pending_spinner_msg)):
                import time
                time.sleep(0.15)
            st.session_state.pending_spinner_msg = ""

        with st.container(key="landing_stage_container"):
            st.markdown("""
            <style>
                header[data-testid="stHeader"] {
                    background: transparent !important;
                }
                .main, [data-testid="stMain"], [data-testid="stAppViewContainer"] {
                    margin-left: 0 !important;
                    width: 100% !important;
                    background: radial-gradient(circle at 12% 18%, rgba(147, 197, 253, 0.55) 0%, transparent 45%),
                                radial-gradient(circle at 85% 22%, rgba(96, 165, 250, 0.42) 0%, transparent 48%),
                                radial-gradient(circle at 52% 85%, rgba(186, 230, 253, 0.65) 0%, transparent 50%),
                                linear-gradient(135deg, #eff6ff 0%, #dbeafe 52%, #e0f2fe 100%) !important;
                }
                section[data-testid="stSidebar"], [data-testid="stSidebar"] {
                    display: none !important;
                }
                .st-key-landing_stage_container {
                    padding: 0 !important;
                    animation: none !important;
                }
                .main .block-container, [data-testid="stMainBlockContainer"] {
                    padding: 0.35rem 0 0 0 !important;
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
<body class="text-slate-800 h-[585px] flex flex-col justify-between relative overflow-hidden" style="background: radial-gradient(circle at 12% 18%, rgba(147, 197, 253, 0.55) 0%, transparent 45%), radial-gradient(circle at 85% 22%, rgba(96, 165, 250, 0.42) 0%, transparent 48%), radial-gradient(circle at 52% 85%, rgba(186, 230, 253, 0.65) 0%, transparent 50%), linear-gradient(135deg, #eff6ff 0%, #dbeafe 52%, #e0f2fe 100%);">

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

            <h1 class="text-4xl md:text-[2.75rem] font-extrabold text-slate-900 leading-[1.18] tracking-tight min-h-[6.5rem]">
                <span id="tw-line1"></span><br>
                <span id="tw-line2" class="text-slate-900"></span><span id="tw-caret" style="display:inline-block; width:3px; height:0.9em; background:#2563eb; margin-left:4px; vertical-align:middle; animation: twBlink 0.75s step-end infinite;"></span>
            </h1>
            <style>
                @keyframes twBlink { 50% { opacity: 0; } }
            </style>
            <script>
                (function() {
                    const l1 = "Dữ liệu thông minh";
                    const l2 = "Báo cáo tức thì";
                    const el1 = document.getElementById("tw-line1");
                    const el2 = document.getElementById("tw-line2");
                    let i = 0, j = 0;
                    function typeL1() {
                        if (i <= l1.length) {
                            el1.textContent = l1.slice(0, i++);
                            setTimeout(typeL1, 45);
                        } else {
                            setTimeout(typeL2, 120);
                        }
                    }
                    function typeL2() {
                        if (j <= l2.length) {
                            el2.textContent = l2.slice(0, j++);
                            setTimeout(typeL2, 45);
                        }
                    }
                    typeL1();
                })();
            </script>

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
        <div class="w-full md:w-[55%] relative h-[350px] flex items-center justify-center">
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
            _landing_comp.html(_landing_html, height=585, scrolling=False)

    # ============================================================
    # BƯỚC 1: NHẬP DỮ LIỆU (CSV / EXCEL / GOOGLE SHEET)
    # ============================================================
    elif st.session_state.current_step == 1:
        if st.session_state.pending_spinner_msg:
            with st.spinner(clean_ui_text(st.session_state.pending_spinner_msg)):
                import time
                time.sleep(0.15)
            st.session_state.pending_spinner_msg = ""

        if "show_step1_uploader" not in st.session_state:
            st.session_state.show_step1_uploader = False

        has_loaded_files = bool(orch.data_agent.raw_dataframes)
        render_page_title(
            "BƯỚC 1 / 3 · KẾT NỐI",
            "Dữ liệu tốt, khởi đầu tốt.",
            "Tải tệp hoặc kết nối Google Sheets. Xem lại dữ liệu và bổ sung bối cảnh trước khi tiếp tục."
        )
        if has_loaded_files:
            btn_lbl = "Đóng khung nạp dữ liệu" if st.session_state.show_step1_uploader else "Nạp thêm tệp / Google Sheet"
            if st.button(btn_lbl, key="btn_toggle_s1_uploader"):
                st.session_state.pop("_last_uploaded_sig", None)
                st.session_state.show_step1_uploader = not st.session_state.show_step1_uploader
                st.rerun()

        if (not has_loaded_files) or st.session_state.show_step1_uploader:
            col_up1, col_divider, col_up2 = st.columns([1, 0.1, 1])
    
            with col_up1:
                with st.container(key="zone_upload_left"):
                    st.markdown("""
                    <div style="display:flex; align-items:center; gap:8px; margin-bottom:4px;">
                        <span style="font-weight:800; color:#2563eb; font-size:1.05rem;">Tải tệp</span>
                    </div>
                    <div class="gsheet-hint-text" style="font-size:0.9rem; color:#63718a; margin-bottom:12px; line-height:1.6;">
                        Chọn một hoặc nhiều tệp CSV, TSV, XLSX, XLS.
                    </div>
                    """, unsafe_allow_html=True)
                    with st.container(key="step1_file_inner_box"):
                        uploaded_files = st.file_uploader(
                            "Chọn file CSV, TSV, Excel...",
                            type=["csv", "tsv", "xlsx", "xls"],
                            accept_multiple_files=True,
                            label_visibility="collapsed",
                            key="s1_file_uploader"
                        )
                    if uploaded_files:
                        _up_sig = tuple((getattr(u, "file_id", u.name), u.name, getattr(u, "size", 0)) for u in uploaded_files)
                        if st.session_state.get("_last_uploaded_sig") != _up_sig:
                            with st.spinner("Đang đọc và kiểm tra chất lượng dữ liệu..."):
                                for up in uploaded_files:
                                    content = up.getvalue()
                                    if up.name.lower().endswith(".tsv"):
                                        # Đảm bảo đọc được .tsv ngay cả khi file_handler cũ chưa cập nhật .tsv
                                        success, msg = orch.load_file(content, up.name[:-4] + ".csv")
                                        if success and (up.name[:-4] + ".csv") in orch.data_agent.raw_dataframes:
                                            orch.data_agent.raw_dataframes[up.name] = orch.data_agent.raw_dataframes.pop(up.name[:-4] + ".csv")
                                            if (up.name[:-4] + ".csv") in orch.data_agent.file_infos:
                                                orch.data_agent.file_infos[up.name] = orch.data_agent.file_infos.pop(up.name[:-4] + ".csv")
                                            if (up.name[:-4] + ".csv") in orch.data_agent.column_mappings:
                                                orch.data_agent.column_mappings[up.name] = orch.data_agent.column_mappings.pop(up.name[:-4] + ".csv")
                                    else:
                                        success, msg = orch.load_file(content, up.name)
                                    st.session_state.file_messages.append({"file": up.name, "success": success, "msg": msg})
                                    if success:
                                        if up.name in orch.data_agent.raw_dataframes:
                                            orch.data_agent.file_infos.setdefault(up.name, {})["original_df"] = orch.data_agent.raw_dataframes[up.name].copy()
                                        if up.name not in st.session_state.files_loaded:
                                            st.session_state.files_loaded.append(up.name)
                                st.session_state._last_uploaded_sig = _up_sig
                                st.session_state.show_step1_uploader = False
                            st.rerun()

            with col_divider, st.container(key="source_divider"):
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
                        <span style="font-weight:800; color:#2563eb; font-size:1.05rem;">Đường dẫn Google Sheet</span>
                    </div>
                    <div class="gsheet-hint-text" style="font-size:0.9rem; color:#63718a; margin-bottom:12px; line-height:1.6;">
                        Dán liên kết bảng tính đã bật quyền xem công khai.
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
                        if st.button("Kết nối & Kiểm tra Google Sheet", type="primary", **_W_STRETCH, key="btn_verify_gsheet"):
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
            _has_any_err_s1 = any(
                (not it["success"]) or bool(detect_data_issues(orch.data_agent.raw_dataframes.get(it["file"]), it["file"]))
                for it in st.session_state.file_messages[-6:]
            )
            if _has_any_err_s1:
                st.markdown(f"####  Chi tiết kiểm tra & Phê duyệt xử lý lỗi ({len(st.session_state.file_messages)} tệp)")
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

                            _is_ok_df, _err_reason_df = _validate_df_meaningful(df_chk)
                            if not _is_ok_df:
                                st.error(
                                    f"**Tệp `{item['file']}` không đủ dữ liệu có ý nghĩa để phân tích:** {_err_reason_df} "
                                    f"Vui lòng nạp tệp khác có dữ liệu thực tế."
                                )
                            elif detected_issues:
                                _short_err_lines = "\n".join(
                                    f"- **{iss['type']}:** {iss['count']:,} {'dòng' if 'trùng' in iss['type'].lower() or 'dòng' in iss['type'].lower() else 'ô'}"
                                    for iss in detected_issues
                                )
                                st.warning(
                                    f"**Phát hiện {len(detected_issues)} nhóm lỗi trong tệp `{item['file']}`:**\n\n"
                                    f"{_short_err_lines}"
                                )
                            else:
                                if has_backup and user_logs_s1:
                                    with st.expander(f"Nhật ký các mục bạn đã duyệt sửa trên `{item['file']}` ({len(user_logs_s1)} thao tác)", expanded=False):
                                        for u_l in user_logs_s1:
                                            st.markdown(f"- {clean_ui_text(u_l)}")
                                        if st.button("Hoàn tác & Khôi phục dữ liệu gốc ban đầu", key=f"btn_undo_clean_s1_{item['file']}"):
                                            orig_copy = f_info_item["original_df"].copy()
                                            orch.data_agent.raw_dataframes[item["file"]] = orig_copy
                                            f_info_item["rows"] = len(orig_copy)
                                            f_info_item["user_action_log"] = []
                                            st.session_state["_detect_issues_cache"] = {}
                                            st.rerun()
                            
                            if (not detected_issues) and _is_ok_df:
                                cache_key = f"v2_{item['file']}_{len(df_chk)}_{len(df_chk.columns)}"
                                if cache_key not in st.session_state.step1_ai_summaries:
                                    rev_cols = [c for c in df_chk.columns if any(k in str(c).lower() for k in ["revenue", "doanh_thu", "doanhthu", "sales", "amount", "profit", "loi_nhuan"])]
                                    biz_parts = [f"- **Tình trạng dữ liệu:** Tệp sạch, không phát hiện ô trống hay dòng trùng lặp."]
                                    if rev_cols:
                                        rc = rev_cols[0]
                                        s_val = pd.to_numeric(df_chk[rc], errors="coerce").dropna()
                                        if len(s_val) > 0:
                                            biz_parts.append(f"- **Tình hình kinh doanh:** Chỉ số `{rc}` đạt tổng **{s_val.sum():,.0f}** (trung bình **{s_val.mean():,.1f}**/giao dịch).")
                                    biz_parts.append("- **Đánh giá chung:** Dữ liệu đã sẵn sàng để tổng hợp báo cáo và Dashboard ở Bước 3.")
                                    st.session_state.step1_ai_summaries[cache_key] = "\n".join(biz_parts)
                                st.info(f"**Nhận xét nhanh về `{item['file']}`:**\n\n{st.session_state.step1_ai_summaries[cache_key]}")
                    else:
                        st.error(f"**Lỗi đọc tệp '{item['file']}':** {clean_ui_text(item['msg'])}\n\n* Hướng dẫn khắc phục: Kiểm tra xem tệp có đang mở hoặc bị khóa bởi phần mềm khác không, hoặc lưu lại tệp dưới định dạng chuẩn CSV (UTF-8) / Excel (.xlsx).*")

        with st.container(key="zone_biz_context"):
            markup('<div class="context-heading"><h2>Bối cảnh doanh nghiệp</h2><p>Thêm thông tin để báo cáo tập trung vào điều bạn cần biết.</p></div>')
            col_ctx1, col_ctx2 = st.columns([1, 1.6], gap="large")
            with col_ctx1:
                st.text_input(
                    "Lĩnh vực hoạt động",
                    placeholder="Ví dụ: Bán lẻ, thương mại điện tử, logistics",
                    key="biz_type"
                )
                st.text_area(
                    "Thông tin bổ sung",
                    placeholder="Mô tả hoạt động, phạm vi dữ liệu hoặc những điểm cần lưu ý...",
                    height=156,
                    key="biz_extra"
                )
            with col_ctx2:
                st.text_area(
                    "Mục tiêu phân tích",
                    placeholder="Bạn muốn tìm hiểu điều gì từ dữ liệu?\nVí dụ: Khu vực nào đang tăng trưởng tốt? Chỉ số nào cần cải thiện?",
                    height=251,
                    key="biz_questions"
                )

            with st.container(key="context_actions"):
                ctx_action, ctx_help = st.columns([1.1, 2.5], gap="medium")
                with ctx_action:
                    if st.button("Gợi ý từ dữ liệu", key="btn_ai_suggest_ctx", **_W_STRETCH, disabled=not has_loaded_files):
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
                            st.session_state["_ai_ctx_done_msg"] = f"Đã điền gợi ý từ `{first_fname}` gồm lĩnh vực và {len(q_list)} câu hỏi. Bạn có thể điều chỉnh trước khi tiếp tục."
                            st.rerun()
                        else:
                            st.warning("Bạn chưa nạp tệp dữ liệu nào! Vui lòng tải tệp CSV/Excel hoặc dán link Google Sheet ở khung phía trên trước khi bấm gợi ý AI.")

                with ctx_help:
                    st.caption("Tạo gợi ý cho lĩnh vực và mục tiêu từ tệp đã nạp. Bạn có thể chỉnh sửa nội dung sau đó.")

            if st.session_state.get("_ai_ctx_done_msg"):
                with st.container(key="context_feedback"):
                    st.caption(clean_ui_text(st.session_state.pop("_ai_ctx_done_msg")))

        if orch.data_agent.raw_dataframes:
            _invalid_files_s1 = []
            _has_num_s1 = False
            for _fn_s1, _df_s1 in orch.data_agent.raw_dataframes.items():
                if _df_s1 is not None and not _df_s1.empty:
                    _ok_s1, _reason_s1 = _validate_df_meaningful(_df_s1)
                    if _ok_s1:
                        _has_num_s1 = True
                    else:
                        _invalid_files_s1.append((_fn_s1, _reason_s1))
            if not _has_num_s1 and _invalid_files_s1:
                _reasons_str = "; ".join(f"`{fn}` ({rs})" for fn, rs in _invalid_files_s1)
                st.error(f"**Chưa đủ điều kiện sang Bước 2:** {_reasons_str} Vui lòng tải lên tệp dữ liệu hợp lệ.")
            with st.container(key="floating_approve_step1"):
                if st.button("Duyệt dữ liệu & tiếp tục làm sạch", type="primary", **_W_STRETCH, key="btn_approve_step1", disabled=(not _has_num_s1)):
                    set_spinner_msg("Đang chuyển sang Bước 2: Làm sạch & Kiểm tra dữ liệu...")
                    st.session_state.step1_approved = True
                    st.session_state.current_step = 2
                    st.rerun()

        if orch.data_agent.raw_dataframes:
            st.markdown("#### Xem và chỉnh sửa dữ liệu")
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
                    s1_edited = st.data_editor(s1_slice, **_W_STRETCH, num_rows="dynamic", height=500, key=f"s1_editor_{s1_chosen_file}")
                else:
                    s1_slice = s1_view_df[display_cols]
                    s1_edited = st.data_editor(s1_slice, **_W_STRETCH, num_rows="dynamic", height=440, key=f"s1_editor_{s1_chosen_file}")

                col_s1_save, col_s1_apply_filter, _ = st.columns([1.3, 1.5, 2.2])
                with col_s1_save:
                    if st.button("Lưu sửa nhanh", type="primary", **_W_STRETCH, key="btn_save_step1"):
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
                                st.session_state["_detect_issues_cache"] = {}
                            st.rerun()
                        except Exception:
                            st.error("Không thể lưu thay đổi. Vui lòng kiểm tra định dạng dữ liệu vừa nhập.")
                with col_s1_apply_filter:
                    if s1_is_filtered:
                        if st.button("Chỉ giữ các dòng đang lọc", **_W_STRETCH, key="btn_keep_filtered_step1"):
                            orch.data_agent.raw_dataframes[s1_chosen_file] = s1_view_df.reset_index(drop=True)
                            st.session_state["_detect_issues_cache"] = {}
                            st.toast(f"Đã lọc giữ lại {len(s1_view_df):,} dòng!")
                            st.rerun()

    # ============================================================
    # BƯỚC 2: XEM TRẠNG THÁI LÀM SẠCH & CHỈNH SỬA DỮ LIỆU
    # ============================================================
    elif st.session_state.current_step == 2:
        if st.session_state.pending_spinner_msg:
            with st.spinner(clean_ui_text(st.session_state.pending_spinner_msg)):
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
            render_page_title(
                "BƯỚC 2 / 3 · CHUẨN HÓA",
                "Sạch dữ liệu, rõ góc nhìn.",
                "Kiểm tra vấn đề, chọn cách xử lý và duyệt thay đổi. Bạn có thể xem trước hoặc khôi phục dữ liệu gốc."
            )

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
                    label="Tải CSV đã làm sạch",
                    data=csv_clean_bytes,
                    file_name=f"Cleaned_{selected_file}.csv",
                    mime="text/csv",
                    **_W_STRETCH,
                    key=f"dl_cleaned_csv_s2_{selected_file}"
                )

            if total_records > 0:
                with st.container(key="floating_approve_step2"):
                    if st.button("Duyệt dữ liệu & tạo báo cáo", type="primary", **_W_STRETCH, key="btn_approve_step2"):
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

            if not s2_issues:
                st.write("")
                lbl_s2_btn = "Đóng bảng chỉnh sửa" if st.session_state.show_step2_editor else "Chỉnh sửa dữ liệu"
                if st.button(lbl_s2_btn, **_W_STRETCH, key="btn_toggle_s2_editor"):
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
                    num_cols_str = ", ".join(f"`{c}`" for c in num_cols[:8]) + (f"(+{len(num_cols)-8} cột)" if len(num_cols) > 8 else "")
                    txt_cols_str = ", ".join(f"`{c}`" for c in txt_cols[:6]) + (f"(+{len(txt_cols)-6} cột)" if len(txt_cols) > 6 else "")
                    mapped_str = ", ".join(f"`{k}`" for k in list(mapped_dict.keys())[:8]) + (f"(+{len(mapped_dict)-8})" if len(mapped_dict) > 8 else "")

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
                                    if st.button(f"Chọn tất cả ({len(all_s2_ids)})", **_W_STRETCH, key=f"btn_sel_all_s2_{selected_file}"):
                                        st.session_state[f"{s2_issue_key_prefix}_selected"] = list(all_s2_ids)
                                        for iid in all_s2_ids:
                                            st.session_state[f"chk_s2_{selected_file}_{iid}"] = True
                                        st.rerun()
                                else:
                                    if st.button(f"Bỏ chọn tất cả ({len(all_s2_ids)})", **_W_STRETCH, key=f"btn_unsel_all_s2_{selected_file}"):
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
                                    "0 3px 12px rgba(37, 99, 235, 0.05)"
                                    if is_selected_card else
                                    "none"
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
                                        transition: border-color 0.16s ease;
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
                                    c_top_left, c_top_badge = st.columns([5.65, 1.35])
                                    with c_top_left:
                                        is_checked = st.checkbox(
                                            f"{s2_iss['type']} · {s2_iss['count']:,} {unit_lbl}",
                                            value=is_selected_card,
                                            key=f"chk_s2_{selected_file}_{s2_iss['id']}"
                                        )
                                        if is_checked and s2_iss["id"] not in st.session_state[f"{s2_issue_key_prefix}_selected"]:
                                            st.session_state[f"{s2_issue_key_prefix}_selected"].append(s2_iss["id"])
                                        elif not is_checked and s2_iss["id"] in st.session_state[f"{s2_issue_key_prefix}_selected"]:
                                            st.session_state[f"{s2_issue_key_prefix}_selected"].remove(s2_iss["id"])
                                    with c_top_badge:
                                        st.markdown(
                                            f"<div style='display:flex; justify-content:flex-end;'>"
                                            f"<span style='display:inline-flex; align-items:center; gap:5px; background:{sev_bg}; color:{sev_fg}; border:1px solid {sev_bd}; font-size:0.74rem; font-weight:700; padding:2px 10px; border-radius:999px; white-space:nowrap;'>"
                                            f"<span style='width:6px; height:6px; border-radius:50%; background:{sev_dot}; display:inline-block;'></span>{sev_label}</span></div>",
                                            unsafe_allow_html=True
                                        )

                                    st.markdown(
                                        f"<div style='margin:2px 0 8px 0; font-size:0.86rem; color:#334155; line-height:1.45;'>"
                                        f"{clean_desc}</div>",
                                        unsafe_allow_html=True
                                    )

                                    sug_box_key = f"s2_sug_box_{idx_s2i}"
                                    st.markdown(f"""
                                    <style>
                                        .st-key-{sug_box_key} {{
                                            background: {sug_bg} !important;
                                            border: 1px solid #cbd5e1 !important;
                                            border-radius: 10px !important;
                                            padding: 6px 12px 4px 12px !important;
                                        }}
                                        .st-key-{sug_box_key} div[data-testid="stTextInput"] > div,
                                        .st-key-{sug_box_key} div[data-testid="stTextInput"] > div > div,
                                        .st-key-{sug_box_key} div[data-testid="stTextInput"] > div > div > div,
                                        .st-key-{sug_box_key} div[data-baseweb="input"],
                                        .st-key-{sug_box_key} div[data-baseweb="base-input"],
                                        .st-key-{sug_box_key} input {{
                                            background: transparent !important;
                                            border: none !important;
                                            box-shadow: none !important;
                                            outline: none !important;
                                        }}
                                        .st-key-{sug_box_key} div[data-testid="stTextInput"] label {{
                                            font-size: 0.78rem !important;
                                            font-weight: 700 !important;
                                            color: #1e3a8a !important;
                                            margin-bottom: 0 !important;
                                        }}
                                        .st-key-{sug_box_key} input {{
                                            padding: 2px 0 !important;
                                            height: 28px !important;
                                        }}
                                    </style>
                                    """, unsafe_allow_html=True)
                                    with st.container(key=sug_box_key):
                                        s2_custom_txt = st.text_input(
                                            "Cách xử lý đề xuất",
                                            value=st.session_state.get(f"instr_s2_{selected_file}_{s2_iss['id']}", s2_iss["suggested_fix"]),
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
                                                <div style="color:#0f172a;"><b class="s2-subhead-lg">Xem trước các dòng dữ liệu có lỗi</b> <span style="color:#64748b;">· {len(s2_err_preview)} dòng mẫu</span></div>
                                                <div style="font-size:0.8rem; color:#64748b; margin-top:1px;">Đối chiếu trực tiếp các ô bị khuyết, số âm và chuỗi dư khoảng trắng trước khi sửa</div>
                                            </div>
                                        </div>
                                        """, unsafe_allow_html=True)
                                    with pv_c2:
                                        pv_lbl = "Thu gọn" if st.session_state[s2_pv_key] else "Xem dữ liệu"
                                        if st.button(pv_lbl, **_W_STRETCH, key="btn_toggle_pv_s2"):
                                            st.session_state[s2_pv_key] = not st.session_state[s2_pv_key]
                                            st.rerun()
                                    if st.session_state[s2_pv_key]:
                                        st.dataframe(s2_err_preview, **_W_STRETCH, height=460)

                            st.write("")
                            _, col_s2_btn_apply, _ = st.columns([1.3, 1.4, 1.3])
                            with col_s2_btn_apply:
                                btn_s2_fix_label = f"Duyệt & Sửa ngay ({len(s2_chosen_fixes)} mục đã chọn)" if s2_chosen_fixes else "Chưa chọn mục nào để sửa"
                                if st.button(btn_s2_fix_label, type="primary", **_W_STRETCH, key=f"btn_apply_fixes_s2_{selected_file}", disabled=(not s2_chosen_fixes)):
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
                                        st.session_state["_detect_issues_cache"] = {}
                                        st.toast(f"Đã xử lý xong các lỗi trên {selected_file}!")
                                    st.rerun()
                            if has_s2_backup and user_edits:
                                _, col_undo_mid, _ = st.columns([1.3, 1.4, 1.3])
                                with col_undo_mid:
                                    if st.button("Khôi phục bản gốc", **_W_STRETCH, key=f"btn_undo_s2_{selected_file}"):
                                        orig_copy = file_info_cur["original_df"].copy()
                                        orch.data_agent.raw_dataframes[selected_file] = orig_copy
                                        file_info_cur["rows"] = len(orig_copy)
                                        file_info_cur["user_action_log"] = []
                                        st.session_state["_detect_issues_cache"] = {}
                                        st.toast(f"Đã khôi phục tệp {selected_file} về dữ liệu gốc ban đầu.")
                                        st.rerun()

                        details = [f"**Nhật ký kiểm tra & cấu trúc tệp `{selected_file}`:**"]
                        details.append(f"-  **Quy mô hiện tại:** **{len(df_current):,} dòng × {len(df_current.columns)} cột**.")
                        details.append(f"-  **Cột số ({len(num_cols)} cột):** {num_cols_str if num_cols else 'Không có'}.")
                        details.append(f"-  **Cột phân loại / văn bản ({len(txt_cols)} cột):** {txt_cols_str if txt_cols else 'Không có'}.")
                        details.append(f"-  **Chuẩn hóa tên cột ({len(mapped_dict)} cột):** {mapped_str if mapped_dict else 'Tự động nhận diện'}.")
                        for u_log in user_edits:
                            details.append(f"-  **Đã phê duyệt & thực thi:** {u_log}")
                        st.info("\n".join(details))
                        if not s2_issues and has_s2_backup and user_edits:
                            if st.button("Hoàn tác & Khôi phục dữ liệu gốc ban đầu", key=f"btn_undo_clean_s2_{selected_file}"):
                                orig_copy = file_info_cur["original_df"].copy()
                                orch.data_agent.raw_dataframes[selected_file] = orig_copy
                                file_info_cur["rows"] = len(orig_copy)
                                file_info_cur["user_action_log"] = []
                                st.session_state["_detect_issues_cache"] = {}
                                st.rerun()

            if (not s2_issues) and st.session_state.show_step2_editor:
                with st.container(key="zone_step2_workspace"):
                    s2_view_df, s2_display_cols, s2_is_filtered, s2_has_show_cols = _render_excel_filter_toolbar(
                        df_current, f"s2_{selected_file}"
                    )
                    if len(s2_view_df) > 1000:
                        df_slice = s2_view_df[s2_display_cols].iloc[:500]
                        edited_slice = st.data_editor(
                            df_slice,
                            **_W_STRETCH,
                            num_rows="dynamic",
                            height=540,
                            key=f"editor_{selected_file}_large"
                        )
                    else:
                        st.caption("Nhấp đúp vào ô bất kỳ để sửa trực tiếp, sau đó bấm nút **Lưu Dữ Liệu Đã Sửa** hoặc **Làm Sạch & Chuẩn Hóa** bên dưới:")
                        edited_slice = st.data_editor(
                            s2_view_df[s2_display_cols],
                            **_W_STRETCH,
                            num_rows="dynamic",
                            height=500,
                            key=f"editor_{selected_file}"
                        )

                    col_save, col_clean = st.columns([1, 1])
                    with col_save:
                        if st.button("Lưu dữ liệu", type="primary", **_W_STRETCH, key="btn_save_step2"):
                            try:
                                with st.spinner("Đang lưu dữ liệu đã chỉnh sửa vào hệ thống..."):
                                    if not s2_is_filtered and not s2_has_show_cols and len(s2_view_df) <= 1000:
                                        orch.data_agent.raw_dataframes[selected_file] = edited_slice
                                    else:
                                        updated_full = df_current.copy()
                                        common_idx = edited_slice.index.intersection(updated_full.index)
                                        updated_full.loc[common_idx, s2_display_cols] = edited_slice.loc[common_idx, s2_display_cols]
                                        orch.data_agent.raw_dataframes[selected_file] = updated_full

                                    from utils.column_mapper import map_columns
                                    from utils.file_handler import _auto_aggregate
                                    new_df = orch.data_agent.raw_dataframes[selected_file]
                                    orch.data_agent.column_mappings[selected_file] = map_columns(list(new_df.columns))
                                    if len(new_df) > 1000:
                                        agg_df, agg_note = _auto_aggregate(new_df, selected_file)
                                        orch.data_agent.file_infos[selected_file]["aggregated_df"] = agg_df
                                        orch.data_agent.file_infos[selected_file]["aggregation_note"] = agg_note
                                    orch.data_agent.file_infos[selected_file]["rows"] = len(new_df)
                                    orch.data_agent.file_infos.setdefault(selected_file, {}).setdefault("user_action_log", []).append(
                                        f"Đã lưu chỉnh sửa trực tiếp ({len(new_df):,} dòng)."
                                    )
                                    st.session_state["_detect_issues_cache"] = {}
                                    st.success(f"Đã lưu cập nhật thành công cho tệp {selected_file} ({len(new_df):,} dòng)!")
                                set_spinner_msg(f"Đang cập nhật lại bảng dữ liệu {selected_file} sau khi lưu...")
                                st.rerun()
                            except Exception:
                                st.error("Đã xảy ra lỗi khi lưu dữ liệu chỉnh sửa. Vui lòng kiểm tra lại định dạng các ô vừa nhập.")

                    with col_clean:
                        if st.button("Chuẩn hóa dữ liệu", type="primary", **_W_STRETCH, key="btn_clean_step2"):
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
                                st.session_state["_detect_issues_cache"] = {}
                                st.success(f"Đã làm sạch và chuẩn hóa tự động toàn bộ {len(cleaned_df):,} dòng!")
                                set_spinner_msg(f"Đang hiển thị bảng dữ liệu {selected_file} sau khi làm sạch...")
                                st.rerun()
                            except Exception:
                                st.error("Không thể chuẩn hóa tự động một số cột đặc biệt trong tệp này. Dữ liệu gốc vẫn được giữ nguyên an toàn.")

    # ============================================================
    # BƯỚC 3: BÁO CÁO & DASHBOARD ĐA NĂNG CHO MỌI LOẠI FILE (UNIVERSAL ANALYTICS)
    # ============================================================
    elif st.session_state.current_step == 3:
        _all_loaded_dict = {
            k: v for k, v in orch.data_agent.raw_dataframes.items()
            if v is not None and not v.empty
        }
        _has_any_numeric_s3 = any(
            len(df.select_dtypes(include=["number"]).columns) > 0
            for df in _all_loaded_dict.values()
        )

        if not _all_loaded_dict or not _has_any_numeric_s3:
            st.warning(
                "**Dữ liệu chưa đủ điều kiện để phân tích & tạo Dashboard:**\n\n"
                "- Tệp hiện tại **không có cột số liệu định lượng** nào hợp lệ.\n"
                "- Vui lòng tải lên tệp có ít nhất 1 cột số liệu để hệ thống phân tích chính xác."
            )
            if st.button("Quay lại Bước 1 để nạp tệp khác", type="primary"):
                st.session_state.current_step = 1
                st.rerun()
            st.stop()

        import html as _html_lib
        import re as _re_lib
        import streamlit.components.v1 as components

        render_page_title(
            "BƯỚC 3 / 3 · KHÁM PHÁ",
            "Những con số biết kể chuyện.",
            "Khám phá chỉ số, tùy chỉnh góc nhìn và hoàn thiện báo cáo để chia sẻ."
        )

        # 1. Cho phép chọn tệp phân tích (nếu nạp nhiều tệp khác cấu trúc vẫn xử lý mượt)
        _file_names = list(_all_loaded_dict.keys())
        if len(_file_names) > 1:
            _scope_opts = [None] + _file_names
            _chosen_scope = st.selectbox(
                "Phạm vi dữ liệu", _scope_opts, index=0,
                format_func=lambda name: "Gộp tất cả các tệp tương thích" if name is None else name,
                key="s3_file_scope"
            )
            if _chosen_scope is not None:
                _active_fname = _chosen_scope
                df_all = _all_loaded_dict[_active_fname].copy()
                _files_display_str = _active_fname
            else:
                df_all = pd.concat(_all_loaded_dict.values(), ignore_index=True)
                _files_display_str = ", ".join(_file_names)
        else:
            _active_fname = _file_names[0]
            df_all = _all_loaded_dict[_active_fname].copy()
            _files_display_str = _active_fname

        _dynamic_default_title = f"Báo Cáo Phân Tích Dữ Liệu & Dashboard — {_files_display_str}"
        total_records_all = len(df_all)
        total_nulls_all = int(df_all.isna().sum().sum())

        # 2. Bộ nhận diện ngữ nghĩa cột thông minh cho mọi loại file
        def _detect_universal_schema(df_in: pd.DataFrame):
            raw_num_cols = list(df_in.select_dtypes(include=["number"]).columns)
            id_patterns = ["id", "stt", "index", "ma_", "mã", "code", "phone", "sdt", "sđt", "cccd", "cmnd", "zip"]

            valid_metrics = []
            for c in raw_num_cols:
                c_low = str(c).lower().strip()
                is_id_name = any(c_low == pat or c_low.startswith(pat + "_") or c_low.endswith("_" + pat) for pat in id_patterns)
                s_clean = df_in[c].dropna()
                is_seq = False
                if len(s_clean) >= 10 and s_clean.nunique() == len(s_clean):
                    diffs = s_clean.sort_values().diff().dropna()
                    if len(diffs) > 0 and (diffs == 1).all():
                        is_seq = True
                if not (is_id_name and is_seq):
                    valid_metrics.append(c)

            if not valid_metrics:
                valid_metrics = raw_num_cols

            time_kw = ["tháng", "month", "ngày", "date", "năm", "year", "quý", "quarter", "kỳ", "period", "tuần", "week", "time", "created", "updated"]
            time_cols = []
            cat_cols = []

            for c in df_in.columns:
                if c in valid_metrics:
                    continue
                c_low = str(c).lower()
                n_uniq = df_in[c].nunique(dropna=True)
                if any(tk in c_low for tk in time_kw) or pd.api.types.is_datetime64_any_dtype(df_in[c]):
                    if 1 <= n_uniq <= 366:
                        time_cols.append(c)
                elif 2 <= n_uniq <= min(100, max(2, int(len(df_in) * 0.9))):
                    cat_cols.append(c)

            if not cat_cols:
                cat_cols = [c for c in df_in.columns if c not in valid_metrics and c not in time_cols and df_in[c].nunique(dropna=True) >= 1]

            cat_cols = sorted(
                cat_cols,
                key=lambda col: (
                    0 if 2 <= df_in[col].nunique(dropna=True) <= 12 else 1,
                    df_in[col].nunique(dropna=True)
                )
            )

            return valid_metrics, cat_cols, time_cols

        def _is_additive_metric(col_name: str, series_in: pd.Series) -> bool:
            """Kiểm tra chỉ số có cộng dồn được không (Doanh thu, Số lượng -> True; Điểm TB, %, Tuổi -> False)."""
            c_low = str(col_name).lower()
            non_add_kw = ["%", "pct", "percent", "tỷ lệ", "ty le", "tỉ lệ", "rate", "ratio", "điểm", "diem", "score", "gpa", "rating", "tuổi", "tuoi", "age", "nhiệt độ", "temp", "bmi"]
            if any(k in c_low for k in non_add_kw):
                return False
            return True

        num_cols, cat_cols, time_cols = _detect_universal_schema(df_all)

        # Thanh tùy chọn linh hoạt cho mọi file — chỉ hiển thị các thanh có từ 2 lựa chọn trở lên
        primary_dim_options = cat_cols + time_cols if (cat_cols or time_cols) else ["(Toàn bộ dữ liệu)"]
        _show_metric_sel = len(num_cols) >= 2
        _show_dim1_sel = len(primary_dim_options) >= 2
        _cur_dim1_preview = st.session_state.get("s3_dim1_col") if (
            _show_dim1_sel and st.session_state.get("s3_dim1_col") in primary_dim_options
        ) else primary_dim_options[0]
        sec_candidates = [c for c in (cat_cols + time_cols) if c != _cur_dim1_preview]
        sec_options = ["(Không chọn)"] + sec_candidates
        _show_dim2_sel = len(sec_options) >= 2
        time_options = ["(Không có / Tự động)"] + time_cols
        _show_time_sel = len(time_cols) >= 2

        _active_ctrls = []
        if _show_metric_sel:
            _active_ctrls.append("metric")
        if _show_dim1_sel:
            _active_ctrls.append("dim1")
        if _show_dim2_sel:
            _active_ctrls.append("dim2")
        if _show_time_sel:
            _active_ctrls.append("time")

        _ctrl_vals = {
            "metric": num_cols[0] if num_cols else None,
            "dim1": primary_dim_options[0],
            "dim2": "(Không chọn)",
            "time": time_cols[0] if time_cols else "(Không có / Tự động)",
        }

        def _render_single_ctrl(_ckey: str):
            if _ckey == "metric":
                _ctrl_vals["metric"] = st.selectbox("Chỉ số phân tích chính:", num_cols, index=0, key="s3_metric_col")
            elif _ckey == "dim1":
                _ctrl_vals["dim1"] = st.selectbox("Chiều phân nhóm chính:", primary_dim_options, index=0, key="s3_dim1_col")
            elif _ckey == "dim2":
                sec_candidates_live = [c for c in (cat_cols + time_cols) if c != _ctrl_vals["dim1"]]
                sec_options_live = ["(Không chọn)"] + sec_candidates_live
                default_sec_idx = 1 if len(sec_options_live) > 1 else 0
                _ctrl_vals["dim2"] = st.selectbox("Chiều phân tích phụ (Chéo):", sec_options_live, index=default_sec_idx, key="s3_dim2_col")
            elif _ckey == "time":
                _ctrl_vals["time"] = st.selectbox("Trục thời gian / Kỳ:", time_options, index=1, key="s3_time_col")

        if len(_active_ctrls) == 1:
            _render_single_ctrl(_active_ctrls[0])
        elif len(_active_ctrls) >= 2:
            _ctrl_cols = st.columns(len(_active_ctrls))
            for _idx_c, _ckey in enumerate(_active_ctrls):
                with _ctrl_cols[_idx_c]:
                    _render_single_ctrl(_ckey)

        selected_metric = _ctrl_vals["metric"]
        selected_dim1 = _ctrl_vals["dim1"]
        selected_dim2 = _ctrl_vals["dim2"]
        selected_time_opt = _ctrl_vals["time"]

        time_col = selected_time_opt if selected_time_opt != "(Không có / Tự động)" else (time_cols[0] if time_cols else None)
        is_additive = _is_additive_metric(selected_metric, df_all[selected_metric])

        def _fmt_num(val: float) -> str:
            if pd.isna(val):
                return "0"
            f_val = float(val)
            if f_val.is_integer() or abs(f_val) >= 1000:
                return f"{f_val:,.0f}"
            return f"{f_val:,.2f}"

        def _analyze_universal_dataframe(df_in: pd.DataFrame, metric_col: str, dim1_col: str, dim2_col: str, t_col: str, additive: bool):
            df_work = df_in.copy()
            df_work[metric_col] = pd.to_numeric(df_work[metric_col], errors="coerce")
            df_work = df_work.dropna(subset=[metric_col])

            grand_total = float(df_work[metric_col].sum())
            grand_mean = float(df_work[metric_col].mean()) if len(df_work) > 0 else 0.0
            grand_median = float(df_work[metric_col].median()) if len(df_work) > 0 else 0.0
            grand_min = float(df_work[metric_col].min()) if len(df_work) > 0 else 0.0
            grand_max = float(df_work[metric_col].max()) if len(df_work) > 0 else 0.0
            grand_std = float(df_work[metric_col].std()) if len(df_work) > 1 else 0.0

            sort_col = "sum" if additive else "mean"

            time_range_label = "Toàn bộ dữ liệu"
            time_stats_df = pd.DataFrame()
            overall_growth_pct = None
            if t_col and t_col in df_work.columns:
                t_grp = df_work.groupby(t_col, dropna=True)[metric_col].agg(["count", "sum", "mean"]).reset_index()
                t_grp = t_grp.sort_values(by=t_col).reset_index(drop=True)
                if len(t_grp) >= 1:
                    t_first = str(t_grp[t_col].iloc[0])
                    t_last = str(t_grp[t_col].iloc[-1])
                    time_range_label = f"{t_first} → {t_last} ({len(t_grp)} kỳ)" if len(t_grp) > 1 else t_first
                    base_val = float(t_grp[sort_col].iloc[0])
                    end_val = float(t_grp[sort_col].iloc[-1])
                    if len(t_grp) >= 2 and base_val != 0:
                        overall_growth_pct = ((end_val - base_val) / abs(base_val)) * 100.0
                time_stats_df = t_grp

            if dim1_col != "(Toàn bộ dữ liệu)" and dim1_col in df_work.columns:
                g1 = df_work.groupby(dim1_col, dropna=True)[metric_col].agg(["count", "sum", "mean", "median", "min", "max"]).reset_index()
                g1 = g1.rename(columns={dim1_col: "Nhóm"})
            else:
                g1 = pd.DataFrame([{
                    "Nhóm": "Toàn bộ tệp",
                    "count": len(df_work),
                    "sum": grand_total,
                    "mean": grand_mean,
                    "median": grand_median,
                    "min": grand_min,
                    "max": grand_max
                }])

            g1["Tỷ trọng (%)"] = g1["sum"].apply(lambda x: round((float(x) / grand_total * 100.0), 2) if (grand_total != 0 and additive) else round(100.0 / max(1, len(g1)), 2))
            g1 = g1.sort_values(by=sort_col, ascending=False).reset_index(drop=True)
            g1["Xếp hạng"] = [f"Hạng {i+1}" for i in range(len(g1))]

            if t_col and t_col in df_work.columns and dim1_col in df_work.columns and dim1_col != t_col and df_work[t_col].nunique() >= 2:
                piv_t = df_work.pivot_table(index=dim1_col, columns=t_col, values=metric_col, aggfunc=sort_col)
                first_p, last_p = piv_t.columns[0], piv_t.columns[-1]
                growth_map = {}
                for idx_g, row_p in piv_t.iterrows():
                    v0, v1 = row_p.get(first_p, 0), row_p.get(last_p, 0)
                    if pd.notna(v0) and pd.notna(v1) and float(v0) != 0:
                        growth_map[idx_g] = round(((float(v1) - float(v0)) / abs(float(v0))) * 100.0, 2)
                if growth_map:
                    g1["Biến động đầu-cuối kỳ (%)"] = g1["Nhóm"].map(lambda x: growth_map.get(x, 0.0))

            summary_table = pd.DataFrame({
                "Xếp hạng": g1["Xếp hạng"],
                f"Nhóm ({dim1_col})": g1["Nhóm"].astype(str),
                "Số bản ghi": g1["count"].astype(int),
            })
            if additive:
                summary_table[f"Tổng {metric_col}"] = g1["sum"].round(2)
                summary_table[f"Trung bình {metric_col}"] = g1["mean"].round(2)
                summary_table["Trung vị (Median)"] = g1["median"].round(2)
                summary_table["Thấp nhất (Min)"] = g1["min"].round(2)
                summary_table["Cao nhất (Max)"] = g1["max"].round(2)
                summary_table["Tỷ trọng (%)"] = g1["Tỷ trọng (%)"]
            else:
                summary_table[f"Trung bình {metric_col}"] = g1["mean"].round(2)
                summary_table["Trung vị (Median)"] = g1["median"].round(2)
                summary_table["Thấp nhất (Min)"] = g1["min"].round(2)
                summary_table["Cao nhất (Max)"] = g1["max"].round(2)

            if "Biến động đầu-cuối kỳ (%)" in g1.columns:
                summary_table["Biến động đầu-cuối kỳ (%)"] = g1["Biến động đầu-cuối kỳ (%)"]

            other_num_cols = [c for c in num_cols if c != metric_col][:3]
            if dim1_col != "(Toàn bộ dữ liệu)" and dim1_col in df_work.columns and other_num_cols:
                for onc in other_num_cols:
                    onc_add = _is_additive_metric(onc, df_work[onc])
                    agg_fn = "sum" if onc_add else "mean"
                    lbl_prefix = "Tổng" if onc_add else "TB"
                    onc_map = df_work.groupby(dim1_col, dropna=True)[onc].agg(agg_fn).to_dict()
                    summary_table[f"{lbl_prefix} {onc}"] = g1["Nhóm"].map(lambda x: round(float(onc_map[x]), 2) if pd.notna(onc_map.get(x)) else 0.0)

            g2_table = pd.DataFrame()
            top_combo_info = None
            if dim2_col != "(Không chọn)" and dim2_col in df_work.columns:
                g2 = df_work.groupby(dim2_col, dropna=True)[metric_col].agg(["count", "sum", "mean", "min", "max"]).reset_index()
                g2 = g2.sort_values(by=sort_col, ascending=False).reset_index(drop=True)
                g2["Tỷ trọng (%)"] = g2["sum"].apply(lambda x: round((float(x) / grand_total * 100.0), 2) if (grand_total != 0 and additive) else round(100.0 / max(1, len(g2)), 2))
                g2_table = g2

                if dim1_col in df_work.columns and dim1_col != dim2_col:
                    cross_grp = df_work.groupby([dim1_col, dim2_col], dropna=True)[metric_col].agg(["count", "sum", "mean"]).reset_index()
                    cross_grp = cross_grp.sort_values(by=sort_col, ascending=False).reset_index(drop=True)
                    if not cross_grp.empty:
                        best_c = cross_grp.iloc[0]
                        worst_c = cross_grp.iloc[-1]
                        top_combo_info = {
                            "best_pair": f"{best_c[dim1_col]} × {best_c[dim2_col]}",
                            "best_val": float(best_c[sort_col]),
                            "best_sum": float(best_c["sum"]),
                            "best_mean": float(best_c["mean"]),
                            "best_share": round(float(best_c["sum"]) / grand_total * 100.0, 2) if (grand_total and additive) else 0.0,
                            "worst_pair": f"{worst_c[dim1_col]} × {worst_c[dim2_col]}",
                            "worst_val": float(worst_c[sort_col]),
                            "worst_sum": float(worst_c["sum"]),
                            "worst_mean": float(worst_c["mean"]),
                        }

            other_metrics_summary = []
            for onc in [c for c in num_cols if c != metric_col][:4]:
                s_o = pd.to_numeric(df_work[onc], errors="coerce").dropna()
                if len(s_o) > 0:
                    corr_v = df_work[metric_col].corr(s_o) if len(s_o) > 2 else None
                    other_metrics_summary.append({
                        "col": onc,
                        "additive": _is_additive_metric(onc, s_o),
                        "sum": float(s_o.sum()),
                        "mean": float(s_o.mean()),
                        "min": float(s_o.min()),
                        "max": float(s_o.max()),
                        "corr": float(corr_v) if (corr_v is not None and pd.notna(corr_v)) else None
                    })

            return {
                "additive": additive,
                "sort_col": sort_col,
                "grand_total": grand_total,
                "grand_mean": grand_mean,
                "grand_median": grand_median,
                "grand_min": grand_min,
                "grand_max": grand_max,
                "grand_std": grand_std,
                "time_range_label": time_range_label,
                "time_stats_df": time_stats_df,
                "overall_growth_pct": overall_growth_pct,
                "g1_raw": g1,
                "summary_table": summary_table,
                "g2_table": g2_table,
                "top_combo_info": top_combo_info,
                "other_metrics_summary": other_metrics_summary
            }

        stats_bundle = _analyze_universal_dataframe(df_all, selected_metric, selected_dim1, selected_dim2, time_col, is_additive)

        # Tạo nhận định ngắn 1-2 câu cho từng biểu đồ, báo cáo phân tích chi tiết & đề xuất hành động (100% từ dữ liệu gốc, không bịa)
        def _build_chart_insights_and_plan(bundle: dict):
            g1 = bundle["g1_raw"]
            g2 = bundle["g2_table"]
            t_df = bundle["time_stats_df"]
            combo = bundle["top_combo_info"]
            additive = bundle["additive"]
            sort_col = bundle["sort_col"]

            top_row = g1.iloc[0]
            bot_row = g1.iloc[-1]
            diff_val = float(top_row[sort_col]) - float(bot_row[sort_col])
            diff_pct = (diff_val / abs(float(bot_row[sort_col])) * 100.0) if float(bot_row[sort_col]) != 0 else 0.0

            # 1. Nhận định 1-2 câu ngay dưới Biểu đồ cột so sánh
            if len(g1) >= 2:
                if additive:
                    ins_bar = (
                        f"Nhóm <b>{_html_lib.escape(str(top_row['Nhóm']))}</b> dẫn đầu về tổng <b>{_html_lib.escape(selected_metric)}</b> với "
                        f"<b>{_fmt_num(top_row['sum'])}</b> (trung bình <b>{_fmt_num(top_row['mean'])}</b>/bản ghi). "
                        f"Mức này cao hơn nhóm thấp nhất là <b>{_html_lib.escape(str(bot_row['Nhóm']))}</b> (<b>{_fmt_num(bot_row['sum'])}</b>) khoảng <b>{_fmt_num(diff_val)}</b> (+{diff_pct:.1f}%)."
                    )
                else:
                    ins_bar = (
                        f"Nhóm <b>{_html_lib.escape(str(top_row['Nhóm']))}</b> đạt mức trung bình <b>{_html_lib.escape(selected_metric)}</b> cao nhất là "
                        f"<b>{_fmt_num(top_row['mean'])}</b> (trung vị <b>{_fmt_num(top_row['median'])}</b>). "
                        f"Chênh lệch so với nhóm thấp nhất là <b>{_html_lib.escape(str(bot_row['Nhóm']))}</b> (<b>{_fmt_num(bot_row['mean'])}</b>) đạt <b>{_fmt_num(diff_val)}</b> (+{diff_pct:.1f}%)."
                    )
            else:
                ins_bar = (
                    f"Toàn bộ <b>{int(top_row['count']):,}</b> bản ghi thuộc nhóm <b>{_html_lib.escape(str(top_row['Nhóm']))}</b> "
                    f"có giá trị trung bình <b>{_fmt_num(top_row['mean'])}</b> (dao động từ <b>{_fmt_num(top_row['min'])}</b> đến <b>{_fmt_num(top_row['max'])}</b>)."
                )

            # 2. Nhận định 1-2 câu ngay dưới Biểu đồ tròn cơ cấu %
            total_cnt_g1 = max(1, int(g1["count"].sum()))
            if len(g1) >= 2:
                if additive:
                    top2_share = float(g1["Tỷ trọng (%)"].iloc[0]) + float(g1["Tỷ trọng (%)"].iloc[1])
                    ins_donut = (
                        f"<b>{_html_lib.escape(str(top_row['Nhóm']))}</b> chiếm tỷ trọng lớn nhất với <b>{top_row['Tỷ trọng (%)']:.1f}%</b> tổng quy mô toàn tệp. "
                        f"Hai nhóm đứng đầu đóng góp cộng dồn <b>{top2_share:.1f}%</b> trên tổng số <b>{len(g1)}</b> nhóm."
                    )
                else:
                    top_cnt_sh = float(top_row["count"]) / total_cnt_g1 * 100.0
                    ins_donut = (
                        f"Nhóm <b>{_html_lib.escape(str(top_row['Nhóm']))}</b> chiếm <b>{top_cnt_sh:.1f}%</b> tổng số bản ghi ({int(top_row['count']):,}/{total_cnt_g1:,} dòng). "
                        f"Dữ liệu được phân bổ trên tổng cộng <b>{len(g1)}</b> nhóm phân loại thực tế."
                    )
            else:
                ins_donut = f"Dữ liệu tập trung <b>100%</b> vào nhóm duy nhất là <b>{_html_lib.escape(str(top_row['Nhóm']))}</b> ({total_cnt_g1:,} bản ghi)."

            # 3. Nhận định 1-2 câu ngay dưới Biểu đồ phân tích chiều chính & chiều phụ
            if not g2.empty and selected_dim2 != "(Không chọn)" and combo:
                top_g2 = g2.iloc[0]
                if additive:
                    ins_dim_panel = (
                        f"Trên chiều chính <b>{_html_lib.escape(selected_dim1)}</b>, <b>{_html_lib.escape(str(top_row['Nhóm']))}</b> đứng đầu; "
                        f"còn ở chiều phụ <b>{_html_lib.escape(selected_dim2)}</b>, <b>{_html_lib.escape(str(top_g2[selected_dim2]))}</b> dẫn đầu với <b>{_fmt_num(top_g2['sum'])}</b> ({top_g2['Tỷ trọng (%)']:.1f}%). "
                        f"Tổ hợp đạt giá trị cao nhất là <b>{_html_lib.escape(combo['best_pair'])}</b> (<b>{_fmt_num(combo['best_sum'])}</b>)."
                    )
                else:
                    ins_dim_panel = (
                        f"Ở chiều phụ <b>{_html_lib.escape(selected_dim2)}</b>, nhóm <b>{_html_lib.escape(str(top_g2[selected_dim2]))}</b> có mức trung bình cao nhất đạt <b>{_fmt_num(top_g2['mean'])}</b>. "
                        f"Kết hợp hai chiều cho thấy tổ hợp <b>{_html_lib.escape(combo['best_pair'])}</b> đạt trung bình cao nhất (<b>{_fmt_num(combo['best_mean'])}</b>)."
                    )
            else:
                ins_dim_panel = (
                    f"Biên độ giá trị của <b>{_html_lib.escape(selected_metric)}</b> trong từng nhóm dao động từ thấp nhất <b>{_fmt_num(bundle['grand_min'])}</b> "
                    f"đến cao nhất <b>{_fmt_num(bundle['grand_max'])}</b>, với mức trung vị toàn tệp là <b>{_fmt_num(bundle['grand_median'])}</b>."
                )

            # 4. Nhận định 1-2 câu ngay dưới Biểu đồ xu hướng thời gian / tương quan
            if not t_df.empty and time_col:
                t_first_row = t_df.iloc[0]
                t_last_row = t_df.iloc[-1]
                if len(t_df) >= 2 and bundle["overall_growth_pct"] is not None:
                    g_pct = bundle["overall_growth_pct"]
                    trend_word = "tăng" if g_pct > 0 else ("giảm" if g_pct < 0 else "đi ngang")
                    sign_s = "+" if g_pct > 0 else ""
                    val_0 = _fmt_num(t_first_row[sort_col])
                    val_1 = _fmt_num(t_last_row[sort_col])
                    ins_right_panel = (
                        f"Qua <b>{len(t_df)}</b> kỳ từ <b>{_html_lib.escape(str(t_first_row[time_col]))}</b> đến <b>{_html_lib.escape(str(t_last_row[time_col]))}</b>, "
                        f"chỉ số có xu hướng <b>{trend_word} {sign_s}{g_pct:.1f}%</b> (từ <b>{val_0}</b> lên <b>{val_1}</b>)."
                    )
                else:
                    ins_right_panel = (
                        f"Dữ liệu ghi nhận tại kỳ <b>{_html_lib.escape(str(t_first_row[time_col]))}</b> với tổng <b>{_fmt_num(t_first_row['sum'])}</b> "
                        f"và trung bình <b>{_fmt_num(t_first_row['mean'])}</b> trên {int(t_first_row['count']):,} bản ghi."
                    )
            elif bundle["other_metrics_summary"]:
                om0 = bundle["other_metrics_summary"][0]
                if om0["corr"] is not None:
                    corr_desc = "tương quan thuận" if om0["corr"] >= 0.3 else ("tương quan nghịch" if om0["corr"] <= -0.3 else "tương quan yếu")
                    ins_right_panel = (
                        f"Chỉ số <b>{_html_lib.escape(selected_metric)}</b> có mối <b>{corr_desc} (r = {om0['corr']:.2f})</b> với cột <b>{_html_lib.escape(str(om0['col']))}</b>. "
                        f"Giá trị trung bình của <b>{_html_lib.escape(str(om0['col']))}</b> trong tệp đạt <b>{_fmt_num(om0['mean'])}</b>."
                    )
                else:
                    ins_right_panel = (
                        f"Tệp dữ liệu còn ghi nhận cột số <b>{_html_lib.escape(str(om0['col']))}</b> với giá trị trung bình đạt <b>{_fmt_num(om0['mean'])}</b> "
                        f"(dao động từ <b>{_fmt_num(om0['min'])}</b> đến <b>{_fmt_num(om0['max'])}</b>)."
                    )
            else:
                comp_pct = 100.0 * (df_all.size - total_nulls_all) / max(1, df_all.size)
                ins_right_panel = (
                    f"Tập dữ liệu đạt độ đầy đủ <b>{comp_pct:.1f}%</b> ({total_nulls_all:,} ô trống) với độ lệch chuẩn là <b>{_fmt_num(bundle['grand_std'])}</b>."
                )

            # 5. PHẦN PHÂN TÍCH CHI TIẾT (ĐẶT NGAY BÊN TRÊN PHẦN ĐỀ XUẤT — 100% SỐ LIỆU THẬT, TUYỆT ĐỐI KHÔNG BỊA)
            completeness_pct = 100.0 * (df_all.size - total_nulls_all) / max(1, df_all.size)
            dup_cnt_all = int(df_all.duplicated().sum())
            val_range = bundle["grand_max"] - bundle["grand_min"]
            cv_pct = (bundle["grand_std"] / abs(bundle["grand_mean"]) * 100.0) if bundle["grand_mean"] != 0 else 0.0
            cols_preview = ", ".join(f"`{c}`" for c in df_all.columns[:12]) + (f"(+{len(df_all.columns)-12} cột khác)" if len(df_all.columns) > 12 else "")

            analysis_lines = [
                f"### 1. Tổng quan cấu trúc & thống kê mô tả dữ liệu (`{_files_display_str}`)",
                f"- **Quy mô & chất lượng tệp:** Tệp gồm **{total_records_all:,} dòng × {len(df_all.columns)} cột** ({cols_preview}). Độ đầy đủ đạt **{completeness_pct:.1f}%** (**{total_nulls_all:,}** ô trống, **{dup_cnt_all:,}** dòng trùng lặp).",
            ]
            if additive:
                analysis_lines.append(
                    f"- **Thống kê tổng hợp `{selected_metric}`:** Tổng cộng đạt **{_fmt_num(bundle['grand_total'])}** | Trung bình: **{_fmt_num(bundle['grand_mean'])}**/bản ghi | Trung vị (Median): **{_fmt_num(bundle['grand_median'])}**."
                )
            else:
                analysis_lines.append(
                    f"- **Thống kê tổng hợp `{selected_metric}`:** Trung bình đạt **{_fmt_num(bundle['grand_mean'])}** | Trung vị (Median): **{_fmt_num(bundle['grand_median'])}** (tính trên {total_records_all:,} bản ghi)."
                )
            analysis_lines.append(
                f"- **Mức độ phân tán:** Giá trị thấp nhất (Min) là **{_fmt_num(bundle['grand_min'])}**, cao nhất (Max) là **{_fmt_num(bundle['grand_max'])}** (khoảng biến thiên: **{_fmt_num(val_range)}**); độ lệch chuẩn đạt **{_fmt_num(bundle['grand_std'])}** (hệ số biến thiên CV = **{cv_pct:.1f}%**)."
            )

            if bundle["other_metrics_summary"]:
                other_bits = []
                for om in bundle["other_metrics_summary"]:
                    corr_str = f", tương quan r = **{om['corr']:.2f}** với `{selected_metric}`" if om["corr"] is not None else ""
                    if om["additive"]:
                        other_bits.append(f"`{om['col']}` (Tổng **{_fmt_num(om['sum'])}**, TB **{_fmt_num(om['mean'])}**, Min–Max: {_fmt_num(om['min'])} → {_fmt_num(om['max'])}{corr_str})")
                    else:
                        other_bits.append(f"`{om['col']}` (TB **{_fmt_num(om['mean'])}**, Min–Max: {_fmt_num(om['min'])} → {_fmt_num(om['max'])}{corr_str})")
                analysis_lines.append(f"- **Các cột số định lượng khác trong tệp:** {'; '.join(other_bits)}.")

            # Mục 2: Phân tích chi tiết theo chiều chính
            sec_num = 2
            analysis_lines.append("")
            analysis_lines.append(f"### {sec_num}. Phân tích chi tiết theo chiều chính `{selected_dim1}` ({len(g1)} nhóm)")
            for idx_r, r_g1 in g1.head(15).iterrows():
                gr_txt = ""
                if "Biến động đầu-cuối kỳ (%)" in r_g1 and pd.notna(r_g1["Biến động đầu-cuối kỳ (%)"]):
                    sign_g = "+" if r_g1["Biến động đầu-cuối kỳ (%)"] >= 0 else ""
                    gr_txt = f" | Biến động đầu–cuối kỳ: **{sign_g}{r_g1['Biến động đầu-cuối kỳ (%)']:.1f}%**"
                if additive:
                    analysis_lines.append(
                        f"- **Hạng {idx_r+1} — {r_g1['Nhóm']}:** Tổng đạt **{_fmt_num(r_g1['sum'])}** (chiếm **{r_g1['Tỷ trọng (%)']:.1f}%** toàn tệp), "
                        f"trung bình **{_fmt_num(r_g1['mean'])}**, trung vị **{_fmt_num(r_g1['median'])}** ({int(r_g1['count']):,} bản ghi; biên độ **{_fmt_num(r_g1['min'])} → {_fmt_num(r_g1['max'])}**){gr_txt}."
                    )
                else:
                    cnt_sh = float(r_g1["count"]) / total_cnt_g1 * 100.0
                    analysis_lines.append(
                        f"- **Hạng {idx_r+1} — {r_g1['Nhóm']}:** Trung bình đạt **{_fmt_num(r_g1['mean'])}**, trung vị **{_fmt_num(r_g1['median'])}**, "
                        f"gồm **{int(r_g1['count']):,}** bản ghi ({cnt_sh:.1f}% số dòng; biên độ **{_fmt_num(r_g1['min'])} → {_fmt_num(r_g1['max'])}**){gr_txt}."
                    )
            if len(g1) > 15:
                analysis_lines.append(f"- *(Và còn **{len(g1) - 15}** nhóm khác đã được liệt kê đầy đủ trong bảng tổng hợp phía trên.)*")

            if len(g1) >= 2:
                lbl_mode = "tổng" if additive else "trung bình"
                gap_vs_mean = float(top_row["mean"]) - bundle["grand_mean"]
                gap_vs_mean_pct = (gap_vs_mean / abs(bundle["grand_mean"]) * 100.0) if bundle["grand_mean"] != 0 else 0.0
                analysis_lines.append(
                    f"- **So sánh khoảng cách nhóm:** Nhóm dẫn đầu (**{top_row['Nhóm']}**) có {lbl_mode} cao hơn nhóm thấp nhất (**{bot_row['Nhóm']}**) là **{_fmt_num(diff_val)}** (tương đương **+{diff_pct:.1f}%**). "
                    f"Mức trung bình/bản ghi của **{top_row['Nhóm']}** (**{_fmt_num(top_row['mean'])}**) cao hơn mặt bằng chung toàn tệp (**{_fmt_num(bundle['grand_mean'])}**) là **{_fmt_num(gap_vs_mean)}** ({gap_vs_mean_pct:+.1f}%)."
                )
                if additive and len(g1) >= 3:
                    top2_sh = float(g1["Tỷ trọng (%)"].iloc[0]) + float(g1["Tỷ trọng (%)"].iloc[1])
                    analysis_lines.append(
                        f"- **Mức độ tập trung:** Hai nhóm đứng đầu (**{g1['Nhóm'].iloc[0]}** và **{g1['Nhóm'].iloc[1]}**) đóng góp cộng dồn **{top2_sh:.1f}%** tổng `{selected_metric}` toàn tệp."
                    )

            # Mục 3: Phân tích chi tiết chiều phụ & tương quan chéo (chỉ hiện khi có chọn chiều phụ)
            if not g2.empty and selected_dim2 != "(Không chọn)":
                sec_num += 1
                analysis_lines.append("")
                analysis_lines.append(f"### {sec_num}. Phân tích chi tiết chiều phụ `{selected_dim2}` & tương quan chéo ({len(g2)} nhóm)")
                for idx_2, r_g2 in g2.head(10).iterrows():
                    if additive:
                        analysis_lines.append(
                            f"- **{r_g2[selected_dim2]}:** Tổng đạt **{_fmt_num(r_g2['sum'])}** (chiếm **{r_g2['Tỷ trọng (%)']:.1f}%**), trung bình **{_fmt_num(r_g2['mean'])}** ({int(r_g2['count']):,} bản ghi; Min–Max: **{_fmt_num(r_g2['min'])} → {_fmt_num(r_g2['max'])}**)."
                        )
                    else:
                        analysis_lines.append(
                            f"- **{r_g2[selected_dim2]}:** Trung bình đạt **{_fmt_num(r_g2['mean'])}** ({int(r_g2['count']):,} bản ghi; Min–Max: **{_fmt_num(r_g2['min'])} → {_fmt_num(r_g2['max'])}**)."
                        )
                if combo:
                    combo_gap = combo["best_val"] - combo["worst_val"]
                    combo_gap_pct = (combo_gap / abs(combo["worst_val"]) * 100.0) if combo["worst_val"] != 0 else 0.0
                    if additive:
                        analysis_lines.append(
                            f"- **Đối chiếu chéo (`{selected_dim1}` × `{selected_dim2}`):** Tổ hợp đạt cao nhất là **{combo['best_pair']}** với tổng **{_fmt_num(combo['best_sum'])}** (chiếm **{combo['best_share']:.1f}%** toàn tệp, TB **{_fmt_num(combo['best_mean'])}**). "
                            f"Tổ hợp thấp nhất là **{combo['worst_pair']}** với tổng **{_fmt_num(combo['worst_sum'])}** (TB **{_fmt_num(combo['worst_mean'])}**), chênh lệch giữa 2 tổ hợp là **{_fmt_num(combo_gap)}** (+{combo_gap_pct:.1f}%)."
                        )
                    else:
                        analysis_lines.append(
                            f"- **Đối chiếu chéo (`{selected_dim1}` × `{selected_dim2}`):** Tổ hợp đạt trung bình cao nhất là **{combo['best_pair']}** (**{_fmt_num(combo['best_mean'])}**); thấp nhất là **{combo['worst_pair']}** (**{_fmt_num(combo['worst_mean'])}**), chênh lệch **{_fmt_num(combo_gap)}** (+{combo_gap_pct:.1f}%)."
                        )

            # Mục 4: Phân tích xu hướng biến động theo thời gian (chỉ hiện khi file có cột thời gian)
            if not t_df.empty and time_col:
                sec_num += 1
                t_first_row = t_df.iloc[0]
                t_last_row = t_df.iloc[-1]
                t_peak_row = t_df.loc[t_df[sort_col].idxmax()]
                t_low_row = t_df.loc[t_df[sort_col].idxmin()]
                analysis_lines.append("")
                analysis_lines.append(f"### {sec_num}. Phân tích diễn biến theo `{time_col}` ({bundle['time_range_label']})")
                analysis_lines.append(
                    f"- **So sánh kỳ đầu & kỳ cuối:** Kỳ đầu **`{t_first_row[time_col]}`** ghi nhận tổng **{_fmt_num(t_first_row['sum'])}** (TB **{_fmt_num(t_first_row['mean'])}**, {int(t_first_row['count']):,} bản ghi) "
                    f"→ Kỳ cuối **`{t_last_row[time_col]}`** ghi nhận tổng **{_fmt_num(t_last_row['sum'])}** (TB **{_fmt_num(t_last_row['mean'])}**, {int(t_last_row['count']):,} bản ghi)."
                )
                if len(t_df) >= 2:
                    t_diffs = t_df[sort_col].diff().dropna()
                    avg_step_change = float(t_diffs.mean()) if len(t_diffs) > 0 else 0.0
                    if (t_diffs > 0).all():
                        pattern_txt = "tăng liên tục qua tất cả các kỳ"
                    elif (t_diffs < 0).all():
                        pattern_txt = "giảm liên tục qua tất cả các kỳ"
                    elif (t_diffs == 0).all():
                        pattern_txt = "giữ nguyên không đổi qua các kỳ"
                    else:
                        pattern_txt = "có sự biến động tăng/giảm xen kẽ giữa các kỳ"
                    sign_tot = "+" if (bundle["overall_growth_pct"] or 0) >= 0 else ""
                    sign_step = "+" if avg_step_change >= 0 else ""
                    analysis_lines.append(
                        f"- **Xu hướng & nhịp biến động:** Toàn giai đoạn có xu hướng **{pattern_txt}**, tổng mức thay đổi từ kỳ đầu đến kỳ cuối là **{sign_tot}{bundle['overall_growth_pct']:.1f}%** (bình quân thay đổi **{sign_step}{_fmt_num(avg_step_change)}**/kỳ)."
                        if bundle["overall_growth_pct"] is not None else
                        f"- **Nhịp biến động:** Dữ liệu **{pattern_txt}** (bình quân thay đổi **{sign_step}{_fmt_num(avg_step_change)}**/kỳ)."
                    )
                    analysis_lines.append(
                        f"- **Đỉnh & đáy theo thời gian:** Kỳ cao nhất là **`{t_peak_row[time_col]}`** (đạt **{_fmt_num(t_peak_row[sort_col])}**); kỳ thấp nhất là **`{t_low_row[time_col]}`** (đạt **{_fmt_num(t_low_row[sort_col])}**)."
                    )

            # 6. Đề xuất hành động cuối báo cáo — linh hoạt theo độ phong phú dữ liệu của từng file (không bao giờ bịa ngoài file)
            has_time_series = (not t_df.empty and time_col is not None and len(t_df) >= 2)
            has_multi_group = (len(g1) >= 2)
            has_cross_dim = (not g2.empty and selected_dim2 != "(Không chọn)" and combo is not None)

            val_top_str = _fmt_num(top_row[sort_col])
            val_bot_str = _fmt_num(bot_row[sort_col])

            if has_multi_group and (has_time_series or has_cross_dim):
                p1_detail = (
                    f"Tập trung duy trì hiệu suất tại nhóm dẫn đầu <b>{top_row['Nhóm']}</b> (đạt <b>{val_top_str}</b>"
                    + (f", chiếm <b>{top_row['Tỷ trọng (%)']:.1f}%</b>" if additive else "")
                    + ")"
                    + (f" và tổ hợp đỉnh nhất <b>{combo['best_pair']}</b> (<b>{_fmt_num(combo['best_val'])}</b>)." if has_cross_dim else ".")
                )
                p2_detail = (
                    f"Rà soát và cải thiện nhóm đang ở cuối bảng là <b>{bot_row['Nhóm']}</b> (hiện đạt <b>{val_bot_str}</b>, thấp hơn nhóm dẫn đầu <b>{_fmt_num(diff_val)}</b>)"
                    + (f", đặc biệt tại tổ hợp <b>{combo['worst_pair']}</b> (<b>{_fmt_num(combo['worst_val'])}</b>)." if has_cross_dim else ".")
                )
                p3_detail = (
                    f"Tiếp tục theo dõi biến động chỉ số <b>{selected_metric}</b> theo các kỳ tiếp theo của cột <b>{time_col}</b> (biến động hiện tại: <b>{bundle['overall_growth_pct']:+.1f}%</b>) để kịp thời điều chỉnh phân bổ nguồn lực."
                    if (has_time_series and bundle["overall_growth_pct"] is not None) else
                    f"Đối chiếu định kỳ bảng tổng hợp theo <b>{selected_dim1}</b> và <b>{selected_dim2}</b> để nhân rộng cách vận hành từ nhóm Hạng 1 sang các nhóm còn lại."
                )
                plan_lines = [
                    f"### Đề xuất hành động theo giai đoạn (Dựa trên dữ liệu `{_files_display_str}`)",
                    f"- **Giai đoạn 1 — Củng cố trọng tâm ({top_row['Nhóm']}):** {p1_detail}",
                    f"- **Giai đoạn 2 — Thu hẹp chênh lệch ({bot_row['Nhóm']}):** {p2_detail}",
                    f"- **Giai đoạn 3 — Theo dõi & Tối ưu mở rộng:** {p3_detail}",
                ]
            elif has_multi_group:
                plan_lines = [
                    f"### Đề xuất hành động từ số liệu thực tế (`{_files_display_str}`)",
                    f"- **Ưu tiên duy trì nhóm dẫn đầu ({top_row['Nhóm']}):** Đang đứng Hạng 1 về <b>{selected_metric}</b> với mức <b>{val_top_str}</b>, cần giữ ổn định các yếu tố tạo nên kết quả này.",
                    f"- **Cải thiện nhóm thấp nhất ({bot_row['Nhóm']}):** Hiện đạt <b>{val_bot_str}</b> (chênh lệch <b>{_fmt_num(diff_val)}</b> so với nhóm đầu), cần rà soát nguyên nhân chênh lệch dựa trên các bản ghi thực tế của nhóm này.",
                ]
            else:
                plan_lines = [
                    f"### Đề xuất theo dõi dữ liệu (`{_files_display_str}`)",
                    f"- **Theo dõi chỉ số `{selected_metric}`:** Giá trị trung bình hiện đạt <b>{_fmt_num(bundle['grand_mean'])}</b> (trung vị <b>{_fmt_num(bundle['grand_median'])}</b>, biên độ <b>{_fmt_num(bundle['grand_min'])} → {_fmt_num(bundle['grand_max'])}</b>).",
                    f"- **Mở rộng chiều phân tích (nếu cần):** Bổ sung thêm cột phân loại (như khu vực, danh mục, thời gian) trong tệp nguồn để hệ thống so sánh chéo giữa các nhóm ở lần phân tích sau.",
                ]

            if total_nulls_all > 0:
                plan_lines.append(
                    f"- **Hoàn thiện dữ liệu gốc:** Tệp hiện còn <b>{total_nulls_all:,} ô trống</b>; nên bổ sung đầy đủ các ô khuyết này ở Bước 2 để kết quả thống kê chính xác tuyệt đối."
                )

            return {
                "ins_bar": ins_bar,
                "ins_donut": ins_donut,
                "ins_dim_panel": ins_dim_panel,
                "ins_right_panel": ins_right_panel,
                "analysis_md": "\n".join(analysis_lines),
                "plan_md": "\n".join(plan_lines),
            }

        insights_bundle = _build_chart_insights_and_plan(stats_bundle)

        _current_step3_sig = (
            "v11_analysis_above_plan_zero_hallucination",
            _files_display_str,
            total_records_all,
            total_nulls_all,
            selected_metric,
            selected_dim1,
            selected_dim2,
            str(time_col)
        )

        if st.session_state.get("_last_step3_data_sig") != _current_step3_sig:
            st.session_state.editable_report = insights_bundle["analysis_md"]
            st.session_state.editable_plan = insights_bundle["plan_md"]
            st.session_state.dashboard_title = _dynamic_default_title
            st.session_state.dashboard_scores_df = stats_bundle["summary_table"]
            st.session_state._last_step3_data_sig = _current_step3_sig

        if "editable_report" not in st.session_state or not st.session_state.editable_report:
            st.session_state.editable_report = insights_bundle["analysis_md"]
        if "editable_plan" not in st.session_state or not st.session_state.editable_plan:
            st.session_state.editable_plan = insights_bundle["plan_md"]

        if "show_edit_report" not in st.session_state:
            st.session_state.show_edit_report = False
        if "show_edit_dashboard" not in st.session_state:
            st.session_state.show_edit_dashboard = False

        def _md_to_clean_html(md_text: str) -> str:
            if not md_text:
                return ""
            html_lines = []
            in_ul = False
            for raw_line in md_text.splitlines():
                line = raw_line.strip()
                if not line:
                    if in_ul:
                        html_lines.append("</ul>")
                        in_ul = False
                    continue
                line_fmt = _html_lib.escape(line)
                line_fmt = _re_lib.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", line_fmt)
                line_fmt = _re_lib.sub(r"&lt;b&gt;(.+?)&lt;/b&gt;", r"<b>\1</b>", line_fmt)
                line_fmt = _re_lib.sub(r"`(.+?)`", r"<code style='background:#eff6ff;color:#1d4ed8;padding:1px 6px;border-radius:5px;font-weight:600;'>\1</code>", line_fmt)
                if line_fmt.startswith("### "):
                    if in_ul:
                        html_lines.append("</ul>")
                        in_ul = False
                    html_lines.append(f"<h4 style='color:#1e3a8a;font-size:1.06rem;font-weight:800;margin:12px 0 8px 0;'>{line_fmt[4:]}</h4>")
                elif line_fmt.startswith("- "):
                    if not in_ul:
                        html_lines.append("<ul style='margin:0 0 8px 18px;padding:0;line-height:1.65;color:#334155;'>")
                        in_ul = True
                    html_lines.append(f"<li style='margin-bottom:6px;'>{line_fmt[2:]}</li>")
                else:
                    if in_ul:
                        html_lines.append("</ul>")
                        in_ul = False
                    html_lines.append(f"<p style='margin:6px 0;color:#334155;line-height:1.6;'>{line_fmt}</p>")
            if in_ul:
                html_lines.append("</ul>")
            return "\n".join(html_lines)

        def _build_universal_dashboard_html(title: str, bundle: dict, df_table: pd.DataFrame, ins_data: dict, rep_md: str, pln_md: str) -> str:
            g1 = bundle["g1_raw"]
            g2 = bundle["g2_table"]
            t_df = bundle["time_stats_df"]
            additive = bundle["additive"]
            sort_col = bundle["sort_col"]
            grand_total = bundle["grand_total"]
            grand_mean = bundle["grand_mean"]
            time_badge = _html_lib.escape(bundle["time_range_label"])
            top_g = g1.iloc[0]

            # 1. Biểu đồ cột dọc phía trên: Hiển thị Chiều phân nhóm chính (selected_dim1)
            g1_plot = g1.head(12)
            max_g1_val = max(float(g1_plot[sort_col].max()), 1e-9)
            bars_g1_html = ""
            bar_w = "34px" if len(g1_plot) > 8 else "42px"
            col_min_w = "56px" if len(g1_plot) > 8 else "72px"
            for _, r in g1_plot.iterrows():
                val_main = float(r[sort_col])
                h_pct = max(18, int(round((val_main / max_g1_val) * 100)))
                sub_lbl = f"TB: {_fmt_num(r['mean'])}" if additive else f"Median: {_fmt_num(r['median'])}"
                bars_g1_html += f"""
                <div style="flex:1; display:flex; flex-direction:column; align-items:center; min-width:{col_min_w};">
                    <div style="font-weight:800; color:#1e293b; font-size:0.80rem; margin-bottom:6px; white-space:nowrap;">{_fmt_num(val_main)}</div>
                    <div style="width:{bar_w}; height:145px; background:#e2e8f0; border-radius:10px; display:flex; align-items:flex-end; overflow:hidden;">
                        <div style="width:100%; height:{h_pct}%; background:linear-gradient(180deg, #2563eb 0%, #1d4ed8 100%); border-radius:10px;"></div>
                    </div>
                    <div style="font-weight:700; color:#334155; font-size:0.80rem; margin-top:8px; text-align:center; word-break:break-word;">{_html_lib.escape(str(r['Nhóm']))}</div>
                    <div style="font-size:0.71rem; color:#64748b; white-space:nowrap;">{sub_lbl}</div>
                </div>
                """

            # 2. Biểu đồ tròn Tỷ trọng theo Chiều phân nhóm chính (selected_dim1)
            palette = ["#1d4ed8", "#2563eb", "#3b82f6", "#60a5fa", "#93c5fd", "#0284c7", "#38bdf8", "#818cf8", "#a5b4fc", "#6366f1", "#4f46e5", "#c7d2fe"]
            conic_parts = []
            legend_parts = []
            acc_pct = 0.0
            total_cnt_g1 = max(1, int(g1["count"].sum()))
            for idx_c, r in g1_plot.iterrows():
                sh = float(r["Tỷ trọng (%)"]) if additive else round(float(r["count"]) / total_cnt_g1 * 100.0, 1)
                col_hex = palette[idx_c % len(palette)]
                next_pct = min(100.0, acc_pct + sh)
                conic_parts.append(f"{col_hex} {acc_pct:.2f}% {next_pct:.2f}%")
                acc_pct = next_pct
                legend_parts.append(
                    f"<span style='display:inline-flex;align-items:center;gap:5px;font-size:0.79rem;font-weight:700;color:#1e293b;margin:2px 6px;'>"
                    f"<span style='width:8px;height:8px;border-radius:50%;background:{col_hex};display:inline-block;'></span>"
                    f"{_html_lib.escape(str(r['Nhóm']))} {sh:.1f}%</span>"
                )
            if acc_pct < 99.9:
                conic_parts.append(f"#cbd5e1 {acc_pct:.2f}% 100%")
            conic_css = ", ".join(conic_parts) if conic_parts else "#2563eb 0% 100%"
            donut_title = f"Tỷ trọng {selected_metric} theo {selected_dim1}" if additive else f"Tỷ trọng bản ghi theo {selected_dim1}"

            # 3. Khung phân tích thanh ngang theo Chiều chính & Chiều phụ
            primary_bars_html = ""
            max_g1_all = max(float(g1[sort_col].max()), 1e-9)
            for idx_p, r1 in g1.head(15).iterrows():
                v1 = float(r1[sort_col])
                w_pct1 = max(10, int(round((v1 / max_g1_all) * 100)))
                r1_right = f"{_fmt_num(r1['sum'])} (TB: {_fmt_num(r1['mean'])})" if additive else f"TB: {_fmt_num(r1['mean'])} (Min–Max: {_fmt_num(r1['min'])}→{_fmt_num(r1['max'])})"
                primary_bars_html += f"""
                <div style="margin-bottom:10px;">
                    <div style="display:flex; justify-content:space-between; font-size:0.85rem; font-weight:700; color:#1e293b; margin-bottom:4px;">
                        <span>#{idx_p+1}. {_html_lib.escape(str(r1['Nhóm']))} ({r1['Tỷ trọng (%)']:.1f}%)</span>
                        <span style="color:#2563eb;">{r1_right}</span>
                    </div>
                    <div style="width:100%; height:9px; background:#e2e8f0; border-radius:999px; overflow:hidden;">
                        <div style="width:{w_pct1}%; height:100%; background:linear-gradient(90deg, #2563eb, #38bdf8); border-radius:999px;"></div>
                    </div>
                </div>
                """

            sec_cross_html = ""
            if not g2.empty and selected_dim2 != "(Không chọn)":
                max_g2 = max(float(g2[sort_col].max()), 1e-9)
                sec_rows_tmp = ""
                for idx_s, r2 in g2.head(10).iterrows():
                    v2 = float(r2[sort_col])
                    w_pct2 = max(10, int(round((v2 / max_g2) * 100)))
                    r2_right = f"{_fmt_num(r2['sum'])} (TB: {_fmt_num(r2['mean'])})" if additive else f"TB: {_fmt_num(r2['mean'])} (Min–Max: {_fmt_num(r2['min'])}→{_fmt_num(r2['max'])})"
                    sec_rows_tmp += f"""
                    <div style="margin-bottom:9px;">
                        <div style="display:flex; justify-content:space-between; font-size:0.83rem; font-weight:700; color:#334155; margin-bottom:3px;">
                            <span>{_html_lib.escape(str(r2[selected_dim2]))} ({r2['Tỷ trọng (%)']:.1f}%)</span>
                            <span style="color:#0284c7;">{r2_right}</span>
                        </div>
                        <div style="width:100%; height:8px; background:#e2e8f0; border-radius:999px; overflow:hidden;">
                            <div style="width:{w_pct2}%; height:100%; background:linear-gradient(90deg, #0284c7, #38bdf8); border-radius:999px;"></div>
                        </div>
                    </div>
                    """
                sec_cross_html = f"""
                <div style="margin-top:14px; padding-top:12px; border-top:1.5px dashed #cbd5e1;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:9px;">
                        <span style="font-size:0.92rem; font-weight:800; color:#0f172a;"> Phân tích theo chiều phụ: {_html_lib.escape(selected_dim2)}</span>
                        <span class="badge-pill" style="background:#f0f9ff; color:#0284c7; border-color:#bae6fd;">Chiều phụ</span>
                    </div>
                    {sec_rows_tmp}
                </div>
                """

            # 4. Khối Thời gian (nếu file có cột thời gian) HOẶC Tương quan các cột số khác
            right_panel_html = ""
            if not t_df.empty and time_col:
                right_panel_title = f"Diễn biến theo {time_col}"
                max_t = max(float(t_df[sort_col].max()), 1e-9)
                for _, rt in t_df.tail(12).iterrows():
                    vt = float(rt[sort_col])
                    w_t = max(12, int(round((vt / max_t) * 100)))
                    rt_lbl = f"Tổng: {_fmt_num(rt['sum'])} (TB: {_fmt_num(rt['mean'])})" if additive else f"TB: {_fmt_num(rt['mean'])} ({int(rt['count'])} dòng)"
                    right_panel_html += f"""
                    <div style="margin-bottom:9px;">
                        <div style="display:flex; justify-content:space-between; font-size:0.84rem; font-weight:700; color:#1e293b; margin-bottom:3px;">
                            <span>{_html_lib.escape(str(rt[time_col]))}</span>
                            <span style="color:#1d4ed8;">{rt_lbl}</span>
                        </div>
                        <div style="width:100%; height:9px; background:#e2e8f0; border-radius:999px; overflow:hidden;">
                            <div style="width:{w_t}%; height:100%; background:linear-gradient(90deg, #1d4ed8, #60a5fa); border-radius:999px;"></div>
                        </div>
                    </div>
                    """
            elif bundle["other_metrics_summary"]:
                right_panel_title = "Thống kê & Tương quan các cột số khác trong tệp"
                for om in bundle["other_metrics_summary"]:
                    corr_badge = f"Tương quan r = {om['corr']:.2f}" if om["corr"] is not None else "Chỉ số phụ"
                    val_om_txt = f"Tổng: {_fmt_num(om['sum'])} · TB: {_fmt_num(om['mean'])}" if om["additive"] else f"TB: {_fmt_num(om['mean'])} · Min–Max: {_fmt_num(om['min'])}→{_fmt_num(om['max'])}"
                    w_om = int(round(min(100.0, max(15.0, abs(om["corr"] or 0.5) * 100.0))))
                    right_panel_html += f"""
                    <div style="margin-bottom:11px;">
                        <div style="display:flex; justify-content:space-between; font-size:0.84rem; font-weight:700; color:#1e293b; margin-bottom:3px;">
                            <span>{_html_lib.escape(str(om['col']))} <span style="color:#64748b;font-weight:500;">({corr_badge})</span></span>
                            <span style="color:#1d4ed8;">{val_om_txt}</span>
                        </div>
                        <div style="width:100%; height:9px; background:#e2e8f0; border-radius:999px; overflow:hidden;">
                            <div style="width:{w_om}%; height:100%; background:linear-gradient(90deg, #0284c7, #38bdf8); border-radius:999px;"></div>
                        </div>
                    </div>
                    """
            else:
                right_panel_title = "Chỉ số phân tán & Độ đầy đủ dữ liệu"
                comp_pct = 100.0 * (df_all.size - total_nulls_all) / max(1, df_all.size)
                right_panel_html = f"""
                <div style="font-size:0.87rem; color:#334155; line-height:1.7;">
                    <div>• <b>Độ đầy đủ dữ liệu:</b> {comp_pct:.1f}% ({total_nulls_all:,} ô trống)</div>
                    <div>• <b>Trung vị (Median):</b> {_fmt_num(bundle['grand_median'])}</div>
                    <div>• <b>Độ lệch chuẩn (Std Dev):</b> {_fmt_num(bundle['grand_std'])}</div>
                    <div>• <b>Khoảng biến thiên (Range):</b> {_fmt_num(bundle['grand_max'] - bundle['grand_min'])}</div>
                </div>
                """

            if not t_df.empty and time_col and bundle["other_metrics_summary"]:
                om_rows_html = ""
                for om in bundle["other_metrics_summary"]:
                    corr_badge = f"r = {om['corr']:.2f}" if om["corr"] is not None else ""
                    val_om_txt = f"Tổng: {_fmt_num(om['sum'])} (TB: {_fmt_num(om['mean'])})" if om["additive"] else f"TB: {_fmt_num(om['mean'])}"
                    om_rows_html += f"""
                    <div style="display:flex; justify-content:space-between; font-size:0.82rem; padding:4px 0; border-bottom:1px solid #f1f5f9;">
                        <span style="font-weight:700; color:#334155;">{_html_lib.escape(str(om['col']))} <span style="color:#64748b;font-weight:500;">{corr_badge}</span></span>
                        <span style="font-weight:700; color:#1e3a8a;">{val_om_txt}</span>
                    </div>
                    """
                right_panel_html += f"""
                <div style="margin-top:14px; padding-top:10px; border-top:1.5px dashed #cbd5e1;">
                    <div style="font-size:0.90rem; font-weight:800; color:#0f172a; margin-bottom:6px;"> Các chỉ số định lượng khác trong tệp</div>
                    {om_rows_html}
                </div>
                """

            th_cells = "".join(
                f"<th style='padding:10px 12px;text-align:left;font-size:0.81rem;color:#1e3a8a;background:#eff6ff;border-bottom:1.5px solid #bfdbfe;'>{_html_lib.escape(str(c))}</th>"
                for c in df_table.columns
            )
            tr_rows = ""
            for _, row_t in df_table.iterrows():
                tds = ""
                for col_name in df_table.columns:
                    val = row_t[col_name]
                    if isinstance(val, (int, float)) and not isinstance(val, bool):
                        if "%" in str(col_name):
                            val_str = f"{val:,.2f}%"
                        elif "Số bản ghi" in str(col_name):
                            val_str = f"{int(val):,}"
                        else:
                            val_str = _fmt_num(val)
                    else:
                        val_str = _html_lib.escape(str(val))
                    tds += f"<td style='padding:10px 12px;font-size:0.84rem;color:#1e293b;border-bottom:1px solid #e2e8f0;font-weight:600;'>{val_str}</td>"
                tr_rows += f"<tr>{tds}</tr>"

            kpi1_title = f"Tổng {selected_metric}" if additive else f"Trung bình {selected_metric}"
            kpi1_val = _fmt_num(grand_total) if additive else _fmt_num(grand_mean)
            kpi2_title = "Trung bình / bản ghi" if additive else "Trung vị (Median)"
            kpi2_val = _fmt_num(grand_mean) if additive else _fmt_num(bundle["grand_median"])
            top_val_txt = f"Tổng {_fmt_num(top_g['sum'])} ({top_g['Tỷ trọng (%)']:.1f}%)" if additive else f"TB: {_fmt_num(top_g['mean'])}"

            growth_kpi_txt = (
                f"+{bundle['overall_growth_pct']:.1f}%" if bundle["overall_growth_pct"] is not None and bundle["overall_growth_pct"] >= 0
                else (f"{bundle['overall_growth_pct']:.1f}%" if bundle["overall_growth_pct"] is not None else f"{len(g1)} nhóm")
            )
            growth_kpi_sub = "Biến động kỳ đầu → kỳ cuối" if bundle["overall_growth_pct"] is not None else f"Phân nhóm theo {selected_dim1}"

            return f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>{_html_lib.escape(title)}</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
    body {{
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        background: #f4f7fb;
        margin: 0;
        padding: 14px;
        color: #1e293b;
    }}
    .dash-card {{
        background: #ffffff;
        border: 1px solid #dbeafe;
        border-radius: 18px;
        padding: 18px 20px;
        box-shadow: 0 4px 16px rgba(37, 99, 235, 0.05);
        margin-bottom: 16px;
    }}
    .badge-pill {{
        background: #eff6ff;
        color: #1d4ed8;
        border: 1px solid #bfdbfe;
        font-size: 0.78rem;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 999px;
        display: inline-block;
    }}
    .kpi-grid {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 14px;
        margin-bottom: 16px;
    }}
    .kpi-box {{
        background: #ffffff;
        border: 1px solid #dbeafe;
        border-radius: 16px;
        padding: 16px;
        box-shadow: 0 3px 12px rgba(30, 58, 138, 0.04);
    }}
    .grid-2 {{
        display: grid;
        grid-template-columns: 1.25fr 1fr;
        gap: 16px;
        margin-bottom: 16px;
    }}
    * {{ box-sizing: border-box; }}
    body {{ font-size: 16px; line-height: 1.6; }}
    .dash-card, .kpi-box {{ box-shadow: 0 3px 12px rgba(30, 58, 138, 0.025); border-color: #e2e8f1; }}
    .dash-card {{ overflow: auto; }}
    .dash-card table {{ min-width: 540px; }}
    @media (max-width: 900px) {{
        .kpi-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
        .grid-2 {{ grid-template-columns: minmax(0, 1fr); }}
    }}
    @media (max-width: 480px) {{
        body {{ padding: 6px; }}
        .dash-card {{ padding: 14px; border-radius: 12px; }}
        .kpi-grid {{ grid-template-columns: minmax(0, 1fr); }}
        .kpi-box {{ padding: 14px; }}
    }}
    .chart-caption {{
        margin-top: 12px;
        padding: 10px 13px;
        background: #f8fbff;
        border-left: 3.5px solid #2563eb;
        border-radius: 0 10px 10px 0;
        font-size: 0.84rem;
        color: #334155;
        line-height: 1.55;
    }}
</style>
</head>
<body>
    <div class="dash-card" style="background:linear-gradient(90deg, #eff6ff 0%, #ffffff 100%); display:flex; justify-content:space-between; align-items:center;">
        <div>
            <div style="font-size:1.22rem; font-weight:800; color:#1e3a8a;">{_html_lib.escape(title)}</div>
            <div style="font-size:0.85rem; color:#475569; margin-top:3px;">
                Phân tích tự động 100% từ dữ liệu thực tế ({total_records_all:,} dòng × {len(df_all.columns)} cột · Chỉ số: <b>{_html_lib.escape(selected_metric)}</b> · Chiều chính: <b>{_html_lib.escape(selected_dim1)}</b>)
            </div>
        </div>
        <span class="badge-pill">{time_badge}</span>
    </div>

    <div class="kpi-grid">
        <div class="kpi-box">
            <div style="font-size:0.81rem; color:#64748b; font-weight:600;">{_html_lib.escape(kpi1_title)}</div>
            <div style="font-size:1.42rem; font-weight:800; color:#1e3a8a; margin:6px 0 4px 0;">{kpi1_val}</div>
            <div style="font-size:0.77rem; color:#2563eb; font-weight:600;">Trên {total_records_all:,} bản ghi hợp lệ</div>
        </div>
        <div class="kpi-box">
            <div style="font-size:0.81rem; color:#64748b; font-weight:600;">{_html_lib.escape(kpi2_title)}</div>
            <div style="font-size:1.42rem; font-weight:800; color:#1e3a8a; margin:6px 0 4px 0;">{kpi2_val}</div>
            <div style="font-size:0.77rem; color:#2563eb; font-weight:600;">Min: {_fmt_num(bundle['grand_min'])} · Max: {_fmt_num(bundle['grand_max'])}</div>
        </div>
        <div class="kpi-box">
            <div style="font-size:0.81rem; color:#64748b; font-weight:600;">Nhóm dẫn đầu ({_html_lib.escape(selected_dim1)})</div>
            <div style="font-size:1.42rem; font-weight:800; color:#1e3a8a; margin:6px 0 4px 0;">{_html_lib.escape(str(top_g['Nhóm']))}</div>
            <div style="font-size:0.77rem; color:#2563eb; font-weight:600;">{top_val_txt}</div>
        </div>
        <div class="kpi-box">
            <div style="font-size:0.81rem; color:#64748b; font-weight:600;">Biến động / Quy mô nhóm</div>
            <div style="font-size:1.42rem; font-weight:800; color:#1e3a8a; margin:6px 0 4px 0;">{growth_kpi_txt}</div>
            <div style="font-size:0.77rem; color:#2563eb; font-weight:600;">{_html_lib.escape(growth_kpi_sub)}</div>
        </div>
    </div>

    <div class="grid-2">
        <div class="dash-card" style="margin-bottom:0; display:flex; flex-direction:column; justify-content:space-between;">
            <div>
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
                    <span style="font-size:1.0rem; font-weight:800; color:#0f172a;">Biểu đồ so sánh {_html_lib.escape(selected_metric)} theo {_html_lib.escape(selected_dim1)}</span>
                    <span class="badge-pill">{len(g1_plot)}/{len(g1)} nhóm</span>
                </div>
                <div style="display:flex; justify-content:space-around; align-items:flex-end; padding:12px 10px; background:#f8fbff; border-radius:14px; gap:6px; overflow-x:auto;">
                    {bars_g1_html}
                </div>
            </div>
            <div class="chart-caption"> <b>Nhận định biểu đồ:</b> {ins_data['ins_bar']}</div>
        </div>

        <div class="dash-card" style="margin-bottom:0; display:flex; flex-direction:column; justify-content:space-between;">
            <div>
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:1.0rem; font-weight:800; color:#0f172a;">{_html_lib.escape(donut_title)}</span>
                    <span class="badge-pill">Cơ cấu %</span>
                </div>
                <div style="display:flex; flex-direction:column; align-items:center; margin:12px 0 6px 0;">
                    <div style="width:130px; height:130px; border-radius:50%; background:conic-gradient({conic_css}); display:flex; align-items:center; justify-content:center;">
                        <div style="width:82px; height:82px; border-radius:50%; background:#ffffff; display:flex; flex-direction:column; align-items:center; justify-content:center;">
                            <span style="font-weight:800; font-size:1.0rem; color:#0f172a;">100%</span>
                            <span style="font-size:0.72rem; color:#64748b;">{len(g1)} nhóm</span>
                        </div>
                    </div>
                    <div style="margin-top:10px; text-align:center;">{''.join(legend_parts)}</div>
                </div>
            </div>
            <div class="chart-caption"> <b>Nhận định cơ cấu:</b> {ins_data['ins_donut']}</div>
        </div>
    </div>

    <div class="grid-2">
        <div class="dash-card" style="margin-bottom:0; display:flex; flex-direction:column; justify-content:space-between;">
            <div>
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
                    <span style="font-size:1.0rem; font-weight:800; color:#0f172a;">Phân tích chi tiết theo {_html_lib.escape(selected_dim1)}</span>
                    <span class="badge-pill">Chiều phân nhóm chính</span>
                </div>
                {primary_bars_html}
                {sec_cross_html}
            </div>
            <div class="chart-caption"> <b>Nhận định phân nhóm:</b> {ins_data['ins_dim_panel']}</div>
        </div>

        <div class="dash-card" style="margin-bottom:0; display:flex; flex-direction:column; justify-content:space-between;">
            <div>
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
                    <span style="font-size:1.0rem; font-weight:800; color:#0f172a;">{_html_lib.escape(right_panel_title)}</span>
                    <span class="badge-pill">{time_badge}</span>
                </div>
                {right_panel_html}
            </div>
            <div class="chart-caption"> <b>Nhận định xu hướng:</b> {ins_data['ins_right_panel']}</div>
        </div>
    </div>

    <div class="dash-card">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
            <span style="font-size:1.05rem; font-weight:800; color:#0f172a;">Bảng tổng hợp số liệu chi tiết theo {_html_lib.escape(selected_dim1)}</span>
            <span class="badge-pill">Số liệu gốc 100%</span>
        </div>
        <div style="overflow-x:auto;">
            <table style="width:100%; border-collapse:collapse;">
                <thead><tr>{th_cells}</tr></thead>
                <tbody>{tr_rows}</tbody>
            </table>
        </div>
    </div>

    <div class="dash-card">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
            <span style="font-size:1.08rem; font-weight:800; color:#0f172a;">Phân tích chi tiết dữ liệu</span>
            <span class="badge-pill">100% từ dữ liệu gốc</span>
        </div>
        {_md_to_clean_html(rep_md)}
    </div>

    <div class="dash-card" style="background:linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
            <span style="font-size:1.08rem; font-weight:800; color:#0f172a;">Đề xuất hành động dựa trên dữ liệu</span>
            <span class="badge-pill">Bám sát dữ liệu gốc</span>
        </div>
        {_md_to_clean_html(pln_md)}
    </div>
</body>
</html>"""

        if st.session_state.get("dashboard_scores_df") is None:
            st.session_state.dashboard_scores_df = stats_bundle["summary_table"]
        df_scores = st.session_state.dashboard_scores_df.copy()
        unified_html = _build_universal_dashboard_html(
            title=st.session_state.dashboard_title,
            bundle=stats_bundle,
            df_table=df_scores,
            ins_data=insights_bundle,
            rep_md=st.session_state.editable_report,
            pln_md=st.session_state.editable_plan
        )

        with st.container(key="zone_step3_preview"):
            components.html(unified_html, height=860, scrolling=True)

        with st.container(key="floating_download_step3"):
            st.download_button(
                label="Tải báo cáo HTML",
                data=unified_html.encode("utf-8"),
                file_name="Bao_Cao_Dashboard_Phan_Tich.html",
                mime="text/html",
                type="primary",
                **_W_STRETCH,
                key="dl_unified_html"
            )

        st.write("")
        btn_ed_col1, btn_ed_col2 = st.columns(2)
        with btn_ed_col1:
            label_rep_btn = "Đóng khung sửa phân tích & đề xuất" if st.session_state.show_edit_report else "Chỉnh sửa phân tích & đề xuất"
            if st.button(label_rep_btn, **_W_STRETCH, key="toggle_edit_report_btn"):
                st.session_state.show_edit_report = not st.session_state.show_edit_report
                st.rerun()

        with btn_ed_col2:
            label_dash_btn = "Đóng khung sửa bảng số liệu" if st.session_state.show_edit_dashboard else "Chỉnh sửa bảng số liệu tổng hợp"
            if st.button(label_dash_btn, **_W_STRETCH, key="toggle_edit_dashboard_btn"):
                st.session_state.show_edit_dashboard = not st.session_state.show_edit_dashboard
                st.rerun()

        if st.session_state.show_edit_report:
            st.markdown("#####  Chỉnh sửa tiêu đề, nội dung phân tích & đề xuất hành động")
            new_title = st.text_input("Tiêu đề báo cáo:", value=st.session_state.dashboard_title, key="rep_title_input")
            col_ed1, col_ed2 = st.columns(2)
            with col_ed1:
                new_report = st.text_area("Nội dung phân tích chi tiết:", value=st.session_state.editable_report, height=260)
            with col_ed2:
                new_plan = st.text_area("Nội dung đề xuất hành động:", value=st.session_state.editable_plan, height=260)

            if st.button("Lưu thay đổi báo cáo", type="primary", **_W_STRETCH):
                st.session_state.dashboard_title = new_title
                st.session_state.editable_report = new_report
                st.session_state.editable_plan = new_plan
                st.session_state.show_edit_report = False
                st.rerun()

        if st.session_state.show_edit_dashboard:
            st.markdown("#####  Chỉnh sửa bảng số liệu tổng hợp trên Dashboard")
            edited_dash_df = st.data_editor(
                st.session_state.dashboard_scores_df,
                **_W_STRETCH,
                num_rows="dynamic",
                key="dashboard_score_editor"
            )
            if st.button("Lưu bảng số liệu & cập nhật Dashboard", type="primary", **_W_STRETCH):
                st.session_state.dashboard_scores_df = edited_dash_df.copy()
                st.session_state.show_edit_dashboard = False
                st.rerun()

except Exception as _global_exc:
    import traceback
    traceback.print_exc()
    st.error(_vietnamese_error_message(_global_exc))

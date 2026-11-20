"""Presentation components. Data processing stays in app.py and agents/."""

from html import escape
from pathlib import Path
import re
from textwrap import dedent

import streamlit as st


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
        <div><strong>Data Insight</strong><span>KHÔNG GIAN PHÂN TÍCH</span></div></div>
    ''')


def render_header(step: int, file_count: int):
    pages = ["Tổng quan", "Nhập dữ liệu", "Làm sạch dữ liệu", "Báo cáo & Dashboard"]
    markup(f'''
        <div class="app-topline"><div>Không gian làm việc <span>/</span> <b>{pages[step]}</b></div>
        <span class="session-chip">{file_count} tệp trong phiên</span></div>
    ''')


def render_page_title(eyebrow: str, title: str, description: str):
    markup(f'''
        <div class="page-heading"><span class="eyebrow">{escape(eyebrow)}</span>
        <h1>{escape(title)}</h1><p>{escape(description)}</p></div>
    ''')


def render_landing():
    with st.container(key="landing_stage_container"):
        left, right = st.columns([1.08, 1], gap="large")
        with left:
            markup('''
                <div class="hero-copy"><span class="eyebrow hero-eyebrow">PHÂN TÍCH THÔNG MINH · QUYẾT ĐỊNH TỰ TIN</span>
                <h1>Từ dữ liệu thô,<br>đến <em>góc nhìn mới.</em></h1>
                <p>Hiểu dữ liệu của bạn theo cách đơn giản hơn. Kết nối, làm sạch và tạo báo cáo trực quan trong một quy trình liền mạch.</p></div>
            ''')
            if st.button("Bắt đầu phân tích", type="primary", key="btn_hero_start"):
                st.session_state.current_step = 1
                st.session_state.pending_spinner_msg = "Đang mở không gian dữ liệu..."
                st.rerun()
            markup('''
                <div class="hero-support"><span>CSV, TSV, Excel & Google Sheets</span>
                <span>Bạn kiểm soát mọi thay đổi</span></div>
            ''')
        with right:
            markup('''
                <div class="preview-scene" aria-label="Minh họa một báo cáo trực quan; đây không phải dữ liệu của bạn">
                <div class="preview-heading"><div class="preview-mark">DI</div><span>Góc nhìn tổng quan</span><span class="preview-demo">Dữ liệu minh họa</span></div>
                <div class="preview-metrics"><div><span>Bản ghi đã xử lý</span><strong>2.480</strong><small>Tổng hợp từ dữ liệu nguồn</small></div>
                <div><span>Chất lượng dữ liệu</span><strong>98,6<small>%</small></strong><small class="preview-green">Sẵn sàng phân tích</small></div></div>
                <div class="preview-chart"><div class="preview-chart-title"><b>Hiệu suất theo khu vực</b><span>Tổng quan</span></div>
                <div class="preview-bars" aria-hidden="true"><div><i style="--height:48%;--delay:0ms"></i><span>Miền Bắc</span></div><div><i style="--height:74%;--delay:80ms"></i><span>Miền Trung</span></div><div><i style="--height:95%;--delay:160ms"></i><span>Miền Nam</span></div><div><i style="--height:62%;--delay:240ms"></i><span>Khác</span></div></div></div>
                <div class="preview-note"><div><b>Góc nhìn rõ ràng hơn</b><span>Nhận diện xu hướng. Tìm cơ hội tăng trưởng.</span></div></div>
                </div>
            ''')

    markup('''
        <div class="section-intro"><span class="eyebrow">ÍT THAO TÁC HƠN, NHIỀU GÓC NHÌN HƠN</span>
        <h2>Một quy trình. Ba bước rõ ràng.</h2><p>Từ tệp đầu tiên đến báo cáo sẵn sàng chia sẻ.</p></div>
    ''')
    features = [
        ("upload", "Kết nối dữ liệu", "Tải nhiều tệp hoặc kết nối Google Sheets. Kiểm tra và chỉnh sửa ngay trên bảng.", "CSV · EXCEL · GOOGLE SHEETS"),
        ("clean", "Làm sạch có kiểm soát", "Phát hiện dữ liệu thiếu, trùng lặp và sai lệch. Xem trước, duyệt sửa và hoàn tác.", "KIỂM TRA · PHÊ DUYỆT · HOÀN TÁC"),
        ("chart", "Khám phá & chia sẻ", "Theo dõi chỉ số, so sánh các nhóm và tùy chỉnh báo cáo trước khi tải xuống.", "DASHBOARD · PHÂN TÍCH · BÁO CÁO"),
    ]
    for col, (kind, title, description, detail) in zip(st.columns(3, gap="medium"), features):
        with col:
            markup(f'''
                <div class="feature-card {kind}">
                <h3>{title}</h3><p>{description}</p><span class="feature-detail">{detail}</span></div>
            ''')
    markup('''
        <div class="landing-footnote">
        <span><b>Dữ liệu của bạn, quyết định của bạn.</b> Mọi thay đổi dữ liệu đều do bạn chủ động thực hiện.</span></div>
    ''')

"""
Bộ công cụ Xuất Báo Cáo & Dashboard Đa Định Dạng (HTML, DOCX, PDF)
- Tạo ảnh biểu đồ phân tích độ phân giải cao (PNG/Base64) từ dữ liệu điểm số
- Tách riêng Báo cáo Đề xuất (có nhúng ảnh biểu đồ phân tích) và Dashboard Tương tác
- Hỗ trợ xuất ra 3 định dạng chuẩn: .html, .docx (Word), .pdf (văn bản Tiếng Việt + biểu đồ)
"""

import io
import re
import base64
import textwrap
from typing import List, Dict, Any
import pandas as pd
import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH


# Cấu hình font hỗ trợ đầy đủ Tiếng Việt Unicode trên Windows
plt.rcParams["font.sans-serif"] = ["Segoe UI", "Arial", "Tahoma", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


def render_chart_png_bytes(df_scores: pd.DataFrame, chart_type: str = "bar") -> bytes:
    """
    Vẽ biểu đồ chất lượng cao bằng Matplotlib trả về PNG bytes để chèn vào Báo cáo HTML, Word (.docx) và PDF (.pdf).
    chart_type: 'bar' | 'radar' | 'grouped'
    """
    buf = io.BytesIO()

    if chart_type == "bar":
        fig, ax = plt.subplots(figsize=(8.5, 4.5), dpi=160)
        fig.patch.set_facecolor("#ffffff")
        ax.set_facecolor("#eff6ff")

        regions = df_scores["Địa bàn"].astype(str).tolist()
        scores = df_scores["Điểm tổng hợp"].astype(float).tolist()
        colors = ["#2563eb", "#3b82f6", "#60a5fa", "#93c5fd", "#bfdbfe"][:len(regions)]

        bars = ax.bar(regions, scores, color=colors, width=0.52, edgecolor="#1e3a8a", linewidth=1.0)
        ax.set_ylim(0, 10.8)
        ax.set_ylabel("Điểm Tổng Hợp (Thang 10)", fontsize=11, fontweight="bold", color="#0f172a")
        ax.set_title("Biểu Đồ 1: Xếp Hạng Điểm Tổng Hợp Có Trọng Số Theo Địa Bàn", fontsize=13, fontweight="bold", color="#1e3a8a", pad=14)
        ax.grid(axis="y", linestyle="--", alpha=0.45, color="#60a5fa")

        for bar, val in zip(bars, scores):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.22,
                f"{val:.2f}",
                ha="center",
                va="bottom",
                fontsize=11,
                fontweight="bold",
                color="#1e3a8a"
            )
        plt.tight_layout()
        fig.savefig(buf, format="png", bbox_inches="tight")
        plt.close(fig)

    elif chart_type == "radar":
        categories = ["Quy mô\n(25%)", "Nhu cầu WMS\n(25%)", "Khả thi On-site\n(25%)", "Cạnh tranh\n(15%)", "Tăng trưởng\n(10%)"]
        col_keys = ["Quy mô (25%)", "Nhu cầu WMS (25%)", "Khả thi On-site (25%)", "Cạnh tranh (15%)", "Tăng trưởng (10%)"]
        N = len(categories)
        angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(6.8, 5.5), subplot_kw=dict(polar=True), dpi=160)
        fig.patch.set_facecolor("#ffffff")
        ax.set_facecolor("#f8fafc")

        palette = ["#2563eb", "#7c3aed", "#0284c7", "#059669", "#d97706"]
        for idx, row in df_scores.iterrows():
            vals = [float(row.get(k, 0)) for k in col_keys]
            vals += vals[:1]
            c = palette[idx % len(palette)]
            ax.plot(angles, vals, color=c, linewidth=2.2, label=str(row["Địa bàn"]))
            ax.fill(angles, vals, color=c, alpha=0.14)

        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, fontsize=9.5, fontweight="bold", color="#0f172a")
        ax.set_ylim(0, 10)
        ax.set_title("Biểu Đồ 2: Radar 5 Chiều So Sánh Năng Lực Địa Bàn", fontsize=12.5, fontweight="bold", color="#1e3a8a", pad=20)
        ax.legend(loc="upper right", bbox_to_anchor=(1.28, 1.12), fontsize=9.5)
        plt.tight_layout()
        fig.savefig(buf, format="png", bbox_inches="tight")
        plt.close(fig)

    else:  # grouped
        fig, ax = plt.subplots(figsize=(9.5, 4.8), dpi=160)
        fig.patch.set_facecolor("#ffffff")
        ax.set_facecolor("#eff6ff")

        regions = df_scores["Địa bàn"].astype(str).tolist()
        col_keys = ["Quy mô (25%)", "Nhu cầu WMS (25%)", "Khả thi On-site (25%)", "Cạnh tranh (15%)", "Tăng trưởng (10%)"]
        palette = ["#3b82f6", "#8b5cf6", "#3b82f6", "#10b981", "#f59e0b"]

        x = np.arange(len(regions))
        width = 0.15

        for i, (col_k, color) in enumerate(zip(col_keys, palette)):
            vals = df_scores[col_k].astype(float).tolist()
            offset = (i - 2) * width
            ax.bar(x + offset, vals, width, label=col_k, color=color)

        ax.set_xticks(x)
        ax.set_xticklabels(regions, fontsize=11, fontweight="bold", color="#0f172a")
        ax.set_ylim(0, 10.8)
        ax.set_ylabel("Điểm số (1-10)", fontsize=10.5, fontweight="bold", color="#0f172a")
        ax.set_title("Biểu Đồ 3: Phân Tích Chi Tiết 5 Tiêu Chí Theo Từng Địa Bàn", fontsize=13, fontweight="bold", color="#1e3a8a", pad=14)
        ax.legend(loc="upper right", fontsize=8.5, ncol=2)
        ax.grid(axis="y", linestyle="--", alpha=0.4, color="#60a5fa")
        plt.tight_layout()
        fig.savefig(buf, format="png", bbox_inches="tight")
        plt.close(fig)

    return buf.getvalue()


def _md_to_html_block(md_text: str) -> str:
    """Chuyển đổi văn bản Markdown sang HTML sạch đẹp."""
    lines = md_text.split("\n")
    out = []
    for line in lines:
        s = line.strip()
        if not s:
            continue
        if s.startswith("### "):
            out.append(f"<h3>{s[4:]}</h3>")
        elif s.startswith("## "):
            out.append(f"<h2>{s[3:]}</h2>")
        elif s.startswith("# "):
            out.append(f"<h1>{s[2:]}</h1>")
        elif s.startswith("- "):
            content_li = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", s[2:])
            out.append(f"<li>{content_li}</li>")
        else:
            content_p = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", line)
            out.append(f"<p>{content_p}</p>")
    return "\n".join(out)


def build_standalone_report_html(
    title: str,
    report_md: str,
    plan_md: str,
    df_scores: pd.DataFrame,
    selected_charts: List[str]
) -> str:
    """
    Tạo HTML riêng cho BÁO CÁO ĐỀ XUẤT (có kèm các ảnh biểu đồ mà người dùng tích chọn để minh họa phân tích).
    """
    scores_html_table = df_scores.to_html(index=False, classes="styled-table")
    report_body = _md_to_html_block(report_md)
    plan_body = _md_to_html_block(plan_md)

    charts_html_section = ""
    chart_titles = {
        "bar": "Biểu Đồ 1: Xếp Hạng Điểm Tổng Hợp Có Trọng Số",
        "radar": "Biểu Đồ 2: Radar 5 Chiều So Sánh Năng Lực Địa Bàn",
        "grouped": "Biểu Đồ 3: Phân Tích Chi Tiết 5 Tiêu Chí Theo Địa Bàn"
    }

    if selected_charts:
        charts_items = ""
        for ch_key in selected_charts:
            png_bytes = render_chart_png_bytes(df_scores, ch_key)
            b64_img = base64.b64encode(png_bytes).decode("utf-8")
            c_title = chart_titles.get(ch_key, "Biểu đồ phân tích")
            charts_items += f"""
            <div class="report-chart-card">
                <h4>📊 {c_title}</h4>
                <img src="data:image/png;base64,{b64_img}" alt="{c_title}" />
            </div>
            """
        charts_html_section = f"""
        <h2>📈 HÌNH ẢNH BIỂU ĐỒ MINH HỌA PHÂN TÍCH TRONG BÁO CÁO</h2>
        <div class="report-charts-container">
            {charts_items}
        </div>
        """

    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>{title} - Báo Cáo Đề Xuất</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        body {{
            font-family: 'Plus Jakarta Sans', 'Segoe UI', sans-serif;
            line-height: 1.7;
            color: #1e1b4b;
            background: #f0f7ff;
            padding: 28px;
            margin: 0;
        }}
        .report-paper {{
            max-width: 1050px;
            margin: auto;
            background: #ffffff;
            padding: 44px 52px;
            border-radius: 24px;
            box-shadow: 0 14px 36px rgba(131, 24, 67, 0.1);
            border: 2px solid #dbeafe;
        }}
        .doc-header {{
            border-bottom: 3px solid #60a5fa;
            padding-bottom: 20px;
            margin-bottom: 28px;
        }}
        .doc-header h1 {{
            color: #1e3a8a;
            margin: 0 0 8px 0;
            font-size: 1.9rem;
        }}
        .doc-header .meta {{
            color: #0369a1;
            font-weight: 600;
            font-size: 1rem;
        }}
        h2 {{
            color: #1e3a8a;
            border-left: 5px solid #3b82f6;
            padding-left: 12px;
            margin-top: 32px;
            font-size: 1.4rem;
        }}
        h3 {{
            color: #0f172a;
            margin-top: 20px;
            font-size: 1.2rem;
        }}
        .styled-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 18px 0 26px 0;
            font-size: 1rem;
        }}
        .styled-table th, .styled-table td {{
            border: 1px solid #dbeafe;
            padding: 10px 14px;
            text-align: left;
        }}
        .styled-table th {{
            background-color: #eff6ff;
            color: #1e3a8a;
            font-weight: 700;
        }}
        .styled-table tr:nth-child(even) {{
            background-color: #f8fafc;
        }}
        .report-charts-container {{
            display: flex;
            flex-direction: column;
            gap: 24px;
            margin: 22px 0;
        }}
        .report-chart-card {{
            background: #f0f9ff;
            border: 1.5px solid #bfdbfe;
            border-radius: 18px;
            padding: 18px;
            text-align: center;
        }}
        .report-chart-card h4 {{
            margin: 0 0 12px 0;
            color: #1e3a8a;
            font-size: 1.1rem;
        }}
        .report-chart-card img {{
            max-width: 92%;
            height: auto;
            border-radius: 12px;
        }}
        .content-box {{
            background: #f8fafc;
            border: 1px solid #dbeafe;
            border-radius: 16px;
            padding: 22px 28px;
            margin-top: 16px;
            font-size: 1.08rem;
        }}
    </style>
</head>
<body>
    <div class="report-paper">
        <div class="doc-header">
            <h1>📄 {title}</h1>
            <div class="meta">Hệ thống Phân Tích Dữ Liệu Thông Minh | Báo Cáo Đề Xuất & Kế Hoạch Hành Động</div>
        </div>

        <h2>📋 BẢNG TỔNG HỢP ĐIỂM SỐ & XẾP HẠNG ĐỊA BÀN</h2>
        {scores_html_table}

        {charts_html_section}

        <h2>📑 NỘI DUNG BÁO CÁO PHÂN TÍCH & ĐỀ XUẤT</h2>
        <div class="content-box">
            {report_body}
        </div>

        <h2>📅 KẾ HOẠCH KHẢO SÁT THỰC ĐỊA TIẾP THEO</h2>
        <div class="content-box">
            {plan_body}
        </div>
    </div>
</body>
</html>"""


def build_standalone_dashboard_html(
    title: str,
    df_scores: pd.DataFrame,
    bar_html: str,
    radar_html: str,
    grouped_html: str
) -> str:
    """
    Tạo HTML riêng cho DASHBOARD BIỂU ĐỒ TƯƠNG TÁC (Executive Dashboard).
    """
    top2_list = df_scores["Địa bàn"].head(2).tolist()
    best_region = df_scores.iloc[0]["Địa bàn"] if len(df_scores) > 0 else "N/A"
    best_score = df_scores.iloc[0]["Điểm tổng hợp"] if len(df_scores) > 0 else 0
    avg_score = round(df_scores["Điểm tổng hợp"].mean(), 2) if len(df_scores) > 0 else 0
    scores_html_table = df_scores.to_html(index=False, classes="styled-table")

    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>{title} - Interactive Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        body {{
            font-family: 'Plus Jakarta Sans', 'Segoe UI', sans-serif;
            background: linear-gradient(180deg, #f0f9ff 0%, #e0f2fe 100%);
            color: #1e1b4b;
            padding: 24px;
            margin: 0;
        }}
        .dash-wrapper {{
            max-width: 1260px;
            margin: auto;
            background: #ffffff;
            padding: 34px 40px;
            border-radius: 26px;
            box-shadow: 0 16px 40px rgba(131, 24, 67, 0.12);
            border: 2px solid #dbeafe;
        }}
        .dash-banner {{
            background: linear-gradient(135deg, #bfdbfe 0%, #e0f2fe 50%, #bae6fd 100%);
            padding: 22px 30px;
            border-radius: 20px;
            margin-bottom: 26px;
        }}
        .dash-banner h1 {{
            color: #0f172a;
            margin: 0 0 6px 0;
            font-size: 1.8rem;
        }}
        .dash-banner p {{
            color: #0369a1;
            margin: 0;
            font-weight: 600;
        }}
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            margin-bottom: 26px;
        }}
        .kpi-card {{
            background: #eff6ff;
            border: 1.5px solid #bfdbfe;
            border-radius: 18px;
            padding: 16px 18px;
            text-align: center;
        }}
        .kpi-card .label {{
            font-size: 0.9rem;
            color: #64748b;
            font-weight: 700;
            text-transform: uppercase;
        }}
        .kpi-card .val {{
            font-size: 1.65rem;
            color: #1e3a8a;
            font-weight: 800;
            margin-top: 6px;
        }}
        .charts-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin: 22px 0;
        }}
        .chart-box {{
            background: #ffffff;
            border: 1.5px solid #dbeafe;
            border-radius: 20px;
            padding: 14px;
            box-shadow: 0 6px 20px rgba(244, 114, 182, 0.08);
        }}
        .chart-box-full {{
            background: #ffffff;
            border: 1.5px solid #dbeafe;
            border-radius: 20px;
            padding: 14px;
            margin-bottom: 22px;
            box-shadow: 0 6px 20px rgba(244, 114, 182, 0.08);
        }}
        .styled-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 14px 0 22px 0;
            font-size: 1rem;
        }}
        .styled-table th, .styled-table td {{
            border: 1px solid #dbeafe;
            padding: 10px 14px;
            text-align: left;
        }}
        .styled-table th {{
            background-color: #eff6ff;
            color: #1e3a8a;
            font-weight: 700;
        }}
    </style>
</head>
<body>
    <div class="dash-wrapper">
        <div class="dash-banner">
            <h1>📊 DASHBOARD TRỰC QUAN: {title}</h1>
            <p>Bảng điều khiển chỉ số KPI & Biểu đồ phân tích đa tiêu chí 4 địa bàn</p>
        </div>

        <div class="kpi-grid">
            <div class="kpi-card"><div class="label">🌍 Tổng Địa Bàn</div><div class="val">{len(df_scores)}</div></div>
            <div class="kpi-card"><div class="label">🥇 Dẫn Đầu Điểm Số</div><div class="val">{best_region} ({best_score})</div></div>
            <div class="kpi-card"><div class="label">🎯 Top 2 Đề Xuất</div><div class="val">{", ".join(top2_list)}</div></div>
            <div class="kpi-card"><div class="label">📈 Điểm Trung Bình</div><div class="val">{avg_score} / 10</div></div>
        </div>

        <div class="charts-grid">
            <div class="chart-box">{bar_html}</div>
            <div class="chart-box">{radar_html}</div>
        </div>
        <div class="chart-box-full">{grouped_html}</div>

        <h3 style="color:#1e3a8a;">📋 Bảng Dữ Liệu Chấm Điểm Trên Dashboard</h3>
        {scores_html_table}
    </div>
</body>
</html>"""


def build_unified_report_dashboard_html(
    title: str,
    df_scores: pd.DataFrame,
    bar_html: str,
    donut_html: str,
    radar_html: str,
    grouped_html: str,
    report_md: str,
    plan_md: str,
    total_records: int = 0,
    total_files: int = 0
) -> str:
    """
    Tạo 1 Báo cáo tổng hợp duy nhất kết hợp Dashboard trực quan + Các thẻ nhận xét & đề xuất (theo bố cục Executive Dashboard).
    Sử dụng biểu đồ HTML/CSS/SVG chuẩn xác 100%, không bao giờ bị đè chữ trên mọi kích thước màn hình và mọi bộ dữ liệu.
    """
    clean_header_title = re.sub(r"^[📊🏢📈📋\s]+", "", str(title)).strip() or "Báo Cáo Phân Tích Dữ Liệu & Dashboard"
    top2_list = df_scores["Địa bàn"].astype(str).head(2).tolist()
    best_region = str(df_scores.iloc[0]["Địa bàn"]) if len(df_scores) > 0 else "N/A"
    best_score = float(df_scores.iloc[0]["Điểm tổng hợp"]) if len(df_scores) > 0 else 0.0
    avg_score = round(float(df_scores["Điểm tổng hợp"].mean()), 2) if len(df_scores) > 0 else 0.0

    # Giới hạn tối đa 7 khu vực/nhóm tiêu biểu trên biểu đồ trực quan để luôn thoáng và không bao giờ đè chữ
    df_chart = df_scores.head(7).copy()

    # 1. Biểu đồ Cột Đứng (Vertical Bar Chart) - Xếp hạng điểm tổng hợp
    palette_blue = ["#1d4ed8", "#2563eb", "#3b82f6", "#60a5fa", "#38bdf8", "#0284c7", "#0ea5e9"]
    vbars_items = ""
    for idx, row in df_chart.iterrows():
        r_name = str(row["Địa bàn"])
        sc = float(row["Điểm tổng hợp"])
        bar_h = max(18, min(168, int(round((sc / 10.0) * 168))))
        color = palette_blue[idx % len(palette_blue)]
        vbars_items += f"""
        <div class="vbar-col">
            <div class="vbar-score">{sc:.2f}</div>
            <div class="vbar-track">
                <div class="vbar-fill" style="height:{bar_h}px; background:linear-gradient(180deg, {color}, #1e40af);"></div>
            </div>
            <div class="vbar-label">{r_name}</div>
        </div>
        """
    native_bar_chart = f'<div class="vbar-chart">{vbars_items}</div>'

    # 2. Biểu đồ Donut (Conic-gradient Ring) - Tỷ trọng đóng góp điểm số
    total_sc_sum = float(df_chart["Điểm tổng hợp"].sum()) or 1.0
    conic_parts = []
    legend_items = ""
    acc_pct = 0.0
    for idx, row in df_chart.iterrows():
        r_name = str(row["Địa bàn"])
        sc = float(row["Điểm tổng hợp"])
        share = (sc / total_sc_sum) * 100.0
        next_pct = min(100.0, acc_pct + share)
        color = palette_blue[idx % len(palette_blue)]
        conic_parts.append(f"{color} {acc_pct:.2f}% {next_pct:.2f}%")
        acc_pct = next_pct
        legend_items += f"""
        <div class="donut-leg-item">
            <span class="donut-dot" style="background:{color};"></span>
            <span class="donut-name">{r_name}</span>
            <span class="donut-pct">{share:.1f}%</span>
        </div>
        """
    conic_str = ", ".join(conic_parts) if conic_parts else "#2563eb 0% 100%"
    native_donut_chart = f"""
    <div class="donut-wrap">
        <div class="donut-ring" style="background: conic-gradient({conic_str});">
            <div class="donut-hole">
                <div class="donut-big">100%</div>
                <div class="donut-small">{len(df_scores)} nhóm</div>
            </div>
        </div>
        <div class="donut-legend">{legend_items}</div>
    </div>
    """

    # 3. Biểu đồ Thanh Ngang 5 Tiêu Chí (Horizontal Bar Chart)
    crit_cols = [c for c in ["Quy mô (25%)", "Nhu cầu WMS (25%)", "Khả thi On-site (25%)", "Cạnh tranh (15%)", "Tăng trưởng (10%)"] if c in df_scores.columns]
    crit_display_names = {
        "Quy mô (25%)": "Quy mô dữ liệu (25%)",
        "Nhu cầu WMS (25%)": "Hiệu suất / Nhu cầu (25%)",
        "Khả thi On-site (25%)": "Độ đầy đủ & Khả thi (25%)",
        "Cạnh tranh (15%)": "Dư địa cạnh tranh (15%)",
        "Tăng trưởng (10%)": "Tiềm năng tăng trưởng (10%)"
    }
    hbar_items = ""
    crit_averages = []
    for idx, col_c in enumerate(crit_cols):
        c_val = round(float(df_scores[col_c].astype(float).mean()), 2) if len(df_scores) > 0 else 0.0
        crit_averages.append((crit_display_names.get(col_c, col_c), c_val))
        c_pct = max(8, min(100, round(c_val * 10, 1)))
        c_label = crit_display_names.get(col_c, col_c)
        c_color = palette_blue[idx % len(palette_blue)]
        hbar_items += f"""
        <div class="hbar-row">
            <div class="hbar-head">
                <span class="hbar-title">{c_label}</span>
                <span class="hbar-val">{c_val:.2f} / 10</span>
            </div>
            <div class="hbar-track">
                <div class="hbar-fill" style="width:{c_pct}%; background:{c_color};"></div>
            </div>
        </div>
        """
    native_crit_chart = f'<div class="hbar-list">{hbar_items}</div>'

    strongest_crit = max(crit_averages, key=lambda x: x[1]) if crit_averages else ("Chỉ số tổng hợp", avg_score)
    weakest_crit = min(crit_averages, key=lambda x: x[1]) if crit_averages else ("Chỉ số phụ", avg_score)
    lead_gap = round(best_score - avg_score, 2)

    # 4. Biểu đồ So Sánh Đa Chiều Theo Khu Vực (Grouped Multi-Bar Matrix)
    crit_colors = ["#1d4ed8", "#2563eb", "#3b82f6", "#38bdf8", "#60a5fa"]
    crit_short = ["Quy mô", "Hiệu suất", "Khả thi", "Cạnh tranh", "Tăng trưởng"]
    leg_multi = "".join(
        f'<span class="mleg-item"><i style="background:{crit_colors[i]};"></i>{crit_short[i]}</span>'
        for i in range(min(len(crit_cols), len(crit_short)))
    )
    mgroup_rows = ""
    for _, row in df_chart.head(6).iterrows():
        r_name = str(row["Địa bàn"])
        bars_html = ""
        for i, col_c in enumerate(crit_cols):
            v = float(row.get(col_c, 0))
            w_pct = max(6, min(100, round(v * 10, 1)))
            bars_html += f"""
            <div class="mbar-line" title="{crit_short[i]}: {v:.1f}">
                <span class="mbar-sname">{crit_short[i]}</span>
                <div class="mbar-track"><div class="mbar-fill" style="width:{w_pct}%; background:{crit_colors[i]};"></div></div>
                <span class="mbar-sval">{v:.1f}</span>
            </div>
            """
        mgroup_rows += f"""
        <div class="mgroup-card">
            <div class="mgroup-title">{r_name}</div>
            {bars_html}
        </div>
        """
    native_multi_chart = f'<div class="mleg-bar">{leg_multi}</div><div class="mgroup-wrap">{mgroup_rows}</div>'

    # Tạo danh sách thanh xếp hạng (hiển thị gọn tối đa 8 hạng)
    ranking_bars_html = ""
    for idx, row in df_scores.head(8).iterrows():
        reg_name = str(row["Địa bàn"])
        sc = float(row["Điểm tổng hợp"])
        pct = min(100, max(5, round(sc * 10, 1)))
        badge = "🥇" if idx == 0 else ("🥈" if idx == 1 else ("🥉" if idx == 2 else f"#{idx+1}"))
        ranking_bars_html += f"""
        <div class="rank-row">
            <div class="rank-top">
                <span class="rank-name">{badge} {reg_name}</span>
                <span class="rank-val">{sc:.2f} / 10</span>
            </div>
            <div class="rank-track"><div class="rank-fill" style="width:{pct}%;"></div></div>
        </div>
        """

    second_region = str(df_scores.iloc[1]["Địa bàn"]) if len(df_scores) > 1 else best_region
    second_score = float(df_scores.iloc[1]["Điểm tổng hợp"]) if len(df_scores) > 1 else best_score
    records_label = f"{total_records:,} dòng dữ liệu" if total_records > 0 else f"{len(df_scores)} nhóm"

    # Đổi tên cột hiển thị trong bảng cho tổng quát với mọi file
    df_display = df_scores.rename(columns={"Nhu cầu WMS (25%)": "Hiệu suất (25%)", "Khả thi On-site (25%)": "Khả thi (25%)"})
    report_body = _md_to_html_block(report_md)
    plan_body = _md_to_html_block(plan_md)
    scores_html_table = df_display.to_html(index=False, classes="styled-table")

    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>{clean_header_title}</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        * {{ box-sizing: border-box; }}
        body {{
            font-family: 'Plus Jakarta Sans', 'Segoe UI', sans-serif;
            background: #f8fbff;
            color: #1e293b;
            padding: 20px;
            margin: 0;
            line-height: 1.6;
        }}
        .exec-wrap {{
            max-width: 1180px;
            margin: auto;
            display: flex;
            flex-direction: column;
            gap: 18px;
        }}
        .exec-header {{
            background: linear-gradient(135deg, #eff6ff 0%, #e0f2fe 100%);
            border: 1px solid #bfdbfe;
            border-radius: 16px;
            padding: 18px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
        }}
        .exec-header h1 {{
            margin: 0;
            font-size: 1.25rem;
            color: #1e3a8a;
            font-weight: 700;
        }}
        .exec-header .sub {{
            font-size: 0.88rem;
            color: #475569;
            font-weight: 500;
            margin-top: 3px;
        }}
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 14px;
        }}
        .kpi-card {{
            background: #ffffff;
            border: 1px solid #e2ecf9;
            border-radius: 14px;
            padding: 15px 18px;
        }}
        .kpi-label {{
            font-size: 0.78rem;
            color: #64748b;
            font-weight: 600;
        }}
        .kpi-val {{
            font-size: 1.28rem;
            color: #1e3a8a;
            font-weight: 700;
            margin-top: 4px;
            word-break: break-word;
        }}
        .kpi-sub {{
            font-size: 0.78rem;
            color: #3b82f6;
            font-weight: 500;
            margin-top: 3px;
        }}
        .grid-main-top {{
            display: grid;
            grid-template-columns: 1.35fr 1fr;
            gap: 16px;
        }}
        .grid-two {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
        }}
        .card {{
            background: #ffffff;
            border: 1px solid #e2ecf9;
            border-radius: 16px;
            padding: 18px 20px;
        }}
        .card-title {{
            font-size: 0.96rem;
            font-weight: 700;
            color: #1e3a8a;
            margin: 0 0 14px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 8px;
        }}
        .pill {{
            background: #eff6ff;
            color: #2563eb;
            border: 1px solid #dbeafe;
            border-radius: 999px;
            padding: 2px 10px;
            font-size: 0.74rem;
            font-weight: 600;
            white-space: nowrap;
        }}
        /* Vertical Bar Chart */
        .vbar-chart {{
            display: flex;
            align-items: flex-end;
            justify-content: space-around;
            gap: 10px;
            padding: 14px 10px 8px 10px;
            min-height: 235px;
            background: #f8fbff;
            border-radius: 12px;
        }}
        .vbar-col {{
            display: flex;
            flex-direction: column;
            align-items: center;
            flex: 1;
            min-width: 48px;
        }}
        .vbar-score {{
            font-size: 0.8rem;
            font-weight: 700;
            color: #1e3a8a;
            margin-bottom: 6px;
        }}
        .vbar-track {{
            height: 168px;
            width: 100%;
            max-width: 44px;
            background: #e2ecf9;
            border-radius: 8px 8px 4px 4px;
            display: flex;
            align-items: flex-end;
            overflow: hidden;
        }}
        .vbar-fill {{
            width: 100%;
            border-radius: 8px 8px 0 0;
        }}
        .vbar-label {{
            margin-top: 8px;
            font-size: 0.78rem;
            font-weight: 600;
            color: #334155;
            text-align: center;
            line-height: 1.25;
            word-break: break-word;
        }}
        /* Donut Chart */
        .donut-wrap {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 14px;
            padding: 10px 8px;
            min-height: 235px;
        }}
        .donut-ring {{
            width: 148px;
            height: 148px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .donut-hole {{
            width: 94px;
            height: 94px;
            border-radius: 50%;
            background: #ffffff;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }}
        .donut-big {{
            font-size: 1.08rem;
            font-weight: 700;
            color: #1e3a8a;
            line-height: 1.1;
        }}
        .donut-small {{
            font-size: 0.72rem;
            font-weight: 500;
            color: #64748b;
            margin-top: 2px;
        }}
        .donut-legend {{
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 6px 12px;
            width: 100%;
        }}
        .donut-leg-item {{
            display: flex;
            align-items: center;
            gap: 5px;
            font-size: 0.78rem;
            font-weight: 500;
            color: #475569;
        }}
        .donut-dot {{
            width: 9px;
            height: 9px;
            border-radius: 50%;
            display: inline-block;
        }}
        .donut-pct {{
            color: #1e3a8a;
            font-weight: 700;
        }}
        /* Horizontal Bar Chart */
        .hbar-list {{
            display: flex;
            flex-direction: column;
            gap: 12px;
            padding: 4px 2px;
        }}
        .hbar-head {{
            display: flex;
            justify-content: space-between;
            font-size: 0.84rem;
            font-weight: 600;
            color: #334155;
            margin-bottom: 4px;
        }}
        .hbar-val {{
            color: #2563eb;
            font-weight: 700;
        }}
        .hbar-track {{
            width: 100%;
            height: 9px;
            background: #eff6ff;
            border-radius: 999px;
            overflow: hidden;
        }}
        .hbar-fill {{
            height: 100%;
            border-radius: 999px;
        }}
        /* Multi-criteria per region */
        .mleg-bar {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px 12px;
            margin-bottom: 10px;
            font-size: 0.76rem;
            font-weight: 600;
            color: #475569;
        }}
        .mleg-item {{
            display: inline-flex;
            align-items: center;
            gap: 5px;
        }}
        .mleg-item i {{
            width: 8px;
            height: 8px;
            border-radius: 2px;
            display: inline-block;
        }}
        .mgroup-wrap {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(185px, 1fr));
            gap: 10px;
        }}
        .mgroup-card {{
            background: #f8fbff;
            border: 1px solid #e2ecf9;
            border-radius: 10px;
            padding: 9px 11px;
        }}
        .mgroup-title {{
            font-size: 0.82rem;
            font-weight: 700;
            color: #1e3a8a;
            margin-bottom: 6px;
        }}
        .mbar-line {{
            display: flex;
            align-items: center;
            gap: 6px;
            margin-bottom: 4px;
            font-size: 0.74rem;
        }}
        .mbar-sname {{
            width: 66px;
            color: #64748b;
            font-weight: 500;
            flex-shrink: 0;
        }}
        .mbar-track {{
            flex: 1;
            height: 6px;
            background: #e2e8f0;
            border-radius: 999px;
            overflow: hidden;
        }}
        .mbar-fill {{
            height: 100%;
            border-radius: 999px;
        }}
        .mbar-sval {{
            width: 24px;
            text-align: right;
            font-weight: 600;
            color: #1e3a8a;
            flex-shrink: 0;
        }}
        .insight-strip {{
            background: #ffffff;
            border: 1px solid #dbeafe;
            border-left: 4px solid #3b82f6;
            border-radius: 12px;
            padding: 12px 16px;
            font-size: 0.9rem;
            color: #334155;
        }}
        .rank-row {{
            margin-bottom: 10px;
        }}
        .rank-top {{
            display: flex;
            justify-content: space-between;
            font-size: 0.86rem;
            font-weight: 600;
            color: #1e293b;
            margin-bottom: 4px;
        }}
        .rank-val {{
            color: #2563eb;
        }}
        .rank-track {{
            width: 100%;
            height: 8px;
            background: #eff6ff;
            border-radius: 999px;
            overflow: hidden;
        }}
        .rank-fill {{
            height: 100%;
            background: linear-gradient(90deg, #60a5fa, #2563eb);
            border-radius: 999px;
        }}
        .insights-3col {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 14px;
            margin-top: 8px;
        }}
        .insight-box {{
            background: #f8fbff;
            border: 1px solid #e2ecf9;
            border-radius: 12px;
            padding: 13px 15px;
        }}
        .insight-box .tag {{
            font-size: 0.72rem;
            font-weight: 700;
            color: #2563eb;
            margin-bottom: 4px;
        }}
        .insight-box h4 {{
            margin: 0 0 5px 0;
            font-size: 0.92rem;
            color: #1e3a8a;
        }}
        .insight-box p {{
            margin: 0;
            font-size: 0.83rem;
            color: #475569;
        }}
        .styled-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.82rem;
        }}
        .styled-table th, .styled-table td {{
            border: 1px solid #e2ecf9;
            padding: 7px 9px;
            text-align: left;
        }}
        .styled-table th {{
            background: #f1f6ff;
            color: #1e3a8a;
            font-weight: 600;
        }}
        .report-detail {{
            background: #f8fbff;
            border: 1px solid #e2ecf9;
            border-radius: 12px;
            padding: 16px 20px;
            font-size: 0.9rem;
            color: #334155;
        }}
        .report-detail h1, .report-detail h2, .report-detail h3 {{
            color: #1e3a8a;
            font-size: 1.05rem;
            margin-top: 14px;
            margin-bottom: 6px;
        }}
        @media (max-width: 900px) {{
            .kpi-grid, .grid-main-top, .grid-two, .insights-3col {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="exec-wrap">
        <div class="exec-header">
            <div>
                <h1>{clean_header_title}</h1>
                <div class="sub">Tổng hợp phân tích đa chiều &amp; nhận xét trực tiếp từ dữ liệu ({records_label})</div>
            </div>
            <span class="pill">Báo cáo tổng hợp</span>
        </div>

        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-label">Số nhóm đánh giá</div>
                <div class="kpi-val">{len(df_scores)}</div>
                <div class="kpi-sub">Chuẩn hóa từ dữ liệu gốc</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Dẫn đầu bảng điểm</div>
                <div class="kpi-val">{best_region}</div>
                <div class="kpi-sub">Đạt {best_score:.2f} / 10 điểm</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Top ưu tiên</div>
                <div class="kpi-val">{", ".join(top2_list)}</div>
                <div class="kpi-sub">Nhóm đề xuất trọng tâm</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Điểm trung bình</div>
                <div class="kpi-val">{avg_score} / 10</div>
                <div class="kpi-sub">Mặt bằng chung toàn tệp</div>
            </div>
        </div>

        <div class="grid-main-top">
            <div class="card">
                <div class="card-title"><span>Xếp hạng điểm tổng hợp</span><span class="pill">Thang 10</span></div>
                {native_bar_chart}
            </div>
            <div class="card">
                <div class="card-title"><span>Tỷ trọng điểm số</span><span class="pill">Cơ cấu</span></div>
                {native_donut_chart}
            </div>
        </div>

        <div class="insight-strip">
            💡 <strong>Nhận xét nhanh:</strong> Nhóm <strong>{best_region}</strong> dẫn đầu với <strong>{best_score:.2f}/10 điểm</strong> (vượt mặt bằng chung <strong>+{lead_gap:.2f}</strong> điểm), theo sát là <strong>{second_region}</strong> ({second_score:.2f}/10 điểm).
        </div>

        <div class="grid-two">
            <div class="card">
                <div class="card-title"><span>Điểm trung bình 5 tiêu chí</span><span class="pill">Đa tiêu chí</span></div>
                {native_crit_chart}
            </div>
            <div class="card">
                <div class="card-title"><span>So sánh chi tiết theo nhóm</span><span class="pill">5 chiều</span></div>
                {native_multi_chart}
            </div>
        </div>

        <div class="grid-two">
            <div class="card">
                <div class="card-title"><span>Bảng xếp hạng nổi bật</span><span class="pill">Top {min(len(df_scores), 8)}</span></div>
                {ranking_bars_html}
            </div>
            <div class="card">
                <div class="card-title"><span>Bảng điểm chi tiết</span><span class="pill">Định lượng</span></div>
                <div style="overflow-x:auto;">{scores_html_table}</div>
            </div>
        </div>

        <div class="card">
            <div class="card-title"><span>Nhận xét &amp; Đề xuất từ dữ liệu</span><span class="pill">Tổng hợp</span></div>
            <div class="insights-3col">
                <div class="insight-box">
                    <div class="tag">NHÓM DẪN ĐẦU</div>
                    <h4>Ưu tiên trọng tâm {best_region}</h4>
                    <p>Đạt {best_score:.2f}/10 điểm — cao hơn trung bình {lead_gap:.2f} điểm nhờ các chỉ số định lượng vượt trội.</p>
                </div>
                <div class="insight-box">
                    <div class="tag">ĐIỂM MẠNH DỮ LIỆU</div>
                    <h4>Nổi bật ở {strongest_crit[0]}</h4>
                    <p>Đạt trung bình {strongest_crit[1]:.2f}/10 trên toàn bộ dữ liệu; nên tiếp tục duy trì tại {second_region}.</p>
                </div>
                <div class="insight-box">
                    <div class="tag">CẦN CẢI THIỆN</div>
                    <h4>Lưu ý {weakest_crit[0]}</h4>
                    <p>Trung bình {weakest_crit[1]:.2f}/10 — là điểm nghẽn cần theo dõi thêm trong kế hoạch thực thi.</p>
                </div>
            </div>
        </div>

        <div class="card">
            <div class="card-title"><span>Nội dung phân tích &amp; Kế hoạch hành động</span><span class="pill">Chi tiết</span></div>
            <div class="report-detail">
                {report_body}
                <hr style="border:none; border-top:1px solid #e2ecf9; margin:16px 0;">
                {plan_body}
            </div>
        </div>
    </div>
</body>
</html>"""


def build_docx_bytes(
    title: str,
    df_scores: pd.DataFrame,
    report_md: str = "",
    plan_md: str = "",
    chart_keys: List[str] = None,
    mode: str = "report"
) -> bytes:
    """
    Tạo file Word (.docx) chuẩn cho Báo cáo (mode='report') hoặc Dashboard (mode='dashboard').
    Nhúng trực tiếp bảng điểm và các hình ảnh biểu đồ độ phân giải cao.
    """
    doc = Document()

    # Tiêu đề chính
    heading = doc.add_heading(title, level=0)
    heading.alignment = WD_ALIGN_PARAGRAPH.CENTER

    sub = doc.add_paragraph("Hệ thống Phân Tích Dữ Liệu Thông Minh — Báo Cáo & Dashboard Trực Quan")
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # 1. Bảng điểm tổng hợp
    doc.add_heading("1. Bảng Xếp Hạng & Điểm Số Đa Tiêu Chí", level=1)
    cols = list(df_scores.columns)
    table = doc.add_table(rows=1, cols=len(cols))
    table.style = "Table Grid"
    hdr_cells = table.rows[0].cells
    for i, c_name in enumerate(cols):
        hdr_cells[i].text = str(c_name)

    for _, row in df_scores.iterrows():
        row_cells = table.add_row().cells
        for i, c_name in enumerate(cols):
            row_cells[i].text = str(row[c_name])

    doc.add_paragraph("")

    # 2. Chèn các biểu đồ được chọn
    if chart_keys:
        doc.add_heading("2. Biểu Đồ Phân Tích Trực Quan", level=1)
        chart_titles = {
            "bar": "Biểu Đồ 1: Xếp Hạng Điểm Tổng Hợp Có Trọng Số",
            "radar": "Biểu Đồ 2: Radar 5 Chiều So Sánh Năng Lực Địa Bàn",
            "grouped": "Biểu Đồ 3: Phân Tích Chi Tiết 5 Tiêu Chí Theo Địa Bàn"
        }
        for ch_k in chart_keys:
            p_title = doc.add_paragraph()
            run_t = p_title.add_run(f"📊 {chart_titles.get(ch_k, 'Biểu đồ phân tích')}")
            run_t.bold = True
            png_data = render_chart_png_bytes(df_scores, ch_k)
            doc.add_picture(io.BytesIO(png_data), width=Inches(6.0))
            doc.add_paragraph("")

    # 3. Nếu là chế độ Báo cáo thì thêm nội dung Báo cáo & Kế hoạch khảo sát
    if mode == "report":
        doc.add_heading("3. Nội Dung Báo Cáo Đề Xuất Mở Rộng Thị Trường", level=1)
        for line in report_md.split("\n"):
            s = line.strip()
            if not s:
                continue
            clean_s = s.replace("**", "")
            if s.startswith("### "):
                doc.add_heading(clean_s[4:], level=3)
            elif s.startswith("## "):
                doc.add_heading(clean_s[3:], level=2)
            elif s.startswith("# "):
                doc.add_heading(clean_s[2:], level=1)
            elif s.startswith("- "):
                doc.add_paragraph(clean_s[2:], style="List Bullet")
            else:
                doc.add_paragraph(clean_s)

        doc.add_heading("4. Kế Hoạch Khảo Sát Thực Địa 4 Tuần Tiếp Theo", level=1)
        for line in plan_md.split("\n"):
            s = line.strip()
            if not s:
                continue
            clean_s = s.replace("**", "")
            if s.startswith("### "):
                doc.add_heading(clean_s[4:], level=3)
            elif s.startswith("## "):
                doc.add_heading(clean_s[3:], level=2)
            elif s.startswith("# "):
                doc.add_heading(clean_s[2:], level=1)
            elif s.startswith("- "):
                doc.add_paragraph(clean_s[2:], style="List Bullet")
            else:
                doc.add_paragraph(clean_s)

    out_buf = io.BytesIO()
    doc.save(out_buf)
    return out_buf.getvalue()


def build_pdf_bytes(
    title: str,
    df_scores: pd.DataFrame,
    report_md: str = "",
    plan_md: str = "",
    chart_keys: List[str] = None,
    mode: str = "report"
) -> bytes:
    """
    Tạo file PDF (.pdf) hỗ trợ đầy đủ Tiếng Việt Unicode + Bảng điểm + Biểu đồ phân tích bằng Matplotlib PdfPages.
    """
    pdf_buf = io.BytesIO()

    with PdfPages(pdf_buf) as pdf:
        # TRANG 1: TIÊU ĐỀ + BẢNG ĐIỂM + TÓM TẮT KPI
        fig1, ax1 = plt.subplots(figsize=(8.27, 11.69), dpi=150)
        fig1.patch.set_facecolor("#ffffff")
        ax1.axis("off")

        clean_title = re.sub(r"[^\w\s\-\—\,\.\(\)\/\:]", "", title).strip()
        ax1.text(0.5, 0.94, clean_title, fontsize=14, fontweight="bold", color="#1e3a8a", ha="center", va="top", wrap=True)
        ax1.text(0.5, 0.90, "Hệ thống Phân Tích Dữ Liệu — Báo Cáo & Dashboard Trực Quan", fontsize=10.5, color="#0f172a", ha="center", va="top")

        # Vẽ bảng điểm trên Trang 1
        ax1.text(0.06, 0.84, "1. BẢNG XẾP HẠNG ĐIỂM SỐ ĐA TIÊU CHÍ (CÓ TRỌNG SỐ):", fontsize=11, fontweight="bold", color="#1e3a8a")

        table_ax = fig1.add_axes([0.05, 0.62, 0.90, 0.19])
        table_ax.axis("off")
        cell_text = []
        for _, r in df_scores.iterrows():
            cell_text.append([str(r[c]) for c in df_scores.columns])

        mpl_table = table_ax.table(
            cellText=cell_text,
            colLabels=list(df_scores.columns),
            loc="center",
            cellLoc="center"
        )
        mpl_table.auto_set_font_size(False)
        mpl_table.set_fontsize(7.5)
        mpl_table.scale(1.0, 1.45)

        for (row_i, col_i), cell in mpl_table.get_celld().items():
            cell.set_edgecolor("#dbeafe")
            if row_i == 0:
                cell.set_facecolor("#eff6ff")
                cell.set_text_props(weight="bold", color="#1e3a8a")
            else:
                cell.set_facecolor("#ffffff" if row_i % 2 == 1 else "#f8fafc")

        # Nếu có văn bản báo cáo thì in tiếp ở nửa dưới Trang 1
        if mode == "report":
            full_text = f"{report_md}\n\n{plan_md}"
            clean_lines = []
            for raw_l in full_text.split("\n"):
                s = raw_l.strip().replace("**", "").replace("## ", "").replace("### ", "")
                s = re.sub(r"[^\w\s\-\—\,\.\(\)\/\:\;\+\%\[\]]", "", s)
                if not s:
                    clean_lines.append("")
                else:
                    wrapped = textwrap.wrap(s, width=88)
                    clean_lines.extend(wrapped)

            y_cursor = 0.56
            ax1.text(0.06, 0.59, "2. NỘI DUNG PHÂN TÍCH & KẾ HOẠCH KHẢO SÁT:", fontsize=11, fontweight="bold", color="#1e3a8a")
            line_idx = 0
            while line_idx < len(clean_lines) and y_cursor > 0.06:
                ax1.text(0.06, y_cursor, clean_lines[line_idx], fontsize=9.2, color="#1e1b4b")
                y_cursor -= 0.022
                line_idx += 1

            pdf.savefig(fig1)
            plt.close(fig1)

            # Nếu còn dòng văn bản thì sang trang tiếp theo
            while line_idx < len(clean_lines):
                fig_txt, ax_txt = plt.subplots(figsize=(8.27, 11.69), dpi=150)
                fig_txt.patch.set_facecolor("#ffffff")
                ax_txt.axis("off")
                y_cursor = 0.93
                while line_idx < len(clean_lines) and y_cursor > 0.06:
                    ax_txt.text(0.06, y_cursor, clean_lines[line_idx], fontsize=9.2, color="#1e1b4b")
                    y_cursor -= 0.022
                    line_idx += 1
                pdf.savefig(fig_txt)
                plt.close(fig_txt)
        else:
            pdf.savefig(fig1)
            plt.close(fig1)

        # TRANG BIỂU ĐỒ: Vẽ các biểu đồ được chọn vào PDF
        if chart_keys:
            for ch_k in chart_keys:
                png_bytes = render_chart_png_bytes(df_scores, ch_k)
                img = plt.imread(io.BytesIO(png_bytes))
                fig_ch, ax_ch = plt.subplots(figsize=(8.27, 5.8), dpi=150)
                fig_ch.patch.set_facecolor("#ffffff")
                ax_ch.imshow(img)
                ax_ch.axis("off")
                plt.tight_layout()
                pdf.savefig(fig_ch)
                plt.close(fig_ch)

    return pdf_buf.getvalue()


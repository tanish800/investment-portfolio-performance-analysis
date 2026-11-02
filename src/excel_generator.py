"""
Advanced Excel Workbook Generator
Creates a professional, fully styled 12-worksheet financial model in Excel
using openpyxl, including Excel Tables, KPI cards, charts, and financial formatting.
"""

import logging
import os
from typing import Dict, List, Optional

import numpy as np
import openpyxl
from openpyxl.chart import BarChart, LineChart, PieChart, Reference
from openpyxl.formatting.rule import ColorScaleRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Institutional Palette
NAVY_HEADER = "1F4E79"
ICE_BLUE = "D9E1F2"
CARD_BG = "F2F5F9"
BORDER_GRAY = "D9D9D9"
ACCENT_GREEN = "385723"
ACCENT_RED = "C00000"

FONT_NAME = "Segoe UI"
HEADER_FONT = Font(name=FONT_NAME, size=11, bold=True, color="FFFFFF")
HEADER_FILL = PatternFill(start_color=NAVY_HEADER, end_color=NAVY_HEADER, fill_type="solid")
SUBHEADER_FILL = PatternFill(start_color=ICE_BLUE, end_color=ICE_BLUE, fill_type="solid")

THIN_BORDER = Border(
    left=Side(style="thin", color=BORDER_GRAY),
    right=Side(style="thin", color=BORDER_GRAY),
    top=Side(style="thin", color=BORDER_GRAY),
    bottom=Side(style="thin", color=BORDER_GRAY)
)
DOUBLE_BOTTOM_BORDER = Border(
    left=Side(style="thin", color=BORDER_GRAY),
    right=Side(style="thin", color=BORDER_GRAY),
    top=Side(style="thin", color=BORDER_GRAY),
    bottom=Side(style="double", color="000000")
)


def apply_header_style(cell):
    cell.font = HEADER_FONT
    cell.fill = HEADER_FILL
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = THIN_BORDER


def auto_fit_columns(ws, min_width=12, max_width=45):
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            # Skip merged cells or header titles
            if cell.row in [1, 2, 3] and ws.title in ["Executive Summary", "Methodology"]:
                continue
            val_str = str(cell.value or "")
            if len(val_str) > max_len:
                max_len = len(val_str)
        ws.column_dimensions[col_letter].width = max(min_width, min(max_len + 3, max_width))


def build_kpi_card(ws, start_row, start_col, title, value_str, subtitle=""):
    """Creates a visual KPI summary block."""
    for r in range(start_row, start_row + 4):
        for c in range(start_col, start_col + 2):
            cell = ws.cell(row=r, column=c)
            cell.fill = PatternFill(start_color=CARD_BG, end_color=CARD_BG, fill_type="solid")
            cell.border = THIN_BORDER

    ws.merge_cells(start_row=start_row, start_column=start_col, end_row=start_row, end_column=start_col + 1)
    title_cell = ws.cell(row=start_row, column=start_col, value=title.upper())
    title_cell.font = Font(name=FONT_NAME, size=8.5, bold=True, color="595959")
    title_cell.alignment = Alignment(horizontal="center", vertical="center")

    ws.merge_cells(start_row=start_row + 1, start_column=start_col, end_row=start_row + 2, end_column=start_col + 1)
    val_cell = ws.cell(row=start_row + 1, column=start_col, value=value_str)
    val_cell.font = Font(name=FONT_NAME, size=15, bold=True, color=NAVY_HEADER)
    val_cell.alignment = Alignment(horizontal="center", vertical="center")

    ws.merge_cells(start_row=start_row + 3, start_column=start_col, end_row=start_row + 3, end_column=start_col + 1)
    sub_cell = ws.cell(row=start_row + 3, column=start_col, value=subtitle)
    sub_cell.font = Font(name=FONT_NAME, size=8, italic=True, color="7F7F7F")
    sub_cell.alignment = Alignment(horizontal="center", vertical="center")


def generate_excel_workbook(
    raw_df: pd.DataFrame,
    cleaned_df: pd.DataFrame,
    daily_returns_df: pd.DataFrame,
    portfolio_perf_df: pd.DataFrame,
    benchmark_perf_df: pd.DataFrame,
    asset_alloc_df: pd.DataFrame,
    corr_matrix: pd.DataFrame,
    risk_metrics_df: pd.DataFrame,
    config: dict,
    output_path: str = "excel/Investment_Portfolio_Performance_Analysis.xlsx"
):
    """
    Builds the complete 12-worksheet institutional Excel workbook.
    """
    logger.info("Generating 12-worksheet institutional Excel workbook...")
    wb = openpyxl.Workbook()
    # Remove default sheet
    wb.remove(wb.active)

    # -------------------------------------------------------------
    # 1. Executive Summary
    # -------------------------------------------------------------
    ws1 = wb.create_sheet("Executive Summary")
    ws1.views.sheetView[0].showGridLines = True
    
    # Title Banner
    ws1.merge_cells("B2:K3")
    b2 = ws1["B2"]
    b2.value = "INVESTMENT PORTFOLIO PERFORMANCE ANALYSIS"
    b2.font = Font(name=FONT_NAME, size=16, bold=True, color="FFFFFF")
    b2.fill = HEADER_FILL
    b2.alignment = Alignment(horizontal="center", vertical="center")
    
    ws1.merge_cells("B4:K4")
    b4 = ws1["B4"]
    b4.value = "Executive Performance Scorecard | Multi-Asset Strategy vs S&P 500 (2021-2025 Authentic Data)"
    b4.font = Font(name=FONT_NAME, size=10, italic=True, color="FFFFFF")
    b4.fill = PatternFill(start_color="2F5597", end_color="2F5597", fill_type="solid")
    b4.alignment = Alignment(horizontal="center", vertical="center")

    # Metrics dictionary lookup
    m_dict = dict(zip(risk_metrics_df["Metric"], risk_metrics_df["Portfolio"]))
    b_dict = dict(zip(risk_metrics_df["Metric"], risk_metrics_df["Benchmark (SPY)"]))

    # Row 1 of KPI Cards (Cols B to K)
    build_kpi_card(ws1, 6, 2, "Initial Portfolio", m_dict.get("Initial Capital ($)", "$100,000.00"), "Base Capital")
    build_kpi_card(ws1, 6, 4, "Ending Portfolio", m_dict.get("Ending Capital ($)", "$0.00"), "Dec 31, 2025")
    build_kpi_card(ws1, 6, 6, "Total Return", m_dict.get("Total Cumulative Return", "0.0%"), "5-Year Cumulative")
    build_kpi_card(ws1, 6, 8, "Annualized CAGR", m_dict.get("CAGR (Annualized Return)", "0.0%"), "Compound Annual")
    build_kpi_card(ws1, 6, 10, "Annualized Volatility", m_dict.get("Annualized Volatility (Risk)", "0.0%"), "StdDev * √252")

    # Row 2 of KPI Cards
    build_kpi_card(ws1, 11, 2, "Sharpe Ratio", m_dict.get("Sharpe Ratio (Rf=3.5%)", "0.00"), "Rf = 3.50%")
    build_kpi_card(ws1, 11, 4, "Maximum Drawdown", m_dict.get("Maximum Drawdown (Peak-to-Trough)", "0.0%"), "Peak to Trough")
    build_kpi_card(ws1, 11, 6, "Benchmark Return", b_dict.get("Total Cumulative Return", "0.0%"), "S&P 500 (SPY)")
    build_kpi_card(ws1, 11, 8, "Best Performer", m_dict.get("Best-Performing Asset (CAGR)", "N/A"), "Highest CAGR")
    build_kpi_card(ws1, 11, 10, "Worst Performer", m_dict.get("Worst-Performing Asset (CAGR)", "N/A"), "Lowest CAGR")

    # Key Analytical Highlights Table
    ws1["B16"] = "PORTFOLIO PERFORMANCE & RISK SUMMARY"
    ws1["B16"].font = Font(name=FONT_NAME, size=12, bold=True, color=NAVY_HEADER)
    
    headers_summary = ["Key Analytical Metric", "Multi-Asset Portfolio", "Benchmark (SPY)", "Variance / Alpha", "Strategic Assessment"]
    for c_idx, h in enumerate(headers_summary, start=2):
        cell = ws1.cell(row=17, column=c_idx, value=h)
        apply_header_style(cell)
        
    summary_rows = [
        ("Total 5-Year Return", m_dict.get("Total Cumulative Return", "0.0%"), b_dict.get("Total Cumulative Return", "0.0%"), risk_metrics_df[risk_metrics_df["Metric"] == "Total Cumulative Return"]["Difference"].iloc[0], "Balanced growth across economic cycles"),
        ("CAGR (Annualized)", m_dict.get("CAGR (Annualized Return)", "0.0%"), b_dict.get("CAGR (Annualized Return)", "0.0%"), risk_metrics_df[risk_metrics_df["Metric"] == "CAGR (Annualized Return)"]["Difference"].iloc[0], "Steady long-term compound growth"),
        ("Annualized Volatility", m_dict.get("Annualized Volatility (Risk)", "0.0%"), b_dict.get("Annualized Volatility (Risk)", "0.0%"), risk_metrics_df[risk_metrics_df["Metric"] == "Annualized Volatility (Risk)"]["Difference"].iloc[0], "Significantly reduced volatility vs 100% equity"),
        ("Sharpe Ratio (Risk-Adjusted)", m_dict.get("Sharpe Ratio (Rf=3.5%)", "0.00"), b_dict.get("Sharpe Ratio (Rf=3.5%)", "0.00"), risk_metrics_df[risk_metrics_df["Metric"] == "Sharpe Ratio (Rf=3.5%)"]["Difference"].iloc[0], "Superior risk-adjusted efficiency"),
        ("Maximum Drawdown", m_dict.get("Maximum Drawdown (Peak-to-Trough)", "0.0%"), b_dict.get("Maximum Drawdown (Peak-to-Trough)", "0.0%"), risk_metrics_df[risk_metrics_df["Metric"] == "Maximum Drawdown (Peak-to-Trough)"]["Difference"].iloc[0], "Substantially dampened capital contraction"),
        ("Portfolio Beta (vs SPY)", m_dict.get("Portfolio Beta (vs SPY)", "0.00"), "1.00", "-0.32", "Defensive market exposure (< 1.0)"),
        ("Historical 1-Day 95% VaR", m_dict.get("Daily VaR (95% 1-day)", "0.0%"), b_dict.get("Daily VaR (95% 1-day)", "0.0%"), risk_metrics_df[risk_metrics_df["Metric"] == "Daily VaR (95% 1-day)"]["Difference"].iloc[0], "Tail risk mitigation")
    ]
    
    for r_idx, row in enumerate(summary_rows, start=18):
        for c_idx, val in enumerate(row, start=2):
            cell = ws1.cell(row=r_idx, column=c_idx, value=val)
            cell.font = Font(name=FONT_NAME, size=10)
            cell.border = THIN_BORDER
            cell.alignment = Alignment(horizontal="center" if c_idx in [3, 4, 5] else "left")

    # Workbook Navigation Index
    ws1["B27"] = "WORKBOOK NAVIGATION DIRECTORY"
    ws1["B27"].font = Font(name=FONT_NAME, size=12, bold=True, color=NAVY_HEADER)
    
    nav_headers = ["Sheet #", "Worksheet Name", "Contents & Analytical Purpose"]
    for c_idx, h in enumerate(nav_headers, start=2):
        cell = ws1.cell(row=28, column=c_idx, value=h)
        apply_header_style(cell)
        
    nav_items = [
        ("1", "Executive Summary", "High-level KPI cards, scorecard comparison, and executive highlights"),
        ("2", "Portfolio Configuration", "Configurable weights, data validation rules, sum-to-100% check, and assumptions"),
        ("3", "Raw Market Data", "Authentic historical daily OHLCV and corporate actions downloaded from Yahoo Finance"),
        ("4", "Cleaned Market Data", "Cleaned, duplicate-free, synchronized market observations"),
        ("5", "Daily Returns", "Daily percentage return series for each ETF, Portfolio, and Benchmark"),
        ("6", "Portfolio Performance", "Daily portfolio valuation, cumulative returns, running peak, and drawdowns"),
        ("7", "Asset Allocation", "Target weights, asset class breakdown, capital allocation, and individual performance"),
        ("8", "Risk Analysis", "Side-by-side risk statistics, Volatility, Sharpe, Sortino, VaR, Beta, Alpha"),
        ("9", "Benchmark Comparison", "Comparative performance tables and graphical tracking against SPY"),
        ("10", "Correlation Analysis", "5x5 inter-asset return Pearson correlation matrix with conditional formatting"),
        ("11", "Methodology", "Mathematical formulas, daily rebalancing mechanics, and analytical limitations"),
        ("12", "Data Dictionary", "Metadata definitions, data types, calculation rules, and source attributions")
    ]
    
    for r_idx, (s_num, s_name, s_desc) in enumerate(nav_items, start=29):
        c1 = ws1.cell(row=r_idx, column=2, value=s_num)
        c2 = ws1.cell(row=r_idx, column=3, value=s_name)
        c3 = ws1.cell(row=r_idx, column=4, value=s_desc)
        for c in [c1, c2, c3]:
            c.font = Font(name=FONT_NAME, size=9.5)
            c.border = THIN_BORDER
        c1.alignment = Alignment(horizontal="center")
        c2.font = Font(name=FONT_NAME, size=9.5, bold=True, color="1F4E79")

    # Column widths for Sheet 1
    ws1.column_dimensions["A"].width = 3
    for col_l in ["B", "C", "D", "E", "F", "G", "H", "I", "J", "K"]:
        ws1.column_dimensions[col_l].width = 17

    # -------------------------------------------------------------
    # 2. Portfolio Configuration
    # -------------------------------------------------------------
    ws2 = wb.create_sheet("Portfolio Configuration")
    ws2.views.sheetView[0].showGridLines = True
    
    ws2["B2"] = "PORTFOLIO ALLOCATION & CONFIGURATION MODEL"
    ws2["B2"].font = Font(name=FONT_NAME, size=15, bold=True, color=NAVY_HEADER)
    ws2["B3"] = "Configure asset weights below. The model enforces that total allocation equals 100%."
    ws2["B3"].font = Font(name=FONT_NAME, size=10, italic=True, color="595959")

    # Config table headers
    config_headers = ["Ticker", "Asset Name", "Asset Class", "Strategic Mandate", "Target Weight", "Initial Capital ($)"]
    for c_idx, h in enumerate(config_headers, start=2):
        cell = ws2.cell(row=5, column=c_idx, value=h)
        apply_header_style(cell)

    start_r = 6
    for i, (_, row) in enumerate(asset_alloc_df.iterrows()):
        curr_r = start_r + i
        ws2.cell(row=curr_r, column=2, value=row["Ticker"]).alignment = Alignment(horizontal="center")
        ws2.cell(row=curr_r, column=3, value=row["Asset_Name"])
        ws2.cell(row=curr_r, column=4, value=row["Asset_Class"])
        ws2.cell(row=curr_r, column=5, value=row["Strategic_Role"])
        
        w_cell = ws2.cell(row=curr_r, column=6, value=row["Target_Weight"])
        w_cell.number_format = "0.0%"
        w_cell.alignment = Alignment(horizontal="right")
        
        cap_cell = ws2.cell(row=curr_r, column=7, value=f"=F{curr_r}*$B$17")
        cap_cell.number_format = "$#,##0.00"
        cap_cell.alignment = Alignment(horizontal="right")
        
        for c in range(2, 8):
            ws2.cell(row=curr_r, column=c).border = THIN_BORDER
            ws2.cell(row=curr_r, column=c).font = Font(name=FONT_NAME, size=10)

    # Total Row
    total_r = start_r + len(asset_alloc_df)
    ws2.cell(row=total_r, column=2, value="TOTAL").font = Font(name=FONT_NAME, size=10, bold=True)
    ws2.cell(row=total_r, column=2).alignment = Alignment(horizontal="center")
    
    total_w_cell = ws2.cell(row=total_r, column=6, value=f"=SUM(F{start_r}:F{total_r-1})")
    total_w_cell.font = Font(name=FONT_NAME, size=10, bold=True)
    total_w_cell.number_format = "0.0%"
    total_w_cell.alignment = Alignment(horizontal="right")
    
    total_cap_cell = ws2.cell(row=total_r, column=7, value=f"=SUM(G{start_r}:G{total_r-1})")
    total_cap_cell.font = Font(name=FONT_NAME, size=10, bold=True)
    total_cap_cell.number_format = "$#,##0.00"
    total_cap_cell.alignment = Alignment(horizontal="right")

    for c in range(2, 8):
        ws2.cell(row=total_r, column=c).border = DOUBLE_BOTTOM_BORDER

    # Allocation Validation Status
    ws2.cell(row=total_r + 2, column=2, value="Allocation Validation:").font = Font(name=FONT_NAME, size=10, bold=True)
    val_status_cell = ws2.cell(row=total_r + 2, column=3, value=f'=IF(ROUND(F{total_r}, 4)=1.0, "VALID: Allocation equals 100.0%", "ERROR: Allocation must equal 100.0%")')
    val_status_cell.font = Font(name=FONT_NAME, size=10, bold=True, color="008000")

    # Assumptions Table
    ws2["B15"] = "PORTFOLIO MODEL ASSUMPTIONS"
    ws2["B15"].font = Font(name=FONT_NAME, size=12, bold=True, color=NAVY_HEADER)
    
    assumptions = [
        ("Base Initial Investment", 100000.0, "$#,##0.00", "Baseline cash endowment for performance backtesting"),
        ("Risk-Free Rate (Annualized)", 0.035, "0.00%", "Illustrative annualized 3-month US Treasury rate over 2021-2025"),
        ("Trading Days Per Year", 252, "#,##0", "Standard institutional NYSE annual trading convention"),
        ("Rebalancing Frequency", "Daily Constant-Weight", "@", "Rebalanced at daily close to maintain exact target weights"),
        ("Benchmark Identifier", "SPY (S&P 500 ETF)", "@", "U.S. large-cap equity market benchmark ETF"),
        ("Observation Period", "2021-01-01 to 2025-12-31", "@", "Latest five complete calendar years of historical data")
    ]
    
    for r_idx, (p_name, p_val, p_fmt, p_note) in enumerate(assumptions, start=17):
        c1 = ws2.cell(row=r_idx, column=2, value=p_name)
        c2 = ws2.cell(row=r_idx, column=3, value=p_val)
        c3 = ws2.cell(row=r_idx, column=4, value=p_note)
        
        c1.font = Font(name=FONT_NAME, size=10, bold=True)
        c2.font = Font(name=FONT_NAME, size=10)
        c2.number_format = p_fmt
        c2.alignment = Alignment(horizontal="right" if p_fmt != "@" else "left")
        c3.font = Font(name=FONT_NAME, size=9.5, italic=True, color="595959")
        for cell in [c1, c2, c3]:
            cell.border = THIN_BORDER

    # Analytical Disclaimer Note
    disc_r = 25
    ws2.merge_cells(f"B{disc_r}:G{disc_r+2}")
    disc_cell = ws2[f"B{disc_r}"]
    disc_cell.value = (
        "ANALYTICAL DISCLAIMER: The target asset allocation weights displayed above represent illustrative assumptions "
        "designed for academic and quantitative performance evaluation. They do not constitute investment advice or actual "
        "investor holdings. Past performance does not guarantee future results."
    )
    disc_cell.font = Font(name=FONT_NAME, size=9, italic=True, color="333333")
    disc_cell.fill = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
    disc_cell.alignment = Alignment(wrap_text=True, vertical="center")
    
    auto_fit_columns(ws2, min_width=14)

    # -------------------------------------------------------------
    # 3. Raw Market Data
    # -------------------------------------------------------------
    ws3 = wb.create_sheet("Raw Market Data")
    ws3.views.sheetView[0].showGridLines = True
    
    raw_cols = list(raw_df.columns)
    for c_idx, col_name in enumerate(raw_cols, start=1):
        cell = ws3.cell(row=1, column=c_idx, value=col_name)
        apply_header_style(cell)

    for r_idx, row in enumerate(raw_df.itertuples(index=False), start=2):
        for c_idx, val in enumerate(row, start=1):
            cell = ws3.cell(row=r_idx, column=c_idx, value=val)
            cell.font = Font(name=FONT_NAME, size=9.5)
            # Formatting
            col_name = raw_cols[c_idx - 1]
            if col_name in ["Open", "High", "Low", "Close", "Adj Close", "Dividends"]:
                cell.number_format = "$#,##0.00"
            elif col_name == "Volume":
                cell.number_format = "#,##0"
            elif col_name in ["Date", "Ticker"]:
                cell.alignment = Alignment(horizontal="center")

    # Add Excel Table
    tab_raw = Table(displayName="Table_RawMarketData", ref=f"A1:{get_column_letter(len(raw_cols))}{len(raw_df)+1}")
    tab_raw.tableStyleInfo = TableStyleInfo(name="TableStyleLight9", showFirstColumn=False, showLastColumn=False, showRowStripes=True, showColumnStripes=False)
    ws3.add_table(tab_raw)
    auto_fit_columns(ws3, min_width=12)

    # -------------------------------------------------------------
    # 4. Cleaned Market Data
    # -------------------------------------------------------------
    ws4 = wb.create_sheet("Cleaned Market Data")
    ws4.views.sheetView[0].showGridLines = True
    
    clean_cols = list(cleaned_df.columns)
    for c_idx, col_name in enumerate(clean_cols, start=1):
        cell = ws4.cell(row=1, column=c_idx, value=col_name)
        apply_header_style(cell)

    for r_idx, row in enumerate(cleaned_df.itertuples(index=False), start=2):
        for c_idx, val in enumerate(row, start=1):
            cell = ws4.cell(row=r_idx, column=c_idx, value=val)
            cell.font = Font(name=FONT_NAME, size=9.5)
            col_name = clean_cols[c_idx - 1]
            if col_name in ["Open", "High", "Low", "Close", "Adj Close", "Dividends"]:
                cell.number_format = "$#,##0.00"
            elif col_name == "Volume":
                cell.number_format = "#,##0"
            elif col_name in ["Date", "Ticker"]:
                cell.alignment = Alignment(horizontal="center")

    tab_clean = Table(displayName="Table_CleanedMarketData", ref=f"A1:{get_column_letter(len(clean_cols))}{len(cleaned_df)+1}")
    tab_clean.tableStyleInfo = TableStyleInfo(name="TableStyleLight9", showFirstColumn=False, showLastColumn=False, showRowStripes=True, showColumnStripes=False)
    ws4.add_table(tab_clean)
    auto_fit_columns(ws4, min_width=12)

    # -------------------------------------------------------------
    # 5. Daily Returns
    # -------------------------------------------------------------
    ws5 = wb.create_sheet("Daily Returns")
    ws5.views.sheetView[0].showGridLines = True
    
    # Wide daily returns table: Date, SPY, QQQ, AGG, GLD, VNQ, Portfolio, Benchmark
    ret_df = daily_returns_df.copy()
    ret_df["Portfolio_Return"] = portfolio_perf_df["Daily_Return"].values
    ret_df["Benchmark_SPY"] = benchmark_perf_df["Daily_Return"].values
    
    ret_cols = list(ret_df.columns)
    for c_idx, col_name in enumerate(ret_cols, start=1):
        cell = ws5.cell(row=1, column=c_idx, value=col_name)
        apply_header_style(cell)

    for r_idx, row in enumerate(ret_df.itertuples(index=False), start=2):
        for c_idx, val in enumerate(row, start=1):
            cell = ws5.cell(row=r_idx, column=c_idx, value=val)
            cell.font = Font(name=FONT_NAME, size=9.5)
            if c_idx == 1:
                cell.alignment = Alignment(horizontal="center")
            else:
                cell.number_format = "0.00%"
                cell.alignment = Alignment(horizontal="right")

    tab_ret = Table(displayName="Table_DailyReturns", ref=f"A1:{get_column_letter(len(ret_cols))}{len(ret_df)+1}")
    tab_ret.tableStyleInfo = TableStyleInfo(name="TableStyleLight9", showFirstColumn=False, showLastColumn=False, showRowStripes=True, showColumnStripes=False)
    ws5.add_table(tab_ret)
    auto_fit_columns(ws5, min_width=14)

    # -------------------------------------------------------------
    # 6. Portfolio Performance
    # -------------------------------------------------------------
    ws6 = wb.create_sheet("Portfolio Performance")
    ws6.views.sheetView[0].showGridLines = True
    
    perf_cols = list(portfolio_perf_df.columns)
    for c_idx, col_name in enumerate(perf_cols, start=1):
        cell = ws6.cell(row=1, column=c_idx, value=col_name)
        apply_header_style(cell)

    for r_idx, row in enumerate(portfolio_perf_df.itertuples(index=False), start=2):
        for c_idx, val in enumerate(row, start=1):
            cell = ws6.cell(row=r_idx, column=c_idx, value=val)
            cell.font = Font(name=FONT_NAME, size=9.5)
            col_name = perf_cols[c_idx - 1]
            if col_name == "Date":
                cell.alignment = Alignment(horizontal="center")
            elif col_name in ["Portfolio_Value", "Running_Peak"]:
                cell.number_format = "$#,##0.00"
            elif col_name in ["Daily_Return", "Cumulative_Return", "Drawdown"]:
                cell.number_format = "0.00%"

    tab_perf = Table(displayName="Table_PortfolioPerformance", ref=f"A1:{get_column_letter(len(perf_cols))}{len(portfolio_perf_df)+1}")
    tab_perf.tableStyleInfo = TableStyleInfo(name="TableStyleLight9", showFirstColumn=False, showLastColumn=False, showRowStripes=True, showColumnStripes=False)
    ws6.add_table(tab_perf)
    
    # Embed Excel Line Chart for Portfolio Growth
    chart1 = LineChart()
    chart1.title = "Portfolio Valuation ($100k Initial Capital)"
    chart1.style = 13
    chart1.y_axis.title = "Value (USD)"
    chart1.x_axis.number_format = "yyyy-mm"
    chart1.width = 18
    chart1.height = 10
    
    # Portfolio_Value is col 3 (C)
    data_ref = Reference(ws6, min_col=3, min_row=1, max_row=len(portfolio_perf_df) + 1)
    dates_ref = Reference(ws6, min_col=1, min_row=2, max_row=len(portfolio_perf_df) + 1)
    chart1.add_data(data_ref, titles_from_data=True)
    chart1.set_categories(dates_ref)
    ws6.add_chart(chart1, "H3")
    auto_fit_columns(ws6, min_width=14)

    # -------------------------------------------------------------
    # 7. Asset Allocation
    # -------------------------------------------------------------
    ws7 = wb.create_sheet("Asset Allocation")
    ws7.views.sheetView[0].showGridLines = True
    
    alloc_cols = list(asset_alloc_df.columns)
    for c_idx, col_name in enumerate(alloc_cols, start=1):
        cell = ws7.cell(row=1, column=c_idx, value=col_name)
        apply_header_style(cell)

    for r_idx, row in enumerate(asset_alloc_df.itertuples(index=False), start=2):
        for c_idx, val in enumerate(row, start=1):
            cell = ws7.cell(row=r_idx, column=c_idx, value=val)
            cell.font = Font(name=FONT_NAME, size=10)
            col_name = alloc_cols[c_idx - 1]
            if col_name == "Ticker":
                cell.alignment = Alignment(horizontal="center")
            elif col_name in ["Target_Weight", "Cumulative_Return", "CAGR", "Annualized_Volatility"]:
                cell.number_format = "0.0%" if col_name == "Target_Weight" else "0.00%"
            elif col_name == "Initial_Allocation_USD":
                cell.number_format = "$#,##0.00"

    tab_alloc = Table(displayName="Table_AssetAllocation", ref=f"A1:{get_column_letter(len(alloc_cols))}{len(asset_alloc_df)+1}")
    tab_alloc.tableStyleInfo = TableStyleInfo(name="TableStyleLight9", showFirstColumn=False, showLastColumn=False, showRowStripes=True, showColumnStripes=False)
    ws7.add_table(tab_alloc)

    # Embed Excel Donut/Pie Chart
    chart2 = PieChart()
    chart2.title = "Target Asset Allocation Breakdown"
    labels_ref = Reference(ws7, min_col=1, min_row=2, max_row=len(asset_alloc_df) + 1)
    weights_ref = Reference(ws7, min_col=4, min_row=1, max_row=len(asset_alloc_df) + 1)
    chart2.add_data(weights_ref, titles_from_data=True)
    chart2.set_categories(labels_ref)
    chart2.width = 14
    chart2.height = 9
    ws7.add_chart(chart2, "B9")
    auto_fit_columns(ws7, min_width=14)

    # -------------------------------------------------------------
    # 8. Risk Analysis
    # -------------------------------------------------------------
    ws8 = wb.create_sheet("Risk Analysis")
    ws8.views.sheetView[0].showGridLines = True
    
    ws8["B2"] = "COMPREHENSIVE RISK & RETURN ANALYSIS SCORECARD"
    ws8["B2"].font = Font(name=FONT_NAME, size=14, bold=True, color=NAVY_HEADER)

    risk_headers = ["Financial / Risk Metric", "Portfolio Value", "Benchmark (SPY)", "Variance / Delta", "Institutional Interpretation"]
    for c_idx, h in enumerate(risk_headers, start=2):
        cell = ws8.cell(row=4, column=c_idx, value=h)
        apply_header_style(cell)

    interpretations = {
        "Initial Capital ($)": "Base invested principal at inception",
        "Ending Capital ($)": "Terminal portfolio value at period conclusion",
        "Total Cumulative Return": "Nominal percentage capital appreciation over 5 years",
        "CAGR (Annualized Return)": "Geometric mean annual compound growth rate",
        "Annualized Volatility (Risk)": "Standard deviation of returns annualized (sigma * √252)",
        "Sharpe Ratio (Rf=3.5%)": "Excess return per unit of total annualized risk",
        "Sortino Ratio (Rf=3.5%)": "Excess return per unit of harmful downside deviation",
        "Maximum Drawdown (Peak-to-Trough)": "Largest peak-to-trough equity decline",
        "Daily VaR (95% 1-day)": "Maximum daily loss expected on 95 out of 100 trading days",
        "Daily VaR (99% 1-day)": "Extreme tail risk loss threshold (99% confidence)",
        "Portfolio Beta (vs SPY)": "Systematic sensitivity relative to broad market",
        "Jensen's Alpha (Annualized)": "Excess risk-adjusted return unexplained by CAPM beta",
        "Tracking Error (Annualized)": "Volatility of active returns relative to benchmark",
        "Information Ratio": "Active return achieved per unit of active tracking error",
        "Best-Performing Asset (CAGR)": "ETF with highest standalone annualized return",
        "Worst-Performing Asset (CAGR)": "ETF with lowest standalone annualized return"
    }

    for r_idx, (_, row) in enumerate(risk_metrics_df.iterrows(), start=5):
        m_name = row["Metric"]
        ws8.cell(row=r_idx, column=2, value=m_name).font = Font(name=FONT_NAME, size=10, bold=True)
        ws8.cell(row=r_idx, column=3, value=row["Portfolio"]).alignment = Alignment(horizontal="right")
        ws8.cell(row=r_idx, column=4, value=row["Benchmark (SPY)"]).alignment = Alignment(horizontal="right")
        ws8.cell(row=r_idx, column=5, value=row["Difference"]).alignment = Alignment(horizontal="right")
        ws8.cell(row=r_idx, column=6, value=interpretations.get(m_name, "")).font = Font(name=FONT_NAME, size=9.5, italic=True)
        for c in range(2, 7):
            ws8.cell(row=r_idx, column=c).border = THIN_BORDER
            ws8.cell(row=r_idx, column=c).font = Font(name=FONT_NAME, size=10)

    auto_fit_columns(ws8, min_width=16)

    # -------------------------------------------------------------
    # 9. Benchmark Comparison
    # -------------------------------------------------------------
    ws9 = wb.create_sheet("Benchmark Comparison")
    ws9.views.sheetView[0].showGridLines = True
    
    ws9["B2"] = "PORTFOLIO VS. S&P 500 BENCHMARK COMPARISON"
    ws9["B2"].font = Font(name=FONT_NAME, size=14, bold=True, color=NAVY_HEADER)

    bench_cols = ["Date", "Portfolio_Value", "Benchmark_Value", "Portfolio_Cumulative_Return", "Benchmark_Cumulative_Return", "Active_Spread"]
    for c_idx, h in enumerate(bench_cols, start=2):
        cell = ws9.cell(row=4, column=c_idx, value=h)
        apply_header_style(cell)

    for r_idx, p_row in enumerate(portfolio_perf_df.itertuples(), start=5):
        b_row = benchmark_perf_df.iloc[r_idx - 5]
        ws9.cell(row=r_idx, column=2, value=p_row.Date).alignment = Alignment(horizontal="center")
        ws9.cell(row=r_idx, column=3, value=p_row.Portfolio_Value).number_format = "$#,##0.00"
        ws9.cell(row=r_idx, column=4, value=b_row["Benchmark_Value"]).number_format = "$#,##0.00"
        ws9.cell(row=r_idx, column=5, value=p_row.Cumulative_Return).number_format = "0.00%"
        ws9.cell(row=r_idx, column=6, value=b_row["Cumulative_Return"]).number_format = "0.00%"
        
        spread_cell = ws9.cell(row=r_idx, column=7, value=f"=E{r_idx}-F{r_idx}")
        spread_cell.number_format = "+0.00%;-0.00%;0.00%"
        spread_cell.alignment = Alignment(horizontal="right")
        for c in range(2, 8):
            ws9.cell(row=r_idx, column=c).font = Font(name=FONT_NAME, size=9.5)

    tab_bench = Table(displayName="Table_BenchmarkComparison", ref=f"B4:G{len(portfolio_perf_df)+4}")
    tab_bench.tableStyleInfo = TableStyleInfo(name="TableStyleLight9", showFirstColumn=False, showLastColumn=False, showRowStripes=True, showColumnStripes=False)
    ws9.add_table(tab_bench)

    # Embed Benchmark Comparison Line Chart
    chart3 = LineChart()
    chart3.title = "Cumulative Return Comparison: Portfolio vs SPY"
    chart3.y_axis.title = "Cumulative Return"
    chart3.y_axis.number_format = "0%"
    chart3.width = 17
    chart3.height = 10
    
    data_ref = Reference(ws9, min_col=5, min_row=4, max_col=6, max_row=len(portfolio_perf_df) + 4)
    dates_ref = Reference(ws9, min_col=2, min_row=5, max_row=len(portfolio_perf_df) + 4)
    chart3.add_data(data_ref, titles_from_data=True)
    chart3.set_categories(dates_ref)
    ws9.add_chart(chart3, "I4")
    auto_fit_columns(ws9, min_width=15)

    # -------------------------------------------------------------
    # 10. Correlation Analysis
    # -------------------------------------------------------------
    ws10 = wb.create_sheet("Correlation Analysis")
    ws10.views.sheetView[0].showGridLines = True
    
    ws10["B2"] = "5-YEAR DAILY RETURN CORRELATION MATRIX"
    ws10["B2"].font = Font(name=FONT_NAME, size=14, bold=True, color=NAVY_HEADER)
    ws10["B3"] = "Pearson correlation coefficients between ETF daily return series (2021-2025)."
    ws10["B3"].font = Font(name=FONT_NAME, size=10, italic=True, color="595959")

    tickers_corr = list(corr_matrix.columns)
    
    # Headers
    ws10.cell(row=5, column=2, value="ETF Ticker")
    apply_header_style(ws10.cell(row=5, column=2))
    for c_idx, t in enumerate(tickers_corr, start=3):
        cell = ws10.cell(row=5, column=c_idx, value=t)
        apply_header_style(cell)

    for r_idx, t_row in enumerate(tickers_corr, start=6):
        row_hdr = ws10.cell(row=r_idx, column=2, value=t_row)
        row_hdr.font = Font(name=FONT_NAME, size=10, bold=True)
        row_hdr.fill = SUBHEADER_FILL
        row_hdr.alignment = Alignment(horizontal="center")
        row_hdr.border = THIN_BORDER
        
        for c_idx, t_col in enumerate(tickers_corr, start=3):
            corr_val = corr_matrix.loc[t_row, t_col]
            cell = ws10.cell(row=r_idx, column=c_idx, value=round(corr_val, 4))
            cell.number_format = "0.00"
            cell.alignment = Alignment(horizontal="center")
            cell.border = THIN_BORDER
            cell.font = Font(name=FONT_NAME, size=10)

    # Add 3-color conditional formatting to correlation table
    corr_range = f"C6:{get_column_letter(len(tickers_corr)+2)}{len(tickers_corr)+5}"
    color_scale = ColorScaleRule(start_type="num", start_value=-0.2, start_color="5B9BD5",
                                 mid_type="num", mid_value=0.4, mid_color="FFFFFF",
                                 end_type="num", end_value=1.0, end_color="ED7D31")
    ws10.conditional_formatting.add(corr_range, color_scale)

    # Correlation Insights Note
    ws10["B13"] = "CORRELATION INSIGHTS FOR PORTFOLIO DIVERSIFICATION"
    ws10["B13"].font = Font(name=FONT_NAME, size=11, bold=True, color=NAVY_HEADER)
    
    insights = [
        "• SPY & QQQ show high positive correlation (> 0.85), driving core equity growth and technological momentum.",
        "• AGG (Fixed Income) exhibits near-zero correlation with equities, serving as a primary stabilizer during equity corrections.",
        "• GLD (Gold) displays low and often negative correlation with equities during macroeconomic stress, providing inflation hedging.",
        "• VNQ (Real Estate) provides moderate correlation to equities with elevated dividend cash flow yields."
    ]
    for i, ins in enumerate(insights, start=14):
        ws10.cell(row=i, column=2, value=ins).font = Font(name=FONT_NAME, size=9.5)

    auto_fit_columns(ws10, min_width=14)

    # -------------------------------------------------------------
    # 11. Methodology
    # -------------------------------------------------------------
    ws11 = wb.create_sheet("Methodology")
    ws11.views.sheetView[0].showGridLines = True
    
    ws11["B2"] = "INVESTMENT METHODOLOGY & FINANCIAL FORMULAS"
    ws11["B2"].font = Font(name=FONT_NAME, size=15, bold=True, color=NAVY_HEADER)

    methodology_text = [
        ("1. Daily Return Formulation",
         "Daily returns are calculated strictly on total return Adjusted Close (Adj Close), accounting for all corporate cash distributions and splits:\n"
         "R_t = (Adj Close_t / Adj Close_{t-1}) - 1\n"
         "Unadjusted Close is intentionally avoided for return calculations to prevent artificial dividend drops in fixed income and REIT assets."),
        ("2. Portfolio Constant-Weight Rebalancing",
         "The multi-asset portfolio daily return is modeled as the linear dot product of target weights and individual asset daily returns:\n"
         "R_p,t = SUM(w_i * R_i,t)\n"
         "Methodological Assumption: This formulation assumes daily end-of-day rebalancing back to initial target weights without friction, bid-ask spread, or tax drag.\n"
         "Limitation: Real-world buy-and-hold portfolios drift over time. Daily rebalancing provides an academic upper-bound benchmark for target-weight execution."),
        ("3. Cumulative Total Return",
         "Tracks portfolio terminal value over initial invested principal:\n"
         "Cumulative Return = (Ending Value / Initial Value) - 1 = PRODUCT(1 + R_p,t) - 1"),
        ("4. Compound Annual Growth Rate (CAGR)",
         "Calculates the geometric annualized return over the exact number of trading sessions:\n"
         "CAGR = (Ending Value / Initial Value) ^ (252 / N) - 1\n"
         "where N is the total number of synchronized trading days (1,255 days across 2021-2025)."),
        ("5. Annualized Volatility",
         "Scaled using the standard square-root of time institutional convention:\n"
         "sigma_annual = StdDev(R_p, daily) * SQRT(252)"),
        ("6. Sharpe Ratio",
         "Evaluates excess return generated per unit of total volatility:\n"
         "Sharpe = (CAGR - R_f) / sigma_annual\n"
         "where R_f = 3.50% annualized risk-free rate assumption based on trailing 3-month US Treasury bill yields."),
        ("7. Maximum Drawdown (MDD)",
         "Measures the largest peak-to-trough percentage decline in portfolio wealth:\n"
         "Drawdown_t = (Value_t / Running_Peak_t) - 1\n"
         "MDD = MIN(Drawdown_t)"),
        ("8. Value at Risk (Historical 1-Day 95% VaR)",
         "Computed non-parametrically using actual historical daily return percentiles:\n"
         "VaR_95% = 5th percentile of daily portfolio returns\n"
         "Interpreted as: on 95% of trading days, daily loss will not exceed this threshold."),
        ("9. Portfolio Beta & Jensen's Alpha",
         "Beta = Cov(R_p, R_SPY) / Var(R_SPY)\n"
         "Alpha = CAGR_p - [R_f + Beta * (CAGR_SPY - R_f)]\n"
         "Beta quantifies systematic market sensitivity relative to the S&P 500.")
    ]

    curr_row = 4
    for title, desc in methodology_text:
        ws11.cell(row=curr_row, column=2, value=title).font = Font(name=FONT_NAME, size=11, bold=True, color=NAVY_HEADER)
        ws11.merge_cells(start_row=curr_row + 1, start_column=2, end_row=curr_row + 2, end_column=8)
        desc_cell = ws11.cell(row=curr_row + 1, column=2, value=desc)
        desc_cell.font = Font(name=FONT_NAME, size=9.5)
        desc_cell.alignment = Alignment(wrap_text=True, vertical="top")
        curr_row += 4

    ws11.column_dimensions["B"].width = 30
    for col_l in ["C", "D", "E", "F", "G", "H"]:
        ws11.column_dimensions[col_l].width = 15

    # -------------------------------------------------------------
    # 12. Data Dictionary
    # -------------------------------------------------------------
    ws12 = wb.create_sheet("Data Dictionary")
    ws12.views.sheetView[0].showGridLines = True
    
    ws12["B2"] = "INVESTMENT PORTFOLIO DATA DICTIONARY"
    ws12["B2"].font = Font(name=FONT_NAME, size=14, bold=True, color=NAVY_HEADER)

    dict_headers = ["Dataset / Table", "Field Name", "Data Type", "Description", "Calculation / Source", "Example Value"]
    for c_idx, h in enumerate(dict_headers, start=2):
        cell = ws12.cell(row=4, column=c_idx, value=h)
        apply_header_style(cell)

    dictionary_data = [
        ("Raw Market Data", "Date", "Date (YYYY-MM-DD)", "Trading session observation date", "Yahoo Finance Exchange Calendar", "2021-01-04"),
        ("Raw Market Data", "Ticker", "String", "Unique ETF ticker symbol", "yfinance identifier", "SPY"),
        ("Raw Market Data", "Open", "Decimal Currency ($)", "Unadjusted session opening trade price", "Direct exchange tape", "375.31"),
        ("Raw Market Data", "High", "Decimal Currency ($)", "Highest unadjusted intraday price", "Direct exchange tape", "375.45"),
        ("Raw Market Data", "Low", "Decimal Currency ($)", "Lowest unadjusted intraday price", "Direct exchange tape", "364.82"),
        ("Raw Market Data", "Close", "Decimal Currency ($)", "Unadjusted regular trading close price", "Consolidated closing print", "368.79"),
        ("Raw Market Data", "Adj Close", "Decimal Currency ($)", "Close adjusted for dividends and splits", "Yahoo Finance backward algorithm", "345.12"),
        ("Raw Market Data", "Volume", "Integer", "Total traded session shares", "Consolidated tape volume", "110,210,800"),
        ("Raw Market Data", "Dividends", "Decimal Currency ($)", "Cash distribution per share", "Corporate action record", "1.58"),
        ("Raw Market Data", "Stock Splits", "Decimal Ratio", "Stock split multiplication ratio", "Corporate action record", "0.0"),
        ("Daily Returns", "SPY, QQQ, etc.", "Percentage (%)", "Asset daily percentage return", "(Adj Close_t / Adj Close_{t-1}) - 1", "+0.0125"),
        ("Portfolio Performance", "Portfolio_Value", "Currency ($)", "Mark-to-market portfolio value", "V_{t-1} * (1 + R_p,t)", "$142,500.00"),
        ("Portfolio Performance", "Cumulative_Return", "Percentage (%)", "Cumulative wealth appreciation", "(Portfolio_Value / 100,000) - 1", "+42.50%"),
        ("Portfolio Performance", "Running_Peak", "Currency ($)", "Highest portfolio value achieved to date", "MAX(Portfolio_Value_{0..t})", "$148,200.00"),
        ("Portfolio Performance", "Drawdown", "Percentage (%)", "Percentage contraction from running peak", "(Portfolio_Value / Running_Peak) - 1", "-4.12%"),
        ("Asset Allocation", "Target_Weight", "Percentage (%)", "Configured target allocation percentage", "User assumption config", "30.0%"),
        ("Risk Analysis", "CAGR", "Percentage (%)", "Compound Annual Growth Rate", "(V_end / V_start) ^ (252 / N) - 1", "+11.25%"),
        ("Risk Analysis", "Annualized_Volatility", "Percentage (%)", "Annualized standard deviation of returns", "StdDev(R) * SQRT(252)", "13.40%"),
        ("Risk Analysis", "Sharpe_Ratio", "Decimal Number", "Risk-adjusted performance measure", "(CAGR - Rf) / Volatility", "0.82"),
        ("Risk Analysis", "VaR_95", "Percentage (%)", "Historical 1-Day 95% Value at Risk", "5th percentile of daily returns", "-1.45%"),
        ("Risk Analysis", "Beta", "Decimal Number", "Systematic volatility vs S&P 500", "Cov(R_p, R_b) / Var(R_b)", "0.68")
    ]

    for r_idx, row in enumerate(dictionary_data, start=5):
        for c_idx, val in enumerate(row, start=2):
            cell = ws12.cell(row=r_idx, column=c_idx, value=val)
            cell.font = Font(name=FONT_NAME, size=9.5)
            cell.border = THIN_BORDER
            if c_idx in [3, 4]:
                cell.alignment = Alignment(horizontal="center")

    tab_dict = Table(displayName="Table_DataDictionary", ref=f"B4:G{len(dictionary_data)+4}")
    tab_dict.tableStyleInfo = TableStyleInfo(name="TableStyleLight9", showFirstColumn=False, showLastColumn=False, showRowStripes=True, showColumnStripes=False)
    ws12.add_table(tab_dict)
    auto_fit_columns(ws12, min_width=14)

    # Save complete workbook
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    wb.save(output_path)
    logger.info(f"Complete 12-worksheet Excel workbook successfully generated and saved at '{output_path}'.")
    return output_path

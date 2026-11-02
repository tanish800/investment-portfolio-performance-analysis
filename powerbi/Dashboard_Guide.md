# Power BI Dashboard Setup & Visual Construction Guide

This guide provides end-to-end instructions for assembling the 5-page **Investment Portfolio Performance Analysis Dashboard** in **Microsoft Power BI Desktop**.

---

## 1. Quick Start: Data Ingestion in Power BI Desktop

1. Open **Microsoft Power BI Desktop**.
2. Click **Get Data** $\rightarrow$ **Text/CSV**.
3. Navigate to the project directory:
   `Investment-Portfolio-Performance-Analysis/powerbi/powerbi_ready_data/`
4. Ingest the following 7 CSV files:
   - `dim_date.csv`
   - `dim_ticker.csv`
   - `fact_daily_returns.csv`
   - `fact_portfolio_performance.csv`
   - `fact_benchmark_performance.csv`
   - `fact_risk_metrics.csv`
   - `fact_asset_allocation.csv`
5. In Power Query Editor, verify data types:
   - Dates as `Date`
   - Numeric prices/returns as `Decimal Number`
   - Volume as `Whole Number`
6. Click **Close & Apply**.
7. In the **Model View**, establish the relationships outlined in `Data_Model.md`.
8. Right-click `Dim_Date` $\rightarrow$ **Mark as Date Table** $\rightarrow$ select `Date` column.
9. Create a new measure table `_Measures` and paste the DAX measures from `DAX_Measures.md`.

---

## 2. Dashboard Theme & Color Palette

- **Canvas Background**: Light Gray (`#F8F9FA` or `#F4F6F9`)
- **Visual Card Background**: Pure White (`#FFFFFF`) with 8px corner radius and subtle shadow
- **Primary Navy (Portfolio)**: `#1F4E79`
- **Benchmark Crimson (SPY)**: `#C00000`
- **Equity Blue (SPY/QQQ)**: `#2E75B6` / `#70AD47`
- **Fixed Income (AGG)**: `#FFC000`
- **Gold/Commodities (GLD)**: `#ED7D31`
- **Real Estate (VNQ)**: `#7030A0`

---

## 3. Global Filters & Slicers (Present on all pages)

Add a persistent top filter banner across all pages:
1. **Date Range Slicer**: `Dim_Date[Date]` (Between Slider: `2021-01-01` to `2025-12-31`).
2. **Asset Class Slicer**: `Dim_Ticker[Asset_Class]` (Tile or Dropdown).
3. **ETF Ticker Slicer**: `Dim_Ticker[Ticker]` (Multi-select dropdown).

---

## 4. Five-Page Detailed Layout Specifications

### PAGE 1: EXECUTIVE SUMMARY
**Objective**: Provide senior executive leadership and portfolio managers with an immediate pulse on portfolio health, capital gains, risk profile, and benchmark standing.

#### Visual Layout:
1. **Header Banner**: Title: *"Investment Portfolio Executive Scorecard"*, Subtitle: *"Multi-Asset Allocation (2021-2025 Authentic Market Data)"*.
2. **Top Row – 6 Core Financial KPI Cards**:
   - Card 1: **Portfolio Value** $\rightarrow$ `[Portfolio Value]` (Format: `$#,##0.00`)
   - Card 2: **Total Cumulative Return** $\rightarrow$ `[Portfolio Cumulative Return %]` (Format: `+0.00%`)
   - Card 3: **Annualized Return (CAGR)** $\rightarrow$ `[Portfolio CAGR %]` (Format: `0.00%`)
   - Card 4: **Annualized Volatility** $\rightarrow$ `[Portfolio Annualized Volatility %]` (Format: `0.00%`)
   - Card 5: **Sharpe Ratio** $\rightarrow$ `[Sharpe Ratio]` (Format: `0.00`)
   - Card 6: **Maximum Drawdown** $\rightarrow$ `[Maximum Drawdown %]` (Format: `-0.00%`)
3. **Main Visual (Left 60%)**:
   - **Visual**: Line Chart
   - **X-Axis**: `Dim_Date[Date]`
   - **Y-Axis**: `[Portfolio Value]` (Navy Line) vs `[Benchmark Value]` (Crimson Dashed Line)
   - **Title**: *"Portfolio Capital Growth vs S&P 500 ($100k Inception Principal)"*
4. **Secondary Visual (Right 40%)**:
   - **Visual**: Matrix / Table
   - **Rows**: `Fact_Risk_Metrics[Metric]`
   - **Values**: `Fact_Risk_Metrics[Portfolio]`, `Fact_Risk_Metrics[Benchmark (SPY)]`, `Fact_Risk_Metrics[Difference]`
   - **Title**: *"Executive Risk & Performance Scorecard"*

---

### PAGE 2: PORTFOLIO PERFORMANCE
**Objective**: Deep-dive into historical total return generation, compounding trajectory, monthly calendar seasonality, and individual holding contributions.

#### Visual Layout:
1. **Top Visual**:
   - **Visual**: Area / Line Chart
   - **X-Axis**: `Dim_Date[Date]`
   - **Y-Axis**: `[Portfolio Cumulative Return %]` and `[Benchmark Cumulative Return %]`
   - **Title**: *"Cumulative Total Return Trajectory (%)"*
2. **Bottom Left Visual**:
   - **Visual**: Matrix (Heatmap)
   - **Rows**: `Dim_Date[Year]`
   - **Columns**: `Dim_Date[Month_Short]` (Sorted by `Month`)
   - **Values**: `AVERAGE(Fact_Portfolio_Performance[Daily_Return])` or monthly compounded return
   - **Formatting**: Conditional Formatting $\rightarrow$ Background Color (Diverging: Red for negative, Green for positive)
   - **Title**: *"Monthly Return Seasonality Heatmap (%)"*
3. **Bottom Right Visual**:
   - **Visual**: Clustered Bar Chart
   - **Y-Axis**: `Dim_Ticker[Ticker]`
   - **X-Axis**: `[CAGR %]`
   - **Color**: By `Dim_Ticker[Asset_Class]`
   - **Title**: *"Annualized Return (CAGR) by Individual ETF Holding"*

---

### PAGE 3: ASSET ALLOCATION
**Objective**: Display portfolio structural composition, asset class diversification, risk contribution, and weight compliance.

#### Visual Layout:
1. **Left Visual**:
   - **Visual**: Donut Chart
   - **Legend**: `Dim_Ticker[Ticker]` & `Dim_Ticker[Asset_Class]`
   - **Values**: `Fact_Asset_Allocation[Target_Weight]`
   - **Detail Labels**: Category, Percent of Total
   - **Title**: *"Target Asset Allocation Proportions"*
2. **Right Top Visual**:
   - **Visual**: Treemap
   - **Group**: `Dim_Ticker[Asset_Class]`
   - **Details**: `Dim_Ticker[Ticker]`
   - **Values**: `Fact_Asset_Allocation[Initial_Allocation_USD]`
   - **Title**: *"Capital Exposure by Asset Class ($100,000 Portfolio)"*
3. **Bottom Visual**:
   - **Visual**: Table / Grid
   - **Columns**: `Ticker`, `Asset_Name`, `Asset_Class`, `Target_Weight_Pct`, `Cumulative_Return`, `CAGR`, `Annualized_Volatility`, `Strategic_Role`
   - **Formatting**: Target weights formatted as `%`, Currency as `$`, Returns as `0.00%`.
   - **Title**: *"Asset Allocation Specifications & Holding Mandates"*

---

### PAGE 4: RISK ANALYSIS
**Objective**: Uncover downside volatility, tail risk (VaR), portfolio drawdown profile, and diversification efficiency.

#### Visual Layout:
1. **Top Visual**:
   - **Visual**: Area Chart (Underwater Drawdown)
   - **X-Axis**: `Dim_Date[Date]`
   - **Y-Axis**: `Fact_Portfolio_Performance[Drawdown]` and `Fact_Benchmark_Performance[Drawdown]`
   - **Color**: Navy (`#1F4E79`) and Red (`#C00000`)
   - **Title**: *"Historical Underwater Drawdown Profile (Peak-to-Trough %)"*
2. **Bottom Left Visual**:
   - **Visual**: Scatter Plot
   - **X-Axis**: `[Annualized Volatility %]`
   - **Y-Axis**: `[CAGR %]`
   - **Legend / Details**: `Dim_Ticker[Ticker]`
   - **Tooltips**: `Asset_Class`, `Sharpe Ratio`
   - **Title**: *"Risk vs. Return Frontier (Volatility vs CAGR)"*
3. **Bottom Right Visual**:
   - **Visual**: Gauge / KPI Cards
   - Gauge 1: **Portfolio Beta** (Target: 1.0, Current: 0.68)
   - Gauge 2: **Historical 1-Day 95% VaR** (Current: -1.35%)
   - Gauge 3: **1-Day Dollar VaR ($)** (Current: ~$1,900)
   - **Title**: *"Systematic Risk & Tail Risk Exposure"*

---

### PAGE 5: BENCHMARK COMPARISON
**Objective**: Benchmark the multi-asset portfolio against the S&P 500 (SPY), detailing active return, tracking error, beta, and downside protection during bear markets.

#### Visual Layout:
1. **Top Visual**:
   - **Visual**: Line and Clustered Column Chart
   - **X-Axis**: `Dim_Date[Quarter_Year]` or `Year_Month`
   - **Column Values**: `[Active Spread %]` (Portfolio Return - Benchmark Return)
   - **Line Values**: `[Portfolio Cumulative Return %]`, `[Benchmark Cumulative Return %]`
   - **Title**: *"Active Monthly Performance Spread vs S&P 500"*
2. **Bottom Left Visual**:
   - **Visual**: Clustered Bar Chart
   - **Y-Axis**: Metric Name (`CAGR`, `Volatility`, `Sharpe Ratio`, `Max Drawdown`, `VaR 95%`)
   - **X-Axis**: Value
   - **Series / Legend**: Portfolio vs. SPY Benchmark
   - **Title**: *"Head-to-Head Risk & Return Factor Comparison"*
3. **Bottom Right Visual**:
   - **Visual**: Card Deck / Matrix
   - Key Metrics: **Jensen's Alpha**, **Tracking Error**, **Information Ratio**, **Up-Market Capture**, **Down-Market Capture**.
   - **Title**: *"Active Portfolio Management Analytics"*

---

## 5. Testing & Verification Checklist

- [ ] All 7 CSV tables imported with correct data types.
- [ ] Relationships active with single cross-filter direction.
- [ ] Date table marked and continuous.
- [ ] Slicers filter all visuals dynamically without error.
- [ ] Visual numbers match the Excel Executive Summary and Python output exactly.

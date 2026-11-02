# Investment Portfolio Performance Analysis

[![Python Version](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Excel](https://img.shields.io/badge/Excel-12%20Worksheets%20Model-green.svg)](https://products.office.com/excel)
[![Power BI](https://img.shields.io/badge/Power%20BI-Star%20Schema%20Model-orange.svg)](https://powerbi.microsoft.com/)
[![Tests](https://img.shields.io/badge/Tests-19%20Passed%20(100%25)-brightgreen.svg)](tests/)

An institutional-grade quantitative investment analysis project evaluating a multi-asset Exchange-Traded Fund (ETF) portfolio against the S&P 500 benchmark (`SPY`) across five complete calendar years (**2021–2025**). 

The project incorporates **authentic historical market data** sourced from Yahoo Finance, advanced financial risk engineering in **Python**, a fully modeled 12-worksheet **Microsoft Excel** financial workbook, and a star-schema **Microsoft Power BI** analytical dashboard suite.

---

## Table of Contents

1. [Executive Summary & Analytical Findings](#1-executive-summary--analytical-findings)
2. [Business Problem & Analytical Objectives](#2-business-problem--analytical-objectives)
3. [Authentic Market Dataset & Ticker Universe](#3-authentic-market-dataset--ticker-universe)
4. [Portfolio Strategy & Methodological Assumptions](#4-portfolio-strategy--methodological-assumptions)
5. [Mathematical & Financial Engineering Formulations](#5-mathematical--financial-engineering-formulations)
6. [Technology Stack](#6-technology-stack)
7. [Project Architecture & Directory Structure](#7-project-architecture--directory-structure)
8. [Installation & Virtual Environment Setup](#8-installation--virtual-environment-setup)
9. [Execution & Reproducibility](#9-execution--reproducibility)
10. [Automated Testing & Validation](#10-automated-testing--validation)
11. [Advanced Excel Financial Model (`.xlsx`)](#11-advanced-excel-financial-model-xlsx)
12. [Power BI Dashboard Architecture & DAX Measures](#12-power-bi-dashboard-architecture--dax-measures)
13. [Key Visualizations Gallery](#13-key-visualizations-gallery)
14. [Data Limitations & Yahoo Finance Caveats](#14-data-limitations--yahoo-finance-caveats)
15. [Future Scope & Institutional Extensions](#15-future-scope--institutional-extensions)
16. [Interview Talking Points for Candidates](#16-interview-talking-points-for-candidates)

---

## 1. Executive Summary & Analytical Findings

Across the 5-year observation window (January 4, 2021 to December 31, 2025; 1,253 synchronized trading days), a **$100,000 initial capital investment** yielded the following actual historical results:

| Institutional Financial Metric | Multi-Asset Portfolio | Benchmark (SPY - S&P 500) | Variance / Active Spread | Analytical Interpretation |
|---|:---:|:---:|:---:|---|
| **Initial Capital** | **$100,000.00** | **$100,000.00** | $0.00 | Identical starting principal |
| **Ending Capital (Dec 31, 2025)** | **$168,963.82** | **$199,563.32** | -$30,599.50 | Net capital appreciation |
| **Total Cumulative Return** | **+68.96%** | **+99.56%** | -30.60% | Strong multi-asset compounding |
| **CAGR (Annualized Return)** | **11.13%** | **14.91%** | -3.78% | Healthy double-digit annual growth |
| **Annualized Volatility (Risk)** | **11.95%** | **17.11%** | **-5.17%** | **30.2% lower overall portfolio volatility** |
| **Sharpe Ratio ($R_f = 3.50\%$)** | **0.638** | **0.667** | -0.028 | Comparable risk-adjusted efficiency |
| **Sortino Ratio ($R_f = 3.50\%$)** | **0.635** | **0.650** | -0.015 | Efficient compensation for downside risk |
| **Maximum Drawdown (Peak-to-Trough)** | **-22.70%** | **-24.50%** | **+1.80%** | **Superior capital preservation in bear markets** |
| **Historical 1-Day 95% VaR** | **-1.16%** | **-1.66%** | **+0.50%** | Lower maximum expected single-day loss |
| **Historical 1-Day 99% VaR** | **-2.04%** | **-2.93%** | **+0.89%** | Significant reduction in catastrophic tail risk |
| **Portfolio Beta ($\beta_{SPY}$)** | **0.661** | **1.000** | -0.339 | Defensive market posture ($\beta < 1.0$) |
| **Jensen's Alpha ($\alpha$)** | **+0.08%** | **0.00%** | +0.08% | Positive excess risk-adjusted alpha |
| **Annualized Tracking Error** | **6.95%** | 0.00% | 6.95% | Active divergence from equity benchmark |
| **Information Ratio** | **-0.544** | N/A | -0.544 | Reflects conservative asset dampening |
| **Best-Performing Asset (CAGR)** | **GLD (+17.05%)** | SPY (+14.91%) | +2.14% | Gold served as the primary return driver |
| **Worst-Performing Asset (CAGR)** | **AGG (-0.33%)** | SPY (+14.91%) | -15.24% | Fixed income impacted by Fed rate hikes |

### Key Core Insights:
1. **Diversification Asymmetric Protection**: The Multi-Asset Portfolio reduced annualized volatility from **17.11% to 11.95%** (a 30.2% volatility reduction) and mitigated 1-day 99% Value at Risk from **-2.93% to -2.04%**, while preserving a strong **11.13% CAGR**.
2. **Gold Outperformance**: `GLD` was the top-performing asset class with a **17.05% CAGR** (+118.77% cumulative), surging due to geopolitical tensions, high inflation, and central bank bullion accumulation.
3. **Macro Headwinds on Fixed Income**: `AGG` posted a slightly negative return (**-0.33% CAGR**) due to the historic Federal Reserve monetary tightening cycle (2022–2023), but provided essential portfolio stabilization with a microscopic 6.07% volatility and near-zero correlation to equities ($0.195$).

---

## 2. Business Problem & Analytical Objectives

Asset management firms, wealth advisors, family offices, and institutional investors constantly grapple with the trade-off between **capital growth** and **downside risk mitigation**. An all-equity portfolio (100% S&P 500) generates high terminal wealth during bull runs, but subjects investors to volatile equity sell-offs (e.g., the 2022 bear market drawdown of -24.50%).

### Core Analytical Questions Addressed:
1. **Long-Term Performance**: How did a multi-asset allocation grow relative to a single-index benchmark over a volatile 5-year cycle?
2. **Return & Risk Attribution**: Which specific ETF holding delivered the highest compound return, and which exhibited the highest volatility?
3. **Correlation & Diversification**: Did inter-asset correlations offer sufficient diversification benefit during market turbulence?
4. **Tail Risk & Downside Drawdowns**: Did the multi-asset strategy dampen portfolio drawdown depth and shorten recovery time?
5. **Risk-Adjusted Efficiency**: Was the return generated per unit of risk (Sharpe & Sortino) justified relative to broad equity indices?

---

## 3. Authentic Market Dataset & Ticker Universe

The project downloads actual daily market observations from **Yahoo Finance** via `yfinance` across 5 primary ETFs:

| Ticker | ETF Full Name | Asset Class | Target Weight | Inception | Mandate & Strategic Portfolio Role |
|---|---|---|:---:|:---:|---|
| **SPY** | SPDR S&P 500 ETF Trust | U.S. Large-Cap Equity | **30%** | 1993 | Core equity beta; broad U.S. corporate earnings exposure |
| **QQQ** | Invesco QQQ Trust | Tech / Growth Equity | **20%** | 1999 | High-growth Nasdaq-100 technology and communication leaders |
| **AGG** | iShares Core U.S. Aggregate Bond ETF | U.S. Investment-Grade Bonds | **25%** | 2003 | Fixed income anchor; capital preservation and ballast |
| **GLD** | SPDR Gold Shares | Commodities / Precious Metals | **15%** | 2004 | Non-correlated store of value; currency debasement hedge |
| **VNQ** | Vanguard Real Estate ETF | Real Estate (REITs) | **10%** | 2004 | Commercial real estate exposure and quarterly dividend income |

### Downloaded Fields:
- `Date`: Trading day observation.
- `Ticker`: Unique symbol identifier.
- `Open`, `High`, `Low`, `Close`: Unadjusted session execution prices.
- `Adj Close`: Total return price adjusted backward for stock splits and dividend cash reinvestments.
- `Volume`: Daily consolidated venue share volume.
- `Dividends`: Corporate distribution per share.
- `Stock Splits`: Corporate split ratio.

---

## 4. Portfolio Strategy & Methodological Assumptions

1. **Illustrative Target Weights**:
   - `SPY: 30%` | `QQQ: 20%` | `AGG: 25%` | `GLD: 15%` | `VNQ: 10%` (Sum = 100.0%).
   - The weights are configurable assumptions stored in `config/portfolio_config.json`.
2. **Constant-Weight Rebalancing Strategy**:
   - Returns are evaluated under a daily constant-weight framework:
     $$R_{p, t} = \sum_{i=1}^{N} w_i R_{i, t}$$
   - **Methodology Explanation**: At the end of each trading session, proceeds from outperforming assets are reallocated back into target percentages.
   - **Methodological Caveat**: Assumes zero transaction frictions, zero bid-ask spread slippage, and no tax drag. Buy-and-hold portfolios drift over time without active rebalancing.
3. **Risk-Free Rate**:
   - Configured at **3.50% annualized**, reflecting the average yield of 3-month US Treasury Bills over the 2021–2025 observation window.
4. **Trading Day Convention**:
   - 252 annual trading days based on the New York Stock Exchange (NYSE) calendar.

---

## 5. Mathematical & Financial Engineering Formulations

### 1. Daily Return ($R_t$)
Calculated strictly on Adjusted Close prices:
$$R_t = \frac{\text{Adj Close}_t}{\text{Adj Close}_{t-1}} - 1$$

### 2. Cumulative Return ($R_{\text{cum}}$)
$$R_{\text{cum}} = \frac{V_{\text{end}}}{V_{\text{start}}} - 1 = \prod_{t=1}^{T} (1 + R_{p, t}) - 1$$

### 3. Compound Annual Growth Rate (CAGR)
$$CAGR = \left(\frac{V_{\text{end}}}{V_{\text{start}}}\right)^{\frac{252}{N}} - 1$$
*(where $N = 1,253$ trading days across the 5 complete calendar years).*

### 4. Annualized Volatility ($\sigma_{\text{ann}}$)
$$\sigma_{\text{ann}} = \sigma_{\text{daily}} \times \sqrt{252}$$

### 5. Sharpe Ratio
$$\text{Sharpe} = \frac{CAGR - R_f}{\sigma_{\text{ann}}}$$

### 6. Sortino Ratio
$$\text{Sortino} = \frac{CAGR - R_f}{\sqrt{\frac{1}{N}\sum_{t=1}^N \min(R_t - R_{f,\text{daily}}, 0)^2} \times \sqrt{252}}$$

### 7. Maximum Drawdown (MDD)
$$D_t = \frac{V_t}{\max_{k \le t} V_k} - 1 \quad \implies \quad MDD = \min_{t} D_t$$

### 8. Value at Risk (Historical 1-Day 95% & 99% VaR)
Calculated non-parametrically as the 5th and 1st percentiles of realized daily returns:
$$\text{VaR}_{95} = \text{Percentile}(R_p, 5\%)$$
$$\text{Dollar VaR}_{95} = |V_t \times \text{VaR}_{95}|$$

### 9. Portfolio Beta ($\beta$) & Jensen's Alpha ($\alpha$)
$$\beta = \frac{\text{Cov}(R_p, R_{\text{SPY}})}{\text{Var}(R_{\text{SPY}})}$$
$$\alpha = CAGR_p - [R_f + \beta (CAGR_{\text{SPY}} - R_f)]$$

### 10. Tracking Error ($TE$) & Information Ratio ($IR$)
$$TE = \text{StdDev}(R_p - R_{\text{SPY}}) \times \sqrt{252}$$
$$IR = \frac{CAGR_p - CAGR_{\text{SPY}}}{TE}$$

---

## 6. Technology Stack

- **Python 3.10+** (Core financial analytics engine)
- **Pandas & NumPy** (Vectorized time-series manipulation, matrix math)
- **yfinance & curl-cffi** (Resilient TLS-backed Yahoo Finance market data retrieval)
- **Matplotlib & Seaborn** (Publication-grade 300 DPI financial charts)
- **OpenPyXL** (Automated generation of 12-worksheet advanced Excel workbook)
- **Microsoft Power BI** (Enterprise star-schema dashboard, dimensional model)
- **DAX (Data Analysis Expressions)** (Dynamic portfolio calculations)
- **Pytest** (Automated unit test suite)

---

## 7. Project Architecture & Directory Structure

```
Investment-Portfolio-Performance-Analysis/
│
├── config/
│   └── portfolio_config.json          # Editable target weights, dates, and assumptions
│
├── data/
│   ├── raw/
│   │   └── raw_market_data.csv        # 6,270 authentic observations downloaded from yfinance
│   ├── processed/
│   │   ├── cleaned_market_data.csv    # Duplicate-free, date-synchronized market data
│   │   ├── daily_returns.csv          # Wide return series for all 5 ETFs
│   │   ├── portfolio_performance.csv  # Daily portfolio valuation, returns, and drawdown
│   │   ├── benchmark_performance.csv  # SPY daily valuation, returns, and drawdown
│   │   ├── asset_allocation.csv       # Weights, individual CAGR, vol, and attribution
│   │   ├── correlation_matrix.csv     # 5x5 Pearson correlation matrix
│   │   └── risk_metrics.csv           # 16-row executive risk scorecard
│   └── metadata/
│       ├── dataset_metadata.json      # Timestamps, record counts, and API provenance
│       └── yahoo_finance_limitations.md # Official documentation of Yahoo Finance caveats
│
├── src/
│   ├── __init__.py
│   ├── data_collection.py             # Yahoo Finance ingestion with TLS session handling
│   ├── data_cleaning.py               # Data validation, cleaning, and date alignment
│   ├── portfolio_analysis.py          # Portfolio compounding & allocation calculations
│   ├── risk_analysis.py               # CAGR, Volatility, Sharpe, VaR, Beta, Alpha math
│   ├── visualization.py               # Matplotlib & Seaborn 8-chart rendering engine
│   ├── excel_generator.py             # 12-worksheet openpyxl workbook generator
│   └── powerbi_prep.py                # Star-schema CSV preparation for Power BI
│
├── excel/
│   └── Investment_Portfolio_Performance_Analysis.xlsx # 12-sheet Excel financial model
│
├── powerbi/
│   ├── DAX_Measures.md                # 20+ production-grade DAX measures
│   ├── Data_Model.md                  # Star-schema dimensional architecture guide
│   ├── Dashboard_Guide.md             # 5-page dashboard blueprint & import steps
│   └── powerbi_ready_data/
│       ├── dim_date.csv               # Continuous calendar dimension (1,822 days)
│       ├── dim_ticker.csv             # ETF asset universe dimension
│       ├── fact_daily_returns.csv     # Long-format daily returns & OHLCV fact table
│       ├── fact_portfolio_performance.csv # Daily portfolio valuation fact table
│       ├── fact_benchmark_performance.csv # Daily benchmark valuation fact table
│       ├── fact_risk_metrics.csv      # Risk metrics summary fact table
│       └── fact_asset_allocation.csv  # Asset allocation fact table
│
├── reports/
│   └── figures/
│       ├── portfolio_growth.png       # Chart 1: Portfolio vs SPY growth ($100k)
│       ├── etf_performance_comparison.png # Chart 2: Cumulative returns by ETF
│       ├── asset_allocation_donut.png # Chart 3: Target allocation donut
│       ├── correlation_heatmap.png    # Chart 4: Seaborn correlation heatmap
│       ├── risk_return_scatter.png    # Chart 5: Volatility vs CAGR scatter
│       ├── portfolio_drawdown.png     # Chart 6: Underwater drawdown profiles
│       ├── monthly_return_heatmap.png # Chart 7: Monthly returns calendar matrix
│       └── benchmark_comparison.png   # Chart 8: Side-by-side metric comparison
│
├── notebooks/
│   └── investment_analysis.ipynb      # Interactive Jupyter Notebook walkthrough
│
├── tests/
│   ├── __init__.py
│   ├── test_data_collection.py        # Validation, schema check, and duplicate cleaning
│   ├── test_returns.py                # Daily returns, weight validation, portfolio math
│   └── test_risk_metrics.py           # CAGR, Vol, Sharpe, VaR, Beta, and Alpha tests
│
├── main.py                            # Unified CLI pipeline entrypoint
├── requirements.txt                   # Production dependencies
├── README.md                          # Comprehensive documentation
├── .gitignore                         # Standard Python/IDE ignore rules
└── LICENSE                            # MIT Open-Source License
```

---

## 8. Installation & Virtual Environment Setup

### 1. Clone or Navigate to the Repository
```bash
cd Investment-Portfolio-Performance-Analysis
```

### 2. Create and Activate a Python Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 9. Execution & Reproducibility

Execute the entire end-to-end data pipeline with a single command:

```bash
python main.py
```

### Command-Line Arguments:
- `--refresh`: Force a fresh download from Yahoo Finance (bypassing local raw cache).
- `--config`: Specify a custom configuration JSON path.

```bash
python main.py --refresh --config config/portfolio_config.json
```

---

## 10. Automated Testing & Validation

The test suite contains **19 unit tests** utilizing small labeled synthetic fixtures to validate data cleaning logic, return compounding, portfolio weighting constraints, and statistical risk formulas.

To run the automated tests:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

or with Pytest:

```bash
pytest -v tests/
```

**Result: 19/19 tests passed (100% success rate).**

---

## 11. Advanced Excel Financial Model (`.xlsx`)

The workbook `excel/Investment_Portfolio_Performance_Analysis.xlsx` contains **12 structured worksheets** designed with institutional aesthetics:

1. **Executive Summary**: 10 visual financial KPI cards, high-level scorecard table, and workbook navigation links.
2. **Portfolio Configuration**: Dynamic asset allocation model with `=SUM()` validation check and analytical disclaimers.
3. **Raw Market Data**: Official Excel Table (`Table_RawMarketData`) containing 6,270 authentic raw observations from Yahoo Finance.
4. **Cleaned Market Data**: Formatted Excel Table (`Table_CleanedMarketData`) with synchronized dates.
5. **Daily Returns**: Matrix of daily returns for each ETF, Portfolio, and Benchmark (`Table_DailyReturns`).
6. **Portfolio Performance**: Daily portfolio valuations, running peaks, drawdowns, and an embedded **Portfolio Valuation Line Chart**.
7. **Asset Allocation**: Weight breakdown table, individual CAGR, volatility, and an embedded **Donut Chart**.
8. **Risk Analysis**: Side-by-side risk comparison with institutional financial explanations.
9. **Benchmark Comparison**: Head-to-head comparison against SPY with an embedded **Active Tracking Line Chart**.
10. **Correlation Analysis**: 5x5 return correlation matrix with **3-color gradient conditional formatting**.
11. **Methodology**: Academic documentation of formulas, daily rebalancing mechanics, and friction assumptions.
12. **Data Dictionary**: Field-level descriptions, data types, calculations, and sample values.

---

## 12. Power BI Dashboard Architecture & DAX Measures

The `powerbi/` directory includes a production-ready **Star Schema** data model and complete visual blueprint.

### 5-Page Dashboard Structure:
- **Page 1: Executive Summary**: Top KPI cards, capital growth line visual, and risk scorecard matrix.
- **Page 2: Portfolio Performance**: Cumulative return trajectory, annual return matrices, and monthly calendar heatmap.
- **Page 3: Asset Allocation**: Donut allocation, capital exposure treemap, and holding mandate grid.
- **Page 4: Risk Analysis**: Underwater drawdown area chart, volatility vs. CAGR scatter frontier, and VaR gauges.
- **Page 5: Benchmark Comparison**: Active return column spread, beta gauges, tracking error, and alpha metrics.

### Sample DAX Measure (Sharpe Ratio):
```dax
Sharpe Ratio = 
VAR Rf = 0.035
VAR PortCAGR = [Portfolio CAGR %]
VAR PortVol = [Portfolio Annualized Volatility %]
RETURN
    DIVIDE(PortCAGR - Rf, PortVol, BLANK())
```
*(Refer to `powerbi/DAX_Measures.md` for all 20+ DAX formulas).*

---

## 13. Key Visualizations Gallery

The Python pipeline automatically generates 8 publication-quality figures saved in `reports/figures/`:

1. `portfolio_growth.png` – Multi-Asset Portfolio vs SPY ($100,000 Initial Principal).
2. `etf_performance_comparison.png` – 5-Year Cumulative Return comparison across all 5 individual holdings.
3. `asset_allocation_donut.png` – Illustrative target weights and asset class donut chart.
4. `correlation_heatmap.png` – Inter-asset daily return Pearson correlation heatmap.
5. `risk_return_scatter.png` – Risk vs. Return frontier (Annualized Volatility vs CAGR).
6. `portfolio_drawdown.png` – Historical underwater peak-to-trough drawdowns.
7. `monthly_return_heatmap.png` – Year $\times$ Month portfolio return calendar matrix.
8. `benchmark_comparison.png` – Head-to-head bar chart on CAGR, Volatility, Sharpe, and Drawdown.

---

## 14. Data Limitations & Yahoo Finance Caveats

1. **Ex-Dividend Reinvestment Timing**: Yahoo Finance calculates `Adj Close` using a backward-adjustment factor assuming full dividend reinvestment on the ex-date without dividend withholding taxes or broker commissions.
2. **Post-Market Settlement Restatements**: Historical closing prints can occasionally experience retrospective corrections from exchange settlement reconciliations.
3. **Rebalancing Friction**: The daily constant-weight assumption does not penalize transaction costs or bid-ask spread friction. In live practice, quarterly or threshold-based rebalancing (e.g. $\pm 5\%$ band) is more tax-efficient.
4. **Survivorship & Liquidity**: All 5 selected ETFs (`SPY`, `QQQ`, `AGG`, `GLD`, `VNQ`) represent liquid institutional mega-cap ETFs with zero delisting risk over the observed timeframe.

---

## 15. Future Scope & Institutional Extensions

- **Threshold / Calendar Rebalancing**: Introduce dynamic monthly, quarterly, or $\pm 5\%$ tolerance-band rebalancing engines.
- **Monte Carlo Simulation**: Run 10,000-path stochastic simulations for 10-year wealth projections.
- **Modern Portfolio Theory (MPT) Optimization**: Integrate Markowitz mean-variance efficient frontier optimization to solve for Tangency / Maximum Sharpe weights.
- **Factor Attribution**: Decompose returns into Fama-French 5-Factor exposures (Market, Size, Value, Profitability, Investment).

---

## 16. Interview Talking Points for Candidates

When discussing this project during **Data Analyst / Financial Analyst** interviews:

1. **"Why use Adjusted Close instead of Close?"**  
   *Answer*: Unadjusted Close ignores cash dividend distributions. For income-generating instruments like `AGG` (Bonds) and `VNQ` (Real Estate), ignoring dividends artificially suppresses total return. `Adj Close` captures total economic return.
2. **"How does the daily constant-weight rebalancing work?"**  
   *Answer*: Portfolio daily return is calculated as $R_{p,t} = \sum w_i R_{i,t}$. This mathematically models selling fractional outperforming winners and buying underperforming assets back to target weights each day.
3. **"What caused Gold (GLD) to outperform Equities over 2021–2025?"**  
   *Answer*: A confluence of high global inflation (CPI peaking over 9% in 2022), geopolitical fragmentation, de-dollarization trends, and historic central bank gold reserve buying pushed gold to record highs, generating a 17.05% CAGR.
4. **"Why did Bonds (AGG) produce a negative return?"**  
   *Answer*: The Federal Reserve executed its fastest monetary tightening campaign in 40 years, raising the Fed Funds rate from 0% to over 5.25%. Because bond prices are inversely related to interest rates, longer-duration bond ETFs experienced significant price drops before yield recovery took hold.
5. **"How was the Power BI model structured?"**  
   *Answer*: Developed following a Kimball Star Schema with a conformed `Dim_Date` calendar table and `Dim_Ticker` dimension table joined via 1-to-many single-direction relationships to fact tables (`Fact_Daily_Returns`, `Fact_Portfolio_Performance`), avoiding bi-directional join penalties and ensuring high DAX calculation speeds.

---

## License

This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.

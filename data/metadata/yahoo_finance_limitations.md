# Yahoo Finance Historical Market Data: Documentation & Limitations

## Overview

The dataset used in this project is sourced directly from **Yahoo Finance** (`finance.yahoo.com`) using the open-source Python library `yfinance`. Yahoo Finance aggregates market data provided primarily by ICE Data Services and direct exchange feeds.

## Data Granularity & Scope

- **Asset Class**: Exchange-Traded Funds (ETFs)
- **Tickers**: `SPY`, `QQQ`, `AGG`, `GLD`, `VNQ`
- **Frequency**: Daily market observations (OHLCV + Corporate Actions)
- **Fields Downloaded**:
  - `Date`: Observation trading date (trading sessions only, excluding exchange holidays and weekends).
  - `Ticker`: ETF symbol identifier.
  - `Open`: Unadjusted opening market trade price.
  - `High`: Unadjusted highest trade price of the trading session.
  - `Low`: Unadjusted lowest trade price of the trading session.
  - `Close`: Unadjusted closing settlement price.
  - `Adj Close`: Adjusted closing price accounting for dividend distributions, capital gains distributions, and stock splits.
  - `Volume`: Total daily shares traded across reporting venues.
  - `Dividends`: Cash distribution amount per share ex-dividend date.
  - `Stock Splits`: Stock split ratio applied on the execution date.

## Return Calculation Methodology & Adjusted Prices

For total return calculations over long horizons, institutional analysis requires accounting for all cash flows (dividends) and corporate actions (splits). 

In this project:
1. `Adj Close` (Adjusted Close) is used as the single consistent basis for daily return calculations:
   $$\text{Daily Return}_t = \frac{\text{Adj Close}_t}{\text{Adj Close}_{t-1}} - 1$$
2. `yfinance` provides `Adj Close` when downloaded with `auto_adjust=False`. We explicitly avoid double-adjusting OHLC values by maintaining raw OHLC alongside `Adj Close`.
3. Calculating returns on unadjusted `Close` would artificially misrepresent dividend-paying ETFs (such as `AGG`, `VNQ`, and `SPY`), making their total returns appear artificially low due to cash dividend drops.

## Data Limitations & Analytical Caveats

1. **Dividend Reinvestment Assumptions**:
   The standard Yahoo Finance `Adj Close` algorithm calculates adjustment factors backwards from the current date. It assumes dividends are reinvested on the ex-dividend date at the closing price, without factoring in broker commissions, dividend withholding taxes, or cash drag between ex-date and payment date.

2. **Timing of Restatements**:
   Yahoo Finance data can occasionally undergo retrospective adjustments or corrections by the underlying data vendor (ICE Data Services) if trade reporting errors occurred during post-market settlement.

3. **Intraday Gaps & Tick Nuances**:
   Daily OHLC reflects consolidated tape trades. Extreme intraday anomalies, illiquid pre-market or after-hours prints are excluded from regular session Close.

4. **Exchange Holidays & Non-Synchronous Trading**:
   All 5 selected ETFs trade on major U.S. exchanges (NYSE Arca and Nasdaq) following the U.S. equity holiday calendar. Consequently, trading days are 100% synchronous across all five assets with 0 cross-holiday mismatches.

5. **Rate Limiting & Network Resilience**:
   The Yahoo Finance public API endpoint does not require an authenticated API key, but enforces IP-based rate limits and browser impersonation checks. The data collection module implements retry logic and session-level TLS handling to guarantee reproducible downloads.

6. **Survivorship & Selection Bias**:
   The five selected ETFs are among the largest, most liquid, and longest-running ETFs in history. This project evaluates their actual realized historical performance over the 5-year observation period.

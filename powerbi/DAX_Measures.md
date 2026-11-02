# Power BI DAX Measures Reference Guide

This document contains production-grade **DAX (Data Analysis Expressions)** measures designed for the **Investment Portfolio Performance Analysis** Power BI model.

---

## 1. Portfolio Valuation & Capital Measures

### Initial Portfolio Capital
```dax
Initial Capital = 
100000.00
```

### Current / Ending Portfolio Value
```dax
Portfolio Value = 
VAR MaxSelectedDate = MAX(Dim_Date[Date_String])
RETURN
    CALCULATE(
        MAX(Fact_Portfolio_Performance[Portfolio_Value]),
        Fact_Portfolio_Performance[Date] = MaxSelectedDate
    )
```

### Benchmark (SPY) Value
```dax
Benchmark Value = 
VAR MaxSelectedDate = MAX(Dim_Date[Date_String])
RETURN
    CALCULATE(
        MAX(Fact_Benchmark_Performance[Benchmark_Value]),
        Fact_Benchmark_Performance[Date] = MaxSelectedDate
    )
```

### Capital Net Gain (USD)
```dax
Portfolio Net Profit ($) = 
[Portfolio Value] - [Initial Capital]
```

---

## 2. Return & Growth Measures

### Portfolio Cumulative Return (%)
```dax
Portfolio Cumulative Return % = 
VAR EndVal = [Portfolio Value]
VAR StartVal = [Initial Capital]
RETURN
    DIVIDE(EndVal - StartVal, StartVal, 0)
```

### Benchmark Cumulative Return (%)
```dax
Benchmark Cumulative Return % = 
VAR EndVal = [Benchmark Value]
VAR StartVal = [Initial Capital]
RETURN
    DIVIDE(EndVal - StartVal, StartVal, 0)
```

### Portfolio CAGR (Compound Annual Growth Rate)
```dax
Portfolio CAGR % = 
VAR StartVal = [Initial Capital]
VAR EndVal = [Portfolio Value]
VAR TotalTradingDays = COUNTROWS(Fact_Portfolio_Performance)
VAR Years = DIVIDE(TotalTradingDays, 252, 1)
RETURN
    IF(
        StartVal > 0 && EndVal > 0 && Years > 0,
        ( (EndVal / StartVal) ^ (1 / Years) ) - 1,
        BLANK()
    )
```

### Benchmark CAGR %
```dax
Benchmark CAGR % = 
VAR StartVal = [Initial Capital]
VAR EndVal = [Benchmark Value]
VAR TotalTradingDays = COUNTROWS(Fact_Benchmark_Performance)
VAR Years = DIVIDE(TotalTradingDays, 252, 1)
RETURN
    IF(
        StartVal > 0 && EndVal > 0 && Years > 0,
        ( (EndVal / StartVal) ^ (1 / Years) ) - 1,
        BLANK()
    )
```

### Active Return Spread (Portfolio vs. SPY)
```dax
Active Spread % = 
[Portfolio Cumulative Return %] - [Benchmark Cumulative Return %]
```

---

## 3. Volatility & Risk-Adjusted Measures

### Annualized Portfolio Volatility
```dax
Portfolio Annualized Volatility % = 
VAR DailyStdDev = STDEV.S(Fact_Portfolio_Performance[Daily_Return])
RETURN
    DailyStdDev * SQRT(252)
```

### Annualized Benchmark Volatility
```dax
Benchmark Annualized Volatility % = 
VAR DailyStdDev = STDEV.S(Fact_Benchmark_Performance[Daily_Return])
RETURN
    DailyStdDev * SQRT(252)
```

### Sharpe Ratio (Risk-Free Rate = 3.50%)
```dax
Sharpe Ratio = 
VAR Rf = 0.035
VAR PortCAGR = [Portfolio CAGR %]
VAR PortVol = [Portfolio Annualized Volatility %]
RETURN
    DIVIDE(PortCAGR - Rf, PortVol, BLANK())
```

### Benchmark Sharpe Ratio
```dax
Benchmark Sharpe Ratio = 
VAR Rf = 0.035
VAR BenchCAGR = [Benchmark CAGR %]
VAR BenchVol = [Benchmark Annualized Volatility %]
RETURN
    DIVIDE(BenchCAGR - Rf, BenchVol, BLANK())
```

### Downside Deviation (Harmful Risk)
```dax
Portfolio Downside Deviation = 
VAR DailyRf = (1 + 0.035) ^ (1 / 252) - 1
VAR DownsideSquaredSum = 
    SUMX(
        Fact_Portfolio_Performance,
        IF(
            Fact_Portfolio_Performance[Daily_Return] < DailyRf,
            (Fact_Portfolio_Performance[Daily_Return] - DailyRf) ^ 2,
            0
        )
    )
VAR CountDays = COUNTROWS(Fact_Portfolio_Performance)
RETURN
    SQRT(DIVIDE(DownsideSquaredSum, CountDays, 0)) * SQRT(252)
```

### Sortino Ratio
```dax
Sortino Ratio = 
VAR Rf = 0.035
VAR DownsideDev = [Portfolio Downside Deviation]
RETURN
    DIVIDE([Portfolio CAGR %] - Rf, DownsideDev, BLANK())
```

---

## 4. Drawdown & Tail Risk Measures

### Current Portfolio Drawdown %
```dax
Current Drawdown % = 
VAR MaxSelectedDate = MAX(Dim_Date[Date_String])
RETURN
    CALCULATE(
        MAX(Fact_Portfolio_Performance[Drawdown]),
        Fact_Portfolio_Performance[Date] = MaxSelectedDate
    )
```

### Maximum Drawdown (MDD) %
```dax
Maximum Drawdown % = 
MIN(Fact_Portfolio_Performance[Drawdown])
```

### Benchmark Maximum Drawdown %
```dax
Benchmark Maximum Drawdown % = 
MIN(Fact_Benchmark_Performance[Drawdown])
```

### Historical 1-Day 95% Value at Risk (VaR)
```dax
Historical 1-Day 95% VaR % = 
PERCENTILE.INC(Fact_Portfolio_Performance[Daily_Return], 0.05)
```

### Historical 1-Day 99% Value at Risk (VaR)
```dax
Historical 1-Day 99% VaR % = 
PERCENTILE.INC(Fact_Portfolio_Performance[Daily_Return], 0.01)
```

### Portfolio 1-Day Dollar VaR ($)
```dax
Dollar VaR 95% ($) = 
ABS([Portfolio Value] * [Historical 1-Day 95% VaR %])
```

---

## 5. Systematic Risk & Benchmark Metrics

### Portfolio Beta (relative to S&P 500)
```dax
Portfolio Beta = 
VAR MergedTable = 
    ADDCOLUMNS(
        Fact_Portfolio_Performance,
        "BenchReturn",
        LOOKUPVALUE(
            Fact_Benchmark_Performance[Daily_Return],
            Fact_Benchmark_Performance[Date],
            Fact_Portfolio_Performance[Date]
        )
    )
VAR MeanPort = AVERAGEX(MergedTable, [Daily_Return])
VAR MeanBench = AVERAGEX(MergedTable, [BenchReturn])
VAR Covariance = 
    AVERAGEX(
        MergedTable,
        ([Daily_Return] - MeanPort) * ([BenchReturn] - MeanBench)
    )
VAR BenchVariance = 
    VAR.S(Fact_Benchmark_Performance[Daily_Return])
RETURN
    DIVIDE(Covariance, BenchVariance, 1.0)
```

### Jensen's Alpha (Annualized)
```dax
Jensen's Alpha % = 
VAR Rf = 0.035
VAR Beta = [Portfolio Beta]
VAR ExpectedReturn = Rf + Beta * ([Benchmark CAGR %] - Rf)
RETURN
    [Portfolio CAGR %] - ExpectedReturn
```

### Tracking Error (Annualized)
```dax
Tracking Error % = 
VAR ExcessReturns = 
    ADDCOLUMNS(
        Fact_Portfolio_Performance,
        "Excess",
        Fact_Portfolio_Performance[Daily_Return] - 
        LOOKUPVALUE(Fact_Benchmark_Performance[Daily_Return], Fact_Benchmark_Performance[Date], Fact_Portfolio_Performance[Date])
    )
RETURN
    STDEV.S(EXCEPT(ExcessReturns, Fact_Portfolio_Performance)) * SQRT(252)
```

---

## 6. Time Intelligence Measures

### Year-to-Date (YTD) Return %
```dax
Portfolio YTD Return % = 
VAR LastDateVal = MAX(Dim_Date[Date])
VAR CurrentYear = YEAR(LastDateVal)
VAR StartOfYearValue = 
    CALCULATE(
        FIRSTNONBLANKVALUE(Fact_Portfolio_Performance[Date], MAX(Fact_Portfolio_Performance[Portfolio_Value])),
        YEAR(RELATED(Dim_Date[Date])) = CurrentYear
    )
VAR EndOfYearValue = [Portfolio Value]
RETURN
    DIVIDE(EndOfYearValue - StartOfYearValue, StartOfYearValue, 0)
```

### 1-Year Trailing Return %
```dax
Portfolio 1Y Trailing Return % = 
VAR EndVal = [Portfolio Value]
VAR OneYearAgoDate = EDATE(MAX(Dim_Date[Date]), -12)
VAR StartVal = 
    CALCULATE(
        MAX(Fact_Portfolio_Performance[Portfolio_Value]),
        FILTER(ALL(Dim_Date), Dim_Date[Date] <= OneYearAgoDate)
    )
RETURN
    DIVIDE(EndVal - StartVal, StartVal, 0)
```

---

## 7. Dynamic Summary & Best / Worst Performers

### Best-Performing ETF (by 5-Year CAGR)
```dax
Best Performing ETF = 
TOPN(
    1,
    VALUES(Fact_Asset_Allocation[Ticker]),
    CALCULATE(MAX(Fact_Asset_Allocation[CAGR])),
    DESC
)
```

### Worst-Performing ETF (by 5-Year CAGR)
```dax
Worst Performing ETF = 
TOPN(
    1,
    VALUES(Fact_Asset_Allocation[Ticker]),
    CALCULATE(MIN(Fact_Asset_Allocation[CAGR])),
    ASC
)
```

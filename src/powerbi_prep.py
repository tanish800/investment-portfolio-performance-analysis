"""
Power BI Data Preparation Module
Exports star-schema dimension and fact tables optimized for Power BI Desktop.
"""

import json
import logging
import os
from typing import Dict, List

import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def prepare_powerbi_tables(
    cleaned_df: pd.DataFrame,
    daily_returns_df: pd.DataFrame,
    portfolio_perf_df: pd.DataFrame,
    benchmark_perf_df: pd.DataFrame,
    asset_alloc_df: pd.DataFrame,
    risk_metrics_df: pd.DataFrame,
    config: dict,
    output_dir: str = "powerbi/powerbi_ready_data"
):
    """
    Creates star-schema dimension and fact tables for Power BI.
    """
    logger.info("Preparing Power BI-ready Star Schema tables...")
    os.makedirs(output_dir, exist_ok=True)

    # 1. Dim_Date (Calendar Table)
    unique_dates = pd.to_datetime(cleaned_df["Date"].unique()).sort_values()
    min_date = unique_dates.min()
    max_date = unique_dates.max()
    
    # Full calendar sequence
    full_dates = pd.date_range(start=min_date, end=max_date, freq="D")
    dim_date = pd.DataFrame({"Date": full_dates})
    dim_date["Date_Key"] = dim_date["Date"].dt.strftime("%Y%m%d").astype(int)
    dim_date["Date_String"] = dim_date["Date"].dt.strftime("%Y-%m-%d")
    dim_date["Year"] = dim_date["Date"].dt.year
    dim_date["Quarter"] = "Q" + dim_date["Date"].dt.quarter.astype(str)
    dim_date["Quarter_Year"] = dim_date["Quarter"] + " " + dim_date["Year"].astype(str)
    dim_date["Month"] = dim_date["Date"].dt.month
    dim_date["Month_Name"] = dim_date["Date"].dt.strftime("%B")
    dim_date["Month_Short"] = dim_date["Date"].dt.strftime("%b")
    dim_date["Year_Month"] = dim_date["Date"].dt.strftime("%Y-%m")
    dim_date["Day"] = dim_date["Date"].dt.day
    dim_date["Day_of_Week"] = dim_date["Date"].dt.strftime("%A")
    dim_date["Day_of_Week_Number"] = dim_date["Date"].dt.dayofweek + 1
    dim_date["Is_Weekend"] = dim_date["Date"].dt.dayofweek.isin([5, 6])
    dim_date["Is_Trading_Day"] = dim_date["Date_String"].isin(cleaned_df["Date"].unique())

    dim_date_path = os.path.join(output_dir, "dim_date.csv")
    dim_date.to_csv(dim_date_path, index=False)
    logger.info(f"Saved: {dim_date_path} ({len(dim_date)} rows)")

    # 2. Dim_Ticker
    ticker_records = []
    for ticker, info in config["assets"].items():
        ticker_records.append({
            "Ticker": ticker,
            "Asset_Name": info.get("name", ticker),
            "Asset_Class": info.get("asset_class", "Equity"),
            "Strategic_Role": info.get("role", ""),
            "Target_Weight": info.get("target_weight", 0.0),
            "Target_Weight_Pct": f"{info.get('target_weight', 0.0) * 100:.1f}%",
            "Is_Benchmark": ticker == config.get("benchmark_ticker", "SPY")
        })
    dim_ticker = pd.DataFrame(ticker_records)
    dim_ticker_path = os.path.join(output_dir, "dim_ticker.csv")
    dim_ticker.to_csv(dim_ticker_path, index=False)
    logger.info(f"Saved: {dim_ticker_path}")

    # 3. Fact_Daily_Returns (Long format for analytical power)
    # Melt wide daily returns into long format
    ret_melted = daily_returns_df.melt(id_vars=["Date"], var_name="Ticker", value_name="Daily_Return")
    # Merge with prices and volume from cleaned_df
    fact_returns = pd.merge(
        cleaned_df[["Date", "Ticker", "Open", "High", "Low", "Close", "Adj Close", "Volume"]],
        ret_melted,
        on=["Date", "Ticker"],
        how="left"
    )
    fact_returns["Daily_Return"] = fact_returns["Daily_Return"].fillna(0.0)
    fact_returns_path = os.path.join(output_dir, "fact_daily_returns.csv")
    fact_returns.to_csv(fact_returns_path, index=False)
    logger.info(f"Saved: {fact_returns_path} ({len(fact_returns)} rows)")

    # 4. Fact_Portfolio_Performance
    fact_portfolio = portfolio_perf_df.copy()
    fact_portfolio_path = os.path.join(output_dir, "fact_portfolio_performance.csv")
    fact_portfolio.to_csv(fact_portfolio_path, index=False)
    logger.info(f"Saved: {fact_portfolio_path}")

    # 5. Fact_Benchmark_Performance
    fact_bench = benchmark_perf_df.copy()
    fact_bench_path = os.path.join(output_dir, "fact_benchmark_performance.csv")
    fact_bench.to_csv(fact_bench_path, index=False)
    logger.info(f"Saved: {fact_bench_path}")

    # 6. Fact_Risk_Metrics
    risk_metrics_path = os.path.join(output_dir, "fact_risk_metrics.csv")
    risk_metrics_df.to_csv(risk_metrics_path, index=False)
    logger.info(f"Saved: {risk_metrics_path}")

    # 7. Fact_Asset_Allocation
    asset_alloc_path = os.path.join(output_dir, "fact_asset_allocation.csv")
    asset_alloc_df.to_csv(asset_alloc_path, index=False)
    logger.info(f"Saved: {asset_alloc_path}")

    logger.info("Power BI star-schema tables successfully prepared.")

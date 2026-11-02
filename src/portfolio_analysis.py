"""
Portfolio Analysis Module
Calculates daily returns, portfolio performance, benchmark comparison,
and asset allocation metrics based on authentic historical market data.
"""

import json
import logging
import os
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def calculate_daily_returns(cleaned_df: pd.DataFrame, output_dir: str = "data/processed") -> pd.DataFrame:
    """
    Pivots cleaned market data by Date and calculates daily returns using Adjusted Close.
    Daily Return = (Adj Close_t / Adj Close_{t-1}) - 1
    First row has return = 0.0 or dropped for return-series calculations.
    Saves daily_returns.csv.
    """
    logger.info("Computing daily returns from Adjusted Close...")
    # Pivot Adj Close into a wide table: index = Date, columns = Ticker
    adj_pivot = cleaned_df.pivot(index="Date", columns="Ticker", values="Adj Close")
    
    # Calculate daily percent change
    daily_ret = adj_pivot.pct_change().dropna()
    
    # Reset index so Date is a column
    daily_ret_df = daily_ret.reset_index()
    
    # Save to CSV
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, "daily_returns.csv")
    daily_ret_df.to_csv(out_path, index=False)
    logger.info(f"Daily returns saved to '{out_path}' ({len(daily_ret_df)} trading days).")
    
    return daily_ret_df


def validate_weights(weights: Dict[str, float], available_tickers: List[str]) -> bool:
    """
    Validates that portfolio weights:
    1. Sum to 1.0 (within 1e-4 tolerance).
    2. Only reference available tickers.
    3. Are non-negative (long-only).
    """
    total_w = sum(weights.values())
    if not (0.999 <= total_w <= 1.001):
        raise ValueError(f"Portfolio weights must sum to 1.0 (100%). Current sum: {total_w:.4f}")
    
    for ticker, w in weights.items():
        if w < 0:
            raise ValueError(f"Negative weight found for {ticker}: {w}. Long-only portfolio required.")
        if ticker not in available_tickers:
            raise ValueError(f"Configured weight for '{ticker}' not found in available tickers: {available_tickers}")
            
    return True


def calculate_portfolio_performance(
    daily_returns_df: pd.DataFrame,
    weights: Dict[str, float],
    initial_value: float = 100000.0,
    output_dir: str = "data/processed"
) -> pd.DataFrame:
    """
    Calculates portfolio daily return under a constant-weight daily rebalanced strategy:
    R_p,t = sum(w_i * R_i,t)
    Tracks Portfolio Value, Cumulative Return, Running Peak, and Drawdown.
    Saves portfolio_performance.csv.
    """
    logger.info("Calculating portfolio performance under constant-weight daily rebalancing...")
    tickers = [t for t in weights.keys() if t in daily_returns_df.columns]
    validate_weights(weights, list(daily_returns_df.columns))

    df = daily_returns_df[["Date"]].copy()
    
    # Compute weighted daily return
    # R_{p, t} = sum_i (w_i * R_{i, t})
    weighted_returns = pd.Series(0.0, index=daily_returns_df.index)
    for ticker in tickers:
        weighted_returns += daily_returns_df[ticker] * weights[ticker]
        
    df["Daily_Return"] = weighted_returns
    
    # Portfolio growth simulation
    # V_t = V_0 * prod(1 + R_{p, k})
    growth_factor = (1.0 + df["Daily_Return"]).cumprod()
    df["Portfolio_Value"] = initial_value * growth_factor
    df["Cumulative_Return"] = (df["Portfolio_Value"] / initial_value) - 1.0
    
    # Drawdown calculation
    df["Running_Peak"] = df["Portfolio_Value"].cummax()
    df["Drawdown"] = (df["Portfolio_Value"] / df["Running_Peak"]) - 1.0
    
    # Add initial row (Day 0) for complete financial tracking
    first_date = pd.to_datetime(daily_returns_df["Date"].iloc[0]) - pd.Timedelta(days=1)
    # We keep daily trading records
    out_path = os.path.join(output_dir, "portfolio_performance.csv")
    df.to_csv(out_path, index=False)
    logger.info(f"Portfolio performance saved to '{out_path}'.")
    return df


def calculate_benchmark_performance(
    daily_returns_df: pd.DataFrame,
    benchmark_ticker: str = "SPY",
    initial_value: float = 100000.0,
    output_dir: str = "data/processed"
) -> pd.DataFrame:
    """
    Calculates benchmark (e.g. SPY) performance metrics matching portfolio timeline.
    Tracks Benchmark Value, Cumulative Return, Running Peak, and Drawdown.
    Saves benchmark_performance.csv.
    """
    logger.info(f"Computing benchmark performance for '{benchmark_ticker}'...")
    if benchmark_ticker not in daily_returns_df.columns:
        raise ValueError(f"Benchmark ticker '{benchmark_ticker}' not found in daily returns columns.")
        
    df = daily_returns_df[["Date"]].copy()
    df["Daily_Return"] = daily_returns_df[benchmark_ticker]
    df["Benchmark_Value"] = initial_value * (1.0 + df["Daily_Return"]).cumprod()
    df["Cumulative_Return"] = (df["Benchmark_Value"] / initial_value) - 1.0
    df["Running_Peak"] = df["Benchmark_Value"].cummax()
    df["Drawdown"] = (df["Benchmark_Value"] / df["Running_Peak"]) - 1.0
    
    out_path = os.path.join(output_dir, "benchmark_performance.csv")
    df.to_csv(out_path, index=False)
    logger.info(f"Benchmark performance saved to '{out_path}'.")
    return df


def calculate_asset_allocation_summary(
    cleaned_df: pd.DataFrame,
    daily_returns_df: pd.DataFrame,
    weights_config: Dict[str, dict],
    initial_value: float = 100000.0,
    output_dir: str = "data/processed"
) -> pd.DataFrame:
    """
    Summarizes asset allocation, asset classes, target weights, individual cumulative returns,
    CAGR, annualized volatility, and capital attribution.
    Saves asset_allocation.csv.
    """
    logger.info("Generating asset allocation summary...")
    records = []
    num_days = len(daily_returns_df)
    trading_years = num_days / 252.0
    
    for ticker, info in weights_config.items():
        weight = info["target_weight"]
        name = info.get("name", ticker)
        asset_class = info.get("asset_class", "General")
        role = info.get("role", "")
        
        # Individual return series
        ret_series = daily_returns_df[ticker]
        total_cum_ret = (1.0 + ret_series).prod() - 1.0
        cagr = (1.0 + total_cum_ret) ** (1.0 / trading_years) - 1.0 if trading_years > 0 else 0.0
        ann_vol = ret_series.std() * np.sqrt(252)
        initial_alloc = initial_value * weight
        
        records.append({
            "Ticker": ticker,
            "Asset_Name": name,
            "Asset_Class": asset_class,
            "Target_Weight": weight,
            "Target_Weight_Pct": f"{weight * 100:.1f}%",
            "Initial_Allocation_USD": initial_alloc,
            "Cumulative_Return": total_cum_ret,
            "CAGR": cagr,
            "Annualized_Volatility": ann_vol,
            "Strategic_Role": role
        })
        
    df_alloc = pd.DataFrame(records)
    out_path = os.path.join(output_dir, "asset_allocation.csv")
    df_alloc.to_csv(out_path, index=False)
    logger.info(f"Asset allocation summary saved to '{out_path}'.")
    return df_alloc


def calculate_correlation_matrix(
    daily_returns_df: pd.DataFrame,
    tickers: List[str],
    output_dir: str = "data/processed"
) -> pd.DataFrame:
    """
    Calculates Pearson correlation matrix between ETF daily return series.
    Saves correlation_matrix.csv.
    """
    logger.info("Computing ETF return correlation matrix...")
    ret_subset = daily_returns_df[tickers]
    corr_matrix = ret_subset.corr(method="pearson")
    
    out_path = os.path.join(output_dir, "correlation_matrix.csv")
    corr_matrix.to_csv(out_path)
    logger.info(f"Correlation matrix saved to '{out_path}'.")
    return corr_matrix

"""
Risk Analysis Module
Calculates advanced institutional financial and risk metrics:
CAGR, Annualized Volatility, Sharpe Ratio, Sortino Ratio, Maximum Drawdown,
Value at Risk (VaR 95% 1-day), Portfolio Beta, Alpha, and Tracking Error.
"""

import json
import logging
import os
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def calculate_cagr(start_val: float, end_val: float, num_trading_days: int) -> float:
    """
    Computes Compound Annual Growth Rate (CAGR) based on 252 trading days per year:
    CAGR = (End Value / Start Value) ^ (252 / Num Days) - 1
    """
    if start_val <= 0 or end_val <= 0 or num_trading_days <= 0:
        return 0.0
    years = num_trading_days / 252.0
    return float((end_val / start_val) ** (1.0 / years) - 1.0)


def calculate_annualized_volatility(daily_returns: pd.Series, periods_per_year: int = 252) -> float:
    """
    Annualized Volatility = StdDev(Daily Returns) * sqrt(252)
    """
    return float(daily_returns.std() * np.sqrt(periods_per_year))


def calculate_sharpe_ratio(
    annualized_return: float,
    annualized_volatility: float,
    risk_free_rate: float = 0.035
) -> float:
    """
    Sharpe Ratio = (Annualized Return - Risk Free Rate) / Annualized Volatility
    """
    if annualized_volatility == 0:
        return 0.0
    return float((annualized_return - risk_free_rate) / annualized_volatility)


def calculate_max_drawdown(values: pd.Series) -> Tuple[float, int, str, str]:
    """
    Calculates Maximum Drawdown (MDD) and duration.
    Returns (max_drawdown, max_duration_days, peak_date, trough_date).
    """
    running_max = values.cummax()
    drawdowns = (values / running_max) - 1.0
    mdd = float(drawdowns.min())
    return mdd


def calculate_var_historical(daily_returns: pd.Series, confidence_level: float = 0.95) -> float:
    """
    Calculates historical Value at Risk (VaR) at the specified confidence level (e.g. 95%).
    Returns the cutoff return threshold (typically negative, representing maximum loss expected 95% of days).
    For 95% confidence, returns the 5th percentile of daily returns.
    """
    percentile = (1.0 - confidence_level) * 100.0
    var_cutoff = float(np.percentile(daily_returns.dropna(), percentile))
    return var_cutoff


def calculate_beta(asset_returns: pd.Series, benchmark_returns: pd.Series) -> float:
    """
    Calculates Beta relative to benchmark:
    Beta = Cov(R_asset, R_bench) / Var(R_bench)
    """
    common_idx = asset_returns.index.intersection(benchmark_returns.index)
    r_a = asset_returns.loc[common_idx]
    r_b = benchmark_returns.loc[common_idx]
    
    cov_matrix = np.cov(r_a, r_b)
    covariance = cov_matrix[0, 1]
    bench_variance = cov_matrix[1, 1]
    
    if bench_variance == 0:
        return 1.0
    return float(covariance / bench_variance)


def calculate_jensens_alpha(
    portfolio_cagr: float,
    benchmark_cagr: float,
    beta: float,
    risk_free_rate: float = 0.035
) -> float:
    """
    Jensen's Alpha = CAGR_p - [R_f + Beta * (CAGR_b - R_f)]
    """
    expected_return = risk_free_rate + beta * (benchmark_cagr - risk_free_rate)
    return float(portfolio_cagr - expected_return)


def calculate_sortino_ratio(
    daily_returns: pd.Series,
    annualized_return: float,
    risk_free_rate: float = 0.035,
    periods_per_year: int = 252
) -> float:
    """
    Sortino Ratio = (Annualized Return - Risk Free Rate) / Annualized Downside Deviation
    """
    daily_rf = (1.0 + risk_free_rate) ** (1.0 / periods_per_year) - 1.0
    downside_returns = daily_returns[daily_returns < daily_rf] - daily_rf
    if len(downside_returns) == 0:
        return 0.0
    downside_dev = np.sqrt((downside_returns ** 2).mean()) * np.sqrt(periods_per_year)
    if downside_dev == 0:
        return 0.0
    return float((annualized_return - risk_free_rate) / downside_dev)


def calculate_tracking_error(portfolio_returns: pd.Series, benchmark_returns: pd.Series) -> float:
    """
    Tracking Error = Annualized StdDev of excess returns (R_p - R_b)
    """
    excess_returns = portfolio_returns - benchmark_returns
    return float(excess_returns.std() * np.sqrt(252))


def generate_risk_metrics_table(
    portfolio_perf_df: pd.DataFrame,
    benchmark_perf_df: pd.DataFrame,
    daily_returns_df: pd.DataFrame,
    risk_free_rate: float = 0.035,
    output_dir: str = "data/processed"
) -> pd.DataFrame:
    """
    Computes a comprehensive side-by-side risk and performance scorecard
    comparing Portfolio against Benchmark (SPY) and individual assets.
    Saves risk_metrics.csv.
    """
    logger.info("Computing complete institutional risk scorecard...")
    p_ret = portfolio_perf_df["Daily_Return"]
    b_ret = benchmark_perf_df["Daily_Return"]
    num_days = len(p_ret)
    
    # Portfolio metrics
    p_start_val = portfolio_perf_df["Portfolio_Value"].iloc[0] / (1.0 + p_ret.iloc[0])
    p_end_val = portfolio_perf_df["Portfolio_Value"].iloc[-1]
    p_total_ret = (p_end_val / p_start_val) - 1.0
    p_cagr = calculate_cagr(p_start_val, p_end_val, num_days)
    p_vol = calculate_annualized_volatility(p_ret)
    p_sharpe = calculate_sharpe_ratio(p_cagr, p_vol, risk_free_rate)
    p_sortino = calculate_sortino_ratio(p_ret, p_cagr, risk_free_rate)
    p_mdd = calculate_max_drawdown(portfolio_perf_df["Portfolio_Value"])
    p_var95 = calculate_var_historical(p_ret, 0.95)
    p_var99 = calculate_var_historical(p_ret, 0.99)
    p_beta = calculate_beta(p_ret, b_ret)
    
    # Benchmark metrics
    b_start_val = benchmark_perf_df["Benchmark_Value"].iloc[0] / (1.0 + b_ret.iloc[0])
    b_end_val = benchmark_perf_df["Benchmark_Value"].iloc[-1]
    b_total_ret = (b_end_val / b_start_val) - 1.0
    b_cagr = calculate_cagr(b_start_val, b_end_val, num_days)
    b_vol = calculate_annualized_volatility(b_ret)
    b_sharpe = calculate_sharpe_ratio(b_cagr, b_vol, risk_free_rate)
    b_sortino = calculate_sortino_ratio(b_ret, b_cagr, risk_free_rate)
    b_mdd = calculate_max_drawdown(benchmark_perf_df["Benchmark_Value"])
    b_var95 = calculate_var_historical(b_ret, 0.95)
    b_var99 = calculate_var_historical(b_ret, 0.99)
    b_beta = 1.0  # By definition
    
    # Comparative metrics
    alpha = calculate_jensens_alpha(p_cagr, b_cagr, p_beta, risk_free_rate)
    te = calculate_tracking_error(p_ret, b_ret)
    ir = (p_cagr - b_cagr) / te if te != 0 else 0.0

    # Best and worst asset determination
    asset_cagrs = {}
    for col in daily_returns_df.columns:
        if col != "Date":
            col_tot = (1.0 + daily_returns_df[col]).prod() - 1.0
            col_cagr = (1.0 + col_tot) ** (252.0 / num_days) - 1.0
            asset_cagrs[col] = col_cagr
            
    best_etf = max(asset_cagrs, key=asset_cagrs.get)
    worst_etf = min(asset_cagrs, key=asset_cagrs.get)

    metrics_list = [
        {"Metric": "Initial Capital ($)", "Portfolio": f"${p_start_val:,.2f}", "Benchmark (SPY)": f"${b_start_val:,.2f}", "Difference": "$0.00"},
        {"Metric": "Ending Capital ($)", "Portfolio": f"${p_end_val:,.2f}", "Benchmark (SPY)": f"${b_end_val:,.2f}", "Difference": f"${p_end_val - b_end_val:,.2f}"},
        {"Metric": "Total Cumulative Return", "Portfolio": f"{p_total_ret * 100:.2f}%", "Benchmark (SPY)": f"{b_total_ret * 100:.2f}%", "Difference": f"{(p_total_ret - b_total_ret) * 100:+.2f}%"},
        {"Metric": "CAGR (Annualized Return)", "Portfolio": f"{p_cagr * 100:.2f}%", "Benchmark (SPY)": f"{b_cagr * 100:.2f}%", "Difference": f"{(p_cagr - b_cagr) * 100:+.2f}%"},
        {"Metric": "Annualized Volatility (Risk)", "Portfolio": f"{p_vol * 100:.2f}%", "Benchmark (SPY)": f"{b_vol * 100:.2f}%", "Difference": f"{(p_vol - b_vol) * 100:+.2f}%"},
        {"Metric": "Sharpe Ratio (Rf=3.5%)", "Portfolio": f"{p_sharpe:.3f}", "Benchmark (SPY)": f"{b_sharpe:.3f}", "Difference": f"{p_sharpe - b_sharpe:+.3f}"},
        {"Metric": "Sortino Ratio (Rf=3.5%)", "Portfolio": f"{p_sortino:.3f}", "Benchmark (SPY)": f"{b_sortino:.3f}", "Difference": f"{p_sortino - b_sortino:+.3f}"},
        {"Metric": "Maximum Drawdown (Peak-to-Trough)", "Portfolio": f"{p_mdd * 100:.2f}%", "Benchmark (SPY)": f"{b_mdd * 100:.2f}%", "Difference": f"{(p_mdd - b_mdd) * 100:+.2f}%"},
        {"Metric": "Daily VaR (95% 1-day)", "Portfolio": f"{p_var95 * 100:.2f}%", "Benchmark (SPY)": f"{b_var95 * 100:.2f}%", "Difference": f"{(p_var95 - b_var95) * 100:+.2f}%"},
        {"Metric": "Daily VaR (99% 1-day)", "Portfolio": f"{p_var99 * 100:.2f}%", "Benchmark (SPY)": f"{b_var99 * 100:.2f}%", "Difference": f"{(p_var99 - b_var99) * 100:+.2f}%"},
        {"Metric": "Portfolio Beta (vs SPY)", "Portfolio": f"{p_beta:.3f}", "Benchmark (SPY)": f"{b_beta:.3f}", "Difference": f"{p_beta - b_beta:+.3f}"},
        {"Metric": "Jensen's Alpha (Annualized)", "Portfolio": f"{alpha * 100:.2f}%", "Benchmark (SPY)": "0.00%", "Difference": f"{alpha * 100:+.2f}%"},
        {"Metric": "Tracking Error (Annualized)", "Portfolio": f"{te * 100:.2f}%", "Benchmark (SPY)": "0.00%", "Difference": f"{te * 100:.2f}%"},
        {"Metric": "Information Ratio", "Portfolio": f"{ir:.3f}", "Benchmark (SPY)": "N/A", "Difference": f"{ir:.3f}"},
        {"Metric": "Best-Performing Asset (CAGR)", "Portfolio": f"{best_etf} ({asset_cagrs[best_etf]*100:.2f}%)", "Benchmark (SPY)": "SPY", "Difference": "-"},
        {"Metric": "Worst-Performing Asset (CAGR)", "Portfolio": f"{worst_etf} ({asset_cagrs[worst_etf]*100:.2f}%)", "Benchmark (SPY)": "SPY", "Difference": "-"}
    ]

    metrics_df = pd.DataFrame(metrics_list)
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, "risk_metrics.csv")
    metrics_df.to_csv(out_path, index=False)
    logger.info(f"Risk metrics table saved to '{out_path}'.")
    return metrics_df

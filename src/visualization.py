"""
Visualization Module
Generates high-resolution financial charts and statistical figures
for presentation and executive reporting using authentic market data.
"""

import logging
import os
from typing import Dict, List, Optional

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for headless execution
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import pandas as pd
import seaborn as sns

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Institutional styling defaults
plt.rcParams.update({
    "font.sans-serif": "Segoe UI, Arial, Helvetica, sans-serif",
    "font.family": "sans-serif",
    "axes.edgecolor": "#D0D7DE",
    "axes.linewidth": 0.8,
    "grid.color": "#E1E4E8",
    "grid.linestyle": "--",
    "grid.alpha": 0.7,
    "figure.autolayout": True
})

PALETTE = {
    "Portfolio": "#1F4E79",     # Institutional Navy
    "SPY": "#2E75B6",           # Blue
    "QQQ": "#70AD47",           # Green
    "AGG": "#FFC000",           # Amber/Gold
    "GLD": "#ED7D31",           # Copper/Orange
    "VNQ": "#7030A0",           # Purple
    "Benchmark": "#C00000"      # Crimson
}


def plot_portfolio_growth(
    portfolio_df: pd.DataFrame,
    benchmark_df: pd.DataFrame,
    output_path: str = "reports/figures/portfolio_growth.png"
):
    """1. Portfolio Growth Chart: Portfolio Value vs SPY Benchmark over time."""
    logger.info("Generating Portfolio Growth Chart...")
    fig, ax = plt.subplots(figsize=(12, 6), dpi=300)
    
    dates = pd.to_datetime(portfolio_df["Date"])
    p_vals = portfolio_df["Portfolio_Value"]
    b_vals = benchmark_df["Benchmark_Value"]
    
    ax.plot(dates, p_vals, label="Multi-Asset Portfolio", color=PALETTE["Portfolio"], linewidth=2.2)
    ax.plot(dates, b_vals, label="Benchmark (SPY - S&P 500)", color=PALETTE["Benchmark"], linewidth=1.8, linestyle="--")
    
    ax.fill_between(dates, p_vals, 100000, alpha=0.1, color=PALETTE["Portfolio"])
    
    # End value annotations
    last_p = p_vals.iloc[-1]
    last_b = b_vals.iloc[-1]
    last_date = dates.iloc[-1]
    ax.annotate(f"Portfolio: ${last_p:,.0f}", xy=(last_date, last_p), xytext=(10, 0),
                textcoords="offset points", fontweight="bold", color=PALETTE["Portfolio"])
    ax.annotate(f"SPY: ${last_b:,.0f}", xy=(last_date, last_b), xytext=(10, 0),
                textcoords="offset points", fontweight="bold", color=PALETTE["Benchmark"])

    ax.set_title("Portfolio Growth vs Benchmark ($100,000 Initial Investment)", fontsize=14, fontweight="bold", pad=15)
    ax.set_ylabel("Portfolio Value (USD)", fontsize=11, fontweight="bold")
    ax.yaxis.set_major_formatter(mtick.StrMethodFormatter("${x:,.0f}"))
    ax.grid(True)
    ax.legend(frameon=True, facecolor="#F9FBFD", loc="upper left", fontsize=10)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig.savefig(output_path)
    plt.close(fig)
    logger.info(f"Saved: {output_path}")


def plot_etf_performance_comparison(
    daily_returns_df: pd.DataFrame,
    tickers: List[str],
    output_path: str = "reports/figures/etf_performance_comparison.png"
):
    """2. ETF Performance Comparison: Normalized Cumulative Return for all individual ETFs."""
    logger.info("Generating ETF Performance Comparison Chart...")
    fig, ax = plt.subplots(figsize=(12, 6), dpi=300)
    
    dates = pd.to_datetime(daily_returns_df["Date"])
    
    for ticker in tickers:
        cum_ret = (1.0 + daily_returns_df[ticker]).cumprod() - 1.0
        color = PALETTE.get(ticker, None)
        ax.plot(dates, cum_ret * 100, label=f"{ticker}", linewidth=1.8, color=color)
        # End value annotation
        end_pct = cum_ret.iloc[-1] * 100
        ax.annotate(f"{ticker}: {end_pct:+.1f}%", xy=(dates.iloc[-1], end_pct),
                    xytext=(6, 0), textcoords="offset points", fontsize=8.5, fontweight="bold")

    ax.axhline(0, color="#888888", linestyle="-", linewidth=0.8, alpha=0.7)
    ax.set_title("5-Year Cumulative Total Return Comparison by ETF Asset Class", fontsize=14, fontweight="bold", pad=15)
    ax.set_ylabel("Cumulative Return (%)", fontsize=11, fontweight="bold")
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
    ax.grid(True)
    ax.legend(frameon=True, facecolor="#F9FBFD", loc="upper left", ncol=len(tickers))
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig.savefig(output_path)
    plt.close(fig)
    logger.info(f"Saved: {output_path}")


def plot_asset_allocation_donut(
    asset_alloc_df: pd.DataFrame,
    output_path: str = "reports/figures/asset_allocation_donut.png"
):
    """3. Asset Allocation Donut Chart: Target weights and asset class proportions."""
    logger.info("Generating Asset Allocation Donut Chart...")
    fig, ax = plt.subplots(figsize=(8, 8), dpi=300)
    
    labels = [f"{row['Ticker']} ({row['Asset_Class']})\n{row['Target_Weight_Pct']}" for _, row in asset_alloc_df.iterrows()]
    weights = asset_alloc_df["Target_Weight"]
    colors = [PALETTE.get(t, "#4F81BD") for t in asset_alloc_df["Ticker"]]
    
    wedges, texts, autotexts = ax.pie(
        weights, labels=labels, autopct="%1.1f%%", pctdistance=0.75,
        startangle=140, colors=colors,
        wedgeprops=dict(width=0.45, edgecolor="white", linewidth=2)
    )
    
    for t in texts:
        t.set_fontsize(9.5)
        t.set_fontweight("semibold")
    for at in autotexts:
        at.set_fontsize(9)
        at.set_color("white")
        at.set_fontweight("bold")
        
    ax.text(0, 0, "Target\nAllocation\n100%", ha="center", va="center", fontsize=13, fontweight="bold", color="#1F4E79")
    ax.set_title("Illustrative Asset Allocation Breakdown", fontsize=14, fontweight="bold", pad=20)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig.savefig(output_path)
    plt.close(fig)
    logger.info(f"Saved: {output_path}")


def plot_correlation_heatmap(
    corr_matrix: pd.DataFrame,
    output_path: str = "reports/figures/correlation_heatmap.png"
):
    """4. Correlation Heatmap: Inter-asset return correlation matrix."""
    logger.info("Generating Correlation Heatmap...")
    fig, ax = plt.subplots(figsize=(8, 6.5), dpi=300)
    
    cmap = sns.diverging_palette(220, 20, as_cmap=True)
    sns.heatmap(
        corr_matrix, annot=True, fmt=".2f", cmap="coolwarm", vmin=-0.2, vmax=1.0,
        square=True, linewidths=1.5, linecolor="white", cbar_kws={"shrink": 0.8},
        ax=ax, annot_kws={"fontsize": 11, "fontweight": "bold"}
    )
    
    ax.set_title("5-Year Daily Return Correlation Matrix", fontsize=14, fontweight="bold", pad=15)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig.savefig(output_path)
    plt.close(fig)
    logger.info(f"Saved: {output_path}")


def plot_risk_return_scatter(
    asset_alloc_df: pd.DataFrame,
    portfolio_perf_df: pd.DataFrame,
    benchmark_perf_df: pd.DataFrame,
    risk_free_rate: float = 0.035,
    output_path: str = "reports/figures/risk_return_scatter.png"
):
    """5. Risk versus Return Scatter Plot: Annualized Volatility vs CAGR."""
    logger.info("Generating Risk vs Return Scatter Plot...")
    fig, ax = plt.subplots(figsize=(10, 6.5), dpi=300)
    
    num_days = len(portfolio_df := portfolio_perf_df)
    
    # Portfolio stats
    p_start = portfolio_df["Portfolio_Value"].iloc[0] / (1.0 + portfolio_df["Daily_Return"].iloc[0])
    p_end = portfolio_df["Portfolio_Value"].iloc[-1]
    p_cagr = (p_end / p_start) ** (252.0 / num_days) - 1.0
    p_vol = portfolio_df["Daily_Return"].std() * np.sqrt(252)
    
    # Benchmark stats
    b_start = benchmark_perf_df["Benchmark_Value"].iloc[0] / (1.0 + benchmark_perf_df["Daily_Return"].iloc[0])
    b_end = benchmark_perf_df["Benchmark_Value"].iloc[-1]
    b_cagr = (b_end / b_start) ** (252.0 / num_days) - 1.0
    b_vol = benchmark_perf_df["Daily_Return"].std() * np.sqrt(252)

    # Plot individual ETFs
    for _, row in asset_alloc_df.iterrows():
        t = row["Ticker"]
        v = row["Annualized_Volatility"] * 100
        c = row["CAGR"] * 100
        color = PALETTE.get(t, "#4F81BD")
        ax.scatter(v, c, color=color, s=150, zorder=5, label=f"{t} ({row['Asset_Class']})")
        ax.annotate(f"{t}\n({c:.1f}%, {v:.1f}%)", xy=(v, c), xytext=(8, -5),
                    textcoords="offset points", fontsize=9, fontweight="bold")

    # Plot Portfolio and Benchmark
    ax.scatter(p_vol * 100, p_cagr * 100, color=PALETTE["Portfolio"], s=280, marker="D",
               zorder=6, label=f"Portfolio (CAGR: {p_cagr*100:.1f}%, Vol: {p_vol*100:.1f}%)")
    ax.annotate("PORTFOLIO", xy=(p_vol * 100, p_cagr * 100), xytext=(10, 4),
                textcoords="offset points", fontsize=10, fontweight="heavy", color=PALETTE["Portfolio"])

    ax.scatter(b_vol * 100, b_cagr * 100, color=PALETTE["Benchmark"], s=250, marker="s",
               zorder=6, label=f"SPY Benchmark (CAGR: {b_cagr*100:.1f}%, Vol: {b_vol*100:.1f}%)")
    ax.annotate("SPY BENCHMARK", xy=(b_vol * 100, b_cagr * 100), xytext=(10, -12),
                textcoords="offset points", fontsize=10, fontweight="heavy", color=PALETTE["Benchmark"])

    # Reference line for Risk-Free Rate
    ax.axhline(risk_free_rate * 100, color="gray", linestyle=":", linewidth=1.2, label=f"Risk-Free Rate ({risk_free_rate*100:.1f}%)")

    ax.set_title("Risk vs. Return Frontier: Multi-Asset Portfolio, Benchmark & Holdings", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Annualized Volatility (%)", fontsize=11, fontweight="bold")
    ax.set_ylabel("Compound Annual Growth Rate (CAGR %)", fontsize=11, fontweight="bold")
    ax.grid(True)
    ax.legend(frameon=True, facecolor="#F9FBFD", loc="upper left", fontsize=8.5)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig.savefig(output_path)
    plt.close(fig)
    logger.info(f"Saved: {output_path}")


def plot_portfolio_drawdown(
    portfolio_perf_df: pd.DataFrame,
    benchmark_perf_df: pd.DataFrame,
    output_path: str = "reports/figures/portfolio_drawdown.png"
):
    """6. Portfolio Drawdown Chart: Underwater historical drawdowns vs SPY."""
    logger.info("Generating Portfolio Drawdown Chart...")
    fig, ax = plt.subplots(figsize=(12, 6), dpi=300)
    
    dates = pd.to_datetime(portfolio_perf_df["Date"])
    p_dd = portfolio_perf_df["Drawdown"] * 100
    b_dd = benchmark_perf_df["Drawdown"] * 100
    
    ax.plot(dates, p_dd, label="Portfolio Drawdown", color=PALETTE["Portfolio"], linewidth=1.8)
    ax.fill_between(dates, p_dd, 0, color=PALETTE["Portfolio"], alpha=0.25)
    
    ax.plot(dates, b_dd, label="SPY Benchmark Drawdown", color=PALETTE["Benchmark"], linewidth=1.4, linestyle="--", alpha=0.8)
    
    max_p_dd = p_dd.min()
    max_b_dd = b_dd.min()
    
    ax.set_title("Underwater Drawdown Profile: Multi-Asset Portfolio vs. S&P 500", fontsize=14, fontweight="bold", pad=15)
    ax.set_ylabel("Drawdown from Peak (%)", fontsize=11, fontweight="bold")
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
    ax.grid(True)
    ax.legend(frameon=True, facecolor="#F9FBFD", loc="lower left", fontsize=10)
    
    # Annotate max drawdown
    ax.text(0.98, 0.05, f"Max Portfolio Drawdown: {max_p_dd:.2f}%\nMax SPY Drawdown: {max_b_dd:.2f}%",
            transform=ax.transAxes, ha="right", va="bottom",
            bbox=dict(boxstyle="round,pad=0.5", facecolor="white", edgecolor="#D0D7DE", alpha=0.9),
            fontsize=9.5, fontweight="bold")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig.savefig(output_path)
    plt.close(fig)
    logger.info(f"Saved: {output_path}")


def plot_monthly_return_heatmap(
    portfolio_perf_df: pd.DataFrame,
    output_path: str = "reports/figures/monthly_return_heatmap.png"
):
    """7. Monthly Return Heatmap: Calendar breakdown of monthly portfolio returns."""
    logger.info("Generating Monthly Return Heatmap...")
    df = portfolio_perf_df.copy()
    df["Date"] = pd.to_datetime(df["Date"])
    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.month
    
    # Calculate monthly return as (1 + R_daily).prod() - 1
    monthly_ret = df.groupby(["Year", "Month"])["Daily_Return"].apply(lambda r: (1.0 + r).prod() - 1.0).unstack()
    
    # Map month numbers to 3-letter codes
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    monthly_ret.columns = [month_names[m - 1] for m in monthly_ret.columns]
    
    # Compute full-year return
    annual_ret = df.groupby("Year")["Daily_Return"].apply(lambda r: (1.0 + r).prod() - 1.0)
    monthly_ret["Full Year"] = annual_ret

    fig, ax = plt.subplots(figsize=(12, 5), dpi=300)
    
    sns.heatmap(
        monthly_ret * 100, annot=True, fmt=".1f", cmap="vlag", center=0,
        linewidths=1.0, linecolor="white", cbar_kws={"label": "Monthly Return (%)", "shrink": 0.8},
        ax=ax, annot_kws={"fontsize": 9.5, "fontweight": "bold"}
    )
    
    ax.set_title("Portfolio Monthly & Annual Historical Returns (%)", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Calendar Month", fontsize=11, fontweight="bold")
    ax.set_ylabel("Year", fontsize=11, fontweight="bold")
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig.savefig(output_path)
    plt.close(fig)
    logger.info(f"Saved: {output_path}")


def plot_benchmark_comparison(
    risk_metrics_df: pd.DataFrame,
    output_path: str = "reports/figures/benchmark_comparison.png"
):
    """8. Benchmark Comparison Chart: Grouped bar chart of key risk/return metrics."""
    logger.info("Generating Benchmark Comparison Bar Chart...")
    # Select key numeric metrics to visualize
    target_metrics = [
        "CAGR (Annualized Return)",
        "Annualized Volatility (Risk)",
        "Sharpe Ratio (Rf=3.5%)",
        "Maximum Drawdown (Peak-to-Trough)",
        "Daily VaR (95% 1-day)"
    ]
    
    df_sub = risk_metrics_df[risk_metrics_df["Metric"].isin(target_metrics)].copy()
    
    # Helper to parse string values to floats
    def clean_val(val_str):
        clean = str(val_str).replace("%", "").replace("$", "").replace(",", "")
        return float(clean)

    p_vals = [clean_val(row["Portfolio"]) for _, row in df_sub.iterrows()]
    b_vals = [clean_val(row["Benchmark (SPY)"]) for _, row in df_sub.iterrows()]
    labels = [m.split("(")[0].strip() for m in df_sub["Metric"]]

    x = np.arange(len(labels))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(11, 6), dpi=300)
    
    rects1 = ax.bar(x - width/2, p_vals, width, label="Portfolio", color=PALETTE["Portfolio"], edgecolor="none")
    rects2 = ax.bar(x + width/2, b_vals, width, label="Benchmark (SPY)", color=PALETTE["Benchmark"], edgecolor="none")
    
    ax.set_title("Portfolio vs Benchmark (SPY) Performance & Risk Comparison", fontsize=14, fontweight="bold", pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=10, fontweight="bold")
    ax.axhline(0, color="gray", linewidth=0.8)
    ax.grid(axis="y")
    ax.legend(frameon=True, facecolor="#F9FBFD", loc="upper right")
    
    # Value annotations on bars
    for bar in rects1:
        height = bar.get_height()
        va = "bottom" if height >= 0 else "top"
        ax.annotate(f"{height:.1f}",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3 if height >= 0 else -10),
                    textcoords="offset points", ha="center", va=va, fontsize=8.5, fontweight="bold")
                    
    for bar in rects2:
        height = bar.get_height()
        va = "bottom" if height >= 0 else "top"
        ax.annotate(f"{height:.1f}",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3 if height >= 0 else -10),
                    textcoords="offset points", ha="center", va=va, fontsize=8.5, fontweight="bold")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig.savefig(output_path)
    plt.close(fig)
    logger.info(f"Saved: {output_path}")


def generate_all_visualizations(
    portfolio_perf_df: pd.DataFrame,
    benchmark_perf_df: pd.DataFrame,
    daily_returns_df: pd.DataFrame,
    asset_alloc_df: pd.DataFrame,
    corr_matrix: pd.DataFrame,
    risk_metrics_df: pd.DataFrame,
    tickers: List[str],
    risk_free_rate: float = 0.035,
    output_dir: str = "reports/figures"
):
    """Generates all 8 institutional visualizations."""
    os.makedirs(output_dir, exist_ok=True)
    plot_portfolio_growth(portfolio_perf_df, benchmark_perf_df, os.path.join(output_dir, "portfolio_growth.png"))
    plot_etf_performance_comparison(daily_returns_df, tickers, os.path.join(output_dir, "etf_performance_comparison.png"))
    plot_asset_allocation_donut(asset_alloc_df, os.path.join(output_dir, "asset_allocation_donut.png"))
    plot_correlation_heatmap(corr_matrix, os.path.join(output_dir, "correlation_heatmap.png"))
    plot_risk_return_scatter(asset_alloc_df, portfolio_perf_df, benchmark_perf_df, risk_free_rate, os.path.join(output_dir, "risk_return_scatter.png"))
    plot_portfolio_drawdown(portfolio_perf_df, benchmark_perf_df, os.path.join(output_dir, "portfolio_drawdown.png"))
    plot_monthly_return_heatmap(portfolio_perf_df, os.path.join(output_dir, "monthly_return_heatmap.png"))
    plot_benchmark_comparison(risk_metrics_df, os.path.join(output_dir, "benchmark_comparison.png"))
    logger.info("All 8 financial visualizations generated successfully.")

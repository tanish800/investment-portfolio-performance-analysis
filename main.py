"""
INVESTMENT PORTFOLIO PERFORMANCE ANALYSIS
Main Execution Pipeline Orchestrator

Executes the complete financial data lifecycle:
1. Downloads authentic historical market observations from Yahoo Finance (yfinance).
2. Cleans, synchronizes, and validates market data.
3. Computes daily returns, constant-weight portfolio growth, and benchmark performance.
4. Calculates advanced institutional risk metrics (CAGR, Volatility, Sharpe, MDD, VaR, Beta, Alpha).
5. Generates the 12-worksheet Advanced Excel workbook with tables, KPI cards, and charts.
6. Exports Power BI-ready star-schema dimension and fact tables.
7. Produces 8 publication-grade financial visualizations.
"""

import argparse
import json
import logging
import os
import sys
import time

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.data_collection import download_market_data
from src.data_cleaning import clean_market_data, validate_market_data
from src.portfolio_analysis import (
    calculate_daily_returns,
    calculate_portfolio_performance,
    calculate_benchmark_performance,
    calculate_asset_allocation_summary,
    calculate_correlation_matrix
)
from src.risk_analysis import generate_risk_metrics_table
from src.visualization import generate_all_visualizations
from src.excel_generator import generate_excel_workbook
from src.powerbi_prep import prepare_powerbi_tables

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("InvestmentPortfolioAnalysis")


def load_config(config_path: str = "config/portfolio_config.json") -> dict:
    """Loads and validates portfolio configuration file."""
    if not os.path.isabs(config_path):
        config_path = os.path.join(BASE_DIR, config_path)
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found at: {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    return config


def run_pipeline(config_path: str = "config/portfolio_config.json", refresh: bool = False):
    """
    Executes the complete investment portfolio analysis pipeline.
    """
    start_time = time.time()
    print("=" * 80)
    print(" INVESTMENT PORTFOLIO PERFORMANCE ANALYSIS ")
    print(" Multi-Asset ETF Strategy vs S&P 500 Benchmark ")
    print("=" * 80)

    # 1. Load Configuration
    logger.info(f"Loading configuration from '{config_path}'...")
    config = load_config(config_path)
    tickers = list(config["assets"].keys())
    weights = {t: config["assets"][t]["target_weight"] for t in tickers}
    start_date = config["date_range"]["start_date"]
    end_date = config["date_range"]["end_date"]
    initial_val = config.get("initial_portfolio_value", 100000.0)
    risk_free_rate = config.get("risk_free_rate", 0.035)
    bench_ticker = config.get("benchmark_ticker", "SPY")

    logger.info(f"Target Universe: {tickers}")
    logger.info(f"Configured Weights: {weights}")
    logger.info(f"Date Horizon: {start_date} to {end_date}")

    # 2. Authentic Data Collection
    print("\n[Step 1/8] Downloading authentic historical market data from Yahoo Finance...")
    raw_dir = os.path.join(BASE_DIR, "data", "raw")
    meta_dir = os.path.join(BASE_DIR, "data", "metadata")
    raw_df = download_market_data(
        tickers=tickers,
        start_date=start_date,
        end_date=end_date,
        output_dir=raw_dir,
        metadata_dir=meta_dir,
        refresh=refresh
    )
    logger.info(f"Market data acquired: {len(raw_df)} total observations.")

    # 3. Data Cleaning and Validation
    print("\n[Step 2/8] Cleaning and validating market observations...")
    processed_dir = os.path.join(BASE_DIR, "data", "processed")
    cleaned_df = clean_market_data(
        raw_df=raw_df,
        expected_tickers=tickers,
        output_dir=processed_dir
    )

    # 4. Return Calculations
    print("\n[Step 3/8] Computing daily returns from Adjusted Close...")
    daily_returns_df = calculate_daily_returns(cleaned_df, output_dir=processed_dir)

    # 5. Portfolio & Benchmark Performance
    print("\n[Step 4/8] Simulating portfolio and benchmark growth...")
    portfolio_perf_df = calculate_portfolio_performance(
        daily_returns_df=daily_returns_df,
        weights=weights,
        initial_value=initial_val,
        output_dir=processed_dir
    )
    benchmark_perf_df = calculate_benchmark_performance(
        daily_returns_df=daily_returns_df,
        benchmark_ticker=bench_ticker,
        initial_value=initial_val,
        output_dir=processed_dir
    )
    asset_alloc_df = calculate_asset_allocation_summary(
        cleaned_df=cleaned_df,
        daily_returns_df=daily_returns_df,
        weights_config=config["assets"],
        initial_value=initial_val,
        output_dir=processed_dir
    )
    corr_matrix = calculate_correlation_matrix(
        daily_returns_df=daily_returns_df,
        tickers=tickers,
        output_dir=processed_dir
    )

    # 6. Risk Analysis & Institutional Scorecard
    print("\n[Step 5/8] Computing comprehensive institutional risk scorecard...")
    risk_metrics_df = generate_risk_metrics_table(
        portfolio_perf_df=portfolio_perf_df,
        benchmark_perf_df=benchmark_perf_df,
        daily_returns_df=daily_returns_df,
        risk_free_rate=risk_free_rate,
        output_dir=processed_dir
    )

    # 7. Financial Visualizations
    print("\n[Step 6/8] Generating 8 publication-grade financial charts...")
    figures_dir = os.path.join(BASE_DIR, "reports", "figures")
    generate_all_visualizations(
        portfolio_perf_df=portfolio_perf_df,
        benchmark_perf_df=benchmark_perf_df,
        daily_returns_df=daily_returns_df,
        asset_alloc_df=asset_alloc_df,
        corr_matrix=corr_matrix,
        risk_metrics_df=risk_metrics_df,
        tickers=tickers,
        risk_free_rate=risk_free_rate,
        output_dir=figures_dir
    )

    # 8. Advanced Excel Workbook
    print("\n[Step 7/8] Generating 12-worksheet advanced financial Excel workbook...")
    excel_path = os.path.join(BASE_DIR, "excel", "Investment_Portfolio_Performance_Analysis.xlsx")
    generate_excel_workbook(
        raw_df=raw_df,
        cleaned_df=cleaned_df,
        daily_returns_df=daily_returns_df,
        portfolio_perf_df=portfolio_perf_df,
        benchmark_perf_df=benchmark_perf_df,
        asset_alloc_df=asset_alloc_df,
        corr_matrix=corr_matrix,
        risk_metrics_df=risk_metrics_df,
        config=config,
        output_path=excel_path
    )

    # 9. Power BI Data Preparation
    print("\n[Step 8/8] Preparing Power BI Star Schema tables...")
    powerbi_dir = os.path.join(BASE_DIR, "powerbi", "powerbi_ready_data")
    prepare_powerbi_tables(
        cleaned_df=cleaned_df,
        daily_returns_df=daily_returns_df,
        portfolio_perf_df=portfolio_perf_df,
        benchmark_perf_df=benchmark_perf_df,
        asset_alloc_df=asset_alloc_df,
        risk_metrics_df=risk_metrics_df,
        config=config,
        output_dir=powerbi_dir
    )

    elapsed = time.time() - start_time
    print("\n" + "=" * 80)
    print(" PIPELINE EXECUTION COMPLETED SUCCESSFULLY ")
    print(f" Execution Time: {elapsed:.2f} seconds ")
    print("=" * 80)
    
    # Print Executive Summary Scorecard to Console
    print("\nEXECUTIVE SCORECARD HIGHLIGHTS:")
    print("-" * 75)
    for _, row in risk_metrics_df.head(10).iterrows():
        print(f"  {row['Metric']:<36} | Portfolio: {row['Portfolio']:>14} | Benchmark (SPY): {row['Benchmark (SPY)']:>14}")
    print("-" * 75)
    print(f"\nGenerated Deliverables:")
    print(f"  • Processed Data: {processed_dir}")
    print(f"  • Excel Workbook: {excel_path}")
    print(f"  • Visualizations: {figures_dir}")
    print(f"  • Power BI Ready: {powerbi_dir}")
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(description="Investment Portfolio Performance Analysis Pipeline")
    parser.add_argument("--config", default="config/portfolio_config.json", help="Path to portfolio configuration file")
    parser.add_argument("--refresh", action="store_true", help="Force redownload of fresh data from Yahoo Finance")
    args = parser.parse_args()

    run_pipeline(config_path=args.config, refresh=args.refresh)


if __name__ == "__main__":
    main()

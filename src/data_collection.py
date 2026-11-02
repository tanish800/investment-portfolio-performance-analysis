"""
Data Collection Module
Retrieves authentic historical market data from Yahoo Finance via yfinance.
"""

import json
import logging
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

import pandas as pd
import yfinance as yf

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def get_yfinance_session():
    """
    Creates a resilient session for yfinance requests.
    Supports curl_cffi with chrome impersonation and handles enterprise SSL environments.
    """
    try:
        import curl_cffi.requests as cffi_requests
        session = cffi_requests.Session(impersonate="chrome", verify=False)
        return session
    except ImportError:
        logger.warning("curl_cffi not available, falling back to standard requests session.")
        import requests
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        return session


def fetch_etf_history(
    ticker: str,
    start_date: str,
    end_date: str,
    session=None
) -> pd.DataFrame:
    """
    Downloads historical daily data for a single ETF from Yahoo Finance.
    Ensures non-adjusted OHLC and explicit Adjusted Close columns are captured.
    """
    logger.info(f"Fetching market data for ticker '{ticker}' from {start_date} to {end_date}...")
    try:
        yf_ticker = yf.Ticker(ticker, session=session)
        # auto_adjust=False ensures 'Adj Close' is provided explicitly alongside raw 'Close'
        df = yf_ticker.history(start=start_date, end=end_date, auto_adjust=False)
        
        if df.empty:
            raise ValueError(f"Yahoo Finance returned an empty dataset for ticker '{ticker}'.")
            
        # Standardize columns and index
        df = df.reset_index()
        # Normalize Date column: extract YYYY-MM-DD
        if pd.api.types.is_datetime64_any_dtype(df["Date"]):
            df["Date"] = df["Date"].dt.tz_localize(None).dt.strftime("%Y-%m-%d")
        else:
            df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")
            
        df["Ticker"] = ticker
        
        # Ensure mandatory columns exist
        expected_cols = ["Date", "Ticker", "Open", "High", "Low", "Close", "Adj Close", "Volume", "Dividends", "Stock Splits"]
        for col in expected_cols:
            if col not in df.columns:
                if col == "Adj Close" and "Close" in df.columns:
                    logger.warning(f"'Adj Close' not separated for {ticker}; using 'Close'.")
                    df["Adj Close"] = df["Close"]
                elif col in ["Dividends", "Stock Splits"]:
                    df[col] = 0.0
                else:
                    df[col] = None

        return df[expected_cols]
        
    except Exception as e:
        logger.error(f"Error fetching data for ticker '{ticker}': {e}")
        raise RuntimeError(
            f"Failed to retrieve authentic data for {ticker} from Yahoo Finance: {e}. "
            "Please verify your network connection or retry later. Synthetic data is prohibited."
        ) from e


def download_market_data(
    tickers: List[str],
    start_date: str,
    end_date: str,
    output_dir: str = "data/raw",
    metadata_dir: str = "data/metadata",
    refresh: bool = False
) -> pd.DataFrame:
    """
    Downloads market data for all specified tickers, saves raw CSV and metadata.
    """
    raw_csv_path = os.path.join(output_dir, "raw_market_data.csv")
    metadata_path = os.path.join(metadata_dir, "dataset_metadata.json")
    
    if os.path.exists(raw_csv_path) and not refresh:
        logger.info(f"Existing raw data found at '{raw_csv_path}'. Loading from local cache.")
        df_all = pd.read_csv(raw_csv_path)
        return df_all

    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(metadata_dir, exist_ok=True)
    
    session = get_yfinance_session()
    all_frames = []
    ticker_stats = {}
    
    for ticker in tickers:
        df_ticker = fetch_etf_history(ticker, start_date, end_date, session=session)
        all_frames.append(df_ticker)
        ticker_stats[ticker] = {
            "record_count": len(df_ticker),
            "start_date": df_ticker["Date"].min(),
            "end_date": df_ticker["Date"].max(),
            "min_adj_close": float(df_ticker["Adj Close"].min()),
            "max_adj_close": float(df_ticker["Adj Close"].max())
        }
        
    df_combined = pd.concat(all_frames, ignore_index=True)
    # Sort deterministically by Date then Ticker
    df_combined = df_combined.sort_values(by=["Date", "Ticker"]).reset_index(drop=True)
    
    # Save raw CSV
    df_combined.to_csv(raw_csv_path, index=False)
    logger.info(f"Authentic market data saved to '{raw_csv_path}' ({len(df_combined)} records).")
    
    # Record metadata
    retrieval_meta = {
        "dataset_name": "Yahoo Finance Historical ETF Market Observations",
        "source": "https://finance.yahoo.com/",
        "api_library": f"yfinance {yf.__version__}",
        "retrieval_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "date_range_requested": {"start_date": start_date, "end_date": end_date},
        "actual_date_range": {
            "start_date": df_combined["Date"].min(),
            "end_date": df_combined["Date"].max()
        },
        "tickers": tickers,
        "total_records": len(df_combined),
        "fields": list(df_combined.columns),
        "ticker_summary": ticker_stats,
        "is_synthetic": False,
        "license_and_usage": "Data provided for educational and analytical research purposes via Yahoo Finance terms of service."
    }
    
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(retrieval_meta, f, indent=2)
    logger.info(f"Dataset metadata successfully written to '{metadata_path}'.")
    
    return df_combined


if __name__ == "__main__":
    test_tickers = ["SPY", "QQQ", "AGG", "GLD", "VNQ"]
    df = download_market_data(test_tickers, "2021-01-01", "2025-12-31", refresh=True)
    print(df.head())
    print("Downloaded tickers:", df["Ticker"].unique())

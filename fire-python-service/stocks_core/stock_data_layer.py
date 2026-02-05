"""
Market Data Acquisition and Transformation Layer.

This module provides utilities for downloading historical stock prices via 
yfinance, handling MultiIndex data structures, and calculating weighted 
portfolio returns for the FIRE analysis engine.
"""
import yfinance as yf
import pandas as pd


def get_portfolio_prices(tickers, start):
    """
    Downloads historical price data and validates that tickers have sufficient historical data.
    It handles yfinance MultiIndex formatting.

    Args:
        tickers (list/str): A list of stock symbols or a single symbol string.
        start (str): The start date for the data (YYYY-MM-DD).

    Returns:
        pd.DataFrame or pd.Series: Cleaned closing prices with a simplified index.
    """
    # Download with auto_adjust to avoid the subscriptable error
    data = yf.download(tickers, start=start,
                       auto_adjust=True, group_by='column')

    if data is None or data.empty:
        raise ValueError(
            f"No data returned for {tickers}. check internet or tickers.")

    # yfinance returns a MultiIndex if multiple tickers are passed
    if isinstance(data.columns, pd.MultiIndex):
        if 'Close' in data.columns.levels[0]:
            prices = data['Close']
        else:
            # Fallback for different yfinance versions
            prices = data.xs(
                'Close', axis=1, level=0) if 'Close' in data.columns else data
    else:
        # Single ticker case
        prices = data['Close'] if 'Close' in data else data

    # Handle mixed start dates (e.g., if one stock IPO'd after 2010)
    # We drop days where NO stocks had data, then fill gaps for individual stocks.
    prices = prices.dropna(how='all').ffill()

    # Log a warning if a ticker started much later than the requested 'start' date
    if isinstance(prices, pd.DataFrame):
        for ticker in prices.columns:
            first_date = prices[ticker].first_valid_index()
            # The 'hasattr' check prevents IDE red-lines for strftime
            if isinstance(first_date, pd.Timestamp):
                if str(first_date.year) > start[:4]:
                    print(
                        f"NOTE: {ticker} history only begins in {first_date.year}.")

    # Strip the 'Date' name from the index to prevent crashes
    prices.index.name = None

    return prices


def calculate_portfolio_returns(prices, weights):
    """
    Calculates weighted daily returns for a portfolio. Relative weights.

    Args:
        prices (pd.DataFrame): Historical price data.
        weights (dict): A dictionary mapping tickers to their weight values.

    Returns:
        pd.Series: The daily percentage returns for the combined portfolio.
    """
    returns = prices.ffill().pct_change().dropna()

    if returns.empty:
        raise ValueError("No valid returns data. Tickers might be invalid.")

    if isinstance(returns, pd.Series):
        return returns

    available_tickers = returns.columns
    weight_map = {t: weights[t] for t in available_tickers if t in weights}

    if not weight_map:
        raise ValueError(
            "None of the tickers in your JSON were found in the downloaded data.")

    # Force numeric data
    weight_series = pd.Series(weight_map, dtype=float)

    # Re-normalize weights
    total_w = weight_series.sum()
    if total_w > 0:
        weight_series = weight_series / total_w
    else:
        raise ValueError("Weights sum to zero.")

    return returns.dot(weight_series)


def current_portfolio_value(prices, weights):
    """
    Calculates the most recent total value of the portfolio.

    Args:
        prices (pd.DataFrame/pd.Series): Historical price data.
        weights (dict): Ticker-weight mapping.

    Returns:
        float: The current total dollar value.
    """
    if isinstance(prices, pd.Series):
        return prices.iloc[-1]

    latest_prices = prices.iloc[-1]
    weight_series = pd.Series(weights, dtype=float)

    # Alignment check to prevent NaN if tickers are missing
    common_tickers = latest_prices.index.intersection(weight_series.index)

    return (latest_prices[common_tickers] * weight_series[common_tickers]).sum()

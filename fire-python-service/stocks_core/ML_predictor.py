"""
Log-Linear Regression Engine for Portfolio Projections.

This module provides the core ML logic to forecast future portfolio values
by transforming cumulative returns into log-space, fitting a linear trend,
and applying conservative financial constraints (CAGR caps).
"""
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import r2_score
import numpy as np


def predict_future(returns, current_value, monthly_contribution, years):
    """
    Predicts future portfolio value using log-linear regression
    but uses the more conservative of regression CAGR vs historical CAGR.

    Args:
        returns (pd.Series): Historical daily returns (percentage format).
        current_value (float): Starting portfolio balance.
        monthly_contribution (float): Cash added every 21 trading days.
        years (int): Number of years to forecast.

    Returns:
        tuple: (future_values_array, confidence_score)
    """
    safe_current_value = max(1.0, float(current_value))
    if returns.empty:
        raise ValueError("Cannot predict future: no returns data")

    # Standard financial constant for annualization
    x = np.arange(len(returns)).reshape(-1, 1)

    # Convert percentage returns into a cumulative price series
    y = ((1 + returns).cumprod() * safe_current_value).values.flatten()

    # Log-transform y to model exponential growth as a linear trend
    # We add 1e-9 (epsilon) to handle potential zero values
    y_clipped = np.clip(y, a_min=1.0, a_max=None)
    y_log = np.log(y_clipped)

    model_full = LinearRegression().fit(x, y_log)
    in_sample_r2 = r2_score(y_log, model_full.predict(x))

    # Evaluate model stability over time using 3-fold backtesting
    if len(returns) >= 60:
        tscv = TimeSeriesSplit(n_splits=3)
        scores = []

        print(
            f"Starting TimeSeries Cross-Validation (3 folds) for {len(returns)} data points...")

        for train_index, test_index in tscv.split(x):
            model_tmp = LinearRegression().fit(
                x[train_index], y_log[train_index])
            # Score the fit based on how well it follows the exponential trend
            fold_score = r2_score(
                y_log[test_index], model_tmp.predict(x[test_index]))
            scores.append(fold_score)
            print(f"Fold {len(scores)} Score: {fold_score:.4f}")

        scores_r2 = np.mean(scores)
        print(f"INFO: CV complete. Avg R2: {scores_r2:.4f}")
    else:
        # Default stability score if we don't have enough data to backtest
        print("INFO: Insufficient data for CV. Using in-sample fit only.")
        scores_r2 = in_sample_r2

    # Heuristic confidence: weighted 70% on historical fit, 30% on CV stability
    confidence = (in_sample_r2 * 0.7) + (max(0, scores_r2) * 0.3)

    # Extract slope (daily log-return) and convert to annual CAGR
    slope = model_full.coef_[0]
    annual_return_reg = np.exp(slope * 252) - 1

    # Historical average CAGR
    avg_daily_return = returns.mean()
    annual_return_hist = (1 + avg_daily_return) ** 252 - 1

    # Always take the more conservative estimate
    annual_return = min(annual_return_reg, annual_return_hist, 0.07)

    print(f"Regression annual return = {annual_return_reg:.4%}, "
          f"Historical annual return = {annual_return_hist:.4%}, "
          f"Using = {annual_return:.4%}")

    # Forecast future log-values and transform back to currency units year-by-year
    future_y = []
    balance = float(current_value)
    for _ in range(1, years + 1):
        balance *= (1 + annual_return)
        balance += (monthly_contribution * 12)
        future_y.append(balance)

    return np.array(future_y), round(float(confidence), 4)

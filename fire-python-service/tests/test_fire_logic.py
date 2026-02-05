import pytest
import numpy as np
import pandas as pd
from stocks_core.ML_predictor import predict_future
from stocks_core.time_to_FIRE import time_to_FIRE


def test_prediction_growth():
    # GIVEN: A steady 1% daily return (extreme, but easy to test)
    returns = pd.Series([0.01] * 100)
    current_val = 1000
    monthly_savings = 0
    years = 1

    # WHEN
    future = predict_future(returns, current_val, monthly_savings, years)

    # THEN: Future value should be greater than starting value
    assert future[-1] > current_val
    assert len(future) == years


def test_fire_already_reached():
    # GIVEN: A target lower than current value
    future_values = np.array([1000000, 1100000])
    target = 500000

    # WHEN
    result = time_to_FIRE(future_values, target)

    # THEN
    assert result["reached"] is True
    assert result["years_to_reach_goal"] == 0.0


def test_shortfall_calculation():
    # GIVEN: A target that is never reached
    future_values = np.array([100, 200, 300])
    target = 1000

    # WHEN
    result = time_to_FIRE(future_values, target)

    # THEN
    assert result["reached"] is False
    assert result["shortfall"] == 700.0

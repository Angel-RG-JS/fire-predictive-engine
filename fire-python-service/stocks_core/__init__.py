"""
Orchestration layer for the FIRE calculation engine.

This module defines the FireEngine class which integrates data retrieval, 
machine learning predictions, and financial goal analysis.
"""
from .stock_data_layer import get_portfolio_prices, calculate_portfolio_returns
from .ML_predictor import predict_future
from .time_to_FIRE import time_to_FIRE, calculate_monthly_needed


class FireEngine:
    """
    Handles the end-to-end execution of a FIRE financial simulation.

    Attributes:
        years_left (int): Time horizon until the desired retirement date.
        current_val (float): Initial portfolio balance.
        monthly_savings (float): Regular monthly contributions.
        allocations (dict): Ticker-to-weight mapping for the portfolio.
        fire_target (float): Total capital required based on the 4% rule (25x expenses).
    """

    def __init__(self, portfolio_data):
        """
        Initializes the engine with user-provided portfolio configurations.

        Args:
            portfolio_data (dict): Dictionary containing keys for retirement goals,
                                   current balances, and asset allocations.
        """
        # 1. User Horizon
        self.years_left = portfolio_data.get("years_to_retirement", 0)

        # 2. Financial Inputs
        self.current_val = portfolio_data.get("current_value", 0.0)
        self.monthly_savings = portfolio_data.get(
            "monthly_savings", 0)
        self.allocations = portfolio_data.get("allocations", {})

        # 3. Goal Calculation
        monthly_goal = portfolio_data.get("monthly_retirement_goal", 0.0)
        self.fire_target = 25 * (12 * monthly_goal)

    def run_analysis(self):
        """
        Executes the full pipeline: Data download, ML prediction, and FIRE analysis.

        Returns:
            dict: Comprehensive results including projection metrics and 
                  actionable advice if targets are not met.
        """
        # 1. Data Layer
        tickers = list(self.allocations.keys())
        if not tickers:
            raise ValueError("No tickers provided in allocations.")

        prices = get_portfolio_prices(tickers, start="2010-01-01")
        returns = calculate_portfolio_returns(prices, self.allocations)

        # 2. Prediction
        future_values, confidence = predict_future(
            returns, self.current_val, self.monthly_savings, self.years_left)

        # 3. FIRE Logic
        results = time_to_FIRE(future_values, self.fire_target)

        # 4. Inject "Specifics" for your Main.py report
        results.update({
            "confidence_score": confidence,
            "current_val": float(self.current_val),
            "fire_target": float(self.fire_target),
            "final_estimated_value": round(float(future_values[-1]), 2),
            "years_simulated": float(self.years_left),
            "monthly_savings": float(self.monthly_savings)
        })

        # 5. Actionable advice
        if not results.get("reached", False):
            # Calculate how much MORE they need to save monthly to hit the target
            results["monthly_needed"] = calculate_monthly_needed(
                self.fire_target,
                results["years_simulated"],
                results["final_estimated_value"]
            )
            results["shortfall"] = (
                self.fire_target - results["final_estimated_value"]
            )

        return results

"""
Portfolio FIRE Analysis Tool.

This module provides functions for downloading stock data, calculating 
portfolio returns, and using machine learning (log-linear regression) 
to project future values and time-to-FIRE (Financial Independence, Retire Early).
"""


def time_to_FIRE(future_values, fire_target):
    """
    Calculates when the portfolio hits the target and the final shortfall.
    Args:
        future_values (np.ndarray): Array of projected annual portfolio values.
        fire_target (float): The target monetary value for financial independence.

    Returns:
        dict: { years_to_reach_goal (int): Number of years until target is reached, 
        shortfall (float): Remaining gap if target not reached, 
        reached (bool): Whether target was achieved, 
        final_value (float): Portfolio value at end of horizon }
    """
    if len(future_values) == 0:
        return {
            "years_to_reach_goal": 0,
            "shortfall": fire_target,
            "reached": False,
            "final_value": 0}

    # Case: User is already at or above FIRE target today
    # We check index 0 (the start of the simulation)
    if fire_target <= future_values[0]:
        return {
            "years_to_reach_goal": 0,
            "shortfall": 0,
            "reached": True,
            # Show the compounding value anyway
            "final_value": round(float(future_values[-1]), 2)
        }

    for i, val in enumerate(future_values, start=1):
        if val >= fire_target:
            return {
                "years_to_reach_goal": int(i),
                "shortfall": round(float(0), 2),
                "reached": True,
                "final_value": round(float(future_values[-1]), 2)
            }

    # If target isn't reached, return the max time simulated
    max_val = future_values.max()
    # Always positive or zero
    shortfall = round(float(max(0, fire_target - max_val)), 2)

    return {
        "years_to_reach_goal": len(future_values),
        "shortfall": shortfall,
        "reached": False,
        "final_value": round(float(max_val), 2)
    }


def calculate_monthly_needed(fire_target, years, ml_projected_final_val):
    """
    Calculates the monthly contribution gap based on ML growth projections.

    This calculation assumes a linear fill of the shortfall (no compounding),
    meaning the shortfall is spread evenly across the remaining months.
    This makes the estimate conservative compared to a compounding model.

    Args:
        fire_target (float): The target monetary value for retirement.
        years (int/float): The time horizon for the investment.
        ml_projected_final_val (float): The projected value of current assets 
                                        with 0 future contributions.

    Returns:
        float: The monthly investment required to cover the shortfall.
    """
    months = years * 12
    if months <= 0:
        return 0

    # Derive the "Effective Growth" from ML's final value if you had 0 monthly savings.
    shortfall = fire_target - ml_projected_final_val

    if shortfall <= 0:
        return 0

    # We assume a linear/ML growth path, save that shortfall divided by the months remaining.
    # This assumes a worst case scenario
    monthly_investment = shortfall / months

    return round(monthly_investment, 2)

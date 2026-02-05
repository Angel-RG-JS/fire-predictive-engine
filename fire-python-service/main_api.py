"""
FastAPI Entry point for the FIRE Analysis Service.

This module provides REST endpoints to run financial simulations using 
the FireEngine, including health checks and ticker normalization logic.
"""
import os
import json
from pydantic import BaseModel
from fastapi import FastAPI, Depends, HTTPException, Response, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from stocks_core import FireEngine

app = FastAPI(title="FIRE Analysis Service")
auth_scheme = HTTPBearer()

# Global state for service health
READY_STATE = {
    "ticker_map_loaded": False,
    "version": "1.0.0"
}


def load_ticker_mapping():
    """Loads ticker alias mapping from local JSON resource."""
    file_path = os.path.join(os.path.dirname(
        __file__), "resources", "ticker_mapping.json")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            mapping = json.load(f)
            READY_STATE["ticker_map_loaded"] = True
            return mapping
    print("CRITICAL: Ticker mapping file not found.")
    return {}


# Load mapping into memory at startup
TICKER_MAP = load_ticker_mapping()


class PortfolioRequest(BaseModel):
    """Schema for user portfolio analysis requests."""
    years_to_retirement: int
    current_value: float
    monthly_retirement_goal: float
    monthly_savings: float
    allocations: dict


@app.get("/")
def home():
    """Root endpoint providing basic service info."""
    return {"message": "FIRE Engine API is running. Go to /docs for testing."}


@app.get("/health")
def health_check(response: Response):
    """
    Checks the readiness of the service.
    Returns 503 if critical resources (ticker mapping) are missing.
    """
    is_ready = READY_STATE["ticker_map_loaded"]

    health_status = {
        "status": "ok" if is_ready else "degraded",
        "version": READY_STATE["version"],
        "readiness": {
            "ml_brain_active": True,  # FastApi is up
            "ticker_mapping": is_ready
        }
    }

    # If mapping failed, return 503 so Docker knows we aren't 'Healthy'
    if not is_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return health_status


@app.post("/analyze")
async def analyze(
        request: PortfolioRequest,
        token: HTTPAuthorizationCredentials = Depends(auth_scheme)
):
    """
    Calculates FIRE projections based on portfolio data.

    Normalizes tickers via the TICKER_MAP and executes the ML simulation.
    """
    if not READY_STATE["ticker_map_loaded"]:
        raise HTTPException(
            status_code=503, detail="Service not ready: Ticker mapping missing")
    try:
        print(f"Verified Token: {token.credentials}")
        # Clean and normalization used charged map
        cleaned_allocations = {}
        for ticker, weight in request.allocations.items():
            clean_name = ticker.strip().upper()
            # If not in JSON, use user input
            final_ticker = TICKER_MAP.get(clean_name, clean_name)
            cleaned_allocations[final_ticker] = weight

        processed_data = request.model_dump()
        processed_data['allocations'] = cleaned_allocations

        engine = FireEngine(processed_data)
        return engine.run_analysis()

    except ValueError as e:
        # Error 400 (Bad Request) with which  ticker failed
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}") from e


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main_api:app", host="0.0.0.0", port=8000, reload=True)

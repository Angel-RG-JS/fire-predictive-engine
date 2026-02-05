#Multi-Asset Portfolio Predictive Engine
##A Hybrid Microservices Architecture for Financial Asset Forecasting

This repository hosts a decoupled system designed to simulate and predict portfolio viability against Financial Independence (FIRE) benchmarks.
A decoupled microservices ecosystem designed to simulate and predict the viability of multi-stock portfolios against FIRE (Financial Independence, Retire Early) benchmarks.
By leveraging the robustness of the JVM and the scientific computing agility of Python, this architecture provides a scalable solution for complex financial projections.

🏛️ ##Engineering Architecture

The system implements a Polyglot Microservices Pattern, ensuring that each component handles tasks according to the most efficient stack:

    Orchestration Layer (Spring Boot / Java): Manages business logic, parameter validation, and the core FIRE threshold engine. It serves as the authoritative gateway for state management.

    Inference Engine (FastAPI / Python): A high-performance scientific sub-system. It consumes structured JSON payloads to execute Scikit-learn predictive models, calculating multi-stock portfolio valuations with high precision.

    Data Exchange Protocol: Communication is handled via a Stateless RESTful API, utilizing optimized JSON mapping to bridge the transition from the JVM to the Python runtime.

🛠️ ##Tech Stack & Patterns

    Backend: Java 17+, Spring Boot 3.x.

    Intelligence: Python 3.10+, FastAPI, Scikit-learn, Pandas.

    Patterns: MVC, Separation of Concerns (SoC), Microservices, Predictive Modeling.

    Deployment (Planned): Containerization via Docker for cross-environment consistency.

🚀 ##Implementation Insight

Unlike monolithic "calculators", this architecture separates the statistical inference from the business rules.
This allows for independent scaling of the ML model without affecting the core financial engine—a critical requirement for modern Fintech infrastructures.

##Statistical Methodology: Log-Linear Trend Analysis

Unlike basic calculators, the engine utilizes a Log-Linear Regression model to project portfolio growth. By transforming cumulative returns into log-space, the system linearizes exponential compounding, allowing the Scikit-learn engine to fit a trend line that captures the underlying momentum of the assets.

Reliability Engineering: Weighted Confidence Scoring

The system generates a confidence_score using a robust dual-validation approach:

    In-Sample Fit: 70% of the score is derived from the R2 coefficient of the full historical dataset.

    Time-Series Cross-Validation: 30% is derived from a TimeSeriesSplit, testing the model's predictive stability across different historical windows.

This ensures that the projection isn't just a "best guess," but a mathematically validated trend based on historical asset behavior.

🧪 Testing and Validation

To ensure the integrity of the hybrid bridge and the accuracy of the log-linear projections, follow this three-tier validation suite:

1. Connectivity & Auth Handshake

Verify that the Java Orchestration layer can successfully authenticate and communicate with the Python Inference Engine.

    Action: Execute a POST request to /api/v1/fire/analyze using a valid JWT.

    Success Metric: HTTP 200 OK with a JSON payload containing confidence_score and final_estimated_value.

2. Mathematical Consistency Check

Validate that the Log-Linear transformation is correctly handling compounding growth.

    Action: Input a 0% allocation (cash-only) or assets with flat historical returns.

    Success Metric: The final_estimated_value should equal current_value + (monthly_savings * months), and confidence_score should reflect the linearity of the flat trend.

3. Cross-Validation Stability

Ensure the TimeSeriesSplit logic is functioning within the Python sub-system.

    Action: Check the Python logs during a request.

    Success Metric: Logs should indicate the execution of 3 distinct training/testing folds. A significantly low confidence_score (< 0.2) should correctly flag assets with high volatility or erratic historical trends.

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for pandas/scikit-learn
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

#Set the PYTHONPATH so the container knows 
# how to handle your relative imports in stocks_core
ENV PYTHONPATH=/app

# Expose FastAPI port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main_api:app", "--host", "0.0.0.0", "--port", "8000"]
# IRIS Economic System - Docker Image
# =====================================
#
# This Dockerfile creates a reproducible environment for running
# IRIS economic simulations.
#
# Build: docker build -t iris-simulation .
# Run: docker run -it iris-simulation

FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy the entire project
COPY . .

# Install the package in development mode
RUN pip install -e .

# Create directories for outputs
RUN mkdir -p /app/simulation_results /app/plots /app/data

# Set Python path
ENV PYTHONPATH=/app:$PYTHONPATH

# Default command (can be overridden)
CMD ["python", "-m", "iris.simulations.run_simulation", "--help"]

# Optional: Run tests on build
# RUN pytest iris/tests/ -v

# Labels
LABEL maintainer="Arnault Nolan <arnaultnolan@gmail.com>"
LABEL description="IRIS Economic System Simulation"
LABEL version="1.0.0"

# IRIS Economic System Simulation - Docker Container
# ====================================================
# Build: docker build -t iris-simulation .
# Run:   docker run -v $(pwd)/simulation_results:/app/simulation_results iris-simulation

# Base image: Python 3.11 slim for reduced size
FROM python:3.11-slim

# Metadata
LABEL maintainer="Arnault Nolan <arnaultnolan@gmail.com>"
LABEL description="IRIS Economic System Simulation - Thermodynamic Economic Model"
LABEL version="2.1.0"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app:$PYTHONPATH

# Install system dependencies required for scientific computing
# - gcc, g++: Compilers for building NumPy/SciPy from source if needed
# - build-essential: Build tools
# - libgomp1: OpenMP support for parallel operations
# - make, git: Build and version control tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    build-essential \
    libgomp1 \
    make \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (layer caching optimization)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY iris/ ./iris/
COPY config.yaml .
COPY setup.py .
COPY pyproject.toml .
COPY README.md .
COPY MAPPING_THEORY_CODE.md .

# Install the IRIS package in development mode
RUN pip install -e .

# Create directories for outputs (will be overridden if volumes mounted)
RUN mkdir -p simulation_results plots data

# Expose volume mount points for results
# Mount these when running to persist results:
#   docker run -v $(pwd)/simulation_results:/app/simulation_results \
#              -v $(pwd)/plots:/app/plots \
#              -v $(pwd)/data:/app/data \
#              iris-simulation
VOLUME ["/app/simulation_results", "/app/plots", "/app/data"]

# Default command: run simulation with default config
# Override with custom scenarios:
#   docker run iris-simulation python -m iris.simulations.run_simulation --scenario baseline_stable
#   docker run iris-simulation python -m iris.simulations.run_simulation --steps 1200
#
# Interactive shell:
#   docker run -it iris-simulation /bin/bash
#
# Mount custom config:
#   docker run -v $(pwd)/my_config.yaml:/app/config.yaml iris-simulation
#
# Run tests:
#   docker run iris-simulation pytest iris/tests/ -v
CMD ["python", "-m", "iris.simulations.run_simulation", "--config", "config.yaml"]

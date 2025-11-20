# IRIS Economic System - Makefile
# =================================
# Automation for development, testing, and deployment

# Variables
PYTHON := python
PIP := pip
DOCKER_IMAGE := iris-simulation
DOCKER_TAG := latest
PROJECT_NAME := iris

# Directories
SRC_DIR := iris
TEST_DIR := iris/tests
RESULTS_DIR := simulation_results
PLOTS_DIR := plots
DATA_DIR := data

# Phony targets
.PHONY: help install install-dev test test-unit test-integration test-slow test-coverage \
        lint format typecheck check-all clean clean-results \
        docker-build docker-run docker-shell docker-clean \
        sim sim-baseline sim-crisis sim-no-regulation sim-regulation-only \
        validate docs

# Default target
.DEFAULT_GOAL := help

# =============================================================================
# HELP
# =============================================================================

help:  ## Show this help message
	@echo "╔═══════════════════════════════════════════════════════════════════╗"
	@echo "║            IRIS Economic System - Makefile Commands              ║"
	@echo "╚═══════════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "Installation:"
	@echo "  make install         Install package in development mode"
	@echo "  make install-dev     Install with development dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  make test            Run all tests"
	@echo "  make test-unit       Run only unit tests"
	@echo "  make test-integration  Run integration tests"
	@echo "  make test-slow       Run slow/long-running tests"
	@echo "  make test-coverage   Run tests with coverage report"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint            Run flake8 linting"
	@echo "  make format          Format code with black + isort"
	@echo "  make typecheck       Run mypy type checking"
	@echo "  make check-all       Run all checks (lint + typecheck + test)"
	@echo ""
	@echo "Simulations:"
	@echo "  make sim             Run default simulation"
	@echo "  make sim-baseline    Run baseline_stable scenario (100 years)"
	@echo "  make sim-crisis      Run crisis_high_volatility scenario"
	@echo "  make sim-no-regulation  Run no_regulation scenario"
	@echo "  make sim-regulation-only  Run regulation_only scenario"
	@echo "  make validate        Run validation suite (Monte Carlo)"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build    Build Docker image"
	@echo "  make docker-run      Run simulation in Docker"
	@echo "  make docker-shell    Open interactive shell in Docker"
	@echo "  make docker-clean    Remove Docker image"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean           Clean build artifacts"
	@echo "  make clean-results   Clean simulation results"
	@echo ""

# =============================================================================
# INSTALLATION
# =============================================================================

install:  ## Install package in development mode
	$(PIP) install -e .

install-dev:  ## Install with development dependencies
	$(PIP) install -e ".[dev]"
	$(PIP) install -r requirements.txt

# =============================================================================
# TESTING
# =============================================================================

test:  ## Run all tests
	$(PYTHON) -m pytest $(TEST_DIR) -v

test-unit:  ## Run only unit tests
	$(PYTHON) -m pytest $(TEST_DIR) -v -m unit

test-integration:  ## Run integration tests
	$(PYTHON) -m pytest $(TEST_DIR) -v -m integration

test-slow:  ## Run slow/long-running tests
	$(PYTHON) -m pytest $(TEST_DIR) -v -m slow

test-coverage:  ## Run tests with coverage report
	$(PYTHON) -m pytest $(TEST_DIR) \
		--cov=$(SRC_DIR) \
		--cov-report=html \
		--cov-report=term-missing \
		--cov-report=xml

# =============================================================================
# CODE QUALITY
# =============================================================================

lint:  ## Run flake8 linting
	$(PYTHON) -m flake8 $(SRC_DIR)/ --count --statistics

format:  ## Format code with black and isort
	@echo "Running isort..."
	$(PYTHON) -m isort $(SRC_DIR)/
	@echo "Running black..."
	$(PYTHON) -m black $(SRC_DIR)/
	@echo "Code formatting complete!"

typecheck:  ## Run mypy type checking
	$(PYTHON) -m mypy $(SRC_DIR)/ --ignore-missing-imports

check-all:  ## Run all checks (lint + typecheck + test)
	@echo "Running all checks..."
	@$(MAKE) lint
	@$(MAKE) typecheck
	@$(MAKE) test
	@echo "All checks passed!"

# =============================================================================
# SIMULATIONS
# =============================================================================

sim:  ## Run default simulation (100 steps)
	$(PYTHON) -m iris.simulations.run_simulation --config config.yaml

sim-baseline:  ## Run baseline_stable scenario (100 years = 1200 steps)
	@echo "Running baseline_stable scenario (100 years)..."
	$(PYTHON) -m iris.simulations.run_simulation \
		--config config.yaml \
		--steps 1200 \
		--scenario baseline_stable

sim-crisis:  ## Run crisis_high_volatility scenario (50 years = 600 steps)
	@echo "Running crisis_high_volatility scenario (50 years)..."
	$(PYTHON) -m iris.simulations.run_simulation \
		--config config.yaml \
		--steps 600 \
		--scenario crisis_high_volatility

sim-no-regulation:  ## Run no_regulation scenario (~83 years = 1000 steps)
	@echo "Running no_regulation scenario (control)..."
	$(PYTHON) -m iris.simulations.run_simulation \
		--config config.yaml \
		--steps 1000 \
		--scenario no_regulation

sim-regulation-only:  ## Run regulation_only scenario (~42 years = 500 steps)
	@echo "Running regulation_only scenario (thesis illustration)..."
	$(PYTHON) -m iris.simulations.run_simulation \
		--config config.yaml \
		--steps 500 \
		--scenario regulation_only

validate:  ## Run validation suite (Monte Carlo, sensitivity analysis)
	@echo "Running validation suite..."
	$(PYTHON) -m iris.core.iris_validation --monte-carlo --runs 100

# =============================================================================
# DOCKER
# =============================================================================

docker-build:  ## Build Docker image
	docker build -t $(DOCKER_IMAGE):$(DOCKER_TAG) .

docker-run:  ## Run simulation in Docker with volume mounts
	docker run --rm \
		-v $(PWD)/$(RESULTS_DIR):/app/$(RESULTS_DIR) \
		-v $(PWD)/$(PLOTS_DIR):/app/$(PLOTS_DIR) \
		-v $(PWD)/$(DATA_DIR):/app/$(DATA_DIR) \
		$(DOCKER_IMAGE):$(DOCKER_TAG)

docker-shell:  ## Open interactive shell in Docker
	docker run --rm -it \
		-v $(PWD)/$(RESULTS_DIR):/app/$(RESULTS_DIR) \
		-v $(PWD)/$(PLOTS_DIR):/app/$(PLOTS_DIR) \
		-v $(PWD)/$(DATA_DIR):/app/$(DATA_DIR) \
		$(DOCKER_IMAGE):$(DOCKER_TAG) \
		/bin/bash

docker-clean:  ## Remove Docker image
	docker rmi $(DOCKER_IMAGE):$(DOCKER_TAG)

# =============================================================================
# CLEANUP
# =============================================================================

clean:  ## Clean build artifacts and caches
	@echo "Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .coverage.*
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*~" -delete
	@echo "Cleanup complete!"

clean-results:  ## Clean simulation results
	@echo "Cleaning simulation results..."
	rm -rf $(RESULTS_DIR)/*
	rm -rf $(PLOTS_DIR)/*
	rm -rf $(DATA_DIR)/*
	rm -f *.log
	@echo "Results cleaned!"

# =============================================================================
# LEGACY TARGETS (for backwards compatibility)
# =============================================================================

test-verbose: test  ## Alias for 'make test'

run-simulation: sim  ## Alias for 'make sim'

run-performance:  ## Run performance tests
	$(PYTHON) -m iris.simulations.performance_test

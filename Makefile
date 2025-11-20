# IRIS Economic System - Makefile
# =================================

.PHONY: help install install-dev test test-verbose test-coverage lint format clean docker-build docker-run

help:
	@echo "IRIS Economic System - Available commands:"
	@echo ""
	@echo "  make install         Install the package"
	@echo "  make install-dev     Install with development dependencies"
	@echo "  make test            Run tests"
	@echo "  make test-verbose    Run tests with verbose output"
	@echo "  make test-coverage   Run tests with coverage report"
	@echo "  make lint            Run linting (flake8)"
	@echo "  make format          Format code with black"
	@echo "  make clean           Clean build artifacts"
	@echo "  make docker-build    Build Docker image"
	@echo "  make docker-run      Run Docker container"
	@echo ""

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

test:
	pytest

test-verbose:
	pytest -v

test-coverage:
	pytest --cov=iris --cov-report=html --cov-report=term

lint:
	flake8 iris/

format:
	black iris/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

docker-build:
	docker build -t iris-simulation .

docker-run:
	docker run -it iris-simulation

run-simulation:
	python -m iris.simulations.run_simulation

run-performance:
	python -m iris.simulations.performance_test

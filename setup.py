"""
Setup script for IRIS Economic System Simulation
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = ""
if readme_file.exists():
    long_description = readme_file.read_text(encoding="utf-8")

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    with open(requirements_file) as f:
        requirements = [
            line.strip()
            for line in f
            if line.strip() and not line.startswith("#")
        ]

setup(
    name="iris-economic-system",
    version="2.1.0",
    author="Arnault Nolan",
    author_email="arnaultnolan@gmail.com",
    description="IRIS - Integrative Resilience Intelligence System - Economic Simulation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Nolan-Ar/Iris_Simulation",
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Economics",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-timeout>=2.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "isort>=5.12.0",
        ],
        "notebook": [
            "jupyter>=1.0.0",
            "ipython>=8.0.0",
            "ipykernel>=6.0.0",
            "notebook>=7.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "iris-simulate=iris.simulations.run_simulation:main",
            "iris-performance=iris.simulations.performance_test:main",
        ],
    },
    include_package_data=True,
    package_data={
        "iris": ["*.yaml", "*.yml"],
    },
    zip_safe=False,
)

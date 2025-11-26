#!/usr/bin/env python3
"""
Cellbyte Agentic Data Analyst

An AI-powered data analyst that answers natural language questions about CSV data.

Usage:
    python main.py [CSV_FILES_OR_DIRECTORIES...]

If no paths provided, looks for CSV files in ./data directory.

Examples:
    python main.py data/
    python main.py sales.csv inventory.csv
    python main.py task/case_study_germany_sample.csv task/case_study_germany_treatment_costs_sample.csv
"""
import sys
from pathlib import Path

from src.config import Config
from src.cli import CLI


def main():
    # Validate configuration
    try:
        Config.validate()
    except ValueError as e:
        print(f"Configuration error: {e}")
        sys.exit(1)

    # Initialize CLI
    cli = CLI()

    # Determine data paths
    if len(sys.argv) > 1:
        paths = [Path(p) for p in sys.argv[1:]]
    else:
        # Default to data directory or task directory
        default_paths = [Config.DATA_DIR, Path("task")]
        paths = [p for p in default_paths if p.exists()]
        if not paths:
            print("No data files found. Provide CSV file paths as arguments.")
            print("Usage: python main.py [CSV_FILES_OR_DIRECTORIES...]")
            sys.exit(1)

    # Load data
    print("Loading datasets...")
    cli.load_data(paths)

    if not cli.data_loader.datasets:
        print("No CSV files found in the specified paths.")
        sys.exit(1)

    # Run interactive mode
    cli.run_interactive()


if __name__ == "__main__":
    main()

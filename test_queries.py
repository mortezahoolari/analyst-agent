#!/usr/bin/env python3
"""Test script to verify the agent works with example queries."""
import sys
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from src.config import Config
from src.data_loader import DataLoader
from src.orchestrator import Orchestrator

def test_query(orchestrator: Orchestrator, query: str, query_num: int):
    """Test a single query and print results."""
    print(f"\n{'='*60}")
    print(f"Query {query_num}: {query}")
    print('='*60)

    try:
        response = orchestrator.process(query)

        print("\n--- Steps ---")
        for step in response.steps:
            if step.step_type == "tool_call":
                print(f"Tool: {step.tool_name}")
                print(f"Explanation: {step.content}")
                if step.code:
                    print(f"Code:\n{step.code[:500]}...")
            elif step.step_type == "tool_result":
                output = step.content[:500] if step.content else ""
                print(f"Result: {output}...")

        print("\n--- Answer ---")
        print(response.answer[:1000] if response.answer else "No answer")

        if response.generated_files:
            print(f"\nGenerated files: {response.generated_files}")

        return True
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    # Validate config
    Config.validate()

    # Load data
    print("Loading datasets...")
    data_loader = DataLoader()
    data_loader.load_directory(Path("data"))

    print(f"Loaded datasets: {data_loader.list_datasets()}")
    print(f"\nSchema:\n{data_loader.get_schema_context()[:1000]}...")

    # Create orchestrator
    orchestrator = Orchestrator(data_loader)

    # Test ALL 5 queries from the assignment
    test_queries = [
        "What are the average yearly therapy costs in Non-small cell lung cancer?",
        "Which active substances were also part of the appropriate comparative therapies?",
        "Show me the range of yearly therapy costs by additional benefit rating.",
        "Give me a distribution of additional benefit ratings as a pie chart.",
        "Are there any products that received a higher benefit rating in a reassessment in the same disease area?",
    ]

    results = []
    for i, query in enumerate(test_queries, 1):
        success = test_query(orchestrator, query, i)
        results.append((query, success))

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for query, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status}: {query[:50]}...")

if __name__ == "__main__":
    main()

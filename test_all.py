#!/usr/bin/env python3
"""Comprehensive test suite for the Agentic Data Analyst."""
import sys
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from src.config import Config
from src.data_loader import DataLoader
from src.executor import CodeExecutor
from src.report_generator import ReportGenerator
from src.orchestrator import Orchestrator


def test_config():
    """Test configuration loading."""
    print("\n[TEST] Configuration...")
    try:
        Config.validate()
        print(f"  ✓ API key loaded (length: {len(Config.OPENAI_API_KEY)})")
        print(f"  ✓ Model: {Config.OPENAI_MODEL}")
        print(f"  ✓ Data dir: {Config.DATA_DIR}")
        print(f"  ✓ Output dir: {Config.OUTPUT_DIR}")
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_data_loader():
    """Test CSV loading and schema extraction."""
    print("\n[TEST] Data Loader...")
    try:
        loader = DataLoader()
        loader.load_directory(Path("data"))

        datasets = loader.list_datasets()
        print(f"  ✓ Loaded {len(datasets)} datasets: {datasets}")

        for name, info in loader.dataset_info.items():
            print(f"  ✓ {name}: {info.row_count} rows, {len(info.columns)} columns")

        schema = loader.get_schema_context()
        print(f"  ✓ Schema context generated ({len(schema)} chars)")
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_executor():
    """Test code execution sandbox."""
    print("\n[TEST] Code Executor...")
    try:
        loader = DataLoader()
        loader.load_directory(Path("data"))
        executor = CodeExecutor(loader.datasets)

        # Test simple code
        result = executor.execute("result = 2 + 2")
        assert result.success, f"Simple math failed: {result.error}"
        print("  ✓ Simple code execution works")

        # Test pandas access
        result = executor.execute("result = case_study_germany_sample.shape[0]")
        assert result.success, f"Pandas access failed: {result.error}"
        print(f"  ✓ DataFrame access works (rows: {result.result_value})")

        # Test figure saving
        result = executor.execute("""
import matplotlib.pyplot as plt
plt.figure()
plt.plot([1,2,3], [1,2,3])
plt.title('Test')
save_figure('test_chart.png')
""")
        assert result.success, f"Chart generation failed: {result.error}"
        assert len(result.generated_files) > 0, "No file generated"
        print(f"  ✓ Chart generation works: {result.generated_files[0]}")

        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_report_generator():
    """Test PDF and DOCX report generation."""
    print("\n[TEST] Report Generator...")
    try:
        generator = ReportGenerator(Config.OUTPUT_DIR)

        test_content = """## Summary
This is a test report.

## Key Findings
- Finding 1: Test data works
- Finding 2: Reports generate correctly
- Finding 3: Both formats supported

## Conclusion
The report generator is working properly.
"""

        # Test PDF
        pdf_path = generator.generate_pdf("Test Report", test_content, "test_report")
        assert pdf_path.exists(), "PDF not created"
        print(f"  ✓ PDF generated: {pdf_path} ({pdf_path.stat().st_size} bytes)")

        # Test DOCX
        docx_path = generator.generate_docx("Test Report", test_content, "test_report")
        assert docx_path.exists(), "DOCX not created"
        print(f"  ✓ DOCX generated: {docx_path} ({docx_path.stat().st_size} bytes)")

        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_orchestrator_simple():
    """Test orchestrator with a simple query (no LLM call)."""
    print("\n[TEST] Orchestrator initialization...")
    try:
        loader = DataLoader()
        loader.load_directory(Path("data"))
        orchestrator = Orchestrator(loader)

        print("  ✓ Orchestrator initialized")
        print(f"  ✓ Model: {orchestrator.model}")
        print(f"  ✓ History length: {len(orchestrator.history)}")
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_orchestrator_query():
    """Test orchestrator with a real LLM query."""
    print("\n[TEST] Orchestrator with LLM query...")
    try:
        loader = DataLoader()
        loader.load_directory(Path("data"))
        orchestrator = Orchestrator(loader)

        # Simple query
        response = orchestrator.process("What is the total number of rows in the germany sample dataset?")

        print("  ✓ Query processed")
        print(f"  ✓ Steps: {len(response.steps)}")
        print(f"  ✓ Answer length: {len(response.answer)} chars")
        print(f"  ✓ Generated files: {len(response.generated_files)}")

        # Check answer mentions 100 rows
        if "100" in response.answer:
            print("  ✓ Answer appears correct (mentions 100 rows)")

        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_report_via_orchestrator():
    """Test report generation through the orchestrator."""
    print("\n[TEST] Report generation via orchestrator...")
    try:
        loader = DataLoader()
        loader.load_directory(Path("data"))
        orchestrator = Orchestrator(loader)

        response = orchestrator.process(
            "Generate a brief PDF report summarizing the number of products by additional benefit rating."
        )

        print("  ✓ Query processed")
        print(f"  ✓ Steps: {len(response.steps)}")

        # Check if any PDF was generated
        pdf_files = [f for f in response.generated_files if str(f).endswith('.pdf')]
        if pdf_files:
            print(f"  ✓ PDF generated: {pdf_files[0]}")
        else:
            print(f"  ⚠ No PDF in generated files: {response.generated_files}")

        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("=" * 60)
    print("COMPREHENSIVE TEST SUITE")
    print("=" * 60)

    results = []

    # Unit tests (no LLM)
    results.append(("Config", test_config()))
    results.append(("Data Loader", test_data_loader()))
    results.append(("Code Executor", test_executor()))
    results.append(("Report Generator", test_report_generator()))
    results.append(("Orchestrator Init", test_orchestrator_simple()))

    # Integration tests (with LLM)
    print("\n" + "-" * 60)
    print("INTEGRATION TESTS (requires API)")
    print("-" * 60)

    results.append(("Orchestrator Query", test_orchestrator_query()))
    results.append(("Report via Orchestrator", test_report_via_orchestrator()))

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

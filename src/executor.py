"""Python code execution with namespace isolation for data analysis.

NOTE: This is NOT true sandboxing. Generated code can still import
arbitrary modules and access system resources. For production use,
implement subprocess isolation with resource limits.
"""
import sys
import traceback
from io import StringIO
from typing import Any, Optional
from dataclasses import dataclass
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from pathlib import Path

from .config import Config


@dataclass
class ExecutionResult:
    """Result of code execution."""
    success: bool
    output: str
    error: Optional[str] = None
    result_value: Any = None
    generated_files: list[Path] = None

    def __post_init__(self):
        if self.generated_files is None:
            self.generated_files = []


class CodeExecutor:
    """Executes Python code in a controlled environment."""

    def __init__(self, datasets: dict[str, pd.DataFrame]):
        self.datasets = datasets
        self.output_dir = Config.OUTPUT_DIR
        self.last_result = None

    def execute(self, code: str) -> ExecutionResult:
        """
        Execute Python code with access to loaded datasets.

        The code has access to:
        - All loaded DataFrames by their dataset names
        - pandas as 'pd'
        - matplotlib.pyplot as 'plt'
        - A 'save_figure(filename)' helper function
        - A 'save_dataframe(df, filename)' helper function
        """
        # Capture stdout
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()

        generated_files = []

        # Helper functions for saving outputs
        def save_figure(filename: str) -> Path:
            """Save the current matplotlib figure."""
            filepath = self.output_dir / filename
            plt.savefig(filepath, dpi=150, bbox_inches='tight')
            plt.close()
            generated_files.append(filepath)
            return filepath

        def save_dataframe(df: pd.DataFrame, filename: str) -> Path:
            """Save a DataFrame to file (CSV or Excel based on extension)."""
            filepath = self.output_dir / filename
            if filename.endswith('.xlsx'):
                df.to_excel(filepath, index=False)
            else:
                df.to_csv(filepath, index=False)
            generated_files.append(filepath)
            return filepath

        # Build execution namespace
        namespace = {
            'pd': pd,
            'plt': plt,
            'save_figure': save_figure,
            'save_dataframe': save_dataframe,
            **self.datasets  # Add all datasets by name
        }

        try:
            # Execute the code
            exec(code, namespace)

            # Capture any result variable if set
            result_value = namespace.get('result', None)
            self.last_result = result_value

            output = captured_output.getvalue()

            # If result is a DataFrame, add its string representation
            if isinstance(result_value, pd.DataFrame):
                if len(result_value) > Config.MAX_OUTPUT_ROWS:
                    output += f"\n[Showing first {Config.MAX_OUTPUT_ROWS} of {len(result_value)} rows]\n"
                    output += result_value.head(Config.MAX_OUTPUT_ROWS).to_string()
                else:
                    output += "\n" + result_value.to_string()
            elif result_value is not None:
                output += f"\nResult: {result_value}"

            return ExecutionResult(
                success=True,
                output=output.strip(),
                result_value=result_value,
                generated_files=generated_files
            )

        except Exception:
            error_msg = traceback.format_exc()
            return ExecutionResult(
                success=False,
                output=captured_output.getvalue(),
                error=error_msg,
                generated_files=generated_files
            )
        finally:
            sys.stdout = old_stdout
            plt.close('all')  # Clean up any open figures

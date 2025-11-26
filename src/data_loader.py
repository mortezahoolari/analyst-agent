"""Data loading and schema extraction for CSV files."""
import pandas as pd
from pathlib import Path
from typing import Optional
from dataclasses import dataclass


@dataclass
class ColumnInfo:
    """Information about a DataFrame column."""
    name: str
    dtype: str
    non_null_count: int
    sample_values: list
    unique_count: int


@dataclass
class DatasetInfo:
    """Information about a loaded dataset."""
    name: str
    path: Path
    row_count: int
    columns: list[ColumnInfo]

    def to_schema_string(self) -> str:
        """Generate a human-readable schema description."""
        lines = [f"Dataset: {self.name}"]
        lines.append(f"Rows: {self.row_count}")
        lines.append("Columns:")
        for col in self.columns:
            sample_str = ", ".join(str(v) for v in col.sample_values[:3])
            lines.append(f"  - {col.name} ({col.dtype}): {col.unique_count} unique values. Examples: {sample_str}")
        return "\n".join(lines)


class DataLoader:
    """Loads and manages CSV datasets."""

    def __init__(self):
        self.datasets: dict[str, pd.DataFrame] = {}
        self.dataset_info: dict[str, DatasetInfo] = {}

    def load_csv(self, path: Path, name: Optional[str] = None) -> DatasetInfo:
        """Load a CSV file and extract its schema."""
        name = name or path.stem

        # Try different separators
        for sep in [",", ";", "\t"]:
            try:
                df = pd.read_csv(path, sep=sep)
                if len(df.columns) > 1:
                    break
            except Exception:
                continue

        self.datasets[name] = df

        # Extract column information
        columns = []
        for col in df.columns:
            col_info = ColumnInfo(
                name=col,
                dtype=str(df[col].dtype),
                non_null_count=df[col].notna().sum(),
                sample_values=df[col].dropna().unique()[:5].tolist(),
                unique_count=df[col].nunique()
            )
            columns.append(col_info)

        info = DatasetInfo(
            name=name,
            path=path,
            row_count=len(df),
            columns=columns
        )
        self.dataset_info[name] = info
        return info

    def load_directory(self, directory: Path) -> list[DatasetInfo]:
        """Load all CSV files from a directory."""
        loaded = []
        for csv_file in directory.glob("*.csv"):
            info = self.load_csv(csv_file)
            loaded.append(info)
        return loaded

    def get_schema_context(self) -> str:
        """Get schema context for all loaded datasets."""
        if not self.dataset_info:
            return "No datasets loaded."

        schemas = []
        for info in self.dataset_info.values():
            schemas.append(info.to_schema_string())
        return "\n\n".join(schemas)

    def get_dataframe(self, name: str) -> Optional[pd.DataFrame]:
        """Get a loaded DataFrame by name."""
        return self.datasets.get(name)

    def list_datasets(self) -> list[str]:
        """List all loaded dataset names."""
        return list(self.datasets.keys())

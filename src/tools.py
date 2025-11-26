"""Tool definitions for the LLM agent."""

# OpenAI tool definitions for the Responses API
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "analyze_data",
            "description": "Execute Python code to analyze the loaded CSV datasets. Use pandas for data manipulation. The code has access to all loaded DataFrames by their names (e.g., 'case_study_germany_sample', 'case_study_germany_treatment_costs_sample'). Assign the final result to a variable called 'result' to display it.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Python code using pandas to analyze the data. Available: pd (pandas), plt (matplotlib), all dataset DataFrames by name. Assign output to 'result' variable."
                    },
                    "explanation": {
                        "type": "string",
                        "description": "Brief explanation of what this analysis does, for user transparency."
                    }
                },
                "required": ["code", "explanation"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_chart",
            "description": "Generate a visualization/chart from the data using matplotlib. The chart will be saved as a PNG file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Python code using matplotlib (plt) to create a chart. Use save_figure('filename.png') to save. Available: pd, plt, all dataset DataFrames, save_figure()."
                    },
                    "explanation": {
                        "type": "string",
                        "description": "Brief explanation of what this visualization shows."
                    },
                    "filename": {
                        "type": "string",
                        "description": "Output filename for the chart (e.g., 'benefit_distribution.png')"
                    }
                },
                "required": ["code", "explanation", "filename"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "export_data",
            "description": "Export analysis results or data to a file (CSV, Excel, or other formats).",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Python code to prepare and export data. Use save_dataframe(df, 'filename.csv') or save_dataframe(df, 'filename.xlsx') to save."
                    },
                    "explanation": {
                        "type": "string",
                        "description": "Brief explanation of what data is being exported."
                    },
                    "filename": {
                        "type": "string",
                        "description": "Output filename (e.g., 'results.csv' or 'report.xlsx')"
                    }
                },
                "required": ["code", "explanation", "filename"]
            }
        }
    }
]


def get_system_prompt(schema_context: str, dataset_names: list[str]) -> str:
    """Generate the system prompt with dataset context."""
    datasets_str = ", ".join(f"'{name}'" for name in dataset_names)

    return f"""You are an expert data analyst assistant. You help users analyze tabular data through natural language.

## Available Datasets
{schema_context}

## Your Capabilities
1. **analyze_data**: Run pandas code to answer questions, compute statistics, filter/aggregate data
2. **create_chart**: Generate visualizations using matplotlib (pie charts, bar charts, line plots, etc.)
3. **export_data**: Save results to CSV or Excel files

## Important Guidelines
- ALWAYS use the tools to perform analysis - don't just describe what you would do
- The DataFrames are available directly by name: {datasets_str}
- For analysis, assign the final result to a variable called 'result'
- Be transparent: explain what your code does in the 'explanation' field
- Handle missing/null values appropriately
- When joining datasets, identify common columns (e.g., brand_name, active_substance)

## Code Examples
```python
# Filter data
result = case_study_germany_sample[case_study_germany_sample['disease_area'] == 'Some Disease']

# Aggregation
result = df.groupby('column')['value'].mean()

# Joining datasets
merged = pd.merge(df1, df2, on='common_column', how='inner')
result = merged.groupby('category')['price'].agg(['min', 'max', 'mean'])
```

## Response Style
- First, briefly acknowledge the user's question
- Then use the appropriate tool(s) to perform the analysis
- After getting results, provide insights and interpretation
- If the user asks for a chart or export, use the appropriate tool
"""

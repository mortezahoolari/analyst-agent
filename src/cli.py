"""
Command-line interface for the Agentic Data Analyst.
Provides a rich, interactive chat experience with transparent step display.
"""
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich.table import Table

from .orchestrator import Orchestrator, AgentResponse, AgentStep
from .data_loader import DataLoader
from .config import Config


class CLI:
    """Interactive CLI for the data analyst agent."""

    def __init__(self):
        self.console = Console()
        self.data_loader = DataLoader()
        self.orchestrator: Orchestrator = None

    def display_welcome(self) -> None:
        """Display welcome message and loaded datasets."""
        self.console.print(Panel.fit(
            "[bold blue]Cellbyte Agentic Data Analyst[/bold blue]\n"
            "Ask questions about your data in natural language.",
            border_style="blue"
        ))

    def display_datasets(self) -> None:
        """Display information about loaded datasets."""
        if not self.data_loader.dataset_info:
            self.console.print("[yellow]No datasets loaded.[/yellow]")
            return

        table = Table(title="Loaded Datasets")
        table.add_column("Name", style="cyan")
        table.add_column("Rows", justify="right")
        table.add_column("Columns", justify="right")

        for name, info in self.data_loader.dataset_info.items():
            table.add_row(name, str(info.row_count), str(len(info.columns)))

        self.console.print(table)
        self.console.print()

    def display_step(self, step: AgentStep) -> None:
        """Display a single agent step with appropriate formatting."""
        if step.step_type == "thinking":
            if step.content:
                self.console.print(f"[dim italic]{step.content}[/dim italic]")

        elif step.step_type == "tool_call":
            self.console.print(f"\n[bold yellow]> {step.tool_name}[/bold yellow]")
            if step.content:
                self.console.print(f"[dim]{step.content}[/dim]")
            if step.code:
                syntax = Syntax(step.code, "python", theme="monokai", line_numbers=True)
                self.console.print(Panel(syntax, title="Generated Code", border_style="yellow"))

        elif step.step_type == "tool_result":
            if step.files:
                for f in step.files:
                    self.console.print(f"[green]Created file: {f}[/green]")
            if step.content and "Error" in step.content:
                self.console.print(Panel(step.content, title="Error", border_style="red"))
            elif step.content:
                # Truncate very long outputs
                content = step.content
                if len(content) > 2000:
                    content = content[:2000] + "\n... (output truncated)"
                self.console.print(Panel(content, title="Result", border_style="green"))

        elif step.step_type == "response":
            pass  # Will be displayed as final answer

    def display_response(self, response: AgentResponse) -> None:
        """Display the full agent response with all steps."""
        self.console.print("\n[bold]Agent Steps:[/bold]")

        for step in response.steps:
            self.display_step(step)

        # Display final answer
        self.console.print("\n")
        self.console.print(Panel(
            Markdown(response.answer),
            title="[bold green]Answer[/bold green]",
            border_style="green"
        ))

        if response.generated_files:
            self.console.print("\n[bold]Generated Files:[/bold]")
            for f in response.generated_files:
                self.console.print(f"  - {f}")

    def load_data(self, paths: list[Path]) -> None:
        """Load CSV files from provided paths."""
        for path in paths:
            if path.is_dir():
                self.data_loader.load_directory(path)
            elif path.suffix.lower() == '.csv':
                self.data_loader.load_csv(path)
            else:
                self.console.print(f"[yellow]Skipping non-CSV file: {path}[/yellow]")

        self.orchestrator = Orchestrator(self.data_loader)

    def run_interactive(self) -> None:
        """Run the interactive chat loop."""
        self.display_welcome()
        self.display_datasets()

        self.console.print("[dim]Commands: 'quit' to exit, 'clear' to reset history, 'schema' to show data schema[/dim]\n")

        while True:
            try:
                user_input = self.console.input("[bold blue]You:[/bold blue] ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ('quit', 'exit', 'q'):
                    self.console.print("[dim]Goodbye![/dim]")
                    break

                if user_input.lower() == 'clear':
                    self.orchestrator.clear_history()
                    self.console.print("[dim]Conversation history cleared.[/dim]")
                    continue

                if user_input.lower() == 'schema':
                    self.console.print(self.data_loader.get_schema_context())
                    continue

                # Process the query
                with self.console.status("[bold green]Analyzing...[/bold green]"):
                    response = self.orchestrator.process(user_input)

                self.display_response(response)
                self.console.print()

            except KeyboardInterrupt:
                self.console.print("\n[dim]Use 'quit' to exit.[/dim]")
            except Exception as e:
                self.console.print(f"[red]Error: {e}[/red]")

    def run_single_query(self, query: str) -> AgentResponse:
        """Run a single query and return the response."""
        return self.orchestrator.process(query)

"""
Custom orchestrator for the agentic data analyst.
Uses OpenAI Chat Completions API with function calling.
"""
import json
from typing import Optional
from dataclasses import dataclass, field
from openai import OpenAI

from .config import Config
from .data_loader import DataLoader
from .executor import CodeExecutor, ExecutionResult
from .tools import TOOLS, get_system_prompt
from .report_generator import ReportGenerator


@dataclass
class Message:
    """A message in the conversation history."""
    role: str  # 'user', 'assistant', 'tool'
    content: str
    tool_call_id: Optional[str] = None
    tool_calls: Optional[list] = None


@dataclass
class AgentStep:
    """A single step in the agent's reasoning process."""
    step_type: str  # 'thinking', 'tool_call', 'tool_result', 'response'
    content: str
    tool_name: Optional[str] = None
    code: Optional[str] = None
    files: list = field(default_factory=list)


@dataclass
class AgentResponse:
    """Complete response from the agent including all steps."""
    answer: str
    steps: list[AgentStep]
    generated_files: list


class Orchestrator:
    """
    The main agent orchestrator.

    Implements a simple agent loop:
    1. Send user query + context to LLM
    2. If LLM returns tool calls, execute them
    3. Send tool results back to LLM
    4. Repeat until LLM gives final response
    """

    def __init__(self, data_loader: DataLoader):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.data_loader = data_loader
        self.executor = CodeExecutor(data_loader.datasets)
        self.report_generator = ReportGenerator(Config.OUTPUT_DIR)
        self.history: list[Message] = []
        self.model = Config.OPENAI_MODEL

    def _build_messages(self, user_input: str) -> list[dict]:
        """Build the messages array for the API call."""
        # System prompt with dataset context
        system_prompt = get_system_prompt(
            self.data_loader.get_schema_context(),
            self.data_loader.list_datasets()
        )

        messages = [{"role": "system", "content": system_prompt}]

        # Add conversation history (limited to last N exchanges)
        history_to_include = self.history[-(Config.HISTORY_LENGTH * 2):]
        for msg in history_to_include:
            msg_dict = {"role": msg.role, "content": msg.content}
            if msg.tool_call_id:
                msg_dict["tool_call_id"] = msg.tool_call_id
            if msg.tool_calls:
                msg_dict["tool_calls"] = msg.tool_calls
            messages.append(msg_dict)

        # Add current user input
        messages.append({"role": "user", "content": user_input})

        return messages

    def _execute_tool(self, tool_name: str, arguments: dict) -> tuple[ExecutionResult, str]:
        """Execute a tool and return the result."""
        # Handle report generation separately
        if tool_name == "generate_report":
            return self._execute_report_tool(arguments)

        # For code-based tools (analyze_data, create_chart, export_data)
        code = arguments.get("code", "")
        explanation = arguments.get("explanation", "")

        result = self.executor.execute(code)

        if result.success:
            output = f"Explanation: {explanation}\n\n"
            if result.output:
                output += f"Output:\n{result.output}"
            if result.generated_files:
                output += f"\n\nGenerated files: {[str(f) for f in result.generated_files]}"
        else:
            output = f"Error executing code:\n{result.error}"

        return result, output

    def _execute_report_tool(self, arguments: dict) -> tuple[ExecutionResult, str]:
        """Execute the report generation tool."""
        try:
            title = arguments.get("title", "Report")
            content = arguments.get("content", "")
            format = arguments.get("format", "pdf")
            filename = arguments.get("filename", "report")

            filepath = self.report_generator.generate(title, content, format, filename)

            return ExecutionResult(
                success=True,
                output=f"Report generated successfully: {filepath}",
                generated_files=[filepath]
            ), f"Report generated: {filepath}"

        except Exception as e:
            return ExecutionResult(
                success=False,
                output="",
                error=str(e)
            ), f"Error generating report: {e}"

    def process(self, user_input: str) -> AgentResponse:
        """
        Process a user query through the agent loop.

        Returns an AgentResponse with the final answer and all intermediate steps.
        """
        steps: list[AgentStep] = []
        all_generated_files = []

        # Build initial messages
        messages = self._build_messages(user_input)

        # Add user message to history
        self.history.append(Message(role="user", content=user_input))

        # Agent loop - keep going until we get a final response
        max_iterations = 10  # Safety limit to prevent infinite loops
        iteration = 0

        while iteration < max_iterations:
            iteration += 1

            # Call the LLM
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto"
            )

            assistant_message = response.choices[0].message

            # Check if the model wants to call tools
            if assistant_message.tool_calls:
                # Record the assistant's tool call decision
                steps.append(AgentStep(
                    step_type="thinking",
                    content=assistant_message.content or "Analyzing the request..."
                ))

                # Add assistant message to conversation
                messages.append({
                    "role": "assistant",
                    "content": assistant_message.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in assistant_message.tool_calls
                    ]
                })

                # Execute each tool call
                for tool_call in assistant_message.tool_calls:
                    tool_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)

                    # Record the tool call step
                    steps.append(AgentStep(
                        step_type="tool_call",
                        content=arguments.get("explanation", ""),
                        tool_name=tool_name,
                        code=arguments.get("code", "")
                    ))

                    # Execute the tool
                    exec_result, output = self._execute_tool(tool_name, arguments)

                    # Track generated files
                    all_generated_files.extend(exec_result.generated_files)

                    # Record the tool result step
                    steps.append(AgentStep(
                        step_type="tool_result",
                        content=output,
                        tool_name=tool_name,
                        files=[str(f) for f in exec_result.generated_files]
                    ))

                    # Add tool result to messages
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": output
                    })

            else:
                # No tool calls - this is the final response
                final_answer = assistant_message.content or ""

                steps.append(AgentStep(
                    step_type="response",
                    content=final_answer
                ))

                # Add to history
                self.history.append(Message(role="assistant", content=final_answer))

                return AgentResponse(
                    answer=final_answer,
                    steps=steps,
                    generated_files=all_generated_files
                )

        # If we hit max iterations, return what we have
        return AgentResponse(
            answer="Analysis completed (max iterations reached).",
            steps=steps,
            generated_files=all_generated_files
        )

    def clear_history(self) -> None:
        """Clear the conversation history."""
        self.history = []

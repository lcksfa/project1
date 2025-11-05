"""Math Agent - Enterprise Python Implementation

A LangChain-based AI agent that performs mathematical operations
using streaming responses for better user experience.
"""

from __future__ import annotations

import logging
import os
import sys
import time
from dataclasses import dataclass
from typing import Final

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.tools import tool

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
_ = load_dotenv()


@dataclass
class LLMConfig:
    """Configuration for LLM initialization."""
    temperature: float = 0.0
    model: str = "deepseek-chat"
    base_url: str = "https://api.deepseek.com"
    api_key_env_var: str = "DEEPSEEK_API_KEY"

    # Constants
    STREAM_DELAY: Final[float] = 0.01


class LLMError(Exception):
    """Custom exception for LLM-related errors."""
    pass


class MathAgentError(Exception):
    """Custom exception for math agent operations."""
    pass


def create_llm(config: LLMConfig) -> ChatOpenAI:
    """
    Create and configure a ChatOpenAI instance.

    Args:
        config: LLM configuration object

    Returns:
        Configured ChatOpenAI instance

    Raises:
        LLMError: If API key is not configured
    """
    api_key = os.getenv(config.api_key_env_var)
    if not api_key:
        raise LLMError(
            f"{config.api_key_env_var} environment variable is not set"
        )

    return ChatOpenAI(
        temperature=config.temperature,
        model=config.model,
        base_url=config.base_url,
        api_key=lambda: api_key
    )


@tool
def add_numbers(first_number: int, second_number: int) -> int:
    """
    Add two numbers together.

    Args:
        first_number: The first operand
        second_number: The second operand

    Returns:
        The sum of the two numbers
    """
    return first_number + second_number


@tool
def subtract_numbers(first_number: int, second_number: int) -> int:
    """
    Subtract the second number from the first.

    Args:
        first_number: The minuend
        second_number: The subtrahend

    Returns:
        The result of the subtraction
    """
    return first_number - second_number


def create_math_agent(llm: ChatOpenAI) -> object:
    """
    Create a math-enabled agent with the specified LLM.

    Args:
        llm: The language model to use

    Returns:
        Configured agent instance
    """
    tools = [add_numbers, subtract_numbers]
    return create_agent(
        model=llm,
        tools=tools
    )


class StreamingResponseHandler:
    """Handles streaming response output for the agent."""

    def __init__(self, stream_delay: float = 0.01):
        """
        Initialize the response handler.

        Args:
            stream_delay: Delay between characters for streaming effect
        """
        self.stream_delay = stream_delay

    def display_streaming_response(self, agent_stream) -> str:
        """
        Display agent response with streaming effect.

        Args:
            agent_stream: The agent's stream response

        Returns:
            The complete response content
        """
        response_content = ""

        for chunk in agent_stream:
            if self._should_process_chunk(chunk):
                chunk_content = self._extract_message_content(chunk)
                if chunk_content:
                    response_content += chunk_content
                    self._display_content_char_by_char(chunk_content)

        return response_content

    def _should_process_chunk(self, chunk: dict) -> bool:
        """Check if the chunk contains model messages."""
        return "model" in chunk and "messages" in chunk["model"]

    def _extract_message_content(self, chunk: dict) -> str:
        """Extract AI message content from chunk."""
        messages = chunk["model"]["messages"]
        for message in messages:
            if (
                hasattr(message, "content")
                and message.content
                and isinstance(message, AIMessage)
            ):
                return str(message.content)
        return ""

    def _display_content_char_by_char(self, content: str) -> None:
        """Display content character by character with delay."""
        for char in content:
            print(char, end="", flush=True)
            time.sleep(self.stream_delay)


class MathAgentApp:
    """Main application class for the Math Agent."""

    def __init__(self, config: LLMConfig| None = None):
        """
        Initialize the Math Agent application.

        Args:
            config: Optional LLM configuration
        """
        self.config = config or LLMConfig()
        self.llm = None
        self.agent = None
        self.response_handler = StreamingResponseHandler(
            stream_delay=self.config.STREAM_DELAY
        )

    def initialize(self) -> None:
        """Initialize LLM and agent components."""
        try:
            self.llm = create_llm(self.config)
            self.agent = create_math_agent(self.llm)
            logger.info("Math Agent initialized successfully")
        except LLMError as error:
            logger.error(f"LLM initialization failed: {error}")
            raise

    def run_interactive_loop(self) -> None:
        """Run the main interactive agent loop."""
        self._display_welcome_message()

        while True:
            try:
                user_input = self._get_user_input()
                if self._should_exit(user_input):
                    self._display_exit_message()
                    break

                if not user_input:
                    self._display_input_error()
                    continue

                self._process_user_query(user_input)

            except KeyboardInterrupt:
                self._handle_keyboard_interrupt()
                break
            except MathAgentError as error:
                self._handle_agent_error(error)
            except Exception as error:
                self._handle_unexpected_error(error)

    def _display_welcome_message(self) -> None:
        """Display welcome message to the user."""
        print("Welcome to the Math Agent!")
        print("Math Agent is ready. You can ask it to add or subtract numbers.")
        print("Type 'exit' or 'quit' to end the session.")

    def _get_user_input(self) -> str:
        """Get and validate user input."""
        return input("\nYou: ").strip()

    def _should_exit(self, user_input: str) -> bool:
        """Check if user wants to exit."""
        return user_input.lower() in {"exit", "quit"}

    def _display_exit_message(self) -> None:
        """Display exit message."""
        print("Exiting Math Agent. Goodbye!")

    def _display_input_error(self) -> None:
        """Display input validation error."""
        print("Please enter a valid input.")

    def _process_user_query(self, user_input: str) -> None:
        """Process user query and display response."""
        print("\nMath Agent: ", end="", flush=True)

        try:
            agent_stream = self.agent.stream(
                {"messages": [HumanMessage(content=user_input)]}
            )
            self.response_handler.display_streaming_response(agent_stream)
            print()  # Add newline after response

        except Exception as error:
            raise MathAgentError(f"Failed to process query: {error}") from error

    def _handle_keyboard_interrupt(self) -> None:
        """Handle Ctrl+C interrupt."""
        print("\n\nExiting Math Agent. Goodbye!")
        logger.info("Application interrupted by user")

    def _handle_agent_error(self, error: MathAgentError) -> None:
        """Handle Math Agent specific errors."""
        print(f"\nAgent Error: {error}. Please try again.")
        logger.warning(f"Agent error: {error}")

    def _handle_unexpected_error(self, error: Exception) -> None:
        """Handle unexpected errors."""
        print("\nUnexpected error occurred. Please try again.")
        logger.error(f"Unexpected error: {error}", exc_info=True)


def main() -> None:
    """Main application entry point."""
    try:
        app = MathAgentApp()
        app.initialize()
        app.run_interactive_loop()

    except LLMError as error:
        print(f"Configuration error: {error}")
        logger.error(f"Configuration error: {error}")
        sys.exit(1)

    except KeyboardInterrupt:
        print("\nApplication interrupted by user.")
        logger.info("Application interrupted by user")
        sys.exit(0)

    except Exception as error:
        print(f"Unexpected error: {error}")
        logger.error(f"Unexpected error in main: {error}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
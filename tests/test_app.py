"""Unit tests for application components."""

import os
import pytest
from unittest.mock import Mock, patch, ANY

from main import (
    LLMConfig,
    LLMError,
    MathAgentError,
    create_llm,
    create_math_agent,
    StreamingResponseHandler,
    MathAgentApp
)


class TestLLMConfig:
    """Test cases for LLMConfig class."""

    def test_default_config_values(self):
        """Test default configuration values."""
        config = LLMConfig()
        assert config.temperature == 0.0
        assert config.model == "deepseek-chat"
        assert config.base_url == "https://api.deepseek.com"
        assert config.api_key_env_var == "DEEPSEEK_API_KEY"
        assert config.STREAM_DELAY == 0.01

    def test_custom_config_values(self):
        """Test custom configuration values."""
        config = LLMConfig(
            temperature=0.5,
            model="gpt-4",
            base_url="https://api.openai.com",
            api_key_env_var="OPENAI_API_KEY"
        )
        assert config.temperature == 0.5
        assert config.model == "gpt-4"
        assert config.base_url == "https://api.openai.com"
        assert config.api_key_env_var == "OPENAI_API_KEY"
        assert config.STREAM_DELAY == 0.01  # Constant should remain unchanged


class TestCreateLLM:
    """Test cases for create_llm function."""

    def test_create_llm_success(self):
        """Test successful LLM creation with valid API key."""
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-api-key"}):
            with patch("main.ChatOpenAI") as mock_chat_openai:
                mock_instance = Mock()
                mock_chat_openai.return_value = mock_instance

                config = LLMConfig()
                result = create_llm(config)

                mock_chat_openai.assert_called_once_with(
                    temperature=0.0,
                    model="deepseek-chat",
                    base_url="https://api.deepseek.com",
                    api_key=ANY  # lambda function
                )
                assert result == mock_instance

    def test_create_llm_missing_api_key(self):
        """Test LLM creation fails when API key is missing."""
        with patch.dict(os.environ, {}, clear=False):
            if "DEEPSEEK_API_KEY" in os.environ:
                del os.environ["DEEPSEEK_API_KEY"]

            config = LLMConfig()
            with pytest.raises(LLMError, match="DEEPSEEK_API_KEY environment variable is not set"):
                create_llm(config)


class TestCreateMathAgent:
    """Test cases for create_math_agent function."""

    def test_create_math_agent_success(self):
        """Test successful math agent creation."""
        mock_llm = Mock()
        with patch("main.create_agent") as mock_create_agent:
            mock_agent = Mock()
            mock_create_agent.return_value = mock_agent

            result = create_math_agent(mock_llm)

            mock_create_agent.assert_called_once()
            assert result == mock_agent


class TestStreamingResponseHandler:
    """Test cases for StreamingResponseHandler class."""

    def test_handler_initialization(self):
        """Test handler initialization with default and custom delays."""
        handler_default = StreamingResponseHandler()
        assert handler_default.stream_delay == 0.01

        handler_custom = StreamingResponseHandler(stream_delay=0.05)
        assert handler_custom.stream_delay == 0.05

    def test_should_process_chunk(self):
        """Test chunk processing logic."""
        handler = StreamingResponseHandler()

        # Valid chunk
        valid_chunk = {"model": {"messages": []}}
        assert handler._should_process_chunk(valid_chunk) is True

        # Invalid chunks
        assert handler._should_process_chunk({"other": "data"}) is False
        assert handler._should_process_chunk({"model": {}}) is False
        assert handler._should_process_chunk({}) is False


class TestMathAgentApp:
    """Test cases for MathAgentApp class."""

    def test_app_initialization_with_default_config(self):
        """Test app initialization with default configuration."""
        app = MathAgentApp()
        assert isinstance(app.config, LLMConfig)
        assert app.config.model == "deepseek-chat"
        assert app.llm is None
        assert app.agent is None
        assert isinstance(app.response_handler, StreamingResponseHandler)

    def test_app_initialization_with_custom_config(self):
        """Test app initialization with custom configuration."""
        custom_config = LLMConfig(model="gpt-4")
        app = MathAgentApp(config=custom_config)
        assert app.config == custom_config
        assert app.config.model == "gpt-4"

    @patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-key"})
    def test_app_initialize_success(self):
        """Test successful app initialization."""
        with patch("main.create_llm") as mock_create_llm:
            with patch("main.create_math_agent") as mock_create_agent:
                mock_llm = Mock()
                mock_agent = Mock()
                mock_create_llm.return_value = mock_llm
                mock_create_agent.return_value = mock_agent

                app = MathAgentApp()
                app.initialize()

                assert app.llm == mock_llm
                assert app.agent == mock_agent
                mock_create_llm.assert_called_once_with(app.config)
                mock_create_agent.assert_called_once_with(mock_llm)

    def test_app_initialize_failure(self):
        """Test app initialization failure."""
        with patch.dict(os.environ, {}, clear=False):
            if "DEEPSEEK_API_KEY" in os.environ:
                del os.environ["DEEPSEEK_API_KEY"]

            app = MathAgentApp()
            with pytest.raises(LLMError):
                app.initialize()

    @pytest.mark.parametrize(
        "user_input, expected",
        [
            ("exit", True),
            ("quit", True),
            ("EXIT", True),
            ("Quit", True),
            ("no", False),
            ("continue", False),
            ("", False),
        ]
    )
    def test_should_exit(self, user_input, expected):
        """Test exit condition checking."""
        app = MathAgentApp()
        result = app._should_exit(user_input)
        assert result == expected

    @patch("builtins.print")
    def test_handle_keyboard_interrupt(self, mock_print):
        """Test keyboard interrupt handling."""
        app = MathAgentApp()
        with patch("main.logger") as mock_logger:
            app._handle_keyboard_interrupt()
            mock_print.assert_called_with("\n\nExiting Math Agent. Goodbye!")
            mock_logger.info.assert_called_with("Application interrupted by user")

    @patch("builtins.print")
    def test_handle_agent_error(self, mock_print):
        """Test agent error handling."""
        app = MathAgentApp()
        test_error = MathAgentError("Test error")
        with patch("main.logger") as mock_logger:
            app._handle_agent_error(test_error)
            mock_print.assert_called_with("\nAgent Error: Test error. Please try again.")
            mock_logger.warning.assert_called_with("Agent error: Test error")
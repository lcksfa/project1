# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based Math Agent project that uses LangChain, LangGraph, and OpenAI-compatible APIs to create an interactive AI agent capable of performing mathematical operations. The agent uses tools for addition and subtraction and communicates via streaming responses.

## Development Commands

### Running the Application
```bash
uv run  main.py
```

### Managing Dependencies (using uv)
```bash
# Install dependencies
uv sync

# Add new dependencies
uv add package_name

# Update dependencies
uv sync --upgrade
```

### Environment Setup
- Copy `.env` file and ensure `DEEPSEEK_API_KEY` is set
- The application uses the DeepSeek API by default

## Architecture

### Core Components

1. **Configuration System** (`main.py:13-20`)
   - `Config` dataclass centralizes all configuration parameters
   - Supports custom model, base URL, and API key environment variable

2. **LLM Factory** (`main.py:21-33`)
   - `create_llm()` function handles ChatOpenAI instance creation
   - Includes type-safe API key handling and validation

3. **Tool System** (`main.py:35-44`)
   - LangChain tools for mathematical operations (`add`, `subtract`)
   - Tools are integrated into the agent for autonomous execution

4. **Agent Creation** (`main.py:45-51`)
   - `create_math_agent()` builds the agent with LLM and tools
   - Debug mode disabled for cleaner output

5. **Interactive Loop** (`main.py:53-94`)
   - Streaming response handling for real-time interaction
   - Graceful error handling and exit conditions

### Key Patterns

- **Streaming Responses**: The agent uses `agent.stream()` for real-time output, filtering out debug information and human messages
- **Environment-based Configuration**: API keys and settings loaded from environment variables
- **Type Safety**: API key handling uses lambda functions for proper type safety with LangChain
- **Error Handling**: Comprehensive error handling for configuration, runtime, and user interruptions

## Dependencies

- **langchain**: Core framework for building LLM applications
- **langchain-openai**: OpenAI-compatible API integration
- **langgraph**: Agent and workflow orchestration
- **python-dotenv**: Environment variable management
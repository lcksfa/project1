# pylint: disable=missing-module-docstring
import os
import time
from dataclasses import dataclass

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain.agents import create_agent
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Config:
    """配置类，集中管理所有配置参数"""
    temperature: float = 0
    model: str = "deepseek-chat"
    base_url: str = "https://api.deepseek.com"
    api_key_env_var: str = "DEEPSEEK_API_KEY"

def create_llm(config: Config) -> ChatOpenAI:
    """创建LLM实例，处理API密钥类型安全"""
    api_key = os.getenv(config.api_key_env_var)
    if not api_key:
        raise ValueError(f"{config.api_key_env_var} environment variable is not set")
    
    # 使用lambda函数作为API密钥提供者，确保类型安全
    return ChatOpenAI(
        temperature=config.temperature,
        model=config.model,
        base_url=config.base_url,
        api_key=lambda: api_key
    )

@tool
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

@tool
def subtract(a: int, b: int) -> int:
    """Subtract two numbers."""
    return a - b

def create_math_agent(llm: ChatOpenAI):
    """创建数学代理"""
    return create_agent(
        model=llm,
        tools=[add, subtract],
        debug=False  # 关闭调试模式，避免输出调试信息
    )

def run_agent_loop(agent):
    """运行代理交互循环"""
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in {"exit", "quit"}:
                print("Exiting Math Agent. Goodbye!")
                break
                
            if not user_input:
                print("Please enter a valid input.")
                continue
                
            # 使用流式输出，实时显示AI回复
            print("\nMath Agent: ", end="", flush=True)
            
            # 收集AI回复内容
            ai_response_content = ""
            
            # 使用流式API获取回复
            for chunk in agent.stream(
                {"messages": [HumanMessage(content=user_input)]}
            ):
                # 处理模型生成的消息
                if "model" in chunk and "messages" in chunk["model"]:
                    for message in chunk["model"]["messages"]:
                        if hasattr(message, 'content') and message.content:
                            # 只显示AI消息，过滤掉工具消息和HumanMessage
                            from langchain_core.messages import AIMessage
                            if isinstance(message, AIMessage):
                                # 确保content是字符串类型
                                content_str = str(message.content)
                                # 模拟流式输出，逐字符打印
                                for char in content_str:
                                    print(char, end="", flush=True)
                                    ai_response_content += char
                                    time.sleep(0.01)  # 添加小延时来模拟流式效果
                                
            print()  # 添加换行符
            
        except KeyboardInterrupt:
            print("\n\nExiting Math Agent. Goodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}. Please try again.")

def main():
    """主函数"""
    try:
        config = Config()
        llm = create_llm(config)
        agent = create_math_agent(llm)
        
        print("Welcome to the Math Agent!")
        print("Math Agent is ready. You can ask it to add or subtract numbers.")
        print("Type 'exit' or 'quit' to end the session.")
        
        run_agent_loop(agent)
        
    except ValueError as e:
        print(f"Configuration error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
